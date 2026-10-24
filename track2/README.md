# Track 2: draft evidence summary (not submitted)

**Status:** draft for owner review. Not submitted, not a clinical document. Nothing here is a diagnosis or treatment advice. No PatchLens output is included; any PatchLens record goes only in `../patchlens_outputs/records/`.

## Objective

Track 2 asks for approved-drug hypotheses for mosaic variegated aneuploidy (MVA), grounded in the participant's genetic data. Our approach is mechanism-first:
1. establish what the genetic data can and cannot show;
2. test each drug idea as an explicit causal chain from drug to target, cellular process, disease mechanism and phenotype;
3. stop where the evidence stops.

## Main result, in one paragraph

BUB1B is the **leading candidate gene, not a proven cause**. The data contain a known truncating BUB1B allele and a rare BUB1B missense change of unknown function. **Their phase (cis or trans) is unresolved**, and the **missense change cannot be classified as damaging**. TRIP13, CEP57 and CENATAC could not be ranked against each other. An intronic CEP57 read-level signal is **unresolved**. **No drug has direct evidence of benefit in MVA.** Two approved drugs remain **indirect research hypotheses only**: dasatinib (senescent-cell clearance, a downstream effect) and niacin (NAD+/SIRT2-dependent BUBR1 abundance, relevant only if residual BUBR1 protein exists). The functional experiments are **designs only**; none was performed. Technical confidence that a variant call is real does not establish pathogenicity.

## Files

| File | Content |
|---|---|
| `TRACK2_REPORT.md` | **The Track 2 detailed report** (draft for owner approval). It follows `REPORT_TEMPLATE.md` and includes the abstract and the Track 2 methods-form answers; owner-only fields are marked |
| `SCIENTIFIC_SUMMARY.md` | Workflow; the candidate variants by class; sequencing confidence versus function versus causality; four-gene comparison; competing explanations; findings of stages K2–K6 with evidence labels; what would change the conclusions |
| `METHODS.md` | Data, tools, versions, parameters, decision rules, validation and audit, analyses not run |
| `DRUG_HYPOTHESIS_ASSESSMENT.md` | The 12 drug candidates, their criteria, the ranking rule, the result and regulatory status |
| `FUNCTIONAL_TEST_DESIGNS.md` | Proposed experiments for the variants and the two surviving drug hypotheses (not performed), what each would discriminate, and why no published experiment can be graded |
| `DRUG_EVIDENCE_CARD_DASATINIB.md`, `DRUG_EVIDENCE_CARD_NIACIN.md` | The two surviving approved-drug hypotheses, each filled into the competition card template |
| `REFERENCES.md` | Sources, with the access level actually used (full text, abstract, database record) |
| `REPORT_TEMPLATE.md`, `DRUG_EVIDENCE_CARD_TEMPLATE.md` | Competition templates (unchanged) |

## Track 2 index

