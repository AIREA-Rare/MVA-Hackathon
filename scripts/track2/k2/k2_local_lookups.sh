#!/bin/bash
# K2 local read-only lookups (private outputs): CENATAC P record annotation by transcript (+ GFF3 biotype/tags of those
# transcripts); BUB1B T and intronic VUS in the local gnomAD v4.1.1 exome extract (T2AB) and genome extract.
set -uo pipefail
umask 077
: "${MVA_DATA_ROOT:?set MVA_DATA_ROOT to the private data root}"
: "${MVA_PRIVATE_ENV:?set MVA_PRIVATE_ENV to the private variable file}"; . "$MVA_PRIVATE_ENV"
P="$MVA_DATA_ROOT"; O="$P/out/T2K2_literature_mechanism_2026-10-23"
E2="$P/work/E2_csq_2026-10-16/annotated_bcsq.vcf.gz"
GFF="$P/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz"
EXO="$P/ref/gnomad_v4.1.1_exomes_chr15_BUB1B_gene_2026-10-23/region.vcf.gz"
GEN="$P/ref/gnomad_v4.1.1_genomes_chr15_BUB1B_region_2026-10-19/region.vcf.gz"
{
echo "== CENATAC P record: BCSQ entries (gene|transcript|biotype|strand|change)"
bcftools query -r "$CENATAC_P_REGION" -f '%REF>%ALT\t%INFO/BCSQ\n' "$E2" | tr ',' '\n' | awk -F'|' '{print $1"|"$2"|"$3"|"$4"|"$5"|"$6}'
echo "== GFF3 tags for CENATAC transcripts named above"
for t in $(bcftools query -r "$CENATAC_P_REGION" -f '%INFO/BCSQ\n' "$E2" | tr ',' '\n' | awk -F'|' '$2=="CENATAC"{print $3}' | sort -u); do
  zcat "$GFF" | awk -F'\t' -v T="transcript_id=$t;" '$3!="exon" && $3!="CDS" && index($9,T){print $3"\t"$4"\t"$5"\t"$9; exit}' | cut -c1-300
done
echo "== MANE CENATAC transcript is ENST00000334418 (integrated matrix); does the record fall in its CDS?"
zcat "$GFF" | awk -F'\t' -v P="$CENATAC_P_POS" '$3=="CDS" && $9 ~ /Parent=transcript:ENST00000334418;/ && $4<=P && $5>=P {print "inside MANE CDS segment", $4"-"$5}' | head -2
zcat "$GFF" | awk -F'\t' -v P="$CENATAC_P_POS" '$3=="five_prime_UTR" || $3=="three_prime_UTR" {if ($9 ~ /Parent=transcript:ENST00000334418;/ && $4<=P && $5>=P) print "inside MANE", $3, $4"-"$5}' | head -2
echo "== BUB1B T (position and alleles from the private variable file) in gnomAD v4.1.1 exome extract"
bcftools view -H -r "$BUB1B_T_REGION" "$EXO" | awk -F'\t' -v R="$BUB1B_T_REF" -v A="$BUB1B_T_ALT" '$4==R && $5==A' | cut -f8 | tr ';' '\n' | grep -E '^(AC|AN|AF|nhomalt)=' | tr '\n' ' '; echo
bcftools view -H -r "$BUB1B_T_REGION" "$EXO" | awk -F'\t' -v R="$BUB1B_T_REF" -v A="$BUB1B_T_ALT" '$4==R && $5==A{print "FILTER", $7}'
echo "== BUB1B T in gnomAD v4.1.1 genome extract"
bcftools view -H -r "$BUB1B_T_REGION" "$GEN" | awk -F'\t' -v R="$BUB1B_T_REF" -v A="$BUB1B_T_ALT" '$4==R && $5==A' | cut -f8 | tr ';' '\n' | grep -E '^(AC|AN|AF|nhomalt)=' | tr '\n' ' '; echo
echo "== BUB1B deep intronic VUS (position from the private variable file) in exome extract (records at position, any allele)"
bcftools view -H -r "$BUB1B_V_REGION" "$EXO" | cut -f1-7 | sed 's/^/  /'; echo "  (end)"
} | tee "$O/LOCAL_LOOKUPS.txt"
chmod 600 "$O/LOCAL_LOOKUPS.txt"
