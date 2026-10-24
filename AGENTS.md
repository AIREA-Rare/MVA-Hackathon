# AGENTS.md: rules for AI coding agents in MVA-Hackathon

Codex, Claude Code and any other agent working in this repo must follow this file.

## What this repo is

The AIREA repository for the Rare Disease MVA Hackathon 2026, focused on **Track 2** (drug-repurposing hypotheses for MVA). It is **private now and will be made public at submission**, so treat every file as public. It holds the Track 2 report, methods and sanitised analysis code.

## Hard rules

1. **Nothing restricted.** No patient data: no variants, genomes, genotype tables or identifying phenotype, in files, notes or commit messages. No raw sequence, alignment or reference files (`.vcf`, `.bam`, `.fastq`, `.fasta` and similar), no structure files (`.pdb`, `.cif`), no model weights or caches. The participant's variants are described by class only.
2. **No secrets or local paths.** No tokens, keys, `.env` files, or absolute local filesystem paths (Windows drive paths, or paths under `/Users/` or `/home/`).
3. **Hypotheses, not verdicts.** Track 2 content is research hypotheses. It is never a diagnosis, a pathogenicity verdict or a treatment recommendation. Unavailable values are `unknown` or `null`, never `0`.
4. **Numbers carry their cohort.** Any performance figure is written with its dataset, n and a named comparator. A bare number is a defect. Do not write "validated", "proves", "outperforms", "state of the art" or "novel" without a named comparator and a number in the same sentence.
5. **Isolation.** Do not read from or reference other private AIREA repositories or folders from here, and do not add their internals (for example PatchLens). Add only finished material.
6. **Licensing.** Do not ingest OMIM content. Never add dMaSIF or PeSTo code or weights. Record the licence and attribution of any third-party source (AlphaFold DB is CC-BY-4.0).

## Workflow (do all of this yourself)

1. `git switch main` and `git pull`.
2. `git switch -c <person>/<topic>`, for example `ata/track2-references`. Never commit to `main`.
3. Make a focused change.
4. Run both checks. Both must pass:
   ```bash
   py scripts/check_repository.py
   py -m unittest discover -s tests
   ```
5. Read your own diff (`git diff --staged`) and check it against the hard rules above.
6. Before any number or finding goes into a note, commit message or PR description, run the `science-examiner` check if your environment has it. Otherwise re-check rules 3 and 4 by hand.
7. Commit with a small imperative message, for example `track2: correct a reference`.
8. `git push -u origin <branch>` and open a pull request to `main` with `gh pr create`. In the description, say what changed, which cohort and n any figure covers, and that nothing in it is a diagnosis or treatment recommendation.
9. GitHub Actions runs the same checks. If they fail, fix the cause and push again. Do not weaken or skip a check.

## Review and merge

`main` is protected. A pull request needs one approval from the repository owner, so **do not merge, and do not try to bypass the rules or force-push**. After opening the PR, tell your human that it is waiting for the owner's review and give the PR link.

## When unsure

Ask your human. Do not guess about licensing, data provenance, or anything that would make a claim stronger or expose another AIREA repository's internals.
