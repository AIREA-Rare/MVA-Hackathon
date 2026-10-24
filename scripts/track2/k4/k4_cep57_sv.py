"""K4-D: independent reconstruction and classification of the CEP57 intronic discordant-read cluster (K3-E18).
Inputs: K3 three-locus markdup BAM (screen checksums verified), GRCh38 analysis set FASTA + bwa index, proband VCF.
PRE-DECLARED classification (fixed before results were seen):
  ARTEFACT-LEANING if any: (a) CEP57-side tiles have near-equal secondary alignments at the partner site (homology);
     (b) partner contig is decoy/unplaced/alt; (c) >= 50% of supporting fragments are duplicates; (d) majority of CEP57-side
     reads MAPQ < 20; (e) supporting reads pile in low-complexity sequence (entropy < 1.5 or homopolymer >= 10 or STR
     tract >= 20 bp); (f) the partner site (+-10 kb) also receives mates from discordant clusters at unrelated loci.
  REAL CANDIDATE if all: >= 5 independent (non-duplicate) fragments; reads on both sides with consistent orientation;
     majority CEP57-side MAPQ >= 20; partner mates within 1 kb; no (a)/(b); >= 2 clipped reads whose clipped part
     (>= 20 bp) aligns to the partner site (+-2 kb) with MAPQ >= 20 (junction evidence).
  Otherwise UNRESOLVED.
Read sequences are written only to a private temporary FASTA that is deleted after alignment. Prints categories only.
usage: python3 -B -I k4_cep57_sv.py"""
import json
import math
import os
import re
import statistics
import subprocess
from collections import Counter

P = os.environ["MVA_DATA_ROOT"]
K3 = f"{P}/out/T2K3_research_2026-10-23"
K4 = f"{P}/out/T2K4_mechanistic_2026-10-24"
BAM = f"{P}/work/T2K3_locus_screen_2026-10-23/markdup.bam"
B1 = f"{P}/work/T2F_bub1b_locus_2026-10-22/postproc_2026-10-22/markdup.bam"
FA = f"{P}/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
IDX = f"{P}/work/bwa_index_GRCh38_noalt_hs38d1_2026-10-20/GRCh38_noalt_hs38d1.nochr"
VCF = [f"{P}/raw/{f}" for f in os.listdir(f"{P}/raw") if f.endswith(".vcf.gz")][0]
CH = "11"
os.umask(0o077)
sh = lambda c, i=None: subprocess.run(c, capture_output=True, text=True, input=i).stdout
dd = json.load(open(f"{K3}/private_runs/D_disc_detail_CEP57.json"))
cl = next(c for c in dd["gene_clusters"] if c["orientation_pattern"])
b = cl["bin_start"]
W0, W1 = b - 1000, b + 1500
res = {"source_cluster_bin": b}
# 1 supporting fragments
reads = [l.split("\t") for l in sh(["samtools", "view", "-F", "0x904", BAM, f"{CH}:{W0}-{W1}"]).splitlines()]
disc = [f for f in reads if (int(f[1]) & 1) and not (int(f[1]) & 2) and f[6] not in ("=", CH)]
pc = Counter(f[6] for f in disc).most_common(1)[0][0]
sup = [f for f in disc if f[6] == pc]
frag = {}
for f in sup:
    frag.setdefault(f[0], []).append(f)
