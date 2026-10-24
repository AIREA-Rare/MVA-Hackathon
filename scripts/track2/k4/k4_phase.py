"""K4-B: re-assessment of every phase-bearing source in the existing data (read-only). Checks:
 1 read lengths in the BUB1B BAM and in a FASTQ sample (first 20,000 records of one R1 file); FASTQ comment fields
   (linked-read barcodes such as BX/BC); BAM read tags BX/MI/PS/HP;
 2 VCF header phasing lines and FORMAT PGT/PID/PS at the three BUB1B candidates;
 3 any primary, discordant or supplementary alignment joining candidate regions (each +-1 kb);
 4 the distance between T and P in mRNA (MANE CDS coordinates) -> feasibility of RNA-based physical phasing;
 5 family/segregation data: number of samples in every VCF under the private root; parental/trio keywords (counts only)
   in the raw README-type Markdown (the owner-supplied clinical .docx is not opened, per the standing project rule);
 6 statistical-phasing inputs: any reference haplotype panel or genetic map under ref/.
Results private; prints categories only.
usage: python3 -B -I k4_phase.py"""
import glob
import gzip
import json
import os
import re
import subprocess
from collections import Counter

P = os.environ["MVA_DATA_ROOT"]
K4 = f"{P}/out/T2K4_mechanistic_2026-10-24"
BAM = f"{P}/work/T2F_bub1b_locus_2026-10-22/postproc_2026-10-22/markdup.bam"
VCF = [f"{P}/raw/{f}" for f in os.listdir(f"{P}/raw") if f.endswith(".vcf.gz")][0]
os.umask(0o077)
sh = lambda c: subprocess.run(c, capture_output=True, text=True).stdout
pos = {}
for ln in open(f"{P}/work/T2F_bub1b_locus_2026-10-22/check_positions.tsv"):
    f = ln.rstrip("\n").split("\t")
    if len(f) == 4 and f[0].startswith("BUB1B_"):
        pos[f[0]] = int(f[1])
res = {}
# 1 read lengths and tags
rl, tags = Counter(), Counter()
for ln in sh(["samtools", "view", "-F", "0x900", BAM, "15:40160984-40221137"]).splitlines()[:200000]:
    f = ln.split("\t"); rl[len(f[9])] += 1
    for t in f[11:]:
        tags[t[:2]] += 1
fq = sorted(glob.glob(f"{P}/raw/fastq_2026-10-20/*_R1_001.fastq.gz"))[0]
fl, comments = Counter(), Counter()
with gzip.open(fq, "rt") as fh:
    for i, ln in enumerate(fh):
        if i >= 80000:
            break
        if i % 4 == 0:
            parts = ln.rstrip("\n").split(" ", 1)
            comments["has_comment"] += len(parts) > 1
            if len(parts) > 1 and re.search(r"\b(BX|BC|MI|RX):", parts[1]):
                comments["barcode_like_tag"] += 1
        elif i % 4 == 1:
            fl[len(ln.strip())] += 1
res["bam_read_length_max"] = max(rl) if rl else None
res["bam_read_length_mode"] = rl.most_common(1)[0][0] if rl else None
res["bam_tags_present"] = sorted(tags)
res["bam_phase_or_barcode_tags"] = sorted(t for t in tags if t in ("BX", "MI", "PS", "HP", "RX", "BC"))
res["fastq_read_length_max"] = max(fl); res["fastq_read_length_mode"] = fl.most_common(1)[0][0]
res["fastq_comment_fields"] = dict(comments)
# 2 VCF phasing
hdr = sh(["bcftools", "view", "-h", VCF])
res["vcf_header_phase_format_fields"] = [x for x in ("PGT", "PID", "PS", "HP") if f"##FORMAT=<ID={x}," in hdr]
res["vcf_samples"] = len(sh(["bcftools", "query", "-l", VCF]).split())
ph = {}
for k, p in pos.items():
    q = sh(["bcftools", "query", "-r", f"15:{p}-{p}", "-f", "[%GT\t%PGT\t%PID]\n", VCF]).split("\n")[0].split("\t")
    ph[k] = {"gt_phased": "|" in (q[0] if q else ""), "PGT_present": len(q) > 1 and q[1] not in (".", ""), "PID_present": len(q) > 2 and q[2] not in (".", "")}
