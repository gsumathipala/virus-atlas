"""Build atlas.json from the ICTV Virus Metadata Resource spreadsheet.

Produces a single nested tree:

  Realm -> Subrealm -> Kingdom -> ... -> Family -> Subfamily -> Genus
        -> [Serogroup] -> [Antigenic clade] -> Species -> Isolate

Serogroup and clade levels are synthetic -- they come from atlas/serogroups.py,
not from ICTV -- and are inserted only where an assignment exists. Species in a
genus that has serogroups but no assignment for that species land under
"Unassigned within genus" so nothing is silently dropped.

Usage:  python -m atlas.build [path/to/VMR.xlsx]
"""

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import openpyxl

from atlas import human, profiles
from atlas.serogroups import SEROGROUPS, serogroup_for

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SHEET_HINT = "VMR"

RANKS = [
    ("Realm", "realm"),
    ("Subrealm", "subrealm"),
    ("Kingdom", "kingdom"),
    ("Subkingdom", "subkingdom"),
    ("Phylum", "phylum"),
    ("Subphylum", "subphylum"),
    ("Class", "class"),
    ("Subclass", "subclass"),
    ("Order", "order"),
    ("Suborder", "suborder"),
    ("Family", "family"),
    ("Subfamily", "subfamily"),
    ("Genus", "genus"),
    ("Subgenus", "subgenus"),
]

HOST_LABELS = {
    "vertebrates": "Vertebrates",
    "invertebrates": "Invertebrates",
    "plants": "Plants",
    "fungi": "Fungi",
    "bacteria": "Bacteria",
    "archaea": "Archaea",
    "protists": "Protists",
    "algae": "Algae",
}



def slug(text):
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text or "x"


def unlink(value):
    """Strip =HYPERLINK("url","label") formulas down to the label."""
    if value is None:
        return None
    s = str(value).strip()
    m = re.match(r'^=HYPERLINK\("([^"]*)"\s*,\s*"([^"]*)"\)$', s)
    if m:
        return m.group(2)
    return s or None


def hyperlink_url(value):
    if value is None:
        return None
    m = re.match(r'^=HYPERLINK\("([^"]*)"', str(value).strip())
    return m.group(1) if m else None


def split_names(value):
    if not value:
        return []
    return [p.strip() for p in re.split(r"[;,]\s*", str(value)) if p.strip()]


class Node:
    __slots__ = ("name", "rank", "id", "children", "_index", "meta")

    def __init__(self, name, rank, node_id):
        self.name = name
        self.rank = rank
        self.id = node_id
        self.children = []
        self._index = {}
        self.meta = {}

    def child(self, name, rank):
        key = (rank, name)
        node = self._index.get(key)
        if node is None:
            node = Node(name, rank, f"{self.id}/{slug(name)}")
            self._index[key] = node
            self.children.append(node)
        return node


