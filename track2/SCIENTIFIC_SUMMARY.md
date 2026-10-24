# Scientific summary, stages K2–K6 (draft, 2026-10-24)

**Status:** research evidence assessment. Not a diagnosis, not a clinical variant classification, not treatment advice. No wet-lab experiment was performed. The underlying restricted records stay in approved private storage; this summary describes the participant's alleles by class only.

Labels: measured, database-observed, predicted, indirect, hypothesis, unknown (defined in `README.md`).

## Workflow

| Stage | Question | Main output |
|---|---|---|
| K2 | What do the literature and databases say about the four MVA genes, the candidate variants and the approved drugs? | Gene-level review, four-gene comparison, competing hypotheses, drug review, evidence ledger |
| K3 | Are the candidate calls technically real, and could the data hide a second allele? | Read-level robustness tests, coding callability, structural screens, sensitivity analysis |
| K4 | Can phase be resolved? What could the missense change do? What is the CEP57 signal? | Phase review, mechanism comparison, structural-signal assessment |
| K5 | Does any approved drug have evidence of MVA-relevant benefit? | Causal-chain assessment of 12 candidates, ranking rule, experiment designs |
| K6 | Is there functional evidence for any variant, and which experiments would be informative? | Functional-evidence categories, assay-validity review, minimal experimental programme |

Each stage reused the previous stages' outputs after checking their checksums. A separate audit of K2 led to corrections before K3 (see `METHODS.md`, "Integrity controls").

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
| BUB1B-V | Deep-intronic variant | ClinVar: uncertain significance, single submitter; absent from gnomAD genomes; no splice prediction or RNA | database-observed; unknown |
| CENATAC-P | Variant that is a missense change only on a non-MANE transcript | Deep intronic on the MANE transcript; the alternative isoform has weak annotation support. The call is supported, but it has artefact-associated features (strand bias; next to a homopolymer), so its technical confidence is moderate. | measured; unknown (isoform relevance) |
| CEP57 signal | Intronic read-level cluster suggestive of an insertion or rearrangement | Unresolved | unknown |

## Three separate questions for the candidate pair

Whether a call is real, whether the variant changes function, and whether it causes disease are different questions. Evidence for one does not answer the others.

| Variant | Is the call real? | Does it change function? | Does it cause disease in this case? |
|---|---|---|---|
| BUB1B-T | High technical confidence (measured) | Loss of function expected (NMD prediction; class-level evidence; exact-allele ClinVar assertion) but **not directly demonstrated** | **Not established.** Consistent with a known recessive disease allele, but it needs a second damaging allele in trans. |
| BUB1B-P | High technical confidence (measured) | **Unresolved.** No direct evidence; the support is indirect or computational only | **Not established.** It cannot serve as the second allele without functional evidence and trans phase. |

## K2: literature, mechanism and competing genes

### Four-gene comparison

No numeric score is used, because no scoring model with known performance exists for this question. The order reflects only **how much of the required genetic mechanism is present in the data**, not the probability of causation. Rows combine K2 with the K3 read-level results.

| Criterion | BUB1B | TRIP13 | CEP57 | CENATAC |
|---|---|---|---|---|
| Gene–disease validity (GenCC) *database-observed* | Definitive, autosomal recessive (MVA1) | Strong to Limited, autosomal recessive (MVA3). Missense alleles are also linked to oocyte maturation arrest. | Definitive, autosomal recessive (MVA2) | Limited, autosomal recessive (MVA4); one submitter, one report |
| Gene-level mechanism *indirect* | BUBR1 dosage: null alleles plus abundance- or function-lowering missense; non-coding second alleles are reported | MAD2 remodelling; biallelic loss of function | Centrosome and pericentriolar material; checkpoint largely intact | Minor-spliceosome (AT-AN) intron retention |
| Loss-of-function-class allele in the data *measured* | Yes: a known truncating allele | None found | None found | None found |
| Candidate second variant *measured* | A rare missense change (unclassified); a deep-intronic variant of uncertain significance | None | None. One intronic structural signal is unresolved. | None. The variant is a missense change only on a non-MANE isoform. |
| Coding sequence coverage *measured* | — | ≥ 99% callable at depth ≥ 20 | ≥ 99% callable at depth ≥ 20 | ≥ 99% callable at depth ≥ 20 |
| Structural screen *measured* | Partly assessed; insertions and balanced events not excluded | Depth signal technically uninterpretable | One unresolved intronic signal | Nothing in the gene body |
| Order | First, by completeness of mechanism only | Not rankable against CEP57 or CENATAC | Not rankable | Not rankable |

