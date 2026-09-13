# -*- coding: utf-8 -*-
"""Dump option labels + operator values, then test a real search POST."""
import re, requests, json

html = open("data/raw/dgsfp/rrpp_home_2026-09-13.html", encoding="utf-8").read()
for sid in ["cmbOperadorClave", "Situacion", "cmbAmbito", "cmbTiposEntidades"]:
    m = re.search(r'<select[^>]*id="%s"[\s\S]*?</select>' % sid, html)
    if m:
        print("==== %s ====" % sid)
        for om in re.finditer(r"<option[^>]*>([^<]*)</option>", m.group(0)):
            print(repr(om.group(0)[:150]))

BASE = "https://rrpp.dgsfp.mineco.es"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "X-Requested-With": "XMLHttpRequest",
                  "Referer": "https://rrpp.dgsfp.mineco.es/Aseguradora"})
s.get(BASE + "/", timeout=60)

body = {
    "Gestora": "false",
    "OperadorClave": "3",      # try "begins with"
    "Clave": "L",
    "OperadorCif": "3",
    "Cif": "",
    "OperadorDescripcion": "3",
    "Descripcion": "",
    "Situacion": "1",          # vigente
    "Ambito": "",
    "TipoEntidad": "L ",
    "Espannola": "false",
    "OpcionBusqueda": "actividad",
    "TipoActividadSeleccionada": "--",
    "Ramo": "",
    "Modalidades": "",
    "Prestacion": "",
    "RamosTexto": "",
    "PrestacionesTexto": "",
    "PaisOrigenLPS": "false",
    "PaisOrigenDE": "false",
    "PaisOrigen": "",
    "EEE": "true",
    "BusquedaCombinadaRamos": "false",
    "page": "1",
    "rows": "100",
    "sidx": "",
    "sord": "",
}
r = s.post(BASE + "/Aseguradora/GetAseguradorasBusqueda", data=body, timeout=90)
print("HTTP", r.status_code, r.headers.get("content-type"))
print(r.text[:1500])