def load_rows(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    sheet = next(
        (ws for ws in wb.worksheets if SHEET_HINT in ws.title.upper()),
        wb.worksheets[0],
    )
    rows = sheet.iter_rows(values_only=True)
    header = next(rows)
    idx = {name: i for i, name in enumerate(header) if name}
    required = {"Species", "Genus", "Family", "Realm", "Virus name(s)"}
    missing = required - set(idx)
    if missing:
        raise SystemExit(f"VMR sheet is missing expected columns: {sorted(missing)}")
    out = []
    for row in rows:
        if not row or not row[idx["Species"]]:
            continue
        out.append({name: row[i] for name, i in idx.items()})
    return out


def build_tree(rows):
    root = Node("All viruses", "root", "root")
    stats = Counter()

    for row in rows:
        species = unlink(row.get("Species"))
        if not species:
            continue
        genus = unlink(row.get("Genus"))
        node = root

        for column, rank in RANKS:
            value = unlink(row.get(column))
            if not value:
                continue
            node = node.child(value, rank)
            if rank == "genus" and genus in SEROGROUPS:
                sg, clade = serogroup_for(genus, species)
                node = node.child(sg or "Unassigned within genus", "serogroup")
                if clade:
                    node = node.child(clade, "clade")

        sp = node.child(species, "species")
        if not sp.meta:
            sp.meta = species_meta(species, row)
            stats["species"] += 1

        isolate = {
            "names": split_names(unlink(row.get("Virus name(s)"))),
            "abbrev": split_names(unlink(row.get("Virus name abbreviation(s)"))),
            "designation": unlink(row.get("Virus isolate designation")),
            "exemplar": (unlink(row.get("Exemplar or additional isolate")) or "").upper() == "E",
            "accession": unlink(row.get("Virus GENBANK accession")),
            "coverage": unlink(row.get("Genome coverage")),
            "genome": unlink(row.get("Genome")),
            "host": unlink(row.get("Host source")),
            "ictv_url": hyperlink_url(row.get("ICTV_ID")),
        }
        sp.children.append(
            Node(isolate["names"][0] if isolate["names"] else species, "isolate",
                 f"{sp.id}/i{len(sp.children)}")
        )
        sp.children[-1].meta = isolate
        stats["isolates"] += 1

    return root, stats


def species_meta(species, row):
    genus = unlink(row.get("Genus"))
    family = unlink(row.get("Family"))
    host = unlink(row.get("Host source")) or ""
    sg, clade = serogroup_for(genus, species)
    prof = profiles.get(species)

    meta = {
        "species": species,
        "genus": genus,
        "family": family,
        "genome": unlink(row.get("Genome")),
        "host": host,
        "hosts": [HOST_LABELS.get(h.strip().replace(" (S)", ""), h.strip())
                  for h in re.split(r",\s*", host) if h.strip()],
        "serogroup": sg,
        "clade": clade,
        "profiled": bool(prof),
    }
    if prof:
        meta["profile"] = prof
        meta["tier"] = prof["tier"]
        meta["basis"] = "profile"
    return meta


def assess_tiers(nodes):
    """Fill in the tier for every species that has no curated profile.

    Deferred to its own pass because the strongest signal short of a profile is
    the ICTV record's own isolate names, and those are only complete once every
    row of the spreadsheet has been read.
    """
    tally = Counter()
    for n in nodes.values():
        if n["rank"] != "species":
            continue
        meta = n.setdefault("meta", {})
        if meta.get("tier"):
            tally[meta["basis"]] += 1
            continue
        names = []
        for cid in n["children"]:
            names += (nodes[cid].get("meta") or {}).get("names") or []
        tier, basis, note = human.classify(
            n["name"], meta.get("genus"), meta.get("host"), names)
        meta["tier"] = tier
        meta["basis"] = basis
        meta["tier_note"] = note
        tally[basis] += 1
    return tally


def check_serogroups(nodes):
    """Serogroup epithets that match no species in this VMR release.

    These fail silently: serogroup_for() simply does not match, and the
    species lands in "Unassigned within genus" with nothing to say it should
    have been placed. An audit found 28 of them, from ICTV renames and
    merges, so the check now runs on every build.
    """
    from atlas.serogroups import SEROGROUPS
    by_genus = {}
    for node in nodes.values():
        if node["rank"] != "species":
            continue
        genus = (node.get("meta") or {}).get("genus")
        if genus:
            by_genus.setdefault(genus, set()).add(node["name"].split(" ", 1)[-1])
    out = []
    for genus, groups in SEROGROUPS.items():
        pool = by_genus.get(genus, set())
        if not pool:
            out.append((genus, "*", "genus absent from this release"))
            continue
        for serogroup, epithets in groups.items():
            for epithet in epithets:
                if epithet not in pool:
                    out.append((genus, serogroup, epithet))
    return out


def check_reference(nodes):
    """Warn about REFERENCE keys that match no species in this VMR release.

    ICTV renames species between releases, so a stale key would silently stop
    applying. Better to say so at build time than to quietly mislabel.
    """
    known = {n["name"] for n in nodes.values() if n["rank"] == "species"}
    known |= {(n.get("meta") or {}).get("genus") for n in nodes.values()}
    return sorted(k for k in human.REFERENCE if k not in known)


def flatten(node, out, parent=None, depth=0):
    """Emit a flat dict of nodes for the API, with child id lists."""
    record = {
        "id": node.id,
        "name": node.name,
        "rank": node.rank,
        "parent": parent,
        "depth": depth,
        "children": [c.id for c in node.children],
    }
    if node.meta:
        record["meta"] = node.meta
    if node.rank in ("family", "genus"):
        note = profiles.taxon_note(node.name)
        if note:
            record["note"] = note
    out[node.id] = record
    for c in node.children:
        flatten(c, out, node.id, depth + 1)
    return out


def summarise(nodes):
    """Roll up counts and the strongest pathogenicity tier to every ancestor."""
    order = sorted(nodes.values(), key=lambda n: -n["depth"])
    rank_of = {k: v["rank"] for k, v in profiles.TIERS.items()}

    for n in order:
        counts = Counter()
        best = 99
        species_total = 0
        if n["rank"] == "species":
            species_total = 1
            tier = n.get("meta", {}).get("tier", "no-evidence")
            counts[tier] += 1
            best = rank_of.get(tier, 99)
        for cid in n["children"]:
            c = nodes[cid]
            counts.update(c.get("tiers", {}))
            species_total += c.get("n_species", 0)
            best = min(best, c.get("_best", 99))
        n["tiers"] = dict(counts)
        n["n_species"] = species_total
        n["_best"] = best
        n["top_tier"] = next(
            (k for k, v in profiles.TIERS.items() if v["rank"] == best), None
        )
        if n["rank"] == "species":
            n["n_isolates"] = len(n["children"])

    for n in nodes.values():
        n.pop("_best", None)
    return nodes


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA / "raw" / "vmr.xlsx"
    if not src.exists():
        raise SystemExit(f"VMR spreadsheet not found at {src}")
    print(f"reading {src}")
    rows = load_rows(src)
    print(f"  {len(rows)} isolate rows")

    root, stats = build_tree(rows)
    nodes = flatten(root, {})
    tally = assess_tiers(nodes)
    nodes = summarise(nodes)
    print(f"  {stats['species']} species, {stats['isolates']} isolates, {len(nodes)} tree nodes")
    print("  tier basis: " + ", ".join(f"{k} {v}" for k, v in tally.most_common()))
    dangling = check_serogroups(nodes)
    if dangling:
        print(f"  !! {len(dangling)} serogroup epithets match no species:")
        for genus, serogroup, epithet in dangling[:20]:
            print(f"       {genus} / {serogroup}: {epithet}")

    stale = check_reference(nodes)
    if stale:
        print(f"  !! {len(stale)} REFERENCE entries match no species in this release:")
        for k in stale:
            print(f"       {k}")

    DATA.mkdir(exist_ok=True)
    out = DATA / "atlas.json"
    payload = {
        "source": {
            "name": "ICTV Virus Metadata Resource",
            "file": src.name,
            "url": "https://ictv.global/vmr",
        },
        "tiers": profiles.TIERS,
        "nodes": nodes,
    }
    out.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")

    profiled = sum(1 for n in nodes.values()
                   if n.get("meta", {}).get("profiled"))
    print(f"  {profiled} species carry a curated pathogenicity profile")


if __name__ == "__main__":
    main()
