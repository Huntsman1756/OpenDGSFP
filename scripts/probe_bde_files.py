# -*- coding: utf-8 -*-
import requests, re

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)"})
for tag, url in [("seguros", "https://www.bde.es/wbe/es/estadisticas/otras-clasificaciones/clasificacion-entidades/listas-instituciones-financieras/listas-empresas-seguros-pais/"),
                 ("fondospen", "https://www.bde.es/wbe/es/estadisticas/otras-clasificaciones/clasificacion-entidades/listas-instituciones-financieras/listas-fondos-pensiones-pais/")]:
    r = s.get(url, timeout=60)
    print("==", tag, r.status_code, "len", len(r.text))
    open(f"data/raw/bde/bde_listas_{tag}_page.html", "w", encoding="utf-8").write(r.text)
    for u in sorted(set(re.findall(r'href="([^"]+\.(?:csv|xls|xlsx)[^"]*)"', r.text, re.I))):
        print("   FILE:", u[:140])
    for u, t in re.findall(r'href="([^"]+)"[^>]*>([^<]{4,100})', r.text):
        if ("segur" in (u + t).lower() or "pension" in (u + t).lower()) and "listas" in u:
            print("   LINK:", u[:130], "|", t.strip()[:60])
