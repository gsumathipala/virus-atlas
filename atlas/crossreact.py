"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Serological cross-reactivity within serogroups and antigenic complexes.

Why this matters more than it looks
-----------------------------------
The atlas already models serogroups, because that is how these viruses were
originally sorted and how Oya virus is placed. But a serogroup is an
*antigenic* grouping, and the direct consequence is that serology inside one is
often uninterpretable. Most of the hard problems in arbovirus diagnosis are
cross-reactivity problems:

*   A positive dengue IgM in someone who has had Zika, or vice versa, may be
    nothing more than cross-reaction — which is why plaque-reduction
    neutralisation remains the reference method and why "flavivirus-reactive"
    is sometimes the only honest answer.
*   Simbu-serogroup serology cannot distinguish Oya, Cat Que, Manzanilla,
    Oropouche and Akabane without neutralisation, so published
    seroprevalence in this group has to be read with care.
*   Rabies vaccine-induced antibody neutralises some lyssaviruses and not
    others, so cross-reactivity here is a question of whether prophylaxis
    works at all.

Each entry describes what cross-reacts with what, what it does to
interpretation, and what resolves it.
"""

COMPLEXES = {
    "Flavivirus (genus-wide)": {
        "members": ["Orthoflavivirus denguei", "Orthoflavivirus zikaense",
                    "Orthoflavivirus nilense", "Orthoflavivirus japonicum",
                    "Orthoflavivirus flavi", "Orthoflavivirus louisense",
                    "Orthoflavivirus zilberi", "Orthoflavivirus usutuense",
                    "Orthoflavivirus murrayense", "Orthoflavivirus ilheusense"],
        "genera": ["Orthoflavivirus"],
        "extent": "Extensive, genus-wide",
        "basis": "Shared epitopes on envelope protein E, especially the highly "
                 "conserved fusion loop in domain II.",
        "effect": "IgM and IgG ELISA and immunofluorescence cross-react "
                  "heavily across the whole genus. A secondary flavivirus "
                  "infection, or infection in someone vaccinated against "
                  "yellow fever or Japanese encephalitis, can produce "
                  "broadly positive serology with no reliable indication of "
                  "which virus is responsible. Dengue-Zika confusion during "
                  "the 2015-16 epidemic was the clearest example, and it "
                  "mattered because the pregnancy implications differ "
                  "completely.",
        "resolution": "Plaque-reduction neutralisation (PRNT) against a panel, "
                      "with a four-fold-or-greater titre difference; RT-PCR on "
                      "an acute specimen, which is specific but has a short "
                      "window; NS1 antigen for dengue specifically.",
        "aside": "Fusion-loop cross-reactivity is also functional, not just "
                 "diagnostic: cross-reactive non-neutralising antibody is the "
                 "proposed mechanism for antibody-dependent enhancement "
                 "between dengue serotypes, and the reason Dengvaxia is "
                 "restricted to the seropositive.",
    },
    "Simbu serogroup": {
        "members": ["Orthobunyavirus catqueense", "Orthobunyavirus oropoucheense",
                    "Orthobunyavirus akabaneense", "Orthobunyavirus manzanillaense",
                    "Orthobunyavirus shuniense", "Orthobunyavirus simbuense",
                    "Orthobunyavirus schmallenbergense",
                    "Orthobunyavirus thimiriense"],
        "serogroups": ["Simbu serogroup"],
        "extent": "Strong within the serogroup",
        "basis": "Shared nucleocapsid (N) and Gc glycoprotein epitopes; the "
                 "serogroup was defined by exactly this cross-reaction before "
                 "sequencing existed.",
        "effect": "IgG ELISA and complement fixation cannot separate members. "
                  "Reported human seroprevalence for any one Simbu virus may "
                  "reflect exposure to another — directly relevant to Oya and "
                  "Cat Que virus, where the human evidence is largely "
                  "serological, and to Oropouche, which circulates in the same "
                  "regions as other Simbu viruses.",
        "resolution": "Virus neutralisation against a panel of serogroup "
                      "members, or species-specific RT-PCR on the S segment.",
        "aside": "Reassortment compounds the problem: Simbu viruses exchange "
                 "whole segments, so a virus can carry the N antigen of one "
                 "parent and the glycoproteins of another — Iquitos and Ngari "
                 "viruses arose this way.",
    },
    "California serogroup": {
        "members": ["Orthobunyavirus lacrosseense", "Orthobunyavirus jamestownense",
                    "Orthobunyavirus encephalitidis", "Orthobunyavirus tahynaense",
                    "Orthobunyavirus keystoneense", "Orthobunyavirus khatangaense"],
        "serogroups": ["California serogroup"],
        "extent": "Strong within the serogroup",
        "basis": "Shared N protein epitopes.",
        "effect": "La Crosse, Jamestown Canyon and snowshoe hare virus "
                  "serology cross-react, so paediatric encephalitis attributed "
                  "to La Crosse on ELISA alone may be another member.",
        "resolution": "Neutralisation, or virus-specific RT-PCR.",
    },
    "Lyssavirus phylogroups": {
        "members": ["Lyssavirus rabies", "Lyssavirus australis",
                    "Lyssavirus duvenhage", "Lyssavirus hamburg",
                    "Lyssavirus helsinki", "Lyssavirus irkut",
                    "Lyssavirus mokola", "Lyssavirus caucasicus",
                    "Lyssavirus lagos", "Lyssavirus ikoma"],
        "genera": ["Lyssavirus"],
        "extent": "Partial, and split along phylogroup lines",
        "basis": "Glycoprotein G antigenic sites. Phylogroup I (rabies, "
                 "Duvenhage, European bat lyssaviruses 1 and 2, Australian bat "
                 "lyssavirus, Irkut) is cross-neutralised by rabies "
                 "vaccine-induced antibody. Phylogroup II (Mokola, Lagos bat) "
                 "and the divergent West Caucasian bat virus and Ikoma "
                 "lyssavirus are not.",
        "effect": "This is a prophylaxis question before it is a diagnostic "
                  "one. Standard rabies vaccine and immunoglobulin protect "
                  "against phylogroup I exposures, and cannot be relied on for "
                  "Mokola, Lagos bat virus or West Caucasian bat virus. "
                  "Serology using rabies antigen may also miss infection by "
                  "divergent members.",
        "resolution": "Virus-specific RT-PCR and sequencing; "
                      "lyssavirus-specific neutralisation assays.",
        "aside": "It also means the containment calculus differs: a Mokola "
                 "exposure in a vaccinated worker is not reassuring, which is "
                 "why atlas.biosafety flags the vaccine as unreliable there.",
    },
    "Alphavirus antigenic complexes": {
        "members": ["Alphavirus chikungunya", "Alphavirus onyong",
                    "Alphavirus semliki", "Alphavirus rossriver",
                    "Alphavirus mayaro", "Alphavirus barmah",
                    "Alphavirus sindbis", "Alphavirus venezuelan",
                    "Alphavirus eastern", "Alphavirus western"],
        "genera": ["Alphavirus"],
        "extent": "Strong within complexes, weak between them",
        "basis": "E1 and E2 glycoprotein epitopes. The Semliki Forest complex "
                 "(chikungunya, o'nyong-nyong, Ross River, Mayaro, Semliki "
                 "Forest, Getah) cross-reacts internally; the Western equine "
                 "encephalitis and Venezuelan equine encephalitis complexes "
                 "each do the same.",
        "effect": "Chikungunya and o'nyong-nyong serology are hard to "
                  "separate in Africa, where both circulate, and Mayaro is "
                  "readily mistaken for chikungunya in South America — the "
                  "clinical pictures are also similar, so serology is doing "
                  "real diagnostic work and cannot be trusted alone.",
        "resolution": "Neutralisation against a panel; virus-specific "
                      "RT-PCR in the short viraemic window.",
    },
    "Hantavirus serogroups": {
        "members": ["Orthohantavirus hantanense", "Orthohantavirus seoulense",
                    "Orthohantavirus dobravaense", "Orthohantavirus puumalaense",
                    "Orthohantavirus sinnombreense", "Orthohantavirus andesense"],
        "genera": ["Orthohantavirus"],
        "extent": "Moderate, grouped by reservoir lineage",
        "basis": "Nucleocapsid protein is broadly cross-reactive; the Gn/Gc "
                 "glycoproteins are more type-specific.",
        "effect": "N-based IgM/IgG assays detect hantavirus infection well but "
                  "often cannot say which species, so the clinical syndrome "
                  "and the geography carry much of the identification — "
                  "haemorrhagic fever with renal syndrome in Eurasia versus "
                  "cardiopulmonary syndrome in the Americas.",
        "resolution": "Focus-reduction neutralisation; RT-PCR and sequencing.",
    },
    "Phlebovirus sandfly fever complexes": {
        "members": ["Phlebovirus toscanaense", "Phlebovirus napoliense",
                    "Phlebovirus siciliaense", "Phlebovirus riftense",
                    "Phlebovirus adanaense", "Phlebovirus salehabadense"],
        "genera": ["Phlebovirus"],
        "extent": "Within the Naples and Sicilian complexes",
        "basis": "Shared N and glycoprotein epitopes. Toscana virus sits "
                 "within the sandfly fever Naples complex.",
        "effect": "Toscana virus serology cross-reacts with sandfly fever "
                  "Naples virus, so Mediterranean seroprevalence studies "
                  "conflate them; Sicilian virus is antigenically separate.",
        "resolution": "Neutralisation; virus-specific RT-PCR on CSF for "
                      "Toscana meningitis.",
    },
    "Arenavirus Old and New World groups": {
        "members": ["Mammarenavirus lassaense", "Mammarenavirus choriomeningitidis",
                    "Mammarenavirus juninense", "Mammarenavirus machupoense",
                    "Mammarenavirus guanaritoense", "Mammarenavirus chapareense"],
        "genera": ["Mammarenavirus"],
        "extent": "Broad on NP, narrow on GP",
        "basis": "Nucleoprotein is cross-reactive across the genus; "
                 "glycoprotein responses are largely species-specific.",
        "effect": "Immunofluorescence using one arenavirus antigen may detect "
                  "infection by another, which matters where Lassa and "
                  "non-pathogenic Mopeia or Mobala virus co-circulate in the "
                  "same Mastomys populations.",
        "resolution": "Species-specific RT-PCR; neutralisation, which is "
                      "technically difficult for arenaviruses.",
    },
    "Orthopoxvirus (genus-wide)": {
        "members": ["Orthopoxvirus variola", "Orthopoxvirus vaccinia",
                    "Orthopoxvirus monkeypox", "Orthopoxvirus cowpox",
                    "Orthopoxvirus camelpox"],
        "genera": ["Orthopoxvirus"],
        "extent": "Near-complete across the genus",
        "basis": "Extensive shared antigens across the orthopoxviruses.",
        "effect": "Serology cannot distinguish mpox from vaccinia "
                  "vaccination or cowpox, which made serosurveys during the "
                  "2022 mpox outbreak nearly uninterpretable in anyone "
                  "previously vaccinated.",
        "resolution": "Species-specific real-time PCR, which is the diagnostic "
                      "standard; sequencing for clade assignment.",
        "aside": "The same cross-reactivity is why smallpox vaccination "
                 "protects against mpox — the diagnostic nuisance and the "
                 "prophylactic benefit are the same phenomenon.",
    },
    "Human coronaviruses": {
        "members": ["Betacoronavirus pandemicum", "Betacoronavirus cameli",
                    "Betacoronavirus gravedinis", "Betacoronavirus hongkongense",
                    "Alphacoronavirus chicagoense", "Alphacoronavirus amsterdamense"],
        "genera": ["Betacoronavirus", "Alphacoronavirus"],
        "extent": "Moderate within genus, mostly on nucleocapsid",
        "basis": "N protein is conserved within each genus; the spike "
                 "receptor-binding domain is not.",
        "effect": "Pre-pandemic sera contain antibody cross-reactive with "
                  "SARS-CoV-2 N, which confounded early seroprevalence work. "
                  "Seasonal betacoronavirus exposure also primes "
                  "cross-reactive T cells.",
        "resolution": "Spike-RBD-specific assays; neutralisation against the "
                      "relevant variant.",
    },
}


def for_species(species):
    """Every complex a species belongs to."""
    return [{"name": name, **{k: v for k, v in rec.items() if k != "members"}}
            for name, rec in COMPLEXES.items() if species in rec["members"]]


def for_group(name, rank):
    """Complexes attached to a genus or serogroup node."""
    key = {"genus": "genera", "serogroup": "serogroups"}.get(rank)
    if not key:
        return []
    return [{"name": cname, **{k: v for k, v in rec.items() if k != "members"}}
            for cname, rec in COMPLEXES.items() if name in rec.get(key, [])]


def covered():
    return sorted({m for rec in COMPLEXES.values() for m in rec["members"]})
