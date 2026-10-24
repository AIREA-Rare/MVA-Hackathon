# MVA-Hackathon

**Mechanism-first drug-repurposing hypotheses for mosaic variegated aneuploidy (MVA).**
AIREA's Track 2 entry to the Rare Disease MVA Hackathon 2026.

> **Research evidence assessment, not medical advice.** Nothing here is a diagnosis, a clinical variant classification or a treatment recommendation, and no dose is proposed. No wet-lab experiment was performed. No patient data are in this repository.

## The question

Track 2 asks for repurposed, currently approved drugs that are supported by analysis of the participant's genetic data, together with the mechanism of the variants (loss or gain of function, pathway disrupted, downstream consequence). The submissions are hypotheses for follow-up, not evidence that a medicine works.

## Approach

1. **Establish what the data can show.** Variant quality control, locus-targeted read-level re-analysis, transcript and population checks, and an explicit list of what stays unresolved.
2. **Test every drug idea as a causal chain.** Drug → target → cellular process → disease mechanism → phenotype. Each link is scored for supporting and for contradicting evidence, FDA and EMA status is verified, and a deterministic, documented rule assigns the category.
3. **Stop where the evidence stops.** Every statement carries an evidence label, and the chain is shown where it breaks.

```
variants ─► causal gene ─► molecular mechanism ─► cellular defect ─► drug target ─► phenotype
             UNRESOLVED     UNRESOLVED (missense)   gene level only     indirect      untested
```

## Findings at a glance

- **BUB1B is the leading candidate gene, not a proven cause.** The data contain a known truncating *BUB1B* allele and a rare *BUB1B* missense change of unknown function. It leads because it has the complete set of genetic ingredients; that is completeness of a mechanism, not evidence of causation.
- **Phase (cis or trans) is unresolved**, and **the missense change cannot be classified as damaging.**
- *TRIP13*, *CEP57* and *CENATAC* could not be ranked against each other. An intronic *CEP57* read-level signal is unresolved.
- **No drug has direct evidence of benefit in MVA.** Twelve candidates were assessed:

| Category (deterministic rule) | Candidates |
|---|---|
| Stronger mechanistic research hypothesis | none |
| Plausible but indirect | niacin (NAD+/SIRT2-dependent BUBR1 abundance; relevant only if residual BUBR1 protein exists); dasatinib (senescent-cell clearance, a downstream effect) |
| Weak or nonspecific | gentamicin, dactinomycin, somatropin |
| Contradicted or potentially counterproductive | acetylcysteine, bortezomib, vincristine, microtubule-poison / Aurora / PLK1 inhibitor class |
| Out of scope (not currently approved, or a combination with an unapproved component) | NMN / nicotinamide riboside / nicotinamide; ataluren; dasatinib + quercetin |

- The two surviving ideas are **indirect research hypotheses only.** The experiments in [`track2/FUNCTIONAL_TEST_DESIGNS.md`](track2/FUNCTIONAL_TEST_DESIGNS.md) are **designs; none was performed.**
- The decisive next evidence is the phase of the two *BUB1B* variants and the function of the missense change. Their outcome changes the drug choice.

## Where to start

| You want | Open |
|---|---|
| The full Track 2 report (abstract, mechanism, evidence for and against, drug rationale, experiments, AI-use disclosure, references) | [`track2/AIREA_track2_report.md`](track2/AIREA_track2_report.md) |
| The official methods-description workbook, Track 2 sheet filled | [`track2/AIREA_track2_methods_description_form.xlsx`](track2/AIREA_track2_methods_description_form.xlsx) |
| A guided index to every section, by topic | [`track2/README.md`](track2/README.md) |
| The twelve candidates and the ranking rule | [`track2/DRUG_HYPOTHESIS_ASSESSMENT.md`](track2/DRUG_HYPOTHESIS_ASSESSMENT.md) |
| The two surviving hypotheses as evidence cards | [`track2/DRUG_EVIDENCE_CARD_NIACIN.md`](track2/DRUG_EVIDENCE_CARD_NIACIN.md), [`track2/DRUG_EVIDENCE_CARD_DASATINIB.md`](track2/DRUG_EVIDENCE_CARD_DASATINIB.md) |
| The analysis code and how to run it | [`scripts/track2/README.md`](scripts/track2/README.md) |

## Layout

