"""Entry receptors, attachment factors and cell tropism.

Why a virologist wants this
---------------------------
Receptor use explains more about a virus than almost any other single fact:
which cells it infects, which species it can infect at all, what limits
spillover, and what a blocking antibody or entry inhibitor has to target.
Measles' use of SLAM on activated lymphocytes explains its immunosuppression;
influenza's α2,3 vs α2,6 sialic-acid preference explains why avian viruses
bind human conjunctiva and lower airway but transmit poorly; ACE2 distribution
explains SARS-CoV-2 tropism.

None of this is in ICTV, so it is curated, keyed by ICTV binomial, and
deliberately incomplete rather than padded out with guesses.

Fields
------
  receptors   the entry receptor(s), with the protein name used in the
              literature. Several viruses use more than one.
  attachment  low-affinity attachment factors that concentrate virus at the
              surface without triggering entry -- worth separating, because
              they are often confused with receptors.
  tropism     which cells and tissues, in the order that matters clinically
  entry       how the membrane is crossed: pH-dependent endosomal fusion,
              direct fusion at the plasma membrane, endocytosis + escape
  note        the consequence -- why the receptor explains the disease
"""


def _r(species, **kw):
    RECEPTORS[species] = kw


RECEPTORS = {}

# --- Paramyxoviridae / Pneumoviridae ------------------------------------
_r("Morbillivirus hominis",
   receptors=["SLAM / CD150 (signalling lymphocyte activation molecule)",
              "Nectin-4 (PVRL4)"],
   attachment=["CD46 (vaccine and laboratory-adapted strains only)"],
   tropism="Activated T and B cells, dendritic cells and alveolar macrophages "
           "first (SLAM); then basolateral airway epithelium (nectin-4) for "
           "shedding into the lumen.",
   entry="Direct fusion at the plasma membrane, pH-independent, via the H and "
         "F glycoproteins.",
   note="The two-receptor sequence explains measles precisely: SLAM entry into "
        "immune memory cells causes the profound lymphopenia and 'immune "
        "amnesia' that drives post-measles mortality, while nectin-4 on the "
        "basolateral epithelial surface explains why a systemic infection "
        "ends up as the most transmissible respiratory virus known. CD46 use "
        "by vaccine strains is an artefact of Vero adaptation, not wild-type "
        "biology.")

_r("Henipavirus nipahense",
   receptors=["Ephrin-B2", "Ephrin-B3"],
   tropism="Endothelium of small vessels, neurons, and respiratory epithelium.",
   entry="Direct fusion at the plasma membrane via G and F.",
   note="Ephrin-B2/B3 are extraordinarily conserved across mammals, which is "
        "why Nipah crosses species barriers so easily and why its host range "
        "is so wide. Ephrin-B3 expression in brainstem neurons matches the "
        "encephalitis, and endothelial ephrin-B2 the vasculitis.")

_r("Henipavirus hendraense", receptors=["Ephrin-B2", "Ephrin-B3"],
   tropism="Vascular endothelium and neurons.",
   entry="Direct plasma-membrane fusion.",
   note="Same receptors as Nipah, hence the same vasculitis-and-encephalitis "
        "picture acquired from horses.")

_r("Orthopneumovirus hominis",
   receptors=["Nucleolin", "CX3CR1 (fractalkine receptor)"],
   attachment=["Heparan sulfate (cultured cells; minor in vivo)",
               "Surfactant protein A"],
   tropism="Ciliated apical airway epithelium; syncytium formation.",
   entry="Fusion at the plasma membrane or via macropinocytosis, driven by F.",
   note="CX3CR1 on ciliated cells is the physiological receptor; heparan "
        "sulfate dominates in immortalised cell lines and misled early tropism "
        "work. The prefusion F conformation is the target of both nirsevimab "
        "and the licensed older-adult vaccines.")

