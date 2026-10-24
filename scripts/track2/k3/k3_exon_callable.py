"""K3 Workstream B/D: callability of MANE coding sequence (+-10 bp splice margin) for the four genes in the locus BAMs:
fraction of bases with depth >= 10 and >= 20 (samtools depth -a -Q 20, default flag filter), zero-depth bases, and
the GC fraction of under-covered bases versus all CDS bases. Interpretation rule: a 'no LoF record' statement for a
gene only covers its callable portion. Results private; prints categories only.
usage: python3 -B -I k3_exon_callable.py"""
import gzip
import json
import os
import subprocess

P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
FA = f"{P}/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
G = {"BUB1B": ("15", "ENST00000287598", f"{P}/work/T2F_bub1b_locus_2026-10-22/postproc_2026-10-22/markdup.bam"),
     "TRIP13": ("5", "ENST00000166345", f"{P}/work/T2K3_locus_screen_2026-10-23/markdup.bam"),
     "CEP57": ("11", "ENST00000325542", f"{P}/work/T2K3_locus_screen_2026-10-23/markdup.bam"),
     "CENATAC": ("11", "ENST00000334418", f"{P}/work/T2K3_locus_screen_2026-10-23/markdup.bam")}
os.umask(0o077)
cds = {g: [] for g in G}
with gzip.open(f"{P}/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz", "rt") as fh:
    for ln in fh:
        for g, (_, t, _) in G.items():
            if f"Parent=transcript:{t};" in ln and "\tCDS\t" in ln:
                c = ln.split("\t"); cds[g].append((int(c[3]) - 10, int(c[4]) + 10))
res = {}
for g, (ch, t, bam) in G.items():
    d = {}
    for s, e in cds[g]:
        for ln in subprocess.run(["samtools", "depth", "-a", "-Q", "20", "-r", f"{ch}:{s}-{e}", bam], capture_output=True, text=True).stdout.splitlines():
            _, p, x = ln.split("\t"); d[int(p)] = int(x)
    seqs = {}
    for s, e in cds[g]:
        sq = "".join(subprocess.run(["samtools", "faidx", FA, f"{ch}:{s}-{e}"], capture_output=True, text=True).stdout.splitlines()[1:]).upper()
        for i, b in enumerate(sq):
            seqs[s + i] = b
    n = len(d)
    low = [p for p, x in d.items() if x < 10]
    gc_all = sum(1 for p in d if seqs.get(p) in "GC") / n if n else None
    gc_low = sum(1 for p in low if seqs.get(p) in "GC") / len(low) if low else None
    res[g] = {"transcript": t, "cds_plus_margin_bases": n, "frac_dp10": round(1 - len(low) / n, 4) if n else None,
              "frac_dp20": round(sum(1 for x in d.values() if x >= 20) / n, 4) if n else None, "zero_depth_bases": sum(1 for x in d.values() if x == 0),
              "gc_all": round(gc_all, 3) if gc_all is not None else None, "gc_low_depth_bases": round(gc_low, 3) if gc_low is not None else None,
              "exons_with_low_depth_bases": sum(1 for s, e in cds[g] if any(d.get(p, 0) < 10 for p in range(s, e + 1)))}
    r = res[g]
    cat = lambda f: ">=0.99" if f >= 0.99 else ("0.95-0.99" if f >= 0.95 else ("0.90-0.95" if f >= 0.90 else "<0.90"))
    print(f"{g}: CDS+-10 callable DP>=10 {cat(r['frac_dp10'])} | DP>=20 {cat(r['frac_dp20'])} | zero-depth bases {'0' if r['zero_depth_bases'] == 0 else '>0'} | "
          f"coding exons with any DP<10 base: {r['exons_with_low_depth_bases']}/{len(cds[g])} | low-depth bases GC-richer than CDS average: "
          f"{(r['gc_low_depth_bases'] or 0) > (r['gc_all'] or 0) + 0.1 if r['gc_low_depth_bases'] is not None else 'n/a'}")
json.dump(res, open(f"{K}/private_runs/B_exon_callable.json", "w"), indent=1)
os.chmod(f"{K}/private_runs/B_exon_callable.json", 0o600)
