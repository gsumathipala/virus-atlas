"""Virion architecture per family, for the schematic figures.

ICTV's VMR records taxonomy and genome type but not morphology, so this is a
curated layer: for each family, the shape, envelope, surface projections,
capsid symmetry, approximate size and genome organisation that a textbook
figure would show.

Every species resolves to a spec: by family where one is defined, otherwise by
a generic spec for its genome type, so nothing renders blank. `confident`
records which of the two happened -- the figure labels itself "generalised"
when it is only a genome-type guess.

Fields
  shape      spherical | bullet | filament | icosahedral | rod | helical
             | brick | phage | lemon | bottle | spindle | pleomorphic
  envelope   True/False
  spikes     none | club | spike | fringe | fibre | peplomer
  capsid     icosahedral | helical | complex | none
  nm         [min, max] virion diameter/length in nanometres
  segments   number of genome segments (1 = monopartite)
  kb         approximate genome size in kilobases/kilobasepairs
  genes      ordered gene/segment labels for the genome map
  note       one line on what the architecture means functionally
"""

GENERIC = {
    "dsDNA": dict(shape="icosahedral", envelope=False, spikes="none",
                  capsid="icosahedral", nm=[40, 100], segments=1, kb=40,
                  genes=["early", "late"],
                  note="Double-stranded DNA genome; most such viruses build an icosahedral capsid and replicate in the nucleus."),
    "ssDNA": dict(shape="icosahedral", envelope=False, spikes="none",
                  capsid="icosahedral", nm=[18, 26], segments=1, kb=2,
                  genes=["rep", "cap"],
                  note="Small single-stranded DNA genome, typically encoding little more than a replicase and a capsid protein."),
    "ssDNA(+)": None, "ssDNA(-)": None, "ssDNA(+/-)": None,
    "dsRNA": dict(shape="icosahedral", envelope=False, spikes="spike",
                  capsid="icosahedral", nm=[60, 80], segments=10, kb=20,
                  genes=["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10"],
                  note="Segmented double-stranded RNA inside a multilayered capsid; transcription happens within the particle."),
    "ssRNA(+)": dict(shape="icosahedral", envelope=False, spikes="none",
                     capsid="icosahedral", nm=[27, 40], segments=1, kb=8,
                     genes=["5'UTR", "ORF1", "3'UTR"],
                     note="Positive-sense RNA acts directly as mRNA, so the naked genome is infectious on entry."),
    "ssRNA(-)": dict(shape="pleomorphic", envelope=True, spikes="spike",
                     capsid="helical", nm=[80, 120], segments=1, kb=12,
                     genes=["N", "P", "M", "G", "L"],
                     note="Negative-sense RNA must be transcribed by a virion-packaged polymerase before any protein can be made."),
    "ssRNA(+/-)": dict(shape="spherical", envelope=True, spikes="spike",
                       capsid="helical", nm=[90, 120], segments=2, kb=11,
                       genes=["L", "S"],
                       note="Ambisense segments encode genes in both orientations on the same RNA."),
    "ssRNA-RT": dict(shape="spherical", envelope=True, spikes="peplomer",
                     capsid="complex", nm=[80, 120], segments=1, kb=9,
                     genes=["gag", "pol", "env"],
                     note="Reverse transcribes its RNA into DNA, which integrates into the host genome."),
    "dsDNA-RT": dict(shape="spherical", envelope=True, spikes="none",
                     capsid="icosahedral", nm=[42, 47], segments=1, kb=3,
                     genes=["S", "C", "P", "X"],
                     note="Replicates its DNA genome through an RNA intermediate using reverse transcriptase."),
    "ssRNA": dict(shape="spherical", envelope=True, spikes="spike",
                  capsid="helical", nm=[80, 120], segments=1, kb=10,
                  genes=["ORF"], note="Single-stranded RNA genome."),
}
GENERIC["ssDNA(+)"] = GENERIC["ssDNA"]
GENERIC["ssDNA(-)"] = GENERIC["ssDNA"]
GENERIC["ssDNA(+/-)"] = GENERIC["ssDNA"]
GENERIC["ssRNA(-); ssRNA(+/-)"] = GENERIC["ssRNA(-)"]

