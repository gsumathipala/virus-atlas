"""Containment level, risk group and select-agent status.

Why this is here
----------------
Anyone who works with these viruses needs to know what handling them costs
before they plan anything, and a learner should see that the containment tier
is a consequence of transmissibility, severity and whether a countermeasure
exists — not an arbitrary label. Lassa and LCMV are both arenaviruses from
rodent reservoirs; one is BSL-4 and the other BSL-2, and the reason is
mortality plus person-to-person transmission.

Important caveats, stated here so the interface can repeat them
--------------------------------------------------------------
*   Containment assignment is **jurisdictional**. The levels below follow US
    CDC/NIH and WHO guidance, which are broadly aligned but not identical, and
    several national lists differ — Australia, Canada, the EU and the UK each
    publish their own. This is orientation, not a substitute for a local risk
    assessment or an institutional biosafety committee.
*   The level depends on **what you are doing**, not only on the agent.
    Clinical diagnostic work on an intact sample, cell-culture propagation and
    animal challenge can sit at different levels for the same virus; aerosol-
    generating procedures and high-concentration work push it up.
*   "Select agent" is a United States regulatory category (HHS/USDA) carrying
    registration, personnel-vetting and reporting duties. Other countries have
    analogous but differently-scoped lists.
*   Vaccination status changes practice: vaccinia work is BSL-2 but requires an
    offer of smallpox vaccination, and poliovirus work is governed by the WHO
    global containment framework (GAPIII/GAPIV) rather than BSL alone.

Fields
------
  bsl             containment level for routine propagation
  bsl_note        what moves it up or down
  risk_group      WHO Laboratory Biosafety Manual risk group (1-4)
  select_agent    US HHS/USDA status, or None
  vaccine_offer   vaccination offered or required for laboratory workers
"""

LEVELS = {
    1: {"label": "BSL-1", "note": "Agents not known to cause disease in "
                                  "healthy adults. Open bench, standard "
                                  "microbiological practice."},
    2: {"label": "BSL-2", "note": "Moderate hazard. Biological safety cabinet "
                                  "for aerosol-generating steps, restricted "
                                  "access, sharps precautions."},
    3: {"label": "BSL-3", "note": "Serious or lethal disease by inhalation. "
                                  "Directional airflow into the room, HEPA "
                                  "exhaust, respiratory protection, all work "
                                  "in a cabinet."},
    4: {"label": "BSL-4", "note": "Life-threatening disease with no reliable "
                                  "vaccine or treatment. Positive-pressure "
                                  "suit or Class III cabinet line, dedicated "
                                  "building services. A few dozen operational "
                                  "laboratories worldwide."},
}

RISK_GROUPS = {
    1: "Risk Group 1 — unlikely to cause human or animal disease",
    2: "Risk Group 2 — can cause human disease; unlikely to spread; effective "
       "treatment and prevention usually available",
    3: "Risk Group 3 — serious human disease; may spread; treatment or "
       "prevention usually available",
    4: "Risk Group 4 — serious human disease; readily transmissible; no "
       "effective treatment or prevention",
}


def _b(species, **kw):
    BIOSAFETY[species] = kw


BIOSAFETY = {}

# --- BSL-4 ---------------------------------------------------------------
for sp, label in [
    ("Orthoebolavirus zairense", "Ebola virus"),
    ("Orthoebolavirus sudanense", "Sudan virus"),
    ("Orthoebolavirus bundibugyoense", "Bundibugyo virus"),
    ("Orthoebolavirus taiense", "Taï Forest virus"),
    ("Orthomarburgvirus marburgense", "Marburg and Ravn viruses"),
    ("Mammarenavirus lassaense", "Lassa virus"),
    ("Mammarenavirus juninense", "Junín virus"),
    ("Mammarenavirus machupoense", "Machupo virus"),
    ("Mammarenavirus guanaritoense", "Guanarito virus"),
    ("Mammarenavirus brazilense", "Sabiá virus"),
    ("Mammarenavirus chapareense", "Chapare virus"),
    ("Mammarenavirus lujoense", "Lujo virus"),
    ("Henipavirus nipahense", "Nipah virus"),
    ("Henipavirus hendraense", "Hendra virus"),
    ("Orthonairovirus haemorrhagiae", "Crimean-Congo haemorrhagic fever virus"),
    ("Orthoflavivirus omskense", "Omsk haemorrhagic fever virus"),
    ("Orthoflavivirus kyasanurense", "Kyasanur Forest disease virus"),
]:
    _b(sp, bsl=4, risk_group=4, select_agent="HHS select agent",
       bsl_note=f"{label}: high case fatality with no licensed treatment for "
                "most, and documented person-to-person or nosocomial "
                "transmission. Diagnostic PCR on inactivated material is "
                "routinely done at lower containment.")

