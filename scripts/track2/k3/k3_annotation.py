"""K3 Workstream A/B: independent transcript re-derivation for the candidates (GFF3 Ensembl 116 + reference FASTA).
For each candidate and transcript: CDS/UTR/intron location, distance to the nearest exon boundary, splice-region class
(exonic within 3 bp or intronic within 8 bp of a boundary; canonical +/-1-2), codon and amino-acid change, and a simple
splice-dinucleotide motif observation (does the alternate allele create a new GT or AG at the site). The motif check is a
sequence observation, NOT a splice prediction. Results private; prints consistency categories only.
usage: python3 -B -I k3_annotation.py"""
import gzip
import json
import os
import re
import subprocess

P = os.environ["MVA_DATA_ROOT"]
K = f"{P}/out/T2K3_research_2026-10-23"
FA = f"{P}/ref/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.nochr.fna"
GFF = f"{P}/ref/Homo_sapiens.GRCh38.116.chr.gff3.gz"
TX = {"BUB1B": ["ENST00000287598"], "CENATAC": ["ENST00000334418", "ENST00000891520"]}
CODE = {}
bases = "TCAG"
aas = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
i = 0
for a in bases:
    for b in bases:
        for c in bases:
            CODE[a + b + c] = aas[i]; i += 1
COMP = str.maketrans("ACGT", "TGCA")
os.umask(0o077)

cands = []
for ln in open(f"{P}/work/T2F_bub1b_locus_2026-10-22/check_positions.tsv"):
    f = ln.rstrip("\n").split("\t")
    if len(f) == 4 and f[0].startswith("BUB1B_"):
        cands.append(("15", int(f[1]), f[2], f[3], f[0], "BUB1B"))
cards = open(f"{P}/out/WP2_WP3_evidence_cards_v0.2.0_2026-10-20/VARIANT_EVIDENCE_CARDS.md").read()
for m in re.finditer(r"## (\w+) — route (\w) — (\w+):(\d+):([ACGT]+):([ACGT]+)", cards):
    if m.group(1) == "CENATAC":
        cands.append((m.group(3), int(m.group(4)), m.group(5), m.group(6), f"CENATAC_{m.group(2)}", "CENATAC"))
want = {t for v in TX.values() for t in v}
feat = {t: {"exon": [], "CDS": [], "strand": None, "chrom": None, "attr": ""} for t in want}
with gzip.open(GFF, "rt") as fh:
    for ln in fh:
        if ln.startswith("#"):
            continue
        c = ln.rstrip("\n").split("\t")
        if len(c) < 9:
            continue
        for t in want:
            if c[8].startswith(f"ID=transcript:{t};"):
                feat[t]["strand"], feat[t]["chrom"], feat[t]["attr"] = c[6], c[0], c[8][:400]
            elif f"Parent=transcript:{t};" in c[8] and c[2] in ("exon", "CDS"):
                feat[t][c[2]].append((int(c[3]), int(c[4]), int(c[7]) if c[7].isdigit() else 0))


def fetch(ch, s, e):
    return "".join(subprocess.run(["samtools", "faidx", FA, f"{ch}:{s}-{e}"], capture_output=True, text=True).stdout.splitlines()[1:]).upper()


out = {}
for ch, pos, ref, alt, lab, gene in cands:
    out[lab] = {}
    for t in TX[gene]:
        F = feat[t]
        ex = sorted(F["exon"]); cds = sorted(F["CDS"]); strand = F["strand"]
        r = {"strand": strand, "tags": re.findall(r"tag=[^;]*", F["attr"]), "n_exons": len(ex)}
        inexon = [e for e in ex if e[0] <= pos <= e[1]]
        bnds = sorted({b for e in ex for b in (e[0], e[1])})
        r["location"] = "exon" if inexon else ("intron" if ex and ex[0][0] < pos < ex[-1][1] else "outside transcript")
        # distance to nearest exon boundary and the boundary type
        dist = min((abs(pos - b), b) for b in bnds) if bnds else (None, None)
        r["nearest_exon_boundary_distance_bp"] = dist[0]
        if r["location"] == "intron":
            r["splice_region"] = "canonical (+/-1-2)" if dist[0] <= 2 else ("splice region (<=8 bp intronic)" if dist[0] <= 8 else "deep intronic (>8 bp)")
        elif r["location"] == "exon":
            r["splice_region"] = "splice region (<=3 bp exonic)" if dist[0] < 3 else "exonic, outside splice region"
        r["in_CDS"] = any(c0 <= pos <= c1 for c0, c1, _ in cds)
        if r["in_CDS"]:
            segs = cds if strand == "+" else sorted(cds, key=lambda x: -x[0])
            seq, off = "", None
            for c0, c1, _ in segs:
                s = fetch(ch, c0, c1)
                if strand == "-":
                    s = s.translate(COMP)[::-1]
                if c0 <= pos <= c1:
                    off = len(seq) + (pos - c0 if strand == "+" else c1 - pos)
                seq += s
            phase0 = segs[0][2]
            seq = seq[phase0:]; off -= phase0
            cod_i = off // 3
            codon = seq[3 * cod_i:3 * cod_i + 3]
            a = alt if strand == "+" else alt.translate(COMP)
            mut = codon[:off % 3] + a + codon[off % 3 + 1:]
            r.update({"cds_pos": off + 1, "codon_number": cod_i + 1, "ref_codon": codon, "alt_codon": mut,
                      "ref_aa": CODE.get(codon), "alt_aa": CODE.get(mut), "cds_length_nt": len(seq),
                      "protein_length_aa": len(seq) // 3 - 1,
                      "last_exon_junction_distance_nt": None})
            # NMD 50-nt rule: position of stop vs last exon-exon junction (CDS coordinates)
            ex_t = ex if strand == "+" else sorted(ex, key=lambda x: -x[0])
            if len(ex_t) > 1:
                # transcript coordinate of the last junction and of the variant
                tpos, tcoord, last_junc = 0, None, None
                for k, (e0, e1, _) in enumerate(ex_t):
                    if e0 <= pos <= e1:
                        tcoord = tpos + (pos - e0 if strand == "+" else e1 - pos)
                    tpos += e1 - e0 + 1
                    if k == len(ex_t) - 2:
                        last_junc = tpos
                r["distance_upstream_of_last_junction_nt"] = None if tcoord is None else last_junc - tcoord
        ctx = fetch(ch, pos - 1, pos + 1)
        ac = ctx[0] + alt + ctx[2]
        rc = ctx
        if strand == "-":
            rc = rc.translate(COMP)[::-1]; ac = ac.translate(COMP)[::-1]
        r["motif_new_GT"] = ("GT" in ac) and ("GT" not in rc)
        r["motif_new_AG"] = ("AG" in ac) and ("AG" not in rc)
        out[lab][t] = r
with open(f"{K}/private_runs/A_annotation.json", "w") as fh:
    json.dump(out, fh, indent=1)
os.chmod(f"{K}/private_runs/A_annotation.json", 0o600)
for lab, d in out.items():
    for t, r in d.items():
        print(lab, t, r["location"], r.get("splice_region"), "CDS" if r["in_CDS"] else "nonCDS",
              (f"aa {r['ref_aa']}>{r['alt_aa']}" if r["in_CDS"] else ""), f"newGT={r['motif_new_GT']} newAG={r['motif_new_AG']}",
              ("NMD50:" + ("upstream>50" if (r.get("distance_upstream_of_last_junction_nt") or 0) > 50 else "<=50/none")) if r["in_CDS"] and r["alt_aa"] == "*" else "")
