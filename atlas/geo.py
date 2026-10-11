"""Turn a profile's free-text `geography` field into map countries.

The profiles describe distribution the way the literature does -- "Amazon
basin", "sub-Saharan Africa", "Fennoscandia" -- not as country codes. This
module resolves that prose against the country names baked into
static/data/world.json, so the distribution figure can highlight real polygons.

Resolution is deliberately conservative: a region phrase expands to the
countries where the virus is actually reported in the literature, not to every
country a continent contains. The result is a schematic of reported
distribution, which is what such a figure can honestly claim.
"""

import json
import re
from pathlib import Path

WORLD = Path(__file__).resolve().parent.parent / "static" / "data" / "world.json"

# Phrases that name more than one country. Longest match wins, so
# "West Africa" is tried before "Africa".
REGIONS = {
    "amazon basin": ["Brazil", "Peru", "Colombia", "Ecuador", "Bolivia", "Venezuela"],
    "amazon": ["Brazil", "Peru", "Colombia", "Ecuador", "Bolivia"],
    "sub-saharan africa": [
        "Nigeria", "Kenya", "Uganda", "Tanzania", "Ethiopia", "Senegal", "Mali",
        "Ghana", "Cameroon", "Central African Rep.", "Dem. Rep. Congo", "Congo",
        "South Africa", "Zimbabwe", "Zambia", "Mozambique", "Angola",
        "Burkina Faso", "Côte d'Ivoire", "Guinea", "Sudan", "S. Sudan",
        "Somalia", "Botswana", "Namibia", "Malawi", "Rwanda", "Burundi",
        "Benin", "Togo", "Niger", "Chad", "Gabon", "Sierra Leone", "Liberia",
    ],
    "west africa": [
        "Nigeria", "Senegal", "Mali", "Ghana", "Guinea", "Sierra Leone",
        "Liberia", "Burkina Faso", "Côte d'Ivoire", "Benin", "Togo",
        "Gambia", "Guinea-Bissau", "Mauritania", "Niger",
    ],
    "east africa": [
        "Kenya", "Uganda", "Tanzania", "Ethiopia", "Somalia", "Rwanda",
        "Burundi", "S. Sudan", "Eritrea", "Djibouti",
    ],
    "central africa": [
        "Cameroon", "Central African Rep.", "Dem. Rep. Congo", "Congo",
        "Gabon", "Chad", "Eq. Guinea",
    ],
    "southern africa": [
        "South Africa", "Zimbabwe", "Botswana", "Namibia", "Mozambique",
        "Zambia", "eSwatini", "Lesotho", "Angola", "Malawi",
    ],
    "north africa": ["Egypt", "Libya", "Tunisia", "Algeria", "Morocco"],
    "africa": [
        "Nigeria", "Kenya", "Uganda", "Senegal", "South Africa", "Ethiopia",
        "Cameroon", "Dem. Rep. Congo", "Tanzania", "Ghana", "Sudan", "Egypt",
        "Mali", "Central African Rep.",
    ],
    "southeast asia": [
        "Vietnam", "Thailand", "Cambodia", "Laos", "Malaysia", "Indonesia",
        "Philippines", "Myanmar", "Singapore", "Brunei", "Timor-Leste",
    ],
    "south asia": ["India", "Pakistan", "Bangladesh", "Sri Lanka", "Nepal", "Bhutan"],
    "east asia": ["China", "Japan", "South Korea", "North Korea", "Taiwan", "Mongolia"],
    "central asia": [
        "Kazakhstan", "Uzbekistan", "Turkmenistan", "Kyrgyzstan", "Tajikistan",
    ],
    "middle east": [
        "Saudi Arabia", "Iran", "Iraq", "Israel", "Jordan", "Lebanon", "Syria",
        "Yemen", "Oman", "United Arab Emirates", "Kuwait", "Qatar", "Turkey",
    ],
    "arabian peninsula": [
        "Saudi Arabia", "Yemen", "Oman", "United Arab Emirates", "Kuwait", "Qatar",
    ],
    "asia": ["China", "India", "Vietnam", "Thailand", "Japan", "Indonesia",
             "Malaysia", "South Korea", "Pakistan", "Bangladesh", "Philippines"],
    "central europe": [
        "Germany", "Austria", "Czechia", "Slovakia", "Hungary", "Poland",
        "Slovenia", "Switzerland", "Croatia",
    ],
    "eastern europe": [
        "Poland", "Ukraine", "Belarus", "Romania", "Bulgaria", "Moldova",
        "Slovakia", "Hungary", "Lithuania", "Latvia", "Estonia",
    ],
    "western europe": [
        "France", "Germany", "Netherlands", "Belgium", "United Kingdom",
        "Ireland", "Luxembourg", "Switzerland", "Austria",
    ],
    "northwest europe": [
        "Netherlands", "Belgium", "Germany", "France", "United Kingdom",
        "Denmark", "Luxembourg", "Ireland",
    ],
    "southern europe": [
        "Italy", "Spain", "Portugal", "Greece", "Croatia", "Albania", "Malta",
    ],
    "northern europe": [
        "Sweden", "Norway", "Finland", "Denmark", "Estonia", "Latvia",
        "Lithuania", "Iceland",
    ],
    "fennoscandia": ["Sweden", "Norway", "Finland"],
    "scandinavia": ["Sweden", "Norway", "Denmark", "Finland"],
    "baltic states": ["Estonia", "Latvia", "Lithuania"],
    "the balkans": [
        "Serbia", "Croatia", "Bosnia and Herz.", "Albania", "Bulgaria",
        "Greece", "Macedonia", "Montenegro", "Kosovo", "Romania",
    ],
    "balkans": [
        "Serbia", "Croatia", "Bosnia and Herz.", "Albania", "Bulgaria",
        "Greece", "Macedonia", "Montenegro", "Kosovo", "Romania",
    ],
    "mediterranean": [
        "Italy", "Spain", "France", "Greece", "Turkey", "Portugal", "Tunisia",
        "Morocco", "Algeria", "Egypt", "Israel", "Cyprus", "Croatia", "Albania",
    ],
    "europe": [
        "France", "Germany", "Italy", "Spain", "Poland", "United Kingdom",
        "Netherlands", "Belgium", "Austria", "Czechia", "Sweden", "Finland",
        "Hungary", "Romania", "Greece", "Switzerland", "Croatia", "Slovakia",
        "Slovenia", "Denmark", "Portugal", "Norway",
    ],
    "north america": ["United States of America", "Canada", "Mexico"],
    "central america": [
        "Panama", "Costa Rica", "Nicaragua", "Honduras", "Guatemala",
        "El Salvador", "Belize",
    ],
    "south america": [
        "Brazil", "Peru", "Colombia", "Venezuela", "Argentina", "Bolivia",
        "Ecuador", "Chile", "Paraguay", "Uruguay", "Guyana", "Suriname",
    ],
    "the americas": [
        "United States of America", "Canada", "Mexico", "Brazil", "Peru",
        "Colombia", "Venezuela", "Argentina", "Bolivia", "Ecuador", "Panama",
        "Costa Rica", "Guatemala", "Honduras", "Nicaragua", "Cuba",
        "Dominican Rep.", "Haiti", "Jamaica", "Paraguay", "Chile", "Uruguay",
        "Trinidad and Tobago", "Puerto Rico",
    ],
    "americas": [
        "United States of America", "Canada", "Mexico", "Brazil", "Peru",
        "Colombia", "Venezuela", "Argentina", "Bolivia", "Ecuador", "Panama",
        "Costa Rica", "Guatemala", "Cuba", "Trinidad and Tobago",
    ],
    "caribbean": [
        "Cuba", "Haiti", "Dominican Rep.", "Jamaica", "Trinidad and Tobago",
        "Puerto Rico", "Bahamas",
    ],
    "western united states": ["United States of America"],
    "united states": ["United States of America"],
    "eastern united states": ["United States of America"],
    "upper midwest": ["United States of America"],
    "appalachian": ["United States of America"],
    "great lakes": ["United States of America", "Canada"],
    "gulf coast": ["United States of America"],
    "atlantic coast": ["United States of America"],
    "four corners": ["United States of America"],
    "argentine pampas": ["Argentina"],
    "pampas": ["Argentina"],
    "western ghats": ["India"],
    "indian ocean": ["Madagascar", "India", "Tanzania", "Mozambique"],
    "pacific": ["Fiji", "Papua New Guinea", "Solomon Is.", "Vanuatu", "New Caledonia"],
    "pacific islands": ["Fiji", "Papua New Guinea", "Solomon Is.", "Vanuatu", "New Caledonia"],
    "oceania": ["Australia", "New Zealand", "Papua New Guinea", "Fiji"],
    "russian far east": ["Russia"],
    "worldwide": [],      # handled specially -- highlights everything
    "global": [],
}

