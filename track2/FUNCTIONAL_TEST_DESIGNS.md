# Proposed functional experiments (designs only; not performed)

**Status:** none of these experiments has been performed. They are designs. No result, effect size or functional-evidence strength is claimed. All designs use engineered cells or constructs; none uses patient material, which is outside the hackathon terms.

Why these tests matter: the two open questions are BUB1B phase and the function of the missense change. No test below can settle phase.

## Part 1: variant-function assays (stage K6)

| Order | Assay | Question | Main readouts | Key controls | Falsified or weakened if |
|---|---|---|---|---|---|
| 1 | **B1** Isogenic knock-in at the endogenous BUB1B locus in near-diploid human cells: missense/missense, missense/null, WT/null, WT/WT; at least 2 clones each | Does the missense change lower BUBR1 abundance through faster turnover? | Steady-state BUBR1 normalised to loading and to mitotic index; half-life by cycloheximide chase; proteasome-inhibitor rescue; BUB1B mRNA | **Normal:** WT/WT; a nearby ClinVar benign missense knocked in as a benign control. **Abnormal:** WT/null; a published disease-reported missense in the same domain, as a provisional reference (it is VUS in ClinVar); degron depletion as the null reference. | Missense genotypes match WT for abundance and half-life while the abnormal references separate |
| 1 | **C1** Same knock-in panel | Does the missense change impair checkpoint or attachment function? | Time in mitosis and slippage under nocodazole; lagging chromosomes, bridges and micronuclei per division; KARD phosphorylation and kinetochore PP2A-B56 | As B1, plus a pseudokinase-domain deletion (a function defect) and rescue by WT BUB1B | Missense/null behaves like WT/null, and missense/missense like WT/WT |
| 2 | **A1** Splicing-reporter minigene for the deep-intronic variant, in two cell lines | Does it create a pseudo-exon or cryptic splice site? | RT-PCR products, amplicon sequencing, percent spliced-in | WT construct; a canonical splice-site disruption as the positive control; endogenous splicing | No difference from WT while the positive control works. This weakens the hypothesis but **does not exclude** an effect in the native context. |
| 3 | **A3** Engineered NMD test of a stop of the same type as the truncating allele | Does the stop trigger NMD as predicted? | Allele-specific transcript level, with and without NMD inhibition | WT; an NMD-inhibitor arm | The stop allele's transcript is not reduced, or the reduction is not reversed by NMD inhibition |
| — | **D** TRIP13, CEP57, CENATAC, CEP57 signal | — | — | — | No variant-specific assay is justified until stated prerequisites are met (for example, the CEP57 signal being confirmed as real) |

**Validity limits (ClinGen PS3/BS3 framework, Brnich et al. 2019):**
- **Calibration:** ClinVar holds only one Likely pathogenic BUB1B missense control, against the framework's minimum of 11 pathogenic and benign controls in total for moderate evidence. These assays could therefore be research-calibrated only. **No PS3 or BS3 strength applies** to any variant, now or on the basis of these designs alone.
- **Replication:** at least 2 independent clones and at least 3 biological replicates are required; imaging readouts must be scored blind.
- **Overexpression:** overexpression designs risk masking instability, so endogenous knock-in is preferred.

## Part 2: drug-hypothesis tests (stage K5)

| Order | Test | Hypothesis | Model | Expected if correct | Falsified if |
|---|---|---|---|---|---|
| 1 | **D2 niacin** | Nicotinic acid raises NAD+, lowers BUBR1 K668 acetylation, raises BUBR1 protein and reduces segregation errors per division, in cells that keep some BUBR1 | BUBR1-hypomorphic cells; knock-in genotypes stop/WT, stop/hypomorphic-missense and stop/stop; NAPRT expression confirmed. **Controls:** SIRT2 overexpression (positive); SIRT2 inhibition or knockdown and K668 mutants (on-mechanism negatives); NAPRT-negative cells. | The whole chain appears and is **abolished by SIRT2 loss**; the effect needs residual protein | NAD+ rises without BUBR1, or BUBR1 rises without fewer errors, or the effect survives SIRT2 loss, or viability falls |
| 2 | **D1 dasatinib** | At senolytic concentrations, dasatinib lowers senescent burden in BUBR1-insufficient cultures without raising segregation errors in surviving dividing cells | BUBR1-insufficient RPE1 cells and BubR1-hypomorphic MEFs with isogenic WT controls; dose–response over at least 5 concentrations; intermittent versus continuous exposure | Senescent fraction falls; errors per division and transformation markers unchanged | No senescent-cell reduction at non-toxic concentrations, or more errors or transformation markers, or "benefit" explained by killing proliferating cells |
| 3 | **D3 gentamicin** | Read-through yields full-length BUBR1 from an engineered stop of the same type, limited by NMD | Isogenic engineered stop/WT and stop/– cells | Full-length BUBR1 above background, increasing with NMD inhibition | No full-length BUBR1 above background at non-toxic concentrations (pre-declared stop rule) |

**What a positive result would and would not establish:**
- **Would establish:** in-vitro feasibility only.
- **Would not establish:** tissue exposure, correction of the primary defect, benefit for any MVA feature, safety or dosing in any person, or relevance if the disease gene is not BUB1B.

Not designed: acetylcysteine, bortezomib, vincristine and the microtubule, Aurora and PLK1 inhibitor class (contradicted); dactinomycin and somatropin (not MVA-directed); agents that are not approved.