The BUB1B explanation is **conditional** on two things, neither established: the missense change (or the deep-intronic variant) must be damaging, **and** it must be in trans with the truncating allele. If the variants are in cis, or the missense change is neutral, BUB1B reduces to one null allele, which does not explain a recessive disorder.

### Other K2 findings

- **Contradictions recorded:** *indirect*
  - inheritance (an Orphanet "supportive AD" entry against the autosomal recessive consensus);
  - BUBR1 pseudokinase activity (catalytic versus structural role);
  - TRIP13 allelic heterogeneity;
  - two case reports that are a probable duplicate (shared authors, same presentation), counted as one case.
- **Approved therapies:** none directed at the gene defect for any of the four genes; no US label lists MVA. *database-observed*

### Competing explanations and their current status

Statuses as updated through K3 and K4. A missing literature report is never counted as evidence against a hypothesis.

| Explanation | Status | Main reason |
|---|---|---|
| BUB1B biallelic: the truncating allele in trans with a hypomorphic missense change | UNRESOLVED | Phase and missense function unknown |
| The two BUB1B variants are in cis (one null allele only) | UNRESOLVED | Phase unknown |
| The truncating allele plus an undetected second BUB1B allele (deep-intronic, insertion, regulatory or balanced event) | UNRESOLVED | Large deletions weakened; insertions, balanced events and the deep-intronic variant not addressed |
| The missense change is functionally neutral | UNRESOLVED | No functional data |
| One truncating BUB1B allele is enough (dominant or haploinsufficient) | WEAKENED | Definitive recessive validity; carriers are reportedly unaffected; published apparently monoallelic cases were explained by hidden second alleles |
| A candidate call is a technical artefact | WEAKENED | All pre-declared read-level tests pass; no orthogonal assay |
| Biallelic loss of function in TRIP13, CEP57 or CENATAC | WEAKENED | No coding loss-of-function in callable coding sequence; no run of homozygosity |
| The CENATAC variant changes the canonical protein | REJECTED | Deep intronic on the MANE transcript |
| A run of homozygosity, uniparental disomy or a whole-gene deletion unmasks a recessive allele | WEAKENED | No run of homozygosity; heterozygous calls in every gene body |
| Another MVA gene is responsible | NOT ASSESSED | Out of the analysed gene set |
| The phenotype is blended or not MVA; some features are not explained by these genes | UNRESOLVED | No cytogenetics; non-MVA causes out of scope |

## K3: read-level re-analysis

- **The three BUB1B calls are technically real in this sample.** Each passes ten pre-declared read-level tests (strand, read position, mapping and base quality, local context) compared with 252 control heterozygous SNVs. Genotypes are stable across a 32-combination grid of mapping quality, base quality and duplicate handling. An independent re-call agrees, and flank mapping is unique. *measured.* No orthogonal assay was available, so a technical artefact is weakened, not excluded.
- **No coding loss-of-function in TRIP13, CEP57 or CENATAC.** Each MANE coding sequence (±10 bp) is at least 99% callable at depth ≥ 20, with no zero-depth base. Non-coding, regulatory and structural alleles remain open. *measured*
- **No run of homozygosity** at any of the four genes, and heterozygous calls in every gene body. *measured*
- **BUB1B second-allele search:** no copy-number-like depth change of about 1 kb or more, and no insertion-like or retrocopy pattern. Insertions, balanced events and the deep-intronic variant remain unresolved. *measured; unknown*
- **Structural screens of the other genes:** *measured*
  - TRIP13: the depth signal is technically uninterpretable (subtelomeric noise);
  - CEP57: one new intronic signal (see K4);
  - CENATAC: nothing in the gene body.
- **Population data:** the absence of homozygotes for the truncating allele in gnomAD is **uninformative**: at its frequency, Hardy–Weinberg expects far fewer than one. Population frequency for the TRIP13, CEP57 and CENATAC records was not looked up. *database-observed; computed*
- **Robustness to evidence exclusion:** each hypothesis was re-evaluated after removing:
  - S1: abstract-only literature;
  - S2: single-submitter assertions;
  - S3: indirect evidence (gene-level, model or other-allele);
  - S4: all three together.

  BUB1B stays first by completeness of mechanism under every rule, and no hypothesis changes status. One basis changes: every item supporting a damaging missense change is indirect. With indirect evidence excluded, the BUB1B model rests only on the truncating allele plus the mere presence of the missense change. *measured (sensitivity analysis)*
