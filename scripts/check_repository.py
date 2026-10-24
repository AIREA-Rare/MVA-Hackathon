"""Guard the repository against restricted files, local paths and secrets.

Standard library only. Prints file names and the kind of finding, never file contents. Exit code 1 on any finding.
A passing run is a safety net, not a review: read your diff before you push.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '.github', '__pycache__', '.pytest_cache', '.venv'}
# Anything that would expose patient data, structures, models or credentials.
FORBIDDEN_EXTENSIONS = {
    '.pdb', '.cif', '.mmcif', '.ent', '.pt', '.pth', '.ckpt', '.safetensors', '.onnx',
    '.npz', '.npy', '.pkl', '.pickle', '.h5', '.hdf5', '.joblib', '.db', '.sqlite',
    '.vcf', '.gz', '.bam', '.cram', '.fastq', '.fq', '.fasta', '.fa', '.env', '.pem', '.key',
    '.zip', '.rar', '.7z', '.tar', '.ipynb', '.log',
}
CODE_EXTENSIONS = {'.py', '.sh', '.ps1', '.bat'}
CODE_DIRS = {'scripts', 'tests'}
TEXT_EXTENSIONS = {'.md', '.json', '.csv', '.tsv', '.txt', '.yml', '.yaml'}
LEAK_PATTERNS = [
    (re.compile(r'[A-Za-z]:\\+(?:Users|Desktop|Documents)\\', re.I), 'absolute Windows path'),
    (re.compile(r'(?<![\w.])/(?:Users|home)/[\w.-]+'), 'absolute local path'),
    (re.compile('gh[pousr]' + r'_[A-Za-z0-9]{20,}'), 'GitHub token'),
    (re.compile('AKIA' + r'[0-9A-Z]{16}'), 'AWS access key'),
    (re.compile('-----BEGIN [A-Z ]*' + 'PRIVATE KEY'), 'private key'),
]


def _files(root):
    for path in sorted(root.rglob('*')):
        if path.is_file() and not (set(path.relative_to(root).parts[:-1]) & SKIP_DIRS):
            yield path


def check_repository(root=ROOT):
    """Return the list of problems for the whole working tree."""
    root = Path(root)
    problems = []
    for path in _files(root):
        rel = path.relative_to(root)
        top = rel.parts[0]
        ext = path.suffix.lower()
        if ext in FORBIDDEN_EXTENSIONS:
            problems.append(f'{rel}: forbidden file type {ext}.')
            continue
        if ext in CODE_EXTENSIONS and top not in CODE_DIRS:
            problems.append(f'{rel}: code is only allowed under scripts/ and tests/.')
        if top not in CODE_DIRS and ext in TEXT_EXTENSIONS:
            text = path.read_text(encoding='utf-8', errors='replace')
            for pattern, label in LEAK_PATTERNS:
                if pattern.search(text):
                    problems.append(f'{rel}: contains a {label}.')
    return problems


def main():
    problems = check_repository()
    for p in problems:
        print(p)
    if problems:
        print(f'{len(problems)} problem(s) found.')
        return 1
    print('OK: no forbidden files, local paths or secret-like strings found.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
