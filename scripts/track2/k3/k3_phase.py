"""K3 Workstream D: independent re-check of what short reads can phase at BUB1B (BAM + VCF), recomputed without reusing
T2AC code. (1) template-length distribution of proper pairs in the gene body (MAPQ>=20, duplicates removed);
(2) fragments that place one read at one candidate site and any read of the same fragment at another candidate site;
(3) the heterozygous-site chain between each pair of candidates: largest gap between consecutive PASS heterozygous
calls versus the 99.9th percentile template length (a chain can only link sites if every gap is spanned by fragments).
Results private; prints categories only.
usage: python3 -B -I k3_phase.py"""
import json
import os
import subprocess
from collections import defaultdict

P = os.environ["MVA_DATA_ROOT"]
CFG = json.load(open(os.environ["MVA_PRIVATE_CONFIG"]))  # participant-specific values (private file; never committed)
K = f"{P}/out/T2K3_research_2026-10-23"
BAM = f"{P}/work/T2F_bub1b_locus_2026-10-22/postproc_2026-10-22/markdup.bam"
VCF = [f"{P}/raw/{f}" for f in os.listdir(f"{P}/raw") if f.endswith(".vcf.gz")][0]
os.umask(0o077)
c = {}
for ln in open(f"{P}/work/T2F_bub1b_locus_2026-10-22/check_positions.tsv"):
    f = ln.rstrip("\n").split("\t")
    if len(f) == 4 and f[0].startswith("BUB1B_"):
        c[f[0]] = int(f[1])
tl = []
for ln in subprocess.run(["samtools", "view", "-F", "0xD04", "-f", "0x42", "-q", "20", BAM, "15:40160984-40221137"],
                         capture_output=True, text=True).stdout.splitlines():
    t = abs(int(ln.split("\t")[8]))
    if t > 0:
        tl.append(t)
tl.sort()
q = lambda p: tl[min(len(tl) - 1, int(p * len(tl)))]
tlen = {"n_pairs": len(tl), "median": q(0.5), "p99": q(0.99), "p999": q(0.999), "max": tl[-1]}
names = {}
for lab, pos in c.items():
    names[lab] = {ln.split("\t")[0] for ln in subprocess.run(["samtools", "view", "-F", "0x504", BAM, f"15:{pos}-{pos}"],
                                                              capture_output=True, text=True).stdout.splitlines()}
links = {}
labs = sorted(c)
for i in range(len(labs)):
    for j in range(i + 1, len(labs)):
        a, b = labs[i], labs[j]
        links[f"{a}~{b}"] = {"distance_bp": abs(c[a] - c[b]), "fragments_covering_both": len(names[a] & names[b])}
het = []
for ln in subprocess.run(["bcftools", "query", "-r", CFG["k3_phase_het_chain_region"], "-i", 'FILTER="PASS"', "-f", "%POS[\t%GT]\n", VCF],
                         capture_output=True, text=True).stdout.splitlines():
    p, gt = ln.split("\t")
    if gt.replace("|", "/") in ("0/1", "1/0"):
        het.append(int(p))
chains = {}
for k in links:
    a, b = k.split("~")
    lo, hi = sorted((c[a], c[b]))
    pts = sorted({lo, hi} | {h for h in het if lo < h < hi})
    gaps = [y - x for x, y in zip(pts, pts[1:])]
    chains[k] = {"het_sites_between": len(pts) - 2, "largest_gap_bp": max(gaps), "all_gaps_within_p999_tlen": max(gaps) <= tlen["p999"]}
res = {"bam_sha256_prefix": subprocess.run(["sha256sum", BAM], capture_output=True, text=True).stdout[:16],
       "template_length_gene_body": tlen, "direct_links": links, "het_chains": chains}
with open(f"{K}/private_runs/D_phase_recheck.json", "w") as fh:
    json.dump(res, fh, indent=1)
os.chmod(f"{K}/private_runs/D_phase_recheck.json", 0o600)
print("template length p99.9 <= 1 kb:", tlen["p999"] <= 1000, "| max <= 2 kb:", tlen["max"] <= 2000)
for k in links:
    print(k, "| fragments covering both:", links[k]["fragments_covering_both"], "| distance > p99.9 template:", links[k]["distance_bp"] > tlen["p999"],
          "| het chain could bridge:", chains[k]["all_gaps_within_p999_tlen"])
