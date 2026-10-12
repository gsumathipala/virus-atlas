"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Antiviral therapy: what is licensed, what the trials showed, what is coming.

Scope
-----
`atlas.countermeasures` answers "is there anything?" in a line. This answers
the next question — what, on what evidence, and how good is that evidence —
for the human-infecting viruses where there is something to say.

Every clinical claim carries a reference. References are PMIDs and DOIs and
are machine-verified against Europe PMC by `atlas.update --check-refs`, so a
citation that does not resolve is a build-time failure rather than something a
reader has to catch. Trial identifiers are NCT numbers, verifiable at
ClinicalTrials.gov.

Evidence grading
----------------
Deliberately coarse, because a finer scale would imply a rigour the curation
does not have:

  established     adequately powered randomised trial(s) with a clinical
                  endpoint, reproduced or accepted into major guidelines
  supported       randomised evidence exists but is limited -- single trial,
                  surrogate endpoint, or applicable to a narrow group
  conflicting     randomised trials disagree, or a widely used drug has
                  failed its confirmatory trial
  observational   non-randomised human data only
  preclinical     animal or in-vitro only; no human efficacy data
  historical      long-standing practice predating modern trials

What this is not
----------------
Not a prescribing resource. Doses are omitted on purpose. Licensing,
availability and recommended regimens differ by country and change; the
guideline links are the authority, and this layer exists to point at them and
to say honestly where the evidence is thin or negative.
"""

GRADES = {
    "established": {"rank": 0, "label": "Established",
                    "note": "Adequately powered randomised trial evidence "
                            "with a clinical endpoint, accepted into major "
                            "guidelines."},
    "supported": {"rank": 1, "label": "Supported",
                  "note": "Randomised evidence exists but is limited: a "
                          "single trial, a surrogate endpoint, or a narrow "
                          "population."},
    "conflicting": {"rank": 2, "label": "Conflicting or negative",
                    "note": "Randomised trials disagree, or the drug failed "
                            "its confirmatory trial despite earlier promise."},
    "observational": {"rank": 3, "label": "Observational only",
                      "note": "Non-randomised human data; confounding not "
                              "excluded."},
    "historical": {"rank": 4, "label": "Historical practice",
                   "note": "Long-standing use predating modern trial "
                           "standards."},
    "preclinical": {"rank": 5, "label": "Preclinical",
                    "note": "Animal or in-vitro data only. No human efficacy "
                            "evidence."},
}


def _t(species, **kw):
    THERAPEUTICS[species] = kw


THERAPEUTICS = {}

# ---------------------------------------------------------------- COVID-19
_t("Betacoronavirus pandemicum",
   guidelines=[
       {"body": "WHO", "title": "Therapeutics and COVID-19: living guideline",
        "url": "https://www.who.int/publications/i/item/WHO-2019-nCoV-therapeutics-2023.2"},
       {"body": "NIH", "title": "COVID-19 Treatment Guidelines",
        "url": "https://www.covid19treatmentguidelines.nih.gov/"},
       {"body": "IDSA", "title": "Guidelines on the Treatment and Management of Patients with COVID-19",
        "url": "https://www.idsociety.org/practice-guideline/covid-19-guideline-treatment-and-management/"},
   ],
   agents=[
       {"drug": "Nirmatrelvir/ritonavir", "class": "3CL protease inhibitor",
        "status": "licensed", "grade": "established",
        "use": "Non-hospitalised adults at high risk of progression, within 5 days of symptom onset.",
        "evidence": "EPIC-HR: 88% relative reduction in COVID-19-related "
                    "hospitalisation or death when started within 5 days "
                    "(0.77% vs 6.31%). Benefit was not reproduced in "
                    "standard-risk, largely vaccinated adults in EPIC-SR, "
                    "which is why eligibility is risk-based.",
        "trials": ["NCT04960202", "NCT05011513"],
        "refs": [{"pmid": "35172054", "label": "Hammond et al. EPIC-HR. N Engl J Med 2022"},
                 {"pmid": "38598573", "label": "Hammond et al. EPIC-SR. N Engl J Med 2024"}]},
       {"drug": "Remdesivir", "class": "Nucleotide analogue, RdRp inhibitor",
        "status": "licensed", "grade": "conflicting",
        "use": "Hospitalised patients needing supplemental oxygen; also a 3-day outpatient course.",
        "evidence": "ACTT-1 shortened time to recovery (10 vs 15 days) "
                    "without a clear mortality benefit. WHO SOLIDARITY found "
                    "no effect on mortality, ventilation or hospital stay. "
                    "PINETREE, in outpatients, cut hospitalisation by 87%. "
                    "The disagreement is largely about who and when, not "
                    "whether the drug has antiviral activity.",
        "trials": ["NCT04280705", "NCT04315948", "NCT04501952"],
        "refs": [{"pmid": "32445440", "label": "Beigel et al. ACTT-1. N Engl J Med 2020"},
                 {"pmid": "33264556", "label": "WHO Solidarity Trial Consortium. N Engl J Med 2021"},
                 {"pmid": "34937145", "label": "Gottlieb et al. PINETREE. N Engl J Med 2022"}]},
       {"drug": "Molnupiravir", "class": "Mutagenic nucleoside",
        "status": "licensed in some jurisdictions", "grade": "conflicting",
        "use": "Outpatients where nirmatrelvir is contraindicated by interactions.",
        "evidence": "MOVe-OUT showed a 30% relative reduction in "
                    "hospitalisation or death, well below the 50% seen at "
                    "interim. PANORAMIC, in 25,000 largely vaccinated UK "
                    "adults, found no reduction in hospitalisation or death, "
                    "though recovery was faster. Mutagenesis has also raised "
                    "questions about driving viral diversification.",
        "trials": ["NCT04575597", "ISRCTN30448031"],
        "refs": [{"pmid": "34914868", "label": "Jayk Bernal et al. MOVe-OUT. N Engl J Med 2022"},
                 {"pmid": "36566761", "label": "Butler et al. PANORAMIC. Lancet 2023"}]},
       {"drug": "Dexamethasone", "class": "Corticosteroid (host-directed)",
        "status": "licensed", "grade": "established",
        "use": "Hospitalised patients receiving oxygen or ventilation. Harmful without oxygen.",
        "evidence": "RECOVERY: mortality reduced in ventilated patients "
                    "(29.3% vs 41.4%) and those on oxygen, with no benefit "
                    "and a trend to harm in patients needing neither — the "
                    "clearest demonstration that timing of immunomodulation "
                    "matters more than the drug.",
        "trials": ["NCT04381936"],
        "refs": [{"pmid": "32678530", "label": "RECOVERY Collaborative Group. N Engl J Med 2021"}]},
       {"drug": "Tocilizumab / baricitinib", "class": "IL-6 receptor blockade; JAK inhibition",
        "status": "licensed", "grade": "established",
        "use": "Hospitalised patients with rapidly progressing hypoxia and systemic inflammation.",
        "evidence": "RECOVERY and REMAP-CAP both showed survival benefit "
                    "from tocilizumab added to steroids; baricitinib reduced "
                    "mortality in ACTT-2 and RECOVERY.",
        "trials": ["NCT04381936", "NCT02735707", "NCT04401579"],
        "refs": [{"pmid": "34407334", "label": "REMAP-CAP: Interleukin-6 receptor antagonists in critically ill patients with Covid-19. N Engl J Med 2021"},
                 {"pmid": "33933206", "label": "RECOVERY Collaborative Group. Tocilizumab. Lancet 2021"}]},
       {"drug": "Hydroxychloroquine", "class": "4-aminoquinoline",
        "status": "not recommended", "grade": "conflicting",
        "use": "None. Listed because its failure is instructive.",
        "evidence": "RECOVERY and SOLIDARITY both found no benefit, with a "
                    "signal toward harm. A case study in how in-vitro "
                    "activity and observational series can mislead.",
        "trials": ["NCT04381936", "NCT04315948"],
        "refs": [{"pmid": "33031652", "label": "RECOVERY Collaborative Group. N Engl J Med 2020"}]},
   ],
   investigational=[
       {"drug": "Ensitrelvir", "class": "3CL protease inhibitor",
        "note": "Approved in Japan. SCORPIO-SR shortened time to resolution "
                "of five symptoms; the global phase 3 programme continues.",
        "trials": ["NCT05305547"],
        "refs": [{"pmid": "38972603", "label": "Yotsuyanagi et al. Ensitrelvir and post-COVID-19 condition. 2024"}]},
       {"drug": "Obeldesivir", "class": "Oral nucleoside prodrug",
        "note": "Oral analogue of remdesivir's parent; phase 3 in COVID-19 "
                "did not meet its endpoint, and development has pivoted "
                "toward filoviruses."},
   ],
   note="The useful lesson here is how often early promise did not survive a "
        "properly powered trial — hydroxychloroquine, then molnupiravir in a "
        "vaccinated population, then most monoclonals to viral evolution. The "
        "agents that held up target conserved enzymes or the host response.")

# ---------------------------------------------------------------- influenza
_t("Alphainfluenzavirus influenzae",
   guidelines=[
       {"body": "IDSA", "title": "Clinical Practice Guidelines on Seasonal Influenza",
        "url": "https://www.idsociety.org/practice-guideline/influenza/"},
       {"body": "WHO", "title": "Guidelines for the clinical management of severe illness from influenza virus infections",
        "url": "https://www.who.int/publications/i/item/9789240040816"},
       {"body": "CDC", "title": "Influenza Antiviral Medications: Summary for Clinicians",
        "url": "https://www.cdc.gov/flu/hcp/antivirals/summary-clinicians.html"},
   ],
   agents=[
       {"drug": "Oseltamivir", "class": "Neuraminidase inhibitor",
        "status": "licensed", "grade": "supported",
        "use": "Treatment within 48 hours of onset; earlier is better. Also post-exposure prophylaxis.",
        "evidence": "Shortens symptom duration by roughly a day in otherwise "
                    "healthy adults. The Cochrane review concluded the effect "
                    "on hospitalisation and complications is unproven in "
                    "that group, while observational data in hospitalised and "
                    "high-risk patients suggest a mortality benefit — a "
                    "long-running and unresolved disagreement about what the "
                    "trials can support.",
        "trials": [],
        "refs": [{"pmid": "24811411", "label": "Jefferson et al. Cochrane review. BMJ 2014"},
                 {"pmid": "25640810", "label": "Dobson et al. Oseltamivir meta-analysis. Lancet 2015"},
                 {"pmid": "24815805", "label": "Muthuri et al. PRIDE. Lancet Respir Med 2014"}]},
       {"drug": "Baloxavir marboxil", "class": "Cap-dependent endonuclease inhibitor",
        "status": "licensed", "grade": "established",
        "use": "Single oral dose for uncomplicated influenza; also post-exposure prophylaxis.",
        "evidence": "CAPSTONE-1 matched oseltamivir for symptom relief with "
                    "faster viral clearance from one dose. CAPSTONE-2, in "
                    "high-risk patients, reduced complications. Treatment-"
                    "emergent PA I38X substitutions reduce susceptibility and "
                    "arise in roughly 2-10%, more often in children.",
        "trials": ["NCT02954354", "NCT02949011", "NCT03969212"],
        "refs": [{"pmid": "30184455", "label": "Hayden et al. CAPSTONE-1. N Engl J Med 2018"},
                 {"pmid": "32526195", "label": "Ison et al. CAPSTONE-2. Lancet Infect Dis 2020"}]},
       {"drug": "Zanamivir, peramivir", "class": "Neuraminidase inhibitors",
        "status": "licensed", "grade": "supported",
        "use": "Inhaled and intravenous alternatives; peramivir is a single infusion.",
        "evidence": "Comparable to oseltamivir on symptom duration. Inhaled "
                    "zanamivir is avoided in asthma and COPD.",
        "trials": [], "refs": [
            {"pmid": "24811411", "label": "Jefferson et al. Cochrane review. BMJ 2014"}]},
       {"drug": "Amantadine, rimantadine", "class": "M2 ion-channel blockers",
        "status": "not recommended", "grade": "conflicting",
        "use": "None against currently circulating influenza A.",
        "evidence": "The M2 S31N substitution is near-universal in "
                    "circulating A(H3N2) and A(H1N1)pdm09, abolishing "
                    "activity. A clean example of a drug class lost entirely "
                    "to resistance.",
        "trials": [], "refs": [
            {"pmid": "16456087", "label": "Bright et al. JAMA 2006 (adamantane resistance)"}]},
   ],
   investigational=[
       {"drug": "Baloxavir for transmission reduction", "class": "endonuclease inhibitor",
        "note": "CENTERSTONE tested whether treating an index case reduces "
                "household transmission — a different endpoint from symptom "
                "relief, and relevant to outbreak control.",
        "trials": ["NCT03969212"]},
       {"drug": "Broadly neutralising anti-HA monoclonals", "class": "Immunotherapy",
        "note": "Stem-directed antibodies such as MHAA4549A and CR6261 have "
                "reached phase 2 without establishing benefit over "
                "oseltamivir."},
   ],
   note="For H5N1 and other zoonotic influenza A, oseltamivir is recommended "
        "early and at treatment doses regardless of time since onset, on "
        "extrapolation rather than trial evidence — there has never been a "
        "randomised trial in avian influenza.")

# ---------------------------------------------------------------- HIV
_t("Lentivirus humimdef1",
   guidelines=[
       {"body": "WHO", "title": "Consolidated guidelines on HIV prevention, testing, treatment and care",
        "url": "https://www.who.int/publications/i/item/9789240031593"},
       {"body": "DHHS", "title": "Guidelines for the Use of Antiretroviral Agents in Adults and Adolescents with HIV",
        "url": "https://clinicalinfo.hiv.gov/en/guidelines/hiv-clinical-guidelines-adult-and-adolescent-arv"},
       {"body": "EACS", "title": "European AIDS Clinical Society Guidelines",
        "url": "https://www.eacsociety.org/guidelines/eacs-guidelines/"},
   ],
   agents=[
       {"drug": "Integrase inhibitor-based ART (bictegravir or dolutegravir plus two NRTIs)",
        "class": "INSTI combination", "status": "licensed", "grade": "established",
        "use": "First-line treatment for almost everyone, started on diagnosis.",
        "evidence": "START and TEMPRANO established that immediate treatment "
                    "at any CD4 count reduces serious events. Dolutegravir-"
                    "based regimens outperformed efavirenz in NAMSAL and "
                    "ADVANCE on viral suppression and tolerability.",
        "trials": ["NCT00867048", "NCT00495651", "NCT03122262"],
        "refs": [{"pmid": "26192873", "label": "INSIGHT START Study Group. N Engl J Med 2015"},
                 {"pmid": "26193126", "label": "TEMPRANO ANRS 12136. N Engl J Med 2015"},
                 {"pmid": "31339677", "label": "Venter et al. ADVANCE. N Engl J Med 2019"}]},
       {"drug": "Treatment as prevention", "class": "Public-health use of ART",
        "status": "licensed", "grade": "established",
        "use": "Sustained viral suppression prevents sexual transmission entirely.",
        "evidence": "HPTN 052 showed a 96% reduction in linked transmission. "
                    "PARTNER and PARTNER2 observed zero linked transmissions "
                    "across roughly 77,000 condomless sex acts with an "
                    "undetectable partner — the evidence base for U=U.",
        "trials": ["NCT00074581"],
        "refs": [{"pmid": "21767103", "label": "Cohen et al. HPTN 052. N Engl J Med 2011"},
                 {"pmid": "31056293", "label": "Rodger et al. PARTNER2. Lancet 2019"}]},
       {"drug": "Oral PrEP (tenofovir/emtricitabine)", "class": "Pre-exposure prophylaxis",
        "status": "licensed", "grade": "established",
        "use": "HIV-negative people at substantial risk.",
        "evidence": "iPrEx, Partners PrEP and PROUD all showed large "
                    "reductions in acquisition, with efficacy tracking "
                    "adherence closely.",
        "trials": ["NCT00458393", "NCT00557245"],
        "refs": [{"pmid": "21091279", "label": "Grant et al. iPrEx. N Engl J Med 2010"},
                 {"pmid": "26364263", "label": "McCormack et al. PROUD. Lancet 2016"}]},
       {"drug": "Lenacapavir", "class": "First-in-class capsid inhibitor",
        "status": "licensed", "grade": "established",
        "use": "Twice-yearly injection: multidrug-resistant infection, and now prevention.",
        "evidence": "CAPELLA established efficacy in heavily treatment-"
                    "experienced patients. PURPOSE 1, in young women in sub-"
                    "Saharan Africa, recorded zero infections among 2,134 "
                    "participants — 100% efficacy against the background "
                    "incidence; PURPOSE 2 showed 96% in a broader population.",
        "trials": ["NCT04150068", "NCT04994509", "NCT04925752"],
        "refs": [{"pmid": "35544387", "label": "Segal-Maurer et al. CAPELLA. N Engl J Med 2022"},
                 {"pmid": "39046157", "label": "Bekker et al. PURPOSE 1. N Engl J Med 2024"}]},
       {"drug": "Long-acting cabotegravir", "class": "Injectable INSTI",
        "status": "licensed", "grade": "established",
        "use": "Two-monthly injectable PrEP, and with rilpivirine as maintenance therapy.",
        "evidence": "Both trials were superior to daily oral PrEP. HPTN 083, "
                    "in cisgender men and transgender women, found a hazard "
                    "ratio of 0.34 — a 66% lower incidence — and HPTN 084, in "
                    "women in sub-Saharan Africa, a hazard ratio of 0.12, an "
                    "88% reduction. Injection-site reactions were very common.",
        "trials": ["NCT02720094", "NCT03164564"],
        "refs": [{"pmid": "34379922", "label": "Landovitz et al. HPTN 083. N Engl J Med 2021"},
                 {"pmid": "35378077", "label": "Delany-Moretlwe et al. HPTN 084. Lancet 2022"}]},
   ],
   investigational=[
       {"drug": "Broadly neutralising antibodies (3BNC117, 10-1074)",
        "class": "Immunotherapy", "note": "Combinations delay rebound after "
        "treatment interruption in people with sensitive virus; not a cure, "
        "and pre-existing resistance limits who can use them.",
        "refs": [{"pmid": "30258136", "label": "Mendoza et al. Nature 2018"}]},
       {"drug": "Latency reversal and 'shock and kill'", "class": "Cure strategy",
        "note": "Histone deacetylase inhibitors reliably reverse latency and "
                "have not reduced the reservoir in any trial."},
   ],
   note="No vaccine, and the only cures have come from allogeneic stem-cell "
        "transplant with CCR5-Δ32 donors — not a scalable strategy. The "
        "clinically important fact is that effective treatment eliminates "
        "sexual transmission.")

# ---------------------------------------------------------------- hepatitis B/C/D
_t("Orthohepadnavirus hominoidei",
   guidelines=[
       {"body": "WHO", "title": "Guidelines for the prevention, diagnosis, care and treatment for people with chronic hepatitis B",
        "url": "https://www.who.int/publications/i/item/9789240090903"},
       {"body": "AASLD", "title": "Hepatitis B Guidance",
        "url": "https://www.aasld.org/practice-guidelines/chronic-hepatitis-b"},
       {"body": "EASL", "title": "Clinical Practice Guidelines on the management of hepatitis B virus infection",
        "url": "https://easl.eu/publication/easl-clinical-practice-guidelines-management-of-hepatitis-b/"},
   ],
   agents=[
       {"drug": "Tenofovir disoproxil / tenofovir alafenamide",
        "class": "Nucleotide analogue", "status": "licensed", "grade": "established",
        "use": "First-line suppression; usually lifelong.",
        "evidence": "Durable viral suppression with histological improvement "
                    "and regression of fibrosis and even cirrhosis on "
                    "long-term therapy; no resistance detected through five "
                    "years. Suppression reduces hepatocellular carcinoma "
                    "incidence but does not abolish it.",
        "trials": ["NCT00117676"],
        "refs": [{"pmid": "23234725", "label": "Marcellin et al. Lancet 2013 (5-year regression of cirrhosis)"},
                 {"pmid": "19052126", "label": "Marcellin et al. N Engl J Med 2008"}]},
       {"drug": "Entecavir", "class": "Nucleoside analogue",
        "status": "licensed", "grade": "established",
        "use": "First-line alternative; avoid in lamivudine-experienced patients.",
        "evidence": "Reduced disease progression and hepatocellular carcinoma "
                    "versus placebo in advanced fibrosis.",
        "trials": [],
        "refs": [{"pmid": "15470215", "label": "Liaw et al. N Engl J Med 2004 (lamivudine, progression)"},
                 {"pmid": "16525137", "label": "Chang et al. N Engl J Med 2006 (entecavir vs lamivudine)"}]},
       {"drug": "Pegylated interferon alfa-2a", "class": "Immunomodulator",
        "status": "licensed", "grade": "supported",
        "use": "Finite 48-week course in selected patients; higher rate of HBsAg loss.",
        "evidence": "Achieves functional cure more often than nucleos(t)ides "
                    "but in a minority, and tolerability is poor.",
        "trials": [], "refs": [
            {"pmid": "15987917", "label": "Lau et al. N Engl J Med 2005"}]},
   ],
   investigational=[
       {"drug": "Bepirovirsen", "class": "Antisense oligonucleotide",
        "note": "B-Clear (phase 2b) achieved sustained HBsAg and HBV DNA loss "
                "in roughly 9-10% — the most promising functional-cure signal "
                "so far, now in phase 3 (B-Well).",
        "trials": ["NCT04449029", "NCT05630807"],
        "refs": [{"pmid": "36346079", "label": "Yuen et al. B-Clear. N Engl J Med 2022"}]},
       {"drug": "siRNA (xalnesiran, imdusiran) and capsid assembly modulators",
        "class": "Combination functional cure", "note":
        "Multiple phase 2 combinations with and without immunomodulation; "
        "HBsAg loss remains the hard endpoint and is rarely durable."},
   ],
   note="Treatment is suppressive. cccDNA persists in the hepatocyte nucleus "
        "and integrated HBV DNA continues to make surface antigen, so "
        "'functional cure' — sustained HBsAg loss off therapy — is the goal "
        "rather than eradication.")

_t("Deltavirus italiense",
   guidelines=[
       {"body": "EASL", "title": "Clinical Practice Guidelines on hepatitis delta virus",
        "url": "https://easl.eu/publication/easl-clinical-practice-guidelines-on-hepatitis-delta-virus/"},
   ],
   agents=[
       {"drug": "Bulevirtide", "class": "NTCP entry inhibitor",
        "status": "licensed (EU)", "grade": "established",
        "use": "Chronic hepatitis D with compensated liver disease.",
        "evidence": "MYR301 (phase 3): 45% achieved a combined virological "
                    "and biochemical response at 48 weeks versus 2% with no "
                    "treatment, sustained to 96 weeks. The first drug "
                    "licensed specifically for HDV.",
        "trials": ["NCT03852719"],
        "refs": [{"pmid": "37345876", "label": "Wedemeyer et al. MYR301. N Engl J Med 2023"}]},
       {"drug": "Pegylated interferon alfa", "class": "Immunomodulator",
        "status": "off-label", "grade": "supported",
        "use": "Alternative or add-on; finite course.",
        "evidence": "Sustained response in a minority, with frequent late "
                    "relapse.",
        "trials": [], "refs": [
            {"pmid": "21268724", "label": "Wedemeyer et al. HIDIT-1. N Engl J Med 2011"}]},
   ],
   investigational=[
       {"drug": "Lonafarnib (with ritonavir)", "class": "Prenylation inhibitor",
        "note": "D-LIVR phase 3 met virological endpoints with substantial "
                "gastrointestinal toxicity.",
        "trials": ["NCT03719313"]},
   ],
   note="HDV is the most severe chronic viral hepatitis, and until bulevirtide "
        "there was nothing licensed for it at all. Hepatitis B vaccination "
        "prevents it absolutely.")

_t("Orthohepacivirus hominis",
   guidelines=[
       {"body": "WHO", "title": "Guidelines for the care and treatment of persons diagnosed with chronic hepatitis C",
        "url": "https://www.who.int/publications/i/item/9789240052734"},
       {"body": "AASLD/IDSA", "title": "HCV Guidance: Recommendations for Testing, Managing, and Treating Hepatitis C",
        "url": "https://www.hcvguidelines.org/"},
   ],
   agents=[
       {"drug": "Sofosbuvir/velpatasvir; glecaprevir/pibrentasvir",
        "class": "Pangenotypic direct-acting antivirals",
        "status": "licensed", "grade": "established",
        "use": "8-12 weeks oral therapy, curative across genotypes.",
        "evidence": "Sustained virological response above 95% in ASTRAL-1 "
                    "and ENDURANCE, including in cirrhosis. SVR is a cure: "
                    "late relapse is rare and fibrosis regresses.",
        "trials": ["NCT02201940", "NCT02604017"],
        "refs": [{"pmid": "26571066", "label": "Feld et al. ASTRAL-1. N Engl J Med 2015"},
                 {"pmid": "29365309", "label": "Zeuzem et al. ENDURANCE-1. N Engl J Med 2018"}]},
   ],
   investigational=[],
   note="The clearest therapeutic success in virology: a uniformly chronic, "
        "cirrhosis-causing infection became curable in 8-12 oral weeks within "
        "a decade. There is still no vaccine, so elimination depends entirely "
        "on finding and treating people.")

# ---------------------------------------------------------------- herpesviruses
_t("Simplexvirus humanalpha1",
   guidelines=[
       {"body": "CDC", "title": "STI Treatment Guidelines: Genital Herpes",
        "url": "https://www.cdc.gov/std/treatment-guidelines/herpes.htm"},
   ],
   agents=[
       {"drug": "Aciclovir, valaciclovir, famciclovir",
        "class": "Nucleoside analogues activated by viral thymidine kinase",
        "status": "licensed", "grade": "established",
        "use": "Episodic treatment, daily suppression, and intravenous therapy for encephalitis and neonatal disease.",
        "evidence": "Intravenous aciclovir reduced mortality in HSV "
                    "encephalitis from around 70% to 19-28% — one of the "
                    "largest treatment effects in infectious disease. "
                    "Suppressive valaciclovir also reduces transmission to a "
                    "susceptible partner by about 48%.",
        "trials": [],
        "refs": [{"pmid": "3001520", "label": "Whitley et al. N Engl J Med 1986 (HSV encephalitis)"},
                 {"pmid": "14702423", "label": "Corey et al. N Engl J Med 2004 (transmission)"}]},
       {"drug": "Foscarnet, cidofovir", "class": "Polymerase inhibitors, TK-independent",
        "status": "licensed", "grade": "observational",
        "use": "Aciclovir-resistant disease, usually in immunocompromised patients.",
        "evidence": "Case series only; nephrotoxicity is substantial.",
        "trials": [], "refs": []},
   ],
   investigational=[
       {"drug": "Pritelivir", "class": "Helicase-primase inhibitor",
        "note": "Active against aciclovir-resistant HSV; phase 3 PRIOH-1 in "
                "immunocompromised patients. A distinct target, so no "
                "cross-resistance with nucleoside analogues.",
        "trials": ["NCT03073967"],
        "refs": [{"pmid": "27997653", "label": "Wald et al. JAMA 2016 (pritelivir phase 2)"}]},
   ],
   note="Antivirals suppress replication but cannot clear latent genomes from "
        "sensory ganglia, so they shorten and prevent episodes without curing "
        "or stopping future reactivation. Treatment of encephalitis is a "
        "time-critical emergency: start on suspicion, before confirmation.")

_t("Cytomegalovirus humanbeta5",
   guidelines=[
       {"body": "The Transplantation Society", "title": "International Consensus Guidelines on CMV in Solid-Organ Transplantation",
        "url": "https://tts.org/guidelines-cmv"},
   ],
   agents=[
       {"drug": "Valganciclovir / ganciclovir", "class": "Nucleoside analogue",
        "status": "licensed", "grade": "established",
        "use": "Treatment and prophylaxis of CMV disease in transplant and advanced HIV.",
        "evidence": "Long-established; myelosuppression is the limiting "
                    "toxicity. Valganciclovir is non-inferior to intravenous "
                    "ganciclovir for CMV disease in solid-organ transplant.",
        "trials": [], "refs": [
            {"pmid": "17640310", "label": "Asberg et al. VICTOR. Am J Transplant 2007"}]},
       {"drug": "Letermovir", "class": "Terminase complex inhibitor",
        "status": "licensed", "grade": "established",
        "use": "Prophylaxis after allogeneic haematopoietic stem-cell transplant.",
        "evidence": "Phase 3: clinically significant CMV infection in 37.5% "
                    "versus 60.6% with placebo by week 24, with lower "
                    "all-cause mortality and no myelosuppression — which is "
                    "what changed transplant practice.",
        "trials": ["NCT02137772"],
        "refs": [{"pmid": "29211658", "label": "Marty et al. N Engl J Med 2017"}]},
       {"drug": "Maribavir", "class": "UL97 kinase inhibitor",
        "status": "licensed", "grade": "established",
        "use": "Refractory or resistant post-transplant CMV.",
        "evidence": "SOLSTICE: superior to investigator-assigned therapy for "
                    "viraemia clearance (55.7% vs 23.9%) with less "
                    "nephrotoxicity and neutropenia.",
        "trials": ["NCT02931539"],
        "refs": [{"pmid": "34864943", "label": "Avery et al. SOLSTICE. Clin Infect Dis 2022"}]},
   ],
   investigational=[],
   note="Congenital CMV is the commonest infectious cause of childhood "
        "sensorineural deafness; valganciclovir for symptomatic congenital "
        "disease improves hearing and neurodevelopmental outcomes, and there "
        "is still no vaccine.")

# ---------------------------------------------------------------- RSV
_t("Orthopneumovirus hominis",
   guidelines=[
       {"body": "AAP", "title": "Clinical Practice Guideline: Bronchiolitis",
        "url": "https://publications.aap.org/pediatrics/article/134/5/e1474/75848"},
   ],
   agents=[
       {"drug": "Nirsevimab", "class": "Long-acting anti-prefusion-F monoclonal",
        "status": "licensed", "grade": "established",
        "use": "Single dose to all infants entering their first RSV season.",
        "evidence": "MELODY: 74.5% efficacy against medically attended RSV "
                    "lower respiratory tract infection. HARMONIE, a "
                    "pragmatic trial in 8,058 infants, showed 83% reduction "
                    "in hospitalisation. Real-world national programmes have "
                    "reproduced this.",
        "trials": ["NCT03979313", "NCT05437510"],
        "refs": [{"pmid": "35235726", "label": "Hammitt et al. MELODY. N Engl J Med 2022"},
                 {"pmid": "38157500", "label": "Drysdale et al. HARMONIE. N Engl J Med 2023"}]},
       {"drug": "Palivizumab", "class": "Monoclonal, monthly",
        "status": "licensed", "grade": "established",
        "use": "High-risk infants only; largely superseded by nirsevimab.",
        "evidence": "IMpact-RSV: 55% reduction in hospitalisation.",
        "trials": [], "refs": [
            {"pmid": "9724660", "label": "IMpact-RSV: palivizumab reduces hospitalization from respiratory syncytial virus. Pediatrics 1998"}]},
       {"drug": "Ribavirin", "class": "Nucleoside analogue",
        "status": "licensed but not recommended routinely", "grade": "conflicting",
        "use": "Occasionally in severely immunocompromised patients.",
        "evidence": "No consistent clinical benefit; aerosol administration "
                    "is hazardous to staff.",
        "trials": [], "refs": []},
   ],
   investigational=[
       {"drug": "Ziresovir", "class": "Fusion inhibitor",
        "note": "Phase 3 in hospitalised Chinese infants reduced bronchiolitis "
                "score and viral load — the first antiviral to show clinical "
                "benefit in RSV bronchiolitis.",
        "trials": ["NCT04231968"],
        "refs": [{"pmid": "41140261", "label": "Ziresovir: oral RSV fusion inhibitor \u2014 review of the phase 3 programme. 2025"}]},
   ],
   note="RSV went from nothing to maternal vaccination, infant monoclonal and "
        "older-adult vaccines within about two years, once prefusion F was "
        "stabilised as an immunogen.")

# ---------------------------------------------------------------- filoviruses
_t("Orthoebolavirus zairense",
   guidelines=[
       {"body": "WHO", "title": "Therapeutics for Ebola virus disease: WHO guideline",
        "url": "https://www.who.int/publications/i/item/9789240055742"},
   ],
   agents=[
       {"drug": "Ansuvimab (mAb114)", "class": "Single human monoclonal against GP",
        "status": "licensed", "grade": "established",
        "use": "Confirmed Zaire ebolavirus disease, including neonates and pregnancy.",
        "evidence": "PALM, a randomised trial run during the 2018-20 DRC "
                    "outbreak: 28-day mortality 35.1% versus 49.7% with "
                    "ZMapp. Benefit was greatest when given early with a low "
                    "viral load.",
        "trials": ["NCT03719586"],
        "refs": [{"pmid": "31774950", "label": "Mulangu et al. PALM. N Engl J Med 2019"}]},
       {"drug": "REGN-EB3 (atoltivimab/maftivimab/odesivimab)",
        "class": "Three-antibody cocktail", "status": "licensed", "grade": "established",
        "use": "As above.",
        "evidence": "PALM: 28-day mortality 33.5% versus 49.7% with ZMapp.",
        "trials": ["NCT03719586"],
        "refs": [{"pmid": "31774950", "label": "Mulangu et al. PALM. N Engl J Med 2019"}]},
       {"drug": "Remdesivir, ZMapp", "class": "RdRp inhibitor; antibody cocktail",
        "status": "not recommended", "grade": "conflicting",
        "use": "None — both were dropped from PALM at the interim analysis.",
        "evidence": "Inferior to the two monoclonals; WHO recommends against.",
        "trials": ["NCT03719586"],
        "refs": [{"pmid": "31774950", "label": "Mulangu et al. PALM. N Engl J Med 2019"}]},
   ],
   investigational=[
       {"drug": "Obeldesivir", "class": "Oral nucleoside prodrug",
        "note": "Full protection in non-human primate challenge with Sudan "
                "and Marburg virus; no human efficacy data.",
        "refs": [{"pmid": "38484056", "label": "Cross et al. 2024 (obeldesivir protects NHPs against Sudan virus)"}]},
   ],
   note="Both licensed therapeutics are specific to Zaire ebolavirus, as is "
        "the ERVEBO vaccine. For Sudan, Bundibugyo and Marburg virus there is "
        "nothing licensed at all — which is why the current Bundibugyo "
        "outbreak is a much harder problem than 2018-20 was. PALM is also a "
        "landmark in method: a randomised controlled trial completed during "
        "an active, highly lethal outbreak.")

_t("Orthomarburgvirus marburgense",
   guidelines=[
       {"body": "WHO", "title": "Marburg virus disease fact sheet and outbreak toolbox",
        "url": "https://www.who.int/health-topics/marburg-virus-disease"},
   ],
   agents=[],
   investigational=[
       {"drug": "Remdesivir, obeldesivir, MBP091", "class": "Antivirals and monoclonal",
        "note": "Protection in non-human primates; deployed under trial and "
                "compassionate protocols during the Rwanda and Equatorial "
                "Guinea outbreaks, with no efficacy data yet.",
        "refs": [{"pmid": "38484056", "label": "Cross et al. 2024 (obeldesivir in nonhuman primates)"}]},
       {"drug": "Sabin and IAVI vaccine candidates", "class": "ChAd3 and rVSV vectors",
        "note": "Rapid-response trials initiated during the 2024-25 Rwanda "
                "outbreak; immunogenicity data only."},
   ],
   note="Nothing is licensed. Management is intensive supportive care, which "
        "on its own substantially reduces mortality.")

# ---------------------------------------------------------------- mpox
_t("Orthopoxvirus monkeypox",
   guidelines=[
       {"body": "WHO", "title": "Clinical management and infection prevention and control for mpox",
        "url": "https://www.who.int/publications/i/item/WHO-MPX-Clinical-and-IPC-2022.1"},
       {"body": "CDC", "title": "Clinical Treatment of Mpox",
        "url": "https://www.cdc.gov/poxvirus/mpox/clinicians/treatment.html"},
   ],
   agents=[
       {"drug": "Tecovirimat", "class": "VP37 envelope wrapping inhibitor",
        "status": "licensed for smallpox; used off-label for mpox",
        "grade": "conflicting",
        "use": "Severe or high-risk mpox, now within a trial or protocol where possible.",
        "evidence": "The decisive point in this entry. PALM007, randomised in "
                    "DRC clade I disease, found no difference in time to "
                    "lesion resolution or mortality. STOMP, in clade II "
                    "disease, was stopped for futility. Widespread deployment "
                    "in 2022 rested on animal-rule approval and observational "
                    "series, and the randomised evidence did not support it.",
        "trials": ["NCT05559099", "NCT05534984"],
        "refs": [{"pmid": "42526486", "label": "Tecovirimat treatment of clade II mpox: virological analysis of a randomised trial. 2026"},
                 {"pmid": "41995224", "label": "Mpox clinical outcomes with and without HIV, treated with tecovirimat. 2026"}]},
       {"drug": "Brincidofovir, cidofovir", "class": "Nucleotide analogues",
        "status": "licensed for smallpox", "grade": "observational",
        "use": "Severe disease where tecovirimat has failed.",
        "evidence": "Case series only; hepatotoxicity with brincidofovir and "
                    "nephrotoxicity with cidofovir.",
        "trials": [], "refs": []},
       {"drug": "Vaccinia immune globulin", "class": "Polyclonal antibody",
        "status": "licensed for vaccinia complications", "grade": "observational",
        "use": "Severe disease in profound immunosuppression.",
        "evidence": "No controlled data in mpox.",
        "trials": [], "refs": []},
   ],
   investigational=[
       {"drug": "NIOCH-14", "class": "Tecovirimat-like VP37 inhibitor",
        "note": "Russian compound; preclinical and early human data only."},
   ],
   note="The clearest recent example of why randomised trials during an "
        "outbreak matter: a drug deployed worldwide on the strength of animal "
        "data did not show benefit when it was finally tested. Vaccination "
        "and supportive care remain the effective interventions.")

# ---------------------------------------------------------------- measles, rabies, VHF
_t("Morbillivirus hominis",
   guidelines=[
       {"body": "WHO", "title": "Measles fact sheet and position paper",
        "url": "https://www.who.int/news-room/fact-sheets/detail/measles"},
   ],
   agents=[
       {"drug": "Vitamin A", "class": "Supportive, not antiviral",
        "status": "recommended", "grade": "established",
        "use": "Two doses to all children with measles, regardless of nutritional status.",
        "evidence": "The Cochrane review is more nuanced than it is usually "
                    "quoted: pooling all trials showed NO significant "
                    "reduction in mortality (RR 0.70, 95% CI 0.42-1.15). The "
                    "benefit was confined to the two-dose regimen, and to "
                    "children under two, with a reduction in croup (RR 0.53) "
                    "but not in pneumonia or diarrhoea. Vitamin A is not an "
                    "antiviral: it corrects an acute deficiency that measles "
                    "itself induces.",
        "trials": [],
        "refs": [{"pmid": "16235283", "label": "Huiming et al. Vitamin A for treating measles. Cochrane review 2005"}]},
       {"drug": "Ribavirin", "class": "Nucleoside analogue",
        "status": "not recommended", "grade": "observational",
        "use": "Occasionally in severe or immunocompromised measles.",
        "evidence": "Case reports only; no controlled evidence.",
        "trials": [], "refs": []},
   ],
   investigational=[
       {"drug": "ERDRP-0519", "class": "Polymerase inhibitor",
        "note": "Protective in the ferret canine-distemper model when given "
                "after infection; no human data.",
        "refs": [{"pmid": "24739760", "label": "Krumm et al. Orally available polymerase inhibitor, morbillivirus. Sci Transl Med 2014"}]},
   ],
   note="There is no antiviral for measles. Vaccination is the entire "
        "strategy, and vitamin A plus management of pneumonia and diarrhoea "
        "is what reduces mortality once infection has occurred.")

_t("Lyssavirus rabies",
   guidelines=[
       {"body": "WHO", "title": "Rabies vaccines: WHO position paper, and Expert Consultation on Rabies, third report",
        "url": "https://www.who.int/publications/i/item/WHO-WER9316"},
   ],
   agents=[
       {"drug": "Post-exposure prophylaxis: wound washing, vaccine, and rabies immunoglobulin",
        "class": "Active plus passive immunisation",
        "status": "licensed", "grade": "established",
        "use": "Immediately after any category II or III exposure, at any interval since the bite.",
        "evidence": "Essentially 100% effective when started before symptoms. "
                    "Thorough wound washing alone substantially reduces risk; "
                    "immunoglobulin infiltrated into the wound covers the "
                    "period before vaccine-induced antibody appears.",
        "trials": [],
        "refs": [{"pmid": "30107991", "label": "Rabies vaccines: WHO position paper, April 2018"}]},
       {"drug": "Milwaukee protocol", "class": "Therapeutic coma",
        "status": "not recommended", "grade": "conflicting",
        "use": "None.",
        "evidence": "The single apparent survival has not been reproduced in "
                    "repeated subsequent attempts, and the protocol is no "
                    "longer recommended.",
        "trials": [], "refs": [
            {"pmid": "15958806", "label": "Willoughby et al. N Engl J Med 2005 (Milwaukee protocol)"}]},
   ],
   investigational=[
       {"drug": "Monoclonal antibodies (rabishield, SII RMAb)",
        "class": "Replacement for immunoglobulin",
        "note": "Licensed in India; non-inferior to human rabies "
                "immunoglobulin on neutralising titres, and far more "
                "scalable than plasma-derived product."},
   ],
   note="The widest gap in medicine between prevention and treatment: "
        "prophylaxis is nearly perfect, and established encephalitic rabies "
        "is effectively always fatal.")

_t("Mammarenavirus lassaense",
   guidelines=[
       {"body": "WHO", "title": "Lassa fever fact sheet and clinical management",
        "url": "https://www.who.int/health-topics/lassa-fever"},
   ],
   agents=[
       {"drug": "Ribavirin", "class": "Nucleoside analogue",
        "status": "widely used, off-label", "grade": "conflicting",
        "use": "Historically standard; increasingly questioned.",
        "evidence": "The practice rests on McCormick's 1986 study, whose "
                    "design and analysis have since been seriously "
                    "criticised — non-contemporaneous controls and "
                    "differential ascertainment. A 2021 reanalysis suggested "
                    "ribavirin may be associated with harm at higher viral "
                    "loads. Trials are under way; the honest position is that "
                    "we do not know.",
        "trials": [],
        "refs": [{"pmid": "3940312", "label": "McCormick et al. N Engl J Med 1986 (Lassa fever, ribavirin)"},
                 {"pmid": "35353804", "label": "Salam et al. Ribavirin for Lassa fever: systematic review. 2022"}]},
   ],
   investigational=[
       {"drug": "Favipiravir", "class": "RdRp inhibitor",
        "note": "Superior to ribavirin in animal models; no human efficacy "
                "data."},
       {"drug": "Arevirumab-3 / LASV monoclonal cocktails",
        "class": "Immunotherapy",
        "note": "Protective in non-human primates even late in disease."},
   ],
   note="A good illustration of how long a weakly evidenced practice can "
        "persist when the disease is rare, lethal and occurs where trials are "
        "hard to run.")

_t("Orthonairovirus haemorrhagiae",
   guidelines=[
       {"body": "WHO", "title": "Crimean-Congo haemorrhagic fever fact sheet",
        "url": "https://www.who.int/news-room/fact-sheets/detail/crimean-congo-haemorrhagic-fever"},
   ],
   agents=[
       {"drug": "Ribavirin", "class": "Nucleoside analogue",
        "status": "used, contested", "grade": "conflicting",
        "use": "Variably recommended; practice differs by country.",
        "evidence": "Observational series suggest benefit when started "
                    "early; the one randomised trial was underpowered and "
                    "negative, and systematic reviews have not resolved it.",
        "trials": [],
        "refs": [{"pmid": "29869797", "label": "Johnson et al. Ribavirin for CCHF. Cochrane review 2018"}]},
   ],
   investigational=[
       {"drug": "Favipiravir", "class": "RdRp inhibitor",
        "note": "Effective in the IFNAR-/- mouse model including as "
                "post-exposure treatment; human trials proposed."},
   ],
   note="On the WHO priority pathogen list precisely because high lethality, "
        "nosocomial transmission and the absence of any proven therapy "
        "coincide.")

# ---------------------------------------------------------------- arboviruses
_t("Orthoflavivirus denguei",
   guidelines=[
       {"body": "WHO", "title": "Dengue: guidelines for diagnosis, treatment, prevention and control",
        "url": "https://www.who.int/publications/i/item/9789241547871"},
   ],
   agents=[
       {"drug": "None", "class": "—", "status": "none licensed", "grade": "established",
        "use": "Management is careful fluid balance guided by warning signs and haematocrit.",
        "evidence": "Judicious crystalloid resuscitation during the critical "
                    "plasma-leak phase is what reduces mortality. "
                    "Corticosteroids do not help, and NSAIDs and "
                    "intramuscular injections are avoided because of bleeding "
                    "risk.",
        "trials": [],
        "refs": [{"pmid": "16135832", "label": "Wills et al. N Engl J Med 2005 (fluid resuscitation)"}]},
   ],
   investigational=[
       {"drug": "Mosnodenvir (JNJ-1802)", "class": "NS3-NS4B interaction inhibitor",
        "note": "Prevented infection in a human challenge model — the first "
                "clinical signal for a dengue antiviral.",
        "trials": ["NCT05201794"]},
   ],
   note="No antiviral exists for the most common arboviral infection of "
        "humans. Everything that reduces dengue mortality is supportive, and "
        "it works: case fatality falls below 1% with good fluid management.")

_t("Alphavirus chikungunya",
   guidelines=[
       {"body": "PAHO", "title": "Preparedness and Response for Chikungunya Virus Introduction",
        "url": "https://www.paho.org/en/documents/preparedness-and-response-chikungunya-virus-introduction-americas"},
   ],
   agents=[
       {"drug": "None", "class": "—", "status": "none licensed", "grade": "observational",
        "use": "Analgesia; NSAIDs once dengue is excluded. Chronic arthritis is managed rheumatologically.",
        "evidence": "No antiviral has shown benefit. Chloroquine was no "
                    "better than placebo for acute disease or chronic "
                    "arthralgia; methotrexate has limited evidence in "
                    "post-chikungunya arthritis.",
        "trials": [],
        "refs": [{"pmid": "42030337", "label": "Post-chikungunya chronic arthralgia: frequency and associations. 2026"}]},
   ],
   investigational=[
       {"drug": "IXCHIQ and Vimkunya vaccines", "class": "Prevention, not treatment",
        "note": "Live-attenuated and VLP vaccines now licensed in some "
                "jurisdictions — the therapeutic gap remains complete."},
   ],
   note="Months to years of disabling polyarthralgia with no specific "
        "treatment is the real burden of this infection, and it is "
        "under-recognised relative to the acute illness.")

_t("Henipavirus nipahense",
   guidelines=[
       {"body": "WHO", "title": "Nipah virus fact sheet and R&D blueprint",
        "url": "https://www.who.int/news-room/fact-sheets/detail/nipah-virus"},
   ],
   agents=[],
   investigational=[
       {"drug": "m102.4", "class": "Human monoclonal against G glycoprotein",
        "note": "Protective in African green monkeys when given up to five "
                "days after exposure; used on compassionate grounds in "
                "Australia and in the 2018 Kerala outbreak. Phase 1 "
                "completed; no efficacy trial is possible outside an "
                "outbreak.",
        "refs": [{"pmid": "24964990", "label": "Geisbert et al. m102.4 in nonhuman primates. Sci Transl Med 2014"}]},
       {"drug": "Remdesivir", "class": "RdRp inhibitor",
        "note": "Protected African green monkeys against lethal Nipah "
                "challenge.",
        "refs": [{"pmid": "31142680", "label": "Lo et al. Remdesivir protects African green monkeys from Nipah virus challenge. Sci Transl Med 2019"}]},
       {"drug": "HeV-sG vaccine (Equivac HeV and human candidates)",
        "class": "Soluble G subunit",
        "note": "Licensed for horses against Hendra virus; human candidates "
                "in phase 1."},
   ],
   note="A WHO priority pathogen with 40-75% case fatality and nothing "
        "licensed. Ribavirin was used in the 1998-99 Malaysian outbreak with "
        "an uncontrolled suggestion of benefit that has never been confirmed.")


def get(species):
    rec = THERAPEUTICS.get(species)
    if rec is None:
        return None
    agents = sorted(rec.get("agents") or [],
                    key=lambda a: GRADES.get(a.get("grade"), {}).get("rank", 9))
    return {
        **rec,
        "agents": [{**a, "grade_label": GRADES.get(a.get("grade"), {}).get("label"),
                    "grade_note": GRADES.get(a.get("grade"), {}).get("note")}
                   for a in agents],
        # Deliberately narrow: "is there a licensed drug to TREAT this?".
        # atlas.countermeasures answers the wider "is there anything at all?",
        # which includes vaccines, so the two disagree for measles and dengue
        # by design rather than by error.
        "any_licensed_antiviral": any(
            a.get("status", "").startswith("licensed")
            and a.get("class") not in ("—", "Supportive, not antiviral",
                                       "Corticosteroid (host-directed)")
            for a in agents),
        "has_agents": bool(agents),
    }


def covered():
    return sorted(THERAPEUTICS)


def all_refs():
    """Every reference in the file, for machine verification."""
    out = []
    for species, rec in THERAPEUTICS.items():
        for block in ("agents", "investigational"):
            for item in rec.get(block) or []:
                for ref in item.get("refs") or []:
                    out.append({"species": species,
                                "drug": item.get("drug"), **ref})
    return out


def all_trials():
    out = []
    for species, rec in THERAPEUTICS.items():
        for block in ("agents", "investigational"):
            for item in rec.get(block) or []:
                for nct in item.get("trials") or []:
                    out.append({"species": species, "drug": item.get("drug"),
                                "id": nct})
    return out
