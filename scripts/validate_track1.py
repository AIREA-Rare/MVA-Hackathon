"""Strict local CSV syntax checks; no genotype, phase or clinical validation."""
import argparse
import csv
import math
from pathlib import Path
import re

HEADERS = ['proband_id', 'chrom_1', 'pos_1', 'ref_1', 'alt_1',
           'chrom_2', 'pos_2', 'ref_2', 'alt_2', 'epcr', 'finding_type', 'notes']

def validate(path, expected_proband, synthetic=False, allow_secondary=False):
    errors = []
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != HEADERS:
            return ['Header must match the complete organizer template exactly.']
        rows = list(reader)
    if not 1 <= len(rows) <= 10:
        errors.append('Submission requires 1 to 10 candidate rows.')
    if synthetic and expected_proband != 'SYNTHETIC_ONLY':
        errors.append('Synthetic mode requires the fictional SYNTHETIC_ONLY identifier.')
    if not synthetic and expected_proband != 'PROBAND01':
        errors.append('Current organizer UI expects PROBAND01; resolve any dataset mismatch before submission.')
    previous_epcr = float('inf')
    seen = set()
    for i, raw in enumerate(rows, start=1):
        prefix = f'Row {i}: '
        if None in raw or any(value is None for value in raw.values()):
            errors.append(prefix + 'wrong number of columns.')
            continue
        row = {k: v.strip() for k, v in raw.items()}
        if row['proband_id'] != expected_proband:
            errors.append(prefix + 'proband identifier does not match the confirmed case.')
        if not synthetic and ('SYNTHETIC' in row['proband_id'].upper() or 'fictional' in row['notes'].lower()):
            errors.append(prefix + 'fictional fixture cannot be a real submission.')
        if row['finding_type'] not in ('primary', 'secondary'):
            errors.append(prefix + 'finding_type must be primary or secondary.')
        elif row['finding_type'] == 'secondary' and not allow_secondary:
            errors.append(prefix + 'secondary scoring/release requires organizer clarification.')
        try:
            epcr = float(row['epcr'])
            if not math.isfinite(epcr) or not 0 < epcr <= 1:
                raise ValueError
            if epcr > previous_epcr:
                errors.append(prefix + 'EPCR must be ordered descending.')
            previous_epcr = epcr
        except ValueError:
            errors.append(prefix + 'EPCR must be finite and in (0, 1].')
        second = [row[k] for k in ('chrom_2', 'pos_2', 'ref_2', 'alt_2')]
        if any(second) and not all(second):
            errors.append(prefix + 'second allele fields must be all populated or all blank.')
        alleles = []
        for side in (1, 2) if all(second) else (1,):
            chrom = row[f'chrom_{side}'].removeprefix('chr')
            if chrom not in {str(n) for n in range(1, 23)} | {'X', 'Y', 'MT', 'M'}:
                errors.append(prefix + f'allele {side} chromosome is not a supported GRCh38 chromosome.')
            pos = row[f'pos_{side}']
            if not re.fullmatch(r'[0-9]+', pos) or int(pos) <= 0:
                errors.append(prefix + f'allele {side} position must be a positive integer.')
            ref, alt = row[f'ref_{side}'], row[f'alt_{side}']
            if not re.fullmatch(r'[ACGTN]+', ref) or not re.fullmatch(r'[ACGTN]+', alt):
                errors.append(prefix + f'allele {side} requires explicit uppercase sequence alleles; symbolic SVs need clarification.')
            elif ref == alt:
                errors.append(prefix + f'allele {side} REF and ALT must differ.')
            alleles.append((chrom, str(int(pos)) if pos.isdigit() else pos, ref, alt))
        if len(alleles) == 2 and alleles[0] == alleles[1]:
            errors.append(prefix + 'a pair cannot repeat the same allele twice.')
        candidate = tuple(sorted(alleles))
        if candidate in seen:
            errors.append(prefix + 'duplicate candidate, including reversed pair order.')
        seen.add(candidate)
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path')
    parser.add_argument('--expected-proband', required=True)
    parser.add_argument('--synthetic', action='store_true')
    parser.add_argument('--allow-secondary', action='store_true', help='Use only after organizer scoring/release clarification.')
    args = parser.parse_args()
    try:
        errors = validate(args.csv_path, args.expected_proband, args.synthetic, args.allow_secondary)
    except (OSError, UnicodeError, csv.Error):
        print('FAIL: file cannot be parsed; inspect privately. No rows are printed.')
        return 1
    for error in errors:
        print('FAIL:', error)
    if not errors:
        print('PASS: local CSV syntax only. Biology, normalization, phase and release permissions remain separate reviews.')
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
