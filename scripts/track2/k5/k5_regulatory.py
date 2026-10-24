"""K5: re-verify regulatory status and label pharmacology for every K2 candidate (drug names only; public APIs).
openFDA drugsfda (applications, marketing status) and label (indications, boxed warning, mechanism section), EMA EPAR
pages where reachable. Raw responses are not stored: SHA-256, HTTP status and extracted fields only.
Writes private_runs/REG_*.json; prints a compact public summary (drug-level information only).
usage: python3 -B -I k5_regulatory.py"""
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

K5 = os.path.join(os.environ["MVA_DATA_ROOT"], "out/T2K5_drug_hypotheses_2026-10-24")
os.umask(0o077)
DRUGS = ["dasatinib", "gentamicin", "niacin", "acetylcysteine", "bortezomib", "dactinomycin", "vincristine", "somatropin", "ataluren",
         "quercetin", "nicotinamide", "nicotinamide riboside", "paclitaxel", "alisertib", "volasertib", "barasertib", "onvansertib"]
EMA = {"dasatinib": "sprycel", "bortezomib": "velcade", "ataluren": "translarna", "somatropin": "omnitrope", "acetylcysteine": None}


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "k5-research/1.0"}), timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return None, str(e).encode()


out = {"checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "drugs": {}}
for d in DRUGS:
    rec = {}
    q = urllib.parse.quote(f'openfda.generic_name:"{d}"')
    st, b = get(f"https://api.fda.gov/drug/drugsfda.json?search={q}&limit=50"); time.sleep(0.3)
    rec["drugsfda_http"] = st; rec["drugsfda_sha256"] = hashlib.sha256(b).hexdigest()
    if st == 200:
        res = json.loads(b)["results"]
        apps = [r["application_number"] for r in res]
        status = sorted({p.get("marketing_status") for r in res for p in r.get("products", [])})
        rec.update({"n_applications": len(apps), "nda_bla": [a for a in apps if a.startswith(("NDA", "BLA"))][:6], "anda_count": sum(1 for a in apps if a.startswith("ANDA")),
                    "marketing_statuses": status})
    else:
        rec.update({"n_applications": 0, "note": "openFDA returned no match (404 NOT_FOUND) or error"})
    st2, b2 = get(f"https://api.fda.gov/drug/label.json?search={q}&limit=1"); time.sleep(0.3)
    rec["label_http"] = st2
    if st2 == 200:
        L = json.loads(b2)["results"][0]
        txt = lambda k: " ".join(L.get(k, []))[:1200]
        rec.update({"label_set_id": L.get("set_id"), "label_effective": L.get("effective_time"), "label_appl": (L.get("openfda") or {}).get("application_number"),
                    "indications": txt("indications_and_usage")[:700], "boxed_warning_present": bool(L.get("boxed_warning")),
                    "boxed_warning": txt("boxed_warning")[:500], "mechanism": (txt("mechanism_of_action") or txt("clinical_pharmacology"))[:700],
                    "contraindications": txt("contraindications")[:500], "pediatric_use": txt("pediatric_use")[:600], "label_sha256": hashlib.sha256(b2).hexdigest()})
    if EMA.get(d):
        st3, b3 = get(f"https://www.ema.europa.eu/en/medicines/human/EPAR/{EMA[d]}"); time.sleep(0.3)
        t = re.sub(r"<[^>]+>", " ", b3.decode("utf-8", "replace"))
        t = re.sub(r"\s+", " ", t)
        m = re.search(r"(Authorised|Withdrawn|Expired|Suspended|Refused|Not authorised)[^.]{0,120}", t)
        rec.update({"ema_page": EMA[d], "ema_http": st3, "ema_status_snippet": m.group(0)[:160] if m else None, "ema_sha256": hashlib.sha256(b3).hexdigest()})
    out["drugs"][d] = rec
    print(f"{d:22s} | FDA apps {rec.get('n_applications', 0):3d} (NDA/BLA {len(rec.get('nda_bla', []))}, ANDA {rec.get('anda_count', 0)}) | status {rec.get('marketing_statuses', '-')} | "
          f"label {'yes' if st2 == 200 else 'no'} boxed={rec.get('boxed_warning_present', '-')}" + (f" | EMA {rec.get('ema_http')} {str(rec.get('ema_status_snippet'))[:60]}" if EMA.get(d) else ""))
fn = f"{K5}/private_runs/REG_openfda_ema.json"
json.dump(out, open(fn, "w"), indent=1)
os.chmod(fn, 0o600)
