# -*- coding: utf-8 -*-
"""Final search-endpoint sweep; then verify detail-endpoint key enumeration viability."""
import requests, json

BASE = "https://rrpp.dgsfp.mineco.es"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                  "Accept": "application/json, text/javascript, */*; q=0.01",
                  "Accept-Language": "es-ES,es;q=0.9",
                  "X-Requested-With": "XMLHttpRequest",
                  "Origin": "https://rrpp.dgsfp.mineco.es",
                  "Referer": "https://rrpp.dgsfp.mineco.es/Aseguradora"})
s.get(BASE + "/Aseguradora", timeout=60)

form = {
    "Gestora": "false", "OperadorClave": "4", "Clave": "L1160",
    "OperadorCif": "4", "Cif": "", "OperadorDescripcion": "4", "Descripcion": "",
    "Situacion": "1", "Ambito": "", "TipoEntidad": "L ", "Espannola": "false",
    "OpcionBusqueda": "actividad", "TipoActividadSeleccionada": "--",
    "Ramo": "", "Modalidades": "", "Prestacion": "", "RamosTexto": "", "PrestacionesTexto": "",
    "PaisOrigenLPS": "false", "PaisOrigenDE": "false", "PaisOrigen": "",
    "EEE": "true", "BusquedaCombinadaRamos": "false",
    "page": "1", "rows": "10", "sidx": "", "sord": "",
}
tries = [
    ("charset-hdr", {**form}, {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}),
    ("GET-query", None, None),
]
for tag, body, hdr in tries:
    try:
        if body is None:
            r = s.get(BASE + "/Aseguradora/GetAseguradorasBusqueda", params={**form}, timeout=60)
        else:
            h = dict(s.headers); h.update(hdr)
            r = s.post(BASE + "/Aseguradora/GetAseguradorasBusqueda", data=body, headers=h, timeout=60)
        print(tag, r.status_code, "->", r.text[:160].replace("\n", " "))
    except Exception as e:
        print(tag, "EXC", str(e)[:100])

# key enumeration viability via detail endpoint: probe a spread of L keys
print("\n--- L key probing (detail GET) ---")
for n in [1, 100, 400, 800, 1000, 1200, 1400]:
    clave = f"L{n:04d}"
    r = s.get(BASE + "/Aseguradora/GetAseguradora/", params={"culture": "es-ES", "ui-culture": "es-ES", "clave": clave, "tipoOperador": "L "}, timeout=60)
    import re
    m = re.search(r'aria-label="Denominaci[oó]n"[^>]*>([^<]*)<', r.text)
    sit = re.search(r'aria-label="Situaci[oó]n"[^>]*>([^<]*)<', r.text)
    print(clave, r.status_code, "len", len(r.text), "| denom:", (m.group(1).strip() if m else "-")[:60], "| sit:", (sit.group(1).strip() if sit else "-"))