_b("Orthopoxvirus variola", bsl=4, risk_group=4,
   select_agent="HHS select agent — possession restricted by WHO decision",
   vaccine_offer="Smallpox vaccination required",
   bsl_note="Variola virus is held in only two WHO-authorised repositories "
            "(CDC Atlanta and VECTOR, Koltsovo). Possession anywhere else is "
            "prohibited, so this is a containment level almost nobody can "
            "lawfully work at.")

_b("Orthoebolavirus restonense", bsl=4, risk_group=4,
   select_agent="HHS select agent",
   bsl_note="Reston virus causes no human disease, but is handled as a "
            "filovirus at BSL-4 because it is indistinguishable from the "
            "pathogenic ebolaviruses in practice and lethal in macaques.")

_b("Cuevavirus lloviuense", bsl=4, risk_group=4, select_agent=None,
   bsl_note="No human infection known; handled at filovirus containment on "
            "precautionary grounds.")

# --- BSL-3 ---------------------------------------------------------------
_b("Betacoronavirus pandemicum", bsl=3, risk_group=3, select_agent=None,
   bsl_note="SARS-CoV-2 propagation is BSL-3. SARS-CoV itself is a select "
            "agent in the US. Clinical diagnostic work on specimens, and "
            "inactivated or pseudotyped systems, are BSL-2.")
_b("Betacoronavirus cameli", bsl=3, risk_group=3, select_agent=None,
   bsl_note="MERS-CoV: high case fatality and documented nosocomial "
            "transmission, with no licensed vaccine or antiviral.")
_b("Alphainfluenzavirus influenzae", bsl=2, risk_group=2, select_agent=None,
   vaccine_offer="Seasonal influenza vaccination offered",
   bsl_note="Seasonal influenza A is BSL-2. Highly pathogenic avian strains "
            "including H5N1 and H7N9 require BSL-3 with enhancements, and "
            "reconstructed 1918 virus and some transmissibility-enhanced "
            "constructs are select agents subject to additional oversight.")
_b("Phlebovirus riftense", bsl=3, risk_group=3,
   select_agent="HHS/USDA overlap select agent",
   vaccine_offer="Investigational vaccine offered at some institutions",
   bsl_note="Rift Valley fever virus is highly infectious by aerosol in the "
            "laboratory and has caused many laboratory-acquired infections.")
_b("Bandavirus dabieense", bsl=3, risk_group=3, select_agent=None,
   bsl_note="SFTS virus: case fatality up to ~10-30% in reported series, with "
            "nosocomial transmission through blood contact.")
_b("Lyssavirus rabies", bsl=2, risk_group=3,
   vaccine_offer="Pre-exposure rabies vaccination required, with titre "
                 "monitoring",
   select_agent=None,
   bsl_note="Rabies virus is handled at BSL-2 for diagnostic work by "
            "immunised staff, and BSL-3 for high-concentration propagation or "
            "aerosol-generating procedures. Containment practice here depends "
            "far more on vaccination than on the room.")
_b("Lyssavirus australis", bsl=3, risk_group=3,
   vaccine_offer="Rabies vaccination required",
   select_agent=None,
   bsl_note="Australian bat lyssavirus: rabies vaccine is cross-protective, "
            "which is why containment is survivable in practice.")
_b("Lyssavirus mokola", bsl=3, risk_group=3,
   vaccine_offer="Rabies vaccination offered but NOT reliably protective",
   select_agent=None,
   bsl_note="Mokola virus is poorly neutralised by rabies vaccine-induced "
            "antibody, so immunisation does not substitute for containment — "
            "the opposite of the situation with classical rabies.")
