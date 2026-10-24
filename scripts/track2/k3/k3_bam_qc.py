"""K3 Workstream B: read-level robustness of candidate variants against empirical controls (pure Python + samtools/bcftools).
Candidates are read from private records at run time; nothing patient-level is printed (categories only). Full numeric
results go to private_runs/. Pre-declared thresholds (fixed before any result was seen):
  T1 allele balance: fragment-level alt fraction in [0.25, 0.75] and exact binomial p >= 0.01 vs 0.5
  T2 strand: Fisher exact p >= 0.01 and GATK-style SOR <= 3 (SNV hard-filter value)
  T3 read position: Mann-Whitney p >= 0.01 (alt vs ref distance to nearest aligned-read end) and alt fraction with
     distance <= 5 bp <= 0.5
  T4 mapping: mean alt MAPQ >= 40, MAPQ0 fraction among covering reads <= 0.1, alt reads with XA tag <= 0.2, MWU p >= 0.01
  T5 base quality: Mann-Whitney p >= 0.01 (alt vs ref BQ)
  T6 threshold sensitivity: het-consistent support (alt >= 3 fragments and alt fraction in [0.15, 0.85]) in every
     MAPQ {0,20,40,60} x BQ {0,13,20,30} x duplicates {kept, removed} combination
  T7 duplicate sensitivity: alt fraction change between duplicates kept/removed <= 0.1
  T8 local context: max homopolymer touching the site < 6, no STR tract >= 12 bp spanning the site, 41-bp entropy >= 1.5
  T9 re-calling: bcftools 1.19 mpileup/call -m (MAPQ>=20, BQ>=13) genotype equals the supplied VCF genotype
  T10 VCF annotations: GATK SNV hard filters (QD>=2, FS<=60, MQ>=40, SOR<=3, MQRankSum>=-12.5, ReadPosRankSum>=-8)
Controls: PASS biallelic heterozygous SNVs of the supplied VCF inside the analysed locus, same metrics; each candidate
metric is also expressed as a percentile among controls.
usage: python3 -B -I k3_bam_qc.py <label> <bam> <chrom> <start> <end>   (label: BUB1B or CENATAC)"""
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter

LABEL, BAM, CH, S, E = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
FA = f"{P}/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
VCF = [f"{P}/raw/{f}" for f in os.listdir(f"{P}/raw") if f.endswith(".vcf.gz")][0]
os.umask(0o077)


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


# ---------------- candidates (private records)
cands = []
cp = f"{P}/work/T2F_bub1b_locus_2026-10-22/check_positions.tsv"
for ln in open(cp):
    f = ln.rstrip("\n").split("\t")
    if len(f) == 4 and f[0].startswith("BUB1B_") and f[1].isdigit():
        cands.append(("15", int(f[1]), f[2], f[3], f[0]))
cards = open(f"{P}/out/WP2_WP3_evidence_cards_v0.2.0_2026-10-20/VARIANT_EVIDENCE_CARDS.md").read()
for m in re.finditer(r"## (\w+) — route (\w) — (\w+):(\d+):([ACGT]+):([ACGT]+)", cards):
    lab = f"{m.group(1)}_{m.group(2)}"
    if m.group(1) != "BUB1B":
        cands.append((m.group(3), int(m.group(4)), m.group(5), m.group(6), lab))
cands = [c for c in cands if c[0] == CH and S <= c[1] <= E]
cand_pos = {c[1] for c in cands}
# ---------------- VCF records in locus
vrec = {}
q = sh(["bcftools", "query", "-r", f"{CH}:{S}-{E}", "-f", "%POS\t%REF\t%ALT\t%FILTER\t%QUAL\t%INFO/QD\t%INFO/FS\t%INFO/MQ\t%INFO/SOR\t%INFO/MQRankSum\t%INFO/ReadPosRankSum\t%INFO/BaseQRankSum\t[%GT\t%AD\t%DP\t%GQ]\n", VCF])
for ln in q.splitlines():
    f = ln.split("\t")
    vrec[(int(f[0]), f[1], f[2])] = dict(zip(["POS", "REF", "ALT", "FILTER", "QUAL", "QD", "FS", "MQ", "SOR", "MQRankSum", "ReadPosRankSum", "BaseQRankSum", "GT", "AD", "DP", "GQ"], f))
