"""K3 follow-up of post-screen flags (categories printed; numbers private):
 (a) CENATAC P: which components of T2 (strand) and T8 (local context) failed, plus VCF FS/SOR for comparison and the
     strand balance of the control SNVs;
 (b) depth runs (k3_sv_cov.py) per gene: GC fraction of run windows vs normal windows, MAPQ0 fraction of reads in runs,
     heterozygous VCF calls inside runs (a heterozygous call inside a putative deletion argues against hemizygous loss
     at that position), exon overlap;
 (c) oriented discordant clusters: fragment count, reads on both sides, mate MAPQ, reference soft-masking (lower-case)
     at the partner site if the FASTA is soft-masked, split reads near the cluster;
 (d) split-read clusters: context.
usage: python3 -B -I k3_followup.py"""
import gzip
import json
import os
import re
import statistics
import subprocess

P = os.environ["MVA_DATA_ROOT"]
CFG = json.load(open(os.environ["MVA_PRIVATE_CONFIG"]))  # participant-specific values (private file; never committed)
K = f"{P}/out/T2K3_research_2026-10-23"
R = f"{K}/private_runs"
FA = f"{P}/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
VCF = [f"{P}/raw/{f}" for f in os.listdir(f"{P}/raw") if f.endswith(".vcf.gz")][0]
BAMS = {"BUB1B": f"{P}/work/T2F_bub1b_locus_2026-10-22/postproc_2026-10-22/markdup.bam"}
for g in ("TRIP13", "CEP57", "CENATAC"):
    BAMS[g] = f"{P}/work/T2K3_locus_screen_2026-10-23/markdup.bam"
GENE = {"BUB1B": ("15", 40160984, 40221137, "ENST00000287598"), "TRIP13": ("5", 892849, 919357, "ENST00000166345"),
        "CEP57": ("11", 95789965, 95837070, "ENST00000325542"), "CENATAC": ("11", 118998051, 119015811, "ENST00000334418")}
os.umask(0o077)


def sh(c):
    return subprocess.run(c, capture_output=True, text=True).stdout


def seq(ch, s, e):
    return "".join(sh(["samtools", "faidx", FA, f"{ch}:{s}-{e}"]).splitlines()[1:])


out = {}
# (a)
q = json.load(open(f"{R}/B_bam_qc_CENATAC.json"))
m = q["candidates"]["CENATAC_P"]
C = q["controls"]
a = {"fisher_ok": m["fisher_strand_p"] >= 0.01, "sor_ok": m["SOR"] <= 3,
     "alt_one_strand_only": (m["alt_fwd"] == 0 or m["alt_rev"] == 0), "ref_one_strand_only": (m["ref_fwd"] == 0 or m["ref_rev"] == 0),
     "homopolymer_ok": m["homopolymer_at_site"] < 6 and max(m["homopolymer_left"], m["homopolymer_right"]) < 6,
     "str_ok": m["str_tract_spanning_site"] < 12, "entropy_ok": m["entropy_41bp"] >= 1.5,
     "vcf_FS": m["vcf"].get("FS"), "vcf_SOR": m["vcf"].get("SOR"),
     "controls_fisher_p_min": min(c["fisher_strand_p"] for c in C), "controls_SOR_max": max(c["SOR"] for c in C),
     "candidate_SOR_pct_among_controls": m["control_percentiles"].get("SOR"), "n_controls": len(C)}
out["a_cenatac_p"] = a
print("(a) CENATAC_P strand: Fisher ok =", a["fisher_ok"], "| SOR<=3 =", a["sor_ok"], "| alt reads on one strand only =", a["alt_one_strand_only"],
      "| ref one strand only =", a["ref_one_strand_only"])
print("    context: homopolymer ok =", a["homopolymer_ok"], "| STR ok =", a["str_ok"], "| entropy ok =", a["entropy_ok"],
      "| VCF SOR<=3 =", (float(a["vcf_SOR"]) <= 3) if a["vcf_SOR"] not in (None, ".") else "n/a",
      "| candidate SOR above all controls =", m["SOR"] > a["controls_SOR_max"])
# exon sets
ex = {g: [] for g in GENE}
with gzip.open(f"{P}/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz", "rt") as fh:
    for ln in fh:
        for g, (_, _, _, t) in GENE.items():
            if f"Parent=transcript:{t};" in ln and "\texon\t" in ln:
                c = ln.split("\t"); ex[g].append((int(c[3]), int(c[4])))
