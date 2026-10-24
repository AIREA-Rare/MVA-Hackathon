"""K3 Workstream D: characterise discordant-fragment clusters near a gene (from k3_sv_cov.py output) and compare with the
locus-wide background. Per cluster bin: fragments, read orientation, mate chromosomes (count of distinct), mate MAPQ
(MQ tag), soft-clip pile-ups (>= 3 reads clipped >= 20 bp within +-5 bp) within +-500 bp, gene context (exon/intron/
flank) and distance class to the nearest exon and to each candidate. Insertion-like pattern (pre-declared): forward-
strand discordant reads on one side and reverse-strand on the other within 1 kb, mates on >= 3 distinct chromosomes or
mostly low mate MAPQ (repeat-derived), plus a soft-clip pile-up. Results private; prints categories only.
usage: python3 -B -I k3_disc_detail.py <gene> <bam> <chrom> <gene_start> <gene_end>"""
import gzip
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict

G, BAM, CH, GS, GE = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
os.umask(0o077)
sv = json.load(open(f"{K}/private_runs/D_sv_cov_{G}.json"))
TXS = {"BUB1B": "ENST00000287598", "TRIP13": "ENST00000166345", "CEP57": "ENST00000325542", "CENATAC": "ENST00000334418"}
ex = []
with gzip.open(f"{P}/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz", "rt") as fh:
    for ln in fh:
        if f"Parent=transcript:{TXS[G]};" in ln and "\texon\t" in ln:
            c = ln.split("\t"); ex.append((int(c[3]), int(c[4])))
cands = {}
cp = f"{P}/work/T2F_bub1b_locus_2026-10-22/check_positions.tsv"
for ln in open(cp):
    f = ln.rstrip("\n").split("\t")
    if G == "BUB1B" and len(f) == 4 and f[0].startswith("BUB1B_"):
        cands[f[0]] = int(f[1])


def reads(region, flags="0xD04", q="20"):
    return [ln.split("\t") for ln in subprocess.run(["samtools", "view", "-F", flags, "-q", q, BAM, region], capture_output=True, text=True).stdout.splitlines()]


def disc_bins(s, e):
    b = Counter()
    for f in reads(f"{CH}:{s}-{e}"):
        flag, tlen = int(f[1]), abs(int(f[8]))
        if (flag & 1) and not (flag & 2) and (f[6] not in ("=", CH) or tlen > 1000):
            b[(int(f[3]) // 500) * 500] += 1
    return b


locus_bins = disc_bins(GS - 100_000, GE + 100_000)
locus_clusters = sum(1 for v in locus_bins.values() if v >= 3)
out = []
for b, n in sorted(sv["discordant_clusters_gene_pm10kb"].items(), key=lambda x: int(x[0])):
    b = int(b)
    rs = reads(f"{CH}:{b - 500}-{b + 1000}")
    d = [f for f in rs if (int(f[1]) & 1) and not (int(f[1]) & 2) and (f[6] not in ("=", CH) or abs(int(f[8])) > 1000)]
    fw = [int(f[3]) for f in d if not int(f[1]) & 16]; rv = [int(f[3]) for f in d if int(f[1]) & 16]
    mchr = Counter(f[6] if f[6] != "=" else CH for f in d)
    mq = [int(t[5:]) for f in d for t in f[11:] if t.startswith("MQ:i:")]
    clip = Counter()
    for f in rs:
        import re
        ops = re.findall(r"(\d+)([MIDNSHP=X])", f[5])
        if ops and ops[0][1] == "S" and int(ops[0][0]) >= 20:
            clip[int(f[3]) // 10] += 1
        if ops and ops[-1][1] == "S" and int(ops[-1][0]) >= 20:
            end = int(f[3]) + sum(int(n) for n, o in ops if o in "MDN=X")
            clip[end // 10] += 1
    pile = max(clip.values()) if clip else 0
    inex = any(s <= b + 250 <= e for s, e in ex)
    dist_ex = min(min(abs(b + 250 - s), abs(b + 250 - e)) for s, e in ex) if ex else None
    ctx = "exon" if inex else ("intron" if ex and min(s for s, _ in ex) < b < max(e for _, e in ex) else "flank")
    orient = bool(fw and rv and min(rv) - max(fw) > -1000 and (sum(fw) / len(fw)) < (sum(rv) / len(rv)))
    multi = len([k for k in mchr if k != CH]) >= 3
    lowmq = (sum(1 for x in mq if x < 20) / len(mq) > 0.5) if mq else False
    out.append({"bin_start": b, "fragments": len(d), "fwd": len(fw), "rev": len(rv), "mate_chroms_distinct": len(mchr),
                "mate_chroms_other": len([k for k in mchr if k != CH]), "mate_mapq_low_frac": round(sum(1 for x in mq if x < 20) / len(mq), 3) if mq else None,
                "softclip_pileup_max": pile, "context": ctx, "dist_to_nearest_exon_bp": dist_ex,
                "dist_to_candidates_bp": {k: abs(v - (b + 250)) for k, v in cands.items()},
                "insertion_like": orient and (multi or lowmq) and pile >= 3, "orientation_pattern": orient})
res = {"gene": G, "locus_disc_clusters_total": locus_clusters, "locus_bins_with_any_disc": len(locus_bins), "gene_clusters": out}
with open(f"{K}/private_runs/D_disc_detail_{G}.json", "w") as fh:
    json.dump(res, fh, indent=1)
os.chmod(f"{K}/private_runs/D_disc_detail_{G}.json", 0o600)
print(G, "| locus-wide discordant clusters (gene+-100kb):", locus_clusters, "| gene+-10kb clusters:", len(out))
for i, o in enumerate(out, 1):
    dc = min(o["dist_to_candidates_bp"].values()) if o["dist_to_candidates_bp"] else None
    print(f"  cluster {i}: context={o['context']} | nearest exon {'<1kb' if o['dist_to_nearest_exon_bp'] < 1000 else '>=1kb'} | "
          f"mate other-chrom count {'>=3' if o['mate_chroms_other'] >= 3 else o['mate_chroms_other']} | low mate MAPQ majority={o['mate_mapq_low_frac'] is not None and o['mate_mapq_low_frac'] > 0.5} | "
          f"orientation pattern={o['orientation_pattern']} | clip pileup>=3={o['softclip_pileup_max'] >= 3} | INSERTION-LIKE={o['insertion_like']}"
          + (f" | nearest candidate {'<5kb' if dc < 5000 else '>=5kb'}" if dc is not None else ""))
