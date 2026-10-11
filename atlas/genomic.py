"""Live genomic epidemiology, from Nextstrain.

Why this is separate from the radial tree
-----------------------------------------
The radial view in this app is a TAXONOMY: ICTV ranks, no branch lengths,
because ICTV ranks are not sequence distances. That is an honest picture but it
is not what a virologist means by a phylogeny.

Nextstrain is. Its builds are real time-resolved maximum-likelihood trees over
curated public sequence sets, rebuilt continuously, with clade assignments and
inferred geographic movement. So for the viruses where a build exists, this
module points at the real thing rather than implying the taxonomy is one.

What is fetched
---------------
Nextstrain's dataset JSON is 2-20 MB -- the whole tree -- which is far too much
to hold or forward. So a lookup fetches the dataset once, keeps only a small
summary (title, build date, genome count, clade names, geographic spread) and
caches that. The tree itself is never proxied: the interface links out to
nextstrain.org, where it is rendered by the people who maintain it.

Coverage
--------
DATASETS maps ICTV species to build prefixes. It is curated and partial by
necessity: Nextstrain carries ~318 datasets covering a few dozen viruses, out
of 17,554 species here. A species with no entry simply has no build.
"""

import json
import sqlite3
import time
import urllib.error
import urllib.request
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "genomic.sqlite3"
BASE = "https://nextstrain.org"
CHARON = BASE + "/charon/getDataset?prefix=/"
UA = "virus-atlas/1.0 (educational; local use)"
ACCEPT = "application/vnd.nextstrain.dataset.main+json"
TTL = 60 * 60 * 12          # builds update daily at most
TIMEOUT = 60                # these are multi-megabyte payloads

# ICTV species -> (nextstrain prefix, human label). Several species share a
# build where Nextstrain splits by subtype rather than by ICTV species, which
# is why the label is carried separately.
DATASETS = {
    "Betacoronavirus pandemicum": [
        ("ncov/gisaid/global/6m", "SARS-CoV-2, global, last 6 months"),
    ],
    "Orthopoxvirus monkeypox": [
        ("mpox/clade-IIb", "Mpox clade IIb"),
        ("mpox/clade-I", "Mpox clade I"),
        ("mpox/all-clades", "Mpox, all clades"),
    ],
    "Alphainfluenzavirus influenzae": [
        ("flu/seasonal/h3n2/ha/2y", "Seasonal influenza A/H3N2, HA, 2 years"),
        ("flu/seasonal/h1n1pdm/ha/2y", "Seasonal influenza A/H1N1pdm, HA, 2 years"),
        ("avian-flu/h5n1/ha/2y", "Avian influenza A(H5N1), HA, 2 years"),
        ("avian-flu/h5n1-cattle-outbreak/genome", "A(H5N1) cattle outbreak, whole genome"),
    ],
    "Betainfluenzavirus influenzae": [
        ("flu/seasonal/vic/ha/2y", "Influenza B/Victoria, HA, 2 years"),
    ],
    "Orthoflavivirus denguei": [
        ("dengue/all", "Dengue, all serotypes"),
        ("dengue/denv1", "Dengue virus 1"),
        ("dengue/denv2", "Dengue virus 2"),
        ("dengue/denv3", "Dengue virus 3"),
        ("dengue/denv4", "Dengue virus 4"),
    ],
    "Orthoflavivirus zikaense": [("zika", "Zika virus")],
    "Orthoflavivirus nilense": [("WNV/NA", "West Nile virus, North America")],
    "Orthoflavivirus flavi": [("yellow-fever/prM-E", "Yellow fever virus, prM-E")],
    "Orthopneumovirus hominis": [
        ("rsv/a/genome", "RSV A, whole genome"),
        ("rsv/b/genome", "RSV B, whole genome"),
    ],
    "Morbillivirus hominis": [("measles/genome", "Measles virus, whole genome")],
    "Orthoebolavirus zairense": [("ebola", "Zaire ebolavirus")],
    "Lyssavirus rabies": [("rabies", "Rabies virus")],
    "Enterovirus deconjuncti": [("enterovirus/d68/genome", "Enterovirus D68, whole genome")],
    "Orthorubulavirus parotitidis": [("mumps/global", "Mumps virus, global")],
    "Orthobunyavirus oropoucheense": [("oropouche/segment:L", "Oropouche virus, L segment")],
    "Lentivirus humimdef1": [("hiv/env", "HIV-1 env")],
    "Betacoronavirus cameli": [("mers", "MERS-CoV")],
}


def _db():
    DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS build ("
                "prefix TEXT PRIMARY KEY, fetched_at REAL, summary TEXT)")
    return con


def _cached(prefix):
    con = _db()
    try:
        row = con.execute("SELECT fetched_at, summary FROM build WHERE prefix=?",
                          (prefix,)).fetchone()
    finally:
        con.close()
    return (row[0], json.loads(row[1])) if row else (None, None)


