import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validator', ROOT / 'scripts/validate_track1.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

class SubmissionHazards(unittest.TestCase):
    def check(self, changes=None, extra=None):
        row = dict(zip(validator.HEADERS, ['PROBAND01','1','100001','A','G','1','100101','C','T','0.7','primary','test only']))
        row.update(changes or {})
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as directory:
            assert Path(directory).resolve().is_relative_to((ROOT / 'tests').resolve())
            path = Path(directory) / 'candidate.csv'
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=validator.HEADERS)
                writer.writeheader()
                writer.writerow(row)
                if extra:
                    writer.writerow({**row, **extra})
            return validator.validate(path, 'PROBAND01')

    def test_valid_pair(self):
        self.assertEqual(self.check(), [])

    def test_incomplete_pair(self):
        self.assertTrue(any('second allele' in e for e in self.check({'alt_2':''})))

    def test_nonfinite_probability(self):
        for value in ['nan','inf','0','-1','1.1']:
            with self.subTest(value=value):
                self.assertTrue(any('EPCR must be finite' in e for e in self.check({'epcr':value})))

    def test_wrong_case(self):
        self.assertTrue(any('identifier' in e for e in self.check({'proband_id':'OTHER'})))

    def test_secondary_rejected(self):
        self.assertTrue(any('secondary scoring' in e for e in self.check({'finding_type':'secondary'})))

    def test_reversed_duplicate_pair(self):
        self.assertTrue(any('duplicate candidate' in e for e in self.check(extra={'pos_1':'100101','ref_1':'C','alt_1':'T','pos_2':'100001','ref_2':'A','alt_2':'G','epcr':'0.6'})))

    def test_ordering(self):
        self.assertTrue(any('descending' in e for e in self.check(extra={'pos_1':'300001','pos_2':'300101','epcr':'0.8'})))

    def test_empty_header_rejected(self):
        self.assertTrue(validator.validate(ROOT / 'track1/SUBMISSION_HEADER_ONLY.csv', 'PROBAND01'))

    def test_fictional_fixture_cannot_be_submitted(self):
        path = ROOT / 'fixtures/synthetic/track1_example.csv'
        self.assertTrue(validator.validate(path, 'PROBAND01'))
        self.assertEqual(validator.validate(path, 'SYNTHETIC_ONLY', synthetic=True), [])

if __name__ == '__main__':
    unittest.main()
