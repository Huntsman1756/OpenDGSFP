# -*- coding: utf-8 -*-
"""G0-C probes: fondo/plan detail keys + BdE PF list structure."""
import re
import sys
import html as H
import requests

sys.path.insert(0, "scripts")
from bde_loader import load_bde

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)"})
s.get("https://rrpp.dgsfp.mineco.es/", timeout=60)

def detail(section, clave, extra=None):
    params = {"culture": "es-ES", "ui-culture": "es-ES", "clave": clave}
    if extra:
        params.update(extra)
    r = s.get(f"https://rrpp.dgsfp.mineco.es/{section}/Get{section}/", params=params, timeout=60)
    if r.status_code != 200:
        return clave, r.status_code, None, None
    pairs = re.findall(r'<label class="label-literal">([\s\S]*?)</label>\s*<label[^>]*>([\s\S]*?)</label>', r.text)
    d = {H.unescape(re.sub(r"<[^>]+>", " ", a)).strip(): H.unescape(re.sub(r"<[^>]+>", " ", b)).strip()
         for a, b in pairs}
    den = next((v for k, v in d.items() if "Denominaci" in k), "?")
    lei = next((v for k, v in d.items() if "LEI" in k.upper()), "")
    return clave, 200, den[:60], lei[:26]

for sec, keys in [("Fondo", ["F0001", "F0002", "F0100", "F0150"]),
                  ("Plan", ["W0001", "P0001", "W0002", "B0001"])]:
    for k in keys:
        print(sec, detail(sec, k))

pf = load_bde("data/raw/bde/lista-pf-es.csv")
print("\nBdE PF ES rows:", len(pf), "| cols:", list(pf[0].keys()))
for r in pf[:4]:
    print("  ", {k: v[:38] for k, v in r.items()})
