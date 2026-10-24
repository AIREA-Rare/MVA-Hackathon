"""K5: supporting and contradictory literature for each K2 drug candidate (Europe PMC REST; generic public terms only:
drug names, gene symbols, process words). Per query: hit count, top records with abstracts (raw API text). Raw responses
are not stored (SHA-256 only); abstracts are stored as public text for citation checks. Writes private_runs/LIT_k5.json;
prints query hit counts and top titles (public literature metadata).
usage: python3 -B -I k5_lit.py"""
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

K5 = os.path.join(os.environ["MVA_DATA_ROOT"], "out/T2K5_drug_hypotheses_2026-10-24")
os.umask(0o077)
Q = {
 "D1": ('dasatinib', 'dasatinib AND (aneuploidy OR "chromosome segregation" OR "chromosomal instability" OR mitosis)'),
 "D2": ('dasatinib', '(senolytic OR "senescent cells") AND (BubR1 OR progeroid OR "BubR1 hypomorphic")'),
 "D3": ('dasatinib', '(senolytic OR "senescent cell clearance") AND (cancer OR tumor) AND (promote OR risk OR "tumour suppression" OR "tumor suppression")'),
 "G1": ('gentamicin', 'gentamicin AND readthrough AND ("nonsense-mediated decay" OR NMD) AND (patients OR clinical)'),
 "G2": ('gentamicin', '(aminoglycoside OR gentamicin) AND readthrough AND ("normal stop codons" OR "termination codons" OR toxicity OR ototoxicity)'),
 "A1": ('ataluren', 'ataluren AND (phase 3 OR "phase III") AND (nonsense OR readthrough)'),
 "N1": ('niacin/NAD', 'BubR1 AND (SIRT2 OR NAD OR acetylation)'),
 "N2": ('niacin/NAD', '(niacin OR "nicotinic acid") AND (NAD OR "NAD+") AND (human OR patients) AND (muscle OR blood OR tissue)'),
 "C1": ('acetylcysteine', '("N-acetylcysteine" OR antioxidant) AND ("chromosomal instability" OR aneuploidy OR "chromosome missegregation")'),
 "C2": ('acetylcysteine', '("N-acetylcysteine" OR antioxidants) AND ("tumor progression" OR metastasis OR "tumour progression") AND mice'),
 "B1": ('bortezomib', '(bortezomib OR "proteasome inhibitor") AND (mitosis OR mitotic) AND (arrest OR "anaphase" OR "APC/C" OR "cyclin B")'),
 "B2": ('bortezomib', '(bortezomib OR "proteasome inhibitor") AND (BubR1 OR BUB1B)'),
 "R1": ('R7 class', '("Aurora kinase inhibitor" OR "Aurora B inhibitor" OR "PLK1 inhibitor") AND (aneuploidy OR polyploidy OR "chromosome missegregation")'),
 "R2": ('R7 class', '(paclitaxel OR taxol OR "microtubule poison") AND ("chromosome missegregation" OR aneuploidy OR "multipolar spindle")'),
 "V1": ('vincristine', 'vincristine AND ("mitotic checkpoint" OR "spindle assembly checkpoint" OR aneuploidy OR "mitotic slippage")'),
 "S1": ('somatropin', '"growth hormone" AND ("cancer predisposition" OR "chromosomal instability" OR "DNA repair" OR "Bloom syndrome" OR "Fanconi anemia") AND (risk OR safety)'),
 "M1": ('MVA direct', '"mosaic variegated aneuploidy" AND (treatment OR therapy OR drug OR pharmacological OR rescue)'),
 "M2": ('MVA direct', '(BUB1B OR BubR1) AND (rescue OR restore OR "increase") AND (drug OR compound OR pharmacological) AND (aneuploidy OR checkpoint)'),
 "M3": ('cross-gene', '(TRIP13 OR CEP57 OR CENATAC) AND (drug OR inhibitor OR therapy) AND (aneuploidy OR "mosaic variegated")'),
}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "k5-research/1.0"}), timeout=90) as r:
        return r.status, r.read()


out = {}
for qid, (cand, q) in Q.items():
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": q, "format": "json", "resultType": "core", "pageSize": "6"})
    st, b = get(url); time.sleep(0.4)
    d = json.loads(b)
    recs = []
    for r in d["resultList"]["result"]:
        recs.append({"pmid": r.get("pmid"), "doi": r.get("doi"), "title": r.get("title"), "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title"),
                     "year": r.get("pubYear"), "pubtype": (r.get("pubTypeList") or {}).get("pubType"), "abstract": re.sub(r"<[^>]+>", "", r.get("abstractText") or "")})
    out[qid] = {"candidate": cand, "query": q, "url": url, "http": st, "sha256": hashlib.sha256(b).hexdigest(), "hitCount": d.get("hitCount"), "records": recs,
                "accessed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(f"{qid} [{cand}] hits={d.get('hitCount')}")
    for r in recs[:5]:
        print(f"   {r['pmid']} {r['year']} | {(r['title'] or '')[:115]}")
fn = f"{K5}/private_runs/LIT_k5.json"
json.dump(out, open(fn, "w"), indent=1)
os.chmod(fn, 0o600)
