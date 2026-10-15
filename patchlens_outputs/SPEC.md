# PatchLens output record specification (v0.1.0, proposed)

One JSON file per record, in `patchlens_outputs/records/`. Machine-readable form: [`patchlens_output.schema.json`](patchlens_output.schema.json). `scripts/validate_patchlens_outputs.py` enforces it.

A record is the **result** of a PatchLens run. It names the backend version and carries parameter and structure hashes so a result can be matched to a run privately, but it never contains the code, parameters, structure coordinates or model files behind that result.

## Fields

| Field | Type | Rule |
|---|---|---|
| `schema_version` | string | `"0.1.0"` |
| `record_id` | string | Unique across the repository |
| `passport_id` | string | Links to a causal passport (`schemas/causal_passport.schema.json`) |
| `data_class` | enum | `synthetic` or `permitted_summary`. `restricted` is never allowed in this repository |
| `backend` | object | `name`, `version`, `parameter_hash` (sha256 or `null`) |
| `input` | object | Mapped variant context: `gene`, `transcript`, `protein_accession`, `residue_ref`, `residue_position`, `residue_alt`, `structure_source`, `structure_chain`, `structure_sha256`. Each may be `null` when unknown |
| `applicability` | object | `status` is `available`, `not_assessed` or `abstain`; `reason` is a string or `null`; `reason` is required unless `status` is `available` |
| `metrics` | object | Name to number or `null`. Every value must be `null` unless `status` is `available` |
| `uncertainty_notes` | array of strings | Confidence and uncertainty in plain language |
| `boundaries` | array of strings | At least one statement of what the record does not show |
| `evidence_tier` | const | `"E4"` |
| `call` | const | `null`. Never a pathogenicity or treatment verdict |
| `artifact_sha256` | string or null | Hash of the exported artifact |
| `acceptance_record` | string or null | Reference to the private acceptance decision for this backend |
| `provenance` | object | `structure_license` and `attribution` (strings or `null`). AlphaFold DB structures are CC-BY-4.0 and need attribution |

## Semantics

- Unavailable backend, or unsupported mapping, variant or mechanism: `status` is `not_assessed` or `abstain`, with a reason, and all metrics are `null`.
- No unavailable value is written as `0`.
- Splice, regulatory, CNV/SV, absent-protein and unmapped cases are out of applicability for a missense structural backend and must abstain.
- Mutation-specific structural changes can guide an experiment. They do not establish destabilization, pathogenicity, clinical severity or drug response.
- A performance figure belongs in a note, not in a record, and is written with its dataset, n and comparator. A bare number is a defect.
