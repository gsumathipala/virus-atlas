"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Baltimore classification, derived from the ICTV genome field.

ICTV ranks describe relatedness. Baltimore groups describe *strategy*: what the
genome is made of and therefore how it must get to mRNA. The two are
independent and a virologist uses both, so the atlas should carry both.

The mapping is mechanical from ICTV's own "Genome" column, so every species
gets a group -- unlike the curated layers, this is complete.

One ambiguity is handled explicitly: ICTV writes "ssRNA(+/-)" and
"ssRNA(-); ssRNA(+/-)" for ambisense genomes, which are conventionally placed
in Group V with the negative-sense viruses because they require a virion
polymerase. That is stated rather than silently assumed.
"""

GROUPS = {
    "I": {
        "roman": "I",
        "label": "dsDNA",
        "name": "Group I — double-stranded DNA",
        "strategy": "Transcribed directly by host (or virus-encoded) RNA "
                    "polymerase. Most replicate in the nucleus and many "
                    "encode their own DNA polymerase.",
        "examples": "Herpesviruses, poxviruses, adenoviruses, papillomaviruses, "
                    "most bacteriophages",
    },
    "II": {
        "roman": "II",
        "label": "ssDNA",
        "name": "Group II — single-stranded DNA",
        "strategy": "The strand is converted to a double-stranded "
                    "intermediate before transcription, usually by host "
                    "machinery, which restricts replication to dividing cells "
                    "for several families.",
        "examples": "Parvoviruses, anelloviruses, circoviruses, geminiviruses",
    },
    "III": {
        "roman": "III",
        "label": "dsRNA",
        "name": "Group III — double-stranded RNA",
        "strategy": "Transcribed inside an intact capsid by a virion-packaged "
                    "polymerase: the dsRNA is never exposed to the cytoplasm, "
                    "where it would trigger innate sensors.",
        "examples": "Rotaviruses, orbiviruses, reoviruses, birnaviruses",
    },
    "IV": {
        "roman": "IV",
        "label": "ssRNA(+)",
        "name": "Group IV — positive-sense single-stranded RNA",
        "strategy": "The genome IS mRNA: naked RNA entering a cell is "
                    "infectious. Translated immediately, then copied through a "
                    "negative-sense intermediate on membranous replication "
                    "organelles.",
        "examples": "Picornaviruses, flaviviruses, coronaviruses, "
                    "togaviruses, caliciviruses",
    },
    "V": {
        "roman": "V",
        "label": "ssRNA(-)",
        "name": "Group V — negative-sense single-stranded RNA",
        "strategy": "Cannot be translated. The virion must deliver its own "
                    "RNA-dependent RNA polymerase, and the genome stays coated "
                    "in nucleoprotein throughout. Segmented members can "
                    "reassort.",
        "examples": "Influenza viruses, paramyxoviruses, rhabdoviruses, "
                    "filoviruses, bunyaviruses, arenaviruses",
    },
    "VI": {
        "roman": "VI",
        "label": "ssRNA-RT",
        "name": "Group VI — positive-sense ssRNA with reverse transcriptase",
        "strategy": "Reverse-transcribed to DNA and integrated into the host "
                    "genome as a provirus, which is why infection is "
                    "lifelong and why integration site matters.",
        "examples": "HIV-1 and HIV-2, HTLV-1, other retroviruses",
    },
    "VII": {
        "roman": "VII",
        "label": "dsDNA-RT",
        "name": "Group VII — dsDNA with reverse transcriptase",
        "strategy": "A DNA genome replicated through an RNA intermediate by "
                    "reverse transcriptase. The covalently closed circular DNA "
                    "form persists in the nucleus and is why hepatitis B is so "
                    "hard to cure.",
        "examples": "Hepatitis B virus, other hepadnaviruses, caulimoviruses",
    },
}

# ICTV genome string -> (group, note). The note is shown only where the
# assignment involves a judgement rather than a direct reading.
_MAP = {
    "dsDNA": ("I", None),
    "ssDNA": ("II", None),
    "ssDNA(+)": ("II", None),
    "ssDNA(-)": ("II", None),
    "ssDNA(+/-)": ("II", "ICTV records both polarities for this taxon; "
                         "either way the replication strategy is Group II."),
    "dsRNA": ("III", None),
    "ssRNA(+)": ("IV", None),
    "ssRNA(-)": ("V", None),
    "ssRNA(+/-)": ("V", "Ambisense: genes are encoded in both orientations on "
                        "one segment. Conventionally placed in Group V, since "
                        "the virion still has to supply its own polymerase."),
    "ssRNA(-); ssRNA(+/-)": ("V", "Mixed and ambisense segments. Placed in "
                                  "Group V on the same reasoning."),
    "ssRNA-RT": ("VI", None),
    "dsDNA-RT": ("VII", None),
}


# Families whose replication strategy is settled, used to override an ICTV
# genome string that disagrees. ICTV records "ssRNA(+/-)" for one hepevirus,
# and the ambisense rule then placed a positive-sense virus in Group V.
FAMILY_GROUP = {
    "Hepeviridae": "IV", "Picornaviridae": "IV", "Flaviviridae": "IV",
    "Hepaciviridae": "IV", "Coronaviridae": "IV", "Togaviridae": "IV",
    "Caliciviridae": "IV", "Astroviridae": "IV", "Matonaviridae": "IV",
    "Retroviridae": "VI", "Hepadnaviridae": "VII",
}


def classify(genome, family=None):
    """(group_key, note) for an ICTV genome string, or (None, None).

    "ssRNA" with no polarity is left unassigned on purpose: without the sense
    there is no way to choose between Groups IV and V, and guessing would be
    worse than saying so.
    """
    if not genome:
        return (FAMILY_GROUP[family], None) if family in FAMILY_GROUP else (None, None)
    key = genome.strip()
    override = FAMILY_GROUP.get(family)
    if key in _MAP:
        group, note = _MAP[key]
        if override and group != override:
            return override, (
                f"ICTV records the genome as \u201c{key}\u201d for this "
                f"species, which would imply Group {group}. {family} "
                f"replicates by a settled Group {override} strategy, so the "
                "family assignment is used and the discrepancy noted.")
        return group, note
    if key == "ssRNA":
        return None, ("ICTV records no polarity for this taxon, so Group IV "
                      "cannot be distinguished from Group V.")
    return None, None


def describe(genome, family=None):
    """The full group record for a genome string, plus any caveat."""
    key, note = classify(genome, family)
    if key is None:
        return None if note is None else {"unassigned": True, "note": note}
    return {**GROUPS[key], "key": key, "note": note}