FAMILIES = {
    # --- Bunyavirals: the Oya virus neighbourhood -------------------------
    "Peribunyaviridae": dict(
        shape="spherical", envelope=True, spikes="spike", capsid="helical",
        nm=[80, 120], segments=3, kb=12,
        genes=["L — RNA polymerase", "M — Gn/Gc glycoproteins, NSm", "S — N nucleoprotein, NSs"],
        note="Three negative-sense segments (L, M, S) in a lipid envelope. Because the genome is in three pieces, co-infecting strains can swap whole segments — the reassortment that produced Ngari and Iquitos viruses."),
    "Hantaviridae": dict(
        shape="spherical", envelope=True, spikes="spike", capsid="helical",
        nm=[80, 120], segments=3, kb=12,
        genes=["L — polymerase", "M — Gn/Gc", "S — N"],
        note="Tri-segmented like other bunyavirals, but with a grid-like surface lattice of Gn/Gc spikes and no arthropod vector — transmission is by rodent excreta."),
    "Nairoviridae": dict(
        shape="spherical", envelope=True, spikes="spike", capsid="helical",
        nm=[90, 120], segments=3, kb=19,
        genes=["L — polymerase + OTU domain", "M — Gn/Gc", "S — N"],
        note="The largest bunyaviral L segment, encoding an ovarian-tumour protease domain that strips ubiquitin from host immune signalling proteins."),
    "Phenuiviridae": dict(
        shape="spherical", envelope=True, spikes="spike", capsid="helical",
        nm=[80, 120], segments=3, kb=12,
        genes=["L — polymerase", "M — Gn/Gc, NSm", "S — N + NSs (ambisense)"],
        note="The S segment is ambisense: N and the interferon-antagonist NSs are read in opposite directions from the same RNA."),
    "Nanoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none", capsid="icosahedral",
        nm=[17, 20], segments=8, kb=8,
        genes=["DNA-R — replication", "DNA-S — capsid", "DNA-C — cell-cycle link",
               "DNA-M — movement", "DNA-N — nuclear shuttle", "DNA-U1/U2/U4 — unknown"],
        note="Each of the eight circular ssDNA components is packaged in its own particle, so a complete infection requires all of them to arrive in the same cell."),
    # Multipartite negative-strand families. Listed explicitly because the
    # generic ssRNA(-) fallback is monopartite, which would draw a family- or
    # genus-level figure with one segment for genomes that have five to eleven.
    "Fimoviridae": dict(
        shape="spherical", envelope=True, spikes="none", capsid="helical",
        nm=[80, 200], segments=5, kb=15,
        genes=["RNA1 — polymerase", "RNA2 — glycoprotein", "RNA3 — nucleocapsid",
               "RNA4 — movement", "RNA5+ — accessory"],
        note="Emaraviruses carry four to eight segments; the number varies between species, so the figure follows the ICTV accession list where one is given."),
    "Amnoonviridae": dict(
        shape="spherical", envelope=True, spikes="none", capsid="helical",
        nm=[55, 100], segments=10, kb=10,
        genes=["Seg1 — putative polymerase", "Seg2-10 — largely unassigned"],
        note="Tilapia lake virus: ten segments with almost no sequence similarity to other orthomyxo-like viruses."),
    "Hadakaviridae": dict(
        shape="none", envelope=False, spikes="none", capsid="none",
        nm=[0, 0], segments=11, kb=11,
        genes=["RNA1 — polymerase", "RNA2-11 — accessory"],
        note="Hadaka virus is capsidless — \u201chadaka\u201d means naked — with eleven segments and no virion to draw."),
    "Arenaviridae": dict(
        shape="spherical", envelope=True, spikes="club", capsid="helical",
        nm=[110, 130], segments=2, kb=11,
        genes=["L — polymerase + Z", "S — GPC + NP"],
        note="Two ambisense segments, and ribosomes scavenged from the host cell are visible inside the particle — the sandy granules that name the family."),
    # --- Other negative-sense RNA ----------------------------------------
    "Rhabdoviridae": dict(
        shape="bullet", envelope=True, spikes="spike", capsid="helical",
        nm=[100, 430], segments=1, kb=12,
        genes=["N", "P", "M", "G", "L"],
        note="A rigid bullet-shaped particle: helical nucleocapsid wound inside a bullet envelope studded with a single trimeric G glycoprotein, the target of rabies vaccines."),
    "Filoviridae": dict(
        shape="filament", envelope=True, spikes="spike", capsid="helical",
        nm=[800, 1400], segments=1, kb=19,
        genes=["NP", "VP35", "VP40", "GP", "VP30", "VP24", "L"],
        note="Long filaments, often hooked or 6-shaped, up to a micrometre — among the largest animal virus particles, visible by light microscopy."),
    "Paramyxoviridae": dict(
        shape="pleomorphic", envelope=True, spikes="spike", capsid="helical",
        nm=[150, 350], segments=1, kb=15,
        genes=["N", "P/V/C", "M", "F", "H/G", "L"],
        note="Pleomorphic envelope with two surface glycoproteins: one binds the receptor, the other (F) fuses membranes, which is why these viruses form syncytia."),
    "Pneumoviridae": dict(
        shape="pleomorphic", envelope=True, spikes="spike", capsid="helical",
        nm=[150, 300], segments=1, kb=15,
        genes=["NS1", "NS2", "N", "P", "M", "SH", "G", "F", "M2", "L"],
        note="Filamentous and spherical forms with G attachment and F fusion proteins; F is the target of RSV monoclonals and vaccines."),
    "Orthomyxoviridae": dict(
        shape="spherical", envelope=True, spikes="peplomer", capsid="helical",
        nm=[80, 120], segments=8, kb=13,
        genes=["PB2", "PB1", "PA", "HA", "NP", "NA", "M", "NS"],
        note="Eight separate segments, each a ribonucleoprotein. Two co-infecting strains can exchange segments wholesale — antigenic shift, the mechanism behind influenza pandemics."),
    "Bornaviridae": dict(
        shape="spherical", envelope=True, spikes="spike", capsid="helical",
        nm=[70, 130], segments=1, kb=9,
        genes=["N", "P", "M", "G", "L"],
        note="Unusually for a negative-sense RNA virus, replicates and splices its transcripts in the nucleus."),
    # --- Positive-sense RNA ----------------------------------------------
    "Flaviviridae": dict(
        shape="spherical", envelope=True, spikes="none", capsid="icosahedral",
        nm=[40, 60], segments=1, kb=11,
        genes=["C", "prM", "E", "NS1", "NS2A/B", "NS3", "NS4A/B", "NS5"],
        note="A smooth envelope with E glycoprotein lying flat in a herringbone lattice rather than projecting spikes. One long polyprotein is cleaved into three structural and seven non-structural proteins."),
    "Togaviridae": dict(
        shape="spherical", envelope=True, spikes="spike", capsid="icosahedral",
        nm=[60, 70], segments=1, kb=12,
        genes=["nsP1", "nsP2", "nsP3", "nsP4", "C", "E3", "E2", "6K", "E1"],
        note="A strikingly regular particle: 80 trimeric E1/E2 spikes in T=4 symmetry over an icosahedral capsid. Non-structural genes are translated first, structural genes from a subgenomic RNA."),
    "Coronaviridae": dict(
        shape="spherical", envelope=True, spikes="club", capsid="helical",
        nm=[80, 120], segments=1, kb=30,
        genes=["ORF1a/1b — replicase", "S — spike", "E", "M", "N"],
        note="The club-shaped spike trimers that form the 'corona'. At ~30 kb these are among the largest RNA genomes, which requires a proofreading exonuclease to replicate at all."),
    "Picornaviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[28, 30], segments=1, kb=7.5,
        genes=["VP4", "VP2", "VP3", "VP1", "2A-2C", "3A-3D"],
        note="A small, rugged, naked icosahedron of 60 copies each of four capsid proteins — stable in stomach acid, which is how enteroviruses reach the gut."),
    "Caliciviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[27, 40], segments=1, kb=7.5,
        genes=["NS1-7", "VP1", "VP2"],
        note="Cup-shaped surface depressions give the family its name; the naked capsid survives chlorination and makes norovirus extraordinarily transmissible."),
    "Astroviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[28, 35], segments=1, kb=7,
        genes=["ORF1a", "ORF1b", "ORF2"],
        note="A five- or six-pointed star outline on electron microscopy."),
    "Hepeviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[27, 34], segments=1, kb=7.2,
        genes=["ORF1", "ORF2", "ORF3"],
        note="Naked in faeces but quasi-enveloped in blood, cloaked in host membrane — which changes how antibodies can reach it."),
    "Matonaviridae": dict(
        shape="spherical", envelope=True, spikes="spike", capsid="icosahedral",
        nm=[60, 70], segments=1, kb=10,
        genes=["p150", "p90", "C", "E2", "E1"],
        note="Rubella virus alone: an alphavirus-like architecture but a respiratory, non-arthropod-borne lifestyle and a notorious teratogen."),
    # --- dsRNA ------------------------------------------------------------
    "Sedoreoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[70, 80], segments=11, kb=18,
        genes=["VP1", "VP2", "VP3", "VP4", "NSP1", "VP6", "NSP3", "NSP2", "VP7", "NSP4", "NSP5"],
        note="A smooth triple-layered particle. Rotavirus's 11 segments reassort freely, which is why strains are typed by two independent genes (G and P)."),
    "Spinareoviridae": dict(
        shape="icosahedral", envelope=False, spikes="spike",
        capsid="icosahedral", nm=[70, 85], segments=10, kb=23,
        genes=["L1", "L2", "L3", "M1", "M2", "M3", "S1", "S2", "S3", "S4"],
        note="Turreted capsid: spikes at the icosahedral vertices cap the channels through which mRNA is extruded."),
    # --- DNA viruses ------------------------------------------------------
    "Poxviridae": dict(
        shape="brick", envelope=True, spikes="none", capsid="complex",
        nm=[220, 450], segments=1, kb=190,
        genes=["core — replication", "central — conserved", "terminal — host interaction"],
        note="A brick-shaped particle with a dumbbell core and lateral bodies. Uniquely for a DNA virus it replicates entirely in the cytoplasm, carrying its own transcription machinery."),
    "Orthoherpesviridae": dict(
        shape="spherical", envelope=True, spikes="spike", capsid="icosahedral",
        nm=[150, 200], segments=1, kb=150,
        genes=["IE — immediate early", "E — early", "L — late"],
        note="Four layers: DNA core, T=16 icosahedral capsid, a protein tegument, then the envelope. All establish lifelong latency."),
    "Adenoviridae": dict(
        shape="icosahedral", envelope=False, spikes="fibre",
        capsid="icosahedral", nm=[90, 100], segments=1, kb=36,
        genes=["E1A", "E1B", "E2", "E3", "E4", "L1-L5"],
        note="A naked icosahedron with an antenna-like fibre at each of the twelve vertices — the receptor-binding structure exploited by adenoviral vector vaccines."),
    "Papillomaviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[55, 60], segments=1, kb=8,
        genes=["E6", "E7", "E1", "E2", "E4", "E5", "L2", "L1"],
        note="A small circular dsDNA genome in a T=7 capsid of L1 pentamers. In high-risk types E6 and E7 inactivate p53 and Rb — the basis of cervical cancer, and L1 is the vaccine antigen."),
    "Polyomaviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[40, 45], segments=1, kb=5,
        genes=["large T", "small t", "VP1", "VP2", "VP3"],
        note="Circular dsDNA; large T antigen drives the cell cycle, which makes these viruses both oncogenic and classic tools of cell biology."),
    "Parvoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[18, 26], segments=1, kb=5,
        genes=["NS1", "VP1", "VP2"],
        note="Among the smallest animal viruses. The single-stranded DNA genome needs cells in S phase to replicate, which is why B19 targets erythroid precursors."),
    "Anelloviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[30, 32], segments=1, kb=3.8,
        genes=["ORF1", "ORF2", "ORF3"],
        note="Circular negative-sense ssDNA, carried by most healthy humans for life with no established disease — the bulk of the human 'virome'."),
    "Circoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[17, 22], segments=1, kb=2,
        genes=["rep", "cap"],
        note="A tiny circular ssDNA genome replicated by rolling-circle synthesis."),
    "Hepadnaviridae": dict(
        shape="spherical", envelope=True, spikes="none",
        capsid="icosahedral", nm=[42, 47], segments=1, kb=3.2,
        genes=["S — surface", "C — core", "P — polymerase", "X"],
        note="A partially double-stranded circular DNA genome replicated via RNA. Infected cells shed vast excesses of empty surface-antigen particles — the HBsAg measured in serology."),
    "Retroviridae": dict(
        shape="spherical", envelope=True, spikes="peplomer", capsid="complex",
        nm=[80, 120], segments=1, kb=9.7,
        genes=["LTR", "gag", "pol", "env", "LTR"],
        note="Two copies of the RNA genome, reverse transcriptase and integrase inside a conical core. Integration into host DNA makes infection permanent."),
    "Kolmioviridae": dict(
        shape="spherical", envelope=True, spikes="none", capsid="none",
        nm=[36, 43], segments=1, kb=1.7,
        genes=["HDAg"],
        note="Hepatitis delta: a circular RNA encoding one protein, which borrows hepatitis B surface antigen as its envelope and so cannot spread without it."),
    "Smacoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[17, 22], segments=1, kb=2.5,
        genes=["rep", "cap"], note="Small circular ssDNA viruses found in faecal samples."),
    "Genomoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[20, 22], segments=1, kb=2.2,
        genes=["rep", "cap"], note="Circular ssDNA viruses of fungi and other hosts."),
    # --- Bacteriophages and archaeal viruses ------------------------------
    "Straboviridae": dict(
        shape="phage", envelope=False, spikes="fibre", capsid="icosahedral",
        nm=[200, 250], segments=1, kb=170,
        genes=["early", "middle", "late — structural"],
        note="A myovirus-type phage: icosahedral head, contractile tail and tail fibres that recognise the bacterial surface, then inject DNA like a syringe."),
    "Drexlerviridae": dict(
        shape="phage", envelope=False, spikes="fibre", capsid="icosahedral",
        nm=[150, 200], segments=1, kb=50,
        genes=["structural", "replication", "lysis"],
        note="Siphovirus morphology: a long flexible non-contractile tail."),
    "Demerecviridae": dict(
        shape="phage", envelope=False, spikes="fibre", capsid="icosahedral",
        nm=[150, 200], segments=1, kb=110,
        genes=["structural", "replication", "lysis"],
        note="Long-tailed phages of enteric bacteria."),
    "Peduoviridae": dict(
        shape="phage", envelope=False, spikes="fibre", capsid="icosahedral",
        nm=[120, 170], segments=1, kb=30,
        genes=["structural", "integration", "lysis"],
        note="Temperate myophages that integrate into the bacterial chromosome."),
    "Schitoviridae": dict(
        shape="phage", envelope=False, spikes="fibre", capsid="icosahedral",
        nm=[60, 70], segments=1, kb=75,
        genes=["structural", "replication"],
        note="Podovirus morphology: a very short tail, and a virion-packaged RNA polymerase."),
    "Autographiviridae": dict(
        shape="phage", envelope=False, spikes="fibre", capsid="icosahedral",
        nm=[60, 70], segments=1, kb=40,
        genes=["class I", "class II", "class III"],
        note="Short-tailed phages that encode their own single-subunit RNA polymerase — the source of the T7 promoter used throughout molecular biology."),
    "Fiersviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[24, 28], segments=1, kb=3.6,
        genes=["maturation", "coat", "replicase"],
        note="Tiny positive-sense RNA phages; MS2 and Qβ, whose coat protein and replicase underpinned early molecular genetics."),
    "Steitzviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[24, 28], segments=1, kb=4,
        genes=["maturation", "coat", "lysis", "replicase"],
        note="Single-stranded RNA phages related to the Qβ group, now the largest described family by species count."),
    "Microviridae": dict(
        shape="icosahedral", envelope=False, spikes="spike",
        capsid="icosahedral", nm=[25, 27], segments=1, kb=5.4,
        genes=["A", "B", "C", "D", "E", "F", "G", "H"],
        note="A naked ssDNA capsid with a spike at each vertex; φX174 was the first genome ever fully sequenced."),
    "Inoviridae": dict(
        shape="filament", envelope=False, spikes="none", capsid="helical",
        nm=[800, 2000], segments=1, kb=6.4,
        genes=["pII", "pV", "pVIII", "pIII"],
        note="Long thin filaments extruded from the host without killing it; M13 is the backbone of phage display."),
    "Plasmaviridae": dict(
        shape="pleomorphic", envelope=True, spikes="none", capsid="none",
        nm=[50, 125], segments=1, kb=12,
        genes=["ORFs"], note="One of the few enveloped bacteriophages."),
    "Fuselloviridae": dict(
        shape="lemon", envelope=True, spikes="fibre", capsid="none",
        nm=[55, 100], segments=1, kb=15,
        genes=["ORFs"],
        note="Lemon-shaped archaeal virus with short tail fibres at one pole, from acidic hot springs."),
    "Bicaudaviridae": dict(
        shape="lemon", envelope=True, spikes="none", capsid="none",
        nm=[120, 400], segments=1, kb=63,
        genes=["ORFs"],
        note="A lemon-shaped particle that grows a tail at each end after leaving the cell — development outside a host, which is unique among viruses."),
    "Ampullaviridae": dict(
        shape="bottle", envelope=True, spikes="fibre", capsid="helical",
        nm=[60, 230], segments=1, kb=24,
        genes=["ORFs"], note="Bottle-shaped archaeal virus from an acidic hot spring."),
    "Clavaviridae": dict(
        shape="rod", envelope=False, spikes="none", capsid="helical",
        nm=[16, 143], segments=1, kb=5.3,
        genes=["ORFs"], note="A rigid rod with a cap at one end only."),
    "Lipothrixviridae": dict(
        shape="filament", envelope=True, spikes="fibre", capsid="helical",
        nm=[400, 2000], segments=1, kb=16,
        genes=["ORFs"], note="Enveloped filamentous archaeal virus with claw-like terminal structures."),
    "Chiyouviridae": dict(
        shape="filament", envelope=False, spikes="none", capsid="helical",
        nm=[400, 800], segments=1, kb=20,
        genes=["ORFs"], note="Filamentous archaeal virus with A-form double-stranded DNA."),
    # --- Plant viruses ----------------------------------------------------
    "Geminiviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[18, 38], segments=1, kb=2.7,
        genes=["rep", "cap", "mov"],
        note="Twinned incomplete icosahedra — two joined particles, the geminate morphology that names the family."),
    "Potyviridae": dict(
        shape="filament", envelope=False, spikes="none", capsid="helical",
        nm=[680, 900], segments=1, kb=10,
        genes=["P1", "HC-Pro", "P3", "CI", "NIa", "NIb", "CP"],
        note="Flexuous filaments spread by aphids; the largest family of plant RNA viruses."),
    "Virgaviridae": dict(
        shape="rod", envelope=False, spikes="none", capsid="helical",
        nm=[300, 310], segments=1, kb=6.4,
        genes=["replicase", "movement", "coat"],
        note="Rigid helical rods. Tobacco mosaic virus, in this family, was the first virus ever described and the first to be crystallised."),
    "Secoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[25, 30], segments=2, kb=10,
        genes=["RNA1 — replication", "RNA2 — structural"],
        note="Nematode- and beetle-transmitted plant viruses with a bipartite genome."),
    "Bromoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[26, 35], segments=3, kb=8,
        genes=["RNA1", "RNA2", "RNA3"],
        note="Tripartite plant RNA viruses; all three segments must enter a cell for infection."),
    "Tombusviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[28, 34], segments=1, kb=4.7,
        genes=["p33", "p92", "CP"], note="Small naked icosahedral plant viruses."),
    "Solemoviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[25, 30], segments=1, kb=4.5,
        genes=["ORF1", "ORF2", "CP"], note="Small icosahedral plant viruses."),
    "Betaflexiviridae": dict(
        shape="filament", envelope=False, spikes="none", capsid="helical",
        nm=[600, 1000], segments=1, kb=8,
        genes=["replicase", "movement", "coat"],
        note="Flexuous filamentous plant viruses."),
    "Alphaflexiviridae": dict(
        shape="filament", envelope=False, spikes="none", capsid="helical",
        nm=[470, 800], segments=1, kb=7,
        genes=["replicase", "movement", "coat"],
        note="Flexuous filamentous plant viruses."),
    "Closteroviridae": dict(
        shape="filament", envelope=False, spikes="none", capsid="helical",
        nm=[1200, 2000], segments=1, kb=19,
        genes=["replicase", "HSP70h", "CP", "CPm"],
        note="Very long flexuous filaments with the largest plant RNA genomes, confined to the phloem."),
    "Botourmiaviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[30, 35], segments=1, kb=5,
        genes=["RdRp", "CP"], note="Mostly mycoviruses, plus some plant viruses."),
    "Tolecusatellitidae": dict(
        shape="icosahedral", envelope=False, spikes="none", capsid="none",
        nm=[18, 20], segments=1, kb=1.4,
        genes=["betaC1"],
        note="Satellite DNAs that depend on a helper begomovirus and intensify its symptoms."),
    "Alphasatellitidae": dict(
        shape="icosahedral", envelope=False, spikes="none", capsid="none",
        nm=[18, 20], segments=1, kb=1.4,
        genes=["rep"], note="Satellite DNA components reliant on a helper virus."),
    # --- Giant viruses and amoebal viruses ---------------------------------
    "Mimiviridae": dict(
        shape="icosahedral", envelope=False, spikes="fringe",
        capsid="icosahedral", nm=[400, 750], segments=1, kb=1200,
        genes=["core replication", "translation-related", "accessory"],
        note="Giant viruses of amoebae, large enough to see by light microscopy and bearing a dense fibre fringe. Their genomes encode translation components once thought exclusive to cells."),
    "Phycodnaviridae": dict(
        shape="icosahedral", envelope=False, spikes="none",
        capsid="icosahedral", nm=[100, 220], segments=1, kb=300,
        genes=["early", "late"], note="Large dsDNA viruses of eukaryotic algae."),
    "Iridoviridae": dict(
        shape="icosahedral", envelope=False, spikes="fibre",
        capsid="icosahedral", nm=[120, 350], segments=1, kb=150,
        genes=["early", "late"],
        note="Large icosahedral viruses of invertebrates and fish; purified pellets diffract light, hence 'irido'."),
    "Baculoviridae": dict(
        shape="rod", envelope=True, spikes="peplomer", capsid="helical",
        nm=[250, 400], segments=1, kb=130,
        genes=["early", "late", "very late — polh"],
        note="Rod-shaped insect viruses occluded in protein crystals; the basis of the baculovirus protein expression system."),
    "Polydnaviriformidae": dict(
        shape="rod", envelope=True, spikes="none", capsid="helical",
        nm=[150, 300], segments=20, kb=200,
        genes=["segmented, integrated in wasp genome"],
        note="Encoded in the genome of parasitoid wasps and injected with their eggs to suppress host caterpillar immunity — a virus domesticated as a weapon."),
}

