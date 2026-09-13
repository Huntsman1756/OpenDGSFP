# -*- coding: utf-8 -*-
"""G0-C bounded enumeration: fondos (F) and planes (N) key spaces, small samples.

Existence oracle: detail response containing 'No se han encontrado datos' = absent.
Captures raw HTML for existing keys with provenance.
"""
import concurrent.futures as cf
import datetime
import hashlib
import json
import pathlib
import re
import threading
import time
import html as H

import requests

BASE = "https://rrpp.dgsfp.mineco.es"
OUT = pathlib.Path("data/raw/dgsfp/rrpp_pensions")
OUT.mkdir(parents=True, exist_ok=True)
TLS = threading.local()

SECTIONS = {"Fondo": "F", "Plan": "N"}


def sess():
    if not hasattr(TLS, "s"):
        s = requests.Session()
        s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                          "Referer": BASE + "/"})
        s.get(BASE + "/", timeout=60)
        TLS.s = s
    return TLS.s


def probe(section, prefix, n):
    clave = f"{prefix}{n:04d}"
    r = sess().get(f"{BASE}/{section}/Get{section}/",
                   params={"culture": "es-ES", "ui-culture": "es-ES", "clave": clave}, timeout=60)
    if r.status_code == 200 and "No se han encontrado datos" not in r.text:
        pairs = re.findall(r'<label class="label-literal">([\s\S]*?)</label>\s*<label[^>]*>([\s\S]*?)</label>', r.text)
        d = {H.unescape(re.sub(r"<[^>]+>", " ", a)).strip(): H.unescape(re.sub(r"<[^>]+>", " ", b)).strip()
             for a, b in pairs}
        fn = OUT / f"{clave}.html"
        fn.write_bytes(r.content)
        rec = {
            "source_system": "DGSFP_RRPP",
            "endpoint": f"{BASE}/{section}/Get{section}/",
            "method": "GET",
            "params": {"clave": clave},
            "clave": clave, "section": section,
            "http_status": 200,
            "bytes": len(r.content),
            "content_sha256": hashlib.sha256(r.content).hexdigest(),
            "retrieved_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "captured_file": fn.name,
            "parser_version": "rrpp_detail_parser/0.2",
        }
        return clave, rec, d
    return clave, None, None


def scan(section, prefix, hi):
    out = {}
    log = OUT / f"_capture_log_{section.lower()}.jsonl"
    with log.open("w", encoding="utf-8") as fl:
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(probe, section, prefix, n): n for n in range(1, hi + 1)}
            for f in cf.as_completed(futs):
                clave, rec, fields = f.result()
                if rec:
                    out[clave] = fields
                    fl.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    t0 = time.time()
    fondos = scan("Fondo", "F", 800)
    planes = scan("Plan", "N", 1500)
    print(f"fondos found: {len(fondos)} | planes found: {len(planes)} | {time.time()-t0:.0f}s")
    for k, d in list(sorted(fondos.items()))[:3]:
        den = next((v for kk, v in d.items() if "Denominaci" in kk), "?")
        lei = next((v for kk, v in d.items() if "LEI" in kk.upper()), "")
        print("  fondo", k, den[:50], "| lei:", lei[:24])
    for k, d in list(sorted(planes.items()))[:3]:
        den = next((v for kk, v in d.items() if "Denominaci" in kk), "?")
        print("  plan", k, den[:50])
