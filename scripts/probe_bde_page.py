# -*- coding: utf-8 -*-
import requests, re

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)"})
r = s.get("https://www.bde.es/wbe/es/datos/estadisticas/entidades-registradas/", timeout=60)
print("status", r.status_code, "len", len(r.text))
open("data/raw/bde/bde_entidades_registradas_page.html", "w", encoding="utf-8").write(r.text)
links = re.findall(r'href="([^"]+)"[^>]*>([^<]{3,80})<', r.text)
for u, t in links:
    if any(k in (u + t).lower() for k in ["segur", "reaseg", "csv", "xls", "entidad", "pension"]):
        print(u[:120], "|", t.strip()[:70])
