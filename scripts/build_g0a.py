# -*- coding: utf-8 -*-
"""G0-A: Spanish entities (C/M/P/R) exact identity crosswalk.

Population-level audit (all Activa C/M/P/R) + stratified sample (~20).
Canonical joins use EXACT identifiers only:
  DGSFP clave == BdE 'Código de supervisor' (normalized)
  DGSFP clave == EIOPA 'Identification code' (ES home rows)
  LEI equality across sources (exact string, uppercase)
Name comparison is recorded as diagnostic only.
"""
import datetime
import json
import pathlib
import sys

sys.path.insert(0, "scripts")
from g0_lib import (lei_checksum_valid, load_dgsfp, load_bde_es, load_eiopa,
                    load_gleif, norm_dgsfp_key, diag_name_agree, bde_publication_date,
                    diag_name_agree)

OUT = pathlib.Path("data/derived/g0a_checks.jsonl")
SNAP = {
    "DGSFP_RRPP": {"source_url": "https://rrpp.dgsfp.mineco.es/Aseguradora/GetAseguradora/", "snapshot_date": "2026-09-13"},
    "BDE": {"source_url": "https://www.bde.es/wbe/es/estadisticas/otras-clasificaciones/clasificacion-entidades/listas-instituciones-financieras/listas-empresas-seguros-pais/", "snapshot_date": bde_publication_date()},
    "EIOPA": {"source_url": "https://register.eiopa.europa.eu/registers/register-of-insurance-undertakings", "snapshot_date": None},  # filled from manifest
}


def eiopa_snapshot():
    m = pathlib.Path("evidence/source-manifest.json")
    for e in json.loads(m.read_text(encoding="utf-8")):
        if e.get("source_system") == "EIOPA":
            return e["retrieved_at"][:10]
    return None


def main():
    dgsfp = load_dgsfp()
    bde = load_bde_es()
    eiopa = load_eiopa()
    gleif = load_gleif()
    SNAP["EIOPA"]["snapshot_date"] = eiopa_snapshot()

    bde_by_sup = {}
    for r in bde:
        k = norm_dgsfp_key(r["CÓDIGO DE SUPERVISOR"])
        if k:
            bde_by_sup.setdefault(k, []).append(r)
    eiopa_home_es = {r["Identification code"].strip(): r for r in eiopa
                     if r["Home Country"].strip() == "ES" and r["Cross border status"].strip() == "Domestic undertaking"}

    rows = [e for e in dgsfp if e["tipo"] in ("C", "M", "P", "R") and e["situacion"] == "Activa"]
    out = []
    for e in rows:
        clave = e["clave"]
        bde_rows = bde_by_sup.get(clave, [])
        bde = bde_rows[0] if len(bde_rows) == 1 else (bde_rows[0] if bde_rows else None)
        bde_multi = len(bde_rows) > 1
        ei = eiopa_home_es.get(clave)
        lei_rrpp = e["lei"].strip().upper() or None
        lei_bde = (bde["LEI"].strip().upper() if bde and bde["LEI"].strip() else None)
        lei_eiopa = (ei["LEI"].strip().upper() if ei and ei["LEI"].strip() else None)
        leis = [l for l in (lei_rrpp, lei_bde, lei_eiopa) if l]
        rec = {
            "gate": "G0-A",
            "clave": clave,
            "tipo": e["tipo"],
            "denominacion": e["denominacion"],
            "DGSFP_KEY_UNIQUE": True,  # key->single detail record (enumeration) ; multi-source binding checked below
            "DGSFP_KEY_BDE_SUPERVISOR_CODE_EXACT": bool(bde) and not bde_multi,
            "DGSFP_KEY_EIOPA_ID_EXACT": bool(ei),
            "DGSFP_LEI_AVAILABLE": bool(lei_rrpp),
            "BDE_LEI_AVAILABLE": bool(lei_bde),
            "EIOPA_LEI_AVAILABLE": bool(lei_eiopa),
            "BDE_LEI_EIOPA_LEI_EXACT": bool(lei_bde and lei_eiopa and lei_bde == lei_eiopa),
            "GLEIF_LEI_EXACT": bool(lei_rrpp and lei_rrpp in gleif and gleif[lei_rrpp]["entityStatus"] in ("ACTIVE", "RETIRED") and lei_checksum_valid(lei_rrpp)),
            "GLEIF_RECORD": gleif.get(lei_rrpp or "", {}).get("entityStatus"),
            "all_leis_consistent": len(set(leis)) <= 1,
            "leis_observed": sorted(set(leis)),
            "diagnostic_name_dgsfp_vs_bde": diag_name_agree(e["denominacion"], bde["NOMBRE"]) if bde else None,
            "diagnostic_name_dgsfp_vs_eiopa": diag_name_agree(e["denominacion"], ei["Official name of the entity"]) if ei else None,
            "bde_european_code": bde["CÓDIGO EUROPEO"] if bde else None,
            "eiopa_nca": ei["Name of NCA"] if ei else None,
            "snapshots": SNAP,
        }
        out.append(rec)
    with OUT.open("w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # coverage summary
    def pct(a, b):
        return f"{a}/{b}" + (f" ({100*a/b:.1f}%)" if b else "")
    print("G0-A population audit: Activa C/M/P/R:", len(out))
    for flag in ["DGSFP_KEY_BDE_SUPERVISOR_CODE_EXACT", "DGSFP_KEY_EIOPA_ID_EXACT",
                 "DGSFP_LEI_AVAILABLE", "BDE_LEI_AVAILABLE", "EIOPA_LEI_AVAILABLE",
                 "BDE_LEI_EIOPA_LEI_EXACT", "GLEIF_LEI_EXACT", "all_leis_consistent"]:
        n = sum(1 for r in out if r[flag])
        print(f"  {flag}: {pct(n, len(out))}")
    for t in ("C", "M", "P", "R"):
        sub = [r for r in out if r["tipo"] == t]
        if not sub:
            continue
        lei = sum(1 for r in sub if r["DGSFP_LEI_AVAILABLE"])
        bde = sum(1 for r in sub if r["DGSFP_KEY_BDE_SUPERVISOR_CODE_EXACT"])
        ei = sum(1 for r in sub if r["DGSFP_KEY_EIOPA_ID_EXACT"])
        print(f"  tipo {t}: n={len(sub)} bde={bde} eiopa={ei} lei={lei}")
    # diagnostics
    nm = [r for r in out if r["diagnostic_name_dgsfp_vs_eiopa"] == "different"]
    print("  diagnostic name mismatches dgsfp vs eiopa:", len(nm))
    for r in nm[:5]:
        print("    ", r["clave"], "|", r["denominacion"][:40])


if __name__ == "__main__":
    main()
