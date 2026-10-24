#!/bin/bash
# T2F-1: BUB1B locus read recovery from the eight FASTQ files (restricted; private root only).
# Pass 1: every read pair against the BUB1B +-250 kb locus reference; keep a pair when any mate has >= 60 aligned
#         bases with NM <= 2 (keeps clipped and discordant reads for SV evidence).
# Pass 2: kept pairs realigned to the full GRCh38 analysis set; sorted, indexed.
# Prints progress counts only; no read, sequence or genotype is printed.
set -euo pipefail
umask 077
: "${MVA_DATA_ROOT:?set MVA_DATA_ROOT to the private data root}"
R="$MVA_DATA_ROOT"
FASTQ_PREFIX="${MVA_FASTQ_PREFIX:?set MVA_FASTQ_PREFIX (FASTQ file-name prefix; private)}"
W="$R/work/T2F_bub1b_locus_2026-10-22"
FQ="$R/raw/fastq_2026-10-20"
IDX="$R/work/bwa_index_GRCh38_noalt_hs38d1_2026-10-20/GRCh38_noalt_hs38d1.nochr"
LOG="$W/RUN_LOG.txt"
log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$LOG"; }
log "start T2F-1 | bwa $(bwa 2>&1 | grep -m1 Version) | $(samtools --version | head -1) | nproc $(nproc)"
for L in L001 L002 L003 L004; do
  out="$W/pass1_$L.bam"
  if [ -s "$out" ] && [ -s "$out.done" ]; then log "pass1 $L already done"; continue; fi
  log "pass1 $L start"
  /usr/bin/time -v -o "$W/pass1_$L.time" bash -c "
    bwa mem -t 11 -v 1 '$W/locus.fa' '$FQ/${FASTQ_PREFIX}_${L}_R1_001.fastq.gz' \
        '$FQ/${FASTQ_PREFIX}_${L}_R2_001.fastq.gz' 2> '$W/pass1_$L.bwa.stderr' |
    awk -F'\t' -v OFS='\t' '
      function alen(c,  n,t,s){s=0; while (match(c,/[0-9]+[MIDNSHP=X]/)) {n=substr(c,RSTART,RLENGTH-1)+0;
        t=substr(c,RSTART+RLENGTH-1,1); if (t==\"M\"||t==\"=\"||t==\"X\"||t==\"I\") s+=n; c=substr(c,RSTART+RLENGTH)} return s}
      /^@/ {print; next}
      \$1 != q { if (keep) for (i=1;i<=n;i++) print buf[i]; q=\$1; n=0; keep=0; total++ }
      { buf[++n]=\$0
        if (!and(\$2,4)) { nm=99; for (i=12;i<=NF;i++) if (\$i ~ /^NM:i:/) nm=substr(\$i,6)+0
                           if (alen(\$6) >= 60 && nm <= 2) keep=1 } }
      END { if (keep) for (i=1;i<=n;i++) print buf[i]; print total > \"/dev/stderr\" }' 2> '$W/pass1_$L.pairs_seen' |
    samtools view -b -o '$out' -"
  touch "$out.done"
  log "pass1 $L done | read names seen $(cat "$W/pass1_$L.pairs_seen") | kept records $(samtools view -c "$out") | $(grep -E 'Elapsed' "$W/pass1_$L.time" | sed 's/^\s*//')"
done
log "pass2 start: collate kept pairs and realign to the full analysis set"
samtools cat -o "$W/pass1_all.bam" "$W"/pass1_L00?.bam
samtools view -b -F 0x900 "$W/pass1_all.bam" | samtools collate -O -u - "$W/collate_tmp" |
  samtools fastq -1 "$W/kept_R1.fq.gz" -2 "$W/kept_R2.fq.gz" -0 /dev/null -s /dev/null -n - 2> "$W/fastq.stderr"
log "kept pairs: $(( $(zcat "$W/kept_R1.fq.gz" | wc -l) / 4 ))"
/usr/bin/time -v -o "$W/pass2.time" bash -c "
  bwa mem -t 10 -v 1 -R '@RG\tID:T2F\tSM:proband\tPL:ILLUMINA' '$IDX' '$W/kept_R1.fq.gz' '$W/kept_R2.fq.gz' \
      2> '$W/pass2_bwa.stderr' | samtools sort -m 256M -@ 1 -o '$W/realigned_genome.bam' -"
samtools index "$W/realigned_genome.bam"
log "pass2 done | $(grep -E 'Elapsed|Maximum resident' "$W/pass2.time" | sed 's/^\s*//' | tr '\n' ' ')"
log "realigned records $(samtools view -c "$W/realigned_genome.bam") | in locus MAPQ>=20 $(samtools view -c -q 20 "$W/realigned_genome.bam" "$(cut -f1-3 "$W/locus_coords.tsv" | awk '{print $1":"$2"-"$3}')")"
sha256sum "$W/realigned_genome.bam" "$W/locus.fa" >> "$W/SHA256SUMS.txt"
log "end T2F-1"
