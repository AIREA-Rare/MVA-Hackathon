#!/bin/bash
# K3-B/D: read recovery for TRIP13, CEP57 and CENATAC (each gene +-100 kb, Ensembl 116 gene spans), same method as
# T2F-1 (BUB1B): pass 1 every read pair against the three-locus reference, keep a pair when any mate has >= 60 aligned
# bases with NM <= 2; pass 2 realign kept pairs to the full GRCh38 analysis set; then fixmate/markdup (samtools).
# Private root only. Prints progress counts only; no read, sequence, genotype or identifier is printed.
# Resumable: finished lanes are skipped (.done markers).
set -euo pipefail
umask 077
: "${MVA_DATA_ROOT:?set MVA_DATA_ROOT to the private data root}"
R="$MVA_DATA_ROOT"
W="$R/work/T2K3_locus_screen_2026-10-23"
FQ="$R/raw/fastq_2026-10-20"
FA="$R/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
IDX="$R/work/bwa_index_GRCh38_noalt_hs38d1_2026-10-20/GRCh38_noalt_hs38d1.nochr"
mkdir -p "$W"; chmod 700 "$W"
LOG="$W/RUN_LOG.txt"
log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }
printf '5\t792849\t1019357\tTRIP13\n11\t95689965\t95937070\tCEP57\n11\t118898051\t119115811\tCENATAC\n' > "$W/locus_coords.tsv"
if [ ! -s "$W/locus.fa.bwt" ]; then
  samtools faidx "$FA" $(awk '{print $1":"$2"-"$3}' "$W/locus_coords.tsv") > "$W/locus.fa"
  bwa index "$W/locus.fa" 2> "$W/locus_index.stderr"
fi
log "start K3 locus screen | bwa $(bwa 2>&1 | grep -m1 Version) | $(samtools --version | head -1) | nproc $(nproc)"
for L in L001 L002 L003 L004; do
  out="$W/pass1_$L.bam"
  if [ -s "$out" ] && [ -s "$out.done" ]; then log "pass1 $L already done"; continue; fi
  R1=$(ls "$FQ"/*"${L}_R1_001.fastq.gz"); R2=$(ls "$FQ"/*"${L}_R2_001.fastq.gz")
  log "pass1 $L start"
  /usr/bin/time -v -o "$W/pass1_$L.time" bash -c "
    bwa mem -t 11 -v 1 '$W/locus.fa' '$R1' '$R2' 2> '$W/pass1_$L.bwa.stderr' |
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
if [ ! -s "$W/realigned_genome.bam.bai" ]; then
  log "pass2 start"
  samtools cat -o "$W/pass1_all.bam" "$W"/pass1_L00?.bam
  samtools view -b -F 0x900 "$W/pass1_all.bam" | samtools collate -O -u - "$W/collate_tmp" |
    samtools fastq -1 "$W/kept_R1.fq.gz" -2 "$W/kept_R2.fq.gz" -0 /dev/null -s /dev/null -n - 2> "$W/fastq.stderr"
  /usr/bin/time -v -o "$W/pass2.time" bash -c "
    bwa mem -t 10 -v 1 -R '@RG\tID:K3\tSM:proband\tPL:ILLUMINA' '$IDX' '$W/kept_R1.fq.gz' '$W/kept_R2.fq.gz' \
        2> '$W/pass2_bwa.stderr' | samtools sort -m 256M -@ 1 -o '$W/realigned_genome.bam' -"
  samtools index "$W/realigned_genome.bam"
  log "pass2 done | $(grep -E 'Elapsed|Maximum resident' "$W/pass2.time" | sed 's/^\s*//' | tr '\n' ' ')"
fi
if [ ! -s "$W/markdup.bam.bai" ]; then
  samtools sort -n -@ 2 -m 512M -o "$W/name_sorted.bam" "$W/realigned_genome.bam"
  samtools fixmate -m "$W/name_sorted.bam" "$W/fixmate.bam"
  samtools sort -@ 2 -m 512M -o "$W/fixmate_coord.bam" "$W/fixmate.bam"
  samtools markdup -s "$W/fixmate_coord.bam" "$W/markdup.bam" 2> "$W/markdup.stats"
  samtools index "$W/markdup.bam"
  rm -f "$W/name_sorted.bam" "$W/fixmate.bam"
  log "postproc done"
fi
log "realigned records $(samtools view -c "$W/realigned_genome.bam")"
( cd "$W" && sha256sum realigned_genome.bam markdup.bam locus.fa locus_coords.tsv > SHA256SUMS.txt )
find "$W" -type f -exec chmod 600 {} +
log "end K3 locus screen"