controls = [(CH, p, r, a, "control") for (p, r, a), v in vrec.items()
            if v["FILTER"] == "PASS" and len(r) == 1 and len(a) == 1 and v["GT"] in ("0/1", "0|1", "1|0") and p not in cand_pos]


# ---------------- statistics (pure Python)
def binom_two_sided(k, n, p=0.5):
    if n == 0:
        return 1.0
    pk = [math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(n + 1)]
    return min(1.0, sum(x for x in pk if x <= pk[k] * (1 + 1e-9)))


def fisher(a, b, c, d):
    n, r1, c1 = a + b + c + d, a + b, a + c
    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    p0 = pr(a)
    return min(1.0, sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-9)))


def sor(rf, rr, af, ar):
    rf, rr, af, ar = rf + 1, rr + 1, af + 1, ar + 1
    R = (rf * ar) / (rr * af)
    return math.log(R + 1 / R) + math.log(min(rf, rr) / max(rf, rr)) - math.log(min(af, ar) / max(af, ar))


def mwu(x, y):
    if not x or not y:
        return None
    allv = sorted([(v, 0) for v in x] + [(v, 1) for v in y])
    ranks, i = {}, 0
    rk = [0.0] * len(allv)
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        for t in range(i, j + 1):
            rk[t] = (i + j) / 2 + 1
        i = j + 1
    r1 = sum(rk[t] for t in range(len(allv)) if allv[t][1] == 0)
    n1, n2 = len(x), len(y)
    u = r1 - n1 * (n1 + 1) / 2
    ties = Counter(v for v, _ in allv)
    n = n1 + n2
    var = n1 * n2 / 12 * ((n + 1) - sum(t**3 - t for t in ties.values()) / (n * (n - 1)))
    if var <= 0:
        return 1.0
    z = (u - n1 * n2 / 2) / math.sqrt(var)
    return math.erfc(abs(z) / math.sqrt(2))


def pct(v, arr):
    arr = [a for a in arr if a is not None]
    return None if v is None or not arr else round(100 * sum(1 for a in arr if a <= v) / len(arr), 1)


# ---------------- per-site read extraction
def reads_at(ch, pos):
    out = []
    for ln in sh(["samtools", "view", "-F", "0x904", BAM, f"{ch}:{pos}-{pos}"]).splitlines():
        f = ln.split("\t")
        flag, rpos, mq, cig, seq, qual = int(f[1]), int(f[3]), int(f[4]), f[5], f[9], f[10]
        ops = re.findall(r"(\d+)([MIDNSHP=X])", cig)
        rp, qp, base, bq, qidx = rpos, 0, None, None, None
        lead = int(ops[0][0]) if ops and ops[0][1] == "S" else 0
        trail = int(ops[-1][0]) if ops and ops[-1][1] == "S" else 0
        for n, op in ops:
            n = int(n)
            if op in "M=X":
                if rp <= pos < rp + n:
                    qidx = qp + pos - rp
                    base, bq = seq[qidx], ord(qual[qidx]) - 33
                rp += n; qp += n
            elif op in "IS":
                qp += n
            elif op in "DN":
                if rp <= pos < rp + n:
                    base = "DEL"
                rp += n
        if base is None:
            continue
        alen = len(seq) - lead - trail
        dend = None if qidx is None else min(qidx - lead, (len(seq) - trail - 1) - qidx)
        tags = f[11:]
        out.append({"name": f[0], "flag": flag, "rev": bool(flag & 16), "dup": bool(flag & 1024), "mq": mq, "base": base,
                    "bq": bq, "dend": dend, "clip": lead + trail, "xa": any(t.startswith("XA:Z:") for t in tags),
                    "proper": bool(flag & 2), "alen": alen})
    return out


