"""K6: local, public-data evidence for variant function (no downloads, no new software).
 (a) paralog comparison: Smith-Waterman (BLOSUM62, affine gaps 11/1) of the BUB1B 'Protein kinase' domain (UniProt
     766-1050) against human BUB1 (O43683) from the local UniProt reference proteome; reports the BUB1 residue aligned to
     the P residue and local identity. A single paralog is weak evidence and is not cross-species conservation.
 (b) ClinVar records (local VCF 2026-10-04) within +-10 residues of the P residue, mapped through MANE CDS.
 (c) gnomAD v4.1.1 exome neighbourhood summary from the T2AA package (reused, not recomputed).
 (d) annotation support of the non-MANE CENATAC transcript (GFF3 tags).
Writes private_runs/K6_local.json; prints categories and public database facts only.
usage: python3 -B -I k6_local.py"""
import gzip
import json
import os
import re
import subprocess

P = os.environ["MVA_DATA_ROOT"]
K6 = f"{P}/out/T2K6_variant_function_2026-10-24"
os.umask(0o077)
sh = lambda c: subprocess.run(c, capture_output=True, text=True).stdout
T = 1002
res = {}
# ---------------- (a) paralog alignment
seqs, cur = {}, None
with gzip.open(f"{P}/ref/uniprot_2026_03/UP000005640_9606.fasta.gz", "rt") as fh:
    for ln in fh:
        if ln.startswith(">"):
            acc = ln.split("|")[1] if "|" in ln else ln[1:].split()[0]
            cur = acc if acc in ("O60566", "O43683") else None
            if cur:
                seqs[cur] = []
        elif cur:
            seqs[cur].append(ln.strip())
seqs = {k: "".join(v) for k, v in seqs.items()}
AA = "ARNDCQEGHILKMFPSTWYV"
B62 = """4 -1 -2 -2 0 -1 -1 0 -2 -1 -1 -1 -1 -2 -1 1 0 -3 -2 0
-1 5 0 -2 -3 1 0 -2 0 -3 -2 2 -1 -3 -2 -1 -1 -3 -2 -3
-2 0 6 1 -3 0 0 0 1 -3 -3 0 -2 -3 -2 1 0 -4 -2 -3
-2 -2 1 6 -3 0 2 -1 -1 -3 -4 -1 -3 -3 -1 0 -1 -4 -3 -3
0 -3 -3 -3 9 -3 -4 -3 -3 -1 -1 -3 -1 -2 -3 -1 -1 -2 -2 -1
-1 1 0 0 -3 5 2 -2 0 -3 -2 1 0 -3 -1 0 -1 -2 -1 -2
-1 0 0 2 -4 2 5 -2 0 -3 -3 1 -2 -3 -1 0 -1 -3 -2 -2
0 -2 0 -1 -3 -2 -2 6 -2 -4 -4 -2 -3 -3 -2 0 -2 -2 -3 -3
-2 0 1 -1 -3 0 0 -2 8 -3 -3 -1 -2 -1 -2 -1 -2 -2 2 -3
-1 -3 -3 -3 -1 -3 -3 -4 -3 4 2 -3 1 0 -3 -2 -1 -3 -1 3
-1 -2 -3 -4 -1 -2 -3 -4 -3 2 4 -2 2 0 -3 -2 -1 -2 -1 1
-1 2 0 -1 -3 1 1 -2 -1 -3 -2 5 -1 -3 -1 0 -1 -3 -2 -2
-1 -1 -2 -3 -1 0 -2 -3 -2 1 2 -1 5 0 -2 -1 -1 -1 -1 1
-2 -3 -3 -3 -2 -3 -3 -3 -1 0 0 -3 0 6 -4 -2 -2 1 3 -1
-1 -2 -2 -1 -3 -1 -1 -2 -2 -3 -3 -1 -2 -4 7 -1 -1 -4 -3 -2
1 -1 1 0 -1 0 0 0 -1 -2 -2 0 -1 -2 -1 4 1 -3 -2 -2
0 -1 0 -1 -1 -1 -1 -2 -2 -1 -1 -1 -1 -2 -1 1 5 -2 -2 0
-3 -3 -4 -4 -2 -2 -3 -2 -2 -3 -2 -3 -1 1 -4 -3 -2 11 2 -3
-2 -2 -2 -3 -2 -1 -2 -3 2 -1 -1 -2 -1 3 -3 -2 -2 2 7 -1
0 -3 -3 -3 -1 -2 -2 -3 -3 3 1 -2 1 -1 -2 -2 0 -3 -1 4"""
M = [list(map(int, r.split())) for r in B62.splitlines()]
assert all(M[i][j] == M[j][i] for i in range(20) for j in range(20)), "BLOSUM62 not symmetric"
assert [M[i][i] for i in range(20)] == [4, 5, 6, 6, 9, 5, 5, 6, 8, 4, 4, 5, 5, 6, 7, 4, 5, 11, 7, 4], "BLOSUM62 diagonal"
S = {(AA[i], AA[j]): M[i][j] for i in range(20) for j in range(20)}
a = seqs["O60566"][765:1050]            # BUB1B 766-1050
b = seqs["O43683"]                       # full BUB1 (local alignment finds its kinase domain)
GO, GE = 11, 1
n, m = len(a), len(b)
NEG = -10**9
H = [[0] * (m + 1) for _ in range(n + 1)]; E = [[NEG] * (m + 1) for _ in range(n + 1)]; F = [[NEG] * (m + 1) for _ in range(n + 1)]
TB = [[0] * (m + 1) for _ in range(n + 1)]
best = (0, 0, 0)
for i in range(1, n + 1):
    ai = a[i - 1]
    Hi, Hp, Ei, Fi, Fp, TBi = H[i], H[i - 1], E[i], F[i], F[i - 1], TB[i]
    for j in range(1, m + 1):
        Ei[j] = max(Ei[j - 1] - GE, Hi[j - 1] - GO)
        Fi[j] = max(Fp[j] - GE, Hp[j] - GO)
        d = Hp[j - 1] + S.get((ai, b[j - 1]), -4)
        v = max(0, d, Ei[j], Fi[j])
        Hi[j] = v
        TBi[j] = 1 if v == d else (2 if v == Ei[j] else (3 if v == Fi[j] else 0))
        if v > best[0]:
            best = (v, i, j)
