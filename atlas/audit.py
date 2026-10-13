"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Check the curated data against itself, and against the VMR.

    python -m atlas.audit

Why this exists
---------------
The curated layers carry a few thousand factual claims, and a reader cannot
tell a checked one from an unchecked one. Most of them can only be validated
against the literature, one at a time, by someone who knows the field. But a
large minority contradict something the atlas already holds, and those can be
found mechanically and exhaustively -- which is the only kind of "I checked
all of it" worth saying.

So this looks for disagreement rather than for truth: a profile whose vectors
say "None" while its transmission describes a mosquito; an incubation period
written in prose the travel view cannot parse, so the virus silently drops out
of every time-since-return filter; a species assigned a containment level
below its family's default with nothing said about why; a countermeasure
record claiming nothing is licensed beside a therapeutics record naming a
licensed drug. Each of those is either a data error or a missing explanation.

It is not a substitute for reading the claims. It is what makes reading them
tractable, by taking the mechanical cases off the pile first.
"""

import re
import sys
from collections import Counter

from atlas import (countermeasures, crossreact, differential, geo, human,
                   morphology, profiles, receptors, therapeutics, travel)

VECTOR_WORDS = re.compile(
    r"\b(mosquito|aedes|culex|anopheles|haemagogus|sabethes|tick|ixodes|"
    r"hyalomma|amblyomma|dermacentor|haemaphysalis|midge|culicoides|"
    r"sandfly|phlebotomus|lutzomyia|flea|louse|mite|triatomine|cimex|"
    r"bat bug|\bbug)\b", re.I)

TIERS = ("established", "probable", "possible")


def findings(nodes, species_id):
    """Every disagreement found, as (layer, severity, species, what)."""
    out = []
    def flag(layer, species, what, severity="error"):
        out.append((layer, severity, species, what))

    by_name = {n["name"]: n for n in nodes.values() if n["rank"] == "species"}
    known = geo.travel_names()

    # ---------------------------------------------------------- profiles
    for name, p in profiles.P.items():
        node = by_name.get(name)
        if node is None:
            flag("profiles", name, "profile key matches no ICTV species")
            continue
        meta = node.get("meta") or {}

        vectors = "; ".join(p.get("vectors") or [])
        says_none = bool(re.match(r"^\s*none", vectors, re.I))
        vector_in_prose = VECTOR_WORDS.search(p.get("transmission") or "")
        if says_none and vector_in_prose:
            flag("profiles", name,
                 f'vectors say "{vectors}" but transmission names '
                 f'"{vector_in_prose.group(0)}"')
        if not says_none and vectors and not VECTOR_WORDS.search(vectors):
            flag("profiles", name, f'vectors "{vectors}" name no known vector',
                 "check")

        # An incubation period written with numbers in it that the travel
        # view cannot parse loses a window it could have had. Prose that
        # states ignorance -- "Not established." -- is not a failure: the
        # entry keeps an "unknown" window and survives the day filter.
        inc = p.get("incubation") or ""
        if inc and travel.incubation_days(inc) is None:
            flag("profiles", name,
                 f'incubation "{inc}" does not parse to a window',
                 "error" if re.search(r"\d", inc) else "check")

        # Geography that resolves to nothing, and no other source of it.
        text = p.get("geography") or ""
        countries, worldwide, _m = geo.resolve(text)
        if not countries and not worldwide and not geo.eradicated(text) \
                and not profiles.country_grades(name) \
                and name not in profiles.WORLDWIDE:
            flag("profiles", name, f'geography "{text[:60]}" resolves to no country')

        if p.get("tier") != meta.get("tier") and meta.get("basis") != "override":
            flag("profiles", name,
                 f'profile tier {p.get("tier")!r} != atlas tier {meta.get("tier")!r}')

        for field in ("names", "headline", "syndrome", "transmission", "vectors",
                      "reservoir", "geography", "incubation", "diagnosis",
                      "management", "prevention", "evidence", "refs"):
            if not p.get(field):
                flag("profiles", name, f"{field} is empty")
        # A reference needs something a reader can follow: a URL, a DOI or a
        # PMID. A bare label -- "VEE epidemiology reviews" -- cites nothing.
        for ref in p.get("refs") or []:
            if not (str(ref.get("url", "")).startswith("http")
                    or ref.get("doi") or ref.get("pmid")):
                flag("profiles", name,
                     f'reference cites nothing followable: {ref.get("label")!r}')

        if p.get("cycle") and p["cycle"] not in (
                "vector", "rodent-excreta", "intermediate", "wildlife-contact",
                "animal-bite", "respiratory", "close-contact", "blood-sexual",
                "faecal-oral", "direct"):
            flag("profiles", name, f'unknown cycle {p["cycle"]!r}')

    # ------------------------------------------------- the reference list
    # Three REFERENCE keys are genus names, consumed by GENUS_REFERENCE's
    # epithet-prefix rules rather than matched to a species. They are not
    # dead keys, so they are not reported as such.
    genus_keys = set(getattr(human, "GENUS_REFERENCE", {}))
    for name, (tier, note) in human.REFERENCE.items():
        if name not in by_name and name not in genus_keys:
            flag("human", name, "reference key matches no ICTV species")
        if tier not in TIERS + ("animal-only", "no-evidence", "unassessed"):
            flag("human", name, f"unknown tier {tier!r}")
        if name in profiles.P and profiles.P[name].get("tier") != tier:
            flag("human", name,
                 f"reference tier {tier!r} != profile tier "
                 f"{profiles.P[name].get('tier')!r}")

    # ----------------------------------------------------- the geography
    for name, entry in profiles.COUNTRIES.items():
        if name not in by_name:
            flag("geography", name, "COUNTRIES key matches no ICTV species")
        elif (by_name[name].get("meta") or {}).get("tier") not in TIERS:
            grades = set(profiles.country_grades(name).values())
            if grades - {"reservoir", "vector"}:
                flag("geography", name,
                     "has human-evidence countries but is not a human pathogen",
                     "check")
        if entry is None:
            flag("geography", name,
                 "COUNTRIES entry is None, which reads the same as absent",
                 "check")
        grades = profiles.country_grades(name)
        for c, grade in grades.items():
            if c not in known:
                flag("geography", name, f"country {c!r} is not a destination")
            if grade not in profiles.EVIDENCE_GRADES:
                flag("geography", name,
                     f"{c}: unknown evidence grade {grade!r}")
    for name in profiles.WORLDWIDE:
        if name not in by_name:
            flag("geography", name, "WORLDWIDE key matches no ICTV species")
        elif name in profiles.COUNTRIES:
            flag("geography", name,
                 "is both cosmopolitan and has a country list")

    # ------------------------------------------------------ countermeasures
    for name in countermeasures.covered():
        if name not in by_name:
            flag("countermeasures", name, "key matches no ICTV species")
            continue
        cm = countermeasures.get(name)
        tx = therapeutics.get(name)
        if not cm.get("any") and tx and tx.get("any_licensed_antiviral"):
            flag("countermeasures", name,
                 "countermeasures say nothing is licensed; therapeutics name "
                 "a licensed antiviral")

    for name in therapeutics.covered():
        if name not in by_name:
            flag("therapeutics", name, "key matches no ICTV species")

    # ----------------------------------------------------------- receptors
    for name in receptors.covered():
        if name not in by_name:
            flag("receptors", name, "key matches no ICTV species")
            continue
        rec = receptors.get(name)
        if not rec.get("receptors"):
            flag("receptors", name, "no receptor listed")

    # --------------------------------------------------------- crossreact
    for cname, rec in crossreact.COMPLEXES.items():
        for m in rec.get("members", []):
            if m not in by_name:
                flag("crossreact", cname, f"member {m!r} matches no ICTV species")
        for g in rec.get("genera", []):
            if not any((n.get("meta") or {}).get("genus") == g
                       for n in by_name.values()):
                flag("crossreact", cname, f"genus {g!r} matches no ICTV genus")

    # --------------------------------------------------------- morphology
    # The segment count a group page draws, against what the accessions under
    # it spell out. Checked per genus, not per family, because it varies by
    # genus inside Sedoreoviridae, Rhabdoviridae, Closteroviridae,
    # Potyviridae, Virgaviridae and Tombusviridae.
    import app as _app
    for node in nodes.values():
        if node["rank"] != "genus":
            continue
        spec = _app.group_morphology(node)
        if not spec or not spec.get("segments"):
            continue
        hint = _app.segment_hint(node["id"])
        if hint and hint != spec["segments"]:
            flag("morphology", node["name"],
                 f'page draws {spec["segments"]} segments; the accessions '
                 f'under it show {hint}')

    # ---------------------------------------------------------- morphology
    # Keys in the family table that no longer name a family. They are
    # unreachable -- spec_for is only ever called with a family name out of
    # the VMR -- so they are stale rather than harmful, but they look like
    # coverage that is not there.
    from atlas import morphology as _morph
    fam_names = {n["name"] for n in nodes.values() if n["rank"] == "family"}
    ranks = {n["name"]: n["rank"] for n in nodes.values()}
    for key in sorted(_morph.FAMILIES):
        if key not in fam_names:
            was = ranks.get(key)
            flag("morphology", key,
                 f"is a {was}, not a family" if was else
                 "names no family in this release of the taxonomy", "check")
    # A family holding a human pathogen and drawing a generic particle.
    for node in nodes.values():
        if node["rank"] != "species":
            continue
        meta = node.get("meta") or {}
        if meta.get("tier") in ("established", "probable") \
                and meta.get("family") and meta["family"] not in _morph.FAMILIES:
            flag("morphology", meta["family"],
                 f"holds {node['name']}, an {meta['tier']} human pathogen, "
                 "and has no particle of its own")

    # ----------------------------------------------------------- biosafety
    # Every select-agent badge against the regulation, in both directions. A
    # badge on the wrong virus is a legal claim, and a missing one hides a
    # registration duty.
    from atlas import biosafety
    for sp, rec in biosafety.BIOSAFETY.items():
        claimed = rec.get("select_agent")
        listed = biosafety.SELECT_AGENTS.get(sp)
        if claimed and not listed:
            flag("biosafety", sp,
                 f"marked {claimed!r} but is not on the select-agent list")
        elif listed and not claimed:
            flag("biosafety", sp, f"is {listed!r} and carries no badge")
        elif listed and claimed != listed:
            flag("biosafety", sp,
                 f"badge {claimed!r} does not match the list's {listed!r}")
    for sp, listed in biosafety.SELECT_AGENTS.items():
        if sp not in by_name:
            flag("biosafety", sp,
                 "select-agent list names a species not in this taxonomy")
        elif sp not in biosafety.BIOSAFETY:
            flag("biosafety", sp,
                 f"is {listed!r} but has no species-level containment record")

    # -------------------------------------------------------- differential
    for key, info in differential.SYNDROMES.items():
        for field in ("label", "note"):
            if not info.get(field):
                flag("differential", key, f"{field} is empty")

    return out


def main():
    import app as A
    rows = findings(A.NODES, A.SPECIES_ID)
    errors = [r for r in rows if r[1] == "error"]
    checks = [r for r in rows if r[1] == "check"]

    by_layer = Counter(r[0] for r in rows)
    print(f"Audited the curated layers: {len(errors)} contradictions, "
          f"{len(checks)} to look at\n")
    for kind, label in (("error", "CONTRADICTION"), ("check", "LOOK AT")):
        sel = [r for r in rows if r[1] == kind]
        if not sel:
            continue
        print(f"--- {label} ({len(sel)}) ---")
        for layer, _sev, name, what in sorted(sel):
            print(f"  [{layer}] {name}")
            print(f"      {what}")
        print()
    if by_layer:
        print("by layer:", dict(by_layer.most_common()))
    if not errors:
        print("\nOK    nothing in the curated layers contradicts anything else "
              "in it")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
