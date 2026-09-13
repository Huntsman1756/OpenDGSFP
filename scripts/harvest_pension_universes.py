# -*- coding: utf-8 -*-
"""Harvest pension + PUI universes from RRPP (full JSON arrays), with provenance."""
import datetime
import hashlib
import json
import pathlib
import requests

B = "https://rrpp.dgsfp.mineco.es"
OUT = pathlib.Path("data/raw/dgsfp")
MANIFEST = pathlib.Path("evidence/source-manifest.json")
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)",
                  "X-Requested-With": "XMLHttpRequest",
                  "Referer": B + "/"})
s.get(B + "/", timeout=60)


def grab(section, body=None, save_as=None, cap_mb=40):
    r = s.post(f"{B}/{section}", data=body or {}, timeout=300)
    mb = len(r.content) / 1e6
    print(section, r.status_code, f"{mb:.1f} MB", r.headers.get("content-type"))
    rec = None
    if save_as and mb < cap_mb:
        p = OUT / save_as
        p.write_bytes(r.content)
        rec = {
            "source_system": "DGSFP_RRPP",
            "source_url": f"{B}/{section}",
            "method": "POST",
            "params": body or {},
            "jurisdiction": "ES",
            "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "http_status": r.status_code,
            "content_sha256": hashlib.sha256(r.content).hexdigest(),
            "bytes": len(r.content),
            "raw_file": str(p).replace("\\", "/"),
        }
    return r


r_gest = grab("Gestora/GetGestorasBusqueda", {"page": "1", "rows": "10"}, "rrpp_gestoras.json")
r_fond = grab("Fondo/GetFondosBusqueda", {"page": "1", "rows": "10"}, "rrpp_fondos.json")
r_dep = grab("Depositaria/GetDepositariasBusqueda", {"page": "1", "rows": "10"}, "rrpp_depositarias.json")
# plan: try adding required selects
r_plan = grab("Plan/GetPlanesBusqueda", {"Modalidad": "", "Situacion": "1", "page": "1", "rows": "10"}, "rrpp_planes.json")
# mediador: capture only if moderate size
r_med = grab("Mediador/GetMediadoresBusqueda", {"page": "1", "rows": "10"}, "rrpp_mediadores.json", cap_mb=25)

m = json.loads(MANIFEST.read_text(encoding="utf-8"))
for rec in [r_gest, r_fond, r_dep, r_plan, r_med]:
    pass
print("sizes: gestoras", len(r_gest.content), "fondos", len(r_fond.content),
      "depositarias", len(r_dep.content), "planes", len(r_plan.content), "mediadores", len(r_med.content))
