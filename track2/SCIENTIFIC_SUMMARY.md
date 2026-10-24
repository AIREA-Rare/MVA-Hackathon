# Scientific summary, stages K2–K6 (draft, 2026-10-24)

**Status:** research evidence assessment. Not a diagnosis, not a clinical variant classification, not treatment advice. No wet-lab experiment was performed. The underlying restricted records stay in approved private storage; this summary describes the participant's alleles by class only.

Labels: measured, database-observed, predicted, indirect, hypothesis, unknown (defined in `README.md`).

## Boundaries that hold throughout

1. **BUB1B is the leading candidate, not a proven cause.** It leads only because it is the one gene with a complete set of required genetic ingredients (a loss-of-function-class allele plus candidate second variants). That is completeness of a mechanism, not evidence of causation.
2. **BUB1B phase is unresolved.** Cis and trans remain equally compatible with every data source checked.
3. **The BUB1B missense change cannot be classified as damaging.** All support for an effect is indirect, about other variants or models.
4. **The CEP57 intronic signal is unresolved,** both in whether it is real and in what it would do.
5. **No drug has direct evidence of benefit in MVA.** Dasatinib and niacin are indirect research hypotheses only.
6. **The functional work (K6) is designs only.**
7. **Technical validity is not pathogenicity.** High confidence that a call is real says nothing about its effect or about causality.

## The participant's candidate variants, by class

| Short name | Class | Main evidence | Label |
|---|---|---|---|
| BUB1B-T | Truncating (stop-gain) allele | Exact-allele ClinVar record classified Pathogenic/Likely pathogenic, multiple submitters | database-observed |
| | | Predicted to trigger nonsense-mediated decay (NMD): the stop lies more than 50 nt upstream of the last exon–exon junction on the MANE transcript | predicted |
| BUB1B-P | Rare missense change in the BUBR1 pseudokinase domain | Rare in gnomAD; no functional, RNA, phase or mutant-structure data | database-observed; unknown |
| BUB1B-V | Deep-intronic variant | ClinVar: uncertain significance; absent from gnomAD genomes; no splice prediction or RNA | database-observed; unknown |
| CENATAC-P | Variant that is a missense change only on a non-MANE transcript | Deep intronic on the MANE transcript; the alternative isoform has weak annotation support | measured (annotation); unknown (isoform relevance) |
| CEP57 signal | Intronic read-level cluster suggestive of an insertion or rearrangement | Unresolved | unknown |

## K2: literature, mechanism and competing genes

- **Gene-disease validity (GenCC):** BUB1B and CEP57 Definitive for autosomal recessive MVA; CENATAC Limited (one submitter, one report). *database-observed*
- **Competing genes:** TRIP13, CEP57 and CENATAC have no loss-of-function record in the data. They cannot be discriminated against each other. *measured; unknown*
- **Contradictions recorded:** inheritance (an Orphanet "supportive AD" entry against the autosomal recessive consensus); BUBR1 pseudokinase activity (catalytic versus structural role); TRIP13 allelic heterogeneity; a possible duplicate case report. *indirect*
- **Approved therapies:** none directed at the gene defect for any of the four genes; no US label lists MVA. *database-observed*

## K3: read-level re-analysis

- **The three BUB1B calls are technically real in this sample.** Each passes ten pre-declared read-level tests (strand, read position, mapping and base quality, local context) compared with 252 control heterozygous SNVs. Genotypes are stable across a 32-combination grid of mapping quality, base quality and duplicate handling. An independent re-call agrees, and flank mapping is unique. *measured.* No orthogonal assay was available, so a technical artefact is weakened, not excluded.
- **No coding loss-of-function in TRIP13, CEP57 or CENATAC.** Each MANE coding sequence (±10 bp) is at least 99% callable at depth ≥ 20, with no zero-depth base. Non-coding, regulatory and structural alleles remain open. *measured*
- **No run of homozygosity** at any of the four genes, and heterozygous calls in every gene body. *measured*
- **BUB1B second-allele search:** no copy-number-like depth change of about 1 kb or more, and no insertion-like or retrocopy pattern. Insertions, balanced events and the deep-intronic variant remain unresolved. *measured; unknown*
- **Robustness to evidence exclusion:** BUB1B stays first by completeness of mechanism under every exclusion rule tested. If indirect evidence is excluded, the BUB1B model rests only on the truncating allele plus the presence of the missense. *measured (sensitivity analysis)*

## K4: phase, missense mechanism and the CEP57 signal

- **Phase cannot be resolved from any existing data.** Reads, fragments, supplementary alignments, phase tags, barcodes, family data and reference panels were all checked; none carries phase information for the BUB1B variants. Statistical phasing was deliberately not run, because its inputs and assumptions are absent and it would give a misleading probability. *measured; unknown*
- **Design point:** the truncating and missense positions are close enough in the mRNA for a single cDNA molecule to span both, so RNA could phase them directly if it ever became available. *predicted*
- **Missense mechanism:** stability loss has the most indirect support; "no effect" cannot be excluded. The change sits in a confidently modelled, partly buried turn of the wild-type AlphaFold model. No mutant structure and no ΔΔG were computed. *indirect; computational (wild-type context only)*
- **CEP57 signal:** a two-sided clip pile-up from independent fragments with unique sequence (insertion-like), against a repetitive partner that also collects mates from unrelated loci, no poly-A and no unique junction (artefact-like). The pre-declared rule said artefact-leaning, but its only triggering criterion is confounded with real repeat insertions; that deviation is documented. Even if real, the signal is intronic and heterozygous, with no second CEP57 allele. *measured; unknown*
- **Ranking:** unchanged from K3.

## K5: drug-repurposing hypotheses

See `DRUG_HYPOTHESIS_ASSESSMENT.md`. In short: none of the 12 candidates has direct evidence of MVA-relevant benefit, and none qualifies as a stronger mechanistic hypothesis. Dasatinib and niacin are plausible but indirect research hypotheses. *database-observed (regulatory); indirect (literature); hypothesis (efficacy)*

## K6: functional variant assessment

- **No direct functional evidence exists for any of the participant's variants.** *unknown*
- **Missense neighbourhood in ClinVar:** of the missense records within ±10 residues, all but one are of uncertain significance and one is benign/likely benign; none is pathogenic. A published disease-reported missense nearby in the same domain is itself classified as uncertain significance in ClinVar. *database-observed*
- **Paralog:** the wild-type residue is identical in the paralog BUB1. This is a weak signal; no cross-species conservation data were available locally. *computational*
- **Calibration barrier:** ClinVar holds only one Likely pathogenic BUB1B missense variant, from a single submitter. The ClinGen functional-evidence recommendations (Brnich et al. 2019) require at least 11 pathogenic and benign controls in total for moderate evidence without rigorous statistics. Any assay of the missense change could therefore only be research-calibrated at present. *database-observed; framework*
- **Result:** no PS3 or BS3 functional-evidence code can be applied to any variant.

## What would change the conclusions

| Gap | What would close it | Feasible within the hackathon terms? |
|---|---|---|
| BUB1B phase | Parental genotypes, long reads spanning both variants, or single-molecule cDNA | No (new patient material) |
| Missense function | Isogenic knock-in abundance, turnover and checkpoint assays | Laboratory only; designs given |
| Deep-intronic variant effect | Minigene splicing assay; patient RNA | Minigene: laboratory only |
| CEP57 signal | Targeted PCR across the putative junction, or long reads | No (patient material) |
| Whether the cellular phenotype is MVA | Cytogenetics | Not available |