_SSRNA_PHAGE = dict(
    shape="icosahedral", envelope=False, spikes="none", capsid="icosahedral",
    nm=[24, 28], segments=1, kb=4,
    genes=["maturation", "coat", "replicase"],
    note="A small naked icosahedral positive-sense RNA phage of the Leviviricetes — a genome of only three or four genes, among the simplest replicating entities known.")

_TAILED_PHAGE = dict(
    shape="phage", envelope=False, spikes="fibre", capsid="icosahedral",
    nm=[150, 220], segments=1, kb=60,
    genes=["structural", "replication", "lysis"],
    note="A tailed bacteriophage (class Caudoviricetes): icosahedral head of packaged DNA, a tail that docks on the cell wall, and fibres that select the host.")

for _f in ("Autotranscriptaviridae", "Autoscriptoviridae", "Atkinsviridae",
           "Solspiviridae", "Duinviridae", "Blumeaviridae"):
    FAMILIES[_f] = dict(_SSRNA_PHAGE)

for _f in ("Aliceevansviridae", "Andersonviridae", "Herelleviridae",
           "Casjensviridae", "Vequintavirinae", "Kyanoviridae",
           "Zobellviridae", "Salasmaviridae", "Rountreeviridae",
           "Guelinviridae", "Chaseviridae", "Ackermannviridae",
           "Pachyviridae", "Crevaviridae", "Orlajensenviridae"):
    FAMILIES[_f] = dict(_TAILED_PHAGE)

