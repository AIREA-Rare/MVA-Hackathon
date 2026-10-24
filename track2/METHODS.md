# Methods (draft, 2026-10-24)

All patient-level steps ran in approved private storage, outside every Git repository. Console output was limited to counts and status lines. No genotype, read or identifier was written to a tracked file. External queries used generic gene, drug or process terms only; no patient coordinate, variant notation, sample identifier or phenotype combination was sent to any external service.

## Input data

| Input | Description |
|---|---|
| Participant dataset | The organiser-provided single-sample whole-genome dataset (small-variant VCF and paired-end FASTQ files), used under the organiser's terms. One sample; no parental or family data; no RNA; no cytogenetics. |
| Phenotype | Not used for variant interpretation beyond the gene-level question of MVA. No phenotype list appears in this bundle. |

## Software

| Tool | Version | Use |
|---|---|---|
| bwa | 0.7.17-r1188 | Read alignment (`bwa mem`) |
| samtools | 1.19.2 | Sorting, indexing, mate fixing, duplicate marking, read counts |
| bcftools | 1.19 | Normalisation (`norm -m -any -f <reference>` with reference check), pile-up and re-calling |
| Python | 3.12.3, standard library only | All analysis scripts and checks |

No other software was installed. No splice predictor, structural-variant caller, repeat annotator, assembler or FoldX was available, and their analyses are therefore recorded as not run.

## Reference data

| Resource | Version |
|---|---|
| Genome | NCBI GRCh38 no_alt_plus_hs38d1 analysis set (GCA_000001405.15), with GRC exclusions |
| Gene models | Ensembl release 116 GFF3 |
| Transcript choice | MANE v1.5 (MANE Select) |
| Proteins | UniProt release 2026_03 (human reference proteome UP000005640) and the UniProtKB BUBR1 entry (O60566) |
| Population frequency | gnomAD v4.1.1 genome and exome sites (regional reads only), gnomAD v4.0 exome coverage summary |
| Clinical assertions | ClinVar VCF release 2026-10-04 (local copy) |
| Structure | AlphaFold DB model v6 of BUBR1 (wild type only); AlphaFold DB content is licensed CC BY 4.0. The structure file is not stored here. |
| Literature | Europe PMC REST API (raw abstracts; full text where open access) |
| Gene–disease validity | GenCC |
| Regulatory status | openFDA (`drugsfda`, `label`) and EMA EPAR pages, plus a local EMA medicines-report snapshot dated 2026-10-20 |

OMIM was not used.

## Read-level re-analysis (K3, K4)

Locus-targeted read recovery was used instead of a whole-genome alignment:
1. **Pass 1:** every read pair from all FASTQ files was aligned (`bwa mem -t 11 -v 1`) to a locus reference: BUB1B ±250 kb, then TRIP13, CEP57 and CENATAC ±100 kb using Ensembl 116 gene spans. A pair was kept when either mate had at least 60 aligned bases with edit distance NM ≤ 2. This keeps clipped and discordant reads for structural evidence.
2. **Pass 2:** the kept pairs were realigned to the full analysis set (`bwa mem -t 10 -v 1`, with a read group), then sorted and indexed. For the three-locus screen, `samtools fixmate -m` and `samtools markdup -s` were also applied.
3. **Re-calling:** `bcftools mpileup -q 20 -Q 13 -a AD,DP` piped to `bcftools call -m`.

**Robustness grid:** mapping quality {0, 20, 40, 60} × base quality {0, 13, 20, 30} × duplicates kept or removed (32 combinations).

**Read-level tests:** ten pre-declared tests per candidate (strand, read position, mapping and base quality, local sequence context and others), compared with 252 control heterozygous SNVs from the same sample.

**Limitation:** reads from regions highly divergent from the reference can be lost by locus recovery.

## Annotation and transcript checks (K2–K4)

- **REF and normalisation:** REF allele checked against the analysis set; left-normalisation with bcftools.
- **Transcript effect:** re-derived on the MANE Select transcript from Ensembl 116 exon models.
- **NMD expectation:** the exon-junction-complex rule (a premature stop more than 50 nt upstream of the last exon–exon junction is expected to trigger NMD). This is a prediction.
- **Population frequency:** exact allele matching after normalisation. Equivalent but differently represented variants were not reconciled.

## Drug-hypothesis assessment (K5)

- **Candidates:** the 12 inherited from the curated WP5/K2 review. None was dropped and none substituted.
- **Causal chain:** each candidate was evaluated over five links: drug → target → cellular process → disease mechanism → phenotype.
- **Regulatory status:** verified in openFDA and on EMA pages.
- **Ranking:** a documented deterministic rule over criteria C0–C7 (`DRUG_HYPOTHESIS_ASSESSMENT.md`).

## Functional-evidence assessment (K6)

- **Framework:** the ClinGen SVI PS3/BS3 recommendations (Brnich et al. 2019), steps 1–4.
- **Paralog alignment:** BUBR1 against BUB1 pseudokinase/kinase domains, using local Smith–Waterman with BLOSUM62.
- **ClinVar counts:** within ±10 residues of the missense change and gene-wide, on the MANE protein.
- **No PS3/BS3 strength** was assigned to any proposed experiment.

## Integrity controls

- Each stage ran independent validation checks, all of which passed: K2 12/12, K5 11/11, K6 10/10. K3 and K4 recorded their own checks.
- Each stage kept checksums of all earlier packages and confirmed they were unchanged.
- Corrections found during the work are documented, not silently fixed:
  - a ClinVar consequence parse that kept only the last term;
  - one overstated count;
  - a deviation from a pre-declared rule in the CEP57 classification.

## What these methods cannot show

- Phase of the BUB1B variants.
- Effects on RNA, function, or clinical outcome.
- Variants in classes that short reads or locus recovery cannot detect.
- Population frequency of the CEP57 signal or of the TRIP13, CEP57 and CENATAC records. These were not run; gnomAD regional reads covered BUB1B and a few other genes only.
