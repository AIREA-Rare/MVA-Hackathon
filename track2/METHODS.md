# Methods (draft, 2026-10-24)

All patient-level steps ran in approved private storage, outside every Git repository. No genotype, read or identifier was written to a version-controlled file. The scripts were designed to print counts and status lines only. External database and literature queries used generic gene, drug or process terms and public identifiers only; no patient coordinate, variant notation, sample identifier or phenotype combination was included in any of them. The analysis was run with a cloud AI coding assistant, which processed command output, including variant-level information. Its use is covered by the team's AI-use disclosure.

## Input data

| Input | Description |
|---|---|
| Participant dataset | The organiser-provided single-sample whole-genome dataset (small-variant VCF and paired-end FASTQ files), used under the organiser's terms. One sample; no parental or family data; no RNA; no cytogenetics. |
| Phenotype | A phenotype summary supplied by the team was used at gene level only: to compare the four genes and to keep alternative explanations open. It was not used to classify any variant. No phenotype list appears here. |

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
- **ClinVar counts:** in a small window around the missense change, and gene-wide, on the MANE protein.
- **No PS3/BS3 strength** was assigned to any proposed experiment.

## Integrity controls

- **Validation scripts.** Each stage ran one, recomputing key results by separate code paths (for example samtools or bcftools against the custom parsers) and checking schemas, cross-references, query privacy and document–table agreement:

  | Stage | Checks | Result |
  |---|---|---|
  | K2 | 12 | all PASS |
  | K3 | 15 | all PASS |
  | K4 | 13 | all PASS |
  | K5 | 11 | all PASS |
  | K6 | 10 | all PASS |

  **Limited independence:** the same AI assistant that did the analysis wrote these scripts. A pass shows internal consistency, not external validation.
- **Separate audit of K2.** Its scientific findings:
  - **Corrected before K3:** one overstated statement about a gene-level phenotype association, drawn from a single abstract, was narrowed in corrected copies, which later stages used.
  - **Documented but not re-edited in the K2 files; reflected in this summary:**
    - a source count was wrong;
    - K2's external pages were read through a summarising fetch tool, so its "abstract" and "full" labels mean a summary of that text (see `REFERENCES.md`);
    - two case reports are a probable duplicate and count as one case;
    - one database record lacked its single-submitter flag.

  The audit's process findings about local data handling are tracked internally.
- **Checksums.** Each stage kept checksums of all earlier packages and confirmed they were unchanged.
- **Documented, not silently fixed:**
  - a ClinVar consequence parse that kept only the last term;
  - one overstated count;
  - a deviation from a pre-declared rule in the CEP57 classification.

## Analyses not run, and why

| Analysis | Reason |
|---|---|
| Statistical phasing | No reference panel or genetic map; the missense allele is a singleton; it would give a misleading probability |
| Orthogonal confirmation of the calls (for example Sanger sequencing) | Needs new patient material, outside the hackathon terms |
| Family, long-read or linked-read phasing | No such data |
| Splice prediction | No predictor installed; installs not authorised |
| Residue conservation beyond one paralog | No local alignment; downloads not authorised |
| Repeat classification or local assembly of the CEP57 signal; structural-variant population lookup | Tools or database not available; an external lookup would expose a position |
| gnomAD frequency of the TRIP13, CEP57 and CENATAC records | Needs an owner-approved regional read; not done |
| Full-text reading of most key papers | Not open access |
| Wet-lab experiments | Designs only |

## What these methods cannot show

- Phase of the BUB1B variants.
- Effects on RNA, function, or clinical outcome.
- Variants in classes that short reads or locus recovery cannot detect.
- Population frequency of the CEP57 signal or of the TRIP13, CEP57 and CENATAC records. These were not run; gnomAD regional reads covered BUB1B and a few other genes only.
