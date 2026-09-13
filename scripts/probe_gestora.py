# -*- coding: utf-8 -*-
"""Probe gestora detail keys (G0-C)."""
import re
import html as H
import requests

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "Referer": "https://rrpp.dgsfp.mineco.es/Gestora"})
s.get("https://rrpp.dgsfp.mineco.es/", timeout=60)
for clave in ["G0001", "G0002", "G0100", "G0150", "G0200"]:
    r = s.get("https://rrpp.dgsfp.mineco.es/Gestora/GetGestora/",
              params={"culture": "es-ES", "ui-culture": "es-ES", "clave": clave}, timeout=60)
    print(clave, r.status_code, len(r.text))
    if r.status_code == 200:
        pairs = re.findall(r'<label class="label-literal">([\s\S]*?)</label>\s*<label[^>]*>([\s\S]*?)</label>', r.text)
        d = {H.unescape(re.sub(r"<[^>]+>", " ", a)).strip(): H.unescape(re.sub(r"<[^>]+>", " ", b)).strip()
             for a, b in pairs}
        den = next((v for k, v in d.items() if "Denominaci" in k), "?")
        lei = next((v for k, v in d.items() if "LEI" in k.upper()), "")
        print("   denom:", den[:65], "| lei:", lei[:30])