| Path | Contents |
|---|---|
| `track2/` | The report, the methods workbook, the scientific summary, methods, drug assessment, functional-test designs, references, evidence cards and the competition templates |
| `scripts/track2/` | The sanitised analysis scripts behind the report, in run order, with templates for the private configuration |
| `scripts/` | `validate_patchlens_outputs.py`, the output-record check and repository guard |
| `schemas/` | Proposed causal-convergence passport schema (v0.1) |
| `patchlens_outputs/` | Optional structural-evidence output records for the PatchLens module, their [specification](patchlens_outputs/SPEC.md) and JSON schema. This is the only place PatchLens results go |
| `fixtures/synthetic/` | Fictional examples that demonstrate the formats. They contain no patient data and no real result |
| `tests/` | Unit tests for the drug-ranking rule and the output-record check |

## Reproducibility

- **Without the dataset:** the drug categories can be re-derived. Run `python scripts/track2/k5/drug_ranking.py`; the unit test checks that all twelve published categories follow from the criteria table. The criteria values are curated judgements: the test checks that the categories follow from them, not that the judgements are right.
- **With the dataset:** the analysis scripts in [`scripts/track2/`](scripts/track2/README.md) are the ones actually used. Participant-specific values sit in git-ignored private files, and committed templates document every key. Re-running them needs the organiser's gated dataset under its terms, and the tools and versions in [`track2/METHODS.md`](track2/METHODS.md).
- **Not reproducible from this repository alone:** the patient-level numbers, and the ledger and table builders that embed restricted evidence text.
- The analyses and their validation scripts were written by the same AI coding assistant, under the team's direction. Their validation results show internal consistency, not independent validation.

```bash
python -m unittest discover -s tests          # unit tests (Python 3.12 in CI; standard library only)
python scripts/validate_patchlens_outputs.py  # output records and repository guard
python scripts/track2/k5/drug_ranking.py      # re-derive the twelve drug categories
```

The checks confirm packaging, file syntax and the ranking rule. They do not test the biological findings or measure competitive performance.

## Evidence labels

| Label | Meaning |
|---|---|
| measured | Computed by us from the data, with a recorded script and output |
| database-observed | Read from a public database record (ClinVar, gnomAD, UniProt, openFDA, EMA) |
| predicted | A computational expectation (for example an NMD rule), not an observation |
| indirect | Published evidence about another variant, model or disease |
| hypothesis | A proposed explanation not yet tested |
| unknown | Not determinable with the available data |

Stages: **K2** literature, mechanism and competing genes · **K3** read-level re-analysis · **K4** phase, missense mechanism and the *CEP57* signal · **K5** drug-repurposing hypotheses · **K6** functional variant assessment.

## Data and privacy

The analysis used a single-sample dataset provided by the organiser, under the organiser's terms. It is access-restricted, stays in approved private storage and is not redistributed here. This repository contains no genotype, read-level value, genomic coordinate, variant notation of the participant's alleles, sample identifier, phenotype list or secondary finding; the alleles are described **by class only**. Candidate content is published only where the organiser's rules permit it.

## AI assistance

The analysis scripting, public-source retrieval, evidence tabulation and drafting used an AI coding assistant under the team's direction. Provider, plan, data-handling setting and what was processed are stated in the report ([section 14](track2/AIREA_track2_report.md#14-privacy-ethics-and-ai-use-disclosure)) and in the methods workbook (A9).

## PatchLens (optional module)

PatchLens structural evidence is not required for this Track 2 entry. If records are added, each is tier **E4** with `call` always `null`, never a diagnosis or a pathogenicity verdict, and unavailable values are `null`, never zero. PatchLens source code, models, parameters, caches and structure files are not in this repository; PatchLens is developed in a separate, private AIREA repository. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Limitations

- Phase of the *BUB1B* variants and the function of the missense change are unresolved, so every *BUB1B*-directed drug idea inherits that uncertainty.
- Variant classes that short reads or locus-targeted recovery cannot detect are not assessed.
- Literature was read mostly at abstract level, and searches read first result pages only. Each reference states the access level actually used.
- Regulatory status was checked for the FDA and, where pages exist, the EMA.
- No wet-lab data. The hypotheses are for follow-up and do not demonstrate efficacy.

## Licence and attribution

This repository is licensed under [CC BY 4.0](LICENSE), consistent with the Hackathon's Official Rules for participant submissions. The gated competition dataset is not covered and is not redistributed; third-party material is cited, not relicensed. See [NOTICE.md](NOTICE.md).

## Acknowledgement

> "This work was made possible through the Hackathon, organized by Sage Bionetworks in partnership with the MVA Society, Hugging Face, and BEACON (The Benchmarking, Evaluation, and Assessment Consortium for Science), with prize sponsorship from AWS and Anthropic. We are deeply grateful to the child and their family who generously contributed their data and their story to advance research into this rare disease. We acknowledge their trust in making this Hackathon possible."
