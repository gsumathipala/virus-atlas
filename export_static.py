"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Build a static copy of the atlas for GitHub Pages.

GitHub Pages serves files, not programs, so the Flask API has to be turned
into something a browser can fetch directly. This writes that: the same front
end, plus pre-rendered JSON for everything the server used to compute, plus a
`fetch` interceptor (static/js/static-api.js) that answers `/api/...` from
those files.

What survives, what changes
---------------------------
Everything derived from the atlas is pre-rendered and behaves identically:
the tree, search, the radial view, the pathogen index, travel exposure and
the differential.

The live sources keep working, because all four allow cross-origin browser
requests -- Europe PMC, WHO, Nextstrain and gov.uk all send
`access-control-allow-origin: *`. The browser calls them directly instead of
going through Flask, so the literature lookup, outbreak signals and genomic
builds are still live. The only cost is that responses are no longer cached
server-side, so a repeat lookup re-fetches.

Tier corrections change meaning. There is no server to write
`data/overrides.json`, so they are kept in the browser's localStorage: they
persist for that person in that browser and are not shared or published. The
interface says so.

Sharding
--------
The atlas is 40 MB, which nobody should download to look at one virus. Nodes
are bundled by their family -- or, where ICTV assigns none, by their genus:
1,311 bundles, median 2 KB, fetched on demand. Family rank and above go in a
skeleton that loads first, so the whole upper tree and every group's page are
answered without a second request. Isolates are in neither: the species
record already carries their metadata, and the browser rebuilds the isolate
nodes from it.
"""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

sys.path.insert(0, str(ROOT))
import app as A                                    # noqa: E402
from atlas import differential, geo, travel        # noqa: E402


def slug(node_id):
    return node_id.split("/")[-1] or "root"


def family_of(node_id):
    """The family ancestor's id, or None for ranks above family."""
    parts = node_id.split("/")
    for i in range(len(parts), 0, -1):
        anc = "/".join(parts[:i])
        node = A.NODES.get(anc)
        if node and node["rank"] == "family":
            return anc
    return None


def bundle_root(node_id):
    """The node whose bundle holds this one.

    Normally its family. But ICTV leaves 884 genera -- nearly all of them
    Caudoviricetes -- unassigned to any family, and the 2,611 species under
    them need a bundle too, so those go under their nearest group ancestor,
    which has no family either and is therefore in the skeleton. Keying on
    the family alone left those species in no file at all, and every one of
    their pages answered "not found".
    """
    parts = node_id.split("/")
    fam = group = None
    for i in range(1, len(parts) + 1):
        anc = "/".join(parts[:i])
        node = A.NODES.get(anc)
        if node is None or anc == node_id:
            continue
        if node["rank"] == "family":
            fam = anc
        elif node["rank"] not in ("species", "isolate"):
            group = anc
    return fam or group