FAMILIES["Caulimoviridae"] = dict(
    shape="icosahedral", envelope=False, spikes="none", capsid="icosahedral",
    nm=[45, 50], segments=1, kb=8,
    genes=["ORF I-VII"],
    note="Plant viruses that reverse transcribe like retroviruses but package DNA; many are endogenised in plant genomes.")

FAMILIES["Mitoviridae"] = dict(
    shape="pleomorphic", envelope=False, spikes="none", capsid="none",
    nm=[0, 0], segments=1, kb=2.5,
    genes=["RdRp"],
    note="Capsidless: the genome replicates inside fungal mitochondria as naked RNA and spreads only by cell fusion, never forming a particle at all.")

FAMILIES["Narnaviridae"] = dict(
    shape="pleomorphic", envelope=False, spikes="none", capsid="none",
    nm=[0, 0], segments=1, kb=3,
    genes=["RdRp"],
    note="Capsidless RNA replicons of fungi — a naked ribonucleoprotein with no virion stage.")

# Families whose particles are simply unknown or highly variable.
FAMILIES["Picobirnaviridae"] = dict(
    shape="icosahedral", envelope=False, spikes="none", capsid="icosahedral",
    nm=[33, 41], segments=2, kb=4.3, genes=["segment 1", "segment 2"],
    note="Bisegmented dsRNA viruses found in faeces; whether the host is the animal or its gut bacteria is unresolved.")


SHAPE_LABEL = {
    "spherical": "enveloped spherical",
    "pleomorphic": "enveloped pleomorphic",
    "icosahedral": "naked icosahedral",
    "bullet": "bullet-shaped",
    "filament": "filamentous",
    "rod": "rigid rod",
    "helical": "helical",
    "brick": "brick-shaped",
    "phage": "tailed bacteriophage",
    "lemon": "lemon-shaped",
    "bottle": "bottle-shaped",
    "spindle": "spindle-shaped",
}


def spec_for(family, genome, segments_hint=None):
    """Morphology spec for a species. Falls back to its genome type."""
    base = FAMILIES.get(family)
    confident = base is not None
    if base is None:
        base = GENERIC.get(genome) or GENERIC["ssRNA(+)"]

    spec = dict(base)
    spec["family"] = family
    spec["genome"] = genome
    spec["confident"] = confident
    spec["shape_label"] = SHAPE_LABEL.get(spec["shape"], spec["shape"])
    if segments_hint:
        spec["segments"] = segments_hint
    return spec


def coverage(families):
    """How many of the given families have a curated spec."""
    known = sum(1 for f in families if f in FAMILIES)
    return {"families": len(families), "with_spec": known}
