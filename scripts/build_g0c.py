# -*- coding: utf-8 -*-
"""G0-C: pensions small sample (gestoras/fondos/planes), exact crosswalk only.

Sources: DGSFP RRPP (G/F/N/D keys, detail GET with tipoOperador), BdE lista-pf-es.
EIOPA IORP register: HTTP 401 (documented); gestoras are insurers -> EIOPA
insurance register applies via LEI.
"""
import datetime
import hashlib
import json
import pathlib
import re
import html as H
import sys

import requests

sys.path.insert(0, "scripts")
from g0_lib import load_dgsfp, load_eiopa, load_gleif, diag_name_agree
from bde_loader import load_bde

B = "https://rrpp.dgsfp.mineco.es"
OUT = pathlib.Path("data/derived/g0c_checks.jsonl")
RAW = pathlib.Path("data/raw/dgsfp/rrpp_pensions")
RAW.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)", "Referer": B + "/"})
s.get(B + "/", timeout=60)

PAIR = re.compile(r'<label class="label-literal">([\s\S]*?)</label>\s*<label[^>]*>([\s\S]*?)</label>')


def detail(section, clave, tipo=None):
    params = {"culture": "es-ES", "ui-culture": "es-ES", "clave": clave}
    if tipo:
        params["tipoOperador"] = tipo
    r = s.get(f"{B}/{section}/Get{section}/", params=params, timeout=60)
    if r.status_code != 200 or "No se han encontrado datos" in r.text:
        return None
    fn = RAW / f"{clave.strip()}.html"
    fn.write_bytes(r.content)
    pairs = PAIR.findall(r.text)
    d = {}
    for a, b in pairs:
        k = H.unescape(re.sub(r"<[^>]+>", " ", a)).strip()
        v = H.unescape(re.sub(r"<[^>]+>", " ", b)).strip()
        if k and k not in d:
            d[k] = v
    meta = {
        "source_url": r.url,
        "http_status": r.status_code,
        "content_sha256": hashlib.sha256(r.content).hexdigest(),
        "bytes": len(r.content),
        "retrieved_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "raw_file": str(fn).replace("\\", "/"),
        "parser_version": "rrpp_detail_parser/0.2",
    }
    return d, meta