def _store(prefix, summary):
    con = _db()
    try:
        con.execute("REPLACE INTO build VALUES (?,?,?)",
                    (prefix, time.time(), json.dumps(summary)))
        con.commit()
    finally:
        con.close()


def _walk(node, out):
    """Collect leaf count and trait values from a Nextstrain tree in one pass."""
    kids = node.get("children") or []
    if not kids:
        out["tips"] += 1
        traits = node.get("node_attrs") or {}
        for key in ("country", "region", "clade_membership", "lineage",
                    "clade", "subclade", "host"):
            val = (traits.get(key) or {}).get("value")
            if val:
                out[key][val] = out[key].get(val, 0) + 1
        date = (traits.get("num_date") or {}).get("value")
        if isinstance(date, (int, float)):
            out["date_min"] = min(out["date_min"], date)
            out["date_max"] = max(out["date_max"], date)
    for kid in kids:
        _walk(kid, out)


def _summarise(prefix, payload):
    meta = payload.get("meta") or {}
    acc = {"tips": 0, "date_min": 1e9, "date_max": -1e9,
           "country": {}, "region": {}, "clade_membership": {},
           "lineage": {}, "clade": {}, "subclade": {}, "host": {}}
    tree = payload.get("tree")
    if isinstance(tree, list):            # some builds ship a list of roots
        for root in tree:
            _walk(root, acc)
    elif tree:
        _walk(tree, acc)

    def top(key, n=8):
        return sorted(acc[key].items(), key=lambda kv: -kv[1])[:n]

    clades = top("clade_membership") or top("clade") or top("subclade") or top("lineage")
    return {
        "prefix": prefix,
        "url": f"{BASE}/{prefix}",
        "title": meta.get("title") or prefix,
        "updated": meta.get("updated"),
        "build_url": meta.get("build_url"),
        "maintainers": [m.get("name") for m in (meta.get("maintainers") or [])][:4],
        "genomes": acc["tips"],
        "span": ([round(acc["date_min"], 2), round(acc["date_max"], 2)]
                 if acc["tips"] and acc["date_min"] < 1e9 else None),
        "clades": [{"name": k, "n": v} for k, v in clades],
        "countries": [{"name": k, "n": v} for k, v in top("country", 12)],
        "regions": [{"name": k, "n": v} for k, v in top("region", 8)],
    }


def build_summary(prefix, force=False):
    """Summary for one Nextstrain build. Never raises; reports its state."""
    fetched_at, cached = _cached(prefix)
    if cached is not None and not force and (time.time() - fetched_at) < TTL:
        return {**cached, "state": "cached", "fetched_at": fetched_at, "error": None}
    req = urllib.request.Request(
        CHARON + urllib.parse.quote(prefix, safe="/:"),
        headers={"User-Agent": UA, "Accept": ACCEPT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as fh:
            payload = json.loads(fh.read())
        summary = _summarise(prefix, payload)
        _store(prefix, summary)
        return {**summary, "state": "fetched", "fetched_at": time.time(), "error": None}
    except (urllib.error.URLError, OSError, ValueError,
            json.JSONDecodeError, RecursionError) as err:
        if cached is not None:
            return {**cached, "state": "stale", "fetched_at": fetched_at,
                    "error": str(err)[:200]}
        return {"prefix": prefix, "url": f"{BASE}/{prefix}", "title": prefix,
                "state": "failed", "fetched_at": None, "error": str(err)[:200],
                "genomes": 0, "clades": [], "countries": [], "regions": []}


def for_species(species):
    """Every build listed for one ICTV species, without fetching anything."""
    return [{"prefix": p, "label": label, "url": f"{BASE}/{p}"}
            for p, label in DATASETS.get(species, [])]


def covered():
    return sorted(DATASETS)


import urllib.parse  # noqa: E402  (used by build_summary)


if __name__ == "__main__":  # python -m atlas.genomic ["<species>"]
    import sys
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in sys.argv
    targets = args or ["Orthopoxvirus monkeypox"]
    for species in targets:
        builds = for_species(species)
        print(f"\n{species}: {len(builds)} build(s)")
        for b in builds:
            s = build_summary(b["prefix"], force=force)
            if s["state"] == "failed":
                print(f"  {b['prefix']:<42} FAILED {s['error']}")
                continue
            span = s.get("span")
            print(f"  {b['prefix']:<42} {s['state']:<8} {s['genomes']:>6} genomes"
                  f"  updated {s.get('updated')}"
                  + (f"  {span[0]:.1f}-{span[1]:.1f}" if span else ""))
            if s["clades"]:
                print("      clades:   " + ", ".join(
                    f"{c['name']} ({c['n']})" for c in s["clades"][:6]))
            if s["countries"]:
                print("      top countries: " + ", ".join(
                    f"{c['name']} ({c['n']})" for c in s["countries"][:6]))
