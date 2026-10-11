"""Travel-medicine view: what a returning traveller could have acquired.

The question this answers
------------------------
"Someone came back from Uganda eleven days ago and is febrile. What viral
infections are geographically plausible, and which are still inside their
incubation window?"

That is a different query from browsing the taxonomy, and it needs three
things the atlas already holds, plus two it did not:

  geography    resolved from the curated profile prose by atlas.geo
  evidence     the pathogenicity tier, so the list is ordered by what actually
               infects people
  activity     current WHO outbreak reports naming that country (atlas.surveil)
  NEW  incubation windows parsed to numbers, so time since return can filter
  NEW  exposure route, so advice can be grouped the way a clinician thinks

What it is not
--------------
Not a risk assessment, and not a differential diagnosis. It says "this virus
has been reported from this country", which is a statement about the
literature, not about this traveller, this season, or this itinerary. Endemic
range is not uniform within a country and transmission is often seasonal and
rural. Anything acute and febrile after travel needs malaria excluded first,
and that is a parasite this atlas does not contain.

Cosmopolitan viruses (measles, influenza, hepatitis B) are separated from
destination-specific ones, because listing them per country would bury the
answer under risks that exist at home too.
"""

import re

from atlas import profiles

# ---------------------------------------------------------------------------
# Incubation windows
# ---------------------------------------------------------------------------

# Profile prose is free text written for a reader, so it is parsed rather than
# re-entered: "Typically 3-8 days", "2-21 days", "5-6 weeks", "Not established".
_RANGE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:–|—|-|to)\s*(\d+(?:\.\d+)?)\s*"
    r"(day|week|month|year)s?", re.I)
_SINGLE = re.compile(r"(?:about|around|typically|usually|median|mean)?\s*"
                     r"(\d+(?:\.\d+)?)\s*(day|week|month|year)s?", re.I)
_UNIT = {"day": 1, "week": 7, "month": 30.4, "year": 365}


def incubation_days(text):
    """(min, max) incubation in days, or None when the prose gives no number."""
    if not text:
        return None
    low = text.lower()
    if "not established" in low or "unknown" in low or "variable" in low[:20]:
        # Fall through anyway: some of these still quote a range afterwards.
        pass
    m = _RANGE.search(text)
    if m:
        unit = _UNIT[m.group(3).lower()]
        return round(float(m.group(1)) * unit, 1), round(float(m.group(2)) * unit, 1)
    m = _SINGLE.search(text)
    if m:
        unit = _UNIT[m.group(2).lower()]
        day = float(m.group(1)) * unit
        # A single figure is a central estimate, not a bound; widen it rather
        # than pretending to a precision the source does not have.
        return round(day * 0.5, 1), round(day * 2, 1)
    return None


# ---------------------------------------------------------------------------
# Exposure routes
# ---------------------------------------------------------------------------

# Ordered: the first match wins, so the most actionable route is reported.
ROUTES = [
    ("mosquito", r"\bmosquito|\baedes\b|\bculex\b|\banopheles\b|\bhaemagogus\b|\bsabethes\b"),
    ("midge", r"\bmidge|\bculicoides\b"),
    ("tick", r"\btick|\bixodes\b|\bdermacentor\b|\bhyalomma\b|\bamblyomma\b"),
    ("sandfly", r"\bsandfl|\bphlebotom"),
    ("rodent", r"\brodent|\brat\b|\bmice\b|\bmouse\b|\bvole\b|\bmastomys\b|"
               r"excreta|urine of|aerosolised.*(?:urine|droppings)"),
    ("bat", r"\bbat\b|\bbats\b|\bpteropus\b|\bfruit bat"),
    ("animal-bite", r"\bbite of (?:an? )?(?:infected )?(?:dog|bat|animal|mammal)|"
                    r"animal bite|\bbitten\b|\bscratch|\bsaliva\b|\blick(?:ed|ing)?\b|"
                    r"percutaneous.*(?:saliva|nerve)"),
    ("bodily-fluid", r"body fluids?|bodily fluid|blood[- ]borne|needle|"
                     r"transfusion|nosocomial|person-to-person contact"),
    ("sexual", r"\bsexual|semen\b|genital"),
    ("respiratory", r"\brespiratory droplet|\bairborne\b|\baerosol\b|"
                    r"\bcoughing\b|person-to-person.*respiratory|droplet"),
    ("faecal-oral", r"faecal[- ]oral|fecal[- ]oral|contaminated (?:water|food)|"
                    r"\bshellfish\b|\boyster"),
    ("animal-contact", r"\bbushmeat\b|slaughter|butcher|\bcamel|\bswine\b|\bpig\b|"
                       r"\bpoultry\b|\blivestock\b|\bprimate|\bmonkey|\bdog\b|\bcat\b"),
    ("vertical", r"\bvertical|mother-to-(?:child|fetus)|congenital|transplacental"),
]

