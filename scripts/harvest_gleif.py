# -*- coding: utf-8 -*-
"""GLEIF lei-records harvest (batched filter API, donor mechanism reused).

Inputs : LEI list built from samples + all RRPP LEIs in scope
Output : data/raw/gleif/gleif_records.jsonl, gleif_missing.json, _fetch_log.json
"""
import datetime
import json
import pathlib
import time
import urllib.request

BATCH = 50
OUT = pathlib.Path("data/raw/gleif/gleif_records.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)
MANIFEST = pathlib.Path("evidence/source-manifest.json")

req_count = {"n": 0, "first": None, "last": None}


def fetch_batch(leis):
    url = ("https://api.gleif.org/api/v1/lei-records?filter%5Blei%5D="
           + ",".join(leis) + f"&page%5Bsize%5D={BATCH}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "opendgsfp-g0 (research; identity crosswalk)",
        "Accept": "application/vnd.api+json"})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    req_count["n"] += 1
    req_count["first"] = req_count["first"] or now
    req_count["last"] = now
    out = []
    for r in d.get("data", []):
        a = r["attributes"]
        e = a["entity"]
        reg = a["registration"]
        out.append({
            "lei": r["id"],
            "legalName": e["legalName"]["name"],
            "entityStatus": e.get("status"),
            "legalForm": (e.get("legalForm") or {}).get("id"),
            "jurisdiction": e.get("jurisdiction"),
            "country": (e.get("legalAddress") or {}).get("country"),
            "regStatus": reg.get("status"),
            "lastUpdate": reg.get("lastUpdateDate"),
            "nextRenewal": reg.get("nextRenewalDate"),
            "managingLou": reg.get("managingLou"),
        })
    return out


def harvest(leis):
    leis = sorted({l.strip().upper() for l in leis if l.strip()})
    done = set()
    if OUT.exists():
        for line in OUT.open(encoding="utf-8"):
            try:
                done.add(json.loads(line)["lei"])
            except Exception:
                pass
    todo = [l for l in leis if l not in done]
    print("requested:", len(leis), "todo:", len(todo))
    found = set(done)
    with OUT.open("a", encoding="utf-8") as f:
        for i in range(0, len(todo), BATCH):
            chunk = todo[i:i + BATCH]
            for attempt in range(4):
                try:
                    for rec in fetch_batch(chunk):
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        found.add(rec["lei"])
                    f.flush()
                    break
                except Exception as ex:
                    print("retry", i, attempt, str(ex)[:80])
                    time.sleep(6 * (attempt + 1))
            time.sleep(1.1)
    missing = [l for l in leis if l not in found]
    pathlib.Path("data/raw/gleif/gleif_missing.json").write_text(
        json.dumps({"requested": leis, "missing": missing}, indent=1), encoding="utf-8")
    print("found:", len(found), "missing:", len(missing), missing[:10])
    return missing


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "scripts")
    leis = []
    # all RRPP LEIs among Activa C/M/P/R + sample E/L LEIs
    for line in open("data/derived/dgsfp_rrpp_entities.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r["tipo"] in ("C", "M", "P", "R") and r["situacion"] == "Activa":
            leis.append(r["lei"])
        elif r["tipo"] == "E" and r["situacion"] == "Activa":
            leis.append(r["lei"])
    # documented chain LEIs
    leis += ["F240A7PWJB2BLKELB442", "391200QKNZJ8J1XWFE16",
             "969500798WFE82RZZU93", "213800SCCLMKOWSSX732"]
    leis = [l for l in leis if l]
    print("LEI universe (Spanish C/M/P/R activa + E activa + docs):", len(leis))
    harvest(leis)
    # record fetch log
    log = {
        "source_system": "GLEIF",
        "api": "https://api.gleif.org/api/v1/lei-records",
        "method": "GET batched filter[lei] (donor mechanism, fabio-rovai/insurance-register-ontology)",
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "requests": req_count,
        "records_sha256": None,
    }
    m = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else []
    m.append(log)
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