# Names in the prose that differ from the Natural Earth spelling.
ALIASES = {
    # Longer surface forms that would otherwise lose to a shorter country
    # name, or that the map spells differently.
    "equatorial guinea": "Eq. Guinea",
    "south sudan": "S. Sudan",
    "democratic republic of the congo": "Dem. Rep. Congo",
    "republic of the congo": "Congo",
    "cape verde": "Cabo Verde",
    "czech republic": "Czechia",
    "swaziland": "Eswatini",
    "ivory coast": "Côte d'Ivoire",
    "burma": "Myanmar",
    "east timor": "Timor-Leste",
    "north macedonia": "Macedonia",

    "usa": "United States of America",
    "u.s.": "United States of America",
    "us": "United States of America",
    "united states of america": "United States of America",
    "america": "United States of America",
    "uk": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "drc": "Dem. Rep. Congo",
    "democratic republic of the congo": "Dem. Rep. Congo",
    "dr congo": "Dem. Rep. Congo",
    "congo": "Dem. Rep. Congo",
    "ivory coast": "Côte d'Ivoire",
    "cote d'ivoire": "Côte d'Ivoire",
    "car": "Central African Rep.",
    "central african republic": "Central African Rep.",
    "south sudan": "S. Sudan",
    "swaziland": "eSwatini",
    "czech republic": "Czechia",
    "holland": "Netherlands",
    "the netherlands": "Netherlands",
    "bosnia": "Bosnia and Herz.",
    "north macedonia": "Macedonia",
    "burma": "Myanmar",
    "korea": "South Korea",
    "trinidad": "Trinidad and Tobago",
    "dominican republic": "Dominican Rep.",
    "uae": "United Arab Emirates",
    "saudi arabia": "Saudi Arabia",
    "papua new guinea": "Papua New Guinea",
    "new guinea": "Papua New Guinea",
    "solomon islands": "Solomon Is.",
    "timor leste": "Timor-Leste",
    "east timor": "Timor-Leste",
    "eswatini": "eSwatini",
}