_ROUTES = [(name, re.compile(rx, re.I)) for name, rx in ROUTES]

ROUTE_LABEL = {
    "mosquito": "Mosquito bite",
    "midge": "Biting midge",
    "tick": "Tick bite",
    "sandfly": "Sandfly bite",
    "rodent": "Rodent excreta",
    "bat": "Bat contact or exposure",
    "animal-bite": "Animal bite or scratch",
    "bodily-fluid": "Blood or body fluids",
    "sexual": "Sexual contact",
    "respiratory": "Respiratory",
    "faecal-oral": "Food or water",
    "animal-contact": "Animal contact",
    "vertical": "Mother to child",
}

# Routes a traveller can realistically be counselled about, in the order a
# travel clinic would raise them.
ROUTE_ORDER = ["mosquito", "tick", "midge", "sandfly", "faecal-oral",
               "respiratory", "animal-bite", "animal-contact", "rodent",
               "bat", "bodily-fluid", "sexual", "unclear"]

ARTHROPOD = {"mosquito", "tick", "midge", "sandfly"}

# Words that mean a person is handling the animal, as opposed to prose that
# merely names the animal in a sylvatic cycle. Yellow fever's transmission
# mentions monkeys because of its forest cycle; nobody catches it from a
# monkey.
_DIRECT_CONTACT = re.compile(
    r"slaughter|butcher|bushmeat|handling|\bcontact with\b|skinning|"
    r"\braw milk\b|unpasteurised|occupational|husbandry|\bcull", re.I)

# Not a way a traveller acquires an infection abroad, so it is reported as a
# property of the virus rather than used to group the list.
ATTRIBUTE_ROUTES = {"vertical"}


def routes_for(text):
    found = [name for name, rx in _ROUTES if rx.search(text or "")]
    # An arboviral cycle that names its vertebrate hosts is not an
    # animal-contact risk unless the prose says people handle them.
    if ("animal-contact" in found and ARTHROPOD & set(found)
            and not _DIRECT_CONTACT.search(text or "")):
        found.remove("animal-contact")
    return found or ["unclear"]


# ---------------------------------------------------------------------------
# Building the country index
# ---------------------------------------------------------------------------

TIER_ORDER = {"established": 0, "probable": 1, "possible": 2,
              "animal-only": 3, "no-evidence": 4, "unassessed": 5}

# Tiers worth putting in front of a clinician. "animal-only" and below are not
# travel risks to a person.
TRAVEL_TIERS = ("established", "probable", "possible")


def _genus_routes(nodes):
    """Modal route set per genus, from the species that do have a profile.

    A reference-tier species has a one-line note and no transmission prose, so
    it lands in "unclear" even when its whole genus is tick-borne. Borrowing
    the genus' routes is an inference, so entries that use it are marked.
    """
    tally = {}
    for node in nodes.values():
        if node["rank"] != "species":
            continue
        meta = node.get("meta") or {}
        prof = meta.get("profile")
        if not prof:
            continue
        genus = meta.get("genus")
        if not genus:
            continue
        prose = " ".join(filter(None, [prof.get("transmission"),
                                       " ".join(prof.get("vectors") or [])]))
        for route in routes_for(prose):
            if route != "unclear":
                tally.setdefault(genus, {})
                tally[genus][route] = tally[genus].get(route, 0) + 1
    out = {}
    for genus, counts in tally.items():
        best = max(counts.values())
        # Keep every route at least half as common as the commonest, so a
        # genus that is both mosquito- and midge-borne keeps both.
        out[genus] = sorted(r for r, n in counts.items() if n * 2 >= best)
    return out


