# -*- coding: utf-8 -*-
"""Capture RRPP detail pages reproducibly with full provenance metadata."""
import requests, hashlib, json, datetime, sys, pathlib

BASE = "https://rrpp.dgsfp.mineco.es"
OUT = pathlib.Path("data/raw/dgsfp/rrpp_details")
OUT.mkdir(parents=True, exist_ok=True)
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "Accept-Language": "es-ES,es;q=0.9",
                  "Referer": "https://rrpp.dgsfp.mineco.es/"})

def capture(clave, tipo):
    url = BASE + "/Aseguradora/GetAseguradora/"
    params = {"culture": "es-ES", "ui-culture": "es-ES", "clave": clave, "tipoOperador": tipo}
    r = s.get(url, params=params, timeout=90)
    rec = {
        "source_system": "DGSFP_RRPP",
        "endpoint": url,
        "method": "GET",
        "params": params,
        "jurisdiction": "ES",
        "clave": clave,
        "tipo_operador": tipo,
        "http_status": r.status_code,
        "response_headers": dict(r.headers),
        "retrieved_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "content_sha256": hashlib.sha256(r.content).hexdigest(),
        "bytes": len(r.content),
        "captured_file": f"{clave.strip()}_{tipo.strip()}.html",
    }
    (OUT / rec["captured_file"]).write_bytes(r.content)
    print(json.dumps(rec, ensure_ascii=False)[:400])
    return rec

keys = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] not in ("-", "") else [["C0001", "C "], ["L0419", "L "], ["L1160", "L "], ["E0193", "E "]]
allrec = [capture(k, t) for k, t in keys]
pathlib.Path("data/raw/dgsfp/rrpp_details/_capture_log.json").write_text(
    json.dumps(allrec, indent=2, ensure_ascii=False), encoding="utf-8")