_b("Lyssavirus caucasicus", bsl=3, risk_group=3,
   vaccine_offer="Rabies vaccination offered but of uncertain benefit",
   select_agent=None,
   bsl_note="West Caucasian bat virus escapes rabies vaccine neutralisation, "
            "which makes any exposure consequential despite no human case.")
_b("Orthohantavirus sinnombreense", bsl=3, risk_group=3, select_agent=None,
   bsl_note="Hantavirus cardiopulmonary syndrome agents are BSL-3; rodent "
            "work with infected animals is ABSL-4 in some jurisdictions "
            "because of aerosolised excreta.")
_b("Orthohantavirus hantanense", bsl=3, risk_group=3, select_agent=None,
   bsl_note="HFRS agents: BSL-3 for propagation, with ABSL-3 or higher for "
            "infected rodents.")
_b("Orthoflavivirus japonicum", bsl=3, risk_group=3,
   vaccine_offer="Japanese encephalitis vaccination offered",
   select_agent=None,
   bsl_note="Neuroinvasive flavivirus; vaccine availability is why this is "
            "BSL-3 rather than higher.")
_b("Orthoflavivirus nilense", bsl=3, risk_group=3,
   select_agent=None,
   bsl_note="West Nile virus: BSL-3 for propagation, BSL-2 for serology and "
            "molecular diagnostics.")
_b("Orthoflavivirus zilberi", bsl=3, risk_group=3,
   vaccine_offer="Tick-borne encephalitis vaccination required",
   select_agent="HHS select agent (Far Eastern subtype) in the United States",
   bsl_note="The clearest example of jurisdiction mattering: the Far Eastern "
            "and Siberian subtypes are BSL-3 in Europe, where vaccination is "
            "expected and the virus is endemic, but are HHS select agents "
            "handled at BSL-4 in the United States. Neither level is wrong; "
            "they answer to different regulators.")

_b("Orthoflavivirus neudoerflense", bsl=3, risk_group=3,
   vaccine_offer="Tick-borne encephalitis vaccination required",
   select_agent=None,
   bsl_note="European subtype TBE virus: BSL-3, and not a select agent, "
            "unlike the Far Eastern subtype. Vaccination is effective and "
            "expected for anyone working with it.")
_b("Orthoflavivirus flavi", bsl=3, risk_group=3,
   vaccine_offer="Yellow fever vaccination required",
   select_agent=None,
   bsl_note="Wild-type yellow fever virus is BSL-3. The 17D vaccine strain is "
            "BSL-2, which is a clean illustration of attenuation changing "
            "containment.")
_b("Alphavirus venezuelan", bsl=3, risk_group=3,
   select_agent="HHS/USDA overlap select agent (epizootic subtypes IAB, IC)",
   bsl_note="VEE virus is exceptionally infectious by aerosol and has caused "
            "many laboratory infections; the enzootic subtypes are excluded "
            "from select-agent status.")
_b("Alphavirus eastern", bsl=3, risk_group=3,
   select_agent="HHS/USDA overlap select agent (North American lineage)",
   bsl_note="Eastern equine encephalitis virus: high case fatality and "
            "aerosol infectivity.")
_b("Alphavirus western", bsl=3, risk_group=3, select_agent=None,
   bsl_note="Western equine encephalitis virus.")
_b("Orthopoxvirus monkeypox", bsl=3, risk_group=3,
   select_agent="HHS select agent",
   vaccine_offer="Smallpox/mpox vaccination (MVA-BN) offered",
   bsl_note="Mpox virus propagation is BSL-3; clinical diagnostic PCR is "
            "BSL-2. Clade I is the select agent of concern.")
_b("Mammarenavirus choriomeningitidis", bsl=2, risk_group=2, select_agent=None,
   bsl_note="BSL-2 for diagnostic and routine work, escalating to BSL-3 for "
            "high-concentration propagation and to ABSL-3 for infected "
            "rodents, where aerosolised excreta is the hazard. Severe "
            "outcomes are concentrated in congenital infection and in "
            "transplant transmission, which is why containment sits well "
            "below the haemorrhagic-fever arenaviruses despite the shared "
            "reservoir biology.")
_b("Orthonairovirus kasokeroense", bsl=3, risk_group=3, select_agent=None,
   bsl_note="Kasokero virus: laboratory-acquired febrile illness documented.")
