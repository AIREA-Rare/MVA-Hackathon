# Contributing PatchLens outputs

This repository is public. Anything pushed here is visible to everyone and cached or indexed even if deleted later. Push **outputs only**.

## What may be pushed

- JSON output records under `patchlens_outputs/records/` that pass `scripts/validate_patchlens_outputs.py`.
- Short notes next to a record (`.md`) that describe what it is and its limits.
- Updates to the competition templates, schemas and checks.

## What must never be pushed

- PatchLens source code, notebooks, configs with tuned parameters, model weights, caches or logs.
- Structure files (`.pdb`, `.cif`) or any dMaSIF/PeSTo code or weights.
- Patient data of any kind, including genome-derived tables and identifying phenotype.
- Absolute local paths, credentials, tokens or `.env` files.
- Anything from the private AIREA repositories beyond the output record itself.

`scripts/validate_patchlens_outputs.py` rejects the file types, absolute paths and secret-like strings above, but it is a safety net, not a review. Read your diff before you push.

## Workflow

1. `git pull` on `main`.
2. Branch: `git switch -c <name>/<topic>`. Never commit straight to `main`.
3. Add or update records in `patchlens_outputs/records/`.
4. Run the checks:

   ```bash
   python scripts/validate_patchlens_outputs.py
   python -m unittest discover -s tests
   ```

5. Commit with a short imperative message, for example `patchlens_outputs: add structural evidence records for batch 1`.
6. Push and open a pull request to `main`. The checks also run in GitHub Actions.
7. The repository owner reviews and merges.

## Record rules

See [patchlens_outputs/SPEC.md](patchlens_outputs/SPEC.md). In short: `evidence_tier` is `E4`, `call` is `null`, unavailable values are `null`, and any performance number is written with its dataset, n and comparator.