def frag(reads):
    best = {}
    for r in reads:
        k = r["name"]
        if k not in best or (r["bq"] or 0) > (best[k]["bq"] or 0):
            best[k] = r
    return list(best.values())


def site_metrics(ch, pos, ref, alt):
    rd = reads_at(ch, pos)
    m = {"reads_total": len(rd)}
    grid = {}
    for dupkeep in (True, False):
        for mq in (0, 20, 40, 60):
            for bq in (0, 13, 20, 30):
                fr = frag([r for r in rd if (dupkeep or not r["dup"]) and r["mq"] >= mq and r["bq"] is not None and r["bq"] >= bq])
                a = sum(1 for r in fr if r["base"] == alt); rf = sum(1 for r in fr if r["base"] == ref)
                grid[f"dup{'Kept' if dupkeep else 'Removed'}_MQ{mq}_BQ{bq}"] = (rf, a)
    m["grid"] = grid
    base = frag([r for r in rd if not r["dup"] and r["mq"] >= 20 and r["bq"] is not None and r["bq"] >= 13])
    A = [r for r in base if r["base"] == alt]; Rf = [r for r in base if r["base"] == ref]
    other = [r for r in base if r["base"] not in (alt, ref)]
    n = len(A) + len(Rf)
    m.update({"ref_frag": len(Rf), "alt_frag": len(A), "other_frag": len(other), "alt_fraction": round(len(A) / n, 4) if n else None,
              "binom_p": binom_two_sided(len(A), n) if n else None})
    rfw, rrv = sum(1 for r in Rf if not r["rev"]), sum(1 for r in Rf if r["rev"])
    afw, arv = sum(1 for r in A if not r["rev"]), sum(1 for r in A if r["rev"])
    m.update({"ref_fwd": rfw, "ref_rev": rrv, "alt_fwd": afw, "alt_rev": arv, "fisher_strand_p": fisher(rfw, rrv, afw, arv),
              "SOR": round(sor(rfw, rrv, afw, arv), 3)})
    m["readpos_mwu_p"] = mwu([r["dend"] for r in A], [r["dend"] for r in Rf])
    m["alt_near_end_frac"] = round(sum(1 for r in A if r["dend"] is not None and r["dend"] <= 5) / len(A), 3) if A else None
    m["ref_near_end_frac"] = round(sum(1 for r in Rf if r["dend"] is not None and r["dend"] <= 5) / len(Rf), 3) if Rf else None
    m["bq_mwu_p"] = mwu([r["bq"] for r in A], [r["bq"] for r in Rf])
    m["mean_bq_alt"] = round(sum(r["bq"] for r in A) / len(A), 2) if A else None
    m["mean_bq_ref"] = round(sum(r["bq"] for r in Rf) / len(Rf), 2) if Rf else None
    allfr = frag([r for r in rd if not r["dup"]])
    Aall = [r for r in allfr if r["base"] == alt]; Rall = [r for r in allfr if r["base"] == ref]
    m["mean_mq_alt"] = round(sum(r["mq"] for r in Aall) / len(Aall), 2) if Aall else None
    m["mean_mq_ref"] = round(sum(r["mq"] for r in Rall) / len(Rall), 2) if Rall else None
    m["mq_mwu_p"] = mwu([r["mq"] for r in Aall], [r["mq"] for r in Rall])
    m["mq0_frac"] = round(sum(1 for r in allfr if r["mq"] == 0) / len(allfr), 3) if allfr else None
    m["alt_xa_frac"] = round(sum(1 for r in Aall if r["xa"]) / len(Aall), 3) if Aall else None
    m["alt_clip_frac"] = round(sum(1 for r in A if r["clip"] > 0) / len(A), 3) if A else None
    m["ref_clip_frac"] = round(sum(1 for r in Rf if r["clip"] > 0) / len(Rf), 3) if Rf else None
    m["alt_improper_frac"] = round(sum(1 for r in A if not r["proper"]) / len(A), 3) if A else None
    kept = grid["dupKept_MQ20_BQ13"]; rem = grid["dupRemoved_MQ20_BQ13"]
    fk = kept[1] / sum(kept) if sum(kept) else None; fr_ = rem[1] / sum(rem) if sum(rem) else None
    m["dup_af_change"] = round(abs(fk - fr_), 4) if fk is not None and fr_ is not None else None
    return m


