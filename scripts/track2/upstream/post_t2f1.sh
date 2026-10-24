#!/bin/bash
# Post-T2F-1 steps, run one at a time: post_t2f1.sh verify|preflight|markdup|analysis
# Each step stops with a non-zero exit and a message on any missing item or inconsistency.
# The original realigned_genome.bam is never modified (its SHA-256 is compared before and after markdup).
set -uo pipefail
umask 077
: "${MVA_DATA_ROOT:?set MVA_DATA_ROOT to the private data root}"
P="$MVA_DATA_ROOT"
W="$P/work/T2F_bub1b_locus_2026-10-22"
O="$P/out/T2F_bub1b_locus_analysis_2026-10-22"
S="$(cd "$(dirname "$0")" && pwd)"
BAM="$W/realigned_genome.bam"
MD="$W/postproc_2026-10-22"
fail() { echo "STOP: $*"; exit 1; }

case "${1:-}" in
verify)
  grep -q "end T2F-1" "$W/RUN_LOG.txt" || fail "RUN_LOG has no 'end T2F-1'"
  for L in L001 L002 L003 L004; do
    [ -e "$W/pass1_$L.bam.done" ] || fail "missing pass1_$L.bam.done"
    n=$(cat "$W/pass1_$L.pairs_seen" 2>/dev/null); [[ "$n" =~ ^[0-9]+$ && "$n" -gt 0 ]] || fail "pairs_seen $L empty or invalid"
    echo "lane $L: read names seen $n"
  done
  samtools quickcheck -v "$BAM" || fail "quickcheck failed on realigned_genome.bam"
  [ -s "$BAM.bai" ] || fail "realigned_genome.bam index missing"
  samtools flagstat "$BAM" > "$W/flagstat_realigned_genome.txt" || fail "flagstat failed"
  cat "$W/flagstat_realigned_genome.txt"
  kept=$(grep -o "kept pairs: [0-9]*" "$W/RUN_LOG.txt" | awk '{print $3}')
  prim=$(grep -m1 " primary$" "$W/flagstat_realigned_genome.txt" | awk '{print $1}')
  echo "kept pairs (log) $kept | primary records (flagstat) $prim | expected 2 x kept = $((kept * 2))"
  [ "$prim" -eq $((kept * 2)) ] || fail "primary records != 2 x kept pairs"
  grep -E "Elapsed|Maximum resident" "$W"/pass1_L00?.time "$W/pass2.time"
  echo "VERIFY OK" ;;
preflight)
  grep -q "VERIFY OK" <(bash "$0" verify 2>&1) || fail "verify step does not pass"
  echo "samtools: $(samtools --version | head -1)"
  so=$(samtools view -H "$BAM" | awk -F'\t' '$1=="@HD" {for (i=2;i<=NF;i++) if ($i ~ /^SO:/) print substr($i,4)}')
  echo "sort order: ${so:-not stated}"
  [ "$so" = "coordinate" ] || fail "BAM is not coordinate-sorted"
  echo "fixmate needs name-grouped input: the BAM is coordinate-sorted, so 'samtools sort -n' runs first (separate file)"
  paired=$(samtools view -c -f 1 -F 0x900 "$BAM"); mc=$(samtools view -F 0x904 -f 1 "$BAM" | grep -c "MC:Z:")
  echo "primary paired records $paired | with MC tag before fixmate $mc (fixmate -m adds MC and ms)"
  pgrep -x bwa >/dev/null && fail "a bwa process is still running"
  avail=$(free -m | awk '/^Mem:/ {print $7}'); echo "available memory MB: $avail"; [ "$avail" -ge 2000 ] || fail "less than 2 GB memory available"
  free_gb=$(df -BG --output=avail "$P" | tail -1 | tr -dc 0-9); echo "free disk GB: $free_gb"; [ "$free_gb" -ge 20 ] || fail "less than 20 GB free disk"
  echo "PREFLIGHT OK" ;;
markdup)
  grep -q "PREFLIGHT OK" <(bash "$0" preflight 2>&1) || fail "preflight step does not pass"
  mkdir -p "$MD"
  before=$(sha256sum "$BAM" | cut -d' ' -f1)
  samtools sort -n -m 256M -@ 1 -o "$MD/name_sorted.bam" "$BAM" || fail "sort -n"
  samtools fixmate -m "$MD/name_sorted.bam" "$MD/fixmate.bam" || fail "fixmate"
  samtools sort -m 256M -@ 1 -o "$MD/fixmate_coord.bam" "$MD/fixmate.bam" || fail "sort"
  samtools markdup -s -f "$MD/markdup_stats.txt" "$MD/fixmate_coord.bam" "$MD/markdup.bam" || fail "markdup"
  samtools index "$MD/markdup.bam" || fail "index"
  samtools quickcheck -v "$MD/markdup.bam" || fail "quickcheck markdup.bam"
  after=$(sha256sum "$BAM" | cut -d' ' -f1)
  [ "$before" = "$after" ] || fail "original BAM changed"
  echo "original BAM unchanged: $before"
  samtools flagstat "$MD/markdup.bam" > "$MD/flagstat_markdup.txt"
  echo "== flagstat before -> after (first 14 lines)"; paste -d'|' <(head -14 "$W/flagstat_realigned_genome.txt") <(head -14 "$MD/flagstat_markdup.txt")
  echo "duplicate-flagged records: before $(samtools view -c -f 0x400 "$BAM") | after $(samtools view -c -f 0x400 "$MD/markdup.bam")"
  echo "== markdup stats"; cat "$MD/markdup_stats.txt"
  sha256sum "$MD"/markdup.bam "$MD"/markdup_stats.txt "$MD"/flagstat_markdup.txt > "$MD/SHA256SUMS.txt"
  echo "MARKDUP OK" ;;
analysis)
  [ -s "$MD/markdup.bam.bai" ] && grep -q markdup.bam "$MD/SHA256SUMS.txt" || fail "markdup output missing"
  read -r CHR LS LE GS GE < "$W/locus_coords.tsv"
  FA="$P/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
  VCF="${MVA_VCF:-$(ls "$P"/raw/*.vcf.gz | head -1)}"
  for v in markdup:"$MD/markdup.bam" unmarked:"$BAM"; do
    name=${v%%:*}; b=${v#*:}
    echo "=========== analysis on $name BAM"
    [ -e "$O/${name}_fix1" ] && fail "$O/${name}_fix1 exists; refusing to overwrite"
    python3 -B "$S/locus_analysis.py" "$b" "$O/${name}_fix1" "$CHR" 0 "$GS" "$GE" "$LS" "$LE" "$FA" "$VCF" "$W/check_positions.tsv" \
      || fail "analysis on $name"
  done
  echo "ANALYSIS OK" ;;
*) echo "usage: $0 verify|preflight|markdup|analysis"; exit 2 ;;
esac
