"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Licensed vaccines, antivirals and immunoprophylaxis, per species.

What this answers
-----------------
"Is there anything we can do about it?" — which, together with transmissibility
and severity, is what determines how a virus is actually managed, and which
explains most of the containment tiers in atlas.biosafety.

It also makes the gaps visible, and the gaps are the point: there is no
licensed antiviral for dengue, chikungunya, Nipah, Zika, Rift Valley fever,
West Nile, EV-D68 or any hantavirus. Showing "none licensed" explicitly is
more useful than an empty section a reader might take for missing data.

Scope and caveats
-----------------
*   **Licensed** means approved by at least one stringent regulatory authority,
    which is not the same as available where a reader lives. Availability,
    schedules and age indications vary by country, and several entries here
    are approved in some jurisdictions only.
*   Investigational agents are marked as such and are not treatment advice.
*   This is a curated educational summary and goes out of date. It is not a
    formulary, and nothing here is clinical guidance.
*   `none` is a positive statement: nothing is licensed, as far as this
    curation goes. `unlisted` means this file has no entry at all.
"""


def _c(species, **kw):
    COUNTERMEASURES[species] = kw


COUNTERMEASURES = {}

# --- vaccine-preventable, no specific antiviral -------------------------
_c("Morbillivirus hominis",
   vaccines=["Live attenuated measles vaccine, given as MMR or MR "
             "(Edmonston-Zagreb, Schwarz, Moraten strains)"],
   antivirals=[],
   prophylaxis=["Measles immunoglobulin within 6 days of exposure for infants, "
                "pregnant women and the immunocompromised",
                "Vaccine within 72 hours of exposure"],
   note="Two doses give ~97% protection and immunity is lifelong. Vitamin A "
        "reduces mortality in children and is a WHO recommendation, but it is "
        "not an antiviral. Herd immunity needs about 95% coverage, which is "
        "why measles is the first disease to return when coverage slips.")

_c("Rubivirus rubellae",
   vaccines=["Live attenuated RA 27/3, given as MMR"],
   antivirals=[],
   prophylaxis=[],
   note="Vaccination is about preventing congenital rubella syndrome, not the "
        "mild childhood illness. The vaccine is contraindicated in pregnancy, "
        "so the strategy is to immunise before childbearing age.")

_c("Orthorubulavirus parotitidis",
   vaccines=["Live attenuated mumps vaccine (Jeryl Lynn, RIT 4385, "
             "Urabe strains), given as MMR"],
   antivirals=[],
   prophylaxis=[],
   note="Effectiveness is the weakest component of MMR, around 88% after two "
        "doses, and wanes — which is why outbreaks occur in highly vaccinated "
        "university populations and why a third dose is used in outbreak "
        "control.")

_c("Enterovirus coxsackiepol",
   vaccines=["Inactivated poliovirus vaccine (IPV, Salk)",
             "Oral poliovirus vaccine (OPV, Sabin) — bivalent and "
             "monovalent type 2",
             "Novel OPV2 (nOPV2), genetically stabilised against reversion"],
   antivirals=["Pocapavir — investigational, used for chronic excretors",
               "Pocapavir and V-073 under compassionate use only"],
   prophylaxis=[],
   note="OPV gives mucosal immunity and interrupts transmission, but reverts "
        "to cause circulating vaccine-derived poliovirus; IPV protects the "
        "individual without stopping gut replication. nOPV2 exists to keep "
        "OPV's transmission-blocking without the reversion, and is the main "
        "tool against cVDPV2 outbreaks.")

_c("Orthoflavivirus flavi",
   vaccines=["17D live attenuated yellow fever vaccine — single dose, "
             "lifelong protection"],
   antivirals=[],
   prophylaxis=[],
   note="One of the most effective vaccines ever made, from a 1937 "
        "attenuation. Rare but serious adverse events — vaccine-associated "
        "viscerotropic and neurotropic disease — concentrate in first-time "
        "recipients over 60, which shapes travel-clinic practice.")

_c("Orthoflavivirus japonicum",
   vaccines=["IXIARO / JESPECT (IC51), inactivated Vero-cell",
             "SA 14-14-2 live attenuated",
             "Live recombinant chimeric (IMOJEV)"],
   antivirals=[],
   prophylaxis=[],
   note="No antiviral exists and a third of survivors have permanent "
        "neurological sequelae, so prevention is the whole of management.")

_c("Orthoflavivirus zilberi",
   vaccines=["FSME-IMMUN / TICOVAC", "Encepur", "TBE-Moscow", "EnceVir"],
   antivirals=[], prophylaxis=[],
   note="Highly effective but needs a three-dose primary course plus boosters; "
        "no post-exposure option exists, so it has to be given before the "
        "season.")

_c("Orthoflavivirus denguei",
   vaccines=["Dengvaxia (CYD-TDV) — only for seropositive individuals",
             "Qdenga / TAK-003 — approved in the EU, UK and endemic countries"],
   antivirals=[],
   prophylaxis=[],
   note="The serostatus restriction on Dengvaxia is the clearest example of "
        "antibody-dependent enhancement driving policy: in seronegative "
        "recipients the vaccine behaved like a first infection and made a "
        "later natural infection worse. No antiviral is licensed; management "
        "is fluid balance, and NSAIDs are avoided.")

_c("Orthohepadnavirus hominoidei",
   vaccines=["Recombinant HBsAg vaccine (Engerix-B, Recombivax HB)",
             "HEPLISAV-B with CpG adjuvant",
             "PreHevbrio (3-antigen)"],
   antivirals=["Tenofovir disoproxil or alafenamide", "Entecavir",
               "Pegylated interferon alfa-2a", "Lamivudine, telbivudine, "
               "adefovir (older, higher resistance)"],
   prophylaxis=["Hepatitis B immunoglobulin plus vaccine at birth for infants "
                "of HBsAg-positive mothers"],
   note="Suppressive, not curative: nucleos(t)ide analogues control "
        "replication but do not clear the integrated or episomal cccDNA "
        "reservoir, so treatment is usually lifelong. Birth-dose vaccination "
        "is the single most effective intervention against hepatocellular "
        "carcinoma worldwide.")

_c("Hepatovirus ahepa",
   vaccines=["Inactivated hepatitis A vaccine (Havrix, VAQTA)",
             "Combined HepA/HepB (Twinrix)"],
   antivirals=[],
   prophylaxis=["Vaccine or immunoglobulin within 2 weeks of exposure"],
   note="Post-exposure vaccination works because the incubation period is "
        "long — roughly 28 days — which gives the immune response time to get "
        "ahead of the infection.")

_c("Paslahepevirus balayani",
   vaccines=["Hecolin (HEV 239) — licensed in China only"],
   antivirals=["Ribavirin, for chronic hepatitis E in the immunosuppressed "
               "(off-label)",
               "Pegylated interferon, in liver-transplant recipients"],
   prophylaxis=[],
   note="The only licensed HEV vaccine is available in one country. For "
        "travellers there is no vaccine option, so prevention is food and "
        "water hygiene — and in pregnancy, where genotype 1 mortality reaches "
        "20-25%, that matters a great deal.")

_c("Alphapapillomavirus 9",
   vaccines=["Gardasil 9 (9-valent)", "Cervarix (bivalent)",
             "Gardasil (quadrivalent)", "Cecolin, Walrinvax (bivalent)"],
   antivirals=[],
   prophylaxis=[],
   note="Prophylactic only: the L1 virus-like particles prevent establishment "
        "but do nothing about existing infection. Single-dose schedules are "
        "now WHO-recommended, and countries with early high coverage are "
        "already seeing cervical cancer incidence fall.")

_c("Orthopoxvirus variola",
   vaccines=["ACAM2000 (replication-competent)",
             "MVA-BN / JYNNEOS / IMVANEX (replication-deficient)"],
   antivirals=["Tecovirimat (TPOXX)", "Brincidofovir", "Cidofovir"],
   prophylaxis=["Vaccinia immune globulin for vaccine complications"],
   note="Eradicated in 1980; the countermeasures exist for biodefence and are "
        "what made the 2022 mpox response possible so quickly.")

_c("Orthopoxvirus monkeypox",
   vaccines=["MVA-BN (JYNNEOS / IMVANEX / IMVAMUNE)", "ACAM2000",
             "LC16m8 (Japan)"],
   antivirals=["Tecovirimat — efficacy not demonstrated in the PALM007 and "
               "STOMP trials",
               "Brincidofovir", "Cidofovir"],
   prophylaxis=["Post-exposure MVA-BN within 4 days (ideally), up to 14 days"],
   note="A cautionary case: tecovirimat was widely deployed on the strength of "
        "animal data, and the randomised trials in DRC and the US did not show "
        "a benefit in clade I or clade II disease. Vaccination remains the "
        "effective intervention.")

# --- antiviral-led -------------------------------------------------------
_c("Alphainfluenzavirus influenzae",
   vaccines=["Inactivated quadrivalent and trivalent, egg- and cell-based",
             "Recombinant HA (Flublok)", "Live attenuated intranasal "
             "(FluMist)", "High-dose and adjuvanted formulations for "
             "older adults"],
   antivirals=["Oseltamivir", "Zanamivir", "Peramivir",
               "Baloxavir marboxil (cap-dependent endonuclease inhibitor)"],
   prophylaxis=["Oseltamivir or baloxavir for post-exposure prophylaxis in "
                "high-risk contacts"],
   note="Reformulated annually because of antigenic drift, which is a "
        "consequence of the error-prone polymerase and segmented genome. "
        "Adamantanes (amantadine, rimantadine) are no longer used: essentially "
        "all circulating A viruses carry the M2 S31N resistance change.")

_c("Betacoronavirus pandemicum",
   vaccines=["mRNA (Comirnaty, Spikevax)",
             "Adenovirus-vectored (Vaxzevria, Jcovden)",
             "Protein subunit (Nuvaxovid), inactivated (CoronaVac, Covaxin)"],
   antivirals=["Nirmatrelvir/ritonavir (Paxlovid)", "Remdesivir",
               "Molnupiravir", "Ensitrelvir (Japan)"],
   prophylaxis=["Pemivibart — monoclonal pre-exposure prophylaxis for the "
                "immunocompromised"],
   note="Most therapeutic monoclonals, including casirivimab/imdevimab, "
        "sotrovimab and bebtelovimab, were withdrawn as spike evolved away "
        "from their epitopes. The small-molecule antivirals target conserved "
        "enzymes and have held up — a general lesson about where to aim.")

_c("Lentivirus humimdef1",
   vaccines=[],
   antivirals=["Integrase inhibitors: bictegravir, dolutegravir, cabotegravir",
               "NRTIs: tenofovir, emtricitabine, abacavir, lamivudine",
               "NNRTIs: doravirine, rilpivirine, efavirenz",
               "Protease inhibitors: darunavir, atazanavir",
               "Capsid inhibitor: lenacapavir",
               "Entry: maraviroc (CCR5), fostemsavir, ibalizumab"],
   prophylaxis=["Oral PrEP: tenofovir/emtricitabine",
                "Long-acting injectable PrEP: cabotegravir, lenacapavir",
                "PEP within 72 hours, 28-day course"],
   note="No vaccine after forty years of trying — the diversity of env and the "
        "integrated reservoir defeat it. But treatment is so effective that an "
        "undetectable viral load means no sexual transmission, and "
        "twice-yearly lenacapavir has shown near-complete protection as PrEP.")

_c("Orthopneumovirus hominis",
   vaccines=["Arexvy (RSVPreF3, adjuvanted) for older adults",
             "Abrysvo (RSVpreF) for older adults and in pregnancy",
             "mResvia (mRNA-1345)"],
   antivirals=["Ribavirin — rarely used, marginal benefit"],
   prophylaxis=["Nirsevimab — single-dose long-acting monoclonal for infants",
                "Palivizumab — monthly, for high-risk infants"],
   note="RSV went from having nothing to having several options in two years, "
        "once prefusion F was stabilised as an immunogen. Maternal "
        "immunisation and infant nirsevimab are alternative routes to the same "
        "protection, and the 1960s formalin-inactivated vaccine disaster — "
        "enhanced disease on natural infection — is why the field moved so "
        "carefully.")

_c("Orthoebolavirus zairense",
   vaccines=["ERVEBO (rVSV-ZEBOV-GP), single dose",
             "Zabdeno/Mvabea two-dose regimen"],
   antivirals=["Ansuvimab (Ebanga)", "REGN-EB3 (Inmazeb)"],
   prophylaxis=["Ring vaccination of contacts and contacts of contacts"],
   note="Both licensed monoclonals and ERVEBO are specific to *Zaire* "
        "ebolavirus and do not protect against Sudan, Bundibugyo or Marburg "
        "virus — which is why a Bundibugyo outbreak is a far harder problem "
        "than a Zaire one. The PALM trial that established them was run during "
        "an active outbreak.")

_c("Orthoflavivirus kyasanurense",
   vaccines=["Formalin-inactivated KFD vaccine (India)"],
   antivirals=[], prophylaxis=[],
   note="Effectiveness is limited and coverage poor; tick avoidance does most "
        "of the work.")

_c("Mammarenavirus juninense",
   vaccines=["Candid#1 live attenuated — licensed in Argentina"],
   antivirals=["Immune plasma from convalescent donors, which cuts mortality "
               "from ~15-30% to ~1% if given early",
               "Ribavirin (off-label)"],
   prophylaxis=[],
   note="A rare success: a regionally licensed vaccine plus convalescent "
        "plasma turned Argentine haemorrhagic fever from a major rural killer "
        "into a controlled disease.")

_c("Mammarenavirus lassaense",
   vaccines=[],
   antivirals=["Ribavirin — widely used, but the evidence base has been "
               "seriously questioned"],
   prophylaxis=[],
   note="The ribavirin evidence rests largely on a 1986 study whose analysis "
        "has since been challenged; current trials are reassessing it. "
        "Several vaccine candidates are in trials, none licensed.")

_c("Lyssavirus rabies",
   vaccines=["Human diploid cell vaccine (HDCV)",
             "Purified chick embryo cell (PCECV)",
             "Purified Vero cell rabies vaccine (PVRV)"],
   antivirals=[],
   prophylaxis=["Post-exposure prophylaxis: immediate wound washing, vaccine "
                "series, plus human or equine rabies immunoglobulin infiltrated "
                "into the wound for category III exposures"],
   note="Post-exposure prophylaxis is essentially 100% effective if started "
        "before symptoms, and once encephalitis begins the disease is "
        "effectively always fatal — the widest gap between prevention and "
        "treatment in medicine. The Milwaukee protocol is not a treatment.")

_c("Orthonairovirus haemorrhagiae",
   vaccines=["Inactivated mouse-brain vaccine (Bulgaria) — not internationally "
             "licensed"],
   antivirals=["Ribavirin — benefit contested, observational data only"],
   prophylaxis=[],
   note="No internationally licensed vaccine or proven antiviral, high case "
        "fatality and documented nosocomial spread: the combination is why "
        "CCHF is BSL-4 and on the WHO priority pathogen list.")

_c("Deltavirus italiense",
   vaccines=["Prevented entirely by hepatitis B vaccination"],
   antivirals=["Bulevirtide (Hepcludex) — NTCP entry inhibitor",
               "Pegylated interferon alfa (off-label)"],
   prophylaxis=[],
   note="The only virus here whose vaccine is another virus' vaccine: HDV "
        "cannot infect without HBsAg, so HBV immunisation prevents it "
        "absolutely. Bulevirtide blocks the shared NTCP receptor.")

_c("Rotavirus alphagastroenteritidis",
   vaccines=["Rotarix (monovalent human)", "RotaTeq (pentavalent "
             "human-bovine reassortant)", "Rotavac, ROTASIIL (India)"],
   antivirals=[],
   prophylaxis=[],
   note="Oral vaccines take less well in low-income settings — probably a "
        "mixture of maternal antibody, enteric microbiota and HBGA/secretor "
        "status — which is the reverse of the pattern for injected vaccines. "
        "Intussusception risk is small and outweighed by the benefit.")

_c("Varicellovirus humanalpha3",
   vaccines=["Varivax (live attenuated Oka) for varicella",
             "Shingrix (recombinant gE, adjuvanted) for zoster",
             "Zostavax (live, largely superseded)"],
   antivirals=["Aciclovir", "Valaciclovir", "Famciclovir"],
   prophylaxis=["Varicella-zoster immunoglobulin for exposed susceptible "
                "pregnant women, neonates and the immunocompromised"],
   note="The same virus needs two different vaccines: a live one to prevent "
        "primary infection in children, and a strongly adjuvanted subunit one "
        "to boost waning cellular immunity in older adults and stop "
        "reactivation.")

_c("Simplexvirus humanalpha1",
   vaccines=[],
   antivirals=["Aciclovir", "Valaciclovir", "Famciclovir",
               "Foscarnet and cidofovir for resistant disease",
               "Pritelivir (helicase-primase inhibitor) — investigational"],
   prophylaxis=["Suppressive daily antiviral therapy for frequent recurrence"],
   note="Antivirals suppress replication and shorten episodes but cannot touch "
        "latent genomes in sensory ganglia, so they do not cure or prevent "
        "future reactivation. No licensed vaccine, despite repeated attempts.")

_c("Cytomegalovirus humanbeta5",
   vaccines=[],
   antivirals=["Valganciclovir and ganciclovir", "Letermovir (terminase "
               "inhibitor, prophylaxis)", "Maribavir (for refractory "
               "disease)", "Foscarnet", "Cidofovir"],
   prophylaxis=["Letermovir prophylaxis after allogeneic stem-cell transplant",
                "CMV immunoglobulin in selected transplant settings"],
   note="A congenital CMV vaccine is a long-standing priority and none exists; "
        "the pentameric complex is the leading immunogen. Letermovir changed "
        "transplant practice by being prophylactic without the myelotoxicity "
        "of ganciclovir.")

# --- nothing licensed: stated explicitly --------------------------------
for sp, note in [

    ("Orthoflavivirus zikaense",
     "No vaccine and no antiviral. Prevention is bite avoidance, and "
     "pregnancy-specific travel advice is the main public-health tool."),
    ("Henipavirus nipahense",
     "No licensed vaccine or antiviral. m102.4, a human monoclonal, is "
     "available on compassionate grounds, and HeV-sG vaccine candidates and "
     "remdesivir have animal data. A WHO priority pathogen precisely because "
     "of this gap."),
    ("Phlebovirus riftense",
     "No human vaccine is licensed; veterinary vaccines exist and reduce "
     "human exposure by controlling livestock epizootics — a One Health "
     "intervention rather than a human one."),
    ("Orthoflavivirus nilense",
     "No human vaccine despite effective equine vaccines, and no antiviral. "
     "The commercial case for a human West Nile vaccine has never closed."),
    ("Bandavirus dabieense",
     "No licensed vaccine or antiviral. Favipiravir has been trialled in "
     "China with uncertain benefit."),
    ("Orthohantavirus sinnombreense",
     "No licensed vaccine or antiviral anywhere; Hantavax, an inactivated "
     "HFRS vaccine, is licensed in South Korea and does not cover the "
     "Americas. Management is early ECMO for cardiopulmonary syndrome."),

    ("Enterovirus deconjuncti",
     "No vaccine or antiviral for EV-D68, which is the main concern given its "
     "association with acute flaccid myelitis."),
    ("Norovirus norwalkense",
     "No licensed vaccine or antiviral; candidates are in trials. Management "
     "is rehydration, and control is hand hygiene and environmental "
     "disinfection — alcohol gel is relatively ineffective against a "
     "non-enveloped virus."),
    ("Orthomarburgvirus marburgense",
     "Nothing licensed. The Sabin and IAVI vaccine candidates were deployed "
     "under trial protocols during the Rwanda and Equatorial Guinea "
     "outbreaks; remdesivir and MBP091 have animal data only."),
    ("Orthoebolavirus sudanense",
     "No licensed vaccine or therapeutic: ERVEBO and both monoclonals are "
     "Zaire-specific. Candidate vaccines were trialled during the 2022 Uganda "
     "outbreak."),
    ("Orthoebolavirus bundibugyoense",
     "As for Sudan virus — the Zaire-specific countermeasures do not apply, "
     "which is what makes the current DRC outbreak harder than 2018-20."),
    ("Metapneumovirus hominis",
     "No licensed vaccine or antiviral, despite a burden comparable to RSV in "
     "young children and older adults."),
    ("Alphavirus venezuelan",
     "No licensed human vaccine; TC-83 and C-84 are investigational and used "
     "for laboratory workers under IND."),
    ("Alphavirus eastern",
     "No licensed human vaccine or antiviral, with case fatality around 30% "
     "and severe sequelae in most survivors."),
    ("Orthobunyavirus oropoucheense",
     "No vaccine or antiviral. With the 2024 expansion and reports of vertical "
     "transmission this is now a recognised gap."),
    ("Orthobunyavirus catqueense",
     "No vaccine or antiviral, and no reason to expect one for a virus with a "
     "single published human case."),
    ("Mammarenavirus choriomeningitidis",
     "No vaccine or licensed antiviral; ribavirin has been used off-label. "
     "Prevention is rodent control and screening of transplant donors."),
]:
    _c(sp, vaccines=[], antivirals=[], prophylaxis=[], note=note)


_c("Alphavirus chikungunya",
   vaccines=["IXCHIQ (VLA1553), live attenuated single dose",
             "Vimkunya (PXVX0317), virus-like particle"],
   antivirals=[],
   prophylaxis=[],
   note="The first chikungunya vaccines, licensed from 2023-2024 in the US, "
        "EU and UK. There is still no antiviral, and chronic arthralgia has "
        "no specific treatment. Serious adverse events in older recipients "
        "led to a restriction on IXCHIQ in some jurisdictions.")

_c("Orthohantavirus hantanense",
   vaccines=["Hantavax, inactivated — licensed in South Korea only"],
   antivirals=[],
   prophylaxis=[],
   note="Hantavax is licensed in South Korea; the efficacy evidence is "
        "limited and it is not used elsewhere. No antiviral, and it does not "
        "cover the American hantaviruses.")


def get(species):
    rec = COUNTERMEASURES.get(species)
    if rec is None:
        return None
    has = bool(rec.get("vaccines") or rec.get("antivirals")
               or rec.get("prophylaxis"))
    return {**rec, "any": has}


def covered():
    return sorted(COUNTERMEASURES)
