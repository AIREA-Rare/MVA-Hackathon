"""Validate PatchLens output records and guard the public repository.

Standard library only. Prints findings, never record contents. Exit code 1 on any finding.
"""
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = 'patchlens_outputs'
SKIP_DIRS = {'.git', '.github', '__pycache__', '.pytest_cache', '.venv'}
OUTPUT_EXTENSIONS = {'.json', '.md', '.gitkeep'}
# Anything that would expose PatchLens internals, structures, models or patient data.
FORBIDDEN_EXTENSIONS = {
    '.pdb', '.cif', '.mmcif', '.ent', '.pt', '.pth', '.ckpt', '.safetensors', '.onnx',
    '.npz', '.npy', '.pkl', '.pickle', '.h5', '.hdf5', '.joblib', '.db', '.sqlite',
    '.vcf', '.gz', '.bam', '.cram', '.fastq', '.fq', '.fasta', '.fa', '.env', '.pem', '.key',
    '.zip', '.rar', '.7z', '.tar', '.ipynb', '.log',
}
CODE_EXTENSIONS = {'.py', '.sh', '.ps1', '.bat'}
CODE_DIRS = {'scripts', 'tests'}
LEAK_PATTERNS = [
    (re.compile(r'[A-Za-z]:\\+(?:Users|Desktop|Documents)\\', re.I), 'absolute Windows path'),
    (re.compile(r'(?<![\w.])/(?:Users|home)/[\w.-]+'), 'absolute local path'),
    (re.compile('gh[pousr]' + r'_[A-Za-z0-9]{20,}'), 'GitHub token'),
    (re.compile('AKIA' + r'[0-9A-Z]{16}'), 'AWS access key'),
    (re.compile('-----BEGIN [A-Z ]*' + 'PRIVATE KEY'), 'private key'),
]
SHA = re.compile(r'^[0-9a-f]{64}$')
STATUSES = {'available', 'not_assessed', 'abstain'}
TOP = ['schema_version', 'record_id', 'passport_id', 'data_class', 'backend', 'input',
       'applicability', 'metrics', 'uncertainty_notes', 'boundaries', 'evidence_tier',
       'call', 'artifact_sha256', 'acceptance_record', 'provenance']
INPUT = ['gene', 'transcript', 'protein_accession', 'residue_ref', 'residue_position',
         'residue_alt', 'structure_source', 'structure_chain', 'structure_sha256']


def _exact(obj, keys, where, errors):
    if not isinstance(obj, dict):
        errors.append(f'{where}: must be an object.')
        return False
    for k in keys:
        if k not in obj:
            errors.append(f'{where}: missing "{k}".')
    for k in obj:
        if k not in keys:
            errors.append(f'{where}: unexpected "{k}".')
    return True


def _str_or_null(value, where, errors):
    if value is not None and not isinstance(value, str):
        errors.append(f'{where}: must be a string or null.')


def _sha_or_null(value, where, errors):
    if value is not None and not (isinstance(value, str) and SHA.match(value)):
        errors.append(f'{where}: must be a lowercase sha256 hex string or null.')