# --- Orthomyxoviridae ----------------------------------------------------
_r("Alphainfluenzavirus influenzae",
   receptors=["Sialic acid, α2,6-linked (human airway)",
              "Sialic acid, α2,3-linked (avian enteric and human lower airway)"],
   tropism="Human: α2,6 on upper airway epithelium. Avian viruses prefer α2,3, "
           "found on human type II pneumocytes, alveolar macrophages and "
           "conjunctiva.",
   entry="Clathrin-mediated endocytosis, then low-pH-triggered HA2 fusion; M2 "
         "acidifies the virion to release the ribonucleoprotein.",
   note="This single preference governs pandemic risk. H5N1 binds α2,3 in the "
        "human deep lung and conjunctiva, which explains severe pneumonia, "
        "conjunctivitis in dairy-outbreak cases, and poor human-to-human "
        "transmission: there is little α2,3 in the upper airway for exhaled "
        "droplets to come from. A switch to α2,6 is the change surveillance "
        "watches for.")

_r("Betainfluenzavirus influenzae", receptors=["Sialic acid, α2,6-linked"],
   tropism="Upper and lower respiratory epithelium.",
   entry="Endosomal, low-pH HA-mediated fusion.",
   note="No animal reservoir of consequence, so no reassortment-driven "
        "antigenic shift — influenza B drifts but does not cause pandemics.")

# --- Coronaviridae -------------------------------------------------------
_r("Betacoronavirus pandemicum",
   receptors=["ACE2 (angiotensin-converting enzyme 2)"],
   attachment=["Heparan sulfate", "Neuropilin-1", "AXL"],
   tropism="Nasal ciliated epithelium, type II pneumocytes, enterocytes, "
           "vascular endothelium, renal tubules.",
   entry="Two routes: TMPRSS2-mediated cleavage and fusion at the plasma "
         "membrane, or cathepsin-L-dependent endosomal fusion. The furin site "
         "at S1/S2 pre-activates spike.",
   note="ACE2 distribution maps onto the clinical syndrome — anosmia, "
        "pneumonia, diarrhoea, thrombosis, renal injury. Which of the two "
        "entry routes dominates is cell-type dependent and shifted with "
        "Omicron toward the endosomal route, which tracks its more "
        "upper-airway, less pneumotropic behaviour.")

_r("Betacoronavirus cameli", receptors=["DPP4 / CD26"],
   tropism="Lower respiratory epithelium and type II pneumocytes; little "
           "upper-airway expression in humans.",
   entry="TMPRSS2 or cathepsin-dependent fusion after spike cleavage.",
   note="DPP4 in humans is abundant in the deep lung but sparse in the upper "
        "airway, which is exactly why MERS is severe when it takes and yet "
        "transmits badly outside hospitals.")

_r("Alphacoronavirus chicagoense", receptors=["APN / CD13 (aminopeptidase N)"],
   tropism="Upper respiratory epithelium.",
   entry="Endosomal fusion.",
   note="A common-cold coronavirus; APN use and upper-airway restriction keep "
        "it mild in the immunocompetent.")

_r("Alphacoronavirus amsterdamense", receptors=["ACE2"],
   tropism="Upper airway, with croup in young children.",
   entry="Endosomal fusion.",
   note="Uses the same receptor as SARS-CoV-2 but a quite different spike, and "
        "causes trivial disease — a useful corrective to the idea that the "
        "receptor alone determines severity.")

# --- Retroviridae --------------------------------------------------------
_r("Lentivirus humimdef1",
   receptors=["CD4 (primary receptor)",
              "CCR5 (R5 tropic, transmitted founder viruses)",
              "CXCR4 (X4 tropic, later in disease)"],
   tropism="CD4+ T cells, macrophages, dendritic cells, microglia.",
   entry="Direct fusion at the plasma membrane after CD4 binding exposes the "
         "coreceptor-binding site and releases gp41.",
   note="The coreceptor switch is clinically central: CCR5-tropic viruses "
        "dominate transmission, which is why CCR5-Δ32 homozygotes resist "
        "infection, why maraviroc works only against R5 virus, and why the "
        "Berlin and London cures used CCR5-Δ32 donor marrow. X4 emergence "
        "marks accelerated CD4 decline.")

