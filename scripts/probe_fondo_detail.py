# -*- coding: utf-8 -*-
"""Last attempts at Fondo detail; then classify as functional gap if needed."""
import requests

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "X-Requested-With": "XMLHttpRequest"})
s.get("https://rrpp.dgsfp.mineco.es/Fondo", timeout=60)
B = "https://rrpp.dgsfp.mineco.es"

# 1) GET with word tipoOperador
for to in ["Personal", "Abierto", "Empleo", "Mixto", "0"]:
    r = s.get(B + "/Fondo/GetFondo/", params={"culture": "es-ES", "ui-culture": "es-ES", "clave": "F0021", "tipoOperador": to}, timeout=60)
    print("GET tipoOperador=", to, r.status_code, "has-data:", "No se han encontrado datos" not in r.text)

# 2) POST detail
r = s.post(B + "/Fondo/GetFondo/", data={"clave": "F0021", "tipoOperador": "1"}, timeout=60)
print("POST detail:", r.status_code, "has-data:", "No se han encontrado datos" not in r.text, len(r.text))

# 3) search endpoint with clave only
r = s.post(B + "/Fondo/GetFondosBusqueda", data={"OperadorClave": "4", "Clave": "F0021", "page": "1", "rows": "10"}, timeout=60)
print("search clave only:", r.status_code, "->", r.text[:200])

# 4) search with full default form
form = {"OperadorClave": "3", "Clave": "", "OperadorCif": "3", "Cif": "",
        "OperadorDescripcion": "3", "Descripcion": "PENSIONES", "TipoFondo": "",
        "TipoFondoEuropeo": "", "TipoFondoPublico": "", "page": "1", "rows": "20"}
r = s.post(B + "/Fondo/GetFondosBusqueda", data=form, timeout=60)
print("search denominacion:", r.status_code, "->", r.text[:300])