def main():
    gestoras = json.loads((pathlib.Path("data/raw/dgsfp/rrpp_gestoras.json")).read_bytes().decode("utf-8-sig"))
    fondos = json.loads((pathlib.Path("data/raw/dgsfp/rrpp_fondos.json")).read_bytes().decode("utf-8-sig"))
    depositarias = json.loads((pathlib.Path("data/raw/dgsfp/rrpp_depositarias.json")).read_bytes().decode("utf-8-sig"))
    bde_pf = load_bde("data/raw/bde/lista-pf-es.csv")
    bde_pf_by_lei = {r["LEI"].strip().upper(): r for r in bde_pf if r["LEI"].strip()}
    eiopa = load_eiopa()
    ei_home = {}
    for r in eiopa:
        if r["Home Country"] == "ES" and r["Cross border status"] == "Domestic undertaking":
            lei = r["LEI"].strip().upper()
            if lei:
                ei_home[lei] = r
    gleif = load_gleif()

    # sample selection: 3 gestoras (by known insurer names), 5 fondos, 3 planes (N keys from earlier scan)
    sample_gest = [g for g in gestoras if any(k in g["descripcion"].upper() for k in
                    ("ABANCA VIDA", "MEDVIDA", "MAPFRE", "VIDACAIVA", "BBVA PENSIONES", "CAIXA"))][:3]
    if len(sample_gest) < 3:
        sample_gest = gestoras[:3]
    sample_fond = fondos[:: len(fondos) // 5][:5]
    sample_plan = ["N0002", "N0007", "N0012"]

    out = []
    for g in sample_gest:
        res = detail("Gestora", g["clave"])
        if not res:
            continue
        d, meta = res
        lei = next((v for k, v in d.items() if "LEI" in k.upper()), "")
        # gestoras are ES insurers: EIOPA domestic row by LEI
        ei = ei_home.get(lei.strip().upper())
        out.append({
            "gate": "G0-C", "unit": "gestora", "clave": g["clave"],
            "denominacion": d.get("Denominación:") or d.get("Denominacion:") or g["descripcion"],
            "DGSFP_MANAGER_KEY": True, "LEI": lei,
            "BDE_LEI_WHERE_AVAILABLE": lei.strip().upper() in bde_pf_by_lei if lei else False,
            "EIOPA_IORP_IDENTITY_WHERE_APPLICABLE": bool(ei),
            "EIOPA_HOME_ID": ei["Identification code"] if ei else None,
            "GLEIF_LEI_EXACT": lei.strip().upper() in gleif if lei else False,
            "EXACT_CROSSWALK_ONLY": True, "meta": meta,
        })
    for f in sample_fond:
        res = detail("Fondo", f["clave"], tipo="FONDO")
        if not res:
            out.append({"gate": "G0-C", "unit": "fondo", "clave": f["clave"], "detail": "NOT CAPTURED"})
            continue
        d, meta = res
        lei = next((v for k, v in d.items() if "LEI" in k.upper()), "")
        gest_key = next((v for k, v in d.items() if k.startswith("Clave Gestora")), "")
        gest_den = next((v for k, v in d.items() if k.startswith("Denominaci") and k != "Denominación:"), "")
        # the second Denominación occurrences: gestora and depositaria
        dens = [v for k, v in d.items() if k.startswith("Denominaci")]
        dep_key = next((v for k, v in d.items() if k.startswith("Clave Depositaria")), "")
        bde_row = bde_pf_by_lei.get(lei.strip().upper())
        out.append({
            "gate": "G0-C", "unit": "fondo", "clave": f["clave"],
            "denominacion": d.get("Denominación:") or f["denominacionFondo"],
            "DGSFP_FUND_KEY": True, "LEI": lei,
            "BDE_LEI_WHERE_AVAILABLE": bool(bde_row),
            "BDE_FUND_NAME": bde_row["NOMBRE"] if bde_row else None,
            "BDE_GESTORA_NAME": bde_row["NOMBRE DE LA GESTORA"] if bde_row else None,
            "diagnostic_gestora_name_vs_bde": (diag_name_agree(gest_den or (dens[1] if len(dens) > 1 else ""), bde_row["NOMBRE DE LA GESTORA"]) if bde_row else None),
            "GESTORA_KEY_EXACT": gest_key or None,
            "DEPOSITARIA_KEY_EXACT": dep_key or None,
            "EIOPA_IORP_IDENTITY_WHERE_APPLICABLE": None,  # IORP register 401
            "GLEIF_LEI_EXACT": lei.strip().upper() in gleif if lei else False,
            "EXACT_CROSSWALK_ONLY": True, "meta": meta,
        })
    for pk in ["N0002", "N0003", "N0007"]:
        res = detail("Plan", pk)
        if not res:
            out.append({"gate": "G0-C", "unit": "plan", "clave": pk, "detail": "NOT CAPTURED"})
            continue
        d, meta = res
        raw = (pathlib.Path("data/raw/dgsfp/rrpp_pensions") / f"{pk}.html").read_text(encoding="utf-8", errors="replace")
        fondo_keys = sorted(set(re.findall(r"\bF\d{4}\b", raw)))
        out.append({
            "gate": "G0-C", "unit": "plan", "clave": pk,
            "denominacion": next((v for k, v in d.items() if "Denominaci" in k and v), "?"),
            "DGSFP_PLAN_KEY": True,
            "FONDO_KEY_EXACT": fondo_keys or None,
            "GESTORA_KEY_EXACT": None,
            "LEI": "",  # plans do not carry LEI (not legal entities for identity fabric purposes)
            "EIOPA_IORP_IDENTITY_WHERE_APPLICABLE": None,
            "EXACT_CROSSWALK_ONLY": True, "meta": meta,
        })
    with OUT.open("w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    for r in out:
        print(json.dumps({k: r.get(k) for k in ("gate", "unit", "clave", "denominacion", "LEI",
                                                "BDE_LEI_WHERE_AVAILABLE", "EIOPA_IORP_IDENTITY_WHERE_APPLICABLE",
                                                "EIOPA_HOME_ID", "GLEIF_LEI_EXACT", "GESTORA_KEY_EXACT",
                                                "FONDO_KEY_EXACT", "diagnostic_gestora_name_vs_bde")},
                         ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()