def validate_record(rec):
    """Return a list of problems with one parsed output record."""
    errors = []
    if not _exact(rec, TOP, 'record', errors):
        return errors
    if rec.get('schema_version') != '0.1.0':
        errors.append('schema_version must be "0.1.0".')
    for k in ('record_id', 'passport_id'):
        if not isinstance(rec.get(k), str) or not rec.get(k):
            errors.append(f'{k} must be a non-empty string.')
    if rec.get('data_class') not in ('synthetic', 'permitted_summary'):
        errors.append('data_class must be synthetic or permitted_summary; restricted data is never allowed here.')
    if rec.get('evidence_tier') != 'E4':
        errors.append('evidence_tier must be "E4".')
    if 'call' in rec and rec['call'] is not None:
        errors.append('call must be null; PatchLens output is never a verdict.')

    backend = rec.get('backend')
    if _exact(backend, ['name', 'version', 'parameter_hash'], 'backend', errors):
        for k in ('name', 'version'):
            if not isinstance(backend.get(k), str) or not backend.get(k):
                errors.append(f'backend.{k} must be a non-empty string.')
        _sha_or_null(backend.get('parameter_hash'), 'backend.parameter_hash', errors)

    inp = rec.get('input')
    if _exact(inp, INPUT, 'input', errors):
        for k in INPUT:
            if k == 'residue_position':
                v = inp.get(k)
                if v is not None and not (isinstance(v, int) and not isinstance(v, bool) and v >= 1):
                    errors.append('input.residue_position must be a positive integer or null.')
            elif k == 'structure_sha256':
                _sha_or_null(inp.get(k), 'input.structure_sha256', errors)
            else:
                _str_or_null(inp.get(k), f'input.{k}', errors)

    app = rec.get('applicability')
    status = None
    if _exact(app, ['status', 'reason'], 'applicability', errors):
        status = app.get('status')
        if status not in STATUSES:
            errors.append('applicability.status must be available, not_assessed or abstain.')
        _str_or_null(app.get('reason'), 'applicability.reason', errors)
        if status in ('not_assessed', 'abstain') and not app.get('reason'):
            errors.append('applicability.reason is required when status is not_assessed or abstain.')

    metrics = rec.get('metrics')
    if not isinstance(metrics, dict):
        errors.append('metrics must be an object.')
    else:
        for name, value in metrics.items():
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                errors.append(f'metrics.{name} must be a finite number or null.')
            elif status != 'available':
                errors.append(f'metrics.{name} must be null unless applicability.status is available.')

    for k in ('uncertainty_notes', 'boundaries'):
        v = rec.get(k)
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            errors.append(f'{k} must be an array of strings.')
    if isinstance(rec.get('boundaries'), list) and not rec['boundaries']:
        errors.append('boundaries must contain at least one statement.')

    _sha_or_null(rec.get('artifact_sha256'), 'artifact_sha256', errors)
    _str_or_null(rec.get('acceptance_record'), 'acceptance_record', errors)
    if _exact(rec.get('provenance'), ['structure_license', 'attribution'], 'provenance', errors):
        for k in ('structure_license', 'attribution'):
            _str_or_null(rec['provenance'].get(k), f'provenance.{k}', errors)
    return errors


def _files(root):
    for path in sorted(root.rglob('*')):
        if path.is_file() and not (set(path.relative_to(root).parts[:-1]) & SKIP_DIRS):
            yield path


def check_repository(root=ROOT):
    """Return (problems, record_count) for the whole working tree."""
    root = Path(root)
    problems = []
    ids = {}
    count = 0
    for path in _files(root):
        rel = path.relative_to(root)
        top = rel.parts[0]
        ext = path.suffix.lower() if path.name != '.gitkeep' else '.gitkeep'
        if ext in FORBIDDEN_EXTENSIONS:
            problems.append(f'{rel}: forbidden file type {ext}.')
            continue
        if ext in CODE_EXTENSIONS and top not in CODE_DIRS:
            problems.append(f'{rel}: code is only allowed under scripts/ and tests/.')
        if top == OUT and ext not in OUTPUT_EXTENSIONS:
            problems.append(f'{rel}: only .json and .md files are allowed in {OUT}/.')
        if top not in CODE_DIRS and ext in {'.md', '.json', '.csv', '.tsv', '.txt', '.yml', '.yaml'}:
            text = path.read_text(encoding='utf-8', errors='replace')
            for pattern, label in LEAK_PATTERNS:
                if pattern.search(text):
                    problems.append(f'{rel}: contains a {label}.')
        is_record = (top == OUT and ext == '.json' and rel.name != 'patchlens_output.schema.json'
                     and len(rel.parts) > 2 and rel.parts[1] in ('records', 'examples'))
        if is_record:
            count += 1
            try:
                rec = json.loads(path.read_text(encoding='utf-8'))
            except (ValueError, UnicodeDecodeError):
                problems.append(f'{rel}: not valid UTF-8 JSON.')
                continue
            problems += [f'{rel}: {e}' for e in validate_record(rec)]
            rid = rec.get('record_id') if isinstance(rec, dict) else None
            if isinstance(rid, str):
                if rid in ids:
                    problems.append(f'{rel}: record_id duplicates {ids[rid]}.')
                ids[rid] = str(rel)
    return problems, count


def main():
    problems, count = check_repository()
    for p in problems:
        print(p)
    if problems:
        print(f'{len(problems)} problem(s) found.')
        return 1
    print(f'OK: {count} PatchLens record(s) checked; no forbidden files or leaks found.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
