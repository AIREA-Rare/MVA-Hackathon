"""K4-C: wild-type structural and annotation context of the P residue (no mutant model, no stability prediction).
Uses the valid AlphaFold v6 files (retry_* names; the non-retry files are logged 403 pages) and the local UniProt entry
(2026-10-20 download, entry version 234). Computes: pLDDT; secondary structure from the model's own _struct_conf
annotation; CA-CA and minimum heavy-atom distances and PAE to every UniProt-annotated site/variant/mutagenesis residue in
the kinase-domain annotation; charged residues near the side chain. These are WT-context descriptors only: they do not
show that the substitution is damaging. Results private; prints categories only.
usage: python3 -B -I k4_missense_context.py"""
import json
import math
import os
import re
from collections import Counter

P = os.environ["MVA_DATA_ROOT"]
K4 = f"{P}/out/T2K4_mechanistic_2026-10-24"
S = f"{P}/ref/structures_O60566_2026-10-23"
T = 1002
os.umask(0o077)
atoms = {}
for ln in open(f"{S}/retry_AF-O60566-F1-model_v6.pdb"):
    if ln.startswith("ATOM"):
        r = int(ln[22:26]); atoms.setdefault(r, {"name": ln[17:20], "plddt": float(ln[60:66]), "atoms": []})
        atoms[r]["atoms"].append((ln[12:16].strip(), float(ln[30:38]), float(ln[38:46]), float(ln[46:54]), ln[76:78].strip()))
cif = open(f"{S}/retry_AF-O60566-F1-model_v6.cif").read()
ss = []
m = re.search(r"loop_\s*\n((?:_struct_conf\.\S+\s*\n)+)(.*?)\n(?:#|loop_)", cif, re.S)
if m:
    cols = [c.strip().split(".")[1] for c in m.group(1).strip().splitlines()]
    for ln in m.group(2).strip().splitlines():
        v = ln.split()
        if len(v) == len(cols):
            d = dict(zip(cols, v))
            ss.append((d.get("conf_type_id"), int(d["beg_label_seq_id"]), int(d["end_label_seq_id"])))
ss_here = [t for t, b, e in ss if b <= T <= e]
pae = json.load(open(f"{S}/retry_AF-O60566-F1-predicted_aligned_error_v6.json"))
pae = pae[0] if isinstance(pae, list) else pae
M = pae.get("predicted_aligned_error")


def ca(r):
    return next(((x, y, z) for n, x, y, z, _ in atoms[r]["atoms"] if n == "CA"), None)


def mind(a, b):
    return min(math.dist(p[1:4], q[1:4]) for p in atoms[a]["atoms"] for q in atoms[b]["atoms"] if p[4] != "H" and q[4] != "H")


up = json.load(open(f"{P}/ref/uniprot_entry_O60566_2026-10-20/O60566.json"))
dom = next(f for f in up["features"] if f["type"] == "Domain" and "kinase" in (f.get("description") or "").lower())
ds, de = dom["location"]["start"]["value"], dom["location"]["end"]["value"]
feats = []
for f in up["features"]:
    s, e = f["location"]["start"]["value"], f["location"]["end"]["value"]
    if f["type"] in ("Active site", "Binding site", "Modified residue", "Natural variant", "Mutagenesis", "Site") and ds <= s <= de and s == e and s in atoms:
        feats.append({"type": f["type"], "offset": s - T, "desc": (f.get("description") or "")[:80], "ca_ca": round(math.dist(ca(s), ca(T)), 1),
                      "min_heavy": round(mind(s, T), 1), "pae_T_to_s": M[T - 1][s - 1] if M else None, "pmids": [e.get("id") for e in f.get("evidences", []) if e.get("source") == "PubMed"],
                      "change": (f.get("alternativeSequence") or {}).get("alternativeSequences")})
# side-chain environment
sc = [a for a in atoms[T]["atoms"] if a[0] not in ("N", "CA", "C", "O")]
near = Counter()
for r, d in atoms.items():
    if r == T:
        continue
    for a in d["atoms"]:
        if any(math.dist(a[1:4], b[1:4]) <= 6.0 for b in sc):
            if d["name"] in ("LYS", "ARG") and a[0] in ("NZ", "NH1", "NH2", "NE"):
                near["positive_sidechain_N_within_6A"] += 1
            if d["name"] in ("ASP", "GLU") and a[0] in ("OD1", "OD2", "OE1", "OE2"):
                near["negative_sidechain_O_within_6A"] += 1
res = {"model": "AF-O60566-F1 v6 (retry_ files)", "residue_name": atoms[T]["name"], "plddt": atoms[T]["plddt"], "secondary_structure": ss_here or ["coil/none annotated"],
       "kinase_domain_annotation": [ds, de], "annotated_features_in_domain": sorted(feats, key=lambda x: x["min_heavy"]), "charged_environment": dict(near),
       "uniprot_entry_version": up.get("entryAudit", {}).get("entryVersion")}
json.dump(res, open(f"{K4}/private_runs/C_missense_context.json", "w"), indent=1)
os.chmod(f"{K4}/private_runs/C_missense_context.json", 0o600)
print("residue identity matches Asn:", atoms[T]["name"] == "ASN", "| pLDDT >= 90:", atoms[T]["plddt"] >= 90, "| secondary structure:", res["secondary_structure"])
print("annotated single-residue features in kinase-domain annotation:", len(feats))
for f in res["annotated_features_in_domain"][:8]:
    print(f"  {f['type']:16s} | offset {'+' if f['offset'] > 0 else ''}{f['offset']} | min heavy-atom distance {'<=6 A' if f['min_heavy'] <= 6 else ('6-12 A' if f['min_heavy'] <= 12 else '>12 A')} | PAE {'<=5' if (f['pae_T_to_s'] or 99) <= 5 else '>5'} | {f['desc'][:60]}")
print("charged side-chain atoms within 6 A of the side chain:", dict(near))