_r("Deltaretrovirus priTlym1",
   receptors=["GLUT1", "Neuropilin-1", "Heparan sulfate proteoglycan"],
   tropism="CD4+ T cells, infected by cell-to-cell contact.",
   entry="Fusion at cell-cell contacts; free virions are poorly infectious.",
   note="HTLV-1 spreads almost entirely cell-to-cell through a virological "
        "synapse and biofilm, so plasma viral load is low and transmission "
        "requires cellular material — breastfeeding, transfusion of cellular "
        "products, sexual contact.")

# --- Flaviviridae / Togaviridae -----------------------------------------
_r("Orthoflavivirus denguei",
   receptors=["DC-SIGN (CD209)", "Mannose receptor (CD206)",
              "TIM/TAM phosphatidylserine receptors"],
   attachment=["Heparan sulfate", "Fcγ receptors during ADE"],
   tropism="Dermal dendritic cells first, then monocytes, macrophages and "
           "liver; endothelium is affected largely without infection.",
   entry="Clathrin-mediated endocytosis, low-pH E-mediated fusion.",
   note="No single high-affinity receptor is established, which matters: entry "
        "via Fcγ receptors on monocytes during antibody-dependent enhancement "
        "is the mechanism behind severe secondary dengue, and is why both "
        "licensed vaccines are restricted by serostatus.")

_r("Orthoflavivirus zikaense",
   receptors=["AXL", "TIM-1", "DC-SIGN"],
   tropism="Dermal fibroblasts and keratinocytes, neural progenitor cells, "
           "placental cytotrophoblasts and Hofbauer cells, testis, retina.",
   entry="Endocytosis then low-pH fusion.",
   note="AXL is highly expressed on radial glial neural progenitors and on "
        "placental cells, which is the clearest mechanistic link to "
        "microcephaly and congenital Zika syndrome — though AXL knockouts "
        "remain infectible, so it is facilitating rather than strictly "
        "required.")

_r("Orthoflavivirus flavi", receptors=["DC-SIGN", "Glycosaminoglycans"],
   tropism="Dendritic cells, then hepatocytes, myocardium and kidney.",
   entry="Endosomal fusion.",
   note="Hepatocyte tropism gives the jaundice and coagulopathy that make "
        "yellow fever viscerotropic rather than simply febrile.")

_r("Alphavirus chikungunya", receptors=["MXRA8 (DC-STAMP)"],
   attachment=["Heparan sulfate", "Glycosaminoglycans"],
   tropism="Fibroblasts, synovial tissue, muscle, skin; not neurotropic in "
           "adults.",
   entry="Clathrin-mediated endocytosis, low-pH E1 fusion.",
   note="MXRA8 is expressed on joint fibroblasts, synovium and osteoblasts — a "
        "direct explanation for the months-to-years polyarthralgia that makes "
        "chikungunya distinctive among arboviral fevers.")

_r("Rubivirus rubellae", receptors=["MOG (myelin oligodendrocyte glycoprotein)"],
   tropism="Respiratory epithelium, then placenta and fetal tissues.",
   entry="Endosomal, low-pH E1-mediated fusion.",
   note="Placental and fetal tropism in the first trimester produces congenital "
        "rubella syndrome; maternal infection after 20 weeks rarely does.")

# --- Picornaviridae ------------------------------------------------------
_r("Enterovirus coxsackiepol", receptors=["CD155 / PVR (poliovirus receptor)"],
   tropism="Intestinal epithelium and lymphoid tissue, then anterior horn "
           "motor neurons.",
   entry="CD155 binding triggers uncoating at the membrane or in early "
         "endosomes.",
   note="CD155 expression on motor neurons explains the paralysis, and its "
        "absence in most mammals is why transgenic CD155 mice had to be made "
        "to model poliomyelitis.")

_r("Enterovirus betacoxsackie",
   receptors=["CAR (coxsackie-adenovirus receptor)", "DAF / CD55"],
   tropism="Cardiac myocytes, pancreas, meninges.",
   entry="Receptor-mediated endocytosis and uncoating.",
   note="CAR on cardiomyocytes is the basis of enteroviral myocarditis and "
        "dilated cardiomyopathy.")