softmasked = any(ch.islower() for ch in seq("15", *CFG["k3_followup_softmask_window"]))
out["fasta_softmasked"] = softmasked
# (b)
out["b_runs"] = {}
for g, (ch, gs, ge, _) in GENE.items():
    sv = json.load(open(f"{R}/D_sv_cov_{g}.json"))
    S = gs - 100_000
    runs = sv["cnv_runs"]
    het = [int(l.split("\t")[0]) for l in sh(["bcftools", "query", "-r", f"{ch}:{S}-{ge + 100000}", "-i", 'FILTER="PASS"', "-f", "%POS[\t%GT]\n", VCF]).splitlines()
           if l.split("\t")[1].replace("|", "/") in ("0/1", "1/0")]
    def gc(s, e):
        x = seq(ch, s, e).upper(); return (x.count("G") + x.count("C")) / max(1, len(x) - x.count("N"))
    rr = []
    for r in runs:
        mq = [int(l.split("\t")[4]) for l in sh(["samtools", "view", "-F", "0xD04", BAMS[g], f"{ch}:{r['start']}-{r['end']}"]).splitlines()]
        rr.append({"type": r["type"], "n_windows": r["n_windows"], "mean_ratio": r["mean_ratio"], "in_gene": r["in_gene"], "gc": round(gc(r["start"], r["end"]), 3),
                   "mapq0_frac": round(sum(1 for x in mq if x == 0) / len(mq), 3) if mq else None, "reads": len(mq),
                   "het_calls_inside": sum(1 for p in het if r["start"] <= p <= r["end"]),
                   "exon_overlap": any(s <= r["end"] and e >= r["start"] for s, e in ex[g])})
    # normal-window GC sample: every 10th 500-bp window of the locus
    norm_gc = [gc(S + 2000 + i * 5000, S + 2499 + i * 5000) for i in range(0, (ge + 100000 - S - 4000) // 5000)]
    out["b_runs"][g] = {"runs": rr, "locus_median_gc": round(statistics.median(norm_gc), 3) if norm_gc else None}
    if rr:
        gcs = [x["gc"] for x in rr]
        print(f"(b) {g}: runs {len(rr)} (loss {sum(1 for x in rr if x['type'] == 'loss')}, gain {sum(1 for x in rr if x['type'] == 'gain')}); "
              f"runs with GC > locus median+0.10: {sum(1 for x in gcs if x > out['b_runs'][g]['locus_median_gc'] + 0.10)}/{len(rr)}; "
              f"runs with MAPQ0 frac > 0.2: {sum(1 for x in rr if (x['mapq0_frac'] or 0) > 0.2)}/{len(rr)}; "
              f"in-gene runs: {sum(1 for x in rr if x['in_gene'])} (with het call inside: {sum(1 for x in rr if x['in_gene'] and x['het_calls_inside'] > 0)}; "
              f"exon overlap: {sum(1 for x in rr if x['in_gene'] and x['exon_overlap'])}; in-gene run GC above median+0.10: {sum(1 for x in rr if x['in_gene'] and x['gc'] > out['b_runs'][g]['locus_median_gc'] + 0.10)})")
    else:
        print(f"(b) {g}: no runs")
# (c)
out["c_oriented"] = {}
for g in GENE:
    p = f"{R}/D_disc_detail_{g}.json"
    d = json.load(open(p))
    ch = GENE[g][0]
    for i, cl in enumerate(d["gene_clusters"]):
        if not cl["orientation_pattern"]:
            continue
        b = cl["bin_start"]
        # read MAPQ>=20, as in k3_disc_detail.py (consistency fix after the first post-screen run)
        rs = [l.split("\t") for l in sh(["samtools", "view", "-F", "0xD04", "-q", "20", BAMS[g], f"{ch}:{b - 500}-{b + 1000}"]).splitlines()]
        dd = [f for f in rs if (int(f[1]) & 1) and not (int(f[1]) & 2) and f[6] not in ("=", ch)]
        sa = sum(1 for f in rs if any(t.startswith("SA:Z:") for t in f[11:]))
        pc0 = max({f[6] for f in dd}, key=lambda c: sum(1 for f in dd if f[6] == c)) if dd else None
        sa_to_partner = sum(1 for f in rs for t in f[11:] if t.startswith("SA:Z:") and t[5:].split(",")[0] == pc0)
        mq = [int(t[5:]) for f in dd for t in f[11:] if t.startswith("MQ:i:")]
        pc = max({f[6] for f in dd}, key=lambda c: sum(1 for f in dd if f[6] == c)) if dd else None
        pp = sorted(int(f[7]) for f in dd if f[6] == pc)
        mid = pp[len(pp) // 2] if pp else None
        lower = None
        if softmasked and mid:
            s = seq(pc, max(1, mid - 300), mid + 300); lower = round(sum(1 for c in s if c.islower()) / len(s), 3)
        fw = sum(1 for f in dd if not int(f[1]) & 16); rv = len(dd) - fw
        own_ctx = cl["context"]
        rec = {"gene": g, "fragments": len(dd), "fwd": fw, "rev": rv, "both_sides": fw >= 2 and rv >= 2, "mate_mapq_median": statistics.median(mq) if mq else None,
               "mate_mapq0_frac": round(sum(1 for x in mq if x == 0) / len(mq), 3) if mq else None, "split_reads_near": sa,
               "split_reads_with_SA_on_partner_chrom": sa_to_partner, "mate_mapq_ge20_frac": round(sum(1 for x in mq if x >= 20) / len(mq), 3) if mq else None,
               "partner_softmasked_frac": lower, "context": own_ctx, "dist_to_nearest_exon_bp": cl["dist_to_nearest_exon_bp"]}
        out["c_oriented"][f"{g}_{i + 1}"] = rec
        print(f"(c) {g} oriented cluster: fragments {'>=10' if len(dd) >= 10 else ('5-9' if len(dd) >= 5 else '<5')} | both sides >=2 = {rec['both_sides']} | "
              f"mate MAPQ0 majority = {(rec['mate_mapq0_frac'] or 0) > 0.5} | mate MAPQ>=20 majority = {(rec['mate_mapq_ge20_frac'] or 0) > 0.5} | "
              f"split reads near = {'>=3' if sa >= 3 else sa} (SA on partner chrom: {'>=3' if sa_to_partner >= 3 else sa_to_partner}) | "
              f"partner repeat-masked = {'n/a (FASTA not soft-masked)' if lower is None else lower > 0.5} | context = {own_ctx}")
# (d)
out["d_split"] = {}
for g in GENE:
    sv = json.load(open(f"{R}/D_sv_cov_{g}.json"))
    ch, gs, ge, _ = GENE[g]
    for b, n in sv["split_read_clusters_gene_pm10kb"].items():
        b = int(b)
        inex = any(s <= b + 250 and e >= b for s, e in ex[g])
        ctx = "exon" if inex else ("intron" if gs < b < ge else "flank")
        near_or = any(abs(b - c["bin_start"]) <= 1500 for c in json.load(open(f"{R}/D_disc_detail_{g}.json"))["gene_clusters"] if c["orientation_pattern"])
        out["d_split"][f"{g}_{b}"] = {"n": n, "context": ctx, "within_1500bp_of_oriented_cluster": near_or}
        print(f"(d) {g} split-read cluster: context={ctx} | reads {'>=5' if n >= 5 else '3-4'} | within 1.5 kb of the oriented discordant cluster = {near_or}")
for g in GENE:
    sv = json.load(open(f"{R}/D_sv_cov_{g}.json"))
    cf = sv.get("gene_body_callable_frac_dp10")
    print(f"(e) {g}: gene-body callable (DP>=10) {'>=0.99' if cf >= 0.99 else ('0.95-0.99' if cf >= 0.95 else ('0.90-0.95' if cf >= 0.90 else '<0.90'))} | "
          f"flank callable {'>=0.99' if sv['flank_callable_frac_dp10'] >= 0.99 else ('0.95-0.99' if sv['flank_callable_frac_dp10'] >= 0.95 else '<0.95')} | zero-depth gene bases {'0' if sv['gene_body_zero_depth_bases'] == 0 else '>0'}")
print("FASTA soft-masked:", softmasked)
json.dump(out, open(f"{R}/D_followup.json", "w"), indent=1)
os.chmod(f"{R}/D_followup.json", 0o600)
