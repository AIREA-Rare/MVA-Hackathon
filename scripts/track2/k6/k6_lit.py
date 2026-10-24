"""K6: public literature for functional-evidence frameworks and neighbouring published variants (Europe PMC REST).
Queries contain framework names, gene symbols and a PUBLISHED neighbouring variant (not the patient's variant).
Stores abstracts (public text) and response SHA-256; prints titles and claim-relevant sentences.
usage: python3 -B -I k6_lit.py"""
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

K6 = os.path.join(os.environ["MVA_DATA_ROOT"], "out/T2K6_variant_function_2026-10-24")
CFG = json.load(open(os.environ["MVA_PRIVATE_CONFIG"]))  # participant-specific values (private file; never committed)
os.umask(0o077)
Q = {"F1": "EXT_ID:31892348 AND SRC:MED",
     "F2": '"PS3/BS3" AND (functional OR assay) AND (ClinGen OR ACMG) AND (recommendations OR framework)',
     "F3": '(ClinGen OR ACMG) AND splicing AND (recommendations OR framework) AND ("RNA" OR minigene) AND (PVS1 OR PS3 OR BP7)',
     "N1": CFG["k6_lit_neighbour_query"],
     "N2": 'BUB1B AND homozygous AND ("gastrointestinal" OR colorectal) AND neoplasia',
     "N3": '(BUBR1 OR BUB1B) AND "kinase domain" AND (mutation OR mutant) AND ("protein stability" OR degradation OR "proteasome") AND (mosaic OR MVA OR patient)'}
PAT = CFG["k6_lit_neighbour_pattern"] + r"|kinase domain|turnover|stabilit|degrad|abundance|PS3|BS3|control|calibrat|validat|replicat|splic|minigene|RNA|homozygous|aneuploid|neoplasia|missense"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "k6-research/1.0"}), timeout=90) as r:
        return r.status, r.read()


out = {}
for qid, q in Q.items():
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": q, "format": "json", "resultType": "core", "pageSize": "5"})
    st, b = get(url); time.sleep(0.4)
    d = json.loads(b)
    recs = [{"pmid": r.get("pmid"), "doi": r.get("doi"), "title": r.get("title"), "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title"), "year": r.get("pubYear"),
             "isOpenAccess": r.get("isOpenAccess"), "abstract": re.sub(r"<[^>]+>", "", r.get("abstractText") or "")} for r in d["resultList"]["result"]]
    out[qid] = {"query": q, "http": st, "sha256": hashlib.sha256(b).hexdigest(), "hitCount": d.get("hitCount"), "records": recs, "accessed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(f"===== {qid} hits={d.get('hitCount')} | {q[:90]}")
    for r in recs[:4]:
        print(f"  {r['pmid']} {r['year']} {(r['journal'] or '')[:25]} | {(r['title'] or '')[:100]} | OA {r['isOpenAccess']}")
        for s in [x for x in re.split(r"(?<=[.!?])\s+", r["abstract"]) if re.search(PAT, x)][:3]:
            print("     -", s[:250])
fn = f"{K6}/private_runs/LIT_k6.json"
json.dump(out, open(fn, "w"), indent=1); os.chmod(fn, 0o600)