def context(ch, pos):
    seq = "".join(sh(["samtools", "faidx", FA, f"{ch}:{pos - 20}-{pos + 20}"]).splitlines()[1:]).upper()
    c = 20
    hp = 1
    for b in (seq[c],):
        l = c
        while l - 1 >= 0 and seq[l - 1] == b:
            l -= 1
        r = c
        while r + 1 < len(seq) and seq[r + 1] == b:
            r += 1
        hp = r - l + 1
    # homopolymer adjacent on either side (alt base could extend a neighbouring run)
    left = 1; l = c - 1
    while l - 1 >= 0 and seq[l - 1] == seq[c - 1]:
        left += 1; l -= 1
    right = 1; r = c + 1
    while r + 1 < len(seq) and seq[r + 1] == seq[c + 1]:
        right += 1; r += 1
    str_max = 0
    for k in range(1, 7):
        for st in range(0, len(seq) - k):
            unit = seq[st:st + k]; e = st + k
            while e + k <= len(seq) and seq[e:e + k] == unit:
                e += k
            if e - st >= 2 * k and st <= c < e:
                str_max = max(str_max, e - st)
    cnt = Counter(seq)
    ent = -sum(v / len(seq) * math.log2(v / len(seq)) for v in cnt.values())
    gc = (cnt["G"] + cnt["C"]) / len(seq)
    return {"homopolymer_at_site": hp, "homopolymer_left": left, "homopolymer_right": right, "str_tract_spanning_site": str_max,
            "entropy_41bp": round(ent, 3), "gc_41bp": round(gc, 3), "ref_base_fasta": seq[c]}


def recall(ch, pos):
    mp = subprocess.run(["bcftools", "mpileup", "-f", FA, "-r", f"{ch}:{pos}-{pos}", "-q", "20", "-Q", "13", "-a", "FORMAT/AD,FORMAT/DP",
                         "-Ou", BAM], capture_output=True)
    cl = subprocess.run(["bcftools", "call", "-m", "-Ov"], input=mp.stdout, capture_output=True)
    for ln in cl.stdout.decode().splitlines():
        if not ln.startswith("#"):
            f = ln.split("\t")
            gt = f[9].split(":")[0]
            return {"recall_alt": f[4], "recall_gt": gt, "recall_qual": f[5]}
    return {"recall_alt": None, "recall_gt": "no_call", "recall_qual": None}


def vcf_flags(v):
    def fl(k):
        try:
            return float(v[k])
        except (ValueError, KeyError, TypeError):
            return None
    t = {"QD": (fl("QD"), lambda x: x >= 2), "FS": (fl("FS"), lambda x: x <= 60), "MQ": (fl("MQ"), lambda x: x >= 40),
         "SOR": (fl("SOR"), lambda x: x <= 3), "MQRankSum": (fl("MQRankSum"), lambda x: x >= -12.5),
         "ReadPosRankSum": (fl("ReadPosRankSum"), lambda x: x >= -8)}
    return {k: (val, None if val is None else ok(val)) for k, (val, ok) in t.items()}