- **Findings that depend on filter choices:**
  - the technical robustness of the CENATAC call (strand-bias and homopolymer rules);
  - TRIP13 depth runs (window threshold; subtelomeric GC content and mappability);
  - the classification of weak discordant-read clusters (which read subset is used);
  - the matching of some indel and low-depth records in TRIP13 and CENATAC.

  None of these affects the BUB1B findings or the gene order.

## K4: phase, missense mechanism and the CEP57 signal

- **Phase cannot be resolved from any existing data.** Reads, fragments, supplementary alignments, phase tags, barcodes, family data and reference panels were all checked; none carries phase information for the BUB1B variants. Statistical phasing was deliberately not run, because its inputs and assumptions are absent and it would give a misleading probability. *measured; unknown*
- **Design point:** the truncating and missense positions are close enough in the mRNA for a single cDNA molecule to span both, so RNA could phase them directly if it ever became available. *predicted*
- **Missense mechanism:** the change sits in a confidently modelled, partly buried turn of the wild-type AlphaFold model. No mutant structure and no ΔΔG were computed. Seven candidate mechanisms were compared. **No mechanism is asserted.** *indirect; computational (wild-type context only)*

  | ID | Mechanism | Evidence status | Test that would separate it |
  |---|---|---|---|
  | M0 | No material functional effect | Not excluded: there is no direct damaging evidence | Wild-type-like abundance and function (B1, C1) |
  | M1 | Reduced stability or faster turnover | The most indirect support: kinase-domain MVA missense alleles turn over fast (class level); the domain's conformational stability is sensitive; partly buried position in the wild-type model | B1; optionally purified-domain stability |
  | M2 | Altered regulation by phosphorylation | Speculative | Second line: phosphorylation assay |
  | M3 | Impaired pseudokinase-domain function (KARD phosphorylation, PP2A-B56 recruitment) at normal abundance | Speculative: the domain is needed for this function, but the residue's role is unknown | C1 |
  | M4 | Altered catalytic or ATP-related activity | Weakly contradicted: catalysis is dispensable in human BUBR1 | Not prioritised |
  | M5 | Altered splicing through a new exonic motif | Speculative: outside the splice region; no predictor; no RNA | Second line: exon minigene (A2) |
  | M6 | An effect only in trans with a null allele, or only in some tissues | Hypothesis (recessive dosage model) | Missense/null against missense/WT genotypes in B1 and C1 |

- **CEP57 signal:** a two-sided clip pile-up from independent fragments with unique sequence (insertion-like), against a repetitive partner that also collects mates from unrelated loci, no poly-A and no unique junction (artefact-like). The pre-declared rule said artefact-leaning, but its only triggering criterion is confounded with real repeat insertions; that deviation is documented. Even if real, the signal is intronic and heterozygous, with no second CEP57 allele. *measured; unknown*
- **Ranking:** unchanged from K3.

## K5: drug-repurposing hypotheses

See `DRUG_HYPOTHESIS_ASSESSMENT.md`. In short: none of the 12 candidates has direct evidence of MVA-relevant benefit, and none qualifies as a stronger mechanistic hypothesis. Dasatinib and niacin are plausible but indirect research hypotheses. *database-observed (regulatory); indirect (literature); hypothesis (efficacy)*

## K6: functional variant assessment

- **No direct functional evidence exists for any of the participant's variants.** *unknown*
- **Missense neighbourhood in ClinVar:** of the missense records in a small window around the change, all but one are of uncertain significance and one is benign/likely benign; none is pathogenic. A published disease-reported missense nearby in the same domain is itself classified as uncertain significance in ClinVar. *database-observed*
- **Gene-wide missense controls in ClinVar:** 1 Likely pathogenic (single submitter) and 35 benign/likely benign BUB1B missense variants. *database-observed*
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
| Low-level mosaicism; parental origin of each allele | Other tissues; parental samples | No (new patient material) |
| Population frequency of the TRIP13, CEP57 and CENATAC records | Approved regional gnomAD reads | Yes, with owner approval; not done |
