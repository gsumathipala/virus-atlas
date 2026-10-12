"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Live literature lookup for species with no curated profile.

Europe PMC REST search (free, no API key, no account). Returns real papers --
title, journal, year, authors, abstract snippet, DOI/PMID -- and flags which of
them mention human infection. Nothing is synthesised, so nothing can be
fabricated: every statement the panel makes is a citation the reader can open.

A lookup is performed once per species and then cached in
data/evidence.sqlite, so later visits are instant and work offline.

CLI:
  python -m atlas.enrich "Orthobunyavirus catqueense"     one species
  python -m atlas.enrich --all [--limit N]                warm the whole cache
  python -m atlas.enrich --genus Orthobunyavirus          one genus
"""

import json
import re
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = ROOT / "data" / "evidence.sqlite"

EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = {"User-Agent": "virus-atlas/1.0 (educational virus taxonomy browser)"}

MAX_PAPERS = 25

# Terms that mark a paper as being about human infection rather than the
# vector, the reservoir or pure sequence work.
HUMAN_RX = re.compile(
    r"\b(human|humans|patient|patients|clinical|case report|case series|"
    r"febrile illness|encephalitis|meningitis|haemorrhagic|hemorrhagic|"
    r"seroprevalence|seropositiv|seroconversion|outbreak|epidemic|"
    r"hospitali[sz]ed|infant|children|pregnan|fatal|mortality)\b",
    re.I,
)

_lock = threading.Lock()
_conn = None


# --------------------------------------------------------------------- cache

def conn():
    global _conn
    if _conn is None:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(CACHE_PATH, check_same_thread=False)
        _conn.execute(
            """CREATE TABLE IF NOT EXISTS evidence (
                 species    TEXT PRIMARY KEY,
                 fetched_at TEXT NOT NULL,
                 literature TEXT
               )"""
        )
        _conn.commit()
    return _conn


def cached(species):
    with _lock:
        row = conn().execute(
            "SELECT fetched_at, literature FROM evidence WHERE species = ?",
            (species,),
        ).fetchone()
    if not row:
        return None
    fetched_at, literature = row
    return {
        "species": species,
        "cached": True,
        "fetched_at": fetched_at,
        "literature": json.loads(literature) if literature else None,
    }


def store(species, literature):
    with _lock:
        conn().execute(
            "REPLACE INTO evidence (species, fetched_at, literature) VALUES (?,?,?)",
            (
                species,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                json.dumps(literature) if literature else None,
            ),
        )
        conn().commit()


def cache_stats():
    with _lock:
        (total,) = conn().execute("SELECT COUNT(*) FROM evidence").fetchone()
    return {"species_cached": total}


# ----------------------------------------------------------------- providers

def _get_json(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))




def search_terms(species, names):
    """Quoted search terms: the binomial plus any common virus names."""
    terms = [species]
    for n in names or []:
        n = re.sub(r"\s*\([^)]*\)\s*", " ", n).strip()   # drop "(OYAV)"
        if n and n.lower() != "none" and len(n) > 3:
            terms.append(n)
    seen, out = set(), []
    for t in terms:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out[:6]


def _term_rx(terms):
    return re.compile(
        r"(?<![A-Za-z])(?:" + "|".join(re.escape(t) for t in terms) + r")(?![A-Za-z])",
        re.I,
    )


def _classify(title, abstract, rx):
    """How squarely is this paper about the virus, and does it concern humans?

    An OR query matches anything mentioning any synonym, so a broad review of
    another virus can rank highly. Grading by where the name appears separates
    'about this virus' from 'mentions it in passing'. The human flag requires
    the virus name and a human term in the SAME sentence -- otherwise any paper
    containing the word "human" anywhere trips it, which flagged an archaeal
    virus as a human pathogen.
    """
    in_title = bool(rx.search(title))
    in_abstract = bool(rx.search(abstract))
    focus = "title" if in_title else "abstract" if in_abstract else "weak"

    human = False
    if in_title and HUMAN_RX.search(f"{title} {abstract}"):
        human = True
    else:
        for sentence in re.split(r"(?<=[.!?])\s+", f"{title}. {abstract}"):
            if rx.search(sentence) and HUMAN_RX.search(sentence):
                human = True
                break
    return focus, human and (in_title or in_abstract)


def literature(species, names):
    """Europe PMC search. Returns papers plus a human-infection flag."""
    terms = search_terms(species, names)
    query = " OR ".join(f'"{t}"' for t in terms)
    # No sort parameter: Europe PMC's own relevance ranking beats citation
    # count here, which otherwise floats generic taxonomy papers to the top.
    url = EUROPEPMC + "?" + urllib.parse.urlencode(
        {
            "query": query,
            "format": "json",
            "pageSize": MAX_PAPERS,
            "resultType": "core",
        }
    )
    try:
        data = _get_json(url)
    except (urllib.error.URLError, OSError, ValueError, TimeoutError) as exc:
        return {"error": f"Europe PMC lookup failed: {exc}", "terms": terms}

    result = data.get("resultList", {}).get("result", [])
    rx = _term_rx(terms)
    papers = []
    for r in result:
        abstract = re.sub(r"<[^>]+>", "", (r.get("abstractText") or "").strip())
        title = re.sub(r"<[^>]+>", "", (r.get("title") or "").strip()).rstrip(".")
        focus, human = _classify(title, abstract, rx)
        papers.append(
            {
                "title": title,
                "focus": focus,
                "journal": (r.get("journalInfo", {}) or {}).get("journal", {}).get("title")
                           or r.get("journalTitle"),
                "year": r.get("pubYear"),
                "authors": r.get("authorString"),
                "pmid": r.get("pmid"),
                "pmcid": r.get("pmcid"),
                "doi": r.get("doi"),
                "citations": r.get("citedByCount"),
                "is_open_access": r.get("isOpenAccess") == "Y",
                "abstract": abstract[:700] + ("…" if len(abstract) > 700 else ""),
                "mentions_human": human,
            }
        )

    # Papers naming the virus in the title first, then those naming it in the
    # abstract, then passing mentions; within each band, most-cited first.
    band = {"title": 0, "abstract": 1, "weak": 2}
    papers.sort(key=lambda p: (band[p["focus"]], -(p["citations"] or 0)))

    focused = [p for p in papers if p["focus"] != "weak"]
    return {
        "terms": terms,
        "query": query,
        "total": int(data.get("hitCount", 0)),
        "shown": len(papers),
        "focused": len(focused),
        "human_mentions": sum(1 for p in papers if p["mentions_human"]),
        "papers": papers,
        "source": "Europe PMC",
    }


# ------------------------------------------------------------------ dispatch

def lookup(species, meta, refresh=False):
    """Cached Europe PMC lookup for one species."""
    if not refresh:
        hit = cached(species)
        if hit:
            return hit

    lit = literature(species, meta.get("names"))
    store(species, lit)

    return {
        "species": species,
        "cached": False,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "literature": lit,
    }


# ----------------------------------------------------------------------- CLI

def _species_meta_from_atlas():
    """Load species -> lookup metadata from the built atlas."""
    atlas = ROOT / "data" / "atlas.json"
    if not atlas.exists():
        raise SystemExit("data/atlas.json not found -- run: python -m atlas.build")
    with atlas.open() as fh:
        nodes = json.load(fh)["nodes"]
    out = {}
    for node in nodes.values():
        if node["rank"] != "species":
            continue
        meta = node.get("meta") or {}
        names = []
        for cid in node["children"]:
            iso = nodes[cid].get("meta") or {}
            names.extend(iso.get("names") or [])
        out[node["name"]] = {
            "names": names,
            "family": meta.get("family"),
            "genus": meta.get("genus"),
            "serogroup": meta.get("serogroup"),
            "host": meta.get("host"),
            "profiled": meta.get("profiled"),
        }
    return out


def main(argv):
    args = argv[1:]
    if not args:
        print(__doc__)
        print("cache:", cache_stats())
        return 0

    everything = _species_meta_from_atlas()

    if args[0] == "--all" or args[0] == "--genus":
        if args[0] == "--genus":
            genus = args[1]
            targets = [s for s, m in everything.items() if m["genus"] == genus]
        else:
            targets = list(everything)
        if "--limit" in args:
            targets = targets[: int(args[args.index("--limit") + 1])]
        targets.sort()
        print(f"{len(targets)} species to look up via Europe PMC")
        done = errors = 0
        t0 = time.time()
        for i, sp in enumerate(targets, 1):
            if cached(sp):
                continue
            try:
                res = lookup(sp, everything[sp])
                lit = res.get("literature") or {}
                print(f"  {i}/{len(targets)}  {sp}  "
                      f"[{lit.get('total', 0)} papers, {lit.get('human_mentions', 0)} human]")
                done += 1
            except Exception as exc:                      # keep the batch going
                errors += 1
                print(f"  {i}/{len(targets)}  {sp}  FAILED: {exc}", file=sys.stderr)
            time.sleep(0.4)                               # be polite to the APIs
        print(f"done: {done} fetched, {errors} errors, "
              f"{time.time() - t0:.0f}s, cache={cache_stats()}")
        return 0

    species = args[0]
    if species not in everything:
        matches = [s for s in everything if species.lower() in s.lower()]
        print(f"'{species}' is not an ICTV species name in the atlas.")
        if matches:
            print("Did you mean:", *matches[:10], sep="\n  ")
        return 1
    res = lookup(species, everything[species], refresh="--refresh" in args)
    print(json.dumps(res, indent=1)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
