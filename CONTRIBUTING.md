# Contributing

This repository will be public. Anything pushed here is visible to everyone and cached or indexed even if deleted later.

## What must never be pushed

- Patient data of any kind, including genome-derived tables and identifying phenotype. The participant's variants are described by class only.
- Raw sequence, alignment or reference files, structure files (`.pdb`, `.cif`), model weights or caches.
- Absolute local paths, credentials, tokens or `.env` files. Participant-specific values belong in the git-ignored private configuration files that `scripts/track2/` documents.
- Material from other private AIREA repositories.

`scripts/check_repository.py` rejects the file types, absolute paths and secret-like strings above, but it is a safety net, not a review. Read your diff before you push.

## Workflow

1. `git pull` on `main`.
2. Branch: `git switch -c <name>/<topic>`. Never commit straight to `main`.
3. Make a focused change.
4. Run the checks:

   ```bash
   python scripts/check_repository.py
   python -m unittest discover -s tests
   ```

5. Commit with a short imperative message, for example `track2: correct a reference`.
6. Push and open a pull request to `main`. The checks also run in GitHub Actions.
7. The repository owner reviews and merges.

## Content rules

Track 2 content is research hypotheses, never a diagnosis or a treatment recommendation. Any performance number is written with its dataset, n and a named comparator.
