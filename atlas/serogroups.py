"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Serogroup / serocomplex / antigenic-clade assignments.

ICTV taxonomy stops at species. For arboviruses the classical literature groups
species into *serogroups* (cross-neutralisation / complement-fixation groups),
which is how the clinical and field literature actually refers to them -- e.g.
Oya virus is "an orthobunyavirus of the Simbu serogroup".

Keys are the species epithet as it appears in the ICTV binomial
("Orthobunyavirus catqueense" -> "catqueense"), which is unique within a genus.
Values under each genus: serogroup name -> list of species epithets.
`_clades` optionally nests a finer antigenic clade inside a serogroup, keyed by
serogroup name -> clade name -> epithets.
"""

SEROGROUPS = {
    "Orthobunyavirus": {
        "Simbu serogroup": [
            "simbuense", "akabaneense", "ainoense", "catqueense", "manzanillaense",
            "ingwavumaense", "thimiriense", "sangoense", "saboense", "shuniense",
            "peachesterense", "schmallenbergense", "oropoucheense", "jatobalense",
            "utingaense", "oyoense", "buttonwillowense", "mermetense",
            "faceyense", "leanyerense", "balagoduense", "indianense",
        ],
        "California serogroup": [
            "encephalitidis", "lacrosseense", "jamestownense", "khatangaense",
            "tahynaense", "melajoense", "keystoneense", "angeloense",
            "achiotei", "lumboense", "guaroaense", "infirmati",
        ],
        "Bunyamwera serogroup": [
            "bunyamweraense", "bataiense", "cacheense", "maguariense",
            "northwayense", "iacoense", "kernense", "potosiense", "tensawense",
            "shokweense", "biraoense", "ileshaense", "anhembiense",
            "macauaense", "insulae", "ebiense", "brazoriaense", "sororocaense",
            "shermanense", "lichuanense", "bozoense", "bobayaense",
        ],
        "Group C": [
            "caraparuense", "apeuense", "maritubaense", "oribocaense",
            "madridense", "nepuyoi", "gumbolimboense", "bruconhaense",
            "porteiraense",
        ],
        "Capim serogroup": [
            "capimense", "bushbushense", "benficaense", "guajaraense",
            "acaraense", "belemense", "juandiazense", "enseadaense",
        ],
        "Guamá serogroup": [
            "guamaense", "catuense", "ananindeuaense", "mirimense",
            "navioense", "timboteuaense", "bertiogaense", "guaratubaense",
            "mahoganyense", "lukuniense",
        ],
        "Patois serogroup": [
            "patoisense", "squalofluvii", "abrasense", "barritaense",
            "sanjuanense", "bellavistaense",
        ],
        "Anopheles A serogroup": [
            "horizonteense", "tacaiumaense", "parkeri", "sussexense",
        ],
        "Anopheles B serogroup": ["cuchillaense", "boraceiaense"],
        "Bwamba serogroup": ["bwambaense"],
        "Tete serogroup": ["teteense", "batamaense", "matruhense"],
        "Turlock serogroup": ["turlockense", "umbreense", "mpokoense", "ledniceense"],
        "Wyeomyia serogroup": ["wyeomyiae"],
        "Gamboa serogroup": ["gamboaense", "pacoraense"],
        "Koongol serogroup": ["koongoli"],
        "Mapputta serogroup": [
            "mitchellense", "buffaloense", "ganganense", "maprikense",
            "termeilense", "yacaabaense", "belmontense", "kowanyamaense",
        ],
        "Nyando serogroup": ["nyandoense"],
        "Olifantsvlei serogroup": ["olifantsvleiense", "botambiense", "okolaense"],
        "Minatitlán serogroup": ["minatitlanense"],
        "Bakau serogroup": ["bakauense", "ketapangense", "telokense"],
        "Tataguine serogroup": ["tataguineense"],
        "Kaeng Khoi serogroup": ["kaengkhoiense"],
        "Witwatersrand serogroup": ["witwatersrandense", "wolkbergense", "baakalense"],
        "Thimiri / minor & ungrouped": [
            "anadyrense", "sedlecense", "heptayabaense", "trinitiense",
            "taniyamense", "tangaense", "nesszionaense", "taiense",
        ],
    },

    "Orthoflavivirus": {
        "Mosquito-borne: Japanese encephalitis serocomplex": [
            "japonicum", "nilense", "louisense", "murrayense", "usutuense",
            "koutangoense", "cacipacoreense", "israelense", "yaoundeense",
        ],
        "Mosquito-borne: dengue serocomplex": ["denguei"],
        "Mosquito-borne: yellow fever group": [
            "flavi", "sepikense", "wesselsbronense", "edgehillense",
            "banziense", "boubouiense", "ugandaense", "jugraense",
            "saboyaense", "kedougouense",
        ],
        "Mosquito-borne: Spondweni / Zika group": ["zikaense"],
        "Mosquito-borne: Ntaya serocomplex": [
            "ntayaense", "bagazaense", "ilheusense", "tembusu",
        ],
        "Mosquito-borne: Kokobera group": ["kokoberaorum"],
        "Mosquito-borne: Aroa group": ["aroaense"],
        "Tick-borne: mammalian TBE serocomplex": [
            "neudoerflense", "zilberi", "mediterranense", "loupingi",
            "langatense", "powassanense", "omskense", "kyasanurense",
            "royalense", "gadgetsense", "kadamense",
        ],
        "Tick-borne: seabird group": [
            "meabanense", "saumarezense", "tyuleniyense",
        ],
        "No known vector: bat-associated": [
            "bravoense", "dakarense", "bukalasaense", "entebbeense",
            "phnompenhense", "yokoseense", "montanaense", "careyense",
            "apoiense",
        ],
        "No known vector: rodent-associated": [
            "modocense", "cowboneense", "jutiapaense", "perlitaense",
            "viejaense",
        ],
        "Classical insect-specific flaviviruses": ["iunctionis", "aphei"],
    },

    "Alphavirus": {
        "New World: Venezuelan equine encephalitis complex": [
            "venezuelan", "everglades", "mucambo", "tonate", "pixuna",
            "cabassou", "mossopedras", "negro",
        ],
        "New World: eastern equine encephalitis complex": [
            "eastern", "madariaga",
        ],
        "New World: western equine encephalitis complex": [
            "western", "highlandsj", "fortmorgan", "aura", "sindbis",
            "whataroa",
        ],
        "Old World: Semliki Forest complex": [
            "semliki", "chikungunya", "onyong", "mayaro", "rossriver",
            "getah", "bebaru", "middelburg", "ndumu", "una",
            "barmah",
        ],
        "Aquatic / divergent alphaviruses": ["salmon", "seal", "seal"],
        "Insect-specific alphaviruses": ["eilat", "caaingua", "trocara"],
    },

    "Mammarenavirus": {
        "Old World (Lassa–LCM) complex": [
            "lassaense", "choriomeningitidis", "mopeiaense", "lujoense",
            "ippyense", "praomyidis", "merinoense", "gairoense", "lunaense",
            "lunkense", "marientalense", "marientalense", "okahandjaense",
            "dhati-welelense", "kitaleense", "songeaense", "mafigaense",
            "beregaense", "ngerengerense", "solweziense", "kwanzaense",
            "bituense", "ryukyuense", "wenzhouense", "lijiangense",
            "mecsekense", "loeiense", "alashanense", "batangense",
            "abaense", "ganziense", "cameroonense", "vello",
        ],
        "New World clade A": [
            "paranaense", "piritalense", "flexalense", "allpahuayoense",
            "caliense", "caliense",
        ],
        "New World clade B (haemorrhagic fever group)": [
            "juninense", "machupoense", "guanaritoense", "brazilense",
            "chapareense", "tacaribeense", "amapariense", "cupixiense",
            "aporeense", "tietense", "xapuriense",
        ],
        "New World clade C": ["latinum", "oliverosense"],
        "New World clade A/rec (North American)": [
            "whitewaterense", "bearense", "tamiamiense",
        ],
    },

    "Orthohantavirus": {
        "Murinae-borne (Old World HFRS)": [
            "hantanense", "seoulense", "dobravaense", "sangassouense",
            "thailandense", "jejuense", "thailandense",
        ],
        "Arvicolinae-borne (nephropathia epidemica group)": [
            "puumalaense", "tulaense", "prospectense", "khabarovskense",
            "kenkemeense", "fugongense", "luxiense", "tatenalense",
            "sagercreekense", "artybashense",
        ],
        "Neotominae-borne (North American HPS)": [
            "sinnombreense", "nigrorivense", "bayoui", "montanoense",
            "carrizalense", "ozarkense",
        ],
        "Sigmodontinae-borne (South American HPS)": [
            "andesense", "mamorense", "chocloense", "delgaditoense",
            "maporalense",
        ],
        "Shrew-, mole- and bat-borne (Mobatvirus-like clades)": [
            "asamaense", "asikkalaense", "boweense", "brugesense", "dabieshanense", "lankaense", "rockportense",
            "tigrayense", "wufangense",
        ],
    },

    "Phlebovirus": {
        "Sandfly fever Naples serocomplex": [
            "napoliense", "toscanaense", "massiliaense", "puniqueense",
            "tehranense", "karimabadense", "zerdaliense", "torosense",
            "alcubeense", "medjerdaense",
        ],
        "Sandfly fever Sicilian serocomplex": [
            "siciliaense", "corfouense", "dashliense", "hediense",
            "salangaense",
        ],
        "Salehabad serocomplex": [
            "salehabadense", "adanaense", "arumowotense", "florisense",
            "gordilense", "odrenisrouense", "embossosense", "bogoriaense",
            "kiborgochense", "ntepesense", "perkerraense",
        ],
        "Rift Valley fever group": ["riftense"],
        "Punta Toro serocomplex": [
            "toroense", "buenaventuraense", "campanaense", "cocleense",
            "gloriaense", "monagritaense", "niqueense", "ticoense",
            "duraniaense", "ixcanalense", "penablancaense",
        ],
        "Candiru serocomplex": [
            "candiruense", "alenquerense", "itaitubaense", "mungubaense",
            "oriximinaense", "turunaense", "uriuranaense", "echarateense",
            "leticiaense",
        ],
        "Bujaru / Icoaraci / Frijoles groups": [
            "bujaruense", "icoaraciense", "limboense", "itaporangaense",
            "ambeense", "anhangaense", "chagresense", "claroense",
            "maldonadoense", "almendrasense", "taparaense", "saloboense",
            "urucuriense", "pantanalense", "cacaoense", "gabekense",
            "penshurtense", "riograndense",
        ],
        "Tick- and other arthropod-associated phleboviruses": [
            "alxaense", "baishanense", "manidae", "mukawaense",
            "wuxiangense",
        ],
    },

    "Orthonairovirus": {
        "Crimean-Congo haemorrhagic fever serogroup": [
            "haemorrhagiae", "parahaemorrhagiae", "hazaraense",
            "tomdiense",
        ],
        "Nairobi sheep disease serogroup": [
            "nairobiense", "dugbeense", "amblyommae", "gubboense",
        ],
        "Dera Ghazi Khan serogroup": ["khani", "abuhammadense", "zirkuense"],
        "Hughes serogroup": [
            "bushkeyense", "randallense", "soldadoense", "esteroense",
        ],
        "Qalyub serogroup": ["qalyubense", "bandiaense", "chimense"],
        "Sakhalin serogroup": [
            "sakhalinense", "avalonense", "clomorense", "macquariense",
            "australiaense",
        ],
        "Thiafora / shrew-associated serogroup": [
            "thiaforaense", "erveense", "crocidurae", "sunci", "manidae",
        ],
        "Tamdy serogroup": [
            "buranaense", "issykkulense", "keterehense", "lusakaense",
            "kasokeroense", "tachengense", "meihuashanense", "songlingense",
            "huangpiense", "wenzhouense", "yezoense", "japonicum",
            "dermacentoris", "antuense", "artashatense", "meramense",
            "sulinaense", "tunisense", "gossasense", "peruense",
            "lambarenense", "yogueense",
        ],
    },

    "Lyssavirus": {
        "Phylogroup I (rabies-related; rabies vaccine cross-protects)": [
            "rabies", "australis", "duvenhage", "hamburg", "helsinki",
            "aravan", "khujand", "irkut", "bokeloh", "gannoruwa",
            "kotalahti", "formosa", "formosa",
        ],
        "Phylogroup II (poor vaccine cross-protection)": [
            "lagos", "mokola", "shimoni",
        ],
        "Phylogroup III / divergent bat lyssaviruses": [
            "caucasicus", "ikoma", "lleida", "phala",
        ],
    },

    "Betacoronavirus": {
        "Sarbecovirus (SARS-related)": ["pandemicum"],
        "Merbecovirus (MERS-related)": [
            "cameli", "pipistrelli", "erinacei", "tylonycteridis",
            "hipposideri",
        ],
        "Embecovirus (seasonal HCoV-OC43 / HKU1 lineage)": [
            "gravedinis", "hongkongense", "muris", "muris",
            "ratti",
        ],
        "Nobecovirus / Hibecovirus (bat lineages)": [
            "rousetti", "eidoli",
        ],
    },
}

# Finer antigenic clades nested within a serogroup.
SUBCLADES = {
    "Orthobunyavirus": {
        "Simbu serogroup": {
            "Manzanilla clade": [
                "manzanillaense", "catqueense", "ingwavumaense",
                "balagoduense", "indianense", "buttonwillowense",
                "mermetense",
            ],
            "Oropouche clade": ["oropoucheense", "jatobalense", "utingaense"],
            "Akabane clade": ["akabaneense", "simbuense", "saboense", "oyoense"],
            "Sathuperi / Schmallenberg clade": [
                "schmallenbergense", "peachesterense", "faceyense",
            ],
            "Shamonda / Shuni clade": ["shuniense", "ainoense", "sangoense"],
            "Thimiri clade": ["thimiriense", "leanyerense"],
        },
    },
}


def _invert(table):
    out = {}
    for genus, groups in table.items():
        g = out.setdefault(genus, {})
        for name, epithets in groups.items():
            for e in epithets:
                g[e] = name
    return out


_BY_EPITHET = _invert(SEROGROUPS)

_SUB_BY_EPITHET = {}
for _genus, _groups in SUBCLADES.items():
    for _sg, _clades in _groups.items():
        for _clade, _eps in _clades.items():
            for _e in _eps:
                _SUB_BY_EPITHET.setdefault(_genus, {})[_e] = (_sg, _clade)


def serogroup_for(genus, species):
    """Return (serogroup, subclade) for an ICTV species binomial, or (None, None)."""
    if not genus or not species:
        return None, None
    parts = species.split()
    epithet = parts[1] if len(parts) > 1 else species
    sg = _BY_EPITHET.get(genus, {}).get(epithet)
    sub = _SUB_BY_EPITHET.get(genus, {}).get(epithet)
    return sg, (sub[1] if sub else None)


def genera_with_serogroups():
    return sorted(SEROGROUPS)
