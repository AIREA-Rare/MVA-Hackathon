#!/bin/bash
# T2F-1 probe: build a BUB1B +-250 kb locus reference and time bwa mem for 1M read pairs against it.
# Writes only inside the private root (umask 077). Prints counts and timings only.
set -euo pipefail
umask 077
: "${MVA_DATA_ROOT:?set MVA_DATA_ROOT to the private data root}"
R="$MVA_DATA_ROOT"
FASTQ_PREFIX="${MVA_FASTQ_PREFIX:?set MVA_FASTQ_PREFIX (FASTQ file-name prefix; private)}"
W="$R/work/T2F_bub1b_locus_2026-10-22"
FA="$R/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
GFF="$R/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz"
FQ="$R/raw/fastq_2026-10-20"
mkdir -p "$W"
read -r CHR S E STR < <(zcat "$GFF" | awk -F'\t' '$3=="gene" && $9 ~ /(^|;)Name=BUB1B(;|$)/ {print $1, $4, $5, $7}')
echo "gene span (Ensembl 116, public reference): $CHR:$S-$E strand $STR"
LS=$((S - 250000)); LE=$((E + 250000))
printf "%s\t%s\t%s\t%s\t%s\n" "$CHR" "$LS" "$LE" "$S" "$E" > "$W/locus_coords.tsv"
samtools faidx "$FA" "$CHR:$LS-$LE" > "$W/locus.fa"
bwa index "$W/locus.fa" 2> "$W/locus_index.stderr"
echo "locus: $CHR:$LS-$LE ($((LE - LS + 1)) bp); index built"
/usr/bin/time -v -o "$W/probe.time" bash -c "bwa mem -t 10 '$W/locus.fa' <(zcat '$FQ/${FASTQ_PREFIX}_L001_R1_001.fastq.gz' | head -n 4000000) <(zcat '$FQ/${FASTQ_PREFIX}_L001_R2_001.fastq.gz' | head -n 4000000) 2> '$W/probe_bwa.stderr' | samtools view -b -F 4 -o '$W/probe_mapped.bam' -"
echo "probe 1M pairs: mapped records $(samtools view -c "$W/probe_mapped.bam") | MAPQ>=20 $(samtools view -c -q 20 "$W/probe_mapped.bam")"
grep -E "Elapsed|Maximum resident|Percent of CPU" "$W/probe.time"
echo "== decompression-only timing for 1M pairs (one file)"
/usr/bin/time -f "%e s" bash -c "zcat '$FQ/${FASTQ_PREFIX}_L001_R1_001.fastq.gz' | head -n 4000000 > /dev/null"
echo "== read-count estimate: bytes per 1M reads in gz (R1 L001)"
zcat "$FQ/${FASTQ_PREFIX}_L001_R1_001.fastq.gz" | head -n 4000000 | gzip -1 | wc -c
ls -l "$W" | awk '{print $1, $5, $9}'
