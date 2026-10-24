"""Deterministic K5 category rule for approved-drug research hypotheses — version 0.1.0.

**Scope.** This module re-applies the documented K5 ranking rule to drug-level criteria
(``DRUG_HYPOTHESIS_CRITERIA.tsv`` in this folder). It sorts research hypotheses into evidence categories. It is not an
efficacy estimate, a treatment recommendation or a clinical decision rule, and no category means that a drug benefits
anyone with MVA. The criteria values are curated judgements recorded in the K5 evidence assessment (abstract-level
literature, openFDA and EMA status); this module checks only that the categories follow from them.

Criteria used by the rule:

* ``C0_currently_approved``: ``yes`` or ``no`` (FDA/EMA status at assessment time);
* ``C1_target_relation``: ``direct``, ``regulator``, ``downstream``, ``opposing``, ``none`` or ``unknown``;
* ``C2_expected_direction``: ``restore``, ``compensate``, ``neutral`` or ``perturb``;
* ``C4_best_experimental_support``: ``drug-in-MVA-gene-model``, ``genetic-or-related-compound-in-MVA-gene-model``,
  ``drug-in-other-disease``, ``none`` or ``unknown``;
* ``C5_contradiction_or_harm``: ``minor``, ``moderate``, ``major-other``, ``major-disease-aligned-label`` or
  ``major-disease-aligned-experimental``.

C3, C6 and C7 are recorded for the reader and do not enter the category. Standard library only.
"""
from __future__ import annotations

import csv
from pathlib import Path

__version__ = "0.1.0"

CATEGORIES = (
    "stronger mechanistic research hypothesis",
    "plausible but indirect",
    "weak/nonspecific",
    "insufficient evidence to rank",
    "contradicted or potentially counterproductive",
    "out of scope: not a currently approved medicine",
)
ORDER = {name: rank for rank, name in enumerate(CATEGORIES, start=1)}
REQUIRED = ("candidate_id", "drug", "C0_currently_approved", "C1_target_relation", "C2_expected_direction",
            "C4_best_experimental_support", "C5_contradiction_or_harm")
ALLOWED = {
    "C0_currently_approved": {"yes", "no"},
    "C1_target_relation": {"direct", "regulator", "downstream", "opposing", "none", "unknown"},
    "C2_expected_direction": {"restore", "compensate", "neutral", "perturb"},
    "C4_best_experimental_support": {"drug-in-MVA-gene-model", "genetic-or-related-compound-in-MVA-gene-model",
                                     "drug-in-other-disease", "none", "unknown"},
    "C5_contradiction_or_harm": {"minor", "moderate", "major-other", "major-disease-aligned-label",
                                 "major-disease-aligned-experimental"},
}
MVA_MODEL_SUPPORT = ("drug-in-MVA-gene-model", "genetic-or-related-compound-in-MVA-gene-model")


def category(row: dict) -> str:
    """Return the K5 category for one candidate; the first matching rule wins."""
    for field, allowed in ALLOWED.items():
        if row.get(field) not in allowed:
            raise ValueError(f"{row.get('candidate_id', '?')}: {field}={row.get(field)!r} is not an allowed value")
    c1, c4, c5 = row["C1_target_relation"], row["C4_best_experimental_support"], row["C5_contradiction_or_harm"]
    if row["C0_currently_approved"] != "yes":
        return CATEGORIES[5]
    if c1 == "opposing" or row["C2_expected_direction"] == "perturb" or c5 == "major-disease-aligned-experimental":
        return CATEGORIES[4]
    major = c5.startswith("major")
    if c1 in ("direct", "regulator") and c4 == "drug-in-MVA-gene-model" and not major:
        return CATEGORIES[0]
    if c1 in ("direct", "regulator", "downstream") and c4 in MVA_MODEL_SUPPORT and not major:
        return CATEGORIES[1]
    if c1 == "unknown" and c4 == "unknown":
        return CATEGORIES[3]
    return CATEGORIES[2]


def load(path: Path) -> list[dict]:
    """Read the criteria TSV and check that every required column is present."""
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    missing = [c for c in REQUIRED if rows and c not in rows[0]]
    if missing:
        raise ValueError(f"missing columns: {', '.join(missing)}")
    return rows


def rank(rows: list[dict]) -> list[tuple[int, str, str, str]]:
    """Return (rank group, candidate_id, drug, category), sorted by rank group and then by input order."""
    out = [(ORDER[category(r)], r["candidate_id"], r["drug"], category(r)) for r in rows]
    return sorted(out, key=lambda item: item[0])


if __name__ == "__main__":
    criteria = Path(__file__).resolve().with_name("DRUG_HYPOTHESIS_CRITERIA.tsv")
    for group, cid, drug, cat in rank(load(criteria)):
        print(f"{group}\t{cid}\t{drug}\t{cat}")