_r("Enterovirus alpharhino", receptors=["ICAM-1 (major group)", "LDLR (minor group)"],
   tropism="Upper airway epithelium; replicates best at 33–35 °C.",
   entry="Endocytosis; ICAM-1 binding destabilises the capsid.",
   note="Temperature optimum plus ICAM-1 distribution confine rhinovirus A/B "
        "to the nose and throat. Rhinovirus C uses CDHR3 instead, is not "
        "temperature-restricted in the same way, and reaches the lower airway "
        "— which is why it dominates asthma exacerbations in children.")

_r("Enterovirus cerhino", receptors=["CDHR3 (cadherin-related family member 3)"],
   tropism="Ciliated lower as well as upper airway epithelium.",
   entry="Endocytosis.",
   note="The CDHR3 rs6967330 asthma-risk allele increases surface expression "
        "and rhinovirus C binding — one of the cleanest host-genetics-to-virus "
        "links in respiratory medicine.")

_r("Hepatovirus ahepa", receptors=["Gangliosides (GD1a and related)"],
   attachment=["HAVCR1 / TIM-1 (for quasi-enveloped particles)"],
   tropism="Hepatocytes.",
   entry="Endolysosomal; gangliosides act in the lysosome rather than at the "
         "plasma membrane.",
   note="HAV circulates both naked and cloaked in host membrane "
        "(quasi-enveloped), which lets it evade neutralising antibody while "
        "remaining acid-stable enough for faecal-oral spread.")

# --- Herpesviruses -------------------------------------------------------
_r("Simplexvirus humanalpha1",
   receptors=["Nectin-1 (PVRL1)", "HVEM (TNFRSF14)", "3-O-sulfated heparan sulfate"],
   attachment=["Heparan sulfate"],
   tropism="Mucosal epithelium, then sensory neurons of the trigeminal "
           "ganglion where latency is established.",
   entry="gD binding plus the gB/gH-gL core fusion machinery; plasma-membrane "
         "fusion in neurons, endocytic in some epithelia.",
   note="Nectin-1 at neuronal junctions is what gives HSV access to axon "
        "terminals, hence lifelong ganglionic latency and recurrence at the "
        "same dermatome.")

_r("Varicellovirus humanalpha3",
   receptors=["Insulin-degrading enzyme (IDE)", "Myelin-associated glycoprotein"],
   attachment=["Heparan sulfate"],
   tropism="T cells (which carry it to skin), keratinocytes, dorsal root "
           "ganglia.",
   entry="gB/gH-gL fusion after gE-mediated attachment.",
   note="T-cell-mediated spread to skin explains the diffuse exanthem of "
        "chickenpox, and dorsal-root latency the dermatomal distribution of "
        "zoster decades later.")

_r("Lymphocryptovirus humangamma4",
   receptors=["CD21 (CR2) with HLA class II for B cells",
              "Ephrin receptor A2 for epithelial cells"],
   tropism="B lymphocytes and oropharyngeal epithelium.",
   entry="gp350/CD21 attachment, then gH/gL/gp42-mediated fusion; gp42 is "
         "required for B cells and inhibitory for epithelium.",
   note="The gp42 switch means virus made in B cells preferentially infects "
        "epithelium and vice versa — an elegant mechanism for shuttling "
        "between the two compartments, and the basis of lifelong carriage.")

_r("Cytomegalovirus humanbeta5",
   receptors=["PDGFRα (fibroblasts)", "Neuropilin-2 with CD147 (epithelium, "
              "endothelium, via the pentamer)"],
   tropism="Fibroblasts, endothelium, epithelium, monocytes, placental "
           "trophoblast.",
   entry="Trimer gH/gL/gO for fibroblasts; pentamer gH/gL/UL128-130-131 for "
         "epithelial, endothelial and myeloid cells.",
   note="The trimer/pentamer distinction is why laboratory strains passaged on "
        "fibroblasts lose the pentamer and epithelial tropism, and why "
        "pentamer-containing immunogens are central to congenital CMV vaccine "
        "efforts.")

