# AGENTS.md: rules for AI coding agents in MVA-Hackathon

Codex, Claude Code and any other agent working in this repo must follow this file.

## What this repo is

A showcase repository for the Rare Disease MVA Hackathon 2026. It is **private now and will be made public at submission**, so treat every file as public. It holds PatchLens **outputs** only. PatchLens itself is developed in a separate private repository and must never appear here.

## Hard rules

1. **Outputs only.** Never add PatchLens source code, notebooks, tuned parameters, model weights, caches, logs, or structure files (`.pdb`, `.cif`). Never add dMaSIF or PeSTo code or weights.
2. **No patient data.** No variants, genomes, genotype tables or identifying phenotype, in files, notes or commit messages.
3. **No secrets or local paths.** No tokens, keys, `.env` files, or absolute local filesystem paths (Windows drive paths, or paths under `/Users/` or `/home/`).
4. **Evidence tier.** Every PatchLens record is tier `E4` with `call: null`. It is never a diagnosis, a pathogenicity verdict or a treatment recommendation. Unavailable values are `null`, never `0`.
5. **Numbers carry their cohort.** Any performance figure is written with its dataset, n and a named comparator. A bare number is a defect. Do not write "validated", "proves", "outperforms", "state of the art" or "novel" without a named comparator and a number in the same sentence.
6. **Isolation.** Do not read from or reference other private AIREA repositories or folders from here. Add only the finished output record.
7. **Licensing.** Do not ingest OMIM content. Record the licence and attribution of any structure source in the record's `provenance` field (AlphaFold DB is CC-BY-4.0).

## Where PatchLens results go

Only `patchlens_outputs/records/`, one `.json` file per record, in the format in `patchlens_outputs/SPEC.md` (schema: `patchlens_outputs/patchlens_output.schema.json`). A fictional example is in `patchlens_outputs/examples/`. Allowed file types there: `.json` and `.md`.

## Workflow for adding an output (do all of this yourself)

1. `git switch main` and `git pull`.
2. `git switch -c <person>/<topic>`, for example `ata/structural-records-batch-1`. Never commit to `main`.
3. Add or update records in `patchlens_outputs/records/`. Keep the change to that folder unless the human asks otherwise.
4. Run both checks. Both must pass:
   ```bash
   py scripts/validate_patchlens_outputs.py
   py -m unittest discover -s tests
   ```
5. Read your own diff (`git diff --staged`) and check it against the hard rules above.
6. Before any number or finding goes into a note, commit message or PR description, run the `science-examiner` check if your environment has it. Otherwise re-check rules 4 and 5 by hand.
7. Commit with a small imperative message, for example `patchlens_outputs: add structural evidence records for batch 1`.
8. `git push -u origin <branch>` and open a pull request to `main` with `gh pr create`. In the description, say what the records are, which cohort and n they cover, and that they are E4 with `call: null`.
9. GitHub Actions runs the same checks. If they fail, fix the cause and push again. Do not weaken or skip a check.

## Review and merge

`main` is protected. A pull request needs one approval from the repository owner, so **do not merge, and do not try to bypass the rules or force-push**. After opening the PR, tell your human that it is waiting for the owner's review and give the PR link.

## When unsure

Ask your human. Do not guess about licensing, data provenance, or anything that would make a claim stronger or expose PatchLens internals.
