#!/bin/bash
# Builds the private list of positions for read-level allele counts: BUB1B T and P, the intronic ClinVar-VUS record,
# and the ClinVar Pathogenic upstream record (public). Prints labels and allele lengths only.
set -euo pipefail
umask 077
: "${MVA_DATA_ROOT:?set MVA_DATA_ROOT to the private data root}"
: "${MVA_PRIVATE_ENV:?set MVA_PRIVATE_ENV to the private variable file}"; . "$MVA_PRIVATE_ENV"
O="$MVA_DATA_ROOT/out/T2F_clinvar_panel_2026-10-22"
F="$MVA_DATA_ROOT/work/T2F_bub1b_locus_2026-10-22/check_positions.tsv"
{
  printf "BUB1B_T\t%s\t%s\t%s\n" "$BUB1B_T_POS" "$BUB1B_T_REF" "$BUB1B_T_ALT"
  printf "BUB1B_P\t%s\t%s\t%s\n" "$BUB1B_P_POS" "$BUB1B_P_REF" "$BUB1B_P_ALT"
  awk -F'\t' -v OFS='\t' '$8 ~ /Uncertain/ && $10 ~ /BUB1B/ {print "BUB1B_intronic_VUS", $2, $3, $4}' "$O/proband_panel_clinvar.tsv"
  awk -F'\t' -v OFS='\t' '$6 ~ /^Pathogenic/ {print "ClinVar_upstream_pathogenic_not_in_VCF", $2, $3, $4}' "$O/clinvar_bub1b_upstream_records.tsv"
} > "$F"
awk -F'\t' '{print $1, "ref_len", length($3), "alt_len", length($4)}' "$F"
