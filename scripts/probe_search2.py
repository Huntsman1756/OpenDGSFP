# -*- coding: utf-8 -*-
"""Probe POST support endpoints + search retries after loading /Aseguradora."""
import requests

BASE = "https://rrpp.dgsfp.mineco.es"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "X-Requested-With": "XMLHttpRequest",
                  "Referer": "https://rrpp.dgsfp.mineco.es/Aseguradora"})

r = s.get(BASE + "/Aseguradora", timeout=60)
print("load /Aseguradora:", r.status_code, "cookies:", s.cookies.get_dict())

for ep, body in [("/Aseguradora/GetPaises", {}),
                 ("/Aseguradora/GetRamosPorCodigo", {"codigo": "02"}),
                 ("/Aseguradora/GetServceModalidades", {"codigo": "02"})]:
    r = s.post(BASE + ep, json=body, timeout=60)
    print("POST", ep, "HTTP", r.status_code, "->", r.text[:180].replace("\n", " "))

search = {
    "Gestora": "false",
    "OperadorClave": "4",
    "Clave": "L0419",
    "OperadorCif": "4",
    "Cif": "",
    "OperadorDescripcion": "4",
    "Descripcion": "",
    "Situacion": "1",
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
    "page": "1", "rows": "100", "sidx": "", "sord": "", "_search": "false",
    "nd": "1789260000000",
    "filters": "",
}
r = s.post(BASE + "/Aseguradora/GetAseguradorasBusqueda", data=search, timeout=90)
print("search retry:", r.status_code, "->", r.text[:300].replace("\n", " "))

# maybe values are enum-ish strings for operators
import itertools
for oc, cl in [("1", "L"), ("2", "19"), ("4", "L1160")]:
    body = dict(search); body["OperadorClave"] = oc; body["Clave"] = cl
    r = s.post(BASE + "/Aseguradora/GetAseguradorasBusqueda", data=body, timeout=90)
    print(f"search oc={oc} clave={cl}:", r.status_code, "->", r.text[:300].replace("\n", " "))
