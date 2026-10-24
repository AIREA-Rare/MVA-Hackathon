"""K3 Workstream D: uniform coverage and structural-signal screen for one locus (gene +-100 kb) from a locus BAM.
Depth: samtools depth -a -Q 20 (default flag filter removes duplicates, secondary, QC-fail), 500-bp windows; ratio to
the median of all windows in the locus, excluding 2 kb at each locus edge (read-recovery edge effect). Pre-declared CNV
signal: >= 2 consecutive windows with ratio < 0.65 (heterozygous-loss-like) or > 1.35 (gain-like); single windows are
reported as isolated. Within gene +-10 kb, also: discordant fragments (MAPQ>=20, not proper pair, mate on another
chromosome or |TLEN| > 1000) and split reads (SA tag, MAPQ>=20) clustered in 500-bp bins; a bin with >= 3 fragments
is a 'cluster'. Detectability: depth method ~>= 1 kb copy-number change; insertions (e.g. Alu/SVA), inversions and
balanced events are visible only as clusters and can be missed; repeat-rich or low-MAPQ regions are blind spots.
Results private; prints categories only.
usage: python3 -B -I k3_sv_cov.py <gene> <bam> <chrom> <gene_start> <gene_end>"""
import json
import os
import statistics
import subprocess
from collections import Counter

G, BAM, CH, GS, GE = sys_args = __import__("sys").argv[1], __import__("sys").argv[2], __import__("sys").argv[3], int(__import__("sys").argv[4]), int(__import__("sys").argv[5])
K = os.path.join(os.environ["MVA_DATA_ROOT"], "out/T2K3_research_2026-10-23")
os.umask(0o077)
S, E = GS - 100_000, GE + 100_000
dep = subprocess.run(["samtools", "depth", "-a", "-Q", "20", "-r", f"{CH}:{S}-{E}", BAM], capture_output=True, text=True).stdout
w = {}
gb, fl = [], []  # per-base depth: gene body; flanks (locus minus gene, edges excluded)  [added K3 post-screen: callable fraction]
for ln in dep.splitlines():
    _, p, d = ln.split("\t")
    p = int(p)
    if S + 2000 <= p <= E - 2000:
        w.setdefault((p - S) // 500, []).append(int(d))
        (gb if GS <= p <= GE else fl).append(int(d))
wins = sorted((k, statistics.mean(v)) for k, v in w.items() if len(v) >= 250)
med = statistics.median(d for _, d in wins)
ratios = [(S + k * 500, round(d / med, 3) if med else None) for k, d in wins]
runs, cur = [], []
for st, r in ratios:
    lab = "loss" if r is not None and r < 0.65 else ("gain" if r is not None and r > 1.35 else None)
    if lab and cur and cur[-1][2] == lab and st - cur[-1][0] == 500:
        cur.append((st, r, lab))
    else:
        if len(cur) >= 2:
            runs.append(cur)
        cur = [(st, r, lab)] if lab else []
if len(cur) >= 2:
    runs.append(cur)
isolated = sum(1 for st, r in ratios if r is not None and (r < 0.65 or r > 1.35)) - sum(len(x) for x in runs)
gene_wins = [(st, r) for st, r in ratios if GS <= st <= GE]
# zero-coverage windows inside the gene (possible blind spots or homozygous loss)
zero_gene = sum(1 for st, r in gene_wins if r is not None and r < 0.1)
disc, split = Counter(), Counter()
for ln in subprocess.run(["samtools", "view", "-F", "0xD04", "-q", "20", BAM, f"{CH}:{GS - 10000}-{GE + 10000}"],
                         capture_output=True, text=True).stdout.splitlines():
    f = ln.split("\t")
    flag, pos, rnext, tlen = int(f[1]), int(f[3]), f[6], abs(int(f[8]))
    b = (pos // 500) * 500
    if (flag & 1) and not (flag & 2) and (rnext not in ("=", CH) or tlen > 1000):
        disc[b] += 1
    if any(t.startswith("SA:Z:") for t in f[11:]):
        split[b] += 1
dc = {k: v for k, v in disc.items() if v >= 3}
sc = {k: v for k, v in split.items() if v >= 3}
res = {"gene": G, "bam_sha256_prefix": subprocess.run(["sha256sum", BAM], capture_output=True, text=True).stdout[:16],
       "locus": f"{CH}:{S}-{E}", "windows": len(ratios), "locus_median_depth": med,
       "gene_window_ratio_min": min((r for _, r in gene_wins), default=None), "gene_window_ratio_max": max((r for _, r in gene_wins), default=None),
       "gene_window_ratio_median": statistics.median(r for _, r in gene_wins) if gene_wins else None,
       "cnv_runs": [{"start": x[0][0], "end": x[-1][0] + 499, "n_windows": len(x), "type": x[0][2], "mean_ratio": round(statistics.mean(y[1] for y in x), 3),
                     "in_gene": GS <= x[-1][0] + 499 and x[0][0] <= GE} for x in runs],
       "isolated_outlier_windows": isolated, "gene_windows_near_zero": zero_gene,
       "discordant_clusters_gene_pm10kb": dc, "split_read_clusters_gene_pm10kb": sc,
       "gene_body_mean_depth": round(statistics.mean(gb), 2) if gb else None, "flank_mean_depth": round(statistics.mean(fl), 2) if fl else None,
       "gene_to_flank_depth_ratio": round(statistics.mean(gb) / statistics.mean(fl), 3) if gb and fl and statistics.mean(fl) else None,
       "gene_body_callable_frac_dp10": round(sum(1 for x in gb if x >= 10) / len(gb), 4) if gb else None,
       "flank_callable_frac_dp10": round(sum(1 for x in fl if x >= 10) / len(fl), 4) if fl else None,
       "gene_body_zero_depth_bases": sum(1 for x in gb if x == 0),
       "params": "depth -a -Q20 default flag filter; 500-bp windows; edge 2 kb excluded; loss<0.65 gain>1.35 run>=2; clusters>=3 per 500 bp; callable = depth>=10"}
with open(f"{K}/private_runs/D_sv_cov_{G}.json", "w") as fh:
    json.dump(res, fh, indent=1)
os.chmod(f"{K}/private_runs/D_sv_cov_{G}.json", 0o600)
print(G, "| windows", len(ratios), "| CNV-like runs in locus:", len(runs), "(in gene:", sum(1 for x in res["cnv_runs"] if x["in_gene"]), ")",
      "| isolated outlier windows:", isolated, "| gene windows near zero:", zero_gene,
      "| discordant clusters (gene+-10kb):", len(dc), "| split-read clusters:", len(sc),
      "| gene callable(dp>=10) >=0.99:", (res["gene_body_callable_frac_dp10"] or 0) >= 0.99,
      "| gene/flank depth ratio in [0.8,1.2]:", res["gene_to_flank_depth_ratio"] is not None and 0.8 <= res["gene_to_flank_depth_ratio"] <= 1.2)
