# -*- coding: utf-8 -*-
"""Fondo detail with tipoOperador=FONDO + minimal-param searches for all sections."""
import requests

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "X-Requested-With": "XMLHttpRequest"})
s.get("https://rrpp.dgsfp.mineco.es/Fondo", timeout=60)
B = "https://rrpp.dgsfp.mineco.es"

r = s.get(B + "/Fondo/GetFondo/", params={"culture": "es-ES", "ui-culture": "es-ES", "clave": "F0021", "tipoOperador": "FONDO"}, timeout=60)
print("F0021 detail:", r.status_code, "len", len(r.text), "| has-data:", "No se han encontrado datos" not in r.text)
open("data/raw/dgsfp/rrpp_pensions/F0021.html", "wb").write(r.content)

# minimal searches on the aseguradora controller
for body in [{"OperadorClave": "4", "Clave": "L0419", "page": "1", "rows": "10"},
             {"OperadorClave": "4", "Clave": "C0001", "page": "1", "rows": "10"},
             {"OperadorClave": "1", "Clave": "L", "page": "1", "rows": "10"},
             {"OperadorDescripcion": "4", "Descripcion": "MAPFRE MUTUALIDAD", "page": "1", "rows": "10"}]:
    r = s.post(B + "/Aseguradora/GetAseguradorasBusqueda", data=body, timeout=60)
    print("aseguradora search", body, "->", r.status_code, r.text[:180].replace("\n", " "))

# pension searches: full universes?
for ep, body in [("Gestora/GetGestorasBusqueda", {"page": "1", "rows": "5"}),
                 ("Fondo/GetFondosBusqueda", {"page": "1", "rows": "5"}),
                 ("Plan/GetPlanesBusqueda", {"page": "1", "rows": "5"}),
                 ("Depositaria/GetDepositariasBusqueda", {"page": "1", "rows": "5"}),
                 ("Mediador/GetMediadoresBusqueda", {"page": "1", "rows": "5"})]:
    r = s.post(B + "/" + ep, data=body, timeout=90)
    ct = r.headers.get("content-type", "")
    print(ep, "->", r.status_code, ct[:30], r.text[:150].replace("\n", " "))
