"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Syndrome-led search: work backwards from the presentation.

The query this answers
----------------------
"Encephalitis, returned from Southeast Asia ten days ago, mosquito exposure —
what viruses fit?"

Everything else in the atlas starts from the virus. A clinician starts from the
patient, so this index runs the other way: syndrome first, then destination,
exposure route and time since return as filters.

How syndromes are assigned
--------------------------
By matching the curated profile prose -- `syndrome`, `headline` and the
reference note -- against the patterns below. That is a keyword heuristic over
text written for a reader, not a coded clinical ontology, and it is wrong at
the margins: it will miss a presentation the profile does not mention, and it
cannot weight how *characteristic* a feature is. A virus that mentions
jaundice in passing is scored lower than one whose profile leads with it, but
that is sequence position, not clinical judgement.

So the ranking is explicitly "what matches the words", and every result says
which phrase matched so a reader can disagree.

What it deliberately does not do
--------------------------------
It does not produce a probability, does not account for prevalence, season,
vaccination history or host factors, and contains only viruses. For a febrile
returning traveller the first job is to exclude malaria, which is a parasite
and absent from this atlas. That is stated on every surface that shows these
results.
"""

import re

# Syndromes, in the order a clinician would narrow: the dangerous and specific
# first, the non-specific last. Each pattern set is (regex, weight); a leading
# match on a strong term counts for more than a passing mention.
SYNDROMES = {
    "encephalitis": {
        "label": "Encephalitis or meningoencephalitis",
        "note": "Altered consciousness, seizures or focal deficit with fever.",
        "patterns": [
            (r"encephalit|meningoencephalit|encephalomyelit", 3),
            (r"leukoencephalopath|\bPML\b|meningopolyneurit|"
             r"subacute sclerosing", 3),
            (r"\bneuroinvasive\b|\bneurologic", 2),
            (r"aseptic meningit|\bmeningit", 2),
            (r"altered conscious|\bseizure|\bcoma\b", 2),
        ],
    },
    "haemorrhagic": {
        "label": "Viral haemorrhagic fever",
        "note": "Fever with bleeding, capillary leak or coagulopathy.",
        "patterns": [
            (r"h[ae]emorrhagic fever", 3),
            (r"ebola disease|marburg disease|lassa fever|\bHFRS\b|\bHCPS\b|"
             r"h[ae]emorrhagic fever with renal|cardiopulmonary syndrome", 3),
            (r"\bh[ae]emorrhag|\bbleeding\b|coagulopath|\bDIC\b", 2),
            (r"capillary leak|plasma leak|thrombocytopeni", 2),
        ],
    },
    "paralysis": {
        "label": "Acute flaccid paralysis or myelitis",
        "note": "Weakness of rapid onset, with or without sensory change.",
        "patterns": [
            (r"flaccid (?:paralysis|myelitis)|poliomyelit", 3),
            (r"\bpolio\b|acute flaccid", 3),
            (r"\bmyelit|\bparalys|Guillain-Barr", 2),
            (r"motor neuron", 2),
        ],
    },
    "respiratory": {
        "label": "Respiratory illness",
        "note": "Cough, coryza, bronchiolitis or pneumonia.",
        "patterns": [
            (r"pneumoni|bronchiolit|\bARDS\b|respiratory distress", 3),
            (r"\bMERS\b|\bSARS\b|\bCOVID|seasonal influenza|\binfluenza\b|"
             r"respiratory disease|papillomatosis|pneumonit", 3),
            (r"respiratory illness|respiratory infection|\bcroup\b|"
             r"laryngotracheo?bronchit", 2),
            (r"common cold|coryza|upper respiratory|\bcough\b|\bpharyngit", 1),
        ],
    },
    "gastroenteritis": {
        "label": "Gastroenteritis",
        "note": "Diarrhoea and vomiting.",
        "patterns": [
            (r"gastroenterit|\bdiarrh", 3),
            (r"\bvomiting\b|\benterit", 2),
        ],
    },
    "hepatitis": {
        "label": "Hepatitis",
        "note": "Jaundice or transaminitis.",
        "patterns": [
            (r"\bhepatit", 3),
            (r"liver disease|hepatic failure", 2),
            (r"\bjaundice\b|hepatocellular|\bcirrhosis\b|liver failure", 2),
            (r"\btransaminas|\bhepatomegal", 1),
        ],
    },
    "arthralgia": {
        "label": "Arthralgia or arthritis",
        "note": "Joint pain, often with rash; may persist for months.",
        "patterns": [
            (r"polyarthrit|arthralgi|\barthrit", 3),
            (r"joint pain|\bmyalgi.*\barthr", 2),
        ],
    },
    "rash": {
        "label": "Fever with rash or exanthem",
        "note": "Maculopapular, vesicular or petechial eruption.",
        "patterns": [
            (r"\bexanthem|maculopapular|\bvesicul|\bpustul", 3),
            (r"chickenpox|\bshingles\b|herpes zoster|\bwarts?\b|"
             r"milker'?s nodule|molluscum|\bpox\b|eczema vaccinatum|"
             r"ulcerating lesion|nodular skin|genital herpes|"
             r"anogenital|contagious pustular|papular stomatitis", 3),
            (r"\brash\b|\bskin lesion|\bpapul|\bumbilicated", 2),
        ],
    },
    "congenital": {
        "label": "Congenital or fetal infection",
        "note": "Vertical transmission with fetal loss or malformation.",
        "patterns": [
            (r"congenital|\bmicrocephal|fetal (?:loss|anomal|death)|"
             r"\bhydrops\b|\bstillbirth", 3),
            (r"vertical transmission|mother-to-(?:child|fetus)|"
             r"\bteratogen|\bmiscarriage", 2),
            (r"\bpregnan", 1),
        ],
    },
    "haemolytic-renal": {
        "label": "Renal involvement",
        "note": "Acute kidney injury or nephropathy.",
        "patterns": [
            (r"renal syndrome|nephropath|\bnephrit", 3),
            (r"\bHFRS\b|renal involvement|h[ae]emorrhagic cystitis", 3),
            (r"renal failure|kidney injury|\boliguri|\bproteinuri", 2),
        ],
    },
    "myocarditis": {
        "label": "Myocarditis or cardiac involvement",
        "note": "Chest pain, arrhythmia or heart failure.",
        "patterns": [
            (r"myocardit|pericardit|cardiomyopath", 3),
            (r"\bmyocardi|cardiac involvement", 2),
        ],
    },
    "conjunctivitis": {
        "label": "Conjunctivitis or ocular disease",
        "note": "Red eye, keratitis, retinitis or uveitis.",
        "patterns": [
            (r"conjunctivit|keratit|\bretinit|\buveit|keratoconjunctivit", 3),
            (r"\bocular\b|\bphotophobi", 1),
        ],
    },
    "lymphadenopathy": {
        "label": "Lymphadenopathy or mononucleosis",
        "note": "Node enlargement, sore throat, atypical lymphocytosis.",
        "patterns": [
            (r"mononucleosis|lymphadenopath|\blymphadenit", 3),
            (r"\bsplenomegal|atypical lymphocyt", 2),
        ],
    },
    "parotitis": {
        "label": "Parotitis or orchitis",
        "note": "Salivary gland or testicular swelling.",
        "patterns": [(r"parotit|\borchit|\boophorit", 3)],
    },
    "oncogenic": {
        "label": "Malignancy",
        "note": "Virus-associated cancer, usually after years of infection.",
        "patterns": [
            (r"\bcarcinom|\blymphom|\bsarcoma\b|\bleuk[ae]mi|"
             r"\bmalignan|\boncogen|\btumour\b|\btumor\b", 3),
            (r"cervical cancer|adenocarcinoma|\bcancers?\b|"
             r"Burkitt|nasopharyngeal|Castleman", 3),
        ],
    },
    "immunosuppression": {
        "label": "Immunosuppression or opportunistic disease",
        "note": "Disease caused by, or unmasked by, loss of immune "
                "competence, including reactivation in transplant and HIV "
                "patients.",
        "patterns": [
            (r"\bAIDS\b|immunodeficiency|immunosuppress|immunocompromis", 3),
            (r"opportunist|\bCD4\b|reactivation|transplant|"
             r"progressive vaccinia", 2),
        ],
    },
    "febrile": {
        "label": "Undifferentiated fever",
        "note": "Fever without a localising feature — the commonest "
                "presentation, and the least discriminating.",
        "patterns": [
            (r"febrile illness|undifferentiated fever|\bfever\b", 2),
            (r"\bmyalgi|\bheadache\b|\bchills\b|\bmalaise\b", 1),
        ],
    },
}

_COMPILED = {
    key: [(re.compile(rx, re.I), w) for rx, w in rec["patterns"]]
    for key, rec in SYNDROMES.items()
}


def score(text):
    """{syndrome: (score, matched_phrase)} for one block of profile prose.

    Weighted by pattern strength and by where the match falls: a feature named
    in the first sentence is more likely to be the defining presentation than
    one mentioned at the end.
    """
    if not text:
        return {}
    out = {}
    length = max(len(text), 1)
    for key, pats in _COMPILED.items():
        best, phrase = 0, None
        for rx, weight in pats:
            m = rx.search(text)
            if not m:
                continue
            # Position bonus: 1.0 at the start, decaying to 0.5 at the end.
            position = 1.0 - 0.5 * (m.start() / length)
            value = weight * position
            if value > best:
                best, phrase = value, m.group(0)
        if best:
            out[key] = (round(best, 3), phrase)
    return out


TIERS_WANTED = ("established", "probable", "possible")


def build_index(nodes):
    """species -> syndrome scores, and syndrome -> ranked species.

    Built once at startup from the curated prose.
    """
    by_species, by_syndrome = {}, {k: [] for k in SYNDROMES}
    for node in nodes.values():
        if node["rank"] != "species":
            continue
        meta = node.get("meta") or {}
        if meta.get("tier") not in TIERS_WANTED:
            continue
        prof = meta.get("profile") or {}
        # Syndrome prose first, then the headline, then the reference note.
        text = " ".join(filter(None, [
            prof.get("syndrome"), prof.get("headline"), meta.get("tier_note")]))
        hits = score(text)
        if not hits:
            continue
        entry = {
            "id": node["id"],
            "species": node["name"],
            "common": (prof.get("names") or [None])[0],
            "tier": meta.get("tier"),
            "family": meta.get("family"),
            "profiled": bool(meta.get("profiled")),
            "syndromes": {k: v[0] for k, v in hits.items()},
            "matched": {k: v[1] for k, v in hits.items()},
        }
        by_species[node["name"]] = entry
        for key, (value, phrase) in hits.items():
            by_syndrome[key].append({**entry, "score": value, "phrase": phrase})

    for key, rows in by_syndrome.items():
        rows.sort(key=lambda r: (-r["score"], not r["profiled"], r["species"]))
    return by_species, by_syndrome


def query(by_syndrome, syndrome, *, country=None, route=None, days=None,
          travel_rows=None, limit=60):
    """Rank candidates for a syndrome, narrowed by travel facts if given.

    `travel_rows` is the candidate pool from atlas.travel for the country --
    both the destination-specific viruses and the cosmopolitan ones, because a
    returning traveller with a fever can just as easily have measles or
    influenza as something imported. Each row keeps its own `scope`, so the
    answer can say which is which.
    """
    rows = by_syndrome.get(syndrome) or []
    if travel_rows is None:
        out = [dict(r) for r in rows]
    else:
        # Intersect on species, carrying the travel facts across.
        facts = {r["species"]: r for r in travel_rows}
        out = []
        for r in rows:
            t = facts.get(r["species"])
            if t is None:
                continue
            out.append({
                **r,
                "routes": t.get("routes"),
                "evidence": t.get("evidence"),
                "evidence_label": t.get("evidence_label"),
                "geo_inferred": t.get("geo_inferred"),
                "geo_region": t.get("geo_region"),
                "scope": t.get("scope"),
                "incubation": t.get("incubation"),
                "incubation_days": t.get("incubation_days"),
                "window": t.get("window"),
            })
    if route:
        out = [r for r in out if route in (r.get("routes") or [])]
    if days is not None:
        # Keep anything compatible or unknown; drop only what the window rules
        # out, and say how many were dropped.
        out = [r for r in out if r.get("window") in (None, "plausible",
                                                     "unknown", "unfiltered")]
    return out[:limit]


def syndrome_list():
    return [{"key": k, "label": v["label"], "note": v["note"]}
            for k, v in SYNDROMES.items()]
