"""K3 Workstream B: local alignment ambiguity. For each candidate, the reference and alternate-allele sequences of
+-50 bp and +-100 bp around the site are aligned to the full GRCh38 analysis set with bwa mem -a (all alignments).
Unique placement = primary MAPQ >= 30 and no secondary alignment with alignment score within 10 of the primary.
Sequences are written only to a private temporary FASTA that is deleted afterwards. Prints categories only.
usage: python3 -B -I k3_mappability.py"""
import json
import os
import re
import subprocess

P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
FA = f"{P}/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
IDX = f"{P}/work/bwa_index_GRCh38_noalt_hs38d1_2026-10-20/GRCh38_noalt_hs38d1.nochr"
os.umask(0o077)
cands = []
for ln in open(f"{P}/work/T2F_bub1b_locus_2026-10-22/check_positions.tsv"):
    f = ln.rstrip("\n").split("\t")
    if len(f) == 4 and f[0].startswith("BUB1B_"):
        cands.append(("15", int(f[1]), f[2], f[3], f[0]))
cards = open(f"{P}/out/WP2_WP3_evidence_cards_v0.2.0_2026-10-20/VARIANT_EVIDENCE_CARDS.md").read()
for m in re.finditer(r"## (\w+) — route (\w) — (\w+):(\d+):([ACGT]+):([ACGT]+)", cards):
    if m.group(1) == "CENATAC":
        cands.append((m.group(3), int(m.group(4)), m.group(5), m.group(6), "CENATAC_P"))
tmp = f"{K}/private_runs/_flanks.tmp.fa"
with open(tmp, "w") as fh:
    for ch, pos, ref, alt, lab in cands:
        for w in (50, 100):
            s = "".join(subprocess.run(["samtools", "faidx", FA, f"{ch}:{pos - w}-{pos + w}"], capture_output=True, text=True).stdout.splitlines()[1:]).upper()
            fh.write(f">{lab}|{w}|ref\n{s}\n>{lab}|{w}|alt\n{s[:w] + alt + s[w + 1:]}\n")
sam = subprocess.run(["bwa", "mem", "-a", "-t", "4", "-v", "1", IDX, tmp], capture_output=True, text=True).stdout
os.remove(tmp)
res = {}
for ln in sam.splitlines():
    if ln.startswith("@"):
        continue
    f = ln.split("\t")
    flag = int(f[1])
    q = f[0]
    a = res.setdefault(q, {"primary_mapq": None, "primary_AS": None, "primary_on_target": None, "secondary_AS": []})
    asv = next((int(t[5:]) for t in f[11:] if t.startswith("AS:i:")), None)
    if flag & 0x900 == 0:
        lab = q.split("|")[0]
        ch, pos = next((c[0], c[1]) for c in cands if c[4] == lab)
        a.update({"primary_mapq": int(f[4]), "primary_AS": asv, "primary_on_target": f[2] == ch and abs(int(f[3]) - pos) < 200})
    elif flag & 0x100:
        a["secondary_AS"].append(asv)
for q, a in res.items():
    near = [s for s in a["secondary_AS"] if s is not None and a["primary_AS"] is not None and s >= a["primary_AS"] - 10]
    a["unique"] = bool(a["primary_on_target"]) and (a["primary_mapq"] or 0) >= 30 and not near
    a["n_secondary_within_10"] = len(near)
json.dump(res, open(f"{K}/private_runs/B_mappability.json", "w"), indent=1)
os.chmod(f"{K}/private_runs/B_mappability.json", 0o600)
for q in sorted(res):
    a = res[q]
    print(q, "| primary on target:", a["primary_on_target"], "| MAPQ>=30:", (a["primary_mapq"] or 0) >= 30, "| near-equal secondary hits:", a["n_secondary_within_10"], "| UNIQUE:", a["unique"])
