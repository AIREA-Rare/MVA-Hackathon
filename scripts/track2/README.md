# Track 2 analysis code (sanitised release)

This folder holds the analysis scripts behind the AIREA Track 2 report (`../../track2/AIREA_track2_report.md`). The Hackathon asks the repository to contain documented, reproducible code.

**What "sanitised" means here:**
- The scripts are the ones actually used, copied from the team's private analysis workspace.
- Only three kinds of change were made:
  1. **Private locations.** The private data-root path became an environment variable.
  2. **Participant-specific values.** Candidate positions, alleles, a FASTQ file-name prefix, two genomic windows, and literature-query terms naming residues next to the participant's variant were moved into private configuration files. Committed templates (`config/`) document every key.
  3. **Script location.** One script now locates its sibling script relative to its own folder.
- Nothing else in the logic was changed.
- The participant's data and any participant-specific value are **not** in this repository.

**Research only.** Nothing here is a diagnosis or treatment advice.

## Requirements

| Item | Version used |
|---|---|
| bwa | 0.7.17-r1188 |
| samtools | 1.19.2 |
| bcftools | 1.19 |
| Python | 3.12.3, standard library only |
| Reference data | GRCh38 no_alt_plus_hs38d1 analysis set (GCA_000001405.15) with a bwa index; Ensembl release 116 GFF3; MANE v1.5; UniProt release 2026_03; regional gnomAD v4.1.1 extracts; ClinVar GRCh38 VCF of 2026-10-04; AlphaFold DB model v6 of BUBR1 (see `../../track2/METHODS.md`) |
| Input data | The gated Hackathon dataset (VCF and FASTQ), obtained under the Hackathon Rules and Data Transfer Agreement. It must not be redistributed. |

## Configuration

| Variable | Meaning |
|---|---|
| `MVA_DATA_ROOT` | Private data root: `raw/` (dataset), `ref/` (reference data), `work/` (intermediates), `out/` (results) |
| `MVA_PRIVATE_CONFIG` | Path to `private_config.json` (from `config/private_config.template.json`); used by `k3_phase`, `k3_followup`, `k4_lit` and `k6_lit` |
| `MVA_PRIVATE_ENV` | Path to `private.env` (from `config/private.env.template`); used by `make_check_positions.sh` and `k2_local_lookups.sh` |
| `MVA_FASTQ_PREFIX` | FASTQ file-name prefix; exported by `private.env`; used by `locus_probe.sh` and `locus_run.sh` |
| `MVA_VCF` | Optional; the dataset VCF (default: the only `*.vcf.gz` in `raw/`) |

Filled `private_config.json` and `private.env` files are git-ignored. Never commit them.

The scripts write their outputs under `$MVA_DATA_ROOT/work` and `$MVA_DATA_ROOT/out`, in the folder names they were run with (for example `out/T2K3_research_2026-10-23`). Those outputs are participant-derived and must stay private.

## Run order