def build_index(nodes, geo):
    """country -> [entry], plus a list of cosmopolitan entries.

    Returns (by_country, worldwide, stats). Entries are plain dicts so they can
    be serialised straight to the API.
    """
    by_country, worldwide = {}, []
    stats = {"species": 0, "with_geography": 0, "worldwide": 0, "countries": 0,
             "routes_inherited": 0, "curated_geography": 0}
    known_countries = geo.travel_names()
    genus_routes = _genus_routes(nodes)

    for node in nodes.values():
        if node["rank"] != "species":
            continue
        meta = node.get("meta") or {}
        tier = meta.get("tier")
        if tier not in TRAVEL_TIERS:
            continue
        stats["species"] += 1

        prof = meta.get("profile") or {}
        geo_text = prof.get("geography") or meta.get("tier_note") or ""

        # An explicit country list, where one exists, beats expanding prose.
        # "Central and South Asia" expanded CCHF into Sri Lanka, which has no
        # Hyalomma-borne CCHF and no reported case.
        graded = profiles.country_grades(node["name"])
        grades = {}
        if graded:
            countries = [c for c in graded if c in known_countries]
            is_worldwide = False
            origin = {c: "curated" for c in countries}
            grades = {c: graded[c] for c in countries}
        elif node["name"] in profiles.WORLDWIDE:
            # Cosmopolitan species whose curated note carries no geography.
            # Without this they dropped out of the index entirely, which is
            # how hepatitis E and every herpesvirus came to be missing.
            countries, is_worldwide, origin = [], True, {}
        else:
            countries, is_worldwide, _matched, origin = geo.resolve_detailed(geo_text)
        if not countries and not is_worldwide:
            continue
        stats["with_geography"] += 1
        if graded:
            stats["curated_geography"] += 1

        # Classified from transmission and vectors only. Including the
        # reservoir put dengue and yellow fever under "animal contact" because
        # their sylvatic cycles mention primates, and SARS-CoV-2 under "bat
        # contact" -- all true about maintenance, none of them how a traveller
        # gets infected.
        prose = " ".join(filter(None, [
            prof.get("transmission"), " ".join(prof.get("vectors") or []),
            None if prof else meta.get("tier_note")]))
        if not prose.strip():
            prose = meta.get("tier_note") or ""
        window = incubation_days(prof.get("incubation"))
        route_list = routes_for(prose)
        inherited = False
        if route_list == ["unclear"]:
            borrowed = genus_routes.get(meta.get("genus"))
            if borrowed:
                route_list, inherited = borrowed, True
                stats["routes_inherited"] += 1

        entry = {
            "id": node["id"],
            "species": node["name"],
            "common": (prof.get("names") or [None])[0],
            "tier": tier,
            "family": meta.get("family"),
            "routes": route_list,
            "routes_inherited": inherited,
            "vectors": prof.get("vectors") or [],
            "incubation": prof.get("incubation"),
            "incubation_days": window,
            "syndrome": prof.get("syndrome") or prof.get("headline"),
            "headline": prof.get("headline") or meta.get("tier_note"),
            "prevention": prof.get("prevention"),
            "profiled": bool(meta.get("profiled")),
            "basis": meta.get("basis"),
            "geography": geo_text,
            "eradicated": geo.eradicated(geo_text),
        }

        if is_worldwide:
            info = profiles.EVIDENCE_GRADES[profiles.DEFAULT_GRADE]
            worldwide.append({**entry, "scope": "worldwide",
                              "geo_source": "worldwide", "geo_inferred": False,
                              "geo_region": None, "evidence": "human",
                              "evidence_label": info["label"],
                              "evidence_note": info["note"],
                              "evidence_rank": info["rank"]})
            stats["worldwide"] += 1
            # One list only: a cosmopolitan virus is not a finding about this
            # destination, and duplicating it into every country made the two
            # paths disagree.
            continue
        for country in countries:
            # How confident the geography is for THIS country: stated outright,
            # or inferred by expanding a region phrase.
            src = origin.get(country, "named")
            grade = grades.get(country, profiles.DEFAULT_GRADE)
            info = profiles.EVIDENCE_GRADES[grade]
            by_country.setdefault(country, []).append({
                **entry, "scope": "regional", "geo_source": src,
                "geo_inferred": src.startswith("region:"),
                "geo_region": src.split(":", 1)[1] if src.startswith("region:") else None,
                "evidence": grade,
                "evidence_label": info["label"],
                "evidence_note": info["note"],
                "evidence_rank": info["rank"],
            })

    for rows in by_country.values():
        rows.sort(key=lambda r: (r.get("evidence_rank", 0),
                                 r.get("geo_inferred", False),
                                 TIER_ORDER.get(r["tier"], 9),
                                 not r["profiled"], r["species"]))
    worldwide.sort(key=lambda r: (TIER_ORDER.get(r["tier"], 9), r["species"]))
    stats["countries"] = len(by_country)
    return by_country, worldwide, stats


