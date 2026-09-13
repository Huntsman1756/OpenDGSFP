# -*- coding: utf-8 -*-
"""G0 enumerator: scan DGSFP RRPP key spaces via the detail GET endpoint.

Existence oracle: HTTP 200 = clave exists; HTTP 500 = clave does not exist
(server-side null deref), verified against known-existent and known-absent keys.

Outputs (raw, immutable):
  data/raw/dgsfp/rrpp_details/{CLAVE}.html          one file per existing clave
  data/raw/dgsfp/rrpp_details/_capture_log.jsonl    provenance per capture
  data/raw/dgsfp/_notfound_log.jsonl                non-existence evidence (500s)

Politeness: 6 workers, retries with backoff, ~30k requests/day is trivial for
a register UI but we stay modest.
"""
import concurrent.futures as cf
import datetime
import hashlib
import json
import pathlib
import re
import sys
import threading
import time

import requests
import html as H

BASE = "https://rrpp.dgsfp.mineco.es"
DETAIL = BASE + "/Aseguradora/GetAseguradora/"
OUT_RAW = pathlib.Path("data/raw/dgsfp/rrpp_details")
OUT_RAW.mkdir(parents=True, exist_ok=True)

TLS = threading.local()


def sess():
    if not hasattr(TLS, "s"):
        s = requests.Session()
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 (research; opendgsfp-g0; reproducible capture)",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": BASE + "/Aseguradora",
        })
        s.get(BASE + "/", timeout=60)
        TLS.s = s
    return TLS.s


def fetch(clave, tipo, retries=3):
    params = {"culture": "es-ES", "ui-culture": "es-ES", "clave": clave, "tipoOperador": tipo}
    for attempt in range(retries):
        try:
            r = sess().get(DETAIL, params=params, timeout=60)
            return r
        except Exception:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"fetch failed after retries: {clave}")


def capture(clave, tipo):
    r = fetch(clave, tipo)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if r.status_code == 200:
        fn = OUT_RAW / f"{clave}.html"
        fn.write_bytes(r.content)
        rec = {
            "source_system": "DGSFP_RRPP",
            "endpoint": DETAIL,
            "method": "GET",
            "params": params_of(clave, tipo),
            "jurisdiction": "ES",
            "clave": clave,
            "http_status": 200,
            "bytes": len(r.content),
            "content_sha256": hashlib.sha256(r.content).hexdigest(),
            "retrieved_at_utc": now,
            "captured_file": fn.name,
            "parser_version": "rrpp_detail_parser/0.2",
        }
        return ("200", rec)
    return (str(r.status_code), None)


def params_of(clave, tipo):
    return {"culture": "es-ES", "ui-culture": "es-ES", "clave": clave, "tipoOperador": tipo}


def build_plan():
    plan = []
    for n in range(1, 1000):
        plan.append((f"C{n:04d}", "C "))
    for n in range(1, 1000):
        plan.append((f"M{n:04d}", "M "))
    for n in range(1, 100):
        plan.append((f"P{n:04d}", "P "))
    for n in range(1, 1300):
        plan.append((f"R{n:04d}", "R "))
    for n in range(1, 500):
        plan.append((f"E{n:04d}", "E "))
    for n in range(1, 2000):
        plan.append((f"L{n:04d}", "L "))
    plan += [("C1000", "C "), ("C1200", "C "), ("C1500", "C "), ("C2000", "C "), ("C2500", "C "),
             ("M600", "M "), ("M700", "M "), ("M0600", "M "), ("M0700", "M "),
             ("R1300", "R "), ("R1500", "R "),
             ("E600", "E "), ("E700", "E "), ("E0600", "E "), ("E0700", "E "),
             ("RE0001", "RE"), ("RE0050", "RE"), ("RE0100", "RE"), ("RE0200", "RE")]
    # dedupe preserving order
    seen, out = set(), []
    for c, t in plan:
        if c not in seen:
            seen.add(c)
            out.append((c, t))
    return out


def main():
    plan = build_plan()
    print("plan size:", len(plan))
    cap_log = OUT_RAW / "_capture_log.jsonl"
    nf_log = pathlib.Path("data/raw/dgsfp/_notfound_log.jsonl")
    done = set()
    if cap_log.exists():
        for line in cap_log.open(encoding="utf-8"):
            try:
                done.add(json.loads(line)["clave"])
            except Exception:
                pass
    todo = [(c, t) for c, t in plan if c not in done]
    print("todo:", len(todo), "already captured:", len(done))
    t0 = time.time()
    with cap_log.open("a", encoding="utf-8") as fl, nf_log.open("a", encoding="utf-8") as fnf:
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(capture, c, t): (c, t) for c, t in todo}
            n200 = n404 = 0
            for f in cf.as_completed(futs):
                c, t = futs[f]
                try:
                    status, rec = f.result()
                except Exception as e:
                    print("ERR", c, str(e)[:80])
                    continue
                if status == "200":
                    fl.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n200 += 1
                else:
                    fnf.write(json.dumps({"clave": c, "tipo_operador": t, "http_status": status,
                                          "retrieved_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()},
                                         ensure_ascii=False) + "\n")
                    n404 += 1
                if (n200 + n404) % 250 == 0:
                    print(f"progress {(n200 + n404)}/{len(todo)} 200={n200} absent={n404} elapsed={time.time()-t0:.0f}s")
                    fl.flush()
    print(f"DONE 200={n200} absent={n404} elapsed={time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
