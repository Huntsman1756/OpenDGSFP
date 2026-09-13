# -*- coding: utf-8 -*-
"""Sanity: simple endpoints + alternate content types."""
import requests

BASE = "https://rrpp.dgsfp.mineco.es"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "X-Requested-With": "XMLHttpRequest",
                  "Referer": "https://rrpp.dgsfp.mineco.es/"})
print("cookies after / :", s.get(BASE + "/", timeout=60).cookies.get_dict())

for ep in ["/Aseguradora/GetPaises", "/Aseguradora/GetServceModalidades", "/Aseguradora/GetRamosPorCodigo?codigo=02"]:
    r = s.get(BASE + ep, timeout=60)
    print(ep, "HTTP", r.status_code, r.headers.get("content-type"), "->", r.text[:200].replace("\n", " "))

# detail endpoint as the SPA calls it (GET html)
r = s.get(BASE + "/Aseguradora/GetAseguradora/", params={"culture": "es-ES", "ui-culture": "es-ES", "clave": "C0001", "tipoOperador": "C "}, timeout=60)
print("detail HTTP", r.status_code, "len", len(r.text), r.headers.get("content-type"))
print(r.text[:400])
