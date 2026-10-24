"""K4-D follow-up: test the mobile-element-insertion (MEI) alternative for the CEP57 signal, because a 'mate sink'
(criterion f) is expected both for reference artefacts and for polymorphic MEIs. MEI hallmarks checked:
 (i) poly-A/poly-T run (>= 10 nt allowing 1 mismatch) in clipped parts at the CEP57 side;
 (ii) clipped parts aligning anywhere near the partner site (any MAPQ; MEI sequence is repetitive);
 (iii) clip positions concentrated at one breakpoint (>= 3 clipped reads within 10 bp);
 (iv) partner region repetitiveness: fraction of partner 100-bp tiles with primary MAPQ < 20 or multiple near-equal hits
     (from D_cep57_sv.json); and whether mates of the unrelated-locus 'sink' clusters also show low MAPQ.
 Background control: the same poly-A test on clipped parts of all reads in five random 2.5-kb windows of the CEP57
 locus away from any cluster.
Reads are written only to private temporary FASTA files, deleted afterwards. Prints categories only.
usage: python3 -B -I k4_cep57_mei.py"""
import json
import os
import random
import re
import subprocess
from collections import Counter

P = os.environ["MVA_DATA_ROOT"]
K4 = f"{P}/out/T2K4_mechanistic_2026-10-24"
BAM = f"{P}/work/T2K3_locus_screen_2026-10-23/markdup.bam"
IDX = f"{P}/work/bwa_index_GRCh38_noalt_hs38d1_2026-10-20/GRCh38_noalt_hs38d1.nochr"
os.umask(0o077)
sh = lambda c: subprocess.run(c, capture_output=True, text=True).stdout
sv = json.load(open(f"{K4}/private_runs/D_cep57_sv.json"))
b, pm = sv["source_cluster_bin"], sv["partner_median"]
POLYA = re.compile(r"(?:A{10,}|T{10,}|A{5,}[CGT]A{4,}|T{5,}[ACG]T{4,})")


def clips(region):
    out = []
    for l in sh(["samtools", "view", "-F", "0xD04", "-q", "20", BAM, region]).splitlines():
        f = l.split("\t")
        ops = re.findall(r"(\d+)([MIDNSHP=X])", f[5])
        st = int(f[3])
        if ops and ops[0][1] == "S" and int(ops[0][0]) >= 15:
            out.append((st, f[9][:int(ops[0][0])]))
        if ops and ops[-1][1] == "S" and int(ops[-1][0]) >= 15:
            en = st + sum(int(n) for n, o in ops if o in "MDN=X") - 1
            out.append((en, f[9][-int(ops[-1][0]):]))
    return out


cc = clips(f"11:{b - 1000}-{b + 1500}")
polya = sum(1 for _, s in cc if POLYA.search(s))
pos = Counter(p // 10 for p, _ in cc)
pile = max(pos.values()) if pos else 0
# (ii) clipped parts -> genome, any MAPQ, near partner
tmp = f"{K4}/private_runs/_mei.tmp.fa"
with open(tmp, "w") as fh:
    for i, (_, s) in enumerate(cc):
        fh.write(f">c{i}\n{s}\n")
sam = sh(["bwa", "mem", "-t", "4", "-v", "1", "-k", "13", "-T", "13", IDX, tmp]) if cc else ""
os.remove(tmp)
pc_hits = Counter()
else_chr, else_mq = Counter(), []  # added: diversity and MAPQ of clipped parts aligning away from the partner
for l in sam.splitlines():
    f0 = l.split("\t")
    if not l.startswith("@") and len(f0) > 4 and not int(f0[1]) & 0x904 and f0[2] != "*" and abs(int(f0[3]) - pm) > 10000:
        else_chr[f0[2]] += 1; else_mq.append(int(f0[4]))
    if l.startswith("@"):
        continue
    f = l.split("\t")
    if int(f[1]) & 0x904 or f[2] == "*":
        pc_hits["unmapped" if f[2] == "*" else "skip"] += (f[2] == "*")
        continue
    near = abs(int(f[3]) - pm) <= 10000
    pc_hits["near_partner" if near else "elsewhere"] += 1
    pc_hits["near_partner_mapq_lt20" if near and int(f[4]) < 20 else "x"] += 0 if not near else 1
# background poly-A rate
random.seed(7)
bg_total = bg_polya = 0
for _ in range(5):
    s = random.randrange(95700000, 95930000)
    if abs(s - b) < 20000:
        continue
    c = clips(f"11:{s}-{s + 2500}")
    bg_total += len(c); bg_polya += sum(1 for _, x in c if POLYA.search(x))
res = {"clipped_parts": len(cc), "clipped_with_polyA_T": polya, "max_clips_within_10bp": pile, "clip_alignment": dict(pc_hits),
       "background_clipped_parts": bg_total, "background_polyA_T": bg_polya,
       "partner_tiles_low_mapq_frac": round(sv["partner_tiles_low_mapq"] / sv["partner_tiles"], 3), "partner_tiles_multimapping": sv["partner_tiles_multimapping"]}
res["elsewhere_distinct_chromosomes"] = len(else_chr)
res["elsewhere_local_same_chrom_frac"] = round(else_chr.get("11", 0) / max(1, sum(else_chr.values())), 3)
res["elsewhere_mapq_lt20_frac"] = round(sum(1 for x in else_mq if x < 20) / max(1, len(else_mq)), 3)
mei_like = polya >= 2 and pile >= 3 and pc_hits.get("near_partner", 0) >= 2
res["mei_hallmarks_met"] = mei_like
json.dump(res, open(f"{K4}/private_runs/D_cep57_mei.json", "w"), indent=1)
os.chmod(f"{K4}/private_runs/D_cep57_mei.json", 0o600)
print("clipped parts at CEP57 side:", ">=10" if len(cc) >= 10 else len(cc), "| with poly-A/T:", polya, "| clips concentrated (>=3 within 10 bp):", pile >= 3)
print("clipped parts aligning near the partner (any MAPQ):", pc_hits.get("near_partner", 0), "| elsewhere:", pc_hits.get("elsewhere", 0), "| unmapped:", pc_hits.get("unmapped", 0))
print("background poly-A/T rate in clipped parts:", f"{bg_polya}/{bg_total}", "| partner tiles with low MAPQ fraction > 0.25:", res["partner_tiles_low_mapq_frac"] > 0.25)
print("clipped parts elsewhere: distinct chromosomes", res["elsewhere_distinct_chromosomes"], "| fraction on chr11 (local):", res["elsewhere_local_same_chrom_frac"],
      "| MAPQ<20 fraction:", res["elsewhere_mapq_lt20_frac"])
print("MEI hallmarks met (poly-A>=2, concentrated clips, >=2 clipped parts at partner):", mei_like)
