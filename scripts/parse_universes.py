# -*- coding: utf-8 -*-
"""Parse pension/PUI universes; counts, fields, samples; manifest entry."""
import datetime
import hashlib
import json
import pathlib
import collections

OUT = pathlib.Path("data/raw/dgsfp")
MANIFEST = pathlib.Path("evidence/source-manifest.json")
PARSER = "rrpp_json_universe_parser/0.1"

sums = {}
for name, fn in [("gestoras", "rrpp_gestoras.json"), ("fondos", "rrpp_fondos.json"),
                 ("depositarias", "rrpp_depositarias.json"), ("planes", "rrpp_planes.json"),
                 ("mediadores", "rrpp_mediadores.json")]:
    p = OUT / fn
    raw = p.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8-sig"))
        rec = {
            "file": fn, "kind": "array" if isinstance(data, list) else "error",
            "count": len(data) if isinstance(data, list) else 0,
            "fields": sorted(data[0].keys()) if isinstance(data, list) and data else [],
        }
        if isinstance(data, dict):
            rec["error"] = data
        sums[name] = rec
    except Exception as e:
        sums[name] = {"file": fn, "error": str(e)[:100]}
    # manifest
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m.append({
        "source_system": "DGSFP_RRPP",
        "source_url": "https://rrpp.dgsfp.mineco.es/" + {
            "gestoras": "Gestora/GetGestorasBusqueda", "fondos": "Fondo/GetFondosBusqueda",
            "depositarias": "Depositaria/GetDepositariasBusqueda", "planes": "Plan/GetPlanesBusqueda",
            "mediadores": "Mediador/GetMediadoresBusqueda"}[name],
        "method": "POST",
        "jurisdiction": "ES",
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "content_sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "raw_file": f"raw/dgsfp/{fn}",
        "parser_version": PARSER,
    })
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")

for k, v in sums.items():
    print(k, "->", {x: v.get(x) for x in ("kind", "count")}, (v.get("fields") or v.get("error")))

# mediador field characterization (G0-D)
med = json.loads((OUT / "rrpp_mediadores.json").read_bytes().decode("utf-8-sig"))
print("\nMEDIADOR universe:", len(med))
cm = collections.Counter(x.get("claseMediador") for x in med)
print("claseMediador distribution:", dict(cm.most_common(12)))
print("sample:", json.dumps(med[0], ensure_ascii=False)[:400])
print("with web:", sum(1 for x in med if x.get("paginaWeb")))

# fondos: count with NIF (acreditacion)
fondos = json.loads((OUT / "rrpp_fondos.json").read_bytes().decode("utf-8-sig"))
print("\nFONDOS universe:", len(fondos))
print("con NIF:", sum(1 for x in fondos if x.get("acreditacion")))
gest = json.loads((OUT / "rrpp_gestoras.json").read_bytes().decode("utf-8-sig"))
print("GESTORAS universe:", len(gest))
dep = json.loads((OUT / "rrpp_depositarias.json").read_bytes().decode("utf-8-sig"))
print("DEPOSITARIAS universe:", len(dep))