# Sub-national places worth recognising, mapped to their country.
PLACES = {
    "karnataka": "India", "kerala": "India", "maharashtra": "India",
    "west bengal": "India", "yunnan": "China", "hunan": "China",
    "hainan": "China", "guangdong": "China", "xinjiang": "China",
    "guangxi": "China", "queensland": "Australia",
    "new south wales": "Australia", "northern australia": "Australia",
    "texas": "United States of America", "missouri": "United States of America",
    "california": "United States of America", "florida": "United States of America",
    "siberia": "Russia", "crimea": "Ukraine", "sicily": "Italy",
    "sardinia": "Italy", "corsica": "France", "crete": "Greece",
    "zanzibar": "Tanzania", "valtice": "Czechia", "bavaria": "Germany",
    "tuscany": "Italy", "andalusia": "Spain", "amazonas": "Brazil",
    "para": "Brazil", "belem": "Brazil", "rio de janeiro": "Brazil",
}

_world_names = None


def world_names():
    global _world_names
    if _world_names is None:
        if WORLD.exists():
            with WORLD.open() as fh:
                _world_names = set(json.load(fh)["countries"])
        else:
            _world_names = set()
    return _world_names



# ---------------------------------------------------------------------------
# Destinations the map cannot draw
# ---------------------------------------------------------------------------
#
# Natural Earth 110m carries 177 country polygons, and has none for the small
# island states or the microstates: no Maldives, Singapore, Mauritius,
# Seychelles, Malta, Cabo Verde, and none of the Caribbean or Pacific small
# islands or the overseas territories. Keying the travel index to the map
# therefore made 66 real destinations unanswerable -- which is how a query for
# the Maldives came back empty.
#
# So presence and geometry are separated. These places are first-class travel
# destinations: they can be named in profile prose, they are reached by region
# expansion, and they appear in the travel index. They simply cannot be shaded
# on the choropleth, and the interface says so rather than pretending they do
# not exist.
#
# Each entry lists the regions it belongs to, so "Caribbean" or "South Asia"
# in a profile reaches them the same way it reaches the mapped countries.

