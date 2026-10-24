"""K3 Workstream D: runs of homozygosity (bcftools roh, genotype mode) and local heterozygosity around the four genes
from the single-sample VCF. Signals are indirect: a hemizygous deletion or uniparental isodisomy would remove
heterozygous calls; their absence of signal does not exclude small deletions. Results private; prints categories only.
Pre-declared: a gene region is 'het-depleted' if its 1-Mb window (gene +-500 kb) het count is below the 5th percentile
of genome-wide autosomal 1-Mb windows with >= 100 PASS SNV calls.
usage: python3 -B -I k3_roh_het.py"""
import json
import os
import subprocess
from collections import defaultdict

P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
VCF = [f"{P}/raw/{f}" for f in os.listdir(f"{P}/raw") if f.endswith(".vcf.gz")][0]
GENES = {"BUB1B": ("15", 40160984, 40221137), "TRIP13": ("5", 892849, 919357), "CEP57": ("11", 95789965, 95837070),
         "CENATAC": ("11", 118998051, 119015811)}
os.umask(0o077)
roh_out = f"{K}/private_runs/D_bcftools_roh.txt"
with open(roh_out, "w") as fh:
    subprocess.run(["bcftools", "roh", "-G", "30", "--AF-dflt", "0.4", "-O", "r", VCF], stdout=fh, stderr=subprocess.DEVNULL)
os.chmod(roh_out, 0o600)
rg = []
for ln in open(roh_out):
    f = ln.split("\t")
    if f[0] == "RG":
        rg.append((f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6]), float(f[7])))
auto = [r for r in rg if r[0].isdigit()]
tot = sum(r[3] for r in auto)
gene_roh = {}
for g, (c, s, e) in GENES.items():
    hits = [r for r in rg if r[0] == c and r[1] <= e and r[2] >= s]
    gene_roh[g] = [{"start": r[1], "end": r[2], "length_bp": r[3], "n_markers": r[4], "quality": r[5]} for r in hits]
# window heterozygosity
q = subprocess.run(["bcftools", "query", "-i", 'FILTER="PASS" && TYPE="snp"', "-f", "%CHROM\t%POS[\t%GT]\n", VCF],
                   capture_output=True, text=True).stdout
win = defaultdict(lambda: [0, 0])
calls = defaultdict(list)
for ln in q.splitlines():
    c, p, gt = ln.split("\t")
    if not c.isdigit():
        continue
    het = gt.replace("|", "/") in ("0/1", "1/0")
    win[(c, int(p) // 1_000_000)][0 if het else 1] += 1
    calls[c].append((int(p), het))
vals = sorted(h for (h, o) in win.values() if h + o >= 100)
p5 = vals[int(0.05 * len(vals))] if vals else None
gene_win = {}
for g, (c, s, e) in GENES.items():
    mid = (s + e) // 2
    lo, hi = mid - 500_000, mid + 500_000
    h = sum(1 for p, het in calls[c] if lo <= p <= hi and het)
    o = sum(1 for p, het in calls[c] if lo <= p <= hi and not het)
    gb_h = sum(1 for p, het in calls[c] if s <= p <= e and het)
    gb_o = sum(1 for p, het in calls[c] if s <= p <= e and not het)
    gene_win[g] = {"window_1mb_het": h, "window_1mb_homalt": o, "gene_body_het": gb_h, "gene_body_homalt": gb_o,
                   "window_het_percentile": round(100 * sum(1 for v in vals if v <= h) / len(vals), 1) if vals else None,
                   "het_depleted": (p5 is not None and h < p5)}
res = {"vcf_sha256_prefix": subprocess.run(["sha256sum", VCF], capture_output=True, text=True).stdout[:16],
       "bcftools_roh_params": "-G 30 --AF-dflt 0.4 -O r (genotype mode; default HMM)",
       "roh_segments_autosomal": len(auto), "roh_total_autosomal_bp": tot,
       "roh_segments_ge_1mb": sum(1 for r in auto if r[3] >= 1_000_000), "roh_total_ge_1mb_bp": sum(r[3] for r in auto if r[3] >= 1_000_000),
       "gene_overlapping_roh": gene_roh, "genome_windows_used": len(vals), "window_het_p5": p5, "gene_windows": gene_win}
with open(f"{K}/private_runs/D_roh_het.json", "w") as fh:
    json.dump(res, fh, indent=1)
os.chmod(f"{K}/private_runs/D_roh_het.json", 0o600)
for g in GENES:
    seg = gene_roh[g]
    print(g, "| gene overlaps ROH:", "yes" if seg else "no",
          ("(longest " + (">=1Mb" if max(x["length_bp"] for x in seg) >= 1_000_000 else "<1Mb") + ")") if seg else "",
          "| 1-Mb window het-depleted (<p5):", gene_win[g]["het_depleted"], "| gene body has het calls:", gene_win[g]["gene_body_het"] > 0)
print("genome windows used:", len(vals))