# ---------------------------------------------------------------------------
# The query
# ---------------------------------------------------------------------------

def window_verdict(window, days):
    """How a virus' incubation window sits against days since exposure.

    'plausible'  the traveller is inside the window
    'early'      too soon for this one to have declared itself
    'late'       the window has closed, so a new illness is unlikely to be this
    'unknown'    the profile gives no usable number
    """
    if days is None:
        return "unfiltered"
    if not window:
        return "unknown"
    lo, hi = window
    if days < lo:
        return "early"
    if days > hi:
        return "late"
    return "plausible"


def query(by_country, worldwide, country, days=None, route=None, known=True):
    """Assemble the travel answer for one country.

    `known` says the name is a real destination; it is separate from whether
    any virus is recorded there. Conflating the two made 14 countries --
    New Zealand, Lebanon, Syria, Djibouti, Greenland among them -- report as
    "country not found" when the honest answer is that nothing
    destination-specific is on record and the cosmopolitan risks still apply.
    """
    rows = list(by_country.get(country, []))
    found = known

    def decorate(entry):
        out = dict(entry)
        out["window"] = window_verdict(entry.get("incubation_days"), days)
        return out

    rows = [decorate(r) for r in rows]
    cosmo = [decorate(r) for r in worldwide]

    if route:
        rows = [r for r in rows if route in r["routes"]]
        cosmo = [c for c in cosmo if route in c["routes"]]

    # Group by route, in clinic order, because that is how prevention advice is
    # given -- bite avoidance, then food and water, then contact.
    groups = []
    for key in ROUTE_ORDER:
        members = [r for r in rows if key in r["routes"]
                   and key not in ATTRIBUTE_ROUTES]
        if members:
            groups.append({"route": key, "label": ROUTE_LABEL.get(key, "Unclear"),
                           "entries": members})

    return {
        "country": country,
        "known_country": found,
        "days_since_return": days,
        "route": route,
        "regional": rows,
        "groups": groups,
        "worldwide": cosmo,
        "counts": {
            "regional": len(rows),
            "worldwide": len(cosmo),
            "plausible": sum(1 for r in rows if r["window"] == "plausible"),
            "late": sum(1 for r in rows if r["window"] == "late"),
            "early": sum(1 for r in rows if r["window"] == "early"),
            "unknown_window": sum(1 for r in rows if r["window"] == "unknown"),
            "human_evidence": sum(1 for r in rows if r.get("evidence") == "human"),
            "reservoir_only": sum(1 for r in rows
                                  if r.get("evidence") in ("reservoir", "vector",
                                                           "human-serology")),
        },
    }
