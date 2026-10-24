"""K3 Workstream C/A: Europe PMC precedent searches with generic public terms only (gene symbols, method and disease
words). Raw responses are not stored; per query: URL, HTTP status, SHA-256 of the response, hit count and the top records
(title, journal, year, PMID, DOI). With --abstracts PMID..., fetches those abstracts and stores them (public text) for
citation checks. Writes private_runs/C_lit_*.json; prints titles/PMIDs (public literature metadata only).
usage: python3 -B -I k3_lit.py search | python3 -B -I k3_lit.py abstracts <PMID> [<PMID> ...]"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

K = os.path.join(os.environ["MVA_DATA_ROOT"], "out/T2K3_research_2026-10-23")
os.umask(0o077)
Q = {
 "L01": 'BUB1B AND "mosaic variegated aneuploidy" AND (stability OR turnover OR degradation OR abundance)',
 "L02": '(BUBR1 OR BUB1B) AND ("spindle assembly checkpoint" OR "mitotic checkpoint") AND (nocodazole OR "time-lapse" OR "mitotic timing") AND patient',
 "L03": '"minigene" AND "deep intronic" AND (splicing OR "pseudoexon")',
 "L04": '"allele-specific expression" AND "nonsense-mediated decay" AND (phase OR phasing OR "compound heterozygous")',
 "L05": '"RNA sequencing" AND (diagnosis OR diagnostic) AND ("rare disease" OR Mendelian) AND (fibroblast OR lymphoblastoid OR blood) AND splicing',
 "L06": '"premature chromatid separation" AND (BUB1B OR BUBR1) AND (cytogenetic OR karyotype OR metaphase)',
 "L07": '"long-read sequencing" AND (phasing OR haplotype) AND ("compound heterozygous" OR "in trans") AND (diagnosis OR clinical)',
 "L08": '(BUBR1 OR BUB1B) AND ("kinase domain" OR pseudokinase) AND (mutation OR mutant) AND (stability OR degradation)',
}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "k3-research/1.0"}), timeout=60) as r:
        return r.status, r.read()


log = []
Q2 = {
 "L03r": '"minigene" AND "deep intronic" AND splicing AND (assay OR validation)',
 "L04r": '"nonsense-mediated decay" AND (puromycin OR cycloheximide) AND ("RNA sequencing" OR "RNA-seq") AND (diagnosis OR diagnostic)',
 "L05r": '"transcriptome sequencing" AND "Mendelian" AND diagnosis AND splicing',
 "L07r": '"long-read" AND phasing AND "compound heterozygous" AND (diagnosis OR diagnostic)',
 "L09r": '"premature chromatid separation" AND "mosaic variegated aneuploidy" AND lymphocytes',
}
if sys.argv[1] in ("search", "search_rel"):
    out = {}
    for qid, q in (Q if sys.argv[1] == "search" else Q2).items():
        params = {"query": q, "format": "json", "resultType": "lite", "pageSize": "8"}
        if sys.argv[1] == "search":
            params["sort"] = "CITED desc"
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(params)
        st, b = get(url); time.sleep(0.4)
        d = json.loads(b)
        hits = [{"title": r.get("title", "")[:200], "journal": r.get("journalTitle", ""), "year": r.get("pubYear", ""),
                 "pmid": r.get("pmid", ""), "doi": r.get("doi", ""), "cited": r.get("citedByCount", 0)} for r in d["resultList"]["result"]]
        out[qid] = {"query": q, "url": url, "http": st, "sha256": hashlib.sha256(b).hexdigest(), "hitCount": d.get("hitCount"), "top": hits}
        print(f"{qid} hits={d.get('hitCount')}")
        for h in hits[:6]:
            print(f"   {h['pmid']} {h['year']} {h['journal'][:28]} | {h['title'][:110]}")
    fn = f"{K}/private_runs/C_lit_{sys.argv[1]}.json"
else:
    out = {}
    for pm in sys.argv[2:]:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": (f'DOI:"{pm}"' if "/" in pm else f"EXT_ID:{pm} AND SRC:MED"), "format": "json", "resultType": "core"})
        st, b = get(url); time.sleep(0.4)
        r = json.loads(b)["resultList"]["result"]
        r = r[0] if r else {}
        ab = re.sub(r"<[^>]+>", "", r.get("abstractText", "") or "")
        out[pm] = {"url": url, "http": st, "sha256": hashlib.sha256(b).hexdigest(), "title": r.get("title"), "authors": r.get("authorString", "")[:200],
                   "journal": r.get("journalInfo", {}).get("journal", {}).get("title"), "year": r.get("pubYear"), "doi": r.get("doi"),
                   "abstract": ab}
        print(f"{pm} chars={len(ab)} | {r.get('pubYear')} | {(r.get('title') or '')[:100]}")
    fn = f"{K}/private_runs/C_lit_abstracts_{int(time.time())}.json"
with open(fn, "w") as fh:
    json.dump(out, fh, indent=1)
os.chmod(fn, 0o600)