# traceback (approximate affine traceback via stored best-move; adequate for locating aligned residues)
i, j = best[1], best[2]
pairs = []
while i > 0 and j > 0 and H[i][j] > 0:
    t = TB[i][j]
    if t == 1:
        pairs.append((i, j)); i -= 1; j -= 1
    elif t == 2:
        j -= 1
    elif t == 3:
        i -= 1
    else:
        break
pairs.reverse()
amap = {765 + ai: bj for ai, bj in pairs}
aligned = amap.get(T)
ident = sum(1 for ai, bj in pairs if a[ai - 1] == b[bj - 1]) / len(pairs) if pairs else 0
win = [(765 + ai, bj) for ai, bj in pairs if abs(765 + ai - T) <= 10]
wid = sum(1 for p, q in win if seqs["O60566"][p - 1] == b[q - 1]) / len(win) if win else None
res["paralog"] = {"bub1b_residue": seqs["O60566"][T - 1], "aligned_bub1_residue": b[aligned - 1] if aligned else None, "aligned_bub1_position": aligned,
                  "alignment_pairs": len(pairs), "domain_identity": round(ident, 3), "window_pm10_identity": round(wid, 3) if wid is not None else None,
                  "bub1b_1012_aligned_bub1": b[amap[1012] - 1] if amap.get(1012) else None, "sw_score": best[0], "bub1b_len": len(seqs["O60566"]), "bub1_len": len(b)}
p = res["paralog"]
cat = "gap/unaligned" if not aligned else ("identical (Asn)" if p["aligned_bub1_residue"] == "N" else ("conservative" if S.get(("N", p["aligned_bub1_residue"]), -9) >= 0 else "non-conservative"))
print(f"(a) BUB1B residue is Asn: {p['bub1b_residue'] == 'N'} | paralog BUB1 residue at aligned position: {cat} | domain identity {p['domain_identity']} | +-10 window identity {p['window_pm10_identity']} | aligned pairs {p['alignment_pairs']}")
# ---------------- (b) ClinVar neighbourhood via MANE CDS
cds = []
with gzip.open(f"{P}/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz", "rt") as fh:
    for ln in fh:
        if "Parent=transcript:ENST00000287598;" in ln and "\tCDS\t" in ln:
            c = ln.split("\t"); cds.append((int(c[3]), int(c[4]), int(c[7])))