res["candidate_phase_fields"] = ph
# 3 joining alignments
labs = sorted(pos)
joins = {}
for i in range(len(labs)):
    for j in range(i + 1, len(labs)):
        a, b = labs[i], labs[j]
        ra = f"15:{pos[a] - 1000}-{pos[a] + 1000}"
        n_mate = n_sa = 0
        for ln in sh(["samtools", "view", "-F", "0x4", BAM, ra]).splitlines():
            f = ln.split("\t")
            if f[6] in ("=", "15") and abs(int(f[7]) - pos[b]) <= 1000:
                n_mate += 1
            for t in f[11:]:
                if t.startswith("SA:Z:"):
                    for s in t[5:].split(";"):
                        if s and s.split(",")[0] == "15" and abs(int(s.split(",")[1]) - pos[b]) <= 1000:
                            n_sa += 1
        joins[f"{a}~{b}"] = {"mate_links": n_mate, "supplementary_links": n_sa}
res["joining_alignments"] = joins
# 4 mRNA distance T-P (MANE CDS)
an = json.load(open(f"{P}/out/T2K3_research_2026-10-23/private_runs/A_annotation.json"))
d_mrna = abs(an["BUB1B_P"]["ENST00000287598"]["cds_pos"] - an["BUB1B_T"]["ENST00000287598"]["cds_pos"])
res["T_P_distance_in_mRNA_nt"] = d_mrna
# 5 family data
vcfs = [p for p in glob.glob(f"{P}/**/*.vcf.gz", recursive=True) if "/ref/" not in p]
res["vcf_files_outside_ref"] = len(vcfs)
res["max_samples_in_any_vcf"] = max(len(sh(["bcftools", "query", "-l", v]).split()) for v in vcfs) if vcfs else None
md = [p for p in glob.glob(f"{P}/raw/*.md")]
kw = Counter()
for p in md:
    t = open(p, encoding="utf-8", errors="replace").read().lower()
    for w in ("trio", "parent", "mother", "father", "maternal", "paternal", "segregat", "family", "sibling"):
        kw[w] += t.count(w)
res["raw_md_files"] = len(md); res["raw_md_family_keyword_counts"] = dict(kw)
res["clinical_docx_opened"] = False
# 6 statistical phasing inputs
panel = [p for p in glob.glob(f"{P}/ref/**/*", recursive=True) if re.search(r"1000G|1kg|hgdp|shapeit|eagle|beagle|genetic_map|\.bref|panel", os.path.basename(p), re.I)]
res["reference_panel_files"] = len(panel)
json.dump(res, open(f"{K4}/private_runs/B_phase_reassessment.json", "w"), indent=1)
os.chmod(f"{K4}/private_runs/B_phase_reassessment.json", 0o600)
print("1 read length max (BAM/FASTQ):", res["bam_read_length_max"], "/", res["fastq_read_length_max"], "| BAM phase/barcode tags:", res["bam_phase_or_barcode_tags"] or "none",
      "| FASTQ barcode-like comments:", comments.get("barcode_like_tag", 0))
print("2 VCF phase FORMAT fields defined:", res["vcf_header_phase_format_fields"], "| samples in VCF:", res["vcf_samples"], "| candidates with phased GT/PGT/PID:",
      {k: any(v.values()) for k, v in ph.items()})
print("3 joining alignments (mate or supplementary) between candidate regions:", {k: v["mate_links"] + v["supplementary_links"] for k, v in joins.items()})
print("4 T-P distance in mRNA:", "<1 kb" if d_mrna < 1000 else ">=1 kb", f"({'within' if d_mrna < 1500 else 'beyond'} a single RT-PCR amplicon / long-read cDNA molecule)")
print("5 VCFs outside ref:", res["vcf_files_outside_ref"], "| max samples in any VCF:", res["max_samples_in_any_vcf"], "| raw .md family-keyword hits:", sum(kw.values()), "| clinical .docx opened: no")
print("6 reference haplotype panel / genetic map files:", res["reference_panel_files"])