OFFMAP = {
    # --- Indian Ocean and South Asia ---
    "Maldives": ["south asia", "asia", "indian ocean"],
    "Mauritius": ["indian ocean", "east africa", "sub-saharan africa", "africa"],
    "Seychelles": ["indian ocean", "east africa", "sub-saharan africa", "africa"],
    "Comoros": ["indian ocean", "east africa", "sub-saharan africa", "africa"],
    "Mayotte": ["indian ocean", "east africa", "sub-saharan africa", "africa"],
    "Reunion": ["indian ocean", "east africa", "sub-saharan africa", "africa"],
    # --- East and Southeast Asia ---
    "Singapore": ["southeast asia", "asia"],
    "Hong Kong": ["east asia", "asia"],
    "Macao": ["east asia", "asia"],
    "Brunei": ["southeast asia", "asia"],
    # --- Middle East ---
    "Bahrain": ["middle east", "arabian peninsula", "asia"],
    # --- Africa ---
    "Cabo Verde": ["west africa", "sub-saharan africa", "africa"],
    "Sao Tome and Principe": ["central africa", "sub-saharan africa", "africa"],
    "Saint Helena": ["sub-saharan africa", "africa"],
    "Eswatini": ["southern africa", "sub-saharan africa", "africa"],
    # --- Caribbean ---
    "Barbados": ["caribbean", "the americas", "americas"],
    "Saint Lucia": ["caribbean", "the americas", "americas"],
    "Grenada": ["caribbean", "the americas", "americas"],
    "Dominica": ["caribbean", "the americas", "americas"],
    "Antigua and Barbuda": ["caribbean", "the americas", "americas"],
    "Saint Kitts and Nevis": ["caribbean", "the americas", "americas"],
    "Saint Vincent and the Grenadines": ["caribbean", "the americas", "americas"],
    "Guadeloupe": ["caribbean", "the americas", "americas"],
    "Martinique": ["caribbean", "the americas", "americas"],
    "Aruba": ["caribbean", "the americas", "americas"],
    "Curacao": ["caribbean", "the americas", "americas"],
    "Bonaire": ["caribbean", "the americas", "americas"],
    "Saint Martin": ["caribbean", "the americas", "americas"],
    "Anguilla": ["caribbean", "the americas", "americas"],
    "Montserrat": ["caribbean", "the americas", "americas"],
    "British Virgin Is.": ["caribbean", "the americas", "americas"],
    "U.S. Virgin Is.": ["caribbean", "the americas", "americas"],
    "Cayman Is.": ["caribbean", "the americas", "americas"],
    "Turks and Caicos Is.": ["caribbean", "the americas", "americas"],
    "Bermuda": ["north america", "the americas", "americas"],
    # --- South America ---
    "French Guiana": ["south america", "amazon", "the americas", "americas"],
    # --- Pacific ---
    "Samoa": ["pacific islands", "pacific", "oceania"],
    "American Samoa": ["pacific islands", "pacific", "oceania"],
    "Tonga": ["pacific islands", "pacific", "oceania"],
    "Kiribati": ["pacific islands", "pacific", "oceania"],
    "Tuvalu": ["pacific islands", "pacific", "oceania"],
    "Nauru": ["pacific islands", "pacific", "oceania"],
    "Palau": ["pacific islands", "pacific", "oceania"],
    "Marshall Is.": ["pacific islands", "pacific", "oceania"],
    "Micronesia": ["pacific islands", "pacific", "oceania"],
    "French Polynesia": ["pacific islands", "pacific", "oceania"],
    "New Caledonia": ["pacific islands", "pacific", "oceania"],
    "Guam": ["pacific islands", "pacific", "oceania"],
    "Cook Is.": ["pacific islands", "pacific", "oceania"],
    "Niue": ["pacific islands", "pacific", "oceania"],
    "Tokelau": ["pacific islands", "pacific", "oceania"],
    "Wallis and Futuna": ["pacific islands", "pacific", "oceania"],
    "Norfolk I.": ["pacific", "oceania"],
    "Christmas I.": ["southeast asia", "pacific", "oceania"],
    "Cocos Is.": ["southeast asia", "pacific", "oceania"],
    # --- Europe ---
    "Malta": ["mediterranean", "southern europe", "europe"],
    "Monaco": ["mediterranean", "southern europe", "western europe", "europe"],
    "San Marino": ["mediterranean", "southern europe", "europe"],
    "Andorra": ["southern europe", "western europe", "europe"],
    "Liechtenstein": ["central europe", "western europe", "europe"],
    "Gibraltar": ["mediterranean", "southern europe", "europe"],
    "Isle of Man": ["northwest europe", "western europe", "europe"],
    "Jersey": ["northwest europe", "western europe", "europe"],
    "Guernsey": ["northwest europe", "western europe", "europe"],
    "Faroe Is.": ["northern europe", "fennoscandia", "europe"],
    "Aland": ["northern europe", "fennoscandia", "scandinavia", "europe"],
    "Svalbard": ["northern europe", "fennoscandia", "europe"],
}

