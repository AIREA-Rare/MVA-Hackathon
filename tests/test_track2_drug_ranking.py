"""Tests for scripts/track2/k5/drug_ranking.py (K5 drug-hypothesis category rule). Uses drug-level criteria only; no patient value is used."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("drug_ranking", ROOT / "scripts/track2/k5/drug_ranking.py")
dr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dr)

CRITERIA = ROOT / "scripts/track2/k5/DRUG_HYPOTHESIS_CRITERIA.tsv"
# Categories as published in the K5 assessment (track2/DRUG_HYPOTHESIS_ASSESSMENT.md).
EXPECTED = {
    "WP5-H1": "plausible but indirect",
    "WP5-R1": "plausible but indirect",
    "WP5-H2": "weak/nonspecific",
    "K25-D1": "weak/nonspecific",
    "K25-D3": "weak/nonspecific",
    "WP5-R5": "contradicted or potentially counterproductive",
    "WP5-R6": "contradicted or potentially counterproductive",
    "WP5-R7": "contradicted or potentially counterproductive",
    "K25-D2": "contradicted or potentially counterproductive",
    "WP5-R2": "out of scope: not a currently approved medicine",
    "WP5-R3": "out of scope: not a currently approved medicine",
    "WP5-R4": "out of scope: not a currently approved medicine",
}


def row(**overrides):
    base = {"candidate_id": "SYN-1", "drug": "synthetic", "C0_currently_approved": "yes",
            "C1_target_relation": "regulator", "C2_expected_direction": "restore",
            "C4_best_experimental_support": "drug-in-MVA-gene-model", "C5_contradiction_or_harm": "minor"}
    base.update(overrides)
    return base


class PublishedCriteria(unittest.TestCase):
    def setUp(self):
        self.rows = dr.load(CRITERIA)

    def test_all_twelve_candidates_present_once(self):
        ids = [r["candidate_id"] for r in self.rows]
        self.assertEqual(len(ids), 12)
        self.assertEqual(set(ids), set(EXPECTED))

    def test_recomputed_categories_match_published(self):
        for r in self.rows:
            self.assertEqual(dr.category(r), EXPECTED[r["candidate_id"]], r["candidate_id"])

    def test_no_candidate_is_a_stronger_hypothesis(self):
        self.assertNotIn(dr.CATEGORIES[0], {dr.category(r) for r in self.rows})

    def test_no_candidate_has_direct_mva_evidence(self):
        self.assertEqual({r["C3_direct_MVA_evidence"] for r in self.rows}, {"none"})

    def test_rank_is_sorted_by_group(self):
        groups = [g for g, _, _, _ in dr.rank(self.rows)]
        self.assertEqual(groups, sorted(groups))
        self.assertEqual(dr.rank(self.rows)[0][1], "WP5-H1")


class Rule(unittest.TestCase):
    def test_unapproved_is_out_of_scope_before_anything_else(self):
        self.assertEqual(dr.category(row(C0_currently_approved="no")), dr.CATEGORIES[5])

    def test_opposing_or_perturbing_is_contradicted(self):
        self.assertEqual(dr.category(row(C1_target_relation="opposing")), dr.CATEGORIES[4])
        self.assertEqual(dr.category(row(C2_expected_direction="perturb")), dr.CATEGORIES[4])
        self.assertEqual(dr.category(row(C5_contradiction_or_harm="major-disease-aligned-experimental")),
                         dr.CATEGORIES[4])

    def test_stronger_needs_the_drug_itself_in_an_mva_gene_model(self):
        self.assertEqual(dr.category(row()), dr.CATEGORIES[0])
        self.assertEqual(dr.category(row(C1_target_relation="downstream")), dr.CATEGORIES[1])
        self.assertEqual(dr.category(row(C4_best_experimental_support="genetic-or-related-compound-in-MVA-gene-model")),
                         dr.CATEGORIES[1])

    def test_major_harm_blocks_the_upper_categories(self):
        self.assertEqual(dr.category(row(C5_contradiction_or_harm="major-other")), dr.CATEGORIES[2])

    def test_unknown_target_and_support_is_unrankable(self):
        self.assertEqual(dr.category(row(C1_target_relation="unknown", C4_best_experimental_support="unknown")),
                         dr.CATEGORIES[3])

    def test_invalid_value_is_rejected(self):
        with self.assertRaises(ValueError):
            dr.category(row(C1_target_relation="maybe"))


if __name__ == "__main__":
    unittest.main()
