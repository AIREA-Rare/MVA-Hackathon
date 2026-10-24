"""T2F-1 analysis: BUB1B locus depth, callability, SV signals, read-level allele checks and small-variant re-call.

Restricted: reads a patient-derived BAM in the private root and writes only there. Prints aggregate numbers and
position labels only (no read, sequence or coordinate). Standard library + samtools/bcftools 1.19.

usage: locus_analysis.py BAM OUT_DIR CONTIG OFFSET GENE_START GENE_END LOCUS_START LOCUS_END FASTA VCF POSITIONS_TSV
  OFFSET is added to BAM positions to get GRCh38 positions (0 for a genome-aligned BAM; LOCUS_START-1 for the
  locus-reference probe). GENE_*/LOCUS_* are GRCh38 1-based inclusive. POSITIONS_TSV: label, pos, ref, alt (SNVs).

Outputs: SUMMARY.json, depth_windows.tsv, sv_signals.tsv, position_checks.tsv.
"""
import json
import os
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict

MIN_MAPQ, MIN_BASEQ, CALLABLE_DP, WINDOW, SV_NEAR = 20, 13, 10, 1000, 1000
CIGAR_OP = re.compile(r"(\d+)([MIDNSHP=X])")
POSITION_FIELDS = ("label", "pos", "ref", "alt", "depth_all", "depth_q20", "ref_reads_q20", "alt_reads_q20",
                   "other_reads_q20", "alt_fraction_q20", "mean_mapq_all", "fraction_mapq_ge20", "callable_q20",
                   "window_ratio_to_flank", "sv_signals_within_1kb", "recall_gt", "supplied_vcf_gt")


def reg(contig, start, end):
    """samtools region string; braces protect a contig name that itself contains ':' (the locus-reference probe)."""
    return f"{{{contig}}}:{start}-{end}" if ":" in contig else f"{contig}:{start}-{end}"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", check=True, **kw).stdout


def pileup_bases(s):
    """Counts of 'ref' and A/C/G/T/N/'*' in an mpileup base string; skips ^Q read starts, $ ends and +n/-n indels."""
    counts, i = Counter(), 0
    while i < len(s):
        c = s[i]
        if c == "^":
            i += 2
            continue
        if c in "+-":
            j = i + 1
            while j < len(s) and s[j].isdigit():
                j += 1
            i = j + int(s[i + 1:j])
            continue
        if c in ".,":
            counts["ref"] += 1
        elif c.upper() in "ACGTN*":
            counts[c.upper()] += 1
        i += 1
    return counts


