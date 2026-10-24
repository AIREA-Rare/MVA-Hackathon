"""K3: build K3_VARIANT_QC.tsv and K3_TEST_RUNS.tsv from the private JSON results (numbers are written straight into the
restricted deliverables; nothing patient-level is printed). Prints row counts only.
usage: python3 -B -I k3_build_qc_tables.py"""
import glob
import json
import os
import subprocess

P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
R = f"{K}/private_runs"
os.umask(0o077)


def sha(p):
    return subprocess.run(["sha256sum", p], capture_output=True, text=True).stdout[:64] if os.path.exists(p) else "missing"


THR = {"T1_allele_balance": "fragment alt fraction in [0.25,0.75] and binomial p>=0.01 (MAPQ>=20, BQ>=13, duplicates removed)",
       "T2_strand": "Fisher strand p>=0.01 and SOR<=3", "T3_read_position": "MWU p>=0.01 (distance to aligned read end) and alt fraction <=5 bp from end <=0.5",
       "T4_mapping": "mean alt MAPQ>=40, MAPQ0 fraction<=0.1, alt XA fraction<=0.2, MWU p>=0.01", "T5_base_quality": "MWU p>=0.01 alt vs ref BQ",
       "T6_threshold_sensitivity": "het-consistent (alt>=3, fraction 0.15-0.85) at all MAPQ{0,20,40,60} x BQ{0,13,20,30} x dup{kept,removed}",
       "T7_duplicate_sensitivity": "|alt fraction(dup kept) - alt fraction(dup removed)|<=0.1", "T8_local_context": "homopolymer<6 (site and adjacent), STR tract<12 bp, entropy(41 bp)>=1.5",
       "T9_recall_concordant": "bcftools 1.19 mpileup/call -m (q20 Q13) GT equals supplied VCF GT",
       "T10_vcf_hardfilters": "GATK SNV hard filters QD>=2 FS<=60 MQ>=40 SOR<=3 MQRankSum>=-12.5 ReadPosRankSum>=-8",
       "REF_matches_reference": "VCF REF equals GRCh38 analysis-set base"}
METRIC_FOR = {"T1_allele_balance": ["ref_frag", "alt_frag", "alt_fraction", "binom_p"], "T2_strand": ["ref_fwd", "ref_rev", "alt_fwd", "alt_rev", "fisher_strand_p", "SOR"],
              "T3_read_position": ["readpos_mwu_p", "alt_near_end_frac", "ref_near_end_frac"], "T4_mapping": ["mean_mq_alt", "mean_mq_ref", "mq0_frac", "alt_xa_frac", "mq_mwu_p"],
              "T5_base_quality": ["mean_bq_alt", "mean_bq_ref", "bq_mwu_p"], "T6_threshold_sensitivity": [], "T7_duplicate_sensitivity": ["dup_af_change"],
              "T8_local_context": ["homopolymer_at_site", "homopolymer_left", "homopolymer_right", "str_tract_spanning_site", "entropy_41bp", "gc_41bp"],
              "T9_recall_concordant": ["recall_gt", "recall_qual"], "T10_vcf_hardfilters": [], "REF_matches_reference": ["ref_base_fasta"]}
rows = []
runs = []
for f in sorted(glob.glob(f"{R}/B_bam_qc_*.json")):
    d = json.load(open(f))
    lab = d["label"]
    for cand, m in d["candidates"].items():
        for t, ok in m["tests"].items():
            res = "NOT AVAILABLE" if ok is None else ("PASS" if ok else "FAIL")
            vals = "; ".join(f"{k}={m.get(k)}" for k in METRIC_FOR[t])
            if t == "T6_threshold_sensitivity":
                vals = "; ".join(f"{k}:ref={v[0]},alt={v[1]}" for k, v in m["grid"].items())
            if t == "T10_vcf_hardfilters":
                vals = "; ".join(f"{k}={v[0]}" for k, v in m["vcf_hardfilters"].items())
            pc = "; ".join(f"{k}=p{v}" for k, v in m["control_percentiles"].items() if v is not None and k in METRIC_FOR[t])
            rows.append([f"QC-{cand}-{t.split('_')[0]}", cand, t, THR[t], vals, res, pc or "-",
                         f"controls passing this test: {d['control_test_pass_rates'].get(t, '-')}", f"private_runs/{os.path.basename(f)}"])
    runs.append([f"RUN-B-{lab}", "k3_bam_qc.py", f"bam sha256 prefix {d['bam_sha256_prefix']}; VCF (raw, private); GRCh38 analysis set FASTA",
                 "python 3.12.3 (stdlib); samtools 1.19.2; bcftools 1.19", f"region {d['region']}; thresholds in script header; controls {d['n_controls']} PASS het SNVs",
                 f"private_runs/{os.path.basename(f)}", f"{len(d['candidates'])} candidates; per-test results in K3_VARIANT_QC.tsv", "PASS",
                 "same library as the supplied VCF; re-calling not orthogonal; controls are common het SNVs (may differ from rare variants in context)"])
with open(f"{K}/K3_VARIANT_QC.tsv", "w") as fh:
    fh.write("qc_id\tcandidate\ttest\tthreshold (pre-declared)\tvalues\tresult\tpercentile_among_controls\tcontrol_calibration\traw_result\n")
    for r in rows:
        fh.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