cds.sort()
def codon_of(pos):
    t = 0
    for s, e, _ in cds:
        if s <= pos <= e:
            return (t + pos - s) // 3 + 1
        t += e - s + 1
    return None
gpos = {}
t = 0
for s, e, _ in cds:
    for g in range(s, e + 1):
        cd = t // 3 + 1
        if T - 10 <= cd <= T + 10:
            gpos.setdefault(cd, []).append(g)
        t += 1
lo, hi = min(min(v) for v in gpos.values()), max(max(v) for v in gpos.values())
recs = []
# fix after first run: keep ALL consequence terms (MC is a comma-separated list) and derive the protein change of SNVs
# from the MANE CDS (plus strand gene), instead of taking only the last MC term
CODE = {}
_b = "TCAG"; _aa = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"; _k = 0
for x in _b:
    for y in _b:
        for z in _b:
            CODE[x + y + z] = _aa[_k]; _k += 1
cds_seq = "".join("".join(sh(["samtools", "faidx", f"{P}/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna", f"15:{s}-{e}"]).splitlines()[1:]).upper() for s, e, _ in cds)
def cds_index(pos):
    t = 0
    for s, e, _ in cds:
        if s <= pos <= e:
            return t + pos - s
        t += e - s + 1
    return None
for ln in sh(["bcftools", "query", "-r", f"15:{lo}-{hi}", "-f", "%POS\t%ID\t%REF\t%ALT\t%INFO/CLNSIG\t%INFO/CLNREVSTAT\t%INFO/MC\n", f"{P}/ref/clinvar_20261004/clinvar_20261004.vcf.gz"]).splitlines():
    f = ln.split("\t"); cd = codon_of(int(f[0]))
    if cd and T - 10 <= cd <= T + 10:
        ci = cds_index(int(f[0])); pc = None
        if ci is not None and len(f[2]) == 1 and len(f[3]) == 1:
            cod = cds_seq[(ci // 3) * 3:(ci // 3) * 3 + 3]
            if cod[ci % 3] == f[2]:
                mut = cod[:ci % 3] + f[3] + cod[ci % 3 + 1:]
                pc = f"{CODE[cod]}{cd}{CODE[mut]}"
        recs.append({"offset": cd - T, "variation_id": f[1], "clnsig": f[4], "revstat": f[5],
                     "mc": sorted(set(re.findall(r"\|([A-Za-z0-9_]+)", f[6]))) if f[6] != "." else [],
                     "protein_change_MANE": pc, "same_codon_as_P": cd == T})
from collections import Counter
res["clinvar_pm10"] = recs
print(f"(b) ClinVar records within +-10 residues: {len(recs)} | by significance: {dict(Counter(r['clnsig'] for r in recs))}")
print(f"    coding-change records: {dict(Counter(tuple(r['mc']) for r in recs))}")
for r in recs:
    if r["protein_change_MANE"] and r["protein_change_MANE"][0] != r["protein_change_MANE"][-1] or r["same_codon_as_P"]:
        print(f"    offset {r['offset']:+d} | {r['protein_change_MANE']} | {','.join(r['mc'])} | {r['clnsig']} | {r['revstat']} | VariationID {r['variation_id']}")
# ---------------- (c) gnomAD neighbourhood (T2AA)
gs = json.load(open(f"{P}/out/T2AA_codon1002_audit_2026-10-23/GNOMAD_NEIGHBOURHOOD_SUMMARY.json"))
res["gnomad_neighbourhood_T2AA"] = gs
print("(c) T2AA gnomAD neighbourhood summary keys:", list(gs)[:10])
# ---------------- (d) CENATAC non-MANE transcript support
attr = {}
with gzip.open(f"{P}/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz", "rt") as fh:
    for ln in fh:
        for t2 in ("ENST00000891520", "ENST00000334418"):
            if f"ID=transcript:{t2};" in ln:
                attr[t2] = ln.split("\t")[8].strip()
res["cenatac_transcripts"] = attr
for t2, a2 in attr.items():
    print(f"(d) {t2}: biotype {re.search(r'biotype=([^;]+)', a2).group(1)} | tags {re.findall(r'tag=([^;]+)', a2)} | TSL {re.findall(r'transcript_support_level=([^;]+)', a2)} | version {re.findall(r'version=(\d+)', a2)}")
json.dump(res, open(f"{K6}/private_runs/K6_local.json", "w"), indent=1)
os.chmod(f"{K6}/private_runs/K6_local.json", 0o600)