# region phrase -> the off-map places inside it, built once from OFFMAP so the
# two can never drift apart.
OFFMAP_BY_REGION = {}
for _place, _regions in OFFMAP.items():
    for _region in _regions:
        OFFMAP_BY_REGION.setdefault(_region, []).append(_place)


def travel_names():
    """Every destination the travel index can answer for.

    Wider than world_names(): that is the set the choropleth can shade, this
    is the set a person can actually have travelled to.
    """
    return world_names() | set(OFFMAP)


def is_mappable(country):
    return country in world_names()


# The tropical and subtropical belt, composed from the regions already listed
# so it stays consistent with them. Used when prose says "tropics and
# subtropics worldwide", which is a belt rather than the whole map.
def _belt():
    keys = ["sub-saharan africa", "south asia", "southeast asia",
            "central america", "south america", "caribbean",
            "pacific islands", "oceania", "indian ocean"]
    out = set()
    for key in keys:
        out |= set(REGIONS.get(key, []))
        out |= set(OFFMAP_BY_REGION.get(key, []))
    return sorted(out)


TROPICAL_BELT = _belt()


def resolve(text):
    """Return (countries, worldwide, matched_phrases) for a geography string."""
    countries, worldwide, matched, _origin = resolve_detailed(text)
    return countries, worldwide, matched