| Topic | Where |
|---|---|
| **Detailed report** (submission deliverable) | [Track 2 report](TRACK2_REPORT.md), [abstract](TRACK2_REPORT.md#abstract--500-words), [methods-form answers](TRACK2_REPORT.md#annex-track-2-methods-form-answers-sheet-track-2-methods), [causal evidence diagram](TRACK2_REPORT.md#figures) |
| Overall workflow (K2–K6) | [Workflow](SCIENTIFIC_SUMMARY.md#workflow) |
| Boundaries on every claim | [Boundaries that hold throughout](SCIENTIFIC_SUMMARY.md#boundaries-that-hold-throughout) |
| Candidate variants, by class | [Candidate variants](SCIENTIFIC_SUMMARY.md#the-participants-candidate-variants-by-class) |
| Sequencing confidence versus function versus causality | [Three separate questions](SCIENTIFIC_SUMMARY.md#three-separate-questions-for-the-candidate-pair) |
| **K2:** literature, four-gene comparison, competing explanations | [K2](SCIENTIFIC_SUMMARY.md#k2-literature-mechanism-and-competing-genes), [four-gene comparison](SCIENTIFIC_SUMMARY.md#four-gene-comparison), [competing explanations](SCIENTIFIC_SUMMARY.md#competing-explanations-and-their-current-status) |
| **K3:** read-level robustness, callability, structural screens, sensitivity | [K3](SCIENTIFIC_SUMMARY.md#k3-read-level-re-analysis), [methods](METHODS.md#read-level-re-analysis-k3-k4) |
| **K4:** phase, missense mechanisms, CEP57 signal | [K4](SCIENTIFIC_SUMMARY.md#k4-phase-missense-mechanism-and-the-cep57-signal) |
| **K5:** drug-repurposing assessment | [Assessment](DRUG_HYPOTHESIS_ASSESSMENT.md), [regulatory status](DRUG_HYPOTHESIS_ASSESSMENT.md#regulatory-status-as-checked-2026-10-24), [causal-chain links](DRUG_HYPOTHESIS_ASSESSMENT.md#causal-chain-link-status), [dasatinib card](DRUG_EVIDENCE_CARD_DASATINIB.md), [niacin card](DRUG_EVIDENCE_CARD_NIACIN.md) |
| **K6:** functional evidence and assay validity | [K6](SCIENTIFIC_SUMMARY.md#k6-functional-variant-assessment), [assay designs](FUNCTIONAL_TEST_DESIGNS.md#part-1-variant-function-assays-stage-k6) |
| Proposed experiments (designs only) | [Variant assays](FUNCTIONAL_TEST_DESIGNS.md#part-1-variant-function-assays-stage-k6), [what each discriminates](FUNCTIONAL_TEST_DESIGNS.md#what-each-assay-is-designed-to-tell-apart), [drug tests](FUNCTIONAL_TEST_DESIGNS.md#part-2-drug-hypothesis-tests-stage-k5) |
| Methods, software and parameters | [Software](METHODS.md#software), [reference data](METHODS.md#reference-data), [input data](METHODS.md#input-data) |
| Validation and audit (with their limits) | [Integrity controls](METHODS.md#integrity-controls) |
| Limitations and alternative explanations | [Competing explanations](SCIENTIFIC_SUMMARY.md#competing-explanations-and-their-current-status), [what would change the conclusions](SCIENTIFIC_SUMMARY.md#what-would-change-the-conclusions), [analyses not run](METHODS.md#analyses-not-run-and-why), [what the methods cannot show](METHODS.md#what-these-methods-cannot-show), [drug limits](DRUG_HYPOTHESIS_ASSESSMENT.md#limits) |
| References and access levels | [References](REFERENCES.md) |
| Reproducibility | [Reproducibility](#reproducibility) |

## Evidence labels

Every scientific statement carries one label:

| Label | Meaning |
|---|---|
| measured | Computed by us from the data, with a recorded script and output |
| database-observed | Read from a public database record (ClinVar, gnomAD, UniProt, openFDA, EMA) |
| predicted | A computational expectation (for example an NMD rule), not an observation |
| indirect | Published evidence about another variant, model or disease |
| hypothesis | A proposed explanation not yet tested |
| unknown | Not determinable with the available data |

## Reproducibility

- The patient-level analyses ran in approved private storage, under the organiser's data terms. Their inputs, outputs and scripts are restricted and are **not** in this repository; the scripts embed restricted inputs and patient-derived parameters.
- Re-running them needs the organiser's dataset under its terms.
- `METHODS.md` gives the tools, versions, parameters and reference data. `DRUG_HYPOTHESIS_ASSESSMENT.md` gives the full drug-level criteria and the ranking rule, so the drug categories can be re-derived by hand from this repository.
- This repository's checks (`../scripts/`, `../tests/`) confirm packaging and file syntax only. They do not test these findings.
- The analyses and their validation scripts were written by the same AI coding assistant, under the team's direction. The validation results show internal consistency, not independent validation (`METHODS.md`, "Integrity controls").
- Not produced: image figures (the report contains one text-based causal diagram), wet-lab results, mutant-structure or ΔΔG results.

## Data policy

- This folder contains no genotype, no read-level value, no genomic coordinate, no variant notation of the participant's alleles, no sample identifier and no phenotype list.
- The participant's alleles are described by class only ("a known truncating allele", "a rare missense change in the pseudokinase domain", "a deep-intronic variant of uncertain significance").
- The content is limited to what the organiser's rules let teams keep and report: candidate genes, mechanisms and drug candidates. No secondary or incidental finding is included.
