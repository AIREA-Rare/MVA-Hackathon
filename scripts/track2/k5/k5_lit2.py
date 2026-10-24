"""K5: targeted follow-up literature (Europe PMC REST, public identifiers and generic terms only). Fetches named PMIDs and
three sharper queries; stores abstracts (public text) and SHA-256 of responses; prints the abstract sentences that
match claim-relevant patterns so the claims can be checked against the raw text.
usage: python3 -B -I k5_lit2.py"""
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

K5 = os.path.join(os.environ["MVA_DATA_ROOT"], "out/T2K5_drug_hypotheses_2026-10-24")
os.umask(0o077)
PMIDS = ["28728956", "24477002", "40607964", "41516400", "37883329", "41290707", "42628241", "22048312", "23242215", "24825348", "25754370",
         "14534336", "17290305", "41820377"]
EXTRA = {"X1": 'dasatinib AND (cytokinesis OR polyploidy OR multinucleated OR "mitotic defects")',
         "X2": '(senolytic OR "senescent cell") AND (BubR1 OR "BubR1H/H" OR "BubR1 hypomorphic") AND (drug OR dasatinib OR navitoclax OR "ABT-263")',
         "X3": '"growth hormone" AND ("mosaic variegated aneuploidy" OR CEP57 OR BUB1B)'}
PAT = r"dasatinib|senolytic|senescen|BubR1|aneuploid|missegregat|readthrough|ataluren|primary endpoint|did not|no significant|failed|NAD|niacin|nicotinamide|antioxidant|N-acetylcysteine|metasta|progression|multipolar|mitotic|growth hormone|lifespan|delay|tumou?r"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "k5-research/1.0"}), timeout=90) as r:
        return r.status, r.read()


out = {}
def fetch(qid, q, n):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": q, "format": "json", "resultType": "core", "pageSize": str(n)})
    st, b = get(url); time.sleep(0.4)
    d = json.loads(b)
    recs = [{"pmid": r.get("pmid"), "doi": r.get("doi"), "title": r.get("title"), "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title"),
             "year": r.get("pubYear"), "isOpenAccess": r.get("isOpenAccess"), "abstract": re.sub(r"<[^>]+>", "", r.get("abstractText") or "")} for r in d["resultList"]["result"]]
    out[qid] = {"query": q, "http": st, "sha256": hashlib.sha256(b).hexdigest(), "hitCount": d.get("hitCount"), "records": recs, "accessed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    return recs


for pm in PMIDS:
    for r in fetch(f"P{pm}", f"EXT_ID:{pm} AND SRC:MED", 1):
        print(f"===== {pm} {r['year']} {(r['journal'] or '')[:30]} | {(r['title'] or '')[:110]} | abstract chars {len(r['abstract'])}")
        for s in re.split(r"(?<=[.!?])\s+", r["abstract"]):
            if re.search(PAT, s, re.I):
                print("   -", s[:300])
for qid, q in EXTRA.items():
    recs = fetch(qid, q, 6)
    print(f"===== {qid} hits={out[qid]['hitCount']}")
    for r in recs[:6]:
        print(f"   {r['pmid']} {r['year']} | {(r['title'] or '')[:115]}")
fn = f"{K5}/private_runs/LIT_k5_followup.json"
json.dump(out, open(fn, "w"), indent=1)
os.chmod(fn, 0o600)
