"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Human-infection evidence for ICTV species, outside the curated profiles.

Why this file exists
--------------------
`atlas.profiles` holds long-form briefings, and writing one is slow, so only a
few dozen species have one. Everything else used to fall through to a default
of "no-evidence", which does not mean "we have not looked" -- it asserts that
no human infection has been reported. For measles, hepatitis B, RSV, norovirus
and a few hundred others that assertion is simply false.

So tiers are resolved in layers, weakest claim last, and every species records
WHICH layer decided it so the interface can show its working:

  profile     a curated briefing in atlas.profiles
  reference   the REFERENCE table below -- a tier and a one-line reason
  vmr-name    the ICTV record's own isolate names refer to human sources, and
              the host range includes vertebrates
  host-range  the host range has no vertebrate in it at all, so "no human
              evidence" is a claim the data actually supports
  unassessed  a vertebrate virus nobody here has assessed. Not a finding.
  override    corrected by the user at runtime (see atlas.overrides)

The REFERENCE table is deliberately a flat, auditable list: one line per
species, the tier, and why. It is a curated layer, not ICTV data, and it is
certainly incomplete -- which is what the override mechanism is for.

Species names are ICTV binomials as they appear in the VMR, verified against
the loaded dataset by `atlas.build`; a typo shows up as a startup warning
rather than silently doing nothing.
"""

import re

E, PR, PO, AO, NO = "established", "probable", "possible", "animal-only", "no-evidence"

# --------------------------------------------------------------------------
# Species with human-infection evidence, by family. The note is the reason the
# tier was assigned, phrased so it can be shown verbatim in the interface.
# --------------------------------------------------------------------------

REFERENCE = {

    # --- Paramyxoviridae / Pneumoviridae ---------------------------------
    "Morbillivirus hominis": (E, "Measles virus. Causal agent of measles; eradicable, vaccine-preventable."),
    "Henipavirus nipahense": (E, "Nipah virus. Encephalitis and respiratory disease with person-to-person spread."),
    "Henipavirus hendraense": (E, "Hendra virus. Fatal encephalitis and pneumonitis acquired from horses."),
    "Henipavirus ghanaense": (PO, "Ghanaian bat henipavirus. Henipavirus-reactive antibody in people exposed to bats; no confirmed disease."),
    "Henipavirus cedarense": (NO, "Cedar virus. Replicates in animal models without disease; no human infection reported."),
    "Orthorubulavirus parotitidis": (E, "Mumps virus. Parotitis, orchitis, meningitis; vaccine-preventable."),
    "Orthorubulavirus laryngotracheitidis": (E, "Human parainfluenza virus 2. Croup and upper respiratory illness in children."),
    "Orthorubulavirus hominis": (E, "Human parainfluenza virus 4A/4B. Mild to moderate respiratory illness."),
    "Respirovirus pneumoniae": (E, "Human parainfluenza virus 3. Bronchiolitis and pneumonia in infants."),
    "Respirovirus laryngotracheitidis": (E, "Human parainfluenza virus 1. Leading cause of croup."),
    "Metapneumovirus hominis": (E, "Human metapneumovirus. Bronchiolitis and pneumonia across all ages."),
    "Orthopneumovirus hominis": (E, "Human respiratory syncytial virus. Leading cause of infant bronchiolitis; also severe in older adults."),

    # --- Orthomyxoviridae -------------------------------------------------
    "Betainfluenzavirus influenzae": (E, "Influenza B virus. Seasonal influenza, disproportionately in children."),
    "Gammainfluenzavirus influenzae": (E, "Influenza C virus. Mild upper respiratory illness, mainly paediatric."),
    "Deltainfluenzavirus influenzae": (PO, "Influenza D virus. Seroreactivity in cattle-exposed workers; no confirmed human disease."),
    "Thogotovirus bourbonense": (E, "Bourbon virus. Tick-borne febrile illness with thrombocytopenia; fatal cases reported."),
    "Thogotovirus thogotoense": (PO, "Thogoto virus. Isolated case reports of human meningitis; causation unsettled."),
    "Thogotovirus dhoriense": (PO, "Dhori virus. Laboratory-acquired febrile illness reported; natural human disease unproven."),
    "Quaranjavirus quaranfilense": (PO, "Quaranfil virus. Isolated from febrile children; clinical significance unresolved."),

    # --- Picornaviridae ---------------------------------------------------
    "Enterovirus coxsackiepol": (E, "Includes poliovirus 1-3 and coxsackie A serotypes: poliomyelitis, herpangina, hand-foot-and-mouth disease."),
    "Enterovirus alphacoxsackie": (E, "Coxsackievirus A serotypes. Hand-foot-and-mouth disease, herpangina, aseptic meningitis."),
    "Enterovirus betacoxsackie": (E, "Coxsackievirus B and echoviruses. Myocarditis, pleurodynia, aseptic meningitis, neonatal sepsis."),
    "Enterovirus deconjuncti": (E, "Enterovirus D68 and D70. Severe respiratory illness with acute flaccid myelitis; epidemic conjunctivitis."),
    "Enterovirus alpharhino": (E, "Rhinovirus A. Common cold; asthma and COPD exacerbation."),
    "Enterovirus betarhino": (E, "Rhinovirus B. Common cold, generally milder than A or C."),
    "Enterovirus cerhino": (E, "Rhinovirus C. Common cold with a higher rate of lower respiratory involvement in children."),
    "Hepatovirus ahepa": (E, "Hepatitis A virus. Faecal-oral acute hepatitis; vaccine-preventable."),
    "Parechovirus ahumpari": (E, "Human parechovirus 1-6. Gastroenteritis and, as HPeV-3, neonatal sepsis and meningoencephalitis."),
    "Parechovirus beljungani": (PO, "Ljungan virus. Rodent virus with contested serological links to human disease."),
    "Cardiovirus saffoldi": (PR, "Saffold virus. Repeatedly recovered from children with respiratory and enteric illness; causation not settled."),
    "Kobuvirus aichi": (E, "Aichivirus A. Oyster-associated and travel-associated gastroenteritis."),
    "Salivirus aklasse": (PR, "Salivirus A. Detected in children with acute diarrhoea; association reported but not established."),
    "Cosavirus asiani": (PO, "Cosavirus A. Common in stool from both healthy and diarrhoeic children; significance unresolved."),

    # --- Caliciviridae / rotaviruses --------------------------------------
    "Norovirus norwalkense": (E, "Norwalk virus. The dominant cause of epidemic non-bacterial gastroenteritis worldwide."),
    "Sapovirus sapporoense": (E, "Sapporo virus. Acute gastroenteritis in children and in outbreak settings."),
    "Rotavirus alphagastroenteritidis": (E, "Rotavirus A. Leading cause of severe childhood diarrhoea; vaccine-preventable."),
    "Rotavirus betagastroenteritidis": (E, "Rotavirus B. Adult diarrhoea outbreaks, described chiefly in China."),
    "Rotavirus tritogastroenteritidis": (E, "Rotavirus C. Sporadic cases and family or school outbreaks of gastroenteritis."),
    "Rotavirus aspergastroenteritidis": (PO, "Rotavirus H. Detected in human stool in Asia; also porcine. Clinical role unresolved."),
    "Orthopicobirnavirus hominis": (PO, "Human picobirnavirus. Common in human stool; a bacterial rather than a human host is now suspected."),

    # --- Adenoviridae -----------------------------------------------------
    "Mastadenovirus caesari": (E, "Human adenovirus A/C types including HAdV-1, -2, -5. Respiratory illness and, in the immunocompromised, disseminated disease."),
    "Mastadenovirus blackbeardi": (E, "Human adenovirus B types including HAdV-3, -7, -11. Pneumonia, pharyngoconjunctival fever, haemorrhagic cystitis."),
    "Mastadenovirus dominans": (E, "Human adenovirus D types including HAdV-8, -19, -37. Epidemic keratoconjunctivitis."),
    "Mastadenovirus exoticum": (E, "Human adenovirus E, HAdV-4. Acute respiratory disease, notably in military recruits."),
    "Mastadenovirus faecale": (E, "Human adenovirus F, HAdV-40 and -41. Infantile gastroenteritis."),
    "Mastadenovirus russelli": (E, "Human adenovirus G, HAdV-52. Gastroenteritis."),

    # --- Orthoherpesviridae ------------------------------------------------
    "Simplexvirus humanalpha1": (E, "Herpes simplex virus 1. Orolabial and genital herpes, keratitis, encephalitis."),
    "Simplexvirus humanalpha2": (E, "Herpes simplex virus 2. Genital herpes and neonatal herpes."),
    "Simplexvirus macacinealpha1": (E, "Macacine alphaherpesvirus 1 (B virus). Rare but frequently fatal encephalomyelitis after macaque exposure."),
    "Varicellovirus humanalpha3": (E, "Varicella-zoster virus. Chickenpox and, on reactivation, shingles."),
    "Cytomegalovirus humanbeta5": (E, "Human cytomegalovirus. Congenital infection, and severe disease in transplant and HIV patients."),
    "Roseolovirus humanbeta6a": (E, "Human herpesvirus 6A. Human infection established; disease associations less clear than 6B."),
    "Roseolovirus humanbeta6b": (E, "Human herpesvirus 6B. Roseola infantum and febrile seizures."),
    "Roseolovirus humanbeta7": (E, "Human herpesvirus 7. Roseola-like illness and febrile seizures in infancy."),
    "Lymphocryptovirus humangamma4": (E, "Epstein-Barr virus. Infectious mononucleosis; Burkitt and nasopharyngeal carcinoma."),
    "Rhadinovirus humangamma8": (E, "Kaposi sarcoma-associated herpesvirus. Kaposi sarcoma, primary effusion lymphoma, multicentric Castleman disease."),

    # --- Papillomaviridae / Polyomaviridae --------------------------------
    "Alphapapillomavirus 9": (E, "Includes HPV-16. Cervical, anogenital and oropharyngeal carcinoma; vaccine-preventable."),
    "Alphapapillomavirus 7": (E, "Includes HPV-18. Cervical adenocarcinoma and other anogenital cancers."),
    "Alphapapillomavirus 10": (E, "Includes HPV-6 and -11. Anogenital warts and recurrent respiratory papillomatosis."),
    "Mupapillomavirus 1": (E, "HPV-1. Plantar and common warts."),
    "Betapolyomavirus hominis": (E, "BK polyomavirus. Polyomavirus-associated nephropathy and haemorrhagic cystitis after transplantation."),
    "Betapolyomavirus secuhominis": (E, "JC polyomavirus. Progressive multifocal leukoencephalopathy in immunosuppression."),
    "Alphapolyomavirus quintihominis": (E, "Merkel cell polyomavirus. Clonally integrated in most Merkel cell carcinomas."),
    "Alphapolyomavirus octihominis": (PR, "Trichodysplasia spinulosa polyomavirus. Associated with trichodysplasia spinulosa in immunosuppressed patients."),
    "Alphapolyomavirus nonihominis": (PO, "Human polyomavirus 9. Common human infection; no disease attributed."),
    "Alphapolyomavirus quardecihominis": (PO, "LI polyomavirus. Human infection reported; clinical significance unknown."),
    "Alphapolyomavirus terdecihominis": (PO, "New Jersey polyomavirus. Single case of vasculitis and myositis in an immunosuppressed patient."),
    "Betapolyomavirus quartihominis": (PO, "Human polyomavirus 6/7. Common skin colonisers; pruritic dermatoses reported in immunosuppression."),
    "Betapolyomavirus tertihominis": (PO, "Human polyomavirus 7. As above; disease attribution rare and uncertain."),

    # --- Hepatitis viruses -------------------------------------------------
    "Orthohepadnavirus hominoidei": (E, "Hepatitis B virus. Chronic hepatitis, cirrhosis, hepatocellular carcinoma; vaccine-preventable."),
    "Paslahepevirus balayani": (E, "Hepatitis E virus genotypes 1-4. Acute hepatitis; high mortality in pregnancy, chronic in the immunosuppressed."),
    "Orthohepacivirus hominis": (E, "Hepatitis C virus. Chronic hepatitis, cirrhosis and hepatocellular carcinoma; curable with direct-acting antivirals."),
    "Deltavirus italiense": (E, "Hepatitis D virus genotype 1, the globally distributed genotype. Requires HBV coinfection; accelerates progression to cirrhosis."),
    # HDV genotypes 2-8 are all human viruses, distinguished by geography and
    # by severity rather than by host. Leaving them unassessed implied they
    # were animal viruses.
    "Deltavirus japanense": (E, "Hepatitis D virus genotype 2. East Asia; generally milder course than genotype 1."),
    "Deltavirus peruense": (E, "Hepatitis D virus genotype 3. Amazon basin; associated with fulminant hepatitis in outbreaks."),
    "Deltavirus taiwanense": (E, "Hepatitis D virus genotype 4. Taiwan and Japan."),
    "Deltavirus togense": (E, "Hepatitis D virus genotype 5. West Africa; better interferon response reported."),
    "Deltavirus carense": (E, "Hepatitis D virus genotype 6. West and Central Africa."),
    "Deltavirus cameroonense": (E, "Hepatitis D virus genotype 7. Central Africa."),
    "Deltavirus senegalense": (E, "Hepatitis D virus genotype 8. West Africa and, through migration, South America."),
    "Rocahepevirus ratti": (E, "Rat hepatitis E virus (HEV-C1). Confirmed human hepatitis, first recognised in Hong Kong in 2018, mainly in immunocompromised and transplant patients; not detected by all HEV assays."),
    "Pegivirus hominis": (PO, "Human pegivirus 1 (GBV-C). Persistent human infection with no attributed disease; associated with slower HIV progression."),

    # --- Retroviridae ------------------------------------------------------
    "Lentivirus humimdef1": (E, "HIV-1. Progressive CD4 T-cell depletion and AIDS."),
    "Lentivirus humimdef2": (E, "HIV-2. AIDS with slower progression and lower transmissibility than HIV-1."),
    "Deltaretrovirus priTlym1": (E, "HTLV-1. Adult T-cell leukaemia/lymphoma and HTLV-1-associated myelopathy."),
    "Deltaretrovirus priTlym2": (PO, "HTLV-2. Established human infection; disease association limited and contested."),
    "Deltaretrovirus priTlym3": (PO, "HTLV-3. Human infection detected in central Africa; no disease described."),

    # --- Coronaviridae -----------------------------------------------------
    "Betacoronavirus pandemicum": (E, "SARS-CoV and SARS-CoV-2. SARS and COVID-19."),
    "Betacoronavirus cameli": (E, "MERS-CoV. Severe respiratory disease acquired from dromedary camels."),
    "Betacoronavirus gravedinis": (E, "Human coronavirus OC43. Common cold; occasional severe lower respiratory disease."),
    "Betacoronavirus hongkongense": (E, "Human coronavirus HKU1. Common cold and bronchiolitis."),
    "Alphacoronavirus chicagoense": (E, "Human coronavirus 229E. Common cold."),
    "Alphacoronavirus amsterdamense": (E, "Human coronavirus NL63. Common cold and croup in young children."),

    # --- Astroviridae / Parvoviridae ---------------------------------------
    "Mamastrovirus hominis": (E, "Human astrovirus 1-8. Paediatric gastroenteritis."),
    "Mamastrovirus homustovis": (PR, "Human astrovirus MLB/VA clades. Detected in gastroenteritis and in encephalitis cases in the immunocompromised."),
    "Erythroparvovirus primate1": (E, "Parvovirus B19. Fifth disease, transient aplastic crisis, hydrops fetalis."),
    "Bocaparvovirus primate1": (PR, "Human bocavirus 1. Frequently found in paediatric respiratory illness; causation debated given high co-detection."),
    "Bocaparvovirus primate2": (PO, "Human bocavirus 2-4. Enteric detection; clinical role unresolved."),
    "Protoparvovirus primate1": (PO, "Bufavirus. Detected in stool from children with diarrhoea; significance unresolved."),
    "Dependoparvovirus primate1": (NO, "Adeno-associated viruses. Near-universal human infection with no known disease; used as a gene-therapy vector."),

    # --- Orthoflavivirus ---------------------------------------------------
    "Orthoflavivirus flavi": (E, "Yellow fever virus. Viscerotropic haemorrhagic fever; vaccine-preventable."),
    "Orthoflavivirus nilense": (E, "West Nile virus. Febrile illness and neuroinvasive disease."),
    "Orthoflavivirus japonicum": (E, "Japanese encephalitis virus. Leading cause of vaccine-preventable encephalitis in Asia."),
    "Orthoflavivirus louisense": (E, "St. Louis encephalitis virus. Encephalitis outbreaks in the Americas."),
    "Orthoflavivirus murrayense": (E, "Murray Valley encephalitis virus. Encephalitis in Australia."),
    "Orthoflavivirus zilberi": (E, "Tick-borne encephalitis virus, Far Eastern and Siberian subtypes. Severe meningoencephalitis; vaccine-preventable."),
    "Orthoflavivirus neudoerflense": (E, "Tick-borne encephalitis virus, European subtype. Meningoencephalitis; vaccine-preventable."),
    "Orthoflavivirus kyasanurense": (E, "Kyasanur Forest disease and Alkhumra viruses. Tick-borne haemorrhagic fever."),
    "Orthoflavivirus omskense": (E, "Omsk haemorrhagic fever virus. Tick- and muskrat-associated haemorrhagic fever."),
    "Orthoflavivirus powassanense": (E, "Powassan virus and deer tick virus. Severe tick-borne encephalitis in North America."),
    "Orthoflavivirus usutuense": (PR, "Usutu virus. Human neuroinvasive cases and blood-donor seropositivity in Europe."),
    "Orthoflavivirus ilheusense": (PR, "Ilhéus and Rocio viruses. Rocio virus caused encephalitis epidemics in Brazil."),
    "Orthoflavivirus wesselsbronense": (PO, "Wesselsbron virus. Febrile illness in exposed and laboratory workers."),
    "Orthoflavivirus banziense": (PO, "Banzi virus. Isolated from a febrile child; rare."),
    "Orthoflavivirus zikaense": (E, "Zika virus. Congenital Zika syndrome and Guillain-Barré syndrome."),
    "Orthoflavivirus kedougouense": (PO, "Kédougou virus. Isolated from humans in West Africa; significance unclear."),
    "Orthoflavivirus bagazaense": (PO, "Bagaza virus (Israel turkey meningoencephalitis). Human seropositivity reported in India."),
    "Orthoflavivirus langatense": (PO, "Langat virus. Attenuated in humans; vaccine trials caused rare encephalitis."),
    "Orthoflavivirus apoiense": (PO, "Apoi virus. Rodent-borne; human seropositivity reported in Japan."),
    "Orthoflavivirus tembusu": (AO, "Tembusu virus. Duck pathogen of major veterinary importance; human infection unproven."),

    # --- Togaviridae / Matonaviridae ---------------------------------------
    "Alphavirus eastern": (E, "Eastern equine encephalitis virus. Rare but highly lethal encephalitis."),
    "Alphavirus madariaga": (PR, "Madariaga virus. South American EEE lineage; human encephalitis reported in Panama."),
    "Alphavirus western": (E, "Western equine encephalitis virus. Encephalitis in the Americas."),
    "Alphavirus venezuelan": (E, "Venezuelan equine encephalitis virus. Febrile illness and encephalitis in epidemics."),
    "Alphavirus mucambo": (PR, "Mucambo virus. VEE complex; sporadic human febrile illness."),
    "Alphavirus tonate": (PR, "Tonate virus. VEE complex; human encephalitis reported in French Guiana."),
    "Alphavirus everglades": (PR, "Everglades virus. VEE complex; human febrile illness in Florida."),
    "Alphavirus onyong": (E, "O'nyong-nyong virus. Large epidemics of fever, rash and arthralgia in Africa."),
    "Alphavirus rossriver": (E, "Ross River virus. Epidemic polyarthritis in Australia and the Pacific."),
    "Alphavirus barmah": (E, "Barmah Forest virus. Fever, rash and polyarthritis in Australia."),
    "Alphavirus mayaro": (E, "Mayaro virus. Febrile arthralgic illness in South America."),
    "Alphavirus semliki": (PO, "Semliki Forest virus. One fatal laboratory infection; natural human disease unproven."),
    "Alphavirus sindbis": (E, "Sindbis virus. Pogosta/Ockelbo disease: fever, rash and arthralgia."),
    "Alphavirus getah": (AO, "Getah virus. Disease in horses and pigs; human seropositivity without confirmed illness."),
    "Alphavirus una": (PO, "Una virus. Human seropositivity in South America; no confirmed disease."),
    "Rubivirus rubellae": (E, "Rubella virus. Rubella and congenital rubella syndrome; vaccine-preventable."),

    # --- Filoviridae / Arenaviridae ----------------------------------------
    "Orthoebolavirus zairense": (E, "Ebola virus. Ebola disease with high case fatality."),
    "Orthoebolavirus sudanense": (E, "Sudan virus. Ebola disease outbreaks in East Africa."),
    "Orthoebolavirus bundibugyoense": (E, "Bundibugyo virus. Ebola disease outbreaks in Uganda and DRC."),
    "Orthoebolavirus taiense": (PO, "Taï Forest virus. One non-fatal human infection after contact with a chimpanzee."),
    "Orthoebolavirus restonense": (AO, "Reston virus. Lethal in macaques and infects pigs; documented asymptomatic seroconversion in exposed human handlers but no human disease in over 30 years. Animal pathogen with proven human exposure, which is not the same as no human infection."),
    "Orthoebolavirus bombaliense": (NO, "Bombali virus. Bat virus; no human infection reported."),
    "Orthomarburgvirus marburgense": (E, "Marburg and Ravn viruses. Marburg disease with high case fatality."),
    "Cuevavirus lloviuense": (PO, "Lloviu virus. Bat filovirus; no confirmed human infection to date."),
    "Mammarenavirus lassaense": (E, "Lassa virus. Lassa fever; a leading cause of viral haemorrhagic fever in West Africa."),
    "Mammarenavirus choriomeningitidis": (E, "LCMV. Aseptic meningitis, congenital infection, and fatal transplant-transmitted disease."),
    "Mammarenavirus juninense": (E, "Junín virus. Argentine haemorrhagic fever; vaccine available."),
    "Mammarenavirus machupoense": (E, "Machupo virus. Bolivian haemorrhagic fever."),
    "Mammarenavirus guanaritoense": (E, "Guanarito virus. Venezuelan haemorrhagic fever."),
    "Mammarenavirus brazilense": (E, "Sabiá virus. Brazilian haemorrhagic fever; laboratory infections recorded."),
    "Mammarenavirus chapareense": (E, "Chapare virus. Bolivian haemorrhagic fever with nosocomial transmission."),
    "Mammarenavirus lujoense": (E, "Lujo virus. Nosocomial haemorrhagic fever outbreak in southern Africa."),
    "Mammarenavirus flexalense": (PO, "Flexal virus. Laboratory-acquired febrile illness."),
    "Mammarenavirus tacaribeense": (PO, "Tacaribe virus. One laboratory infection; natural human disease unproven."),
    "Mammarenavirus whitewaterense": (PO, "Whitewater Arroyo virus. Human cases reported in California but not confirmed virologically."),

    # --- Hantaviridae ------------------------------------------------------
    "Orthohantavirus hantanense": (E, "Hantaan virus. Haemorrhagic fever with renal syndrome."),
    "Orthohantavirus seoulense": (E, "Seoul virus. HFRS worldwide, including rat-breeder outbreaks."),
    "Orthohantavirus puumalaense": (E, "Puumala virus. Nephropathia epidemica, the mild European form of HFRS."),
    "Orthohantavirus dobravaense": (E, "Dobrava-Belgrade virus. HFRS in the Balkans and central Europe."),
    "Orthohantavirus sinnombreense": (E, "Sin Nombre virus. Hantavirus cardiopulmonary syndrome in North America."),
    "Orthohantavirus andesense": (E, "Andes virus. HCPS with documented person-to-person transmission."),
    "Orthohantavirus bayoui": (E, "Bayou virus. HCPS with prominent renal involvement in the southern USA."),
    "Orthohantavirus nigrorivense": (E, "Black Creek Canal virus. HCPS in Florida."),
    "Orthohantavirus chocloense": (E, "Choclo virus. HCPS and mild febrile illness in Panama."),
    "Orthohantavirus mamorense": (E, "Laguna Negra virus. HCPS in Paraguay and Bolivia."),
    "Orthohantavirus thailandense": (PO, "Thailand virus. Human seropositivity; disease association unconfirmed."),
    "Orthohantavirus tulaense": (PO, "Tula virus. Rare HFRS-like cases, mainly in immunocompromised patients."),
    "Orthohantavirus khabarovskense": (PO, "Khabarovsk virus. Human seropositivity reported; no confirmed disease."),
    "Orthohantavirus prospectense": (NO, "Prospect Hill virus. Seroconversion in mammalogists without illness."),

    # --- Nairoviridae / Phenuiviridae --------------------------------------
    "Orthonairovirus haemorrhagiae": (E, "Crimean-Congo haemorrhagic fever virus. Tick-borne haemorrhagic fever with nosocomial spread."),
    "Orthonairovirus dugbeense": (PO, "Dugbe virus. Mild febrile illness and thrombocytopenia reported."),
    "Orthonairovirus erveense": (PO, "Erve virus. Associated with thunderclap headache in France; unconfirmed."),
    "Orthonairovirus nairobiense": (PO, "Nairobi sheep disease virus. Febrile illness in a few exposed people."),
    "Orthonairovirus kasokeroense": (PR, "Kasokero virus. Laboratory and bat-exposure febrile illness in Uganda."),
    "Orthonairovirus issykkulense": (PO, "Issyk-Kul virus. Outbreaks of febrile illness attributed in central Asia."),
    "Orthonairovirus songlingense": (PR, "Songling virus. Febrile illness with headache reported in north-eastern China."),
    "Orthonairovirus tachengense": (PR, "Tacheng tick virus 1. Human febrile cases reported in Xinjiang."),
    "Phlebovirus riftense": (E, "Rift Valley fever virus. Febrile illness, retinitis, encephalitis and haemorrhagic fever."),
    "Phlebovirus toscanaense": (E, "Toscana virus. A leading cause of summer meningitis in the Mediterranean."),
    "Phlebovirus napoliense": (E, "Sandfly fever Naples virus. Three-day fever."),
    "Phlebovirus siciliaense": (E, "Sandfly fever Sicilian virus. Three-day fever."),
    "Phlebovirus adanaense": (PO, "Adana virus. Human seropositivity in Turkey."),
    "Phlebovirus toroense": (E, "Punta Toro virus. Febrile illness in Panama and Colombia."),
    "Phlebovirus alenquerense": (PO, "Alenquer virus. Febrile illness in Amazonia."),
    "Phlebovirus candiruense": (PO, "Candiru virus. Febrile illness in Brazil."),
    "Phlebovirus chagresense": (PO, "Chagres virus. Febrile illness in Panama."),
    "Phlebovirus salehabadense": (PO, "Salehabad virus. Human seropositivity in Iran and Europe."),
    "Bandavirus dabieense": (E, "SFTS virus. Severe fever with thrombocytopenia syndrome, with nosocomial transmission."),
    "Bandavirus heartlandense": (E, "Heartland virus. Tick-borne febrile illness with leukopenia in the USA."),
    "Bandavirus bhanjanagarense": (PO, "Bhanja virus. Febrile illness and meningoencephalitis reported."),
    "Uukuvirus uukuniemiense": (NO, "Uukuniemi virus. Bird- and tick-associated; no human disease."),

    # --- Peribunyaviridae (beyond the curated Simbu profiles) -------------
    "Orthobunyavirus bunyamweraense": (E, "Bunyamwera virus. Febrile illness with rash and arthralgia in Africa."),
    "Orthobunyavirus lacrosseense": (E, "La Crosse virus. Paediatric encephalitis in the USA."),
    "Orthobunyavirus jamestownense": (E, "Jamestown Canyon virus. Febrile illness and meningoencephalitis."),
    "Orthobunyavirus encephalitidis": (E, "California encephalitis virus. The namesake of the serogroup."),
    "Orthobunyavirus tahynaense": (E, "Tahyna virus. Valtice fever: influenza-like illness in Europe."),
    "Orthobunyavirus guaroaense": (E, "Guaroa virus. Febrile illness in Central and South America."),
    "Orthobunyavirus ileshaense": (E, "Ilesha virus. Febrile illness, rash and occasional haemorrhage in Africa."),
    "Orthobunyavirus bwambaense": (E, "Bwamba virus. Common cause of undifferentiated fever in East Africa."),
    "Orthobunyavirus caraparuense": (E, "Caraparú virus. Febrile illness in Amazonia."),
    "Orthobunyavirus maritubaense": (E, "Marituba virus. Febrile illness in Amazonia."),
    "Orthobunyavirus madridense": (E, "Madrid virus. Febrile illness in Panama."),
    "Orthobunyavirus apeuense": (E, "Apeú virus. Febrile illness in Brazil."),
    "Orthobunyavirus oribocaense": (E, "Oriboca, Murutucú and Restan viruses. Febrile illness in Amazonia and the Caribbean."),
    "Orthobunyavirus nepuyoi": (PO, "Nepuyo virus. Human febrile cases reported in Central America."),
    "Orthobunyavirus guamaense": (PO, "Guamá virus. Human isolations in Brazil; significance unclear."),
    "Orthobunyavirus tacaiumaense": (PO, "Tacaiuma virus. Febrile illness in Amazonia."),
    "Orthobunyavirus wyeomyiae": (PO, "Wyeomyia virus. Mild febrile illness in South America."),
    "Orthobunyavirus maguariense": (PO, "Maguari virus. Rare human febrile illness."),
    "Orthobunyavirus bataiense": (PO, "Batai virus. Human seropositivity across Eurasia; rare febrile illness."),
    "Orthobunyavirus keystoneense": (PO, "Keystone virus. One confirmed human infection in Florida."),
    "Orthobunyavirus northwayense": (PO, "Northway virus. Human seropositivity in Alaska."),
    "Orthobunyavirus akabaneense": (AO, "Akabane virus. Major cause of bovine congenital arthrogryposis-hydranencephaly; no human disease."),
    "Orthobunyavirus schmallenbergense": (AO, "Schmallenberg virus. Ruminant congenital malformations; human exposure studies negative."),

    # --- Reoviridae relatives -----------------------------------------------
    "Coltivirus ixodis": (E, "Eyach virus. Tick-borne; associated with meningopolyneuritis in Europe."),
    "Coltivirus kundalense": (PO, "Kundal virus. Detected in tick-exposed patients in India."),
    "Seadornavirus bannaense": (PR, "Banna virus. Isolated from patients with encephalitis and fever in China."),
    "Orbivirus orungoense": (PR, "Orungo virus. Febrile illness in West Africa."),
    "Orbivirus lebomboense": (PO, "Lebombo virus. One human isolation in Nigeria."),
    "Orbivirus changuinolaense": (PO, "Changuinola virus. Febrile illness in Panama."),
    "Orbivirus ruminantium": (AO, "Bluetongue virus. Major ruminant pathogen; no human disease."),

    # --- Poxviridae ---------------------------------------------------------
    "Orthopoxvirus variola": (E, "Variola virus. Smallpox; declared eradicated in 1980."),
    "Orthopoxvirus vaccinia": (E, "Vaccinia virus. Vaccine strain; causes progressive vaccinia, eczema vaccinatum and buffalopox."),
    "Orthopoxvirus cowpox": (E, "Cowpox virus. Localised ulcerating lesions, usually from cats; severe in the immunocompromised."),
    "Orthopoxvirus akhmetapox": (PR, "Akhmeta virus. Human skin lesions reported in Georgia."),
    "Orthopoxvirus abatinomacacapox": (PO, "Abatino macacapox virus. Zoonotic potential inferred from related orthopoxviruses."),
    "Orthopoxvirus taterapox": (NO, "Taterapox virus. Gerbil virus; no human infection reported."),
    "Orthopoxvirus raccoonpox": (NO, "Raccoonpox virus. No human disease reported."),
    "Orthopoxvirus volepox": (NO, "Volepox virus. No human disease reported."),
    "Orthopoxvirus skunkpox": (NO, "Skunkpox virus. No human disease reported."),
    "Orthopoxvirus ectromelia": (AO, "Ectromelia virus. Mousepox; a major laboratory-animal pathogen."),
    "Orthopoxvirus camelpox": (PO, "Camelpox virus. Rare skin lesions in camel handlers."),
    "Parapoxvirus orf": (E, "Orf virus. Contagious pustular dermatitis; occupational hand lesions in sheep handlers."),
    "Parapoxvirus pseudocowpox": (E, "Pseudocowpox virus. Milker's nodule."),
    "Parapoxvirus bovinestomatitis": (E, "Bovine papular stomatitis virus. Occupational hand lesions."),
    "Parapoxvirus sealpox": (E, "Sealpox virus. Occupational nodular skin lesions in seal handlers."),
    "Parapoxvirus reddeerpox": (PO, "Red deerpox virus. Human infection plausible by analogy; not reported."),
    "Molluscipoxvirus molluscum": (E, "Molluscum contagiosum virus. Umbilicated papules, common in children and in HIV."),
    "Yatapoxvirus tanapox": (E, "Tanapox and Yaba-like disease viruses. Febrile illness with a nodular skin lesion."),
    "Yatapoxvirus yabapox": (PO, "Yaba monkey tumour virus. Subcutaneous tumours in primates; human infection rare."),

    # --- Rhabdoviridae ------------------------------------------------------
    "Lyssavirus australis": (E, "Australian bat lyssavirus. Rabies-like fatal encephalitis."),
    "Lyssavirus duvenhage": (E, "Duvenhage virus. Fatal rabies-like encephalitis after bat contact."),
    "Lyssavirus mokola": (E, "Mokola virus. Rabies-like fatal encephalitis; human cases reported in Nigeria and Zimbabwe. Critically, it is not neutralised by rabies vaccine-induced antibody, so standard post-exposure prophylaxis cannot be relied on."),
    "Lyssavirus hamburg": (E, "European bat lyssavirus 1. Fatal rabies-like encephalitis."),
    "Lyssavirus helsinki": (E, "European bat lyssavirus 2. Fatal rabies-like encephalitis in bat handlers."),
    "Lyssavirus irkut": (E, "Irkut virus. Fatal human encephalitis reported in Russia and China."),
    "Lyssavirus caucasicus": (PR, "West Caucasian bat virus. No human case; vaccine escape makes exposure consequential."),
    "Lyssavirus gannoruwa": (PO, "Gannoruwa bat lyssavirus. Bat virus in Sri Lanka; no human case."),
    "Vesiculovirus indiana": (E, "Vesicular stomatitis Indiana virus. Influenza-like illness in exposed livestock and laboratory workers."),
    "Vesiculovirus newjersey": (E, "Vesicular stomatitis New Jersey virus. Influenza-like occupational illness."),
    "Vesiculovirus chandipura": (E, "Chandipura virus. Outbreaks of acute encephalitis with high mortality in Indian children."),
    "Vesiculovirus isfahan": (PO, "Isfahan virus. Human seropositivity in Iran."),
    "Vesiculovirus piry": (PO, "Piry virus. Laboratory-acquired febrile illness in Brazil."),
    "Vesiculovirus alagoas": (PO, "VSV Alagoas. Human febrile illness reported in Brazil."),
    "Ledantevirus kern": (PR, "Kern Canyon-related; Oita/Fikirini group bat rhabdoviruses with sparse human data."),

    # --- Anelloviridae (ubiquitous, no attributed disease) ------------------
    "Alphatorquevirus": (PO, "Torque teno viruses. Near-universal lifelong human infection with no disease attributed; used as a marker of immune competence."),
    "Betatorquevirus": (PO, "Torque teno mini viruses. Ubiquitous human infection; no attributed disease."),
    "Gammatorquevirus": (PO, "Torque teno midi viruses. Ubiquitous human infection; no attributed disease."),
}

# Genus-level fallbacks, for genera holding dozens of near-identical species
# where naming each one adds nothing. The epithet prefixes matter: the
# anellovirus genera contain simian, porcine and canine species alongside the
# human ones, and sweeping the whole genus in labelled simian torque teno
# viruses as human-associated.
GENUS_REFERENCE = {
    "Alphatorquevirus": (("homin",), REFERENCE["Alphatorquevirus"]),
    "Betatorquevirus": (("homini",), REFERENCE["Betatorquevirus"]),
    "Gammatorquevirus": (("homidi",), REFERENCE["Gammatorquevirus"]),
}


def _genus_hit(species, genus):
    """A genus fallback, but only for the species epithets it is meant for."""
    rule = GENUS_REFERENCE.get(genus)
    if not rule:
        return None
    prefixes, entry = rule
    epithet = species.split(" ", 1)[-1].lower()
    return entry if epithet.startswith(prefixes) else None

# --------------------------------------------------------------------------
# Host range
# --------------------------------------------------------------------------

# ICTV "Host source" values that mean a human infection is at least on the
# table. Anything else -- plants, bacteria, archaea, fungi, algae, protists,
# invertebrates alone -- supports a real "no human evidence" claim.
VERTEBRATE_HOSTS = ("vertebrates", "human", "mammal", "bird")

_HUMAN_SOURCE = re.compile(
    r"\bhuman\b|\bhomo sapiens\b|\bpatient\b|\bhominis\b", re.I)


def host_is_vertebrate(host):
    h = (host or "").lower()
    return any(k in h for k in VERTEBRATE_HOSTS)


def isolates_name_humans(names):
    """True when the ICTV record's own isolate names point at human sources."""
    return any(_HUMAN_SOURCE.search(n or "") for n in names)


def classify(species, genus, host, isolate_names):
    """Resolve (tier, basis, note) for a species with no curated profile.

    Order matters: an explicit reference entry beats a name-derived guess,
    which beats a host-range argument, which beats admitting we do not know.
    """
    hit = REFERENCE.get(species) or _genus_hit(species, genus)
    if hit:
        return hit[0], "reference", hit[1]

    vertebrate = host_is_vertebrate(host)

    if vertebrate and isolates_name_humans(isolate_names):
        return PO, "vmr-name", (
            "The ICTV record names human-derived isolates for this species, so "
            "human infection has been recorded. No assessment of disease "
            "causation has been made here.")

    if not vertebrate:
        return NO, "host-range", (
            f"ICTV records the host range as “{host or 'unknown'}”, with no "
            "vertebrate host, so human infection is not expected.")

    return "unassessed", "none", (
        "Not assessed. This species has no curated profile here and no "
        "human-derived isolate in the ICTV record — which is not the same as "
        "evidence against human infection.")