# other runs
extra = [
 ("RUN-A-annot", "k3_annotation.py", f"GFF3 sha {sha(P + '/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz')[:16]}; FASTA analysis set", "python 3.12.3; samtools 1.19.2",
  "MANE/non-MANE CDS reconstruction; splice-region rule exonic<3/intronic<=8; NMD 50-nt rule", "private_runs/A_annotation.json", "codons and amino acids match K2; T >50 nt upstream of last junction; P exonic outside splice region (new AG motif); V deep intronic; CENATAC P deep intronic on MANE, CDS on non-MANE", "PASS", "motif check is not a splice prediction; no SpliceAI/MaxEnt installed"),
 ("RUN-D-roh", "k3_roh_het.py", "proband VCF (private)", "bcftools 1.19 roh; python 3.12.3", "bcftools roh -G30 --AF-dflt 0.4; 1-Mb window het p5 rule", "private_runs/D_roh_het.json, D_bcftools_roh.txt", "no gene in ROH; no het-depleted window; het calls in all gene bodies", "PASS", "default AF (no population AF file); variant-only VCF; small deletions not detectable"),
 ("RUN-D-phase", "k3_phase.py", "BUB1B markdup BAM", "samtools 1.19.2; bcftools 1.19", "MAPQ>=20 proper pairs; dup removed", "private_runs/D_phase_recheck.json", "0 fragments link any candidate pair; het chains cannot bridge", "PASS", "short-read limit"),
 ("RUN-D-svcov-BUB1B", "k3_sv_cov.py + k3_disc_detail.py + k3_cluster_probe.py", "BUB1B markdup BAM", "samtools 1.19.2; python 3.12.3", "see script headers", "private_runs/D_sv_cov_BUB1B.json, D_disc_detail_BUB1B.json, D_cluster_probe_BUB1B.json", "no CNV-like run; 3 discordant clusters, none insertion-like; 1 weak oriented cluster (<5 fragments) unexplained; no exon-boundary clip signature", "PASS", "insertions/balanced events can be missed; locus-recovered reads only"),
 ("RUN-C-lit", "k3_lit.py", "Europe PMC REST (public queries)", "python 3.12.3 urllib", "queries L01-L08 (cited sort), L03r-L09r (relevance), abstracts by PMID/DOI", "private_runs/C_lit_*.json", "precedents retrieved; abstracts re-read raw", "PASS", "abstract level only"),
]
extra += [
 ("RUN-B-exoncall", "k3_exon_callable.py", "BUB1B and three-locus markdup BAMs; GFF3", "samtools 1.19.2; python 3.12.3", "MANE CDS +-10 bp; samtools depth -a -Q20; DP>=10/20", "private_runs/B_exon_callable.json", "all four genes >=99% callable at DP>=20; no zero-depth coding base", "PASS", "coding small variants only; locus-recovered reads"),
 ("RUN-B-rrecords", "k3_rrecords.py", "three-locus markdup BAM; M1 table", "samtools 1.19.2; bcftools 1.19; python 3.12.3", "fragment counts MAPQ>=20 BQ>=13 dup removed; bcftools mpileup/call -m q20 Q13, +-10 bp window, equivalent-indel matching", "private_runs/B_rrecords_*.json", "TRIP13 3/3 re-called (2 low-depth: <3 alt fragments); CEP57 3/3; CENATAC 9/12 (3 hom-alt non-coding indels not reproduced)", "PARTIAL", "indel representation differs between callers; homopolymer indels"),
 ("RUN-B-mappability", "k3_mappability.py", "GRCh38 analysis-set FASTA and bwa index", "bwa 0.7.17-r1188 mem -a; samtools 1.19.2", "+-50 and +-100 bp ref/alt flanks; unique = on target, MAPQ>=30, no secondary within AS-10", "private_runs/B_mappability.json", "all 16 flank queries unique", "PASS", "reference-based; non-reference paralogs not covered"),
 ("RUN-D-followup", "k3_followup.py", "QC and SV JSONs; BAMs; VCF", "samtools 1.19.2; bcftools 1.19; python 3.12.3", "see script header (MAPQ>=20 read filter after consistency fix)", "private_runs/D_followup.json", "CENATAC P: SOR>3 and homopolymer-adjacent; TRIP13 runs technical-pattern; CEP57 intronic oriented cluster unresolved", "PASS", "heuristic; no SV caller installed"),
]
for e in extra:
    runs.append(list(e))
for f in sorted(glob.glob(f"{R}/D_sv_cov_*.json")):
    g = json.load(open(f))["gene"]
    if g != "BUB1B":
        runs.append([f"RUN-D-svcov-{g}", "k3_sv_cov.py + k3_disc_detail.py (+ k3_cluster_probe.py if oriented)", "K3 three-locus BAM (markdup)", "bwa 0.7.17-r1188; samtools 1.19.2; python 3.12.3",
                     "locus screen as T2F-1 (gene +-100 kb); see script headers", f"private_runs/{os.path.basename(f)}", "see K3_POPULATION_PHASE_INHERITANCE.md", "PASS", "locus-recovered reads only; insertions/balanced events can be missed"])
for f in sorted(glob.glob(f"{R}/NOTRUN_*.json")):
    d = json.load(open(f))
    runs.append([d["id"], d["script"], d["inputs"], d["software"], d["params"], "-", d["summary"], "NOT RUN", d["reason"]])
with open(f"{K}/K3_TEST_RUNS.tsv", "w") as fh:
    fh.write("run_id\tscript\tinputs_and_hashes\tsoftware_versions\tparameters\traw_result_location (private)\tsummary\tstatus\tlimitations\n")
    for r in runs:
        fh.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
os.chmod(f"{K}/K3_VARIANT_QC.tsv", 0o600); os.chmod(f"{K}/K3_TEST_RUNS.tsv", 0o600)
print("QC rows", len(rows), "| test runs", len(runs))