res = {"label": LABEL, "bam_sha256_prefix": sh(["sha256sum", BAM])[:16], "region": f"{CH}:{S}-{E}", "candidates": {}, "controls": []}
for ch, pos, ref, alt, lab in cands + controls:
    m = site_metrics(ch, pos, ref, alt)
    m.update(context(ch, pos))
    m.update(recall(ch, pos))
    v = vrec.get((pos, ref, alt), {})
    m["vcf"] = {k: v.get(k) for k in ("FILTER", "QUAL", "GT", "AD", "DP", "GQ", "QD", "FS", "MQ", "SOR", "MQRankSum", "ReadPosRankSum", "BaseQRankSum")}
    m["vcf_hardfilters"] = vcf_flags(v) if v else {}
    m["ref_matches_fasta"] = m["ref_base_fasta"] == ref
    if lab == "control":
        m["pos"] = pos
        res["controls"].append(m)
    else:
        m["pos"] = pos; m["ref"] = ref; m["alt"] = alt
        res["candidates"][lab] = m
C = res["controls"]


def tests(m):
    g = m["grid"]
    het_all = all(a >= 3 and 0.15 <= a / (a + r) <= 0.85 for r, a in g.values() if a + r > 0) and all(a + r > 0 for r, a in g.values())
    gt_vcf = (m["vcf"].get("GT") or "").replace("|", "/")
    hf = m["vcf_hardfilters"]
    out = {
        "T1_allele_balance": None if m["alt_fraction"] is None else (0.25 <= m["alt_fraction"] <= 0.75 and m["binom_p"] >= 0.01),
        "T2_strand": m["fisher_strand_p"] >= 0.01 and m["SOR"] <= 3,
        "T3_read_position": None if m["readpos_mwu_p"] is None else (m["readpos_mwu_p"] >= 0.01 and (m["alt_near_end_frac"] or 0) <= 0.5),
        "T4_mapping": None if m["mean_mq_alt"] is None else (m["mean_mq_alt"] >= 40 and (m["mq0_frac"] or 0) <= 0.1 and (m["alt_xa_frac"] or 0) <= 0.2 and (m["mq_mwu_p"] is None or m["mq_mwu_p"] >= 0.01)),
        "T5_base_quality": None if m["bq_mwu_p"] is None else m["bq_mwu_p"] >= 0.01,
        "T6_threshold_sensitivity": het_all,
        "T7_duplicate_sensitivity": None if m["dup_af_change"] is None else m["dup_af_change"] <= 0.1,
        "T8_local_context": m["homopolymer_at_site"] < 6 and max(m["homopolymer_left"], m["homopolymer_right"]) < 6 and m["str_tract_spanning_site"] < 12 and m["entropy_41bp"] >= 1.5,
        "T9_recall_concordant": m["recall_gt"] == gt_vcf if gt_vcf else None,
        "T10_vcf_hardfilters": None if not hf else all(ok for _, ok in hf.values() if ok is not None),
        "REF_matches_reference": m["ref_matches_fasta"],
    }
    return out


summary = {}
for lab, m in res["candidates"].items():
    m["tests"] = tests(m)
    m["control_percentiles"] = {k: pct(m.get(k), [c.get(k) for c in C]) for k in
                                ("alt_fraction", "SOR", "fisher_strand_p", "readpos_mwu_p", "alt_near_end_frac", "mean_mq_alt", "bq_mwu_p", "alt_clip_frac", "dup_af_change")}
    summary[lab] = {k: ("PASS" if v else "FAIL") if v is not None else "NOT AVAILABLE" for k, v in m["tests"].items()}
ctest = [tests(c) for c in C]
res["control_test_pass_rates"] = {k: f"{sum(1 for t in ctest if t[k])}/{sum(1 for t in ctest if t[k] is not None)}" for k in (ctest[0] if ctest else {})}
res["n_controls"] = len(C)
with open(f"{K}/private_runs/B_bam_qc_{LABEL}.json", "w") as fh:
    json.dump(res, fh, indent=1)
os.chmod(f"{K}/private_runs/B_bam_qc_{LABEL}.json", 0o600)
print(f"{LABEL}: candidates {len(res['candidates'])}, controls {len(C)}")
for lab, s in summary.items():
    print(lab, " ".join(f"{k.split('_')[0]}={v}" for k, v in s.items()))
print("control pass rates:", res["control_test_pass_rates"])
