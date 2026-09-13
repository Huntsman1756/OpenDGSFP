# -*- coding: utf-8 -*-
import requests, re, html as H

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "Referer": "https://rrpp.dgsfp.mineco.es/"})
for clave, tipo in [("L9999", "L "), ("E0001", "E "), ("E0002", "E "),
                    ("R0001", "R "), ("M0001", "M "), ("P0001", "P "), ("C9999", "C ")]:
    r = s.get("https://rrpp.dgsfp.mineco.es/Aseguradora/GetAseguradora/",
              params={"culture": "es-ES", "ui-culture": "es-ES", "clave": clave, "tipoOperador": tipo}, timeout=60)
    m = re.search(r'label-literal">Clave:</label>\s*<label[^>]*>([^<]*)<', r.text)
    d = re.search(r'aria-label="Descripcion"[^>]*>([^<]*)<', r.text)
    print(clave, r.status_code, "len", len(r.text),
          "clave-shown:", (m.group(1) if m else None),
          "| denom:", (H.unescape(d.group(1)).strip()[:50] if d else None))
