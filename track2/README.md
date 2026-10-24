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
| `SCIENTIFIC_SUMMARY.md` | Workflow; the candidate variants by class; sequencing confidence versus function versus causality; four-gene comparison; competing explanations; findings of stages K2–K6 with evidence labels; what would change the conclusions |
| `METHODS.md` | Data, tools, versions, parameters, decision rules, validation and audit, analyses not run |
| `DRUG_HYPOTHESIS_ASSESSMENT.md` | The 12 drug candidates, their criteria, the ranking rule, the result and regulatory status |
| `FUNCTIONAL_TEST_DESIGNS.md` | Proposed experiments for the variants and the two surviving drug hypotheses (not performed), what each would discriminate, and why no published experiment can be graded |
| `REFERENCES.md` | Sources, with the access level actually used (full text, abstract, database record) |
| `REPORT_TEMPLATE.md`, `DRUG_EVIDENCE_CARD_TEMPLATE.md` | Competition templates (unchanged) |

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

## Data policy

- This folder contains no genotype, no read-level value, no genomic coordinate, no variant notation of the participant's alleles, no sample identifier and no phenotype list.
- The participant's alleles are described by class only ("a known truncating allele", "a rare missense change in the pseudokinase domain", "a deep-intronic variant of uncertain significance").
- The content is limited to what the organiser's rules let teams keep and report: candidate genes, mechanisms and drug candidates. No secondary or incidental finding is included.
