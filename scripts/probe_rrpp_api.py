# -*- coding: utf-8 -*-
"""Probe DGSFP RRPP search/detail/export endpoints."""
import requests, json, sys, datetime

BASE = "https://rrpp.dgsfp.mineco.es"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 (research; opendgsfp)",
     "Accept": "application/json, text/javascript, */*; q=0.01",
     "X-Requested-With": "XMLHttpRequest",
     "Referer": "https://rrpp.dgsfp.mineco.es/"}

s = requests.Session()
s.headers.update(H)
s.get(BASE + "/", timeout=60)

def show(tag, r, save=None, limit=600):
    print(f"--- {tag}: HTTP {r.status_code} ct={r.headers.get('content-type')} len={len(r.content)}")
    if save:
        open(save, "wb").write(r.content)
        print("saved", save)
    else:
        try:
            t = r.text
            print(t[:limit].replace("\n", " ")[:limit])
        except Exception:
            print(r.content[:200])

# Try GET first
show("GET GetAseguradorasBusqueda", s.get(BASE + "/Aseguradora/GetAseguradorasBusqueda", timeout=60))
# Try POST with empty JSON
show("POST empty json", s.post(BASE + "/Aseguradora/GetAseguradorasBusqueda", json={}, timeout=60))
# Try form-encoded
show("POST form", s.post(BASE + "/Aseguradora/GetAseguradorasBusqueda", data={"pagina": 1, "tamPagina": 10}, timeout=60))
