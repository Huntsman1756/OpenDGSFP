# -*- coding: utf-8 -*-
import requests, re

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)"})
url = "https://www.bde.es/wbe/es/estadisticas/otras-clasificaciones/clasificacion-entidades/listas-instituciones-financieras/"
r = s.get(url, timeout=60)
print("status", r.status_code, "len", len(r.text))
open("data/raw/bde/bde_listas_instituciones_page.html", "w", encoding="utf-8").write(r.text)
for u, t in re.findall(r'href="([^"]+)"[^>]*>([^<]{2,120})', r.text):
    tl = (u + t).lower()
    if any(k in tl for k in ["segur", "reaseg", "csv", "xls", "asegur", "pension", "lista"]):
        print(u[:130], "|", t.strip()[:80])