# --- Filoviridae / Arenaviridae / Bunyavirales --------------------------
_r("Orthoebolavirus zairense",
   receptors=["NPC1 (Niemann-Pick C1), intracellular"],
   attachment=["TIM-1", "DC-SIGN", "integrin β1", "TAM receptors"],
   tropism="Monocytes, macrophages, dendritic cells, then hepatocytes, "
           "adrenal cortex and endothelium.",
   entry="Macropinocytosis, then cathepsin B/L cleavage of GP exposes the "
         "receptor-binding site for NPC1 in late endosomes.",
   note="The receptor is intracellular, so nothing binds Ebola at the cell "
        "surface in a blockable way — one reason entry inhibitors have been "
        "hard, and why the successful therapeutics are monoclonals against GP "
        "(ansuvimab, the REGN-EB3 cocktail).")

_r("Orthomarburgvirus marburgense", receptors=["NPC1, intracellular"],
   attachment=["TIM-1", "DC-SIGN"],
   tropism="Mononuclear phagocytes, hepatocytes, endothelium.",
   entry="Macropinocytosis and cathepsin-dependent late-endosomal fusion.",
   note="Same NPC1 dependence as Ebola, with no licensed countermeasure.")

_r("Mammarenavirus lassaense",
   receptors=["LAMP1 (intracellular, after switch)", "α-dystroglycan (surface)"],
   tropism="Dendritic cells, macrophages, endothelium, placenta.",
   entry="α-dystroglycan binding, endocytosis, then a pH-dependent switch to "
         "LAMP1 in the late endosome.",
   note="The two-receptor hand-off is unusual and explains why Old World "
        "arenaviruses need an acidified compartment; New World haemorrhagic "
        "fever arenaviruses instead use transferrin receptor 1, and human "
        "TfR1 compatibility is what makes Junín, Machupo, Guanarito, Sabiá and "
        "Chapare human pathogens while their relatives are not.")

_r("Mammarenavirus juninense", receptors=["Transferrin receptor 1 (TfR1)"],
   tropism="Macrophages, dendritic cells, endothelium.",
   entry="Receptor-mediated endocytosis, low-pH fusion.",
   note="Use of human TfR1 is the molecular basis of pathogenicity for the "
        "South American haemorrhagic fever arenaviruses — a single receptor "
        "preference separating lethal viruses from harmless relatives.")

_r("Orthohantavirus sinnombreense",
   receptors=["Integrin β3 (αvβ3)", "Decay-accelerating factor"],
   attachment=["Protocadherin-1 (PCDH1) on lung endothelium"],
   tropism="Pulmonary microvascular endothelium.",
   entry="Endocytosis and low-pH Gc-mediated fusion.",
   note="PCDH1 dependence on lung endothelium is a strong explanation for "
        "hantavirus cardiopulmonary syndrome: the capillary leak is driven by "
        "endothelial dysfunction, largely without cytopathology.")

# --- Poxviridae / Papillomaviridae / Polyomaviridae / Hepadnaviridae ----
_r("Orthopoxvirus monkeypox",
   receptors=["No single protein receptor identified"],
   attachment=["Glycosaminoglycans", "Laminin"],
   tropism="Keratinocytes, dermis, mucosa, lymphoid tissue.",
   entry="Either plasma-membrane fusion or low-pH endosomal entry, using an "
         "11-protein entry-fusion complex.",
   note="Poxviruses deliberately avoid dependence on one receptor, binding "
        "ubiquitous matrix components instead, which is part of why their host "
        "and cell range is so broad.")

_r("Alphapapillomavirus 9",
   receptors=["Heparan sulfate proteoglycans, then a secondary receptor "
              "after furin cleavage of L2"],
   attachment=["Laminin-332 in basement membrane"],
   tropism="Basal keratinocytes of squamous and transformation-zone "
           "epithelium, reached through a microwound.",
   entry="Slow, multi-hour: HSPG binding, conformational change, L2 cleavage, "
         "endocytosis, and nuclear delivery that requires mitosis.",
   note="Entry needs access to the basal layer and a dividing cell, which is "
        "why HPV targets the cervical transformation zone and why the "
        "prophylactic vaccines, acting on L1 before basement-membrane "
        "engagement, are so effective.")

