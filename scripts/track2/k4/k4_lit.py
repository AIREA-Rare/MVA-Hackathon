"""K4-C: public literature checks by PMID only (Europe PMC REST). For each PMID: metadata, open-access flag and PMCID;
if open access, the full text XML is fetched and sentences matching residue/mechanism patterns are extracted. Raw
responses are not stored (SHA-256 only). Access level is recorded per source: 'full text (open access XML)' or
'abstract (raw API text)'. Writes private_runs/C_lit.json; prints access levels and pattern-hit counts.
usage: python3 -B -I k4_lit.py <PMID> [<PMID> ...]"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

K4 = os.path.join(os.environ["MVA_DATA_ROOT"], "out/T2K4_mechanistic_2026-10-24")
CFG = json.load(open(os.environ["MVA_PRIVATE_CONFIG"]))  # participant-specific values (private file; never committed)
os.umask(0o077)
PAT = {**CFG["k4_lit_neighbour_patterns"], "turnover/stability": r"turnover|half-life|stabilit|degrad",
       "kinase domain": r"kinase domain|pseudokinase", "PLK1": r"Plk1|PLK1|Polo"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "k4-research/1.0"}), timeout=90) as r:
        return r.status, r.read()


out = {}
for pm in sys.argv[1:]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": (f'DOI:"{pm}"' if "/" in pm else f"EXT_ID:{pm} AND SRC:MED"), "format": "json", "resultType": "core"})
    st, b = get(url); time.sleep(0.4)
    r = (json.loads(b)["resultList"]["result"] or [{}])[0]
    rec = {"pmid": pm, "title": r.get("title"), "authors": (r.get("authorString") or "")[:150], "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title"),
           "year": r.get("pubYear"), "doi": r.get("doi"), "pmcid": r.get("pmcid"), "isOpenAccess": r.get("isOpenAccess"), "meta_sha256": hashlib.sha256(b).hexdigest()}
    text, access = re.sub(r"<[^>]+>", "", r.get("abstractText") or ""), "abstract (raw API text)"
    if r.get("pmcid") and r.get("isOpenAccess") == "Y":
        try:
            st2, b2 = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{r['pmcid']}/fullTextXML"); time.sleep(0.4)
            if st2 == 200 and len(b2) > 5000:
                text = re.sub(r"<[^>]+>", " ", b2.decode("utf-8", "replace")); access = "full text (open access XML)"
                rec["fulltext_sha256"] = hashlib.sha256(b2).hexdigest()
        except Exception as e:
            rec["fulltext_error"] = str(e)[:100]
    rec["access"] = access
    sents = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text))
    rec["hits"] = {k: [s[:400] for s in sents if re.search(p, s)][:12] for k, p in PAT.items()}
    out[pm] = rec
    print(pm, "|", rec["year"], "|", (rec["title"] or "")[:80], "|", access, "|", {k: len(v) for k, v in rec["hits"].items()})
fn = f"{K4}/private_runs/C_lit_{int(time.time())}.json"
json.dump(out, open(fn, "w"), indent=1)
os.chmod(fn, 0o600)
