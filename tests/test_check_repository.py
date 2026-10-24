import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guard', ROOT / 'scripts/check_repository.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


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
        self.assertEqual(guard.check_repository(ROOT), [])

    def test_structure_file_rejected(self):
        problems = guard.check_repository(self.build({'track2/x.pdb': 'ATOM'}))
        self.assertTrue(any('forbidden file type' in p for p in problems))

    def test_genomic_file_rejected(self):
        problems = guard.check_repository(self.build({'track2/x.vcf': '##fileformat'}))
        self.assertTrue(any('forbidden file type' in p for p in problems))

    def test_code_outside_scripts_and_tests_rejected(self):
        problems = guard.check_repository(self.build({'track2/x.py': 'print(1)'}))
        self.assertTrue(any('code is only allowed' in p for p in problems))

    def test_code_under_scripts_allowed(self):
        self.assertEqual(guard.check_repository(self.build({'scripts/x.py': 'print(1)'})), [])

    def test_absolute_windows_path_rejected(self):
        text = 'see C:' + '\\Users\\someone\\file'
        problems = guard.check_repository(self.build({'track2/n.md': text}))
        self.assertTrue(any('absolute Windows path' in p for p in problems))

    def test_absolute_unix_path_rejected(self):
        text = 'see /' + 'home/someone/file'
        problems = guard.check_repository(self.build({'track2/n.md': text}))
        self.assertTrue(any('absolute local path' in p for p in problems))

    def test_secret_like_string_rejected(self):
        text = 'token gh' + 'p_' + 'a' * 24
        problems = guard.check_repository(self.build({'track2/n.md': text}))
        self.assertTrue(any('GitHub token' in p for p in problems))

    def test_findings_name_the_file_not_its_content(self):
        text = 'see /' + 'home/someone/file'
        problems = guard.check_repository(self.build({'track2/n.md': text}))
        self.assertTrue(all('someone' not in p for p in problems))


if __name__ == '__main__':
    unittest.main()