_r("Betapolyomavirus secuhominis",
   receptors=["Serotonin receptor 5-HT2A", "GT1b / lactoseries "
              "tetrasaccharide c glycans"],
   tropism="Renal tubular epithelium; oligodendrocytes and astrocytes in the "
           "brain.",
   entry="Clathrin-mediated endocytosis.",
   note="Oligodendrocyte tropism gives progressive multifocal "
        "leukoencephalopathy; the dependence on immunosuppression explains why "
        "PML follows natalizumab, rituximab and advanced HIV.")

_r("Orthohepadnavirus hominoidei",
   receptors=["NTCP / SLC10A1 (sodium taurocholate cotransporting "
              "polypeptide)"],
   attachment=["Heparan sulfate proteoglycans"],
   tropism="Hepatocytes, essentially exclusively.",
   entry="preS1 domain of large surface protein binds NTCP; endocytosis and "
         "nuclear delivery of relaxed circular DNA, converted to cccDNA.",
   note="NTCP is a bile-acid transporter expressed almost only on hepatocytes, "
        "which accounts for HBV's strict hepatotropism and narrow host range. "
        "It is directly druggable: bulevirtide is an NTCP-blocking preS1 "
        "lipopeptide licensed for hepatitis D.")

_r("Deltavirus italiense", receptors=["NTCP / SLC10A1, via the HBV envelope"],
   tropism="Hepatocytes.",
   entry="Borrowed HBsAg envelope; entry identical to HBV.",
   note="HDV has no envelope of its own, so it is wholly dependent on HBV "
        "surface antigen for entry — which is why HBV vaccination prevents "
        "hepatitis D and why bulevirtide works against it.")

# --- Rhabdoviridae -------------------------------------------------------
_r("Lyssavirus rabies",
   receptors=["Nicotinic acetylcholine receptor", "NCAM / CD56", "p75NTR",
              "mGluR2"],
   tropism="Skeletal muscle at the inoculation site, then peripheral nerve "
           "and CNS neurons.",
   entry="Endocytosis and low-pH G-mediated fusion; retrograde axonal "
         "transport to the CNS.",
   note="Binding the acetylcholine receptor at the neuromuscular junction is "
        "how rabies gets into a motor neuron, and retrograde transport is why "
        "incubation depends on distance from the brain — and why wound "
        "washing plus immunoglobulin at the bite site still works days later.")

# --- Caliciviridae / Sedoreoviridae -------------------------------------
_r("Norovirus norwalkense",
   receptors=["Histo-blood group antigens (HBGAs)",
              "CD300lf (murine norovirus; human receptor unsettled)"],
   tropism="Small intestinal enterocytes and tuft cells.",
   entry="Endocytosis.",
   note="HBGA dependence is why susceptibility is genetically determined: "
        "FUT2 non-secretors are resistant to GII.4 norovirus, which is one of "
        "the few human infections with a clean Mendelian resistance locus.")

_r("Rotavirus alphagastroenteritidis",
   receptors=["Histo-blood group antigens (VP8* of genotype-dependent "
              "specificity)", "Integrin α2β1", "Hsc70"],
   attachment=["Sialoglycans for some animal strains"],
   tropism="Mature enterocytes at the villus tip of the small intestine.",
   entry="Sequential VP8*/VP5* interactions; trypsin cleavage of VP4 is "
         "required, which is why the gut is the permissive site.",
   note="P[8] human strains bind secretor-dependent HBGAs, so FUT2 status "
        "shapes both susceptibility and oral vaccine take — part of why "
        "rotavirus vaccine efficacy differs between high- and low-income "
        "settings.")


def get(species):
    return RECEPTORS.get(species)


def covered():
    return sorted(RECEPTORS)
