"""K3 Workstream D: follow-up of discordant cluster(s) with the orientation pattern (from D_disc_detail_<gene>.json).
For each: mate-position spread on the partner chromosome, whether the partner position lies inside an annotated gene
(GFF3 gene/pseudogene names, kept private), fragment count bucket; plus, gene-wide, soft clips that end exactly at exon
boundaries (retrocopy / processed-pseudogene signature: clipped reads at many exon-exon junctions). Results private;
prints categories only.
usage: python3 -B -I k3_cluster_probe.py <gene> <bam> <chrom>"""
import gzip
import json
import os
import re
import subprocess
import sys
from collections import Counter

G, BAM, CH = sys.argv[1], sys.argv[2], sys.argv[3]
P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
os.umask(0o077)
TXS = {"BUB1B": "ENST00000287598", "TRIP13": "ENST00000166345", "CEP57": "ENST00000325542", "CENATAC": "ENST00000334418"}
dd = json.load(open(f"{K}/private_runs/D_disc_detail_{G}.json"))
genes, ex = [], []
with gzip.open(f"{P}/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz", "rt") as fh:
    for ln in fh:
        if ln.startswith("#"):
            continue
        c = ln.split("\t")
        if len(c) > 8 and c[2] in ("gene", "pseudogene", "ncRNA_gene"):
            m = re.search(r"Name=([^;]+)", c[8]); bt = re.search(r"biotype=([^;]+)", c[8])
            genes.append((c[0], int(c[3]), int(c[4]), m.group(1) if m else "?", bt.group(1) if bt else "?"))
        if f"Parent=transcript:{TXS[G]};" in ln and c[2] == "exon":
            ex.append((int(c[3]), int(c[4])))
res = {"gene": G, "clusters": []}
for cl in dd["gene_clusters"]:
    if not cl["orientation_pattern"]:
        continue
    b = cl["bin_start"]
    rs = [ln.split("\t") for ln in subprocess.run(["samtools", "view", "-F", "0xD04", "-q", "20", BAM, f"{CH}:{b - 500}-{b + 1000}"],
                                                    capture_output=True, text=True).stdout.splitlines()]
    d = [f for f in rs if (int(f[1]) & 1) and not (int(f[1]) & 2) and f[6] not in ("=", CH)]
    mp = Counter(f[6] for f in d)
    pc = mp.most_common(1)[0][0] if mp else None
    pos = sorted(int(f[7]) for f in d if f[6] == pc)
    spread = (pos[-1] - pos[0]) if pos else None
    mid = pos[len(pos) // 2] if pos else None
    hit = [g for g in genes if g[0] == pc and mid is not None and g[1] - 2000 <= mid <= g[2] + 2000]
    res["clusters"].append({"bin_start": b, "partner_chrom": pc, "partner_frags": len(pos), "partner_spread_bp": spread,
                            "partner_median_pos": mid, "partner_features": [(g[3], g[4]) for g in hit][:5]})
# exon-boundary soft clips across the gene (retrocopy signature)
bound = {s for s, _ in ex} | {e for _, e in ex}
clip_at = Counter()
for ln in subprocess.run(["samtools", "view", "-F", "0xD04", "-q", "20", BAM, f"{CH}:{min(bound) - 100}-{max(bound) + 100}"],
                         capture_output=True, text=True).stdout.splitlines():
    f = ln.split("\t")
    ops = re.findall(r"(\d+)([MIDNSHP=X])", f[5])
    st = int(f[3]); en = st + sum(int(n) for n, o in ops if o in "MDN=X") - 1
    if ops and ops[0][1] == "S" and int(ops[0][0]) >= 10 and st in bound:
        clip_at[st] += 1
    if ops and ops[-1][1] == "S" and int(ops[-1][0]) >= 10 and en in bound:
        clip_at[en] += 1
internal = [b for b in bound if b not in (min(bound), max(bound))]
res["exon_boundary_clips"] = {"boundaries_internal": len(internal), "boundaries_with_ge3_clipped_reads": sum(1 for b in internal if clip_at[b] >= 3),
                              "total_clipped_reads_at_boundaries": sum(clip_at[b] for b in internal)}
with open(f"{K}/private_runs/D_cluster_probe_{G}.json", "w") as fh:
    json.dump(res, fh, indent=1)
os.chmod(f"{K}/private_runs/D_cluster_probe_{G}.json", 0o600)
for i, c in enumerate(res["clusters"], 1):
    print(f"{G} oriented cluster {i}: partner fragments {'>=5' if c['partner_frags'] >= 5 else '<5'} | partner mates within 1 kb: {c['partner_spread_bp'] is not None and c['partner_spread_bp'] <= 1000} "
          f"| partner lies in/near an annotated feature: {bool(c['partner_features'])} | feature biotypes: {sorted({x[1] for x in c['partner_features']})}")
eb = res["exon_boundary_clips"]
print(f"{G} exon-boundary clip signature: {eb['boundaries_with_ge3_clipped_reads']}/{eb['boundaries_internal']} internal boundaries with >=3 clipped reads")
