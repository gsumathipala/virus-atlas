"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Virus Atlas -- a browsable tree of ICTV virus taxonomy with serogroups and
human-pathogenicity evidence.

Run:  python app.py        (then open http://127.0.0.1:5057)
"""

import os
import sys

# Running `python3 app.py` picks up the system interpreter, which has no
# Flask: the dependencies live in this project's .venv. Rather than fail with
# a bare ModuleNotFoundError, hand over to the virtualenv's interpreter and
# carry on. Only when run as a script, and only when Flask is genuinely
# missing, so a server that imports `app:app` (gunicorn) is never touched.
if __name__ == "__main__":
    try:
        import flask as _flask_probe       # noqa: F401
    except ModuleNotFoundError:
        _root = os.path.dirname(os.path.abspath(__file__))
        _venv_dir = os.path.join(_root, ".venv")
        _venv = os.path.join(_venv_dir, "bin", "python")
        # Compare sys.prefix, not the binary: a virtualenv's `python` is a
        # symlink to the base interpreter, so realpath() makes the two look
        # identical and the hand-over never happens. What distinguishes them
        # is the prefix, which is what puts site-packages on the path.
        if os.path.exists(_venv) and os.path.realpath(sys.prefix) != os.path.realpath(_venv_dir):
            os.execv(_venv, [_venv, *sys.argv])
        sys.exit(
            "Flask is not installed for this interpreter and no virtualenv "
            "was found at .venv\n\n"
            "  python3 -m venv .venv\n"
            "  .venv/bin/pip install -r requirements.txt\n"
            "  python3 app.py\n")

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request

from atlas import (baltimore, biosafety, countermeasures, crossreact,
                   differential, enrich, genomic, geo, morphology, overrides,
                   receptors, surveil, therapeutics, travel)

import os

ROOT = Path(__file__).resolve().parent

# Set on hosts whose filesystem does not survive a restart (Render free plan,
# most container platforms). Tier corrections are still written and still
# work for the life of the instance; what changes is that they are lost when
# it sleeps or redeploys, and the interface has to say so rather than
# implying they are saved.
EPHEMERAL = os.environ.get("EPHEMERAL_STORAGE") == "1"
ATLAS_PATH = ROOT / "data" / "atlas.json"

app = Flask(__name__)
# Evidence tiers are ordered strongest-first; alphabetising them would scramble
# the legend, the distribution bars and the pathogen index.
app.json.sort_keys = False


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load():
    if not ATLAS_PATH.exists():
        raise SystemExit(
            f"{ATLAS_PATH} not found. Build it first:\n"
            "  python -m atlas.build data/raw/vmr.xlsx"
        )
    with ATLAS_PATH.open() as fh:
        payload = json.load(fh)
    nodes = payload["nodes"]
    index = _build_search_index(nodes)
    return payload, nodes, index


def _fold(text):
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def _build_search_index(nodes):
    """Flat list of (folded haystack, display, node_id, rank, tier) tuples.

    Isolates are indexed against their *species* node, since that is the level
    the sidebar describes. Virus common names and abbreviations matter most --
    people search "OYAV" or "Oya virus", not "Orthobunyavirus catqueense".
    """
    entries = []
    for node in nodes.values():
        rank = node["rank"]
        if rank == "isolate":
            continue
        meta = node.get("meta") or {}
        terms = {node["name"]}
        if rank == "species":
            for cid in node["children"]:
                iso = nodes[cid].get("meta") or {}
                terms.update(iso.get("names") or [])
                terms.update(iso.get("abbrev") or [])
            prof = meta.get("profile")
            if prof:
                terms.update(prof.get("names") or [])
        terms = {t for t in terms if t and t.lower() != "none"}
        entries.append(
            {
                "id": node["id"],
                "name": node["name"],
                "rank": rank,
                "tier": meta.get("tier") or node.get("top_tier"),
                "serogroup": meta.get("serogroup"),
                "family": meta.get("family"),
                "terms": sorted(terms),
                "hay": _fold(" | ".join(sorted(terms))),
                "profiled": bool(meta.get("profiled")),
                "n_species": node.get("n_species", 0),
            }
        )
    return entries


PAYLOAD, NODES, SEARCH_INDEX = _load()

# Species id by ICTV binomial, so a correction can be addressed by name and
# survive a rebuild that renumbers the tree.
SPECIES_ID = {n["name"]: n["id"] for n in NODES.values() if n["rank"] == "species"}

TIER_RANK = {k: v["rank"] for k, v in PAYLOAD["tiers"].items()}

# The travel index is derived from curated geography prose, so it is built once
# at startup rather than per request.
TRAVEL_BY_COUNTRY, TRAVEL_WORLDWIDE, TRAVEL_STATS = travel.build_index(NODES, geo)

# Syndrome index, for the differential view. Also built once: it is derived
# from the same curated prose and never changes at runtime.
DX_BY_SPECIES, DX_BY_SYNDROME = differential.build_index(NODES)
print(f"travel index: {TRAVEL_STATS['with_geography']} species across "
      f"{TRAVEL_STATS['countries']} countries, "
      f"{TRAVEL_STATS['worldwide']} cosmopolitan")
print(f"syndrome index: {len(DX_BY_SPECIES)} species, "
      + ", ".join(f"{k} {len(v)}" for k, v in
                  sorted(DX_BY_SYNDROME.items(), key=lambda kv: -len(kv[1]))[:5]))


def _reroll(species_id):
    """Recompute tier counts and the strongest tier up one species' ancestry.

    Incremental rather than a full re-summarise: a correction touches one leaf,
    and walking 42,000 nodes on every edit would make the control feel broken.
    """
    node = NODES[species_id]
    tier = (node.get("meta") or {}).get("tier")
    node["tiers"] = {tier: 1}
    node["top_tier"] = tier

    cur = NODES.get(node.get("parent"))
    while cur is not None:
        counts = {}
        for cid in cur["children"]:
            child = NODES[cid]
            if child["rank"] == "isolate":
                continue
            for k, v in (child.get("tiers") or {}).items():
                counts[k] = counts.get(k, 0) + v
        # Keep the legend's strongest-first order rather than dict insertion
        # order, which the incremental walk would otherwise scramble.
        cur["tiers"] = {k: counts[k] for k in PAYLOAD["tiers"] if k in counts}
        cur["top_tier"] = next((k for k in PAYLOAD["tiers"] if k in counts), None)
        cur = NODES.get(cur.get("parent"))


def _apply_override(species, entry):
    """Point a stored correction at the live tree. Returns the species id."""
    sid = SPECIES_ID.get(species)
    if not sid:
        return None
    meta = NODES[sid].setdefault("meta", {})
    if "base_tier" not in meta:
        meta["base_tier"] = meta.get("tier")
        meta["base_basis"] = meta.get("basis")
    meta["tier"] = entry["tier"]
    meta["basis"] = "override"
    meta["override"] = entry
    _reroll(sid)
    return sid


def _drop_override(species):
    sid = SPECIES_ID.get(species)
    if not sid:
        return None
    meta = NODES[sid].setdefault("meta", {})
    meta["tier"] = meta.pop("base_tier", meta.get("tier"))
    meta["basis"] = meta.pop("base_basis", "none")
    meta.pop("override", None)
    _reroll(sid)
    return sid


def _load_overrides():
    stored = overrides.load()
    applied, missing = 0, []
    for species, entry in stored.items():
        if entry.get("tier") not in PAYLOAD["tiers"]:
            missing.append(species)
            continue
        if _apply_override(species, entry):
            applied += 1
        else:
            missing.append(species)
    if applied or missing:
        print(f"overrides: {applied} applied"
              + (f", {len(missing)} unmatched: {', '.join(missing[:5])}" if missing else ""))
    return applied


_load_overrides()

RANK_WEIGHT = {
    "species": 0, "clade": 1, "serogroup": 2, "subgenus": 3, "genus": 4,
    "subfamily": 5, "family": 6, "order": 7, "suborder": 7, "class": 8,
    "subclass": 8, "phylum": 9, "subphylum": 9, "kingdom": 10,
    "subkingdom": 10, "subrealm": 11, "realm": 11, "root": 12,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def shallow(node):
    """A node as the tree view needs it -- no profile payload, no isolate list."""
    meta = node.get("meta") or {}
    out = {
        "id": node["id"],
        "name": node["name"],
        "rank": node["rank"],
        "n_children": len(node["children"]),
        "n_species": node.get("n_species", 0),
        "top_tier": node.get("top_tier"),
        "tiers": node.get("tiers", {}),
    }
    if node["rank"] == "species":
        out["tier"] = meta.get("tier")
        out["basis"] = meta.get("basis")
        out["profiled"] = bool(meta.get("profiled"))
        out["serogroup"] = meta.get("serogroup")
        out["genome"] = meta.get("genome")
        out["n_isolates"] = node.get("n_isolates", 0)
        names = []
        for cid in node["children"]:
            iso = NODES[cid].get("meta") or {}
            names.extend(iso.get("names") or [])
        # The common name is what a learner recognises; show it beside the binomial.
        out["common"] = names[0] if names else None
    elif node["rank"] == "isolate":
        out["meta"] = meta
        # An isolate has no pathogenicity record of its own, but it inherits its
        # species' -- so the tree dot is coloured rather than left grey.
        out["tier"] = (NODES.get(node["parent"], {}).get("meta") or {}).get("tier")
        out["common"] = "; ".join(meta.get("abbrev") or []) or meta.get("designation")
    return out


def ancestry(node_id):
    chain = []
    cur = NODES.get(node_id)
    while cur is not None:
        chain.append({"id": cur["id"], "name": cur["name"], "rank": cur["rank"]})
        cur = NODES.get(cur["parent"]) if cur["parent"] else None
    return list(reversed(chain))


def sort_children(ids):
    def key(cid):
        n = NODES[cid]
        unassigned = n["name"].startswith("Unassigned")
        return (unassigned, n["name"].lower())
    return sorted(ids, key=key)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return render_template("index.html", source=PAYLOAD["source"])


@app.get("/api/meta")
def api_meta():
    root = NODES["root"]
    return jsonify(
        {
            "source": PAYLOAD["source"],
            "tiers": PAYLOAD["tiers"],
            "totals": {
                "species": root.get("n_species", 0),
                "nodes": len(NODES),
                "tiers": root.get("tiers", {}),
                "profiled": sum(1 for e in SEARCH_INDEX if e["profiled"]),
            },
            "live": {
                "cache": enrich.cache_stats(),
                "surveillance": surveil.cache_stats(),
                "genomic_species": len(genomic.covered()),
                "receptors": len(receptors.covered()),
                "biosafety": len(biosafety.covered()),
                "countermeasures": len(countermeasures.covered()),
                "therapeutics": len(therapeutics.covered()),
                "crossreact": len(crossreact.COMPLEXES),
                "syndromes": len(DX_BY_SPECIES),
                "travel": TRAVEL_STATS,
            "ephemeral": EPHEMERAL,
            },
            "roots": [shallow(NODES[c]) for c in sort_children(root["children"])],
        }
    )


@app.get("/api/children")
def api_children():
    node_id = request.args.get("id", "root")
    node = NODES.get(node_id)
    if node is None:
        abort(404)
    return jsonify(
        {
            "id": node_id,
            "children": [shallow(NODES[c]) for c in sort_children(node["children"])],
        }
    )


@app.get("/api/node")
def api_node():
    node_id = request.args.get("id", "")
    node = NODES.get(node_id)
    if node is None:
        abort(404)
    out = {
        "id": node["id"],
        "name": node["name"],
        "rank": node["rank"],
        "path": ancestry(node_id),
        "n_species": node.get("n_species", 0),
        "tiers": node.get("tiers", {}),
        "top_tier": node.get("top_tier"),
        "note": node.get("note"),
        "meta": node.get("meta"),
    }
    if node["rank"] in ("genus", "serogroup"):
        out["crossreact"] = crossreact.for_group(node["name"], node["rank"])
    if node["rank"] == "species":
        out["isolates"] = [NODES[c].get("meta") for c in node["children"]]
        out["morphology"] = species_morphology(node)
        out["geo"] = species_geo(node)
        out["baltimore"] = baltimore.describe(
            (node.get("meta") or {}).get("genome"),
            (node.get("meta") or {}).get("family"))
        out["receptors"] = receptors.get(node["name"])
        out["biosafety"] = biosafety.get(
            node["name"], (node.get("meta") or {}).get("family"),
            (node.get("meta") or {}).get("host"),
            (node.get("meta") or {}).get("genus"),
            (node.get("meta") or {}).get("tier"))
        out["countermeasures"] = countermeasures.get(node["name"])
        out["crossreact"] = crossreact.for_species(node["name"])
        out["therapeutics"] = therapeutics.get(node["name"])
        out["syndromes"] = _syndrome_tags(node["name"])
    elif node["rank"] == "isolate":
        # Clinical and pathogenicity information lives at species level, so the
        # isolate view carries its species' record rather than showing nothing.
        parent = NODES.get(node["parent"])
        if parent:
            out["species"] = {
                "id": parent["id"],
                "name": parent["name"],
                "meta": parent.get("meta"),
                "isolates": [NODES[c].get("meta") for c in parent["children"]],
            }
            out["morphology"] = species_morphology(parent)
            out["geo"] = species_geo(parent)
    else:
        out["morphology"] = group_morphology(node)
        out["children"] = [shallow(NODES[c]) for c in sort_children(node["children"])]
        # A short roster of the notable species beneath this node helps orient
        # the reader without expanding the whole subtree.
        out["highlights"] = highlights(node_id)
    return jsonify(out)


def first_species(node_id):
    """Any species beneath a node, for a representative genome type."""
    stack = [node_id]
    while stack:
        n = NODES[stack.pop()]
        if n["rank"] == "species":
            return n
        if n["rank"] != "isolate":
            stack.extend(n["children"])
    return None


def group_morphology(node):
    """Virion architecture for a family/genus/serogroup node.

    Architecture is a family-level trait, so a group node illustrates the same
    particle its species do. Ranks above family are too heterogeneous to draw
    one particle for, so they get nothing.
    """
    family = next(
        (p["name"] for p in ancestry(node["id"]) if p["rank"] == "family"), None
    )
    if not family:
        return None
    sp = first_species(node["id"])
    genome = (sp.get("meta") or {}).get("genome") if sp else None
    spec = morphology.spec_for(family, genome)
    return spec if spec.get("confident") else None


# A segment label in an ICTV accession field: "L: AB1234; M: AB1235; S: AB1236",
# or "RNA1:", "dsRNA4:", "Seg10:", "SegA:", "RNA6c:". The qualifier words ICTV
# also puts in this position -- "partial: AY225133; partial: AY225134; ..." --
# must NOT count, or a monopartite phycodnavirus is drawn with 16 segments.
SEGMENT_LABEL = re.compile(
    r"(?:^|;)\s*("
    r"(?:(?:ds|ss|c)?(?:RNA|DNA)|Seg(?:ment)?)?[-_ ]?"
    r"(?:[A-Za-z]\d{0,2}|\d{1,2})[a-c]?"
    r")\s*:",
    re.I)


def _segment_key(label):
    """Normalise a segment label so variants of one segment count once.

    "RNA3a" and "RNA3b" are two sequenced variants of emaravirus RNA3, not two
    segments. A letter that follows a number is therefore dropped, while a
    letter that IS the identifier ("SegA", "Ma") is kept, because those name
    genuinely distinct segments.
    """
    key = re.sub(r"[-_ ]", "", label.lower())
    return re.sub(r"(\d+)[a-c]$", r"\1", key)


def species_morphology(node):
    """Virion architecture for the schematic figure.

    Segment count comes from the isolate accessions where ICTV spells them out
    ("L: ...; M: ...; S: ..."), which is more specific than the family default.
    """
    meta = node.get("meta") or {}
    hint = None
    for cid in node["children"]:
        acc = (NODES[cid].get("meta") or {}).get("accession") or ""
        labels = {_segment_key(m) for m in SEGMENT_LABEL.findall(acc)}
        if len(labels) > 1:
            hint = max(hint or 0, len(labels))
    return morphology.spec_for(meta.get("family"), meta.get("genome"), hint)


def species_geo(node):
    """Where this species is reported, as the map needs it.

    The same resolution the travel index uses, so the two cannot disagree.
    It used to read the profile's prose only, which meant a map for the 56
    profiled species and nothing for the other 159 the travel panel places
    on a destination list.
    """
    meta = node.get("meta") or {}
    where = travel.geography_for(node["name"], meta, geo)
    eradicated = geo.eradicated(where["text"])
    # An eradicated virus has no countries and is not worldwide, and that is
    # the finding, not an absence of one. Dropping it took the "Eradicated"
    # block off the smallpox page.
    if not where["countries"] and not where["worldwide"] and not eradicated:
        return None
    # A cosmopolitan species has no geography prose to quote -- what it has is
    # a clinical note, which read as a description of the distribution when it
    # was put under the map. Say what the map means instead.
    text = where["text"]
    if where["source"] == "worldwide":
        text = ("Reported worldwide: this species circulates on every "
                "inhabited continent, which is why no country list is held "
                "for it.")
    return {
        "text": text,
        "countries": where["countries"],
        "worldwide": where["worldwide"],
        "matched": where["matched"][:8],
        "source": where["source"],
        "eradicated": eradicated,
    }


@lru_cache(maxsize=512)
def highlights(node_id, limit=12):
    tier_rank = {k: v["rank"] for k, v in PAYLOAD["tiers"].items()}
    found = []
    stack = [node_id]
    while stack:
        n = NODES[stack.pop()]
        if n["rank"] == "species":
            meta = n.get("meta") or {}
            if meta.get("profiled"):
                found.append(
                    {
                        "id": n["id"],
                        "name": n["name"],
                        "tier": meta.get("tier"),
                        "serogroup": meta.get("serogroup"),
                        "headline": (meta.get("profile") or {}).get("headline"),
                        "common": (meta.get("profile") or {}).get("names", [None])[0],
                    }
                )
            continue
        if n["rank"] == "isolate":
            continue
        stack.extend(n["children"])
    found.sort(key=lambda h: (tier_rank.get(h["tier"], 9), h["name"]))
    return found[:limit]


@app.get("/api/search")
def api_search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify({"q": q, "results": []})
    needle = _fold(q)
    tier_filter = request.args.get("tier") or None
    exact = re.compile(rf"(^|\|\s|\s){re.escape(needle)}($|\s|\|)")

    scored = []
    for e in SEARCH_INDEX:
        if needle not in e["hay"]:
            continue
        if tier_filter and e["tier"] != tier_filter:
            continue
        hay = e["hay"]
        if exact.search(hay):
            score = 0
        elif hay.startswith(needle):
            score = 1
        elif re.search(rf"(^|\|\s|\s){re.escape(needle)}", hay):
            score = 2
        else:
            score = 3
        scored.append(
            (score, RANK_WEIGHT.get(e["rank"], 12), not e["profiled"], len(e["name"]), e)
        )

    scored.sort(key=lambda t: t[:4])
    results = []
    for *_, e in scored[:60]:
        matched = [t for t in e["terms"] if needle in _fold(t)]
        results.append(
            {
                "id": e["id"],
                "name": e["name"],
                "rank": e["rank"],
                "tier": e["tier"],
                "serogroup": e["serogroup"],
                "family": e["family"],
                "profiled": e["profiled"],
                "n_species": e["n_species"],
                "matched": matched[:4],
                "path": [p["name"] for p in ancestry(e["id"])[1:-1]],
            }
        )
    return jsonify({"q": q, "total": len(scored), "results": results})


@app.get("/api/subtree")
def api_subtree():
    """A bounded subtree for the radial view.

    The full tree is 42,000 nodes and some families hold over a thousand
    species, so a radial layout has to be bounded in both depth and breadth.
    Breadth is trimmed by species count, keeping the largest children and
    folding the remainder into one "N more" placeholder, so nothing silently
    disappears.
    """
    root_id = request.args.get("id", "root")
    root = NODES.get(root_id)
    if root is None:
        abort(404)

    depth = max(1, min(int(request.args.get("depth", 3)), 6))
    fan = max(4, min(int(request.args.get("fan", 36)), 200))
    budget = max(40, min(int(request.args.get("max", 600)), 2000))

    out = {}
    count = 0

    def visit(node, level, limit):
        nonlocal count
        meta = node.get("meta") or {}
        rec = {
            "id": node["id"],
            "name": node["name"],
            "rank": node["rank"],
            "n_species": node.get("n_species", 0),
            "tier": meta.get("tier") if node["rank"] == "species" else node.get("top_tier"),
            "basis": meta.get("basis"),
            "profiled": bool(meta.get("profiled")),
            "serogroup": meta.get("serogroup"),
            "children": [],
            "truncated": 0,
            "has_more": False,
        }
        out[node["id"]] = rec
        count += 1
        used = 1

        # Isolates are below the level this view is about.
        kids = [NODES[c] for c in node["children"] if NODES[c]["rank"] != "isolate"]
        if not kids:
            return used
        if level >= depth or count >= budget or used >= limit:
            rec["has_more"] = True
            return used

        kids.sort(key=lambda n: (-(n.get("n_species") or 0), n["name"].lower()))
        # The top level is the one place breadth is never trimmed: its children
        # are the independent lineages, and dropping one would misstate how many
        # unrelated origins the tree actually has.
        width = len(kids) if node["rank"] == "root" else fan
        shown, hidden = kids[:width], kids[width:]

        # Share the node budget out by sqrt(species) rather than depth-first.
        # Straight DFS let the largest branch swallow everything, which at the
        # top level left the small lineages as bare stubs; sqrt keeps the big
        # ones visibly bigger without starving the rest.
        weights = [max(1.0, (k.get("n_species") or 1) ** 0.5) for k in shown]
        for i, k in enumerate(shown):
            if count >= budget or used >= limit:
                rec["truncated"] += 1
                continue
            rest = sum(weights[i:]) or 1.0
            share = max(2, int((limit - used) * weights[i] / rest))
            rec["children"].append(k["id"])
            used += visit(k, level + 1, share)
        if hidden:
            rec["truncated"] += len(hidden)
        return used

    visit(root, 0, budget)
    return jsonify({
        "root": root_id,
        "depth": depth,
        "fan": fan,
        "nodes": out,
        "path": ancestry(root_id),
        "total_nodes": len(out),
    })


# Group nodes are addressable by name too, so a genus-level signal can link.
GROUP_ID = {n["name"]: n["id"] for n in NODES.values()
            if n["rank"] not in ("species", "isolate")}


def _descend(node):
    """Every species under a node, or the node itself when it is a species."""
    if node["rank"] == "species":
        return [node]
    out, stack = [], list(node["children"])
    while stack:
        cur = NODES.get(stack.pop())
        if cur is None or cur["rank"] == "isolate":
            continue
        if cur["rank"] == "species":
            out.append(cur)
        else:
            stack.extend(cur["children"])
    return out


def _resolve_country(text):
    """Match user input to a country in the travel index, via geo's aliases."""
    low = text.strip().lower()
    for name in geo.travel_names():
        if name.lower() == low:
            return name
    # geo.resolve understands aliases ("USA", "UK", "Viet Nam") and regions.
    countries, _worldwide, _m = geo.resolve(text)
    known = geo.travel_names()
    for name in countries:
        if name in known:
            return name
    return None


def _country_suggestions(text, limit=8):
    low = text.strip().lower()
    return [c for c in sorted(geo.travel_names()) if low in c.lower()][:limit]


def _syndrome_tags(species):
    """The syndrome labels this species scored on, strongest first."""
    rec = DX_BY_SPECIES.get(species)
    if not rec:
        return []
    ranked = sorted(rec["syndromes"].items(), key=lambda kv: -kv[1])
    return [{"key": k, "label": differential.SYNDROMES[k]["label"],
             "score": v, "matched": rec["matched"].get(k)}
            for k, v in ranked]


def _path_tiers(species_id):
    """The ancestor chain with its rolled-up tiers, for refreshing the tree.

    Returned with the correction itself so the client needs one request, not
    one per ancestor, to repaint the rows a correction actually changed.
    """
    out = []
    cur = NODES.get(species_id)
    while cur is not None:
        out.append({"id": cur["id"], "top_tier": cur.get("top_tier"),
                    "tiers": cur.get("tiers", {})})
        cur = NODES.get(cur.get("parent"))
    return out


@app.post("/api/tier")
def api_set_tier():
    """Correct a species' pathogenicity tier.

    The curated layers cover a few hundred species out of 17,554, so a reader
    who knows a tier is wrong needs to be able to fix it. Corrections are
    stored by ICTV binomial in data/overrides.json, applied to the live tree
    immediately, and rolled up to every ancestor.
    """
    body = request.get_json(silent=True) or {}
    node = NODES.get(body.get("id") or "")
    if node is None:
        abort(404, "unknown node")
    if node["rank"] == "isolate":
        node = NODES[node["parent"]]
    if node["rank"] != "species":
        abort(400, "tiers are held on species; correct the species instead")

    tier = body.get("tier")
    if tier not in PAYLOAD["tiers"]:
        abort(400, f"tier must be one of {', '.join(PAYLOAD['tiers'])}")

    meta = node.get("meta") or {}
    was = meta.get("base_tier", meta.get("tier"))
    entry = overrides.set_tier(node["name"], tier, body.get("note", ""), was=was)
    _apply_override(node["name"], entry)
    return jsonify({
        "id": node["id"],
        "species": node["name"],
        "tier": tier,
        "basis": "override",
        "override": entry,
        "tiers": node.get("tiers", {}),
        "path_tiers": _path_tiers(node["id"]),
        "count": overrides.count(),
    })


@app.delete("/api/tier")
def api_clear_tier():
    """Drop a correction and fall back to whatever the build inferred."""
    node = NODES.get(request.args.get("id", ""))
    if node is None:
        abort(404, "unknown node")
    if node["rank"] == "isolate":
        node = NODES[node["parent"]]
    if node["rank"] != "species":
        abort(400, "tiers are held on species")
    gone = overrides.clear(node["name"])
    _drop_override(node["name"])
    meta = node.get("meta") or {}
    return jsonify({
        "id": node["id"],
        "species": node["name"],
        "cleared": bool(gone),
        "tier": meta.get("tier"),
        "basis": meta.get("basis"),
        "tiers": node.get("tiers", {}),
        "path_tiers": _path_tiers(node["id"]),
        "count": overrides.count(),
    })


@app.get("/api/corrections")
def api_corrections():
    """Every stored correction, newest first, for review and undo."""
    stored = overrides.load()
    rows = []
    for species, entry in stored.items():
        sid = SPECIES_ID.get(species)
        rows.append({
            "species": species,
            "id": sid,
            "matched": bool(sid),
            "tier": entry.get("tier"),
            "was": entry.get("was"),
            "note": entry.get("note"),
            "at": entry.get("at"),
        })
    rows.sort(key=lambda r: r["at"] or "", reverse=True)
    return jsonify({"corrections": rows, "legend": PAYLOAD["tiers"]})


@app.get("/api/signals")
def api_signals():
    """Current outbreak reporting, matched to the taxonomy where possible.

    This is WHO Disease Outbreak News: a record of what WHO has formally
    reported, not incidence. Reports that name no pathogen, and reports about
    bacteria, parasites or chemical events, are returned too but flagged, so
    the feed is never silently filtered.
    """
    reports, sources = surveil.all_signals(force=request.args.get("force") == "1")
    node_id = request.args.get("id")
    want = None
    if node_id:
        node = NODES.get(node_id)
        if node is None:
            abort(404)
        # A genus page should show its species' signals too.
        want = {n["name"] for n in _descend(node)} | {node["name"]}

    out = []
    for r in reports:
        taxon = r.get("taxon")
        if want is not None and taxon not in want:
            continue
        row = dict(r)
        if taxon:
            row["node"] = SPECIES_ID.get(taxon) or GROUP_ID.get(taxon)
        out.append(row)

    if node_id:
        return jsonify({"signals": out, "sources": sources, "id": node_id})
    return jsonify({
        "signals": out,
        "sources": sources,
        "ecdc": surveil.ecdc_threat_report(),
        "counts": {
            "total": len(out),
            "matched": sum(1 for r in out if r.get("taxon")),
            "non_viral": sum(1 for r in out if r["kind"] == "non-viral"),
            "unmatched": sum(1 for r in out if r["kind"] == "unmatched"),
        },
    })


@app.get("/api/genomic")
def api_genomic():
    """Nextstrain builds for a species, with a cached summary of each.

    The tree itself is not proxied -- it is 2-20 MB and belongs to Nextstrain.
    What comes back is the build's size, date, clades and geography, plus the
    link.
    """
    node = NODES.get(request.args.get("id", ""))
    if node is None:
        abort(404)
    if node["rank"] == "isolate":
        node = NODES[node["parent"]]
    builds = genomic.for_species(node["name"])
    if not builds:
        return jsonify({"species": node["name"], "builds": [], "summaries": []})
    if request.args.get("summary") != "1":
        return jsonify({"species": node["name"], "builds": builds, "summaries": []})
    force = request.args.get("force") == "1"
    return jsonify({
        "species": node["name"],
        "builds": builds,
        "summaries": [genomic.build_summary(b["prefix"], force=force) for b in builds],
    })


@app.get("/api/travel")
def api_travel():
    """What a traveller returning from one country could have acquired.

    Geographically plausible viral infections, grouped by exposure route and
    filtered against time since return where an incubation window is known.
    Current WHO reports naming the country are attached separately, because
    "reported this year" and "endemic" are different claims.
    """
    country = (request.args.get("country") or "").strip()
    if not country:
        return jsonify({
            # Every destination, not only those with a virus on record.
            "countries": sorted(geo.travel_names()),
            "stats": TRAVEL_STATS,
            "routes": [{"key": k, "label": travel.ROUTE_LABEL.get(k, "Unclear")}
                       for k in travel.ROUTE_ORDER],
        })

    # Accept an alias or any casing: "usa", "UK", "viet nam".
    name = _resolve_country(country)
    if name is None:
        return jsonify({"country": country, "known_country": False,
                        "suggestions": _country_suggestions(country),
                        "regional": [], "groups": [], "worldwide": [],
                        "counts": {}}), 200

    days = request.args.get("days")
    try:
        days = max(0, min(int(days), 3650)) if days not in (None, "") else None
    except ValueError:
        days = None

    out = travel.query(TRAVEL_BY_COUNTRY, TRAVEL_WORLDWIDE, name, days,
                       request.args.get("route") or None)
    out["asked"] = country

    # Attach current reporting for this country, newest first.
    reports, sources = surveil.all_signals()
    low = name.lower()
    out["signals"] = [
        {**r, "node": SPECIES_ID.get(r.get("taxon")) or GROUP_ID.get(r.get("taxon"))}
        for r in reports
        if low in r["title"].lower() and r.get("taxon")
    ][:12]
    out["signal_sources"] = sources
    return jsonify(out)


@app.get("/api/differential")
def api_differential():
    """Candidate viruses for a presenting syndrome.

    Optionally narrowed by destination, exposure route and days since return,
    by intersecting with the travel index. A keyword match over curated prose,
    not a clinical decision aid -- see atlas/differential.py.
    """
    syndrome = request.args.get("syndrome") or ""
    if not syndrome:
        return jsonify({
            "syndromes": [
                {**s, "n": len(DX_BY_SYNDROME.get(s["key"]) or [])}
                for s in differential.syndrome_list()
            ],
            "routes": [{"key": k, "label": travel.ROUTE_LABEL.get(k, "Unclear")}
                       for k in travel.ROUTE_ORDER],
            "countries": sorted(geo.travel_names()),
            "species_indexed": len(DX_BY_SPECIES),
        })
    if syndrome not in differential.SYNDROMES:
        abort(400, f"unknown syndrome: {syndrome}")

    country = (request.args.get("country") or "").strip()
    route = request.args.get("route") or None
    days = request.args.get("days")
    try:
        days = max(0, min(int(days), 3650)) if days not in (None, "") else None
    except ValueError:
        days = None

    travel_rows, resolved = None, None
    if country:
        resolved = _resolve_country(country)
        if resolved:
            got = travel.query(TRAVEL_BY_COUNTRY, TRAVEL_WORLDWIDE,
                               resolved, days, None)
            # Both pools: destination-specific plus cosmopolitan.
            travel_rows = got["regional"] + got["worldwide"]

    rows = differential.query(DX_BY_SYNDROME, syndrome, country=resolved,
                              route=route, days=days, travel_rows=travel_rows)
    info = differential.SYNDROMES[syndrome]
    return jsonify({
        "syndrome": syndrome,
        "label": info["label"],
        "note": info["note"],
        "country": resolved,
        "asked_country": country or None,
        "known_country": bool(resolved) if country else None,
        "route": route,
        "days_since_return": days,
        "candidates": rows,
        "counts": {
            "total": len(rows),
            "unfiltered": len(DX_BY_SYNDROME.get(syndrome) or []),
        },
    })


@app.get("/api/evidence")
def api_evidence():
    """Live literature (Europe PMC) for one species.

    Accepts a species or isolate node id; an isolate resolves to its species,
    since that is the level the evidence describes. Cached after first fetch.
    """
    node = NODES.get(request.args.get("id", ""))
    if node is None:
        abort(404)
    if node["rank"] == "isolate":
        node = NODES[node["parent"]]
    if node["rank"] != "species":
        abort(400, "evidence lookup applies to a species")

    meta = node.get("meta") or {}
    names = []
    for cid in node["children"]:
        iso = NODES[cid].get("meta") or {}
        names.extend(iso.get("names") or [])

    result = enrich.lookup(
        node["name"],
        {
            "names": names,
            "family": meta.get("family"),
            "genus": meta.get("genus"),
            "serogroup": meta.get("serogroup"),
            "host": meta.get("host"),
        },
        refresh=request.args.get("refresh") == "1",
    )
    result["node_id"] = node["id"]
    return jsonify(result)


@app.get("/api/pathogens")
def api_pathogens():
    """Every species with human-relevant evidence, grouped by tier.

    This used to list only the species carrying a long-form profile, which
    meant 57 entries and no herpesviruses, no HBV, no HIV, no measles -- an
    index of what happened to be written up rather than of what infects
    people. It now lists every species whose tier says something about human
    infection, whatever layer assigned it, and says which layer that was.

    "unassessed" is excluded on purpose: it is the absence of a finding, and
    13,000 rows of "we have not looked" is not an index.
    """
    # "no-evidence" and "unassessed" are both excluded: the first is 13,000
    # bacteriophages and plant viruses whose host range rules humans out, the
    # second is the absence of a finding. Neither belongs in an index of what
    # infects people.
    include = ["established", "probable", "possible", "animal-only"]
    tiers = {k: [] for k in include}
    for e in SEARCH_INDEX:
        if e["rank"] != "species":
            continue
        node = NODES[e["id"]]
        meta = node.get("meta") or {}
        tier = meta.get("tier")
        if tier not in tiers:
            continue
        prof = meta.get("profile") or {}
        # A common name if we have one: the profile's, else the ICTV record's
        # first isolate name, which is what a reader will recognise.
        common = (prof.get("names") or [None])[0]
        if not common:
            for cid in node["children"]:
                names = (NODES[cid].get("meta") or {}).get("names") or []
                if names:
                    common = names[0]
                    break
        tiers[tier].append(
            {
                "id": e["id"],
                "name": node["name"],
                "common": common if common != node["name"] else None,
                "family": meta.get("family"),
                "genus": meta.get("genus"),
                "serogroup": meta.get("serogroup"),
                "headline": prof.get("headline") or meta.get("tier_note"),
                "basis": meta.get("basis"),
                "profiled": bool(meta.get("profiled")),
            }
        )
    for v in tiers.values():
        # Profiled entries first within a family, since they carry the detail.
        v.sort(key=lambda x: (x["family"] or "", not x["profiled"], x["name"]))
    return jsonify({
        "tiers": tiers,
        "legend": PAYLOAD["tiers"],
        "counts": {k: len(v) for k, v in tiers.items()},
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5057, debug=True)