def main(bam, out, contig, offset, gs, ge, ls, le, fasta, vcf, positions):
    offset, gs, ge, ls, le = int(offset), int(gs), int(ge), int(ls), int(le)
    os.umask(0o077)
    os.makedirs(out, mode=0o700, exist_ok=True)
    region = reg(contig, ls - offset, le - offset)
    summary = {"bam_sha256": run(["sha256sum", bam]).split()[0], "region_grch38": f"15:{ls}-{le}",
               "gene_body_grch38": f"15:{gs}-{ge}", "tools": run(["samtools", "--version"]).split("\n")[0],
               "filters": {"min_mapq": MIN_MAPQ, "min_baseq": MIN_BASEQ, "callable_dp": CALLABLE_DP,
                           "window_bp": WINDOW, "sv_near_bp": SV_NEAR,
                           "duplicates": "reads flagged 0x400 are excluded everywhere (samtools depth/mpileup and "
                                         "bcftools mpileup by default; SV scan via -F 0xD04); with an unmarked BAM "
                                         "no read is flagged, so nothing is excluded"},
               "duplicates_flagged_in_bam": int(run(["samtools", "view", "-c", "-f", "0x400", bam]).strip())}

    # 1. per-base depth (all positions), MAPQ/BASEQ filtered
    depth = {}
    for line in run(["samtools", "depth", "-a", "-Q", str(MIN_MAPQ), "-q", str(MIN_BASEQ), "-r", region, bam]).splitlines():
        _, pos, dp = line.split("\t")
        depth[int(pos) + offset] = int(dp)
    in_gene = [depth.get(p, 0) for p in range(gs, ge + 1)]
    flank = [depth.get(p, 0) for p in list(range(ls, gs)) + list(range(ge + 1, le + 1))]
    med_flank = statistics.median(flank)
    summary["depth"] = {"gene_body_median": statistics.median(in_gene), "flank_median": med_flank,
                        "gene_over_flank": round(statistics.median(in_gene) / med_flank, 3) if med_flank else None,
                        "gene_body_callable_fraction": round(sum(d >= CALLABLE_DP for d in in_gene) / len(in_gene), 4),
                        "flank_callable_fraction": round(sum(d >= CALLABLE_DP for d in flank) / len(flank), 4),
                        "gene_body_zero_depth_bases": sum(d == 0 for d in in_gene)}
    windows = []
    for start in range(ls, le + 1, WINDOW):
        vals = [depth.get(p, 0) for p in range(start, min(start + WINDOW, le + 1))]
        ratio = statistics.median(vals) / med_flank if med_flank else None
        part = "gene" if gs <= start + WINDOW // 2 <= ge else "flank"
        windows.append((start, part, statistics.median(vals), round(ratio, 3) if ratio is not None else None,
                        round(sum(v >= CALLABLE_DP for v in vals) / len(vals), 3)))
    with open(os.path.join(out, "depth_windows.tsv"), "w") as h:
        h.write("window_start\tpart\tmedian_dp\tratio_to_flank_median\tcallable_fraction\n")
        h.writelines("\t".join(map(str, w)) + "\n" for w in windows)

    def band(ws):
        vals = [w[3] for w in ws if w[3] is not None]
        return {"n": len(ws), "lt_0.65": sum(v < 0.65 for v in vals), "gt_1.40": sum(v > 1.40 for v in vals),
                "ratio_min": min(vals, default=None), "ratio_max": max(vals, default=None)}
    gene_w = [w for w in windows if w[1] == "gene"]
    longest = run_len = 0
    for w in gene_w:
        run_len = run_len + 1 if w[3] is not None and w[3] < 0.65 else 0
        longest = max(longest, run_len)
    summary["windows"] = {"gene": band(gene_w), "flank": band([w for w in windows if w[1] == "flank"]),
                          "gene_longest_run_lt_0.65_windows": longest}

    # 2. SV signals among primary, non-duplicate alignments with MAPQ >= 20 in the region
    disc, clips = defaultdict(int), Counter()
    n_reads = 0
    for line in run(["samtools", "view", "-F", "0xD04", "-q", str(MIN_MAPQ), bam, region]).splitlines():
        f = line.split("\t")
        flag, pos, cigar, rnext, tlen = int(f[1]), int(f[3]) + offset, f[5], f[6], abs(int(f[8]))
        n_reads += 1
        if flag & 1 and not flag & 8 and (not flag & 2 or rnext != "=" or tlen > 2000):
            disc[(pos // 500) * 500] += 1
        ops = [(int(n), op) for n, op in CIGAR_OP.findall(cigar)]
        if ops and ops[0][1] == "S" and ops[0][0] >= 20:
            clips[pos] += 1  # clipped bases before the first aligned base
        if ops and ops[-1][1] == "S" and ops[-1][0] >= 20:
            clips[pos + sum(n for n, op in ops if op in "MDN=X")] += 1  # first reference base after the alignment
    disc_clusters = sorted((b, n) for b, n in disc.items() if n >= 3)
    clip_clusters = sorted((p, n) for p, n in clips.items() if n >= 3)
    with open(os.path.join(out, "sv_signals.tsv"), "w") as h:
        h.write("type\tposition_or_bin\tsupport\tpart\n")
        for b, n in disc_clusters:
            h.write(f"discordant_500bp_bin\t{b}\t{n}\t{'gene' if gs <= b <= ge else 'flank'}\n")
        for p, n in clip_clusters:
            h.write(f"softclip_ge20_same_pos\t{p}\t{n}\t{'gene' if gs <= p <= ge else 'flank'}\n")
    summary["sv_signals"] = {"reads_considered": n_reads,
                             "discordant_bins_ge3": {"gene": sum(gs <= b <= ge for b, _ in disc_clusters),
                                                     "flank": sum(not gs <= b <= ge for b, _ in disc_clusters)},
                             "clip_positions_ge3": {"gene": sum(gs <= p <= ge for p, _ in clip_clusters),
                                                    "flank": sum(not gs <= p <= ge for p, _ in clip_clusters)},
                             "max_support_gene": max([n for b, n in disc_clusters if gs <= b <= ge] +
                                                     [n for p, n in clip_clusters if gs <= p <= ge] + [0])}

    # 3. small-variant re-call over the whole locus (genome-aligned BAM only); concordance in the gene body
    recall, supplied = {}, {}
    if offset == 0:
        q = "bcftools query -f '%CHROM:%POS:%REF:%ALT\\t[%GT]\\n'"
        calls = run(["bash", "-c", f"bcftools mpileup -q {MIN_MAPQ} -Q {MIN_BASEQ} -a AD,DP -f '{fasta}' -r {region} "
                     f"'{bam}' 2>/dev/null | bcftools call -mv 2>/dev/null | bcftools norm -m -any -f '{fasta}' "
                     f"2>/dev/null | {q}"])
        recall = dict(l.split("\t") for l in calls.splitlines() if l)
        supplied = dict(l.split("\t") for l in run(["bash", "-c", f"bcftools norm -m -any -f '{fasta}' -r {region} "
                        f"'{vcf}' 2>/dev/null | {q}"]).splitlines() if l)
        in_gene_key = lambda k: gs <= int(k.split(":")[1]) <= ge  # noqa: E731
        rg, sg = {k for k in recall if in_gene_key(k)}, {k for k in supplied if in_gene_key(k)}
        summary["recall_gene_body"] = {"supplied_vcf_records": len(sg), "recalled": len(rg), "in_both": len(rg & sg),
                                       "only_supplied": len(sg - rg), "only_recalled": len(rg - sg),
                                       "only_recalled_het": sum(recall[k] in ("0/1", "1/0") for k in rg - sg)}

    # 4. read-level checks at the private positions (template fields; see POSITION_FIELDS)
    rows = []
    for line in open(positions):
        label, pos, ref, alt = line.rstrip("\n").split("\t")
        pos = int(pos)
        r = reg(contig, pos - offset, pos - offset)
        # -f gives the reference so that reference-matching bases print as '.'/','; without it they print as letters
        # (fix1, 2026-10-22: the first run omitted -f and counted reference reads as "other")
        filt = run(["samtools", "mpileup", "-f", fasta, "-Q", str(MIN_BASEQ), "-q", str(MIN_MAPQ), "-r", r,
                    bam]).strip().split("\t")
        allr = run(["samtools", "mpileup", "-f", fasta, "-Q", "0", "-q", "0", "-s", "-r", r,
                    bam]).strip().split("\t")  # duplicates excluded by mpileup defaults
        if len(filt) > 2 and filt[2].upper() != ref.upper():
            raise SystemExit(f"reference base mismatch at check position {label}")
        counts = pileup_bases(filt[4]) if len(filt) > 4 else Counter()
        ref_n = counts["ref"] + counts[ref.upper()]
        alt_n = counts[alt.upper()]
        mq = [ord(c) - 33 for c in allr[6]] if len(allr) > 6 else []
        win = next((w for w in windows if w[0] <= pos < w[0] + WINDOW), None)
        near = sum(1 for b, _ in disc_clusters if abs(b + 250 - pos) <= SV_NEAR) + \
            sum(1 for p, _ in clip_clusters if abs(p - pos) <= SV_NEAR)
        key = f"{contig}:{pos}:{ref}:{alt}"
        rows.append({"label": label, "pos": pos, "ref": ref, "alt": alt,
                     "depth_all": int(allr[3]) if len(allr) > 3 else 0,
                     "depth_q20": int(filt[3]) if len(filt) > 3 else 0, "ref_reads_q20": ref_n,
                     "alt_reads_q20": alt_n, "other_reads_q20": sum(counts.values()) - ref_n - alt_n,
                     "alt_fraction_q20": round(alt_n / (ref_n + alt_n), 3) if ref_n + alt_n else None,
                     "mean_mapq_all": round(statistics.mean(mq), 1) if mq else None,
                     "fraction_mapq_ge20": round(sum(m >= MIN_MAPQ for m in mq) / len(mq), 3) if mq else None,
                     "callable_q20": (int(filt[3]) if len(filt) > 3 else 0) >= CALLABLE_DP,
                     "window_ratio_to_flank": win[3] if win else None, "sv_signals_within_1kb": near,
                     "recall_gt": recall.get(key, "no variant call") if offset == 0 else "not run (probe)",
                     "supplied_vcf_gt": supplied.get(key, "no record") if offset == 0 else "not run (probe)"})
    with open(os.path.join(out, "position_checks.tsv"), "w") as h:
        h.write("\t".join(POSITION_FIELDS) + "\n")
        h.writelines("\t".join(str(row[f]) for f in POSITION_FIELDS) + "\n" for row in rows)
    summary["position_checks"] = {row["label"]: {k: v for k, v in row.items() if k not in ("pos", "ref", "alt")}
                                  for row in rows}
    with open(os.path.join(out, "SUMMARY.json"), "w") as h:
        json.dump(summary, h, indent=2, sort_keys=True)
    print(json.dumps({k: v for k, v in summary.items() if k != "bam_sha256"}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(*sys.argv[1:])