_b("Bandavirus heartlandense", bsl=3, risk_group=3, select_agent=None,
   bsl_note="Heartland virus.")
_b("Thogotovirus bourbonense", bsl=3, risk_group=3, select_agent=None,
   bsl_note="Bourbon virus: fatal human cases, no countermeasure.")
_b("Vesiculovirus chandipura", bsl=2, risk_group=2, select_agent=None,
   bsl_note="Handled as a vesiculovirus at BSL-2, as VSV Indiana and New "
            "Jersey are. Some institutions require BSL-3 on the strength of "
            "the rapidly fatal paediatric encephalitis seen in Indian "
            "outbreaks; that is a local risk assessment rather than a "
            "published level, and this is one to check with your biosafety "
            "committee rather than take from here.")
_b("Simplexvirus macacinealpha1", bsl=3, risk_group=4, select_agent=None,
   vaccine_offer="No vaccine; post-exposure valaciclovir prophylaxis protocol",
   bsl_note="BSL-2 for clinical specimens, BSL-3 for virus propagation, with "
            "BSL-4 practices for high-concentration or large-volume work. The "
            "risk group is 4 because untreated human infection is usually "
            "fatal, and the gap between that and the containment level is "
            "closed by exposure protocols: macaque colonies are managed under "
            "dedicated procedures and any bite, scratch or mucosal splash "
            "triggers immediate first aid and antiviral prophylaxis.")

# --- BSL-2 ---------------------------------------------------------------
for sp, note in [
    ("Orthoflavivirus denguei", "Dengue virus: BSL-2 with enhanced sharps "
     "precautions, since needlestick transmission is the realistic hazard."),
    ("Orthoflavivirus zikaense", "Zika virus: BSL-2, with reproductive risk "
     "assessment for staff who are or may become pregnant."),
    ("Alphavirus chikungunya", "Chikungunya virus."),
    ("Morbillivirus hominis", "Measles virus; vaccination expected."),
    ("Rubivirus rubellae", "Rubella virus; vaccination expected, with "
     "specific attention to pregnancy."),
    ("Orthopneumovirus hominis", "Human respiratory syncytial virus."),
    ("Metapneumovirus hominis", "Human metapneumovirus."),
    ("Norovirus norwalkense", "Norovirus — difficult to culture, and the "
     "practical hazard is faecal-oral spread within the laboratory."),
    ("Rotavirus alphagastroenteritidis", "Rotavirus A."),
    ("Hepatovirus ahepa", "Hepatitis A virus; vaccination expected."),
    ("Paslahepevirus balayani", "Hepatitis E virus."),
    ("Orthohepadnavirus hominoidei", "Hepatitis B virus; vaccination required "
     "for anyone handling human blood."),
    ("Lentivirus humimdef1", "HIV-1: BSL-2 with BSL-3 practices for "
     "concentrated virus; the hazard is percutaneous, not airborne."),
    ("Lentivirus humimdef2", "HIV-2, as for HIV-1."),
    ("Simplexvirus humanalpha1", "Herpes simplex virus 1."),
    ("Varicellovirus humanalpha3", "Varicella-zoster virus; vaccination or "
     "immunity documentation expected."),
    ("Cytomegalovirus humanbeta5", "Human cytomegalovirus; pregnancy risk "
     "assessment."),
    ("Lymphocryptovirus humangamma4", "Epstein-Barr virus — transforming, so "
     "immortalised-line work carries its own controls."),
    ("Alphapapillomavirus 9", "HPV-16; pseudovirion systems are widely used "
     "because the authentic virus is hard to propagate."),
    ("Enterovirus betacoxsackie", "Coxsackie B viruses."),
    ("Enterovirus alpharhino", "Rhinovirus A."),
    ("Betainfluenzavirus influenzae", "Influenza B virus."),
    ("Molluscipoxvirus molluscum", "Molluscum contagiosum virus."),
    ("Parapoxvirus orf", "Orf virus — occupational lesions in handlers."),
]:
    _b(sp, bsl=2, risk_group=2, select_agent=None, bsl_note=note)

