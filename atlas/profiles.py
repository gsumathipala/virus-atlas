"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Curated human-pathogenicity profiles.

Each profile is keyed by the ICTV species binomial. `names` lists the common
virus names/abbreviations that fall under that species (the VMR often holds
several isolates per species).

`tier` grades the strength of evidence that the virus infects and causes
disease in humans:

  established   Virus isolated or amplified from symptomatic humans, with a
                reproducible clinical syndrome and accepted causal link.
  probable      Human infection confirmed (isolation / RT-PCR / seroconversion)
                with compatible illness, but causation not fully established.
  possible      Serological evidence of human exposure only, or isolated
                single case reports; clinical significance unresolved.
  animal-only   Veterinary pathogen with no credible evidence of human disease.
  no-evidence   No reported human infection.

Fields are deliberately uniform so the sidebar can render any virus the same
way. `evidence` is a list of short evidence statements -- what is actually
known, and how it was shown.
"""

P = {}


def profile(species, **kw):
    P[species] = kw


# ---------------------------------------------------------------------------
# Explicit country lists, where prose expansion is not good enough
# ---------------------------------------------------------------------------
#
# Geography is written as prose for a reader, and atlas.geo expands it to
# countries for the travel view. That works for "Italy, Spain, France" and
# fails for "Central and South Asia", which swept Crimean-Congo haemorrhagic
# fever into Sri Lanka -- a country with no Hyalomma-borne CCHF and no
# reported case.
#
# So for the viruses a traveller actually asks about, the country list is
# stated outright and overrides the prose. Names must match Natural Earth
# spellings (atlas.geo.world_names()), which atlas.update --check verifies.
#
# These lists are endemic or repeatedly-reported range, not every country that
# has ever recorded an imported case.
#
# Small island states have no polygon in Natural Earth 110m and were once
# omitted here for that reason. They are listed now: atlas.geo.OFFMAP carries
# them as travel destinations independently of the map, so the only thing they
# cannot do is be shaded on the choropleth.

# ---------------------------------------------------------------------------
# What KIND of evidence places a virus in a country
# ---------------------------------------------------------------------------
#
# "Nipah virus occurs in Sri Lanka" and "Nipah virus occurs in Bangladesh" are
# not the same statement. Bangladesh has annual human outbreaks with
# person-to-person transmission. Sri Lanka has henipavirus-positive Pteropus
# bats and no human case ever reported. Collapsing both into one country list
# either hides a real finding or invents a human risk.
#
# So a country entry carries a grade. The grades are ordered by what they mean
# for a person who has just been there, strongest first.

EVIDENCE_GRADES = {
    "human": {
        "rank": 0,
        "label": "Human cases reported",
        "note": "Human infection has been confirmed in this country.",
    },
    "human-serology": {
        "rank": 1,
        "label": "Human seroprevalence only",
        "note": "Antibody found in people, with no confirmed clinical case "
                "reported. Exposure has happened; disease has not been "
                "demonstrated.",
    },
    "reservoir": {
        "rank": 2,
        "label": "Reservoir detection only",
        "note": "Virus, viral RNA or specific antibody found in the reservoir "
                "host or in livestock, with no human case reported. The virus "
                "is present in the country; whether it has ever infected a "
                "person there is unknown.",
    },
    "vector": {
        "rank": 3,
        "label": "Competent vector present",
        "note": "A vector shown to transmit this virus is established here, "
                "but the virus itself has not been detected. This is a "
                "receptivity statement, not a presence one.",
    },
}

DEFAULT_GRADE = "human"


def country_grades(species):
    """{country: grade} for a species, normalising both accepted shapes.

    COUNTRIES entries may be a plain list, when every country carries the same
    (human-case) evidence, or a dict when they do not.
    """
    entry = COUNTRIES.get(species)
    if entry is None:
        return {}
    if isinstance(entry, dict):
        return dict(entry)
    return {c: DEFAULT_GRADE for c in entry}


# Cosmopolitan species whose curated note carries no geography. Without these
# they fell out of the travel index entirely -- which is how hepatitis E, every
# herpesvirus and the rhinoviruses came to be missing from it.
WORLDWIDE = {
    # enteric, faecal-oral, essentially global
    "Paslahepevirus balayani", "Hepatovirus ahepa", "Kobuvirus aichi",
    "Salivirus aklasse", "Parechovirus ahumpari", "Sapovirus sapporoense",
    "Rotavirus alphagastroenteritidis", "Rotavirus tritogastroenteritidis",
    "Mamastrovirus hominis", "Mamastrovirus homustovis",
    "Enterovirus coxsackiepol", "Enterovirus alphacoxsackie",
    "Enterovirus betacoxsackie", "Enterovirus deconjuncti",
    # respiratory
    "Enterovirus alpharhino", "Enterovirus betarhino", "Enterovirus cerhino",
    "Orthopneumovirus hominis", "Metapneumovirus hominis",
    "Respirovirus pneumoniae", "Respirovirus laryngotracheitidis",
    "Orthorubulavirus hominis", "Orthorubulavirus laryngotracheitidis",
    "Orthorubulavirus parotitidis", "Betainfluenzavirus influenzae",
    "Gammainfluenzavirus influenzae", "Betacoronavirus gravedinis",
    "Betacoronavirus hongkongense", "Alphacoronavirus chicagoense",
    "Alphacoronavirus amsterdamense", "Cardiovirus saffoldi",
    "Mastadenovirus caesari", "Mastadenovirus blackbeardi",
    "Mastadenovirus dominans", "Mastadenovirus exoticum",
    "Mastadenovirus faecale", "Mastadenovirus russelli",
    # herpesviruses and other persistent infections
    "Simplexvirus humanalpha1", "Simplexvirus humanalpha2",
    "Varicellovirus humanalpha3", "Cytomegalovirus humanbeta5",
    "Roseolovirus humanbeta6a", "Roseolovirus humanbeta6b",
    "Roseolovirus humanbeta7", "Lymphocryptovirus humangamma4",
    "Rhadinovirus humangamma8",
    # blood-borne and sexually transmitted
    "Orthohepadnavirus hominoidei", "Deltavirus italiense",
    "Orthohepacivirus hominis",
    "Lentivirus humimdef2", "Deltaretrovirus priTlym1",
    "Alphapapillomavirus 7", "Alphapapillomavirus 9",
    "Alphapapillomavirus 10", "Mupapillomavirus 1",
    # skin and ubiquitous
    "Molluscipoxvirus molluscum", "Erythroparvovirus primate1",
    "Bocaparvovirus primate1", "Betapolyomavirus hominis",
    "Betapolyomavirus secuhominis", "Alphapolyomavirus quintihominis",
    "Alphapolyomavirus octihominis", "Rubivirus rubellae",
    # occupational zoonoses of livestock keeping, wherever livestock are kept
    "Parapoxvirus orf", "Parapoxvirus pseudocowpox",
    "Parapoxvirus bovinestomatitis",
}

COUNTRIES = {
    # CCHF: Hyalomma ticks and seropositive livestock extend well past the
    # countries with recorded human disease.
    "Orthonairovirus haemorrhagiae": {c: "human" for c in [
        # Africa
        "South Africa", "Namibia", "Mauritania", "Senegal", "Sudan",
        "S. Sudan", "Kenya", "Uganda", "Tanzania", "Nigeria", "Mali",
        "Burkina Faso", "Egypt",
        # Balkans and southern Europe
        "Albania", "Bulgaria", "Kosovo", "Macedonia", "Greece",
        "Turkey", "Spain", "Georgia", "Russia", "Ukraine",
        # Middle East and central Asia
        "Iran", "Iraq", "Oman", "United Arab Emirates", "Saudi Arabia",
        "Kazakhstan", "Uzbekistan", "Tajikistan", "Turkmenistan",
        "Kyrgyzstan", "Afghanistan",
        # South Asia and China -- India and Pakistan only, NOT Sri Lanka,
        # Nepal, Bhutan or the Maldives.
        "India", "Pakistan", "China",
    ]} | {c: "reservoir" for c in [
        "Portugal", "France", "Italy", "Hungary", "Romania", "Serbia",
        "Croatia", "Bosnia and Herz.", "Montenegro", "Moldova", "Armenia",
        "Azerbaijan", "Morocco", "Tunisia", "Algeria", "Libya", "Benin",
        "Ghana", "Côte d'Ivoire", "Cameroon", "Chad", "Niger", "Zimbabwe",
        "Zambia", "Tanzania", "Madagascar", "Bangladesh", "Myanmar",
        "Nepal", "Mongolia", "Qatar", "Kuwait", "Jordan",
    ]},
    "Orthoflavivirus flavi": [
        # Africa
        "Angola", "Benin", "Burkina Faso", "Burundi", "Cameroon",
        "Central African Rep.", "Chad", "Côte d'Ivoire", "Dem. Rep. Congo",
        "Congo", "Eq. Guinea", "Ethiopia", "Gabon", "Gambia", "Ghana",
        "Guinea", "Guinea-Bissau", "Kenya", "Liberia", "Mali", "Mauritania",
        "Niger", "Nigeria", "Senegal", "Sierra Leone", "S. Sudan",
        "Sudan", "Togo", "Uganda",
        # South America -- no yellow fever in Asia
        "Brazil", "Bolivia", "Colombia", "Ecuador", "Peru", "Venezuela",
        "Guyana", "Suriname", "Argentina", "Paraguay",
        "Panama", "Trinidad and Tobago",
    ],
    # The virus that prompted the grading. Bangladesh and India have annual
    # human outbreaks; Malaysia and Singapore had the 1998-99 pig-associated
    # epidemic. Everywhere else on this list has henipavirus-positive
    # Pteropus bats, or bat serology, and no human case -- including Sri
    # Lanka, where Pteropus medius carries it.
    "Henipavirus nipahense": {
        "Bangladesh": "human",
        "India": "human",
        "Malaysia": "human",
        "Singapore": "human",
        "Philippines": "human",
        "Sri Lanka": "reservoir",
        "Thailand": "reservoir",
        "Cambodia": "reservoir",
        "Vietnam": "reservoir",
        "Indonesia": "reservoir",
        "China": "reservoir",
        "Madagascar": "reservoir",
        "Papua New Guinea": "reservoir",
        "Timor-Leste": "reservoir",
    },
    "Henipavirus hendraense": {
        "Australia": "human",
        "Papua New Guinea": "reservoir",
    },
    # Rousettus aegyptiacus colonies, mostly without human cases.
    "Orthomarburgvirus marburgense": {
        "Angola": "human", "Uganda": "human", "Kenya": "human",
        "Dem. Rep. Congo": "human", "Tanzania": "human", "Ethiopia": "human",
        "Eq. Guinea": "human", "Ghana": "human", "Guinea": "human",
        "South Africa": "human", "Zimbabwe": "human", "Rwanda": "human",
        "Sierra Leone": "reservoir", "Gabon": "reservoir",
        "Zambia": "reservoir", "Liberia": "reservoir",
    },
    # Dromedary seroprevalence is near-universal across the camel belt; human
    # cases are overwhelmingly Arabian.
    "Betacoronavirus cameli": {
        "Saudi Arabia": "human", "United Arab Emirates": "human",
        "Qatar": "human", "Oman": "human", "Jordan": "human",
        "Kuwait": "human", "Iran": "human", "Yemen": "human",
        "South Korea": "human",
        "Egypt": "reservoir", "Sudan": "reservoir", "Ethiopia": "reservoir",
        "Somalia": "reservoir", "Kenya": "reservoir", "Nigeria": "reservoir",
        "Mali": "reservoir", "Burkina Faso": "reservoir",
        "Morocco": "reservoir", "Tunisia": "reservoir", "Pakistan": "reservoir",
    },
    # Sri Lankan bat lyssavirus: isolated from Pteropus, no human case.
    "Lyssavirus gannoruwa": {"Sri Lanka": "reservoir"},
    "Lyssavirus australis": {"Australia": "human"},
    "Lyssavirus duvenhage": {"South Africa": "human", "Kenya": "human",
                             "Zimbabwe": "reservoir"},
    "Lyssavirus hamburg": {"Germany": "human", "Denmark": "human",
                           "Netherlands": "human", "Poland": "human",
                           "France": "reservoir", "Spain": "reservoir",
                           "Ukraine": "reservoir", "Russia": "reservoir"},
    "Lyssavirus helsinki": {"Finland": "human", "United Kingdom": "human",
                            "Switzerland": "human", "Netherlands": "reservoir",
                            "Germany": "reservoir"},
    "Lyssavirus caucasicus": {"Russia": "reservoir", "Georgia": "reservoir"},
    # Regional viruses that previously had no geography at all.
    "Paslahepevirus balayani": None,          # handled by WORLDWIDE
    "Orthoflavivirus omskense": {"Russia": "human", "Kazakhstan": "human"},
    "Orthoflavivirus zilberi": {
        "Russia": "human", "China": "human", "Japan": "human",
        "Kazakhstan": "human", "Mongolia": "human", "South Korea": "reservoir",
    },
    "Vesiculovirus chandipura": {"India": "human", "Sri Lanka": "reservoir",
                                 "Nigeria": "reservoir", "Senegal": "reservoir"},
    "Vesiculovirus indiana": {
        "United States of America": "human", "Mexico": "human",
        "Panama": "human", "Costa Rica": "human", "Colombia": "human",
        "Venezuela": "human", "Ecuador": "human", "Peru": "human",
        "Brazil": "human", "Argentina": "reservoir", "Guatemala": "human",
        "Honduras": "human", "Nicaragua": "human", "Belize": "reservoir",
    },
    "Vesiculovirus newjersey": {
        "United States of America": "human", "Mexico": "human",
        "Panama": "human", "Costa Rica": "human", "Honduras": "human",
        "Guatemala": "human", "Nicaragua": "human", "Colombia": "reservoir",
    },
    "Alphavirus sindbis": {
        "Finland": "human", "Sweden": "human", "Russia": "human",
        "South Africa": "human", "Egypt": "human", "Israel": "human",
        "Norway": "reservoir", "Estonia": "reservoir", "Germany": "reservoir",
        "Italy": "reservoir", "China": "reservoir", "Australia": "reservoir",
        "Kenya": "reservoir", "Uganda": "reservoir", "Cameroon": "reservoir",
    },
    "Alphavirus mucambo": {"Brazil": "human", "Venezuela": "human",
                           "Suriname": "human", "Guyana": "reservoir",
                           "Trinidad and Tobago": "reservoir"},
    "Alphavirus tonate": {"Brazil": "human", "Peru": "human",
                          "Guyana": "reservoir"},
    "Mammarenavirus brazilense": {"Brazil": "human"},
    "Mammarenavirus chapareense": {"Bolivia": "human"},
    "Mammarenavirus guanaritoense": {"Venezuela": "human"},
    "Mammarenavirus machupoense": {"Bolivia": "human"},
    "Phlebovirus napoliense": {
        "Italy": "human", "Greece": "human", "Cyprus": "human",
        "Turkey": "human", "Egypt": "human", "Portugal": "human",
        "Spain": "reservoir", "France": "reservoir", "Tunisia": "reservoir",
        "Morocco": "reservoir", "Algeria": "reservoir", "Iran": "reservoir",
    },
    "Phlebovirus siciliaense": {
        "Italy": "human", "Egypt": "human", "Turkey": "human",
        "Cyprus": "human", "Greece": "reservoir", "Tunisia": "reservoir",
        "Algeria": "reservoir", "Morocco": "reservoir", "Iran": "reservoir",
        "Pakistan": "reservoir",
    },
    "Thogotovirus bourbonense": {"United States of America": "human"},
    "Orthopoxvirus cowpox": {
        "United Kingdom": "human", "Germany": "human", "France": "human",
        "Netherlands": "human", "Austria": "human", "Finland": "human",
        "Russia": "human", "Norway": "reservoir", "Sweden": "reservoir",
        "Belgium": "reservoir", "Italy": "reservoir",
    },
    "Yatapoxvirus tanapox": {"Kenya": "human", "Dem. Rep. Congo": "human",
                             "Tanzania": "reservoir"},
    "Parapoxvirus sealpox": {
        "United States of America": "human", "United Kingdom": "human",
        "Canada": "reservoir", "Norway": "reservoir", "Iceland": "reservoir",
    },
    "Simplexvirus macacinealpha1": {
        "United States of America": "human", "China": "reservoir",
        "Japan": "reservoir", "India": "reservoir", "Indonesia": "reservoir",
        "Thailand": "reservoir", "Philippines": "reservoir",
        "Nepal": "reservoir", "Bangladesh": "reservoir",
    },
    "Orthobunyavirus maritubaense": {"Brazil": "human", "Peru": "reservoir"},
    # Dengue reaches ~130 countries, so the tropical-belt inference is not
    # wrong -- but leaving the world's most important arbovirus as an
    # "inferred" entry understates it. Principal endemic range, stated.
    "Orthoflavivirus denguei": [
        # Asia
        "India", "Sri Lanka", "Bangladesh", "Nepal", "Pakistan", "Bhutan",
        "Myanmar", "Thailand", "Laos", "Cambodia", "Vietnam", "Malaysia",
        "Indonesia", "Philippines", "Timor-Leste", "Brunei", "China",
        "Taiwan", "Yemen", "Saudi Arabia", "Oman",
        # Pacific
        "Papua New Guinea", "Fiji", "Solomon Is.", "Vanuatu", "New Caledonia",
        "Australia", "Samoa", "Tonga", "Kiribati", "French Polynesia",
        "Micronesia", "Marshall Is.", "Palau", "Guam", "Cook Is.",
        "Singapore", "Maldives", "Mauritius", "Seychelles", "Comoros",
        "Reunion", "Mayotte", "Cabo Verde",
        # Africa
        "Nigeria", "Senegal", "Côte d'Ivoire", "Ghana", "Burkina Faso",
        "Mali", "Guinea", "Sierra Leone", "Cameroon", "Gabon", "Angola",
        "Dem. Rep. Congo", "Sudan", "Ethiopia", "Somalia", "Kenya",
        "Tanzania", "Uganda", "Mozambique", "Madagascar", "Egypt",
        # Americas
        "Mexico", "Guatemala", "Belize", "Honduras", "El Salvador",
        "Nicaragua", "Costa Rica", "Panama", "Colombia", "Venezuela",
        "Ecuador", "Peru", "Bolivia", "Brazil", "Paraguay", "Argentina",
        "Guyana", "Suriname", "Cuba", "Haiti", "Dominican Rep.", "Jamaica",
        "Puerto Rico", "Trinidad and Tobago", "Barbados", "Saint Lucia",
        "Grenada", "Dominica", "Antigua and Barbuda", "Saint Kitts and Nevis",
        "Saint Vincent and the Grenadines", "Guadeloupe", "Martinique",
        "Aruba", "Curacao", "French Guiana", "Sao Tome and Principe",
    ],
    "Orthoflavivirus japonicum": [
        "India", "Nepal", "Bangladesh", "Sri Lanka", "Myanmar", "Thailand",
        "Laos", "Cambodia", "Vietnam", "Malaysia", "Indonesia",
        "Philippines", "China", "Taiwan", "Japan", "South Korea",
        "North Korea", "Papua New Guinea", "Australia", "Pakistan",
        "Timor-Leste", "Brunei", "Bhutan", "Singapore", "Hong Kong",
    ],
    "Orthoflavivirus zikaense": [
        "Brazil", "Colombia", "Venezuela", "Ecuador", "Peru", "Bolivia",
        "Paraguay", "Argentina", "Guyana", "Suriname", "Panama", "Costa Rica", "Nicaragua", "Honduras", "Guatemala",
        "Belize", "El Salvador", "Mexico", "Cuba", "Haiti",
        "Dominican Rep.", "Jamaica", "Puerto Rico", "Trinidad and Tobago",
        "Angola", "Nigeria", "Gabon", "Uganda", "Senegal",
        "India", "Thailand", "Vietnam", "Malaysia",
        "Indonesia", "Philippines", "Fiji", "Papua New Guinea",
        "French Polynesia", "Samoa", "Tonga", "Cook Is.", "New Caledonia",
        "Marshall Is.", "Micronesia",
    ],
    "Alphavirus chikungunya": [
        # The 2004-07 Indian Ocean epidemic began in Kenya and ran through
        # Comoros, Réunion, Mauritius, Seychelles and the Maldives before
        # reaching India — these islands are central to the virus' history,
        # and were missing only because the map has no polygon for them.
        "Comoros", "Reunion", "Mauritius", "Seychelles", "Mayotte",
        "Maldives", "Singapore",
        "India", "Sri Lanka", "Bangladesh", "Myanmar", "Thailand",
        "Cambodia", "Laos", "Vietnam", "Malaysia", "Indonesia",
        "Philippines", "Pakistan", "Kenya", "Tanzania",
        "Uganda", "Sudan", "Ethiopia", "Somalia", "Nigeria", "Senegal",
        "Cameroon", "Gabon", "Dem. Rep. Congo", "Mozambique", "Madagascar",
        "Yemen", "Saudi Arabia",
        "Brazil", "Paraguay", "Bolivia", "Argentina", "Colombia",
        "Venezuela", "Peru", "Mexico", "Guatemala", "Honduras",
        "Nicaragua", "Costa Rica", "Panama", "Haiti", "Dominican Rep.",
        "Jamaica", "Cuba", "Trinidad and Tobago", "Puerto Rico",
        "Barbados", "Saint Lucia", "Grenada", "Dominica", "Martinique",
        "Guadeloupe", "Saint Martin", "Aruba", "Curacao", "French Guiana",
        "Antigua and Barbuda", "Saint Kitts and Nevis",
        "Saint Vincent and the Grenadines", "British Virgin Is.", "Anguilla",
    ],
    "Orthoflavivirus nilense": [
        "United States of America", "Canada", "Mexico", "Brazil",
        "Argentina", "Colombia", "Venezuela", "Israel", "Egypt", "Tunisia",
        "Morocco", "Algeria", "Turkey", "Greece", "Italy", "Spain",
        "France", "Portugal", "Romania", "Hungary", "Serbia", "Croatia",
        "Austria", "Germany", "Czechia", "Slovakia", "Bulgaria", "Russia",
        "Ukraine", "South Africa", "Kenya", "Uganda", "Nigeria", "Senegal",
        "India", "Pakistan", "Australia",
    ],
    "Orthobunyavirus bwambaense": [
        "Uganda", "Kenya", "Tanzania", "Nigeria", "Cameroon",
        "Central African Rep.", "Dem. Rep. Congo", "Senegal", "Guinea",
        "Mozambique", "South Africa",
    ],
    "Orthobunyavirus bataiense": [
        "Germany", "Czechia", "Slovakia", "Austria", "Hungary", "Romania",
        "Italy", "Portugal", "Finland", "Sweden", "Russia", "Ukraine",
        "India", "China", "Malaysia", "Japan", "Sudan", "Uganda",
    ],
    "Orthobunyavirus tahynaense": [
        "Czechia", "Slovakia", "Austria", "Germany", "Hungary", "Romania",
        "Serbia", "Italy", "France", "Moldova", "Russia", "Ukraine",
        "Kazakhstan", "Tajikistan", "Mozambique",
    ],
    "Orthobunyavirus bunyamweraense": [
        "Uganda", "Kenya", "Nigeria", "Senegal", "Cameroon",
        "South Africa", "Mozambique", "Dem. Rep. Congo", "Brazil",
    ],
    "Orthobunyavirus shuniense": [
        "South Africa", "Nigeria", "Zimbabwe", "Israel",
    ],
    "Orthobunyavirus ileshaense": [
        "Nigeria", "Central African Rep.", "Cameroon", "Senegal", "Uganda",
        "Madagascar",
    ],
    "Orthonairovirus kasokeroense": {"Uganda": "human",
                                     "Sierra Leone": "reservoir"},
    # Ebolaviruses: bat and non-human-primate serology far exceeds the
    # countries that have ever had a human case.
    "Orthoebolavirus zairense": {
        "Dem. Rep. Congo": "human", "Gabon": "human", "Congo": "human",
        "Guinea": "human", "Liberia": "human", "Sierra Leone": "human",
        "Nigeria": "human", "Mali": "human", "Senegal": "human",
        "Uganda": "human", "South Africa": "human", "Italy": "human",
        "Cameroon": "reservoir", "Central African Rep.": "reservoir",
        "Eq. Guinea": "reservoir", "Ghana": "reservoir",
        "Côte d'Ivoire": "reservoir", "Guinea-Bissau": "reservoir",
        "Tanzania": "reservoir", "Kenya": "reservoir", "Ethiopia": "reservoir",
        "Mozambique": "reservoir", "Zambia": "reservoir",
        "Madagascar": "reservoir", "Bangladesh": "reservoir",
        "China": "reservoir",
    },
    "Orthoebolavirus sudanense": {
        "Uganda": "human", "Sudan": "human", "S. Sudan": "human",
        "Kenya": "reservoir", "Ethiopia": "reservoir",
    },
    "Orthoebolavirus bundibugyoense": {
        "Uganda": "human", "Dem. Rep. Congo": "human",
    },
    "Orthoebolavirus restonense": {
        # Human seroconversion in animal handlers, never any disease.
        "Philippines": "human-serology", "United States of America": "human-serology",
        "China": "reservoir", "Italy": "reservoir",
    },
    "Orthoebolavirus taiense": {"Côte d'Ivoire": "human",
                                "Liberia": "reservoir"},
    "Orthoebolavirus bombaliense": {
        "Sierra Leone": "reservoir", "Guinea": "reservoir",
        "Kenya": "reservoir", "Mozambique": "reservoir",
    },
    "Cuevavirus lloviuense": {"Spain": "reservoir", "Portugal": "reservoir",
                              "France": "reservoir", "Hungary": "reservoir",
                              "Italy": "reservoir"},
    # Lassa: Mastomys natalensis carriage is far wider than the endemic
    # human belt, and several countries have rodent virus without cases.
    "Mammarenavirus lassaense": {
        "Nigeria": "human", "Liberia": "human", "Sierra Leone": "human",
        "Guinea": "human", "Benin": "human", "Ghana": "human",
        "Mali": "human", "Togo": "human", "Burkina Faso": "human",
        "Côte d'Ivoire": "reservoir", "Senegal": "reservoir",
        "Guinea-Bissau": "reservoir", "Niger": "reservoir",
        "Cameroon": "reservoir",
    },
    # Rift Valley fever: livestock seroprevalence reaches well beyond the
    # countries that have reported human outbreaks.
    "Phlebovirus riftense": {
        "Kenya": "human", "Tanzania": "human", "Somalia": "human",
        "Sudan": "human", "S. Sudan": "human", "Egypt": "human",
        "Mauritania": "human", "Senegal": "human", "South Africa": "human",
        "Namibia": "human", "Madagascar": "human", "Saudi Arabia": "human",
        "Yemen": "human", "Uganda": "human",
        "Mayotte": "human", "Comoros": "human",
        "Ethiopia": "reservoir", "Zambia": "reservoir",
        "Zimbabwe": "reservoir", "Botswana": "reservoir",
        "Mozambique": "reservoir", "Mali": "reservoir", "Niger": "reservoir",
        "Chad": "reservoir", "Nigeria": "reservoir", "Gabon": "reservoir",
        "Central African Rep.": "reservoir", "Burundi": "reservoir",
        "Angola": "reservoir", "Turkey": "reservoir", "Libya": "reservoir",
    },
    # SFTS: tick and livestock positivity ahead of recognised human cases.
    "Bandavirus dabieense": {
        "China": "human", "South Korea": "human", "Japan": "human",
        "Vietnam": "human", "Taiwan": "human", "Myanmar": "human",
        "Thailand": "reservoir", "Pakistan": "reservoir",
    },
    "Bandavirus heartlandense": {"United States of America": "human"},
    "Orthobunyavirus akabaneense": [
        "Australia", "Japan", "South Korea", "China", "Taiwan", "Israel",
        "Turkey", "Kenya", "South Africa", "Indonesia",
    ],
    "Orthobunyavirus schmallenbergense": [
        "Germany", "Netherlands", "Belgium", "France", "United Kingdom",
        "Ireland", "Denmark", "Luxembourg", "Switzerland", "Austria",
        "Italy", "Spain", "Poland", "Sweden", "Norway", "Finland",
        "Czechia", "Estonia", "Latvia", "Lithuania",
    ],
}


# ---------------------------------------------------------------------------
# Peribunyaviridae / Orthobunyavirus -- the Simbu serogroup and relatives
# ---------------------------------------------------------------------------

profile(
    "Orthobunyavirus catqueense",
    names=["Cat Que virus (CQV)", "Oya virus (OYAV)", "I612045 virus"],
    tier="probable",
    headline=(
        "Simbu-serogroup orthobunyavirus of the Manzanilla clade, maintained in "
        "pigs and Culicoides biting midges across East and South Asia. Known "
        "mainly from swine serosurveys and vector surveillance; a single 2026 "
        "report describes severe human disease."
    ),
    syndrome=(
        "Human disease is documented from a single published case: a 2026 New "
        "England Journal of Medicine report of severe hepatitis, enteritis and "
        "coagulopathy. Beyond that the human evidence is serological — IgG in "
        "people in Vietnam and in two individuals in Karnataka, India — so the "
        "clinical spectrum, including whether mild or self-limiting illness is "
        "common, is genuinely unknown. No neuroinvasive human case has been "
        "published, despite the neuropathogenicity of related simbuviruses."
    ),
    transmission=(
        "Arboviral, with Culicoides biting midges the likely vectors: most "
        "isolates come from midges, and experimental competence in mosquitoes "
        "is poor. Pigs act as amplifying hosts. Culex mosquitoes yield field "
        "isolates and support replication, but in oral-challenge experiments "
        "Cx. pipiens pallens reached only 4.8% dissemination and 0% "
        "transmission, so a mosquito-borne cycle is not established."
    ),
    vectors=[
        "Culicoides spp. (biting midges) — the source of most isolates",
        "Culex spp. — field isolates reported; experimental transmission not demonstrated",
    ],
    reservoir="Domestic pigs (high seroprevalence), with birds also implicated; antibodies reported in cattle and sheep.",
    geography="Vietnam, southern China (Yunnan, Hunan, Hainan, Guangdong), India (Karnataka, Maharashtra). Serological signal in Indian swine and humans.",
    incubation="Not established.",
    diagnosis="Virus-specific S-segment RT-qPCR (95% limit of detection 0.80 PFU/mL for the published OYAV primer/probe set), virus isolation in BHK-21, MA104 or PK15 cells, neutralisation and IgG ELISA. Not covered by routine arbovirus panels — requires targeted testing.",
    management="Supportive only. No licensed antiviral or vaccine.",
    prevention="Vector avoidance; midge and mosquito control around pig husbandry; surveillance of swine herds.",
    evidence=[
        "Isolated from Culex mosquitoes and pigs in Vietnam and China; isolate HN1304M recovered from Culicoides midges in Hunan (2013).",
        "Oya virus isolate SZC50 from Yunnan midges killed suckling and IFN-α/β-receptor-deficient mice and induced CPE in three mammalian cell lines, demonstrating mammalian virulence.",
        ">30% neutralising-antibody seroprevalence in Yunnan pigs (up to 95% in Malipo), establishing intense mammalian circulation.",
        "Indian preparedness study screened human and swine sera by RT-PCR and anti-CQV IgG ELISA and found IgG in two people in Karnataka — the only human serological signal reported outside Vietnam.",
        "Cat Que and Balagodu viruses isolated from a jungle myna and a paddy bird in Karnataka, India — Manzanilla clade, suggesting under-reported human and livestock infection.",
        "Detected in Hainan biting midges 2019–2023 at a minimum infection rate of 0.4/1000.",
        "Oya virus was isolated from Karnataka, India in 2016 and characterised as a Simbu-serogroup virus, independently of the Vietnamese and Chinese isolates.",
        "Vector-competence testing of four mosquito species found Cx. pipiens pallens had the highest infection rate (40%) but a dissemination rate of 4.8% and a transmission rate of 0% — evidence against, not for, mosquito-borne transmission.",
        "2026 NEJM case report: severe hepatitis, enteritis and coagulopathy attributed to Oya virus — the only published human case.",
        "Mechanistic work shows OYAV (with Ebinur Lake virus) activates the AhR–CYP1A1 axis to suppress type I interferon responses — a defined immune-evasion module.",
    ],
    refs=[
        {"label": "Oya Virus in a Patient with Severe Hepatitis, Enteritis, and Coagulopathy. NEJM 2026", "doi": "10.1056/NEJMc2602616", "pmid": "42777248"},
        {"label": "In vivo/in vitro characterization of Oya virus isolate SZC50 and seroprevalence in domestic animals, Yunnan. PLoS NTD 2023", "doi": "10.1371/journal.pntd.0011374", "pmid": "37319258"},
        {"label": "Proactive preparedness for Cat Que virus: an existing threat in India. Indian J Med Res 2020", "doi": "10.4103/ijmr.IJMR_1195_18", "pmid": "32719230"},
        {"label": "Characterization of unknown orthobunya-like viruses from India (Manzanilla clade). Viruses 2018", "doi": "10.3390/v10090451", "pmid": "30149496"},
        {"label": "Molecular characterization of HN1304M, a Cat Que virus from midges in China. Pathogens 2022", "doi": "10.3390/pathogens11091049", "pmid": "36145481"},
        {"label": "Evaluating the mosquito vector range for Oya virus and Ebinur Lake virus. Parasit Vectors 2024", "doi": "10.1186/s13071-024-06295-5", "pmid": "38715075"},
        {"label": "OYAV and EBIV co-opt the AhR-CYP1A1 axis to suppress type I IFN. Virol Sin 2026", "doi": "10.1016/j.virs.2026.04.001", "pmid": "41956157"},
        {"label": "The Cat Que Virus: a resurfacing orthobunyavirus could lead to epidemics. Virusdisease 2021", "doi": "10.1007/s13337-021-00745-9", "pmid": "34642639"},
        {"label": "Development and evaluation of RT-qPCR assays for Oya virus and Ebinur Lake virus. Virus Res 2024", "doi": "10.1016/j.virusres.2023.199265", "pmid": "37940076"},
        {"label": "Isolation and characterization of Oya virus, a Simbu serogroup virus from Karnataka, India. Infect Genet Evol 2016", "doi": "10.1016/j.meegid.2016.06.049", "pmid": "27374486"},
    ],
)

profile(
    "Orthobunyavirus oropoucheense",
    host="sloth",
    names=["Oropouche virus (OROV)", "Iquitos virus (IQTV)", "Madre de Dios virus", "Perdões virus", "Pintupo virus"],
    tier="established",
    headline="The most important human pathogen of the Simbu serogroup and, after dengue, one of the most frequent arboviral febrile illnesses in the Amazon basin. Major expansion across the Americas from 2023–2024.",
    syndrome="Abrupt febrile illness ('Oropouche fever') with severe headache, myalgia, arthralgia, chills, photophobia and nausea; frequently relapsing after a few days of apparent recovery. Aseptic meningitis and meningoencephalitis occur. Vertical transmission with fetal loss and congenital anomalies reported during the 2024 expansion, as well as rare fatalities.",
    transmission="Urban/peri-urban cycle via the biting midge Culicoides paraensis; sylvatic cycle involving mosquitoes. Vertical (mother-to-fetus) transmission documented.",
    vectors=["Culicoides paraensis (principal urban vector)", "Culex quinquefasciatus", "Coquillettidia venezuelensis"],
    reservoir="Sylvatic cycle in non-human primates, sloths (Bradypus) and birds; humans amplify the urban cycle.",
    geography="Amazon basin — Brazil, Peru, Bolivia, Ecuador, Colombia, Panama, Trinidad; marked 2024 expansion including Cuba and travel-associated cases exported to Europe and North America.",
    incubation="Typically 3–8 days.",
    diagnosis="RT-PCR on acute serum (first ~5 days), IgM/IgG ELISA, virus isolation. Clinically indistinguishable from dengue — co-circulation demands specific testing.",
    management="Supportive. Avoid NSAIDs until dengue is excluded. No specific antiviral.",
    prevention="Midge control is difficult (C. paraensis is tiny and bites outdoors by day); fine-mesh screening, repellents, reduction of peridomestic breeding (decaying banana/cacao debris).",
    evidence=[
        "Repeatedly isolated from blood of febrile patients since the 1955 Trinidad index case; hundreds of thousands of cases in documented epidemics.",
        "Reassortant members of the same species (Iquitos, Madre de Dios viruses) also recovered from human febrile cases in Peru and Venezuela.",
        "2024 expansion produced the first well-documented deaths and vertically transmitted fetal infections.",
    ],
    refs=[
        {"label": "PAHO/WHO Oropouche epidemiological alerts, 2024–2025", "url": "https://www.paho.org/en/topics/oropouche"},
        {"label": "Oropouche fever reviews, Lancet Infect Dis / NEJM 2024–2025"},
    ],
)

profile(
    "Orthobunyavirus akabaneense",
    names=["Akabane virus (AKAV)", "Tinaroo virus"],
    tier="animal-only",
    headline="Classical teratogenic Simbu-serogroup virus of ruminants; the cause of epizootic arthrogryposis–hydranencephaly in cattle, sheep and goats.",
    syndrome="No accepted human disease. In ruminants, infection of the pregnant dam causes abortion, stillbirth, arthrogryposis and hydranencephaly in the fetus, depending on gestational timing.",
    transmission="Culicoides biting midges; transplacental in the ruminant host.",
    vectors=["Culicoides brevitarsis", "Culicoides oxystoma", "other Culicoides spp."],
    reservoir="Cattle, sheep, goats, buffalo.",
    geography="Australia, East and Southeast Asia, Middle East, Africa.",
    incubation="n/a (human)",
    diagnosis="Veterinary: virus neutralisation, ELISA, RT-PCR on fetal tissues.",
    management="n/a — veterinary vaccines are used in Japan, Korea and Australia.",
    prevention="Vaccination of breeding stock; vector control.",
    evidence=[
        "Decades of veterinary surveillance with no substantiated human disease, despite intense human exposure in endemic livestock regions.",
        "Serves as the comparator that frames why Simbu-serogroup viruses are screened for teratogenicity.",
    ],
    refs=[{"label": "OIE/WOAH Akabane disease technical disease card"}],
)

profile(
    "Orthobunyavirus schmallenbergense",
    names=["Schmallenberg virus (SBV)", "Sathuperi virus (SATV)", "Shamonda virus", "Douglas virus"],
    tier="possible",
    headline="Emerged in northwest Europe in 2011 as a ruminant teratogen; extensive human serosurveys of exposed farmers and veterinarians have found no convincing evidence of human infection.",
    syndrome="No human syndrome identified. In ruminants: transient fever, milk drop and diarrhoea in adults; congenital malformations when infection occurs in mid-gestation.",
    transmission="Culicoides biting midges.",
    vectors=["Culicoides obsoletus complex", "Culicoides dewulfi"],
    reservoir="Cattle, sheep, goats; wild ruminants.",
    geography="Europe (since 2011), with related members (Sathuperi, Shamonda) in Africa and Asia.",
    incubation="n/a (human)",
    diagnosis="Veterinary RT-PCR and serology.",
    management="Supportive/veterinary; inactivated vaccines licensed in Europe.",
    prevention="Herd vaccination and vector management.",
    evidence=[
        "Targeted serological studies of highly exposed European farmers and veterinarians after the 2011–2012 epizootic found no or non-specific reactivity, arguing against zoonotic potential.",
        "Included here because its close relatives in the same species (Sathuperi, Shamonda) circulate in regions with weaker human surveillance.",
    ],
    refs=[{"label": "ECDC rapid risk assessment: Schmallenberg virus, 2012"}],
)

profile(
    "Orthobunyavirus shuniense",
    names=["Shuni virus (SHUV)"],
    tier="possible",
    headline="Simbu-serogroup virus causing neurological disease in horses and ruminants in southern Africa, with serological and occupational evidence pointing to human exposure.",
    syndrome="In animals: encephalitis, ataxia and abortion. In humans: antibodies reported in febrile patients and veterinary workers in Nigeria and South Africa; one historical isolation from a febrile child is cited in older literature, but a defined human syndrome is not established.",
    transmission="Culicoides biting midges and mosquitoes.",
    vectors=["Culicoides spp.", "Culex spp."],
    reservoir="Ruminants, horses, wild mammals.",
    geography="Sub-Saharan Africa (notably South Africa, Nigeria), with detections in Israel.",
    incubation="Not established.",
    diagnosis="RT-PCR, serology; rarely tested outside research settings.",
    management="Supportive.",
    prevention="Vector avoidance; occupational precautions in veterinary work.",
    evidence=[
        "Recurrent detection in neurological cases in South African horses and ruminants.",
        "Human seropositivity among occupationally exposed groups; causal attribution remains open.",
    ],
    refs=[{"label": "Shuni virus neurological disease, South Africa — Emerg Infect Dis"}],
)

profile(
    "Orthobunyavirus manzanillaense",
    names=["Manzanilla virus", "Inini virus"],
    tier="possible",
    headline="Prototype of the Manzanilla clade — the sublineage that also contains Cat Que/Oya virus. Mainly detected in mosquitoes, pigs and birds.",
    syndrome="No defined human syndrome; serological cross-reactivity within the clade complicates attribution.",
    transmission="Mosquito-borne, with pigs and birds as vertebrate hosts.",
    vectors=["Culex spp.", "Aedes spp."],
    reservoir="Pigs, birds, non-human primates.",
    geography="Trinidad, South America, Southeast Asia (clade members).",
    incubation="Not established.",
    diagnosis="Neutralisation and RT-PCR; clade members require sequence-level discrimination.",
    management="Supportive.",
    prevention="Vector avoidance.",
    evidence=[
        "Clade-level serological surveys cannot separate Manzanilla from Cat Que/Oya without sequencing, so human exposure data for the clade are pooled and hard to attribute.",
    ],
    refs=[{"label": "Manzanilla clade phylogenetics — see Cat Que / Oya references"}],
)

profile(
    "Orthobunyavirus lacrosseense",
    names=["La Crosse virus (LACV)"],
    tier="established",
    headline="Leading cause of paediatric arboviral encephalitis in the United States, in the California serogroup.",
    syndrome="Most infections are asymptomatic or a nonspecific summer febrile illness. In children, aseptic meningitis and encephalitis with seizures; status epilepticus and focal deficits occur, with occasional death and lasting neurocognitive and epileptic sequelae.",
    transmission="Bite of Aedes triseriatus (eastern treehole mosquito); maintained by transovarial transmission in the vector and amplified in small mammals.",
    vectors=["Aedes triseriatus", "Aedes albopictus and Ae. japonicus (accessory)"],
    reservoir="Eastern chipmunks and tree squirrels; the virus overwinters in mosquito eggs.",
    geography="Upper Midwest and Appalachian United States.",
    incubation="5–15 days.",
    diagnosis="Serum and CSF IgM (MAC-ELISA) with confirmatory neutralisation; RT-PCR insensitive because viraemia is brief.",
    management="Supportive, with seizure control and intensive-care neurology support.",
    prevention="Removal of peridomestic water-holding containers and tree holes, repellents, screening.",
    evidence=[
        "Hundreds of neuroinvasive cases confirmed by CSF serology under US national arboviral surveillance each decade.",
    ],
    refs=[{"label": "CDC La Crosse encephalitis surveillance", "url": "https://www.cdc.gov/la-crosse-encephalitis/"}],
)

profile(
    "Orthobunyavirus encephalitidis",
    names=["California encephalitis virus (CEV)", "Morro Bay virus"],
    tier="established",
    headline="Prototype of the California serogroup; historically important, now a rare cause of human encephalitis compared with La Crosse virus.",
    syndrome="Aseptic meningitis and encephalitis, classically in children in the western United States.",
    transmission="Mosquito-borne (Aedes/Ochlerotatus spp.) with lagomorph and rodent hosts.",
    vectors=["Aedes melanimon", "Aedes dorsalis"],
    reservoir="Jackrabbits, ground squirrels.",
    geography="Western United States.",
    incubation="5–15 days.",
    diagnosis="Serology with serogroup cross-reactivity; neutralisation needed for species assignment.",
    management="Supportive.",
    prevention="Mosquito avoidance.",
    evidence=["Original 1943 isolations from encephalitis cases in California defined the serogroup."],
    refs=[{"label": "California serogroup virus reviews"}],
)

profile(
    "Orthobunyavirus jamestownense",
    names=["Jamestown Canyon virus (JCV)", "Inkoo virus", "Jerry Slough virus", "South River virus"],
    tier="established",
    headline="California-serogroup virus causing febrile and neuroinvasive disease mainly in adults in North America; Inkoo virus is its Eurasian counterpart.",
    syndrome="Febrile illness with prominent respiratory symptoms, meningitis and meningoencephalitis; unlike La Crosse virus, it affects adults disproportionately.",
    transmission="Multiple Aedes/Ochlerotatus and Coquillettidia mosquitoes; white-tailed deer are the main amplifying host.",
    vectors=["Aedes spp.", "Coquillettidia perturbans"],
    reservoir="White-tailed deer and other cervids.",
    geography="United States and Canada; Inkoo virus across northern Europe and Russia.",
    incubation="Days to ~2 weeks.",
    diagnosis="IgM serology with neutralisation; cross-reacts with other California-serogroup viruses.",
    management="Supportive.",
    prevention="Mosquito avoidance.",
    evidence=["Increasing numbers of laboratory-confirmed neuroinvasive cases reported to US surveillance since the 2010s."],
    refs=[{"label": "CDC Jamestown Canyon virus", "url": "https://www.cdc.gov/jamestown-canyon/"}],
)

profile(
    "Orthobunyavirus tahynaense",
    names=["Ťahyňa virus (TAHV)", "Lumbo virus"],
    tier="established",
    headline="European California-serogroup virus causing 'Valtice fever'.",
    syndrome="Influenza-like illness with fever, headache, pharyngitis and gastrointestinal symptoms; occasional CNS involvement. High background seroprevalence in central Europe.",
    transmission="Aedes vexans and related floodwater mosquitoes; hares and hedgehogs as hosts.",
    vectors=["Aedes vexans", "Culiseta annulata"],
    reservoir="Hares, rabbits, hedgehogs.",
    geography="Central and southern Europe, Russia, Central Asia, Africa (Lumbo virus).",
    incubation="3–7 days.",
    diagnosis="Serology (neutralisation/IgM); rarely sought.",
    management="Supportive.",
    prevention="Mosquito avoidance in floodplain habitats.",
    evidence=["Seroprevalence up to 60% in some central European populations with clinically characterised 'Valtice fever' cases."],
    refs=[{"label": "Ťahyňa virus epidemiology reviews"}],
)

profile(
    "Orthobunyavirus bunyamweraense",
    names=["Bunyamwera virus (BUNV)", "Germiston virus", "Ngari virus (NRIV)", "Xingu virus", "Mboké virus", "Stanfield virus"],
    tier="established",
    headline="Prototype orthobunyavirus. Its reassortant member Ngari virus (Bunyamwera backbone with Batai M segment) causes haemorrhagic fever in East Africa.",
    syndrome="Bunyamwera and Germiston viruses: self-limiting fever with headache, rash and arthralgia. Ngari virus: documented haemorrhagic fever outbreaks in Kenya and Somalia, originally mistaken for Rift Valley fever.",
    transmission="Mosquito-borne (Aedes, Anopheles, Culex).",
    vectors=["Aedes spp.", "Anopheles spp."],
    reservoir="Rodents and other small mammals; vertebrate hosts incompletely defined.",
    geography="Sub-Saharan Africa; Xingu virus in South America.",
    incubation="Days.",
    diagnosis="RT-PCR and serology; segment-level sequencing is required to recognise reassortants such as Ngari.",
    management="Supportive.",
    prevention="Vector avoidance.",
    evidence=[
        "Bunyamwera virus isolated from humans and mosquitoes in Uganda (1943) — the genus prototype and the standard laboratory model.",
        "Ngari virus recovered from haemorrhagic fever patients during the 1997–1998 East African outbreak, demonstrating that orthobunyavirus reassortment can create new human pathogens.",
    ],
    refs=[{"label": "Ngari virus and East African haemorrhagic fever — J Clin Microbiol / Science reports"}],
)

profile(
    "Orthobunyavirus bataiense",
    names=["Batai virus (BATV)", "Calovo virus", "Chittoor virus"],
    tier="probable",
    headline="Widespread Bunyamwera-serogroup virus of Eurasia and Africa; donor of the M segment that created Ngari virus.",
    syndrome="Mild influenza-like febrile illness reported in humans; clinical burden poorly quantified.",
    transmission="Anopheles and Aedes mosquitoes; ruminants and birds as hosts.",
    vectors=["Anopheles maculipennis", "Aedes vexans"],
    reservoir="Ruminants, pigs, birds.",
    geography="Europe, Asia, Africa.",
    incubation="Not well defined.",
    diagnosis="Serology, RT-PCR.",
    management="Supportive.",
    prevention="Vector avoidance.",
    evidence=[
        "Human seroprevalence across Europe and Asia with sporadic isolations; its principal recognised importance is as a reassortment partner.",
    ],
    refs=[{"label": "Batai virus reviews"}],
)

profile(
    "Orthobunyavirus cacheense",
    names=["Cache Valley virus (CVV)", "Tlacotalpan virus", "Cholul virus", "Playas virus"],
    tier="established",
    headline="North American Bunyamwera-serogroup virus; a teratogen in sheep and a rare cause of severe human neuroinvasive disease.",
    syndrome="Rare but documented human meningoencephalitis and multi-organ disease, including fatal cases; mild febrile illness is likely far more common. In sheep, it causes abortion and congenital malformation.",
    transmission="Many mosquito species; white-tailed deer and other cervids amplify.",
    vectors=["Anopheles quadrimaculatus", "Aedes spp.", "Coquillettidia perturbans"],
    reservoir="Deer, sheep and other ungulates.",
    geography="North and Central America.",
    incubation="Not established.",
    diagnosis="CSF/serum serology and RT-PCR at reference laboratories.",
    management="Supportive.",
    prevention="Mosquito avoidance.",
    evidence=["Several well-documented human neuroinvasive and fatal cases confirmed virologically in the US and Canada."],
    refs=[{"label": "Cache Valley virus human disease case series"}],
)

profile(
    "Orthobunyavirus guaroaense",
    names=["Guaroa virus (GROV)"],
    tier="established",
    headline="Natural reassortant bridging the California and Bunyamwera serogroups; a recognised cause of febrile illness in South America.",
    syndrome="Acute undifferentiated fever with headache and myalgia, confirmed by isolation from patients in the Amazon.",
    transmission="Anopheles mosquitoes.",
    vectors=["Anopheles spp."],
    reservoir="Incompletely defined; likely sylvatic mammals.",
    geography="Colombia, Panama, Brazil, Peru.",
    incubation="Days.",
    diagnosis="RT-PCR/isolation during acute viraemia; serology.",
    management="Supportive.",
    prevention="Vector avoidance.",
    evidence=["Repeated isolations from febrile patients in Peruvian and Colombian surveillance cohorts."],
    refs=[{"label": "Guaroa virus febrile illness, Peru — Am J Trop Med Hyg"}],
)

profile(
    "Orthobunyavirus caraparuense",
    names=["Caraparú virus", "Itaquí virus", "El Huayo virus", "Itaya virus"],
    tier="established",
    headline="Group C orthobunyavirus; a frequent cause of acute febrile illness among forest workers in the Amazon.",
    syndrome="Abrupt fever, headache, myalgia and prostration lasting 2–5 days; no documented mortality.",
    transmission="Culex (Melanoconion) mosquitoes in sylvatic cycles.",
    vectors=["Culex (Melanoconion) spp."],
    reservoir="Forest rodents and marsupials.",
    geography="Amazon basin, Panama, Trinidad.",
    incubation="Days.",
    diagnosis="Isolation/RT-PCR during viraemia; neutralisation (strong intra-group cross-reactivity).",
    management="Supportive.",
    prevention="Protective clothing and repellents during forest work.",
    evidence=["Numerous isolations from febrile humans in Brazilian and Peruvian sentinel surveillance."],
    refs=[{"label": "Group C orthobunyaviruses in Amazonian febrile illness"}],
)

profile(
    "Orthobunyavirus oribocaense",
    names=["Oriboca virus", "Murutucú virus", "Restan virus"],
    tier="established",
    headline="Group C viruses repeatedly isolated from febrile Amazonian patients.",
    syndrome="Short febrile illness with headache and myalgia.",
    transmission="Culex (Melanoconion) mosquitoes.",
    vectors=["Culex (Melanoconion) spp."],
    reservoir="Rodents and marsupials.",
    geography="Brazil, Trinidad, Suriname, French Guiana.",
    incubation="Days.",
    diagnosis="Isolation, RT-PCR, neutralisation.",
    management="Supportive.",
    prevention="Vector avoidance.",
    evidence=["Human isolations documented since the 1950s Belém arbovirus programme."],
    refs=[{"label": "Belém (Instituto Evandro Chagas) arbovirus isolations"}],
)

profile(
    "Orthobunyavirus bwambaense",
    names=["Bwamba virus (BWAV)", "Pongola virus"],
    tier="established",
    headline="Highly prevalent African orthobunyavirus causing undifferentiated fever; seroprevalence exceeds 50% in parts of East Africa.",
    syndrome="Fever, headache, backache, rash and occasional mild meningism; self-limiting.",
    transmission="Anopheles mosquitoes.",
    vectors=["Anopheles gambiae", "Anopheles funestus"],
    reservoir="Not firmly established; possibly primates.",
    geography="Sub-Saharan Africa.",
    incubation="Days.",
    diagnosis="Serology; isolation from acute sera.",
    management="Supportive.",
    prevention="Mosquito control.",
    evidence=["Isolated from febrile patients in Uganda (1937) with very high regional seroprevalence since confirmed."],
    refs=[{"label": "Bwamba fever epidemiology"}],
)

profile(
    "Orthobunyavirus tataguineense",
    names=["Tataguine virus (TATV)"],
    tier="probable",
    headline="African orthobunyavirus recovered from febrile patients with rash.",
    syndrome="Fever, rash, joint pain; self-limiting.",
    transmission="Anopheles mosquitoes.",
    vectors=["Anopheles spp."],
    reservoir="Unknown.",
    geography="West and Central Africa.",
    incubation="Not established.",
    diagnosis="Serology/isolation; rarely available.",
    management="Supportive.",
    prevention="Vector avoidance.",
    evidence=["Multiple isolations from human febrile cases in Nigeria, Senegal and Cameroon."],
    refs=[{"label": "Tataguine virus human isolations"}],
)

profile(
    "Orthobunyavirus ileshaense",
    names=["Ilesha virus (ILEV)"],
    tier="probable",
    headline="Bunyamwera-serogroup virus isolated from African febrile patients, with rare reports of haemorrhagic and neurological presentations.",
    syndrome="Fever with rash; isolated reports of meningoencephalitis and haemorrhagic manifestations.",
    transmission="Mosquito-borne (Anopheles).",
    vectors=["Anopheles spp."],
    reservoir="Unknown.",
    geography="West, Central and East Africa, Madagascar.",
    incubation="Not established.",
    diagnosis="Serology/RT-PCR.",
    management="Supportive.",
    prevention="Vector avoidance.",
    evidence=["Human isolations from Nigeria and Central African Republic; case reports of severe disease."],
    refs=[{"label": "Ilesha virus case reports"}],
)

profile(
    "Orthobunyavirus ebiense",
    names=["Ebinur Lake virus (EBIV)"],
    tier="possible",
    headline="Newly characterised Bunyamwera-serogroup virus from Xinjiang, China; studied alongside Oya virus as an emerging orthobunyavirus of concern.",
    syndrome="No confirmed human disease to date. Pathogenic in mice and competent for transmission by Culex pipiens pallens.",
    transmission="Culex mosquitoes.",
    vectors=["Culex pipiens pallens", "Culex modestus"],
    reservoir="Not established; detected in mosquitoes and ticks.",
    geography="Northwestern China (Ebinur Lake, Xinjiang).",
    incubation="n/a",
    diagnosis="Specific RT-qPCR (95% LOD ~0.37 PFU/mL).",
    management="n/a",
    prevention="Vector surveillance.",
    evidence=[
        "Culex pipiens pallens showed a transmission rate up to 15.4% with 3.3% transmission efficiency in oral-infection experiments — true vector competence, unlike for Oya virus.",
        "Shares the AhR–CYP1A1 interferon-evasion mechanism with Oya virus.",
    ],
    refs=[
        {"label": "Vector range of Oya and Ebinur Lake viruses. Parasit Vectors 2024", "doi": "10.1186/s13071-024-06295-5", "pmid": "38715075"},
        {"label": "RT-qPCR assays for Oya and Ebinur Lake viruses. Virus Res 2023", "doi": "10.1016/j.virusres.2023.199265", "pmid": "37940076"},
    ],
)

profile(
    "Orthobunyavirus khatangaense",
    names=["snowshoe hare virus (SSHV)", "Khatanga virus"],
    tier="probable",
    headline="California-serogroup virus of boreal North America and Eurasia.",
    syndrome="Febrile illness and rare meningoencephalitis, mainly reported from Canada and Russia.",
    transmission="Aedes mosquitoes; snowshoe hares and small mammals as hosts.",
    vectors=["Aedes spp."],
    reservoir="Snowshoe hares, squirrels.",
    geography="Canada, Alaska, northern Eurasia.",
    incubation="Days.",
    diagnosis="Serology with neutralisation.",
    management="Supportive.",
    prevention="Mosquito avoidance.",
    evidence=["Sporadic virologically supported human CNS cases in Canada."],
    refs=[{"label": "Snowshoe hare virus encephalitis, Canada"}],
)

# ---------------------------------------------------------------------------
# Other families -- anchors so every major clade has something authoritative
# ---------------------------------------------------------------------------

profile(
    "Orthoflavivirus denguei",
    names=["dengue virus 1–4 (DENV-1, DENV-2, DENV-3, DENV-4)"],
    tier="established",
    headline="The most important arboviral infection of humans worldwide, with an estimated 100–400 million infections annually.",
    syndrome="Dengue fever: high fever, severe headache, retro-orbital pain, myalgia/arthralgia ('breakbone fever'), rash. A minority progress at defervescence to dengue with warning signs or severe dengue — plasma leakage, shock, haemorrhage and organ impairment. Secondary infection with a different serotype raises severe-disease risk through antibody-dependent enhancement.",
    transmission="Aedes aegypti and Ae. albopictus; human–mosquito–human urban cycle with no need for an animal reservoir.",
    vectors=["Aedes aegypti", "Aedes albopictus"],
    reservoir="Humans (urban cycle); sylvatic primate cycles exist in Asia and West Africa.",
    geography="Tropics and subtropics worldwide; expanding with vector range.",
    incubation="4–10 days.",
    diagnosis="NS1 antigen and RT-PCR in the first ~5 days; IgM/IgG thereafter. Serial haematocrit and platelet monitoring guide clinical management.",
    management="No specific antiviral. Careful fluid management per WHO severity categories is the intervention that saves lives; avoid NSAIDs and intramuscular injections.",
    prevention="Vector control, Wolbachia-based mosquito replacement, and the live-attenuated vaccines CYD-TDV (serostatus-restricted) and TAK-003.",
    evidence=["Over a century of virological, serological and epidemiological confirmation; among the best-characterised human viral infections."],
    refs=[{"label": "WHO dengue guidelines", "url": "https://www.who.int/health-topics/dengue"}],
)

profile(
    "Orthoflavivirus nilense",
    names=["West Nile virus (WNV)", "Kunjin virus"],
    tier="established",
    headline="Globally the most widespread encephalitic flavivirus, maintained in a bird–mosquito cycle.",
    syndrome="About 80% of infections are asymptomatic; 20% develop West Nile fever; <1% develop neuroinvasive disease — meningitis, encephalitis or a poliomyelitis-like acute flaccid paralysis, with substantial mortality and long-term sequelae in older adults.",
    transmission="Culex mosquitoes; also transfusion, transplantation, and rare vertical and laboratory transmission.",
    vectors=["Culex pipiens", "Culex quinquefasciatus", "Culex tarsalis"],
    reservoir="Birds (passerines, corvids); humans and horses are dead-end hosts.",
    geography="Africa, Europe, Middle East, Asia, Australia (Kunjin), and across the Americas since 1999.",
    incubation="2–14 days.",
    diagnosis="CSF and serum IgM; RT-PCR has low sensitivity in immunocompetent patients but is useful in immunosuppressed and in blood-donor screening.",
    management="Supportive; no proven antiviral or immunotherapy.",
    prevention="Mosquito control and personal protection; blood-supply nucleic-acid screening; equine vaccines exist but no human vaccine.",
    evidence=["Decades of surveillance with CSF-confirmed neuroinvasive disease and well-documented transfusion transmission."],
    refs=[{"label": "CDC West Nile virus", "url": "https://www.cdc.gov/west-nile-virus/"}],
)

profile(
    "Orthoflavivirus zikaense",
    names=["Zika virus (ZIKV)"],
    tier="established",
    headline="Flavivirus whose 2015–2016 American epidemic established it as a human teratogen.",
    syndrome="Usually mild or asymptomatic: low-grade fever, maculopapular rash, conjunctivitis, arthralgia. Congenital Zika syndrome — microcephaly, cerebral calcification, ocular and joint anomalies — follows infection in pregnancy. Guillain–Barré syndrome is an established post-infectious complication.",
    transmission="Aedes mosquitoes; also sexual, vertical and transfusion transmission.",
    vectors=["Aedes aegypti", "Aedes albopictus"],
    reservoir="Humans in epidemic settings; non-human primates in sylvatic cycles.",
    geography="Africa, Asia, Pacific, Americas.",
    incubation="3–14 days.",
    diagnosis="RT-PCR on serum and urine (urine positive longer); serology confounded by dengue cross-reactivity, needing plaque-reduction neutralisation.",
    management="Supportive; pregnancy surveillance with serial fetal ultrasound.",
    prevention="Vector control, barrier contraception or abstinence after exposure, travel advice in pregnancy. No licensed vaccine.",
    evidence=["Causal link to congenital anomalies established by viral detection in fetal brain tissue, cohort studies and animal models."],
    refs=[{"label": "WHO Zika virus fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/zika-virus"}],
)

profile(
    "Orthoflavivirus japonicum",
    names=["Japanese encephalitis virus (JEV)"],
    tier="established",
    headline="The leading cause of vaccine-preventable viral encephalitis in Asia.",
    syndrome="Fewer than 1% of infections become clinical, but encephalitis carries ~20–30% mortality and leaves neurological or psychiatric sequelae in a third to a half of survivors; parkinsonian and acute flaccid paralysis presentations are characteristic.",
    transmission="Culex tritaeniorhynchus in rice-paddy ecosystems; pigs amplify and ardeid water birds maintain the cycle.",
    vectors=["Culex tritaeniorhynchus", "Culex vishnui complex"],
    reservoir="Ardeid wading birds; pigs as amplifying hosts.",
    geography="South, Southeast and East Asia, Papua New Guinea, northern Australia.",
    incubation="5–15 days.",
    diagnosis="CSF/serum IgM capture ELISA.",
    management="Supportive intensive care.",
    prevention="Highly effective inactivated and live-attenuated vaccines (e.g. IXIARO, SA 14-14-2) in routine childhood programmes; pig husbandry siting; vector control.",
    evidence=["Large vaccine trials and decades of CSF-confirmed surveillance give unambiguous causal evidence."],
    refs=[{"label": "WHO Japanese encephalitis fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/japanese-encephalitis"}],
)

profile(
    "Orthoflavivirus flavi",
    names=["yellow fever virus (YFV)"],
    tier="established",
    headline="The prototype flavivirus and the reason the genus is named 'flavi' — a vaccine-preventable viral haemorrhagic fever.",
    syndrome="Biphasic: an initial fever with headache and myalgia, brief remission, then in ~15% a toxic phase with jaundice, haemorrhage, renal failure and shock; case fatality in the toxic phase is 30–60%.",
    transmission="Urban cycle via Aedes aegypti; sylvatic cycle via Haemagogus and Sabethes mosquitoes with non-human primates.",
    vectors=["Aedes aegypti", "Haemagogus spp.", "Sabethes spp."],
    reservoir="Non-human primates (sylvatic); humans (urban).",
    geography="Tropical South America and sub-Saharan Africa.",
    incubation="3–6 days.",
    diagnosis="RT-PCR early; IgM serology later; histopathology of liver (Councilman bodies) post-mortem.",
    management="Supportive intensive care.",
    prevention="A single dose of the 17D live-attenuated vaccine gives lifelong protection — one of the most effective vaccines ever made; mandated under International Health Regulations for travel to endemic areas.",
    evidence=["Walter Reed Commission human-transmission experiments (1900) and a century of vaccine and surveillance data."],
    refs=[{"label": "WHO yellow fever fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/yellow-fever"}],
)

profile(
    "Orthoflavivirus kyasanurense",
    names=["Kyasanur Forest disease virus (KFDV)", "Alkhumra haemorrhagic fever virus (AHFV)"],
    tier="established",
    headline="Tick-borne flavivirus causing haemorrhagic fever in the Western Ghats of India, with the Alkhumra variant on the Arabian peninsula.",
    syndrome="Abrupt fever with haemorrhage, and in a substantial minority a second phase of meningoencephalitis; case fatality 3–10%.",
    transmission="Haemaphysalis spinigera tick bite; also handling infected animal carcasses, and for Alkhumra virus contact with infected livestock or raw milk.",
    vectors=["Haemaphysalis spinigera and related ticks"],
    reservoir="Small mammals and monkeys (langurs, bonnet macaques — monkey die-offs herald outbreaks).",
    geography="Karnataka and neighbouring Indian states; Saudi Arabia and Yemen (Alkhumra).",
    incubation="3–8 days.",
    diagnosis="RT-PCR and IgM serology at reference laboratories.",
    management="Supportive.",
    prevention="A formalin-inactivated vaccine is used in Karnataka; tick avoidance and acaricide use in forest workers.",
    evidence=["Continuous outbreak documentation since 1957 with virological confirmation."],
    refs=[{"label": "Kyasanur Forest disease — ICMR/NIV reviews"}],
)

profile(
    "Orthoflavivirus neudoerflense",
    names=["tick-borne encephalitis virus, European subtype (TBEV-Eu)"],
    tier="established",
    headline="Principal cause of tick-borne encephalitis in Europe; vaccine-preventable.",
    syndrome="Often biphasic — a febrile viraemic phase, a symptom-free interval, then meningitis, meningoencephalitis or meningoencephalomyelitis. Mortality ~1–2% for the European subtype with frequent long-term sequelae; the Far Eastern subtype is more severe.",
    transmission="Ixodes ricinus tick bite; also unpasteurised milk and cheese from infected goats, sheep or cows.",
    vectors=["Ixodes ricinus"],
    reservoir="Small rodents; ticks maintain the virus transstadially and transovarially.",
    geography="Central, eastern and northern Europe, expanding northwards and to higher altitudes.",
    incubation="7–14 days (2–4 days for milk-borne).",
    diagnosis="Serum and CSF IgM/IgG; RT-PCR useful only in the early viraemic phase.",
    management="Supportive; corticosteroids are not of proven benefit.",
    prevention="Inactivated vaccines (FSME-IMMUN, Encepur) are highly effective; tick checks, pasteurisation of milk.",
    evidence=["Austrian mass-vaccination programme reduced incidence by roughly 90%, a decisive natural experiment."],
    refs=[{"label": "ECDC tick-borne encephalitis", "url": "https://www.ecdc.europa.eu/en/tick-borne-encephalitis"}],
)

profile(
    "Alphavirus chikungunya",
    names=["chikungunya virus (CHIKV)"],
    tier="established",
    headline="Alphavirus of the Semliki Forest complex causing explosive epidemics of febrile polyarthritis.",
    syndrome="Sudden high fever with severe, often symmetrical polyarthralgia and rash; the name means 'that which bends up'. Arthritis persists for months to years in 30–40%. Neonatal infection from intrapartum transmission and neurological disease in older adults can be severe; deaths occur mainly via decompensation of comorbidity.",
    transmission="Aedes aegypti and Ae. albopictus. The A226V envelope mutation improved Ae. albopictus transmission and drove epidemic spread outside the tropics.",
    vectors=["Aedes aegypti", "Aedes albopictus"],
    reservoir="Humans in epidemics; non-human primates in African sylvatic cycles.",
    geography="Africa, Asia, Indian Ocean, Americas since 2013, with autochthonous outbreaks in southern Europe.",
    incubation="3–7 days.",
    diagnosis="RT-PCR in the first week (viraemia is high), IgM thereafter.",
    management="Analgesia and physiotherapy; chronic arthritis may need rheumatological care.",
    prevention="Vector control; the live-attenuated vaccine IXCHIQ and the VLP vaccine VIMKUNYA are now licensed in several jurisdictions.",
    evidence=["High-titre viraemia readily detected in patients; laboratory-confirmed epidemics affecting millions."],
    refs=[{"label": "WHO chikungunya fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/chikungunya"}],
)

profile(
    "Alphavirus eastern",
    names=["eastern equine encephalitis virus (EEEV)"],
    tier="established",
    headline="The most lethal arbovirus endemic to North America.",
    syndrome="Encephalitis with fulminant onset; case fatality ~30% and severe neurological sequelae in most survivors. Infection is rare but outbreaks cluster around freshwater swamp habitats.",
    transmission="Culiseta melanura maintains the bird cycle; bridge vectors (Coquillettidia, Aedes, Culex) infect humans and horses.",
    vectors=["Culiseta melanura", "Coquillettidia perturbans", "Aedes spp."],
    reservoir="Passerine birds in freshwater hardwood swamps.",
    geography="Atlantic and Gulf coasts of the United States, Great Lakes region, Caribbean.",
    incubation="4–10 days.",
    diagnosis="CSF/serum IgM; RT-PCR on brain tissue; MRI shows basal ganglia and thalamic lesions.",
    management="Supportive intensive care; no specific therapy.",
    prevention="Mosquito avoidance and aerial larviciding during amplification; equine vaccine available, none for humans.",
    evidence=["Virologically and histopathologically confirmed fatal human encephalitis over many decades."],
    refs=[{"label": "CDC eastern equine encephalitis", "url": "https://www.cdc.gov/eastern-equine-encephalitis/"}],
)

profile(
    "Alphavirus venezuelan",
    names=["Venezuelan equine encephalitis virus (VEEV), subtypes IAB/IC/ID/IE"],
    tier="established",
    headline="Epizootic alphavirus causing large human and equine outbreaks in the Americas; also a classical laboratory-acquired infection.",
    syndrome="Influenza-like illness with fever, headache, myalgia and prostration in most; encephalitis in ~4% of children and <1% of adults. Infection in pregnancy can cause fetal loss.",
    transmission="Mosquito-borne (many genera); highly infectious by aerosol, which accounts for laboratory-acquired cases.",
    vectors=["Aedes (Ochlerotatus) taeniorhynchus", "Psorophora spp.", "Culex (Melanoconion) spp. (enzootic)"],
    reservoir="Equines amplify epizootic subtypes; rodents maintain enzootic subtypes.",
    geography="Central and South America, with historical incursions into Texas.",
    incubation="1–6 days.",
    diagnosis="RT-PCR during viraemia; IgM serology.",
    management="Supportive.",
    prevention="Equine vaccination (which interrupts amplification), vector control, and biosafety containment in laboratories.",
    evidence=["Human isolations from thousands of cases during the 1962–1971 and 1995 epidemics; documented aerosol laboratory infections."],
    refs=[{"label": "VEE epidemiology reviews"}],
)

profile(
    "Alphavirus rossriver",
    names=["Ross River virus (RRV)"],
    tier="established",
    headline="The most commonly notified arboviral infection in Australia.",
    syndrome="Epidemic polyarthritis: symmetrical joint pain and swelling, rash and fatigue, often lasting months. No deaths attributed.",
    transmission="Mosquito-borne with marsupial reservoirs.",
    vectors=["Culex annulirostris", "Aedes vigilax", "Aedes notoscriptus"],
    reservoir="Macropods (kangaroos, wallabies).",
    geography="Australia, Papua New Guinea, Pacific islands.",
    incubation="7–9 days.",
    diagnosis="IgM/IgG serology; RT-PCR rarely positive by presentation.",
    management="Analgesia and graded exercise.",
    prevention="Mosquito avoidance; no vaccine.",
    evidence=["Thousands of serologically confirmed notifications annually with a well-defined clinical syndrome."],
    refs=[{"label": "Australian Department of Health RRV surveillance"}],
)

profile(
    "Phlebovirus riftense",
    names=["Rift Valley fever virus (RVFV)"],
    tier="established",
    headline="Zoonotic phlebovirus causing devastating ruminant abortion storms and human haemorrhagic fever; a WHO priority pathogen.",
    syndrome="Most human infections are a self-limiting febrile illness. Complications: retinitis with permanent visual loss (1–10%), meningoencephalitis, and haemorrhagic fever with hepatic failure (<1%, but ~50% fatal).",
    transmission="Mosquito bite (Aedes, Culex) but most human infections follow direct contact with blood, tissues or aborted material from infected livestock — slaughtering, butchering, veterinary and husbandry work; also raw milk.",
    vectors=["Aedes mcintoshi (and other floodwater Aedes, with transovarial maintenance)", "Culex spp."],
    reservoir="Sheep, goats, cattle, camels; virus persists in Aedes eggs between rains.",
    geography="Sub-Saharan Africa, Madagascar, Egypt, Arabian peninsula; outbreaks follow heavy rainfall and flooding.",
    incubation="2–6 days.",
    diagnosis="RT-PCR and IgM ELISA; antigen detection.",
    management="Supportive; occupational exposure requires biosafety precautions.",
    prevention="Livestock vaccination, movement controls, protective equipment during slaughter, vector control. No licensed human vaccine.",
    evidence=["Large laboratory-confirmed human outbreaks (Egypt 1977, Kenya/Somalia 1997–98 and 2006–07) with defined occupational risk factors."],
    refs=[{"label": "WHO Rift Valley fever fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/rift-valley-fever"}],
)

profile(
    "Phlebovirus toscanaense",
    host="unknown",
    names=["Toscana virus (TOSV)"],
    tier="established",
    headline="A leading cause of summer aseptic meningitis around the Mediterranean, transmitted by sandflies.",
    syndrome="Aseptic meningitis or meningoencephalitis, usually self-limiting; also undifferentiated 'summer fever'.",
    transmission="Phlebotomus sandfly bite.",
    vectors=["Phlebotomus perniciosus", "Phlebotomus perfiliewi"],
    reservoir="Sandflies maintain the virus; vertebrate reservoirs incompletely defined (dogs and cats implicated).",
    geography="Italy, Spain, France, Portugal, Greece, Turkey, North Africa.",
    incubation="Days to 2 weeks.",
    diagnosis="CSF RT-PCR and serum IgM.",
    management="Supportive.",
    prevention="Sandfly avoidance (fine mesh is needed — standard nets let sandflies through), repellents.",
    evidence=["Routinely identified in CSF of Mediterranean meningitis patients; in some series the second most common cause after enteroviruses."],
    refs=[{"label": "Toscana virus reviews, Clin Microbiol Infect"}],
)

profile(
    "Bandavirus dabieense",
    names=["severe fever with thrombocytopenia syndrome virus (SFTSV)", "Dabie bandavirus"],
    tier="established",
    headline="Tick-borne bandavirus causing a severe haemorrhagic febrile illness in East Asia, with case fatality of roughly 5–30%.",
    syndrome="Fever, thrombocytopenia, leukopenia, gastrointestinal symptoms and elevated liver enzymes, progressing in severe cases to haemorrhage, encephalopathy and multi-organ failure. Older age and high viral load predict death.",
    transmission="Haemaphysalis longicornis tick bite; person-to-person transmission through blood and body fluids is documented, including nosocomial and familial clusters, and transmission from infected cats and dogs to humans.",
    vectors=["Haemaphysalis longicornis", "Rhipicephalus microplus"],
    reservoir="Domestic and wild animals (goats, cattle, dogs, cats, deer, rodents).",
    geography="China, South Korea, Japan, Vietnam, Taiwan.",
    incubation="5–14 days.",
    diagnosis="RT-PCR, IgM/IgG serology, virus isolation.",
    management="Supportive. Favipiravir has been trialled with uncertain benefit; plasma exchange used in severe cases.",
    prevention="Tick avoidance, protective measures in animal handling, strict infection control for contact with patients' blood and secretions.",
    evidence=["Identified in 2009–2011 from clusters in central China; thousands of confirmed cases with documented person-to-person and animal-to-human transmission."],
    refs=[{"label": "SFTSV reviews, Lancet Infect Dis / NEJM"}],
)

profile(
    "Bandavirus heartlandense",
    names=["Heartland virus (HRTV)"],
    tier="established",
    headline="North American counterpart of SFTSV, transmitted by the lone star tick.",
    syndrome="Fever, fatigue, anorexia, thrombocytopenia and leukopenia; deaths reported, mostly in older adults with comorbidity.",
    transmission="Amblyomma americanum tick bite.",
    vectors=["Amblyomma americanum"],
    reservoir="White-tailed deer, raccoons and other wildlife (serological evidence).",
    geography="Central and eastern United States.",
    incubation="~2 weeks.",
    diagnosis="RT-PCR and serology at CDC/state laboratories.",
    management="Supportive; doxycycline is ineffective, which matters because the illness mimics ehrlichiosis.",
    prevention="Tick avoidance.",
    evidence=["First two cases reported in Missouri in 2012 with virus isolation; dozens of confirmed cases since."],
    refs=[{"label": "CDC Heartland virus", "url": "https://www.cdc.gov/heartland-virus/"}],
)

profile(
    "Orthonairovirus haemorrhagiae",
    names=["Crimean-Congo haemorrhagic fever virus (CCHFV)"],
    tier="established",
    headline="The most geographically widespread tick-borne virus causing human haemorrhagic fever; a WHO priority pathogen requiring high-level containment.",
    syndrome="Abrupt fever, myalgia, severe headache, then haemorrhagic manifestations, hepatic dysfunction and DIC. Case fatality ranges from 5% to 40%. Nosocomial outbreaks among healthcare workers are a defining feature.",
    transmission="Hyalomma tick bite, crushing infected ticks, contact with blood or tissues of viraemic livestock during slaughter, and person-to-person via blood and body fluids.",
    vectors=["Hyalomma marginatum", "Hyalomma anatolicum"],
    reservoir="Ticks (transovarial and transstadial), with amplification in cattle, sheep, goats and hares — all of which remain healthy.",
    geography="Africa, the Balkans, Middle East, Central and South Asia, western China; expanding with Hyalomma range into Spain and southern Europe.",
    incubation="1–9 days after tick bite; 5–13 days after blood contact.",
    diagnosis="RT-PCR and antigen detection in BSL-4/BSL-3+ laboratories; IgM/IgG appear late and may be absent in fatal cases.",
    management="Supportive with aggressive blood-product replacement; ribavirin is used widely though trial evidence is inconclusive.",
    prevention="Tick protection, safe slaughter practice, and strict barrier nursing with full PPE. No licensed vaccine (a Bulgarian inactivated vaccine has limited use).",
    evidence=["Extensive virologically confirmed outbreak and nosocomial transmission literature spanning sixty years."],
    refs=[{"label": "WHO CCHF fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/crimean-congo-haemorrhagic-fever"}],
)

profile(
    "Mammarenavirus lassaense",
    names=["Lassa virus (LASV)"],
    tier="established",
    headline="Rodent-borne arenavirus causing 100,000–300,000 infections and thousands of deaths annually in West Africa.",
    syndrome="Insidious fever, sore throat, retrosternal pain, vomiting and diarrhoea; severe cases develop facial oedema, mucosal bleeding, shock and encephalopathy. Overall community case fatality ~1%, but 15–20% in hospitalised patients. Sensorineural deafness in up to a third of survivors is the hallmark sequela, and third-trimester infection carries very high fetal and maternal mortality.",
    transmission="Exposure to urine or droppings of Mastomys natalensis (the natal multimammate mouse) through contaminated food, dust or rodent consumption; person-to-person and nosocomial transmission via body fluids.",
    vectors=["None (rodent-borne, not arthropod-borne)"],
    reservoir="Mastomys natalensis and related rodents, which are persistently and asymptomatically infected.",
    geography="Nigeria, Sierra Leone, Liberia, Guinea, Benin, Ghana, Mali, Togo.",
    incubation="2–21 days.",
    diagnosis="RT-PCR (the mainstay), antigen ELISA, IgM/IgG.",
    management="Supportive care with attention to fluid and electrolyte balance; intravenous ribavirin is widely used on the basis of older observational data now under re-evaluation.",
    prevention="Rodent control, safe food storage, hospital infection control; vaccines are in clinical development (CEPI priority).",
    evidence=["Continuous virologically confirmed seasonal epidemics with detailed cohort data from Nigeria and Sierra Leone."],
    refs=[{"label": "WHO Lassa fever fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/lassa-fever"}],
)

profile(
    "Mammarenavirus choriomeningitidis",
    names=["lymphocytic choriomeningitis virus (LCMV)", "Dandenong virus"],
    tier="established",
    headline="Globally distributed arenavirus of house mice; a neglected cause of aseptic meningitis and of severe congenital infection.",
    syndrome="Biphasic influenza-like illness followed by aseptic meningitis or meningoencephalitis. Congenital infection causes hydrocephalus, chorioretinitis and intellectual disability, and is a frequently missed mimic of congenital toxoplasmosis and CMV. Transplant-transmitted infection is usually fatal.",
    transmission="Inhalation or ingestion of aerosolised rodent excreta; vertical transmission; organ transplantation.",
    vectors=["None (rodent-borne)"],
    reservoir="Mus musculus worldwide; pet rodents including hamsters and guinea pigs.",
    geography="Worldwide.",
    incubation="8–13 days.",
    diagnosis="CSF/serum IgM and IgG, RT-PCR; congenital cases need paired maternal-infant serology.",
    management="Supportive.",
    prevention="Rodent control; counselling pregnant women about rodent exposure and pet rodents; donor screening after transplant-associated clusters.",
    evidence=["Classic model organism virus with well-documented human meningitis, congenital syndrome and fatal transplant-transmitted clusters."],
    refs=[{"label": "CDC LCMV", "url": "https://www.cdc.gov/lymphocytic-choriomeningitis/"}],
)

profile(
    "Mammarenavirus juninense",
    names=["Junín virus (JUNV)"],
    tier="established",
    headline="Cause of Argentine haemorrhagic fever; notable for an effective live-attenuated vaccine and proven immune plasma therapy.",
    syndrome="Insidious fever, conjunctival injection, petechiae, thrombocytopenia and leukopenia; progression to haemorrhage, shock and neurological disease. Untreated case fatality 15–30%.",
    transmission="Inhalation or contact with excreta of infected corn mice, especially during mechanised harvesting.",
    vectors=["None (rodent-borne)"],
    reservoir="Calomys musculinus (drylands vesper mouse).",
    geography="The Argentine pampas.",
    incubation="6–14 days.",
    diagnosis="RT-PCR and serology.",
    management="Immune plasma given within 8 days of onset reduces mortality to below 1% — one of the clearest demonstrations of passive immunotherapy in viral disease.",
    prevention="The live-attenuated Candid#1 vaccine, used in agricultural workers, has cut incidence dramatically.",
    evidence=["Randomised and controlled studies of immune plasma and of Candid#1 vaccination give high-quality causal and interventional evidence."],
    refs=[{"label": "Argentine haemorrhagic fever and Candid#1 vaccine literature"}],
)

profile(
    "Orthohantavirus hantanense",
    names=["Hantaan virus (HTNV)", "Amur virus", "Soochong virus"],
    tier="established",
    headline="Prototype hantavirus and cause of the severe form of haemorrhagic fever with renal syndrome (HFRS) in East Asia.",
    syndrome="Five classical phases — febrile, hypotensive, oliguric, diuretic and convalescent — with haemorrhage, acute kidney injury and shock; case fatality 5–15%.",
    transmission="Inhalation of aerosolised excreta of infected rodents; no arthropod vector and essentially no person-to-person spread (except Andes virus).",
    vectors=["None (rodent-borne)"],
    reservoir="Apodemus agrarius (striped field mouse).",
    geography="Korea, China, Russian Far East.",
    incubation="2–4 weeks.",
    diagnosis="IgM/IgG serology, RT-PCR.",
    management="Supportive with careful fluid balance and renal replacement therapy; early ribavirin has shown benefit in HFRS.",
    prevention="Rodent control, dust-avoidance precautions; inactivated vaccines (Hantavax) used in Korea and China.",
    evidence=["Identified in 1976 from Apodemus lung tissue after the Korean War epidemic of ~3000 UN troops; abundant confirmed clinical data since."],
    refs=[{"label": "HFRS reviews"}],
)

profile(
    "Orthohantavirus puumalaense",
    names=["Puumala virus (PUUV)", "Hokkaido virus", "Muju virus"],
    tier="established",
    headline="Cause of nephropathia epidemica, the mild form of HFRS and the most common hantavirus disease in Europe.",
    syndrome="Fever, severe headache, abdominal and back pain, transient myopia, proteinuria and acute kidney injury; thrombocytopenia is typical. Case fatality below 0.5%, but hospitalisation is often required.",
    transmission="Inhalation of aerosolised excreta of bank voles; incidence tracks vole population cycles and mast years.",
    vectors=["None (rodent-borne)"],
    reservoir="Myodes glareolus (bank vole).",
    geography="Fennoscandia, the Baltic states, central and western Europe, Russia.",
    incubation="2–4 weeks.",
    diagnosis="IgM/IgG serology (rapid tests available); RT-PCR early.",
    management="Supportive; dialysis if needed.",
    prevention="Rodent exclusion from dwellings; precautions when cleaning sheds and cabins. No vaccine in Europe.",
    evidence=["Thousands of serologically confirmed cases annually in Finland and Sweden alone."],
    refs=[{"label": "ECDC hantavirus infection", "url": "https://www.ecdc.europa.eu/en/hantavirus-infection"}],
)

profile(
    "Orthohantavirus sinnombreense",
    names=["Sin Nombre virus (SNV)", "New York virus"],
    tier="established",
    headline="Cause of hantavirus cardiopulmonary syndrome in North America, identified during the 1993 Four Corners outbreak.",
    syndrome="A short prodrome of fever and myalgia, then abrupt non-cardiogenic pulmonary oedema and cardiogenic shock; case fatality ~35–40%. Renal involvement is minimal, in contrast to HFRS.",
    transmission="Inhalation of aerosolised excreta of deer mice, often in enclosed rural buildings.",
    vectors=["None (rodent-borne)"],
    reservoir="Peromyscus maniculatus (deer mouse).",
    geography="Western and central United States, Canada, Mexico.",
    incubation="1–5 weeks.",
    diagnosis="IgM/IgG serology, RT-PCR; immunoblast-rich peripheral smear and haemoconcentration are early clues.",
    management="Early transfer to a centre with ECMO capability is the key intervention; cautious fluid management.",
    prevention="Rodent-proofing and safe cleaning practice (wet methods, no sweeping). No vaccine.",
    evidence=["1993 outbreak investigation established the virus, reservoir and syndrome within months; continuous confirmed surveillance since."],
    refs=[{"label": "CDC hantavirus", "url": "https://www.cdc.gov/hantavirus/"}],
)

profile(
    "Orthohantavirus andesense",
    names=["Andes virus (ANDV)", "Castelo dos Sonhos virus", "Lechiguanas virus", "Orán virus"],
    tier="established",
    headline="The only hantavirus with firmly documented person-to-person transmission.",
    syndrome="Hantavirus cardiopulmonary syndrome as for Sin Nombre virus, with case fatality 25–40%.",
    transmission="Rodent excreta, and — uniquely — person-to-person spread documented in Argentine and Chilean clusters including a 2018–2019 outbreak traced through close contacts.",
    vectors=["None (rodent-borne)"],
    reservoir="Oligoryzomys longicaudatus (long-tailed pygmy rice rat).",
    geography="Argentina, Chile, and related viruses across South America.",
    incubation="1–6 weeks.",
    diagnosis="Serology and RT-PCR.",
    management="Supportive with ECMO; contact tracing and isolation are warranted, unlike for other hantaviruses.",
    prevention="Rodent control plus respiratory and contact precautions for cases.",
    evidence=["Epidemiological and genomic evidence of interhuman chains, including the El Bolsón 1996 and Epuyén 2018 outbreaks."],
    refs=[{"label": "Andes virus person-to-person transmission, NEJM / Emerg Infect Dis"}],
)

profile(
    "Lyssavirus rabies",
    cycle="animal-bite",
    names=["rabies virus (RABV)"],
    tier="established",
    headline="Effectively 100% fatal once clinical, yet entirely preventable by prompt post-exposure prophylaxis; ~59,000 deaths annually, mostly from dog bites.",
    syndrome="Prodromal pain or paraesthesia at the bite site, then either encephalitic ('furious') rabies with hydrophobia, aerophobia, agitation and autonomic instability, or paralytic ('dumb') rabies mimicking Guillain–Barré syndrome. Death follows within days to weeks.",
    transmission="Saliva of an infected mammal through a bite, scratch or mucosal contact; rare transmission by corneal and solid-organ transplantation and by aerosol in bat caves and laboratories.",
    vectors=["None (direct mammal-to-mammal)"],
    reservoir="Domestic dogs in most of Asia and Africa; bats, raccoons, skunks and foxes in the Americas and Europe.",
    geography="Worldwide except a few island nations and Antarctica.",
    incubation="Typically 1–3 months, ranging from days to over a year depending on inoculum and bite site.",
    diagnosis="Ante-mortem: saliva RT-PCR (serial samples), nuchal skin biopsy, corneal impression. Post-mortem: direct fluorescent antibody on brain, Negri bodies.",
    management="No proven treatment once symptomatic; the Milwaukee protocol is not supported by evidence. Care is palliative.",
    prevention="Immediate and thorough wound washing, rabies immunoglobulin infiltration plus vaccine series for category III exposures, pre-exposure vaccination for at-risk groups, and mass dog vaccination — the only intervention that eliminates human rabies at source.",
    evidence=["Unambiguous: viral antigen and RNA in brain tissue of cases, with a complete chain of causation and a highly effective prophylactic intervention."],
    refs=[{"label": "WHO rabies fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/rabies"}],
)

profile(
    "Henipavirus nipahense",
    cycle="intermediate",
    names=["Nipah virus (NiV)"],
    tier="established",
    headline="Bat-borne paramyxovirus with case fatality of 40–75% and documented person-to-person transmission; a WHO priority pathogen requiring BSL-4 handling.",
    syndrome="Fever and headache progressing to encephalitis with brainstem signs, segmental myoclonus and seizures; acute respiratory distress is prominent in the Bangladesh/India lineage. Relapsing and late-onset encephalitis occurs months to years after recovery.",
    transmission="Consumption of date palm sap contaminated by Pteropus bat secretions (Bangladesh/India), contact with infected pigs (the 1998–99 Malaysian outbreak), and person-to-person including nosocomial spread.",
    vectors=["None (bat reservoir, with intermediate hosts)"],
    reservoir="Pteropus fruit bats.",
    geography="Malaysia, Singapore, Bangladesh, India (Kerala, West Bengal), Philippines.",
    incubation="4–14 days, occasionally longer.",
    diagnosis="RT-PCR on throat swab, CSF, urine and blood; IgM/IgG ELISA — all in high-containment laboratories.",
    management="Supportive intensive care. Monoclonal antibody m102.4 has been given compassionately; remdesivir is protective in primate models.",
    prevention="Avoid raw date palm sap, cover sap collection pots, strict PPE and isolation for cases, pig-farm biosecurity. Vaccines are in clinical trials.",
    evidence=["Repeated laboratory-confirmed outbreaks with genomic linkage between bats, intermediate hosts and patients, and documented nosocomial chains."],
    refs=[{"label": "WHO Nipah virus fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/nipah-virus"}],
)

profile(
    "Henipavirus hendraense",
    cycle="intermediate",
    names=["Hendra virus (HeV)"],
    tier="established",
    headline="Australian henipavirus transmitted from flying foxes via horses; rare but highly lethal in humans.",
    syndrome="Influenza-like illness progressing to pneumonitis or encephalitis; four of the seven recognised human cases died.",
    transmission="Close contact with respiratory secretions and tissues of infected horses — all human cases have been horse-associated.",
    vectors=["None (bat reservoir, equine intermediate host)"],
    reservoir="Pteropus flying foxes.",
    geography="Eastern Australia (Queensland, New South Wales).",
    incubation="5–21 days.",
    diagnosis="RT-PCR and serology in high-containment laboratories.",
    management="Supportive; m102.4 monoclonal antibody available on compassionate grounds.",
    prevention="An equine vaccine (Equivac HeV) interrupts the transmission route to humans; PPE for veterinary work on sick horses.",
    evidence=["Each human case virologically confirmed with an identified equine source since the 1994 Brisbane outbreak."],
    refs=[{"label": "Hendra virus — Australian Government and Queensland Health"}],
)

profile(
    "Betacoronavirus pandemicum",
    cycle="respiratory",
    names=["SARS-CoV-2", "SARS coronavirus (SARS-CoV)"],
    tier="established",
    headline="Sarbecovirus subgenus; SARS-CoV caused the 2002–2004 SARS epidemic and SARS-CoV-2 the COVID-19 pandemic.",
    syndrome="SARS-CoV-2: asymptomatic infection through to severe pneumonia, ARDS, thromboembolic and multi-organ disease, with post-acute sequelae (long COVID). SARS-CoV: severe atypical pneumonia with ~10% case fatality and little pre-symptomatic transmission.",
    transmission="Respiratory aerosols and droplets; fomite and faecal routes are secondary.",
    vectors=["None (respiratory)"],
    reservoir="Horseshoe bats (Rhinolophus) harbour the closest relatives; intermediate hosts implicated (palm civets for SARS-CoV).",
    geography="Worldwide (SARS-CoV-2); SARS-CoV contained in 2004.",
    incubation="2–14 days (median ~3–5 days for recent SARS-CoV-2 variants).",
    diagnosis="RT-PCR and antigen testing on respiratory specimens; serology for past infection.",
    management="Antivirals (nirmatrelvir–ritonavir, remdesivir) for those at risk of progression; dexamethasone and IL-6 inhibitors for hypoxaemic disease; oxygen and ventilatory support.",
    prevention="mRNA and protein-subunit vaccines with periodic variant updates; ventilation, respirators in high-risk settings.",
    evidence=["The most intensively documented emergence of a human pathogen in history, with full genomic, clinical and interventional evidence."],
    refs=[{"label": "WHO COVID-19", "url": "https://www.who.int/health-topics/coronavirus"}],
)

profile(
    "Orthoebolavirus zairense",
    cycle="wildlife-contact",
    names=["Ebola virus (EBOV)"],
    tier="established",
    headline="Filovirus causing Ebola disease, with case fatality historically 25–90%; now treatable with monoclonal antibodies and preventable by vaccination.",
    syndrome="Abrupt fever, profound weakness, myalgia, then vomiting and high-volume diarrhoea with electrolyte derangement, shock and sometimes haemorrhage. Survivors experience uveitis, arthralgia and neurological sequelae; virus persists in semen, aqueous humour and CSF, enabling late sexual transmission and relapse.",
    transmission="Direct contact with blood or body fluids of symptomatic or deceased patients; funeral practices are a major amplifier; nosocomial transmission where PPE is inadequate.",
    vectors=["None (direct contact; bat reservoir)"],
    reservoir="Strongly implicated in fruit bats; spillover often via contact with wildlife.",
    geography="Central and West Africa — the 2013–2016 West African epidemic caused over 28,000 cases.",
    incubation="2–21 days.",
    diagnosis="RT-PCR on blood (antigen rapid tests for triage); high-containment handling.",
    management="Monoclonal antibodies ansuvimab (Ebanga) and REGN-EB3 (Inmazeb) improve survival in randomised trials, together with aggressive fluid and electrolyte support.",
    prevention="The rVSV-ZEBOV vaccine (Ervebo) used in ring vaccination, plus the Ad26/MVA regimen; safe burial practices and infection prevention and control.",
    evidence=["PALM randomised controlled trial established monoclonal antibody efficacy; ring-vaccination trial established vaccine efficacy."],
    refs=[{"label": "WHO Ebola disease fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease"}],
)

profile(
    "Orthomarburgvirus marburgense",
    cycle="wildlife-contact",
    names=["Marburg virus (MARV)", "Ravn virus (RAVV)"],
    tier="established",
    headline="The first filovirus recognised (Marburg, 1967), with case fatality in outbreaks of 24–88%; no licensed vaccine or therapeutic.",
    syndrome="Haemorrhagic fever clinically similar to Ebola disease.",
    transmission="Spillover from Egyptian rousette bats, classically in mines and caves, then person-to-person via body fluids.",
    vectors=["None (bat reservoir)"],
    reservoir="Rousettus aegyptiacus (Egyptian rousette bat).",
    geography="Angola, DRC, Uganda, Kenya, Equatorial Guinea, Tanzania, Rwanda, Ghana.",
    incubation="2–21 days.",
    diagnosis="RT-PCR in high-containment laboratories.",
    management="Supportive; candidate vaccines and antibodies deployed under trial protocols during recent outbreaks.",
    prevention="Avoid bat-inhabited mines and caves; strict IPC and safe burial.",
    evidence=["Repeated laboratory-confirmed outbreaks with genomic links to Rousettus colonies."],
    refs=[{"label": "WHO Marburg virus disease fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/marburg-virus-disease"}],
)

profile(
    "Orthopoxvirus monkeypox",
    cycle="close-contact",
    names=["monkeypox virus (MPXV)"],
    tier="established",
    headline="Orthopoxvirus causing mpox; clade I is more virulent, clade II drove the 2022 global outbreak through sexual networks.",
    syndrome="Fever, lymphadenopathy (a feature distinguishing it from smallpox-like illness without nodes) and a deep-seated vesiculopustular rash, often anogenital and oropharyngeal in sexually transmitted clade IIb infection. Proctitis, severe pain and bacterial superinfection are common; severe disease occurs in advanced HIV.",
    transmission="Close skin-to-skin and sexual contact, respiratory secretions on prolonged contact, fomites, vertical transmission, and zoonotic contact with rodents.",
    vectors=["None (contact)"],
    reservoir="African rodents (squirrels, dormice); primates are incidental hosts despite the name.",
    geography="Endemic in Central and West Africa; global clade IIb outbreak since 2022 and clade Ib expansion from eastern DRC since 2023.",
    incubation="3–17 days.",
    diagnosis="PCR on lesion swabs (the specimen of choice).",
    management="Supportive with pain control; tecovirimat showed no efficacy for clade I lesion resolution in the PALM007 trial, tempering earlier expectations.",
    prevention="MVA-BN (JYNNEOS/Imvanex) vaccination pre- and post-exposure; isolation of lesions.",
    evidence=["Tens of thousands of PCR-confirmed cases with detailed transmission-network epidemiology."],
    refs=[{"label": "WHO mpox fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/mpox"}],
)

profile(
    "Orthopoxvirus variola",
    cycle="respiratory",
    names=["variola virus (VARV)"],
    tier="established",
    headline="Cause of smallpox — the only human disease ever eradicated (certified 1980). Retained only in two WHO-authorised repositories.",
    syndrome="Variola major: prodromal fever, then a synchronous centrifugal vesiculopustular rash with ~30% case fatality; haemorrhagic and flat forms were almost uniformly fatal.",
    transmission="Respiratory droplets and contact with lesion material or contaminated linen.",
    vectors=["None"],
    reservoir="Humans only — which is why eradication was achievable.",
    geography="Eradicated.",
    incubation="7–17 days.",
    diagnosis="Historical: electron microscopy, culture. Now PCR in reference laboratories only.",
    management="Historically supportive; tecovirimat and brincidofovir are stockpiled against re-emergence.",
    prevention="Vaccinia-based vaccination; ring vaccination and surveillance-containment achieved eradication.",
    evidence=["Definitive — the eradication programme is the canonical demonstration of a single-host human pathogen.",],
    refs=[{"label": "WHO smallpox", "url": "https://www.who.int/health-topics/smallpox"}],
)

profile(
    "Lentivirus humimdef1",
    cycle="blood-sexual",
    names=["human immunodeficiency virus 1 (HIV-1)"],
    tier="established",
    headline="Retrovirus causing AIDS; roughly 40 million people live with HIV and antiretroviral therapy has transformed it into a manageable chronic infection.",
    syndrome="Acute seroconversion illness (fever, rash, pharyngitis, lymphadenopathy), then years of clinical latency with progressive CD4+ T-cell depletion, culminating in AIDS with opportunistic infections and malignancies.",
    transmission="Sexual contact, blood exposure and injecting drug use, vertical transmission and breastfeeding.",
    vectors=["None"],
    reservoir="Humans; origin in SIVcpz from chimpanzees via cross-species transmission in Central Africa.",
    geography="Worldwide, with the greatest burden in eastern and southern Africa.",
    incubation="2–4 weeks to seroconversion illness; years to AIDS without treatment.",
    diagnosis="Fourth-generation antigen/antibody immunoassay with confirmatory testing; HIV RNA for acute infection and monitoring.",
    management="Lifelong combination antiretroviral therapy achieves durable viral suppression, normal life expectancy and prevents transmission.",
    prevention="Treatment as prevention, pre- and post-exposure prophylaxis (including long-acting injectables), condoms, harm reduction, voluntary medical male circumcision, and prevention of vertical transmission.",
    evidence=["Among the most comprehensively established causal relationships in medicine, with decisive randomised trial evidence for treatment and prevention."],
    refs=[{"label": "WHO HIV", "url": "https://www.who.int/health-topics/hiv-aids"}],
)

profile(
    "Morbillivirus hominis",
    cycle="respiratory",
    names=["measles virus (MeV)"],
    tier="established",
    headline="One of the most contagious human viruses (R0 of 12–18), vaccine-preventable, and a cause of lasting immune amnesia.",
    syndrome="Prodromal fever, coryza, conjunctivitis and Koplik spots, then a confluent maculopapular rash. Complications: pneumonia, otitis media, diarrhoea, acute post-infectious encephalitis, and subacute sclerosing panencephalitis years later. Measles also deletes pre-existing antibody repertoires, raising susceptibility to other infections.",
    transmission="Airborne — infectious aerosols persist for up to two hours in a room.",
    vectors=["None"],
    reservoir="Humans only.",
    geography="Worldwide, with resurgence wherever vaccine coverage falls below ~95%.",
    incubation="7–21 days.",
    diagnosis="IgM serology, throat/nasopharyngeal and urine RT-PCR for genotyping.",
    management="Supportive; vitamin A reduces mortality in children.",
    prevention="Two doses of live-attenuated measles vaccine (MMR); post-exposure vaccine within 72 hours or immunoglobulin within 6 days.",
    evidence=["Definitive, with a century of clinical and virological data and global vaccine-impact evidence."],
    refs=[{"label": "WHO measles fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/measles"}],
)

profile(
    "Alphainfluenzavirus influenzae",
    cycle="respiratory",
    names=["influenza A virus (IAV)"],
    tier="established",
    headline="Segmented orthomyxovirus with an avian reservoir, causing seasonal epidemics and periodic pandemics through antigenic shift and reassortment.",
    syndrome="Abrupt fever, cough, myalgia, headache and malaise; complications include primary viral and secondary bacterial pneumonia, myocarditis, encephalopathy and decompensation of chronic disease. H5N1 and H7N9 zoonotic infections carry high case fatality.",
    transmission="Respiratory droplets and aerosols; zoonotic exposure to poultry, swine and, recently, dairy cattle (H5N1 clade 2.3.4.4b).",
    vectors=["None"],
    reservoir="Wild aquatic birds, with swine as a 'mixing vessel' for reassortment.",
    geography="Worldwide with seasonal patterns.",
    incubation="1–4 days.",
    diagnosis="RT-PCR on respiratory specimens with subtyping; antigen tests are less sensitive.",
    management="Oseltamivir or baloxavir early in high-risk patients; supportive care.",
    prevention="Annual reformulated vaccines, antiviral prophylaxis in outbreaks, poultry sector biosecurity and surveillance of animal-human interfaces.",
    evidence=["Continuous global virological surveillance since 1947 with full genomic characterisation of pandemics."],
    refs=[{"label": "WHO influenza (seasonal)", "url": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)"}],
)

profile(
    "Orthoflavivirus murrayense",
    names=["Murray Valley encephalitis virus (MVEV)", "Alfuy virus"],
    tier="established",
    headline="Australian member of the Japanese encephalitis serocomplex.",
    syndrome="Mostly asymptomatic or mild febrile illness; rare encephalitis with high mortality and frequent sequelae, affecting mainly children and older adults.",
    transmission="Culex annulirostris in wetland and inland floodplain cycles.",
    vectors=["Culex annulirostris"],
    reservoir="Ardeid water birds.",
    geography="Northern and inland Australia, Papua New Guinea; outbreaks follow heavy La Niña rainfall.",
    incubation="5–28 days.",
    diagnosis="CSF/serum IgM; cross-reacts with other JE-serocomplex flaviviruses.",
    management="Supportive.",
    prevention="Mosquito avoidance; sentinel chicken surveillance guides public warnings.",
    evidence=["Confirmed encephalitis cases in Australian epidemics of 1951, 1974 and 2011."],
    refs=[{"label": "MVEV — Australian arbovirus surveillance reports"}],
)

profile(
    "Orthobunyavirus kaengkhoiense",
    names=["Kaeng Khoi virus (KKV)"],
    tier="possible",
    headline="Bat-associated orthobunyavirus from Thailand, transmitted by cave-dwelling bat bugs.",
    syndrome="Antibodies and a reported isolation from febrile humans working in bat caves; clinical significance not established.",
    transmission="Bat bugs (Cimex spp.) in bat caves.",
    vectors=["Cimex insuetus and related bat bugs"],
    reservoir="Free-tailed bats (Chaerephon/Tadarida).",
    geography="Thailand, Cambodia.",
    incubation="Not established.",
    diagnosis="Research assays only.",
    management="Supportive.",
    prevention="Protective equipment for guano harvesters and cave researchers.",
    evidence=["Human seropositivity among guano collectors; occupational exposure is the main concern."],
    refs=[{"label": "Kaeng Khoi virus in bat caves, Thailand"}],
)


# Family- and genus-level orientation text shown when no species profile exists.
TAXON_NOTES = {
    "Peribunyaviridae": (
        "Tri-segmented negative-sense RNA viruses (L, M, S). The segmented genome "
        "permits reassortment between co-infecting strains, which has repeatedly "
        "generated new human pathogens — Ngari virus (haemorrhagic fever in East "
        "Africa) and Iquitos virus arose this way. The family contains the genus "
        "Orthobunyavirus, whose >130 species are traditionally sorted into about "
        "22 serogroups defined by cross-neutralisation."
    ),
    "Orthobunyavirus": (
        "The largest genus of arboviruses. Species are grouped into serogroups "
        "(Simbu, California, Bunyamwera, Group C, Guamá, Capim and others). "
        "Human pathogenicity is highly uneven: a handful of species cause "
        "well-defined disease (Oropouche fever, La Crosse encephalitis), many are "
        "known only from serosurveys, and some are purely veterinary teratogens "
        "(Akabane, Schmallenberg). Because serogroup antibodies cross-react, "
        "species-level attribution usually requires sequencing or neutralisation."
    ),
    "Flaviviridae": (
        "Positive-sense, non-segmented RNA viruses. The genus Orthoflavivirus "
        "divides ecologically into mosquito-borne, tick-borne and no-known-vector "
        "clades, and antigenically into serocomplexes. Cross-reactive antibody is "
        "the central diagnostic problem of the family, and the mechanism behind "
        "antibody-dependent enhancement in dengue."
    ),
    "Togaviridae": (
        "Contains the single genus Alphavirus, split into New World encephalitic "
        "viruses (EEE, WEE, VEE complexes) and Old World arthritogenic viruses "
        "(chikungunya, Ross River, o'nyong-nyong, Sindbis, Mayaro). The clinical "
        "division between encephalitis and polyarthritis maps closely onto that "
        "phylogeny."
    ),
    "Hantaviridae": (
        "Rodent-, shrew-, mole- and bat-borne bunyavirals. Unlike most "
        "bunyavirals they are not arthropod-borne: humans are infected by "
        "inhaling aerosolised rodent excreta. Each virus is tied to one reservoir "
        "species, so the geography of human disease follows small-mammal "
        "distributions. Old World viruses cause HFRS, New World viruses cause "
        "hantavirus cardiopulmonary syndrome."
    ),
    "Arenaviridae": (
        "Bi-segmented ambisense RNA viruses. Mammarenaviruses are rodent-borne, "
        "split into Old World (Lassa, LCMV) and New World clades A–C; clade B "
        "contains the South American haemorrhagic fever viruses (Junín, Machupo, "
        "Guanarito, Sabiá, Chapare). Reservoir specificity again dictates the "
        "geography of human disease."
    ),
    "Nairoviridae": (
        "Tick-borne bunyavirals with unusually large L segments. The genus "
        "Orthonairovirus contains Crimean-Congo haemorrhagic fever virus — the "
        "most widely distributed tick-borne human pathogen — alongside many "
        "serogroups known only from ticks and seabird colonies."
    ),
    "Phenuiviridae": (
        "Sandfly-, mosquito- and tick-borne bunyavirals. Includes Rift Valley "
        "fever virus (Phlebovirus), the sandfly fever/Toscana viruses, and the "
        "tick-borne bandaviruses SFTSV and Heartland virus, which emerged as "
        "serious human pathogens only after 2009."
    ),
    "Filoviridae": (
        "Filamentous negative-sense RNA viruses with bat reservoirs, causing "
        "haemorrhagic fever with high case fatality and amplification through "
        "healthcare and funeral practices. Handling requires maximum containment."
    ),
    "Rhabdoviridae": (
        "Bullet-shaped negative-sense RNA viruses. The genus Lyssavirus contains "
        "rabies virus and its relatives, split into phylogroups that determine "
        "whether standard rabies vaccine cross-protects — phylogroup II "
        "(Mokola, Lagos bat, Shimoni) is poorly covered."
    ),
    "Coronaviridae": (
        "Large positive-sense RNA viruses with a 5'-capped, polyadenylated "
        "genome and prominent spike glycoprotein. Seven species infect humans: "
        "four seasonal (229E, NL63, OC43, HKU1) and three of high consequence "
        "(SARS-CoV, MERS-CoV, SARS-CoV-2). Bats are the ancestral reservoir for "
        "alpha- and betacoronaviruses."
    ),
    "Paramyxoviridae": (
        "Non-segmented negative-sense RNA viruses including measles, mumps, the "
        "parainfluenza viruses, and the bat-borne henipaviruses Nipah and Hendra "
        "— the latter among the most lethal viruses known to infect humans."
    ),
    "Poxviridae": (
        "Large double-stranded DNA viruses that replicate in the cytoplasm. "
        "Contains the only eradicated human pathogen (variola virus) and the "
        "re-emerging zoonosis mpox."
    ),
    "Retroviridae": (
        "Reverse-transcribing RNA viruses that integrate into host DNA. Human "
        "pathogens are HIV-1 and HIV-2 (Lentivirus) and HTLV-1/2 "
        "(Deltaretrovirus), the latter causing adult T-cell leukaemia and HTLV-1 "
        "associated myelopathy."
    ),
    "Orthomyxoviridae": (
        "Segmented negative-sense RNA viruses. Segment reassortment produces "
        "antigenic shift and pandemics. Also contains Thogotovirus — tick-borne "
        "orthomyxoviruses including Bourbon virus, a recognised cause of fatal "
        "human illness in the United States."
    ),
    "Sedoreoviridae": (
        "Double-stranded RNA viruses with multiple segments, including Rotavirus "
        "(a leading cause of childhood gastroenteritis, now vaccine-preventable) "
        "and Orbivirus (bluetongue virus and the human-pathogenic Orungo and "
        "Lebombo viruses)."
    ),
    "Picornaviridae": (
        "Small non-enveloped positive-sense RNA viruses. Enterovirus alone "
        "accounts for polioviruses, coxsackieviruses, echoviruses, EV-A71, EV-D68 "
        "and the rhinoviruses — collectively the commonest human viral "
        "infections."
    ),
}


def get(species):
    return P.get(species)


def taxon_note(name):
    return TAXON_NOTES.get(name)


TIERS = {
    "established": {
        "label": "Established human pathogen",
        "rank": 0,
        "note": "Virus isolated or amplified from symptomatic humans with an accepted causal link to a defined syndrome.",
    },
    "probable": {
        "label": "Probable human pathogen",
        "rank": 1,
        "note": "Human infection confirmed by isolation, RT-PCR or seroconversion alongside compatible illness; causation not fully settled.",
    },
    "possible": {
        "label": "Possible / under investigation",
        "rank": 2,
        "note": "Serological evidence of human exposure, or isolated case reports; clinical significance unresolved.",
    },
    "animal-only": {
        "label": "Animal pathogen, no human disease",
        "rank": 3,
        "note": "Veterinary importance with no credible evidence of human disease despite exposure.",
    },
    "no-evidence": {
        "label": "No human evidence",
        "rank": 4,
        "note": "No reported human infection, and a host range that does not "
                "include vertebrates. This is a claim about the evidence, not "
                "an absence of it.",
    },
    # The weakest tier is the honest default. Before this existed every
    # unprofiled species was labelled "no human evidence", which asserted a
    # negative finding for 17,000 species nobody had looked at -- including
    # measles and hepatitis B.
    "unassessed": {
        "label": "Not assessed",
        "rank": 5,
        "note": "No assessment has been made here. Absence of a profile is "
                "not evidence against human infection.",
    },
}
