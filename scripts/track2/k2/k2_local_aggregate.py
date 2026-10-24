"""K2: read-only aggregation of local private evidence for BUB1B, TRIP13, CEP57, CENATAC (counts and categories only;
no coordinates, genotypes or identifiers printed). Writes LOCAL_EVIDENCE_AGGREGATE.json into the output folder.
usage: python3 -B -I k2_local_aggregate.py <out_dir>"""
import collections
import csv
import glob
import json
import os
import sys

OUT = sys.argv[1]
H = os.path.join(os.environ["MVA_DATA_ROOT"], "out")
GENES = ("BUB1B", "TRIP13", "CEP57", "CENATAC")
res = {}
# M1 records + routes
m1 = f"{H}/M1_mva_genes_v0.1.0_2026-10-19/m1_gene_records.tsv"
rows = list(csv.DictReader(open(m1, encoding="utf-8"), delimiter="\t"))
res["m1_columns"] = list(rows[0].keys())
g = collections.defaultdict(collections.Counter)
for r in rows:
    for gene in (r.get("m1_genes") or "").replace(",", ";").split(";"):
        if gene not in GENES:
            continue
        for k in ("consequence_class_primary", "zygosity", "filter", "m1_pool", "annotation_status"):
            g[gene][f"{k}={r.get(k)}"] += 1
        g[gene]["records"] += 1
res["m1_by_gene"] = {k: dict(v) for k, v in g.items()}
# route outputs (phase_routes)
routes = sorted(glob.glob(f"{H}/**/routes*.tsv", recursive=True)) + sorted(glob.glob(f"{H}/**/*route*.tsv", recursive=True))
res["route_files_found"] = sorted(set(p.replace(H + "/", "") for p in routes))[:10]
# ClinVar panel per gene (no IDs printed)
cv = f"{H}/T2F_clinvar_panel_2026-10-22/proband_panel_clinvar.tsv"
crow = [l.rstrip("\n").split("\t") for l in open(cv, encoding="utf-8") if l.strip()]
res["clinvar_panel_note"] = "headerless TSV; columns assumed CHROM POS REF ALT FILTER GT VariationID CLNSIG GENEINFO (9 columns)"
res["clinvar_panel_ncols"] = sorted({len(r) for r in crow})
cg = collections.defaultdict(collections.Counter)
for r in crow:
    genes = {x.split(":")[0] for x in r[-1].split("|")} if r else set()
    for gene in genes & set(GENES):
        cg[gene][f"CLNSIG={r[7] if len(r) > 7 else '?'}"] += 1
res["clinvar_panel_by_gene"] = {k: dict(v) for k, v in cg.items()}
# evidence cards summary
s = json.load(open(f"{H}/WP2_WP3_evidence_cards_v0.2.0_2026-10-20/summary.json", encoding="utf-8"))
res["evidence_cards_summary_keys"] = list(s.keys())
res["evidence_cards_summary_small"] = {k: v for k, v in s.items() if not isinstance(v, (dict, list)) or k in ("by_route", "by_gene", "labels", "label_counts")}
json.dump(res, open(f"{OUT}/LOCAL_EVIDENCE_AGGREGATE.json", "w"), indent=1)
print(json.dumps(res, indent=1)[:6000])
