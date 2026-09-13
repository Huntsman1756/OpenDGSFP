# -*- coding: utf-8 -*-
"""Find upper bounds of each key space by probing."""
import requests, concurrent.futures as cf

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "Referer": "https://rrpp.dgsfp.mineco.es/"})

def exists(prefix, n):
    clave = f"{prefix}{n:04d}"
    r = s.get("https://rrpp.dgsfp.mineco.es/Aseguradora/GetAseguradora/",
              params={"culture": "es-ES", "ui-culture": "es-ES", "clave": clave, "tipoOperador": prefix + " "}, timeout=45)
    return clave, r.status_code

for prefix, hi in [("C", 2600), ("M", 800), ("P", 800), ("R", 600), ("E", 800), ("L", 2000)]:
    tests = [(prefix, n) for n in [100, 500, 900, hi, hi + 400, hi + 800]]
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for f in cf.as_completed([ex.submit(exists, p, n) for p, n in tests]):
            print(f.result())
    print("---")
