# MVA-Hackathon

Public showcase repository for AIREA's entry to the Rare Disease MVA Hackathon 2026.

It holds the **outputs** that AIREA's PatchLens structural-evidence module produced for the competition, the competition-facing templates, and the checks that keep them consistent. It does **not** contain PatchLens source code, models, parameters, caches or structure files. PatchLens is developed in a separate, private AIREA repository.

## What PatchLens outputs mean here

- Every PatchLens record is structural evidence at tier **E4**, and its `call` field is always `null`.
- A record is never a diagnosis, a pathogenicity verdict or a treatment recommendation.
- Where PatchLens cannot assess a variant, the record says so (`not_assessed` or `abstain`) and every metric is `null`. A missing value is never written as zero.
- Any performance figure added to this repository must carry its dataset and n, and a named comparator.

## Layout

| Path | Contents |
|---|---|
| `patchlens_outputs/` | PatchLens-derived output records, their [specification](patchlens_outputs/SPEC.md) and JSON schema. This is the only place PatchLens results go. |
| `schemas/` | Proposed causal-convergence passport schema (v0.1). |
| `track1/` | Track 1 templates and the header-only submission CSV. |
| `track2/` | Track 2 evidence-card and report templates, and the draft Track 2 evidence summary (see [track2/README.md](track2/README.md)). |
| `fixtures/synthetic/` | Fictional examples that demonstrate the formats. They contain no patient data and no real result. |
| `scripts/` | Standard-library checks: `validate_track1.py` (CSV syntax) and `validate_patchlens_outputs.py` (output records and repository guard). |
| `tests/` | Unit tests for both checks. |

## Run the checks

Python 3.10 or newer. No dependencies.

```bash
python -m unittest discover -s tests
python scripts/validate_patchlens_outputs.py
python scripts/validate_track1.py fixtures/synthetic/track1_example.csv --synthetic --expected-proband SYNTHETIC_ONLY
```

The checks confirm packaging and file syntax. They do not measure biological correctness or competitive performance.

## Data and privacy

No patient data, variants, genomes or identifying phenotype are stored here. The competition dataset is access-restricted and stays in approved private storage. Candidate content is published only where the organizer's rules permit it.

## Contributing

PatchLens outputs are added by the PatchLens developer through pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence and attribution

This repository is licensed under [CC BY 4.0](LICENSE), consistent with the Hackathon's Official Rules for participant submissions. The gated competition dataset is not covered and is not redistributed; third-party material is cited, not relicensed. See [NOTICE.md](NOTICE.md).

## Acknowledgement

> "This work was made possible through the Hackathon, organized by Sage Bionetworks in partnership with the MVA Society, Hugging Face, and BEACON (The Benchmarking, Evaluation, and Assessment Consortium for Science), with prize sponsorship from AWS and Anthropic. We are deeply grateful to the child and their family who generously contributed their data and their story to advance research into this rare disease. We acknowledge their trust in making this Hackathon possible."
