# References and access levels (draft, 2026-10-24)

The **access** column records what was actually read. Most literature was read at abstract level, as raw Europe PMC API text. A claim drawn from an abstract can be wrong about details that only the full text gives.

**Caveat for K2-stage pages.** The external pages read in the K2 stage, including the GenCC gene–disease validity pages, went through a summarising web-fetch tool. For those reads, "database page" or "abstract" means a tool-generated summary of that page, not raw text. The load-bearing literature was later re-read as raw API text.

Each reference is listed with the ID of the claim in the team's internal evidence ledgers (WP2, K3, K5, K6). The ledgers are restricted and not published; the IDs let the team trace each claim to its source record.

## Framework and rules

| Reference | Used for | Access | ID |
|---|---|---|---|
| Brnich et al. (ClinGen SVI). *Genome Med* 2019. PMID 31892348; PMC6938631 | Assay validity steps; minimum of 11 pathogenic and benign controls for moderate evidence | **Full text** (open-access XML) | K6-E06 |
| Nagy E, Maquat LE. A rule for termination-codon position within intron-containing genes: when nonsense affects RNA abundance. *Trends Biochem Sci* 1998;23(6):198-199. PMID 9644970 | Exon-junction-complex NMD rule (50 nt) | Bibliographic record (no abstract in Europe PMC); the threshold was not re-verified against the full text | WP2 |

## MVA and BUBR1 biology

| Reference | Used for | Access | ID |
|---|---|---|---|
| Hanks et al. *Nat Genet* 2004;36:1159-61. PMID 15475955 | Biallelic BUB1B mutations in MVA | Abstract | WP2-01 |
| Matsuura et al. *Am J Med Genet A* 2006;140A:358-67. PMID 16411201 | Monoallelic BUB1B mutations; reduced transcripts | Abstract | WP2-02 |
| Ochiai et al. *PNAS* 2014. PMID 24344301 | Non-coding BUB1B second-allele class | Abstract | WP2-03 |
| Suijkerbuijk et al. 2010. PMID 20516114 | Patient-cell checkpoint defect; fast turnover of kinase-domain missense | Abstract | K3-E29 |
| BubR1 missense mouse model of a disease-reported human missense, *J Clin Invest* 2020. PMID 31738183 | A disease-reported missense in the same domain; allelic effects "beyond protein level" | Abstract | K6-E05 |
| Silva et al. 2024. PMID 39014450 | Monoallelic BUB1B variants with decreased BubR1 expression or stability | Abstract | K6-E09 |
| *Dev Cell* 2012. DOI 10.1016/j.devcel.2012.03.009 | Human BUBR1 catalysis is dispensable; ATP-interacting residues matter for conformational stability (mechanisms M1, M4) | Abstract | WP2-26 |
| *Cell Rep* 2020. DOI 10.1016/j.celrep.2020.108397 | The pseudokinase domain promotes KARD phosphorylation and PP2A-B56 recruitment (mechanism M3) | Abstract | WP2-27 |
| Baker et al. 2013. PMID 23242215 | Sustained high BubR1 expression reduces tumorigenesis and extends lifespan in mice | Abstract | K5-E17 |
| PMID 40607964 (2025) | BubR1 insufficiency causes cardiac hypertrophy, fibrosis and senescence markers in mice | Abstract | K5-E16 |

## Drug hypotheses

| Reference | Used for | Access | ID |
|---|---|---|---|
| Baker et al. 2011. PMID 22048312 | Genetic clearance of p16Ink4a-positive cells delays ageing-type phenotypes in BubR1 progeroid mice; senescence constrains malignant progression | Abstract | K5-E14 |
| Zhu et al. 2015. PMID 25754370 | Dasatinib removes senescent human fat progenitors in vitro | Abstract | K5-E15 |
| North et al. 2014. PMID 24825348 | NAD+/SIRT2-dependent BubR1 K668 deacetylation maintains BubR1 abundance; NMN raised BubR1 in mice | Abstract | K5-E18 |
| PMID 42628241 (2026) | High-dose nicotinic acid raised blood NAD+ in healthy individuals | Abstract | K5-E19 |
| PMIDs 14534336, 11401894 (cystic fibrosis), 17290305 (NMD dependence) | Gentamicin read-through evidence and its dependence on NMD | Abstract | K5-E20 |
| ACT DMD phase 3 trial. PMID 28728956 | Ataluren missed its primary endpoint | Abstract | K5-E21 |
| Gonzalez-Blanco et al. 2026. PMID 41820377 | Genetic ROS scavenging dampened aneuploidy-related brain-size loss in a *Drosophila* MVA model | Abstract | K5-E23 |
| PMID 41290707 (2025) | Antioxidant treatment reduced missegregation in fibroblasts from aged individuals | Abstract | K5-E24 |
| Sayin et al. 2014. PMID 24477002 | N-acetylcysteine and vitamin E accelerated tumour progression in mice | Abstract | K5-E25 |
| PMID 41516400 (2026) | N-acetylcysteine enhanced pulmonary metastasis in mouse breast-cancer models | Abstract | K5-E26 |
| PMID 37883329 (2023) | Microtubule poisons cause chromosome missegregation at clinical concentrations | Abstract | K5-E27 |

## Databases and regulatory sources

| Source | Version or date | Access |
|---|---|---|
| ClinVar | VCF release 2026-10-04 (local copy) | Full (local) |
| gnomAD | v4.1.1 genomes and exomes (regional reads); v4.0 exome coverage summary | Full (local extracts) |
| UniProt | Release 2026_03; entry O60566 | Full (local) |
| AlphaFold DB | BUBR1 model v6 (wild type); licence CC BY 4.0 | Full (local copy, not redistributed) |
| Ensembl / MANE | Release 116 GFF3; MANE v1.5 | Full (local) |
| GenCC | Gene–disease validity pages | Database pages |
| openFDA | `drugsfda` and `label` endpoints; label set IDs are recorded in the internal evidence ledger | API records; openFDA states its data are unvalidated |
| EMA | EPAR pages (Sprycel, Translarna, Velcade, Omnitrope); medicines-report snapshot of 2026-10-20 | Status text; local snapshot |

OMIM was not used.
