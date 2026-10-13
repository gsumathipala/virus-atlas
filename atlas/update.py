"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Keep the atlas current: check, fetch, rebuild, and report what changed.

    python -m atlas.update --check          what is stale, change nothing
    python -m atlas.update --coverage       which layers answer, and for what
    python -m atlas.update --taxonomy       fetch the current ICTV VMR + rebuild
    python -m atlas.update --live           force-refresh the live caches
    python -m atlas.update --all            both, with a change report

There are four data layers and they move at completely different speeds, which
is why they are updated separately rather than on one schedule:

  ICTV VMR         the taxonomy. A few releases a year; a new Master Species
                   List renames species wholesale. Needs a deliberate rebuild
                   and a look at the diff, because renames silently break the
                   curated layers that are keyed by binomial.
  WHO DON          outbreak reporting. Refreshes itself every 3 hours.
  Nextstrain       genomic builds. Refresh themselves every 12 hours.
  Europe PMC       literature. Fetched on demand, cached indefinitely.

The curated layers -- profiles, the human-pathogen reference list, serogroups,
morphology -- are source code, not data, so they are not "updated" here. What
this does instead is tell you which of their keys stopped matching after a
taxonomy change, which is the failure mode that actually bites.

User tier corrections live in data/overrides.json and are keyed by species
binomial. A rebuild never touches them, but a rename can orphan one, so they
are checked too.
"""

import argparse
import collections
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw" / "vmr.xlsx"
ATLAS = DATA / "atlas.json"

VMR_CURRENT = "https://ictv.global/vmr/current"
VMR_INDEX = "https://ictv.global/vmr"
UA = "virus-atlas/1.0 (educational; local use)"


def _get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read()


def digest(path):
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def releases():
    """Every VMR release the ICTV site lists, newest first."""
    try:
        html = _get(VMR_INDEX, timeout=40).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as err:
        return [], str(err)[:160]
    out = []
    for href in re.findall(r'href="([^"]*VMR[^"]*\.xlsx)"', html):
        name = href.rsplit("/", 1)[-1]
        m = re.search(r"MSL(\d+)\D*v?(\d+)?[._](\d{8})", name)
        out.append({
            "file": name,
            "url": href if href.startswith("http") else "https://ictv.global" + href,
            "msl": int(m.group(1)) if m else None,
            "date": m.group(3) if m else None,
        })
    out.sort(key=lambda r: (r["msl"] or 0, r["date"] or ""), reverse=True)
    return out, None


# ---------------------------------------------------------------------------
# Inspecting the built atlas
# ---------------------------------------------------------------------------

def species_set(path):
    """Species names, plus the group names the curated layers may key on.

    atlas.human keys a few entries by genus on purpose (the anellovirus
    genera), so comparing against species alone reported those as broken.
    """
    if not path.exists():
        return set(), None
    payload = json.loads(path.read_text())
    names = set()
    for n in payload["nodes"].values():
        if n["rank"] in ("species", "genus", "family", "subfamily"):
            names.add(n["name"])
    return names, payload.get("source", {}).get("file")


def species_only(path):
    """Species names alone, for counts and diffs."""
    if not path.exists():
        return set()
    payload = json.loads(path.read_text())
    return {n["name"] for n in payload["nodes"].values() if n["rank"] == "species"}


def curated_keys():
    """Every species name the curated layers expect to find."""
    from atlas import human, profiles
    keys = set(human.REFERENCE) | set(profiles.P)
    try:
        from atlas import genomic
        keys |= set(genomic.DATASETS)
    except ImportError:
        pass
    return keys


def overrides_keys():
    from atlas import overrides
    return set(overrides.load())


def report_breakage(names):
    """Curated and user keys that no longer match a species in the atlas."""
    missing_curated = sorted(k for k in curated_keys() if k not in names)
    missing_overrides = sorted(k for k in overrides_keys() if k not in names)
    return missing_curated, missing_overrides


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def surveil_prune():
    """Drop cached rows for feeds that are no longer configured."""
    from atlas import surveil
    stats = surveil.cache_stats()
    gone = [s for s in stats if s not in surveil.FEEDS]
    if gone:
        import sqlite3
        con = sqlite3.connect(surveil.DB)
        try:
            con.executemany("DELETE FROM feed WHERE source=?", [(g,) for g in gone])
            con.commit()
        finally:
            con.close()
    return gone


def check_refs(verbose=True):
    """Resolve every therapeutics citation against Europe PMC.

    Written because the first draft of atlas/therapeutics.py carried PMIDs
    recalled rather than looked up, and most of them resolved to unrelated
    papers -- a beta-blocker trial standing in for EPIC-SR, artificial hearts
    for McCormick's Lassa study. A reference that does not resolve to a
    plausibly matching title is worse than no reference, so this is a check
    that runs rather than a convention that is hoped for.

    Matching is deliberately loose: it compares the label's distinctive words
    against the fetched title, journal and authors, and flags what does not
    overlap for a human to look at. It cannot confirm that a real paper
    supports the claim made about it.
    """
    import re
    import time
    import urllib.parse
    from atlas import therapeutics

    STOP = {"et", "al", "the", "and", "for", "with", "in", "of", "a", "an",
            "to", "on", "vs", "versus", "study", "trial", "group", "n", "engl",
            "j", "med", "lancet", "jama", "clin", "infect", "dis", "sci",
            "transl", "nature", "review", "cochrane", "investigators",
            "collaborative", "consortium", "netw", "open", "am", "transplant",
            "respir", "pediatrics", "science"}

    def tokens(text):
        return {w for w in re.findall(r"[a-z0-9-]{3,}", (text or "").lower())
                if w not in STOP}

    refs = therapeutics.all_refs()
    bad, weak = [], []
    for ref in refs:
        pmid, doi = ref.get("pmid"), ref.get("doi")
        query = f"EXT_ID:{pmid}" if pmid else f'DOI:"{doi}"'
        url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
               + urllib.parse.quote(query) + "&format=json&pageSize=1&resultType=core")
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers={"User-Agent": UA}),
                    timeout=30) as fh:
                hits = (json.loads(fh.read()).get("resultList")
                        or {}).get("result") or []
        except (urllib.error.URLError, OSError, ValueError):
            hits = []
        if not hits:
            bad.append({**ref, "actual": None})
        else:
            h = hits[0]
            actual = f"{h.get('title', '')} {h.get('journalTitle', '')} {h.get('authorString', '')}"
            overlap = tokens(ref.get("label")) & tokens(actual)
            if not overlap:
                weak.append({**ref, "actual": (h.get("title") or "")[:90]})
        time.sleep(0.1)

    if verbose:
        print(f"therapeutics references: {len(refs)} checked, "
              f"{len(bad)} unresolved, {len(weak)} resolved but not matching")
        for r in bad:
            print(f"  UNRESOLVED  {r.get('pmid') or r.get('doi')}  {r['label'][:70]}")
        for r in weak:
            print(f"  MISMATCH    {r.get('pmid') or r.get('doi')}")
            print(f"      claimed: {r['label'][:78]}")
            print(f"      actual : {r['actual']}")
    return bad, weak


def check():
    print("ICTV taxonomy")
    local = digest(RAW)
    print(f"  local file   : {RAW.relative_to(ROOT)}"
          f"{'' if RAW.exists() else '  (MISSING)'}")
    if RAW.exists():
        print(f"  local size   : {RAW.stat().st_size:,} bytes"
              f"   sha256 {local[:16]}…")
        print(f"  built from   : {species_set(ATLAS)[1]}")

    rels, err = releases()
    if err:
        print(f"  release index: unreachable ({err})")
    elif rels:
        print(f"  newest listed: {rels[0]['file']}")
        print(f"  also listed  : " + ", ".join(r["file"] for r in rels[1:4]))

    try:
        head = urllib.request.Request(VMR_CURRENT, headers={"User-Agent": UA})
        with urllib.request.urlopen(head, timeout=60) as fh:
            remote = fh.read()
        same = hashlib.sha256(remote).hexdigest() == local
        print(f"  /vmr/current : {len(remote):,} bytes — "
              + ("identical to the local copy, nothing to do"
                 if same else "DIFFERS from the local copy"))
    except (urllib.error.URLError, OSError) as err:
        print(f"  /vmr/current : unreachable ({str(err)[:80]})")
        same = None

    names, _ = species_set(ATLAS)
    print(f"\nBuilt atlas: {len(species_only(ATLAS)):,} species")
    bad_curated, bad_over = report_breakage(names)
    print(f"  curated keys that match nothing : {len(bad_curated)}")
    for k in bad_curated[:10]:
        print(f"      {k}")
    print(f"  tier corrections orphaned       : {len(bad_over)}")
    for k in bad_over[:10]:
        print(f"      {k}")

    print("\nLive caches")
    dropped = surveil_prune()
    if dropped:
        print(f"  pruned {len(dropped)} cached rows for retired feeds: "
              + ", ".join(dropped))
    from atlas import enrich, genomic, surveil
    for label, stats in (("WHO outbreak news", surveil.cache_stats()),
                         ("Europe PMC", enrich.cache_stats())):
        print(f"  {label:<20} {stats}")
    print(f"  {'Nextstrain':<20} {len(genomic.covered())} species mapped to builds")
    return 0 if same is not False else 1


# An established human pathogen with no distribution, and why there is none.
# Anything else reaching that state is a gap, and --coverage fails on it.
NO_GEOGRAPHY = {
    "Orthopoxvirus vaccinia": "a vaccine strain, with no natural distribution",
}


def coverage():
    """How much of the atlas each curated layer actually answers for.

    Written after two layers turned out to be far thinner than they looked.
    Containment was resolved for 12,249 species and absent from the other
    5,305, 189 of which this atlas itself calls human pathogens; and the
    distribution map was read from profile prose only, so 56 species had one
    while the travel index knew the geography of 215. Neither showed up as an
    error -- the block simply was not rendered -- which is exactly why a
    coverage number has to be something the project asserts rather than
    something a reader notices.
    """
    import app as A
    from atlas import biosafety

    TIERED = ("established", "probable", "possible")
    rows = []
    for node in A.NODES.values():
        if node["rank"] != "species":
            continue
        meta = node.get("meta") or {}
        rows.append((
            node["name"], meta.get("tier"),
            biosafety.get(node["name"], meta.get("family"), meta.get("host"),
                          meta.get("genus"), meta.get("tier")),
            A.species_geo(node),
        ))

    print(f"Coverage over {len(rows):,} species\n")
    print("containment (atlas.biosafety)")
    basis = collections.Counter(b["basis"] for _, _, b, _ in rows)
    for k, v in basis.most_common():
        print(f"  {k:<14}{v:>7,}")
    levelled = sum(1 for _, _, b, _ in rows if b.get("bsl"))
    print(f"  {'with a level':<14}{levelled:>7,}")

    print("\ndistribution (app.species_geo)")
    src = collections.Counter(g["source"] for _, _, _, g in rows if g)
    for k, v in src.most_common():
        print(f"  {k:<14}{v:>7,}")
    print(f"  {'none':<14}{sum(1 for *_, g in rows if not g):>7,}")

    print("\nby human-pathogenicity tier")
    print(f"  {'tier':<13}{'species':>8}{'containment':>13}{'distribution':>14}")
    for tier in TIERED + ("animal-only", "no-evidence", "unassessed"):
        sel = [r for r in rows if r[1] == tier]
        if not sel:
            continue
        bsl = sum(1 for _, _, b, _ in sel if b.get("bsl"))
        gg = sum(1 for *_, g in sel if g)
        print(f"  {tier:<13}{len(sel):>8,}{bsl:>13,}{gg:>14,}")

    fail = 0
    gaps = [n for n, t, b, _ in rows if t in TIERED and not b.get("bsl")]
    if gaps:
        fail = 1
        print(f"\nFAIL  {len(gaps)} species with a pathogenicity tier have no "
              "containment level")
        for n in gaps[:10]:
            print(f"        {n}")
    missing = [n for n, t, _, g in rows
               if t == "established" and not g and n not in NO_GEOGRAPHY]
    if missing:
        fail = 1
        print(f"\nFAIL  {len(missing)} established human pathogens have no "
              "distribution")
        for n in missing[:10]:
            print(f"        {n}")
    for name, why in NO_GEOGRAPHY.items():
        print(f"\nnote  {name} has no distribution: {why}")
    if not fail:
        print("\nOK    every species the atlas calls a human pathogen has a "
              "containment level, and every established one a distribution")
    return fail


def taxonomy(url=None, force=False):
    url = url or VMR_CURRENT
    print(f"fetching {url}")
    try:
        blob = _get(url)
    except (urllib.error.URLError, OSError) as err:
        print(f"  download failed: {err}")
        return 1
    new_digest = hashlib.sha256(blob).hexdigest()
    if new_digest == digest(RAW) and not force:
        print("  identical to the local copy; nothing to rebuild "
              "(use --force to rebuild anyway)")
        return 0

    before = species_only(ATLAS)

    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = RAW.with_name(f"vmr.{stamp}.xlsx")
        shutil.copy2(RAW, backup)
        print(f"  previous copy kept at {backup.relative_to(ROOT)}")
    RAW.write_bytes(blob)
    print(f"  wrote {RAW.relative_to(ROOT)} ({len(blob):,} bytes)")

    print("rebuilding")
    proc = subprocess.run([sys.executable, "-m", "atlas.build", str(RAW)],
                          cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        print("  BUILD FAILED — the previous atlas.json is untouched")
        return proc.returncode

    after = species_only(ATLAS)
    added, removed = sorted(after - before), sorted(before - after)
    print(f"\nTaxonomy diff: {len(after):,} species "
          f"(+{len(added)} / -{len(removed)})")
    for label, rows in (("added", added), ("removed", removed)):
        if rows:
            print(f"  {label} ({len(rows)}):")
            for name in rows[:15]:
                print(f"      {name}")
            if len(rows) > 15:
                print(f"      … and {len(rows) - 15} more")

    bad_curated, bad_over = report_breakage(species_set(ATLAS)[0])
    if bad_curated:
        print(f"\n!! {len(bad_curated)} curated keys no longer match a species.")
        print("   These stopped applying and need renaming in atlas/human.py, "
              "atlas/profiles.py or atlas/genomic.py:")
        for k in bad_curated:
            print(f"      {k}")
    if bad_over:
        print(f"\n!! {len(bad_over)} tier corrections are orphaned. They are "
              "still in data/overrides.json and will apply again if the name "
              "comes back:")
        for k in bad_over:
            print(f"      {k}")
    if not bad_curated and not bad_over:
        print("\nAll curated keys and tier corrections still match.")
    return 0


def live(force=True):
    from atlas import genomic, surveil
    print("WHO Disease Outbreak News")
    reports, sources = surveil.all_signals(force=force)
    for s in sources:
        print(f"  {s['source']:<5} {s['state']:<8} {s['error'] or ''}")
    matched = sum(1 for r in reports if r.get("taxon"))
    print(f"  {len(reports)} reports, {matched} matched to a taxon")

    print("\nNextstrain builds")
    seen = set()
    for species in genomic.covered():
        for build in genomic.for_species(species):
            if build["prefix"] in seen:
                continue
            seen.add(build["prefix"])
            s = genomic.build_summary(build["prefix"], force=force)
            state = s["state"]
            note = f"{s.get('genomes', 0):>6} genomes, updated {s.get('updated')}"
            print(f"  {build['prefix']:<42} {state:<8} "
                  + (note if state != "failed" else s["error"]))
    return 0


def main():
    ap = argparse.ArgumentParser(
        prog="python -m atlas.update",
        description="Check or refresh the data behind the atlas.")
    ap.add_argument("--check", action="store_true",
                    help="report what is stale; change nothing")
    ap.add_argument("--coverage", action="store_true",
                    help="how much of the atlas each curated layer answers")
    ap.add_argument("--taxonomy", action="store_true",
                    help="fetch the current ICTV VMR and rebuild")
    ap.add_argument("--live", action="store_true",
                    help="force-refresh the WHO and Nextstrain caches")
    ap.add_argument("--all", action="store_true", help="--taxonomy then --live")
    ap.add_argument("--url", help="a specific VMR .xlsx URL or path")
    ap.add_argument("--force", action="store_true",
                    help="rebuild even when the VMR is unchanged")
    ap.add_argument("--releases", action="store_true",
                    help="list the VMR releases ICTV publishes")
    ap.add_argument("--check-refs", action="store_true",
                    help="verify every therapeutics citation against Europe PMC")
    args = ap.parse_args()

    if args.releases:
        rels, err = releases()
        if err:
            print(f"could not read the release index: {err}")
            return 1
        for r in rels:
            print(f"  MSL{r['msl']}  {r['date']}  {r['file']}")
        return 0

    if args.coverage:
        return coverage()

    if args.check_refs:
        bad, weak = check_refs()
        return 1 if (bad or weak) else 0

    if not any([args.check, args.taxonomy, args.live, args.all]):
        ap.print_help()
        return 0

    rc = 0
    if args.check:
        rc |= check()
    if args.taxonomy or args.all:
        rc |= taxonomy(args.url, force=args.force)
    if args.live or args.all:
        rc |= live()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
