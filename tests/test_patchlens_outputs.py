import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pl_validator', ROOT / 'scripts/validate_patchlens_outputs.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

EXAMPLE = json.loads((ROOT / 'patchlens_outputs/examples/synthetic_example.json').read_text(encoding='utf-8'))


def mutated(**changes):
    rec = copy.deepcopy(EXAMPLE)
    rec.update(changes)
    return rec


class RecordRules(unittest.TestCase):
    def test_example_is_valid(self):
        self.assertEqual(validator.validate_record(EXAMPLE), [])

    def test_call_must_be_null(self):
        self.assertTrue(any('call must be null' in e for e in validator.validate_record(mutated(call='pathogenic'))))

    def test_tier_must_be_e4(self):
        self.assertTrue(any('E4' in e for e in validator.validate_record(mutated(evidence_tier='E3'))))

    def test_restricted_data_rejected(self):
        self.assertTrue(any('restricted' in e for e in validator.validate_record(mutated(data_class='restricted'))))

    def test_metric_needs_available_status(self):
        rec = mutated(metrics={'example_metric': 0.5})
        self.assertTrue(any('must be null unless' in e for e in validator.validate_record(rec)))

    def test_available_may_carry_metric(self):
        rec = mutated(metrics={'example_metric': 0.5}, applicability={'status': 'available', 'reason': None})
        self.assertEqual(validator.validate_record(rec), [])

    def test_nonfinite_metric_rejected(self):
        rec = mutated(metrics={'m': float('nan')}, applicability={'status': 'available', 'reason': None})
        self.assertTrue(any('finite' in e for e in validator.validate_record(rec)))

    def test_abstain_needs_reason(self):
        rec = mutated(applicability={'status': 'abstain', 'reason': None})
        self.assertTrue(any('reason is required' in e for e in validator.validate_record(rec)))

    def test_unexpected_field_rejected(self):
        self.assertTrue(any('unexpected' in e for e in validator.validate_record(mutated(extra='x'))))

    def test_empty_boundaries_rejected(self):
        self.assertTrue(any('boundaries' in e for e in validator.validate_record(mutated(boundaries=[]))))

    def test_bad_hash_rejected(self):
        self.assertTrue(any('sha256' in e for e in validator.validate_record(mutated(artifact_sha256='abc'))))


class RepositoryGuard(unittest.TestCase):
    def build(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        return root

    def test_repository_is_clean(self):
        problems, count = validator.check_repository(ROOT)
        self.assertEqual(problems, [])
        self.assertGreaterEqual(count, 1)

    def test_structure_file_rejected(self):
        problems, _ = validator.check_repository(self.build({'patchlens_outputs/records/x.pdb': 'ATOM'}))
        self.assertTrue(any('forbidden file type' in p for p in problems))

    def test_code_in_outputs_rejected(self):
        problems, _ = validator.check_repository(self.build({'patchlens_outputs/records/x.py': 'print(1)'}))
        self.assertTrue(any('code is only allowed' in p for p in problems))

    def test_absolute_path_rejected(self):
        text = 'see C:' + '\\Users\\someone\\file'
        problems, _ = validator.check_repository(self.build({'patchlens_outputs/records/n.md': text}))
        self.assertTrue(any('absolute Windows path' in p for p in problems))

    def test_duplicate_record_id_rejected(self):
        body = json.dumps(EXAMPLE)
        root = self.build({'patchlens_outputs/records/a.json': body, 'patchlens_outputs/records/b.json': body})
        problems, _ = validator.check_repository(root)
        self.assertTrue(any('duplicates' in p for p in problems))


if __name__ == '__main__':
    unittest.main()