def resolve_detailed(text):
    """As resolve(), plus where each country came from.

    The fourth value maps country -> "named" when the prose spells the country
    out, or "region:<phrase>" when it was expanded from a region. That
    distinction matters: "Central and South Asia" expanded CCHF into Sri
    Lanka, which has never reported a case. A named country is a claim; a
    region expansion is an inference, and the interface has to say which.
    """
    if not text:
        return [], False, []
    low = " " + re.sub(r"\s+", " ", text.lower()) + " "
    names = travel_names()
    found, matched = set(), []
    origin = {}

    # "global outbreak" describes an event, not an endemic range -- only
    # "worldwide"/"globally" claim the whole map. And "tropics and subtropics
    # worldwide" is a belt, not the whole map: taken literally it put dengue in
    # Iceland.
    worldwide = bool(re.search(r"\bworldwide\b|\bglobally\b|\ball continents\b", low))
    # The belt only ever REPLACES a global claim. Applied on the mere presence
    # of a tropic word it fired on "Tropical South America", where "tropical"
    # is an adjective on a named region, and put yellow fever in Thailand.
    belt = worldwide and bool(re.search(r"\btropic|\bsubtropic", low))
    if belt:
        worldwide = False
        low = low.replace("worldwide", " ").replace("globally", " ")

    # Curated prose sometimes names where RELATED viruses occur, which is not
    # where this one occurs: "Europe, with related members (Sathuperi,
    # Shamonda) in Africa and Asia" was resolving to Africa and Asia too.
    low = re.split(r"\bwith related\b|\brelated members\b|\brelated viruses\b|"
                   r"\bwhereas\b|\bby contrast\b", low)[0]

    # Coordinated region phrases share their noun: "Central and West Africa"
    # means Central Africa AND West Africa, but only "west africa" is a
    # contiguous phrase, so Central Africa was silently dropped. Expand these
    # before matching.
    low = re.sub(
        r"(?<![a-z])(north(?:ern)?|south(?:ern)?|east(?:ern)?|west(?:ern)?|"
        r"central|southeast(?:ern)?|northeast(?:ern)?|southwest(?:ern)?|"
        r"northwest(?:ern)?|sub-saharan)\s*,?\s+and\s+"
        r"(north(?:ern)?|south(?:ern)?|east(?:ern)?|west(?:ern)?|central|"
        r"southeast(?:ern)?|northeast(?:ern)?|southwest(?:ern)?|"
        r"northwest(?:ern)?|sub-saharan)\s+"
        r"(africa|asia|america|americas|europe)(?![a-z])",
        lambda m: f" {m.group(1)} {m.group(3)} and {m.group(2)} {m.group(3)} ",
        low)

    # Region phrases, longest first, and each match is masked out of the text
    # so an enclosing shorter phrase cannot also fire. Without the mask
    # "North Africa" also matched the bare substring "africa" and expanded to
    # the whole continent, which put Mediterranean Toscana virus in Uganda.
    scan = low
    for phrase in sorted(REGIONS, key=len, reverse=True):
        pattern = rf"(?<![a-z]){re.escape(phrase)}(?![a-z])"
        if re.search(pattern, scan):
            expanded = [c for c in REGIONS[phrase] if c in names]
            expanded += [c for c in OFFMAP_BY_REGION.get(phrase, [])
                         if c in names]
            if expanded:
                found.update(expanded)
                matched.append(phrase)
                for c in expanded:
                    origin.setdefault(c, f"region:{phrase}")
            scan = re.sub(pattern, lambda m: "\u00b7" * len(m.group(0)), scan)

    if belt:
        for phrase in ("tropics", "subtropics"):
            if phrase not in matched:
                matched.append(phrase)
        for c in TROPICAL_BELT:
            if c in names:
                found.add(c)
                origin.setdefault(c, "region:tropics")

    # Explicit names, longest surface form first and each match masked out, so
    # a shorter country name cannot also match inside a longer one. Without
    # this, "Papua New Guinea" also returned Guinea, "Guinea-Bissau" returned
    # Guinea, "Equatorial Guinea" returned Guinea and lost Eq. Guinea
    # altogether, and "South Sudan" returned both Sudans.
    surface = []
    for country in names:
        surface.append((country.lower(), country, country))
    for alias, country in ALIASES.items():
        if country in names:
            surface.append((alias.lower(), country, alias))
    for place, country in PLACES.items():
        if country in names:
            surface.append((place.lower(), country, place))
    surface.sort(key=lambda t: len(t[0]), reverse=True)

    scan2 = low
    for form, country, label in surface:
        pattern = rf"(?<![a-z]){re.escape(form)}(?![a-z])"
        if re.search(pattern, scan2):
            found.add(country)
            matched.append(label)
            origin[country] = "named"
            scan2 = re.sub(pattern, lambda m: "\u00b7" * len(m.group(0)), scan2)

    if worldwide:
        everywhere = sorted(names - {"Antarctica", "Greenland",
                                     "Fr. S. Antarctic Lands", "Svalbard"})
        return everywhere, True, ["worldwide"], {c: "region:worldwide"
                                                for c in everywhere}

    return sorted(found), False, matched, origin


def eradicated(text):
    return bool(text) and "eradicated" in text.lower()
