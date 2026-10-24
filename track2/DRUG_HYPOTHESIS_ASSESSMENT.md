# Approved-drug hypothesis assessment, stage K5 (draft, 2026-10-24)

**Status:** research evidence assessment. **This is not a clinical recommendation.** No drug is shown to treat or correct MVA, and none is proposed for any patient.

## Bottom line

- **No candidate has direct evidence of MVA-relevant benefit.** *unknown (first-page literature searches; an absence of record, not evidence of absence)*
- **No candidate qualifies as a "stronger mechanistic research hypothesis".**
- **Two approved drugs survive as plausible but indirect research hypotheses:**
  - **dasatinib:** clearance of senescent cells, a downstream effect;
  - **niacin (nicotinic acid):** the NAD+/SIRT2/BUBR1-abundance axis, relevant only if residual BUBR1 protein exists.
- **The evidence does not support any drug-repurposing recommendation.**

## Where the chain from variant to drug breaks

```
variants ─► causal gene ─► molecular mechanism ─► cellular defect ─► drug target ─► phenotype
             UNRESOLVED     UNRESOLVED (missense)   gene level only     indirect      untested
```

Because the patient-specific mechanism is not established, any BUB1B-directed drug idea inherits that uncertainty. If the BUB1B variants turned out to be in cis, or the missense change benign, every BUB1B-directed idea would collapse. Only the gene-agnostic downstream senolysis idea would remain, and it is weak.

## Method

1. **Candidates:** the 12 inherited from the curated WP5/K2 review. None was dropped and none substituted.
2. **Regulatory status:** each drug's status was verified in openFDA and EMA sources. The official rule admits only currently approved drugs; a combination needs every component approved and supported.
3. **Causal chain:** each candidate was scored over five links (drug → target → cellular process → disease mechanism → phenotype), with supporting and contradicting evidence recorded.
4. **Categories:** assigned by a deterministic rule. The first rule that matches wins:

   | Order | Condition | Category |
   |---|---|---|
   | 1 | Not currently approved | out of scope |
   | 2 | Target relation opposing, **or** expected direction perturbing, **or** a major contradiction aligned with the disease in experimental data | contradicted or potentially counterproductive |
   | 3 | Direct or regulator target relation, **and** the drug itself tested in an MVA-gene model, **and** no major harm | stronger mechanistic research hypothesis |
   | 4 | Direct, regulator or downstream relation, **and** genetic or related-compound evidence in an MVA-gene model, **and** no major harm | plausible but indirect |
   | 5 | Target relation and support both unknown | insufficient evidence to rank |
   | 6 | Otherwise | weak/nonspecific |

The criteria values for all 12 candidates are below. Applying the rule to them reproduces every category in the result table; the team checked this with an internal unit test. The criteria themselves are curated judgements from abstract-level literature and regulatory records, so that check covers consistency, not the correctness of the judgements.

| Candidate | Drug | C0 approved | C1 target relation | C2 direction | C3 direct MVA evidence | C4 best experimental support | C5 contradiction or harm | C6 links supported / contradicted (of 5) | C7 test feasibility |
|---|---|---|---|---|---|---|---|---|---|
| WP5-H1 | dasatinib | yes | downstream | compensate | none | genetic-or-related-compound-in-MVA-gene-model | moderate | 3 / 0 | moderate |
| WP5-R1 | niacin (nicotinic acid) | yes | regulator | restore | none | genetic-or-related-compound-in-MVA-gene-model | moderate | 3 / 0 | high |
| K25-D1 | dactinomycin | yes | none | neutral | none | none | major-disease-aligned-label | 2 / 0 | low |
| WP5-H2 | gentamicin | yes | direct | restore | none | drug-in-other-disease | major-other | 2 / 1 | high |
| K25-D3 | somatropin | yes | none | neutral | none | none | major-disease-aligned-label | 2 / 1 | low |
| WP5-R5 | acetylcysteine (NAC) | yes | downstream | compensate | none | genetic-or-related-compound-in-MVA-gene-model | major-disease-aligned-experimental | 3 / 1 | moderate |
| K25-D2 | vincristine | yes | opposing | perturb | none | none | major-disease-aligned-experimental | 2 / 2 | low |
| WP5-R7 | microtubule poisons / Aurora / PLK1 inhibitors (class) | yes | opposing | perturb | none | none | major-disease-aligned-experimental | 2 / 3 | high |
| WP5-R6 | bortezomib | yes | regulator | perturb | none | none | major-other | 1 / 1 | moderate |
| WP5-R2 | NMN / nicotinamide riboside / nicotinamide | no | regulator | restore | none | genetic-or-related-compound-in-MVA-gene-model | minor | 3 / 0 | high |
| WP5-R4 | dasatinib + quercetin | no | downstream | compensate | none | genetic-or-related-compound-in-MVA-gene-model | moderate | 3 / 0 | moderate |
| WP5-R3 | ataluren | no | direct | restore | none | drug-in-other-disease | moderate | 1 / 2 | high |