| Step | Script(s) | Purpose |
|---|---|---|
| 1 | `upstream/locus_probe.sh` | Build the BUB1B ±250 kb locus reference from the Ensembl 116 gene span; time a 1M-pair probe |
| 2 | `upstream/locus_run.sh` | Pass 1: every read pair against the locus reference (keep a pair if any mate has ≥ 60 aligned bases with NM ≤ 2). Pass 2: realign the kept pairs to GRCh38. |
| 3 | `upstream/post_t2f1.sh verify`, then `preflight`, then `markdup`, then `analysis` | Checks, duplicate marking (`fixmate`/`markdup`), and the T2F-1 locus analysis (`upstream/locus_analysis.py`) |
| 4 | `upstream/make_check_positions.sh` | Private list of candidate positions for read-level checks |
| 5 | `k2/k2_local_lookups.sh`, `k2/k2_local_aggregate.py` | K2 local look-ups: transcript annotation, regional gnomAD, aggregates |
| 6 | `k3/k3_locus_screen.sh` | Read recovery for TRIP13, CEP57 and CENATAC (±100 kb, same method as step 2) |
| 7 | `k3/k3_bam_qc.py`, `k3_rrecords.py`, `k3_mappability.py`, `k3_annotation.py`, `k3_exon_callable.py`, `k3_roh_het.py`, `k3_sv_cov.py`, `k3_cluster_probe.py`, `k3_disc_detail.py`, `k3_followup.py`, `k3_phase.py`, `k3_lit.py`, `k3_build_qc_tables.py` | K3: read-level robustness (32-combination grid), coding callability, runs of homozygosity and heterozygosity, structural screens, phase feasibility, literature, QC tables |
| 8 | `k4/k4_phase.py`, `k4_missense_context.py`, `k4_cep57_sv.py`, `k4_cep57_mei.py`, `k4_lit.py` | K4: phase re-assessment, wild-type structural and annotation context, CEP57 signal reconstruction and insertion-hallmark test, literature |
| 9 | `k5/k5_regulatory.py`, `k5_lit.py`, `k5_lit2.py`, `k5/drug_ranking.py` | K5: openFDA and EMA status, literature, and the deterministic drug-category rule over `k5/DRUG_HYPOTHESIS_CRITERIA.tsv` |
| 10 | `k6/k6_local.py`, `k6_lit.py` | K6: paralog alignment, ClinVar neighbourhood and gene-wide controls, annotation support, literature |
| 11 | `submission/fill_methods_form.py`, `submission/fix_form_view.py` | Fill the official methods workbook from the report's Annex A, so the two are always identical |

Run Python scripts as `python3 -B -I <script>`. Literature and regulatory scripts send only generic gene, drug and process terms or public identifiers to Europe PMC, openFDA and EMA.

**Reproducible from this repository alone,** without the dataset:

```bash
python -m unittest tests.test_track2_drug_ranking   # re-derives all 12 published drug categories
python scripts/track2/k5/drug_ranking.py
```

## What is not included, and why

| Not included | Reason |
|---|---|
| Ledger and table builders (K2 ledgers and source register; K3 hypothesis evidence and ledger; K4 integrated tables; K5 matrix, ledger and template copies; K6 classification) | They embed the curated, participant-specific evidence text (restricted). Their conclusions are summarised in the report. The K5 ranking itself is reproducible through `k5/drug_ranking.py`. |
| Stage validation scripts (K2–K6) | They embed participant-specific expected values. Their results and limits are reported in `../../track2/METHODS.md`. |
| Audit, remediation, snapshot, baseline and git-state scripts | Internal integrity and incident records, not analysis |
| Earlier variant-specific analyses (structure context, substitution descriptors, ClinVar and gnomAD panels, mutant-modelling reviews) | Variant-specific; superseded for interpretation by K2–K6 |
| The upstream candidate-extraction pipeline (VCF split, consequence annotation, gene filtering) | It belongs to the team's separate research codebase. Its outputs are inputs to the steps above. |

## Validation and its limits

- **The same AI assistant wrote the analyses, their validation scripts and this sanitisation.** All of the checks below show consistency, not independent validation.
- **Equivalence of the sanitised copies.** Run against the private data in a sandbox:
  - `upstream/make_check_positions.sh` and `k3/k3_phase.py` reproduced the original outputs byte-for-byte;
  - `k2/k2_local_lookups.sh` reproduced its output except two header lines, which were reworded on purpose to remove a position and alleles.
- **Static checks.** All Python files parse and all shell files pass `bash -n`. A diff against the originals shows only the intended changes.
- **Privacy checks.** Before release, every file was scanned for participant positions, notation, identifiers, phenotype terms, read-level values and local paths. The remaining large numbers are public Ensembl gene spans or read-count limits.
- **Not re-run end to end** in this release: the long read-recovery steps (several hours) and the network-dependent literature scripts.

## Licence

CC BY 4.0 (`../../LICENSE`), as the Hackathon's Official Rules require for submissions and code.