_b("Orthopoxvirus vaccinia", bsl=2, risk_group=2, select_agent=None,
   vaccine_offer="Smallpox vaccination offered and recommended",
   bsl_note="Vaccinia virus is BSL-2, but laboratory-acquired infections are "
            "regularly reported in unvaccinated staff, including from "
            "recombinant vectors. Vaccination is the main control.")
_b("Enterovirus coxsackiepol", bsl=2, risk_group=2, select_agent=None,
   vaccine_offer="Poliovirus vaccination required",
   bsl_note="Poliovirus is governed by the WHO global action plan for "
            "containment (GAPIII/GAPIV) rather than by BSL alone: wild and "
            "Sabin-derived material is being eliminated from laboratories "
            "worldwide, and holding it requires designation as a "
            "poliovirus-essential facility.")

# Family- and genus-level fallbacks, used only when the species is unlisted.
GROUP_DEFAULTS = {
    "Filoviridae": dict(bsl=4, risk_group=4,
                        bsl_note="Filoviruses are handled at BSL-4 as a class."),
    "Arenaviridae": dict(bsl=3, risk_group=3,
                         bsl_note="Arenaviruses are BSL-3 by default; the "
                                  "haemorrhagic-fever species are BSL-4."),
    "Hantaviridae": dict(bsl=3, risk_group=3,
                         bsl_note="Hantaviruses are BSL-3, with higher "
                                  "containment for infected rodents."),
    "Nairoviridae": dict(bsl=3, risk_group=3,
                         bsl_note="Nairoviruses are BSL-3 by default; CCHF "
                                  "virus is BSL-4."),
    "Peribunyaviridae": dict(bsl=2, risk_group=2,
                             bsl_note="Most orthobunyaviruses are BSL-2; "
                                      "neuroinvasive species are BSL-3."),
    "Orthoherpesviridae": dict(bsl=2, risk_group=2,
                               bsl_note="Human herpesviruses are BSL-2; "
                                        "B virus is the exception."),
    "Picornaviridae": dict(bsl=2, risk_group=2,
                           bsl_note="BSL-2; poliovirus is additionally under "
                                    "WHO containment."),
    "Papillomaviridae": dict(bsl=2, risk_group=2, bsl_note="BSL-2."),
    "Caliciviridae": dict(bsl=2, risk_group=2, bsl_note="BSL-2."),
    "Adenoviridae": dict(bsl=2, risk_group=2, bsl_note="BSL-2."),
    "Flaviviridae": dict(bsl=2, risk_group=2,
                         bsl_note="BSL-2 for most; neuroinvasive and "
                                  "haemorrhagic species are BSL-3 or BSL-4."),
    "Togaviridae": dict(bsl=2, risk_group=2,
                        bsl_note="BSL-2 for arthritogenic alphaviruses; the "
                                 "encephalitic ones are BSL-3."),
}

# Host groups for which no human containment question arises.
NON_HUMAN_HOSTS = ("bacteria", "archaea", "plants", "fungi", "algae",
                   "protists", "invertebrates")


def get(species, family=None, host=None):
    """Containment record for a species, with provenance of the assignment."""
    hit = BIOSAFETY.get(species)
    if hit:
        return {**hit, "basis": "species", **_expand(hit)}
    low = (host or "").lower()
    if low and not any(k in low for k in ("vertebrates", "human")) \
            and any(k in low for k in NON_HUMAN_HOSTS):
        rec = dict(bsl=1, risk_group=1, select_agent=None,
                   bsl_note="No vertebrate host recorded by ICTV, so this is "
                            "handled as a Risk Group 1 agent; containment is "
                            "driven by the host organism, not the virus.")
        return {**rec, "basis": "host-range", **_expand(rec)}
    grp = GROUP_DEFAULTS.get(family)
    if grp:
        rec = {"select_agent": None, **grp}
        return {**rec, "basis": "family",
                "family": family, **_expand(rec)}
    return None


def _expand(rec):
    out = {}
    lvl = LEVELS.get(rec.get("bsl"))
    if lvl:
        out["bsl_label"] = lvl["label"]
        out["bsl_practice"] = lvl["note"]
    rg = RISK_GROUPS.get(rec.get("risk_group"))
    if rg:
        out["risk_group_label"] = rg
    return out


def covered():
    return sorted(BIOSAFETY)