## Result

| Category | Candidates | Main reason |
|---|---|---|
| Stronger mechanistic research hypothesis | none | No drug was tested in an MVA-gene model |
| **Plausible but indirect** | **dasatinib** | In BUBR1-insufficient progeroid mice, *genetic* removal of senescent cells delayed ageing-type phenotypes (Baker 2011). Dasatinib is a senolytic in some human cell types (Zhu 2015). There are no dasatinib data in any BUBR1 or MVA model. It does not address missegregation, microcephaly or cancer predisposition; senescence restrains tumour progression; the label carries paediatric growth warnings. |
| | **niacin** | In mice, NAD+ and SIRT2 maintain BubR1 abundance, and a related compound (NMN) raised it (North 2014). High-dose nicotinic acid raised blood NAD+ in humans (2026 study). Niacin itself was never tested on BUBR1. It needs residual BUBR1 protein and a BUB1B mechanism; the label carries muscle and liver warnings. |
| Weak/nonspecific | gentamicin | Read-through of a premature stop codon. But the truncating allele is predicted to undergo NMD; efficacy evidence is small and from cystic fibrosis; the label has boxed oto- and nephrotoxicity warnings. |
| | dactinomycin, somatropin | Approved in the disease context (tumour therapy; growth) but not MVA-directed. Somatropin carries neoplasm-risk warnings. |
| Contradicted or potentially counterproductive | acetylcysteine | Antioxidants accelerated tumour progression and metastasis in mice (Sayin 2014; 2026 study): a direct conflict with cancer predisposition |
| | bortezomib | No evidence of BUBR1 stabilisation; severe label toxicities |
| | vincristine; microtubule poisons, Aurora and PLK1 inhibitors | These increase chromosome missegregation, the wrong direction for MVA |
| Out of scope (not currently approved) | NMN / nicotinamide riboside / nicotinamide; ataluren; dasatinib + quercetin | Not approved medicines, or a combination with an unapproved component |

**Reclassification:** K5 moved niacin from "rejected" (in the earlier curated review) to "plausible but indirect", by applying the documented criteria. The change is recorded rather than hidden. It does not add any evidence of benefit.

### Regulatory status as checked (2026-10-24)

Sources: openFDA `drugsfda` and `label` records, and EMA EPAR pages or the EMA medicines-report snapshot of 2026-10-20. None of these drugs is approved for MVA. Any MVA use would be off-label, and **none is proposed**.

| Candidate | FDA | EMA (central) |
|---|---|---|
| dasatinib | Approved (NDA and ANDAs) | Sprycel authorised |
| niacin (nicotinic acid) | Approved (ANDAs) | Central products withdrawn |
| gentamicin | Approved (ANDAs) | Veterinary combinations only |
| dactinomycin | Approved | Not checked |
| somatropin | Approved (BLAs) | Omnitrope authorised |
| acetylcysteine | Approved (NDA and ANDAs) | No central product |
| bortezomib | Approved (NDA and ANDAs) | Velcade authorised |
| vincristine | Approved | Not checked |
| microtubule poisons / Aurora / PLK1 inhibitors | Paclitaxel and vincristine approved; alisertib, volasertib, barasertib and onvansertib have no FDA application | Not checked for the class |
| NMN / nicotinamide riboside / nicotinamide | No FDA application | No central product |
| ataluren | No FDA application | Translarna expired |
| dasatinib + quercetin | Dasatinib approved; quercetin has no FDA application | Quercetin has no product |

**Limits:** openFDA states its data are unvalidated. EU national authorisations and other jurisdictions were not checked, and an unchecked register is not treated as empty.

## How the open genetic questions change each surviving idea

| Scenario | Dasatinib | Niacin | Gentamicin |
|---|---|---|---|
| BUB1B causal; truncating allele in trans with a hypomorphic missense | Ageing-type features only | **Most relevant** (residual protein could be raised) | Only if transcripts escape NMD |
| BUB1B causal; missense is a functional null | As above | Little benefit expected | As above |
| Variants in cis, or missense benign | Only if MVA has another cause | Irrelevant | Irrelevant |
| TRIP13, CEP57 or CENATAC causal | Possibly (gene-agnostic), no evidence | Irrelevant | Irrelevant |

## Countereffects

- Cancer predisposition is part of MVA. Antioxidants and the loss of senescence can promote tumours.
- Microtubule poisons and spindle-kinase inhibitors increase missegregation.
- Paediatric label toxicities: dasatinib (growth and development), niacin (muscle and liver), gentamicin (boxed oto- and nephrotoxicity).

## Limits

- **Literature access:** all literature was read at abstract level.
- **Regulatory scope:** status was checked for the FDA (openFDA, whose data are unvalidated per its own disclaimer) and, where pages exist, the EMA. EU national authorisations were not checked.
- **Search depth:** searches read first result pages only.