ndup = sum(1 for k, v in frag.items() if all(int(x[1]) & 1024 for x in v))
indep = len(frag) - ndup
side_mq = [int(f[4]) for f in sup]
mate_mq = [int(t[5:]) for f in sup for t in f[11:] if t.startswith("MQ:i:")]
fw = sorted(int(f[3]) for f in sup if not int(f[1]) & 16 and not int(f[1]) & 1024)
rv = sorted(int(f[3]) for f in sup if int(f[1]) & 16 and not int(f[1]) & 1024)
mpos = sorted(int(f[7]) for f in sup)
mstr = Counter("mate_rev" if int(f[1]) & 32 else "mate_fwd" for f in sup)
consistent = bool(fw and rv and max(fw) < min(rv) + 150)
bp_lo, bp_hi = (max(fw) + 150 if fw else None), (min(rv) if rv else None)
res.update({"partner_is_primary_chromosome": bool(re.fullmatch(r"\d{1,2}|X|Y", pc)), "fragments_total": len(frag), "fragments_duplicate": ndup,
            "fragments_independent": indep, "cep57_side_mapq_ge20_frac": round(sum(1 for x in side_mq if x >= 20) / len(side_mq), 3),
            "mate_mapq_median": statistics.median(mate_mq) if mate_mq else None, "mate_mapq_ge20_frac": round(sum(1 for x in mate_mq if x >= 20) / len(mate_mq), 3) if mate_mq else None,
            "fwd_reads": len(fw), "rev_reads": len(rv), "orientation_consistent_two_sided": consistent, "mate_strands": dict(mstr),
            "partner_spread_bp": mpos[-1] - mpos[0], "partner_median": mpos[len(mpos) // 2], "breakpoint_interval_len": (bp_hi - bp_lo) if consistent else None})
# 2 proper pairs spanning the breakpoint interval (expected for a heterozygous event)
span = 0
if consistent:
    for f in reads:
        if int(f[1]) & 2 and not int(f[1]) & 1024 and int(f[8]) > 0 and int(f[3]) < bp_lo and int(f[3]) + int(f[8]) > bp_hi:
            span += 1
res["proper_pairs_spanning_interval"] = span
# 3 local depth (100-bp bins, +-2 kb) vs locus median
dep = [int(l.split("\t")[2]) for l in sh(["samtools", "depth", "-a", "-Q", "20", "-r", f"{CH}:{b - 2000}-{b + 2500}", BAM]).splitlines()]
loc = json.load(open(f"{K3}/private_runs/D_sv_cov_CEP57.json"))["locus_median_depth"]
bins = [statistics.mean(dep[i:i + 100]) / loc for i in range(0, len(dep) - 99, 100)]
res.update({"depth_bins_ratio_min": round(min(bins), 3), "depth_bins_ratio_max": round(max(bins), 3), "depth_bins_below_0.5": sum(1 for x in bins if x < 0.5),
            "depth_bins_above_1.5": sum(1 for x in bins if x > 1.5)})
# 4 clipped sequences -> genome
clips = []
for f in reads:
    if int(f[1]) & 1024 or int(f[4]) < 20:
        continue
    ops = re.findall(r"(\d+)([MIDNSHP=X])", f[5])
    if ops and ops[0][1] == "S" and int(ops[0][0]) >= 20:
        clips.append(f[9][:int(ops[0][0])])
    if ops and ops[-1][1] == "S" and int(ops[-1][0]) >= 20:
        clips.append(f[9][-int(ops[-1][0]):])
tmp = f"{K4}/private_runs/_clips.tmp.fa"
with open(tmp, "w") as fh:
    for i, s in enumerate(clips):
        fh.write(f">c{i}\n{s}\n")
sam = sh(["bwa", "mem", "-t", "4", "-v", "1", "-k", "15", "-T", "15", IDX, tmp]) if clips else ""
os.remove(tmp)
to_partner = 0; clip_hits = Counter()
for ln in sam.splitlines():
    if ln.startswith("@"):
        continue
    f = ln.split("\t")
    if int(f[1]) & 0x904:
        continue
    clip_hits["mapped" if f[2] != "*" else "unmapped"] += 1
    if f[2] == pc and abs(int(f[3]) - res["partner_median"]) <= 2000 and int(f[4]) >= 20:
        to_partner += 1
res.update({"clipped_reads_ge20bp": len(clips), "clipped_mapping": dict(clip_hits), "clipped_to_partner_mapq20": to_partner})
# 5 homology / mappability: 100-bp tiles of the CEP57 cluster region (+-1 kb) and the partner region (+-1 kb), bwa mem -a
def tiles(ch, s, e, tag):
    seq = "".join(sh(["samtools", "faidx", FA, f"{ch}:{s}-{e}"]).splitlines()[1:]).upper()
    return [(f"{tag}{i}", seq[i:i + 100]) for i in range(0, len(seq) - 99, 50)]
pm = res["partner_median"]
tl = tiles(CH, b - 1000, b + 1500, "c") + tiles(pc, pm - 1000, pm + 1000, "p")
tmp2 = f"{K4}/private_runs/_tiles.tmp.fa"
with open(tmp2, "w") as fh:
    for n, s in tl:
        fh.write(f">{n}\n{s}\n")
sam2 = sh(["bwa", "mem", "-a", "-t", "4", "-v", "1", IDX, tmp2]); os.remove(tmp2)
prim, sec = {}, {}
for ln in sam2.splitlines():
    if ln.startswith("@"):
        continue
    f = ln.split("\t"); fl = int(f[1]); asv = next((int(t[5:]) for t in f[11:] if t.startswith("AS:i:")), 0)
    if fl & 0x900 == 0:
        prim[f[0]] = (f[2], int(f[3]), int(f[4]), asv)
    elif fl & 0x100:
        sec.setdefault(f[0], []).append((f[2], int(f[3]), asv))
def multi(n):
    return n in prim and any(a >= prim[n][3] - 10 for _, _, a in sec.get(n, []))
c_tiles = [n for n, _ in tl if n.startswith("c")]; p_tiles = [n for n, _ in tl if n.startswith("p")]
homology = sum(1 for n in c_tiles for ch2, p2, a in sec.get(n, []) if ch2 == pc and abs(p2 - pm) <= 2000)
res.update({"cep57_tiles": len(c_tiles), "cep57_tiles_multimapping": sum(1 for n in c_tiles if multi(n)), "cep57_tiles_low_mapq": sum(1 for n in c_tiles if n in prim and prim[n][2] < 20),
            "partner_tiles": len(p_tiles), "partner_tiles_multimapping": sum(1 for n in p_tiles if multi(n)), "partner_tiles_low_mapq": sum(1 for n in p_tiles if n in prim and prim[n][2] < 20),
            "cep57_tiles_with_secondary_hit_at_partner": homology})
# 6 complexity at the CEP57 side
seq = "".join(sh(["samtools", "faidx", FA, f"{CH}:{b - 1000}-{b + 1500}"]).splitlines()[1:]).upper()
def entropy(s):
    c = Counter(s); return -sum(v / len(s) * math.log2(v / len(s)) for v in c.values())
ent_min = min(entropy(seq[i:i + 50]) for i in range(0, len(seq) - 49, 25))
hp = max(len(m.group(0)) for m in re.finditer(r"A+|C+|G+|T+", seq))
strmax = 0
for k in range(1, 7):
    for m in re.finditer(r"(\w{%d})\1{2,}" % k, seq):
        strmax = max(strmax, len(m.group(0)))
res.update({"cep57_region_min_entropy_50bp": round(ent_min, 3), "cep57_region_max_homopolymer": hp, "cep57_region_max_str_tract": strmax,
            "cep57_region_gc": round((seq.count("G") + seq.count("C")) / len(seq), 3)})
# 7 background: interchromosomal discordant clusters in all four loci; partner recurrence
def clusters(bam, region):
    bins = {}
    for l in sh(["samtools", "view", "-F", "0xD04", "-q", "20", bam, region]).splitlines():
        f = l.split("\t")
        if (int(f[1]) & 1) and not (int(f[1]) & 2) and f[6] not in ("=", region.split(":")[0]):
            bins.setdefault((int(f[3]) // 500) * 500, []).append((f[6], int(f[7])))
    return {k: v for k, v in bins.items() if len(v) >= 3}
bg = {}
for g, (bam, reg) in {"BUB1B": (B1, "15:40060984-40321137"), "TRIP13": (BAM, "5:792849-1019357"), "CEP57": (BAM, "11:95689965-95937070"),
                      "CENATAC": (BAM, "11:118898051-119115811")}.items():
    bg[g] = clusters(bam, reg)
sizes = [len(v) for g in bg for k, v in bg[g].items() if not (g == "CEP57" and abs(k - b) <= 1000)]
recur = sum(1 for g in bg for k, v in bg[g].items() if not (g == "CEP57" and abs(k - b) <= 1000) and any(c == pc and abs(p - pm) <= 10000 for c, p in v))
res.update({"background_interchrom_clusters": len(sizes), "background_cluster_size_median": statistics.median(sizes) if sizes else None,
            "background_cluster_size_max": max(sizes) if sizes else None, "cep57_cluster_size_rank_above_all_background": all(len(frag) > s for s in sizes),
            "partner_recurrence_in_other_clusters": recur})
# 8 VCF records near the cluster
vq = sh(["bcftools", "query", "-r", f"{CH}:{b - 1000}-{b + 1500}", "-f", "%FILTER[\t%GT]\n", VCF]).splitlines()
res.update({"vcf_records_in_window": len(vq), "vcf_nonpass_in_window": sum(1 for l in vq if not l.startswith("PASS"))})
# classification
art = {"a_homology": homology > 0, "b_partner_not_primary": not res["partner_is_primary_chromosome"], "c_duplicates_ge50pct": ndup >= 0.5 * len(frag),
       "d_cep57_side_low_mapq": res["cep57_side_mapq_ge20_frac"] < 0.5, "e_low_complexity": ent_min < 1.5 or hp >= 10 or strmax >= 20,
       "f_partner_recurrent": recur > 0}
real = {"ge5_independent": indep >= 5, "two_sided_consistent": consistent, "cep57_side_mapq": res["cep57_side_mapq_ge20_frac"] >= 0.5,
        "partner_tight": res["partner_spread_bp"] <= 1000, "no_a_b": not art["a_homology"] and not art["b_partner_not_primary"], "junction_ge2_clips_to_partner": to_partner >= 2}
cls = "ARTEFACT-LEANING" if any(art.values()) else ("REAL CANDIDATE" if all(real.values()) else "UNRESOLVED")
res.update({"artefact_criteria": art, "real_criteria": real, "classification": cls})
json.dump(res, open(f"{K4}/private_runs/D_cep57_sv.json", "w"), indent=1)
os.chmod(f"{K4}/private_runs/D_cep57_sv.json", 0o600)
print("fragments:", ">=10" if len(frag) >= 10 else len(frag), "| independent >=5:", indep >= 5, "| duplicates >=50%:", art["c_duplicates_ge50pct"],
      "| CEP57-side MAPQ>=20 majority:", real["cep57_side_mapq"], "| mate MAPQ>=20 majority:", (res["mate_mapq_ge20_frac"] or 0) >= 0.5)
print("two-sided consistent orientation:", consistent, "| partner on primary chromosome:", res["partner_is_primary_chromosome"], "| partner mates within 1 kb:", real["partner_tight"],
      "| proper pairs spanning interval:", ">0" if span else 0)
print("depth (+-2 kb, 100-bp bins): any <0.5x:", res["depth_bins_below_0.5"] > 0, "| any >1.5x:", res["depth_bins_above_1.5"] > 0)
print("clipped reads >=20 bp:", ">=5" if len(clips) >= 5 else len(clips), "| clipped parts aligning to partner (MAPQ>=20):", to_partner)
print("CEP57 tiles multimapping:", res["cep57_tiles_multimapping"], "/", len(c_tiles), "| partner tiles multimapping:", res["partner_tiles_multimapping"], "/", len(p_tiles),
      "| partner tiles low MAPQ:", res["partner_tiles_low_mapq"], "| CEP57 tiles with secondary hit at partner (homology):", homology)
print("CEP57 region low complexity:", art["e_low_complexity"], "| background interchromosomal clusters:", len(sizes), "| CEP57 cluster larger than all background:",
      res["cep57_cluster_size_rank_above_all_background"], "| partner recurrent across loci:", recur > 0, "| VCF records in window:", len(vq))
print("artefact criteria met:", [k for k, v in art.items() if v], "| real-candidate criteria unmet:", [k for k, v in real.items() if not v])
print("CLASSIFICATION:", cls)
