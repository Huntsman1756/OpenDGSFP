# -*- coding: utf-8 -*-
"""Try payload variants for /Aseguradora/GetAseguradorasBusqueda."""
import requests, json

BASE = "https://rrpp.dgsfp.mineco.es"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "X-Requested-With": "XMLHttpRequest",
                  "Referer": "https://rrpp.dgsfp.mineco.es/"})
s.get(BASE + "/", timeout=60)

def post(tag, data, params=None, js=False):
    r = s.post(BASE + "/Aseguradora/GetAseguradorasBusqueda",
               params=params or {}, json=data if js else None, data=None if js else data, timeout=90)
    print(tag, "HTTP", r.status_code, "->", r.text[:220].replace("\n", " "))
    return r

base_form = {
    "Gestora": "false",
    "OperadorClave": "4",
    "Clave": "",
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
}
grid = {"page": "1", "rows": "100", "sidx": "", "sord": ""}

post("form only", base_form)
post("form+grid", {**base_form, **grid})
post("form+grid+_search", {**base_form, **grid, "_search": "false"})
post("form+grid qs", {**base_form, **grid}, params={"culture": "es-ES", "ui-culture": "es-ES"})
post("TipoEntidad 'LPS '", {**base_form, **grid, "TipoEntidad": "LPS "})
post("TipoEntidad LPS notrim", {**base_form, **grid, "TipoEntidad": "LPS"})
post("no TipoEntidad", {**{k: v for k, v in base_form.items() if k != "TipoEntidad"}, **grid})
post("OperadorClave empty", {**base_form, **grid, "Clave": "L", "OperadorClave": "1"})
post("json body", {**base_form, **grid}, js=True)
