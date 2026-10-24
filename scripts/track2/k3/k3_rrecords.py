"""K3 Workstream B: read support for the M1 records of TRIP13, CEP57 and CENATAC in the K3 realigned locus BAM.
For each record (SNVs only; indels counted as 'not assessed'): fragment-level ref/alt counts (MAPQ>=20, BQ>=13,
duplicates removed), whether the read evidence agrees with the VCF genotype class (het: alt fraction 0.15-0.85 with
alt>=3; hom-alt: alt fraction >=0.9 with alt>=3), and depth. Also checks the two low-depth TRIP13 records in particular.
Results private; prints categories only.
usage: python3 -B -I k3_rrecords.py <bam>"""
import csv
import json
import os
import re
import subprocess
import sys

BAM = sys.argv[1]
P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
os.umask(0o077)
rows = list(csv.DictReader(open(f"{P}/out/M1_mva_genes_v0.1.0_2026-10-19/m1_gene_records.tsv"), delimiter="\t"))


def frag_counts(ch, pos, ref, alt):
    best = {}
    for ln in subprocess.run(["samtools", "view", "-F", "0xD04", "-q", "20", BAM, f"{ch}:{pos}-{pos}"], capture_output=True, text=True).stdout.splitlines():
        f = ln.split("\t")
        rp, qp, base, bq = int(f[3]), 0, None, None
        for n, op in re.findall(r"(\d+)([MIDNSHP=X])", f[5]):
            n = int(n)
            if op in "M=X":
                if rp <= pos < rp + n:
                    base, bq = f[9][qp + pos - rp], ord(f[10][qp + pos - rp]) - 33
                rp += n; qp += n
            elif op in "IS":
                qp += n
            elif op in "DN":
                rp += n
        if base is None or bq < 13:
            continue
        if f[0] not in best or bq > best[f[0]][1]:
            best[f[0]] = (base, bq)
    b = [x[0] for x in best.values()]
    return b.count(ref), b.count(alt), len(b)


FA = f"{P}/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"


def recall(ch, pos, ref, alt):
    """bcftools 1.19 mpileup/call -m at the record (SNVs and indels; same parameters as k3_bam_qc.py T9).
    Added after the first post-screen run, which assessed SNVs only."""
    # window widened to +-10 bp; indels may be represented differently by the two callers (second post-screen fix):
    # an exact match is preferred; otherwise an indel of the same length change within +-10 bp counts as an
    # equivalent-representation match and is labelled as such.
    mp = subprocess.run(["bcftools", "mpileup", "-f", FA, "-r", f"{ch}:{max(1, pos - 10)}-{pos + len(ref) + 10}", "-q", "20", "-Q", "13",
                         "-a", "FORMAT/AD,FORMAT/DP", "-Ou", BAM], capture_output=True)
    cl = subprocess.run(["bcftools", "call", "-m", "-Ov"], input=mp.stdout, capture_output=True)
    equiv = None
    for ln in cl.stdout.decode().splitlines():
        if ln.startswith("#"):
            continue
        f = ln.split("\t")
        if int(f[1]) == pos and f[3] == ref and alt in f[4].split(","):
            return f[9].split(":")[0]
        if len(ref) != len(alt) and any(len(a) - len(f[3]) == len(alt) - len(ref) for a in f[4].split(",")) and abs(int(f[1]) - pos) <= 10:
            equiv = f[9].split(":")[0] + " (equivalent representation)"
    return equiv or "no_matching_call"


out = {}
for g in ("TRIP13", "CEP57", "CENATAC"):
    recs = [r for r in rows if g in (r.get("m1_genes") or "").replace(",", ";").split(";")]
    res = []
    for r in recs:
        ch, pos, ref, alt = r["chrom"], int(r["pos"]), r["ref"], r["alt"]
        rc = recall(ch, pos, ref, alt)
        vgt = (r["gt"] or "").replace("|", "/")
        rc_agree = rc.split(" ")[0].replace("|", "/") == vgt if rc != "no_matching_call" else False
        if len(ref) != 1 or len(alt) != 1:
            res.append({"pos": pos, "type": "indel/complex", "assessed": False, "vcf_dp": r["dp"], "zyg": r["zygosity"],
                        "recall_gt": rc, "recall_agrees": rc_agree, "consequence": r["consequence_class_primary"]}); continue
        rf, al, n = frag_counts(ch, pos, ref, alt)
        frac = al / (rf + al) if rf + al else None
        z = r["zygosity"]
        agree = None if frac is None else ((al >= 3 and 0.15 <= frac <= 0.85) if z.startswith("het") else (al >= 3 and frac >= 0.9) if "hom" in z else None)
        low = r["dp"].isdigit() and int(r["dp"]) < 10
        res.append({"pos": pos, "type": "SNV", "assessed": True, "zyg": z, "vcf_dp": r["dp"], "vcf_low_dp": low, "ref_frag": rf, "alt_frag": al,
                    "frag_depth": n, "alt_fraction": None if frac is None else round(frac, 3), "read_genotype_agrees": agree,
                    "recall_gt": rc, "recall_agrees": rc_agree, "consequence": r["consequence_class_primary"],
                    "why_not": None if agree else ("no alt reads" if al == 0 else ("alt < 3 fragments" if al < 3 else "fraction outside het/hom range"))})
    a = [x for x in res if x["assessed"]]
    summ = (f"{sum(1 for x in a if x['read_genotype_agrees'])}/{len(a)} SNV records agree with VCF genotype (fragment counts); "
            f"bcftools re-call agrees {sum(1 for x in res if x['recall_agrees'])}/{len(res)} records (SNV+indel); "
            f"low-VCF-DP records agreeing {sum(1 for x in a if x.get('vcf_low_dp') and x['read_genotype_agrees'])}/{sum(1 for x in a if x.get('vcf_low_dp'))}; "
            f"disagreement reasons: {sorted({x['why_not'] for x in a if x.get('why_not')})}")
    out[g] = {"records": res, "summary": summ}
    json.dump(out[g], open(f"{K}/private_runs/B_rrecords_{g}.json", "w"), indent=1)
    os.chmod(f"{K}/private_runs/B_rrecords_{g}.json", 0o600)
    print(g, "|", summ)