def write(path, payload, label=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    path.write_text(text, encoding="utf-8")
    if label:
        print(f"  {label:<34}{len(text)/1024:>8.0f} KB")
    return len(text)


def main():
    HOIST_KEYS.clear()
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    total = 0

    # ---------------------------------------------------------------- assets
    print("assets")
    shutil.copytree(ROOT / "static", SITE / "static")
    tpl = (ROOT / "templates" / "index.html").read_text()
    # Jinja is a server-side thing; resolve the two tags it uses by hand.
    tpl = re.sub(r"\{\{\s*url_for\('static',\s*filename='([^']+)'\)\s*\}\}",
                 r"static/\1", tpl)
    tpl = tpl.replace("{{ source.url }}", A.PAYLOAD["source"]["url"])
    tpl = tpl.replace("{{ source.file }}", A.PAYLOAD["source"]["file"])
    # The interceptor must be installed before app.js runs.
    tpl = tpl.replace('<script src="static/js/figures.js"></script>',
                      '<script src="static/js/static-api.js"></script>\n'
                      '<script src="static/js/figures.js"></script>')
    assert "static-api.js" in tpl, "failed to inject the static API shim"
    (SITE / "index.html").write_text(tpl, encoding="utf-8")
    (SITE / ".nojekyll").write_text("")       # keep Pages from eating _dirs
    print(f"  index.html + static/        {len(tpl)/1024:>8.0f} KB")

    api = SITE / "api"

    # ------------------------------------------------------------------ meta
    print("\ncore")
    with A.app.test_request_context("/api/meta"):
        meta = A.api_meta().get_json()
    meta["static"] = True
    total += write(api / "meta.json", meta, "meta.json")

    # -------------------------------------------------------------- skeleton
    # Family rank and above: the whole /api/node answer for each one, with
    # children reduced to ids. This is the first thing the client loads, so a
    # group's page -- its particle, its highlights, what it contains -- draws
    # without fetching anything further.
    #
    # It used to hold a trimmed tree row instead, and because the client
    # prefers the skeleton to the bundles, that trimmed row was what the
    # family page was built from: Ampullaviridae lost its bottle-shaped
    # virion, every group lost its roster of pathogenic species, and the
    # contents list was handed bare id strings to render as rows.
    tables = {k: {} for k in ("morphology", "baltimore", "biosafety",
                              "receptors", "countermeasures", "therapeutics",
                              "crossreact")}
    skeleton = {}
    for node in A.NODES.values():
        if node["rank"] in ("species", "isolate"):
            continue
        if family_of(node["id"]) and node["rank"] != "family":
            continue
        rec = detail_for(node["id"], tables)
        rec["children"] = [c["id"] for c in rec.get("children") or []]
        skeleton[node["id"]] = rec
    total += write(api / "skeleton.json", skeleton, "skeleton.json")

    # --------------------------------------------------------------- bundles
    # One file per bundle root: every node under it, in the full shape
    # /api/node would have returned, so the client never needs a second
    # request once it has the file.
    print("\nbundles")
    buckets = {}
    for node_id, node in A.NODES.items():
        # Isolates are reconstituted in the browser from the species record
        # that already carries their metadata, and whatever is in the
        # skeleton is already answered, so neither is written again here.
        if node["rank"] == "isolate" or node_id in skeleton:
            continue
        root = bundle_root(node_id)
        if root is None:
            continue
        buckets.setdefault(root, {})[node_id] = detail_for(node_id, tables)
    # A file name per bundle root. Two roots can end in the same segment now
    # that genera are roots too, and a case-insensitive file system would
    # quietly merge them, so the names are made unique here.
    names, taken = {}, set()
    for root in buckets:
        name, n = slug(root), 2
        while name.lower() in taken:
            name, n = f"{slug(root)}-{n}", n + 1
        taken.add(name.lower())
        names[root] = name

    sizes = []
    for root, nodes in buckets.items():
        size = write(api / "bundle" / f"{names[root]}.json", nodes)
        sizes.append((size, root))
        total += size
    sizes.sort(reverse=True)
    print(f"  {len(sizes)} bundles, {sum(s for s, _ in sizes)/1e6:.1f} MB")
    for s, f in sizes[:3]:
        print(f"     largest: {names[f]:<28}{s/1024:>8.0f} KB")
    med = sorted(s for s, _ in sizes)[len(sizes)//2]
    print(f"     median:  {med/1024:.0f} KB")

    # Which bundle holds a node: the client needs this to know what to fetch.
    index = dict(names)
    total += write(api / "bundle-index.json", index, "bundle-index.json")
    total += write(api / "tables.json", tables, "tables.json")

    # ---------------------------------------------------------------- search
    print("\nderived views")
    search = [{
        "id": e["id"], "name": e["name"], "rank": e["rank"],
        "tier": e["tier"], "serogroup": e["serogroup"], "family": e["family"],
        "terms": e["terms"][:8],
        "profiled": e["profiled"], "n_species": e["n_species"],
    } for e in A.SEARCH_INDEX]
    total += write(api / "search.json", search, "search.json")

    with A.app.test_request_context("/api/pathogens"):
        total += write(api / "pathogens.json", A.api_pathogens().get_json(),
                       "pathogens.json")

    # Travel: one file per destination, plus the picker list.
    dests = sorted(geo.travel_names())
    total += write(api / "travel-index.json",
                   {"countries": dests, "stats": A.TRAVEL_STATS,
                    "routes": [{"key": k, "label": travel.ROUTE_LABEL.get(k, "Unclear")}
                               for k in travel.ROUTE_ORDER]},
                   "travel-index.json")
    total += write(api / "travel-worldwide.json", A.TRAVEL_WORLDWIDE,
                   "travel-worldwide.json")
    tsize = 0
    for name in dests:
        out = travel.query(A.TRAVEL_BY_COUNTRY, A.TRAVEL_WORLDWIDE, name,
                           None, None, known=True)
        out["asked"] = name
        out.pop("worldwide")          # shared; the client merges it back in
        tsize += write(api / "travel" / f"{country_slug(name)}.json", out)
    print(f"  travel/ ({len(dests)} files)        {tsize/1e6:>8.1f} MB")
    total += tsize

    # Differential: one file per syndrome, unfiltered. Country, route and day
    # filters are applied in the browser against the travel files.
    total += write(api / "differential-index.json", {
        "syndromes": [{**s, "n": len(A.DX_BY_SYNDROME.get(s["key"]) or [])}
                      for s in differential.syndrome_list()],
        "routes": [{"key": k, "label": travel.ROUTE_LABEL.get(k, "Unclear")}
                   for k in travel.ROUTE_ORDER],
        "countries": dests,
        "species_indexed": len(A.DX_BY_SPECIES),
    }, "differential-index.json")
    dsize = 0
    for key, info in differential.SYNDROMES.items():
        dsize += write(api / "differential" / f"{key}.json", {
            "syndrome": key, "label": info["label"], "note": info["note"],
            "candidates": A.DX_BY_SYNDROME.get(key) or [],
        })
    print(f"  differential/ ({len(differential.SYNDROMES)} files)  {dsize/1024:>8.0f} KB")
    total += dsize

    # Disease -> taxon map, so the browser can classify WHO and UKHSA items.
    from atlas import surveil
    total += write(api / "diseases.json", {
        "diseases": [{"rx": rx, "kind": kind, "taxon": taxon, "label": label,
                      "node": A.SPECIES_ID.get(taxon) or A.GROUP_ID.get(taxon)}
                     for rx, kind, taxon, label in surveil.DISEASES],
        "non_viral": surveil.NON_VIRAL.pattern,
    }, "diseases.json")

    # Nextstrain build list, so the browser knows what to offer.
    from atlas import genomic
    total += write(api / "genomic.json",
                   {k: [{"prefix": p, "label": lab,
                         "url": f"https://nextstrain.org/{p}"}
                        for p, lab in v]
                    for k, v in genomic.DATASETS.items()},
                   "genomic.json")

    print(f"\ntotal {total/1e6:.1f} MB in {sum(1 for _ in SITE.rglob('*') if _.is_file())} files")
    print(f"wrote {SITE}")


def country_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# Fields that are the same for every member of a family, or derivable from a
# key, are hoisted into tables.json and referenced instead of repeated. Before
# this the Rhabdoviridae bundle was 2.5 MB, of which 971 KB was the ancestry
# path restated on all 687 nodes and 538 KB was one morphology spec and one
# Baltimore record copied per species.
HOISTED = ("path", "id", "morphology", "baltimore", "biosafety",
           "receptors", "countermeasures", "therapeutics", "crossreact")


HOIST_KEYS = {}


def hoist(tables, field, prefer, value):
    """Store `value` in a table once and return the key that reaches it.

    Keyed by content, not by name; the name is only a preference, used when
    free and otherwise suffixed. Keying on the name alone kept whichever
    record arrived first and served it to everything else that shared the
    name, and 47 families draw more than one particle -- the spec follows the
    representative genome, and a family's genera do not all share one -- so
    1,188 nodes were handed a sibling's virion and genome. `host-range` is a
    basis rather than an answer and is one key for every host, which happens
    to be harmless today and would not stay that way.
    """
    blob = json.dumps(value, sort_keys=True, ensure_ascii=False)
    seen = HOIST_KEYS.setdefault(field, {})
    if blob in seen:
        return seen[blob]
    key, n = prefer, 2
    while key in tables[field]:
        key, n = f"{prefer} ({n})", n + 1
    tables[field][key] = value
    seen[blob] = key
    return key


def detail_for(node_id, tables):
    """What /api/node returns, with the shared parts moved into tables."""
    with A.app.test_request_context(f"/api/node?id={node_id}"):
        rec = A.api_node().get_json()
    meta = rec.get("meta") or {}
    name = rec["name"]

    if rec.get("morphology"):
        # Name the slot after the family, since architecture is a family
        # property. Group nodes carry no meta.family, so fall back to the
        # family ancestor in the path and only then to the node's own name --
        # otherwise every genus minted its own key and the table grew to
        # 2,699 near-identical rows.
        fam = meta.get("family")
        if not fam:
            anc = family_of(node_id)
            fam = A.NODES[anc]["name"] if anc else name
        rec["morphology_key"] = hoist(tables, "morphology", fam,
                                      rec["morphology"])
    if rec.get("baltimore"):
        # The caveat note is per-species; keep it, hoist the rest.
        spec = {k: v for k, v in rec["baltimore"].items() if k != "note"}
        rec["baltimore_key"] = hoist(tables, "baltimore",
                                     rec["baltimore"].get("key")
                                     or "unassigned", spec)
        if rec["baltimore"].get("note"):
            rec["baltimore_note"] = rec["baltimore"]["note"]
    # Biosafety answers at three levels and says which in `basis`. Keying all
    # of them by species stored one family default 9,646 times, 4.5 MB of it.
    bs = rec.get("biosafety")
    if bs:
        basis = bs.get("basis")
        prefer = (name if basis == "species"
                  else f"family:{bs.get('family') or meta.get('family')}"
                  if basis == "family" else "host-range")
        rec["biosafety_ref"] = hoist(tables, "biosafety", prefer, bs)

    for field in ("receptors", "countermeasures", "therapeutics",
                  "crossreact"):
        value = rec.get(field)
        if value:
            rec[f"{field}_ref"] = hoist(tables, field, name, value)

    for field in HOISTED:
        rec.pop(field, None)
    return rec


if __name__ == "__main__":
    main()
