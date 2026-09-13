# -*- coding: utf-8 -*-
import requests, re, html as H, concurrent.futures as cf

BASE = "https://rrpp.dgsfp.mineco.es/Aseguradora/GetAseguradora/"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "Referer": "https://rrpp.dgsfp.mineco.es/"})

def probe(clave, tipo):
    try:
        r = s.get(BASE, params={"culture": "es-ES", "ui-culture": "es-ES", "clave": clave, "tipoOperador": tipo}, timeout=45)
        if r.status_code == 200:
            d = re.search(r'aria-label="Descripcion"[^>]*>([^<]*)<', r.text)
            p = re.search(r'aria-label="Pais de origen"[^>]*>([^<]*)<', r.text)
            return clave, "200", (H.unescape(d.group(1)).strip()[:60] if d else "-"),
        return clave, str(r.status_code), "-"
    except Exception as e:
        return clave, "EXC", str(e)[:40]

tests = [("E0050", "E "), ("E0100", "E "), ("E0193", "E "), ("E0300", "E "),
         ("M0002", "M "), ("M0100", "M "), ("M0300", "M "),
         ("P0002", "P "), ("P0100", "P "), ("P0300", "P "),
         ("M0001", "M"), ("P0001", "P")]
with cf.ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(probe, c, t): (c, t) for c, t in tests}
    for f in cf.as_completed(futs):
        res = f.result()
        print(res[0], res[1], res[2])
