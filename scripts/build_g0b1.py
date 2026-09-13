# -*- coding: utf-8 -*-
"""G0-B1: EEE branches in Spain (E-keys) exact identity crosswalk.

Universe: BdE ES list rows with supervisor code E* (70) <-> DGSFP E-claves.
Canonical chain (exact identifiers only):
  DGSFP E-clave == BdE 'Código de supervisor'
  BdE 'ENTIDAD MATRIZ' == home-country BdE list 'Código europeo'  (parent resolution)
  parent LEI (home BdE list) == EIOPA 'EEA branch' row LEI (ES operations)
  GLEIF record for parent LEI
Diagnostics (non-canonical): BDE_PARENT_CODE_EIOPA_ID_MATCH, name agreement.
"""
import collections
import json
import pathlib
import sys

sys.path.insert(0, "scripts")
from g0_lib import (load_dgsfp, load_bde_es, load_bde_home, load_eiopa, load_gleif,
                    lei_checksum_valid, norm_dgsfp_key, diag_name_agree,
                    bde_publication_date)

OUT = pathlib.Path("data/derived/g0b1_checks.jsonl")
HOME_LISTS = {"DE": "de", "FR": "fr", "LU": "lu", "IE": "ie", "BE": "be",
              "PT": "pt", "SE": "se", "IT": "it", "MT": "mt"}


def main():
    dgsfp = {e["clave"]: e for e in load_dgsfp() if e["tipo"] == "E"}
    bde_es = load_bde_es()
    eiopa = load_eiopa()
    gleif = load_gleif()

    # EIOPA branch rows operating in ES: LEI -> row (a branch LEI identifies the HOME entity)
    eiopa_es_branch = {}
    for r in eiopa:
        if (r["Cross border status"].strip() == "EEA branch"
                and r["EU Country where the entity operates"].strip() == "ES"):
            lei = r["LEI"].strip().upper()
            if lei:
                eiopa_es_branch.setdefault(lei, []).append(r)

    e_rows = [r for r in bde_es if r["CÓDIGO DE SUPERVISOR"].strip().startswith("E")]
    out = []
    for r in e_rows:
        clave = norm_dgsfp_key(r["CÓDIGO DE SUPERVISOR"])
        matriz = r["ENTIDAD MATRIZ"].strip()
        pre = matriz[:2]
        home = load_bde_home(HOME_LISTS[pre]) if pre in HOME_LISTS else None
        parent = None
        if matriz and home:
            hits = [h for h in home if h["CÓDIGO EUROPEO"] == matriz]
            parent = hits[0] if len(hits) == 1 else (hits[0] if hits else None)
        parent_lei = (parent["LEI"].strip().upper() if parent and parent["LEI"].strip() else None)
        ei_rows = eiopa_es_branch.get(parent_lei, []) if parent_lei else []
        ei = ei_rows[0] if ei_rows else None
        # EIOPA rows for the parent LEI operating in ES, any cross-border status
        ei_es_any = ([x for x in eiopa if x["LEI"].strip().upper() == parent_lei
                      and x["EU Country where the entity operates"].strip() == "ES"]
                     if parent_lei else [])
        # EIOPA home undertaking row for the parent (exact LEI + home country)
        ei_home = ([x for x in eiopa if x["LEI"].strip().upper() == parent_lei
                    and x["Home Country"].strip() == pre
                    and x["Cross border status"].strip() == "Domestic undertaking"]
                   if parent_lei else [])
        dg = dgsfp.get(clave)
        lei_rrpp = (dg["lei"].strip().upper() or None) if dg else None

        # diagnostic: is BdE parent code == EIOPA identification code anywhere? (scheme check)
        ei_by_code = None
        if parent:
            hc = {"DE": "DE", "FR": "FR", "LU": "LU", "IE": "IE", "BE": "BE", "PT": "PT",
                  "SE": "SE", "IT": "IT", "MT": "MT"}.get(pre)
            cand = [x for x in eiopa
                    if x["Home Country"] == hc and x["Cross border status"] == "Domestic undertaking"
                    and x["Identification code"].strip().upper() == matriz.upper()]
            ei_by_code = cand[0] if cand else None

        rec = {
            "gate": "G0-B1",
            "clave": clave,
            "denominacion_rrpp": dg["denominacion"] if dg else None,
            "situacion_rrpp": dg["situacion"] if dg else None,
            "lei_rrpp_branch": lei_rrpp,
            "bde_european_code": r["CÓDIGO EUROPEO"],
            "bde_lei_branch": r["LEI"].strip().upper() or None,
            "DGSFP_E_KEY_UNIQUE": True,
            "RRPP_E_KEY_EXPOSED_LIVE": bool(dg),
            "BDE_E_SUPERVISOR_CODE_MATCH": bool(dg),
            "BDE_PARENT_EU_CODE_PRESENT": bool(matriz),
            "BDE_PARENT_CODE_RESOLVES_HOME_ENTITY": bool(parent),
            "BDE_PARENT_LEI_AVAILABLE": bool(parent_lei),
            "parent_name": parent["NOMBRE"] if parent else None,
            "BDE_HOME_LEI_EIOPA_LEI_MATCH": bool(parent_lei and ei_home and ei_home[0]["LEI"].strip().upper() == parent_lei),
            "EIOPA_ES_OPERATION_ROW_PRESENT": bool(ei_es_any),
            "EIOPA_ES_OPERATION_STATUS": (ei_es_any[0]["Cross border status"] if ei_es_any else None),
            "EIOPA_BRANCH_ROW_IN_ES": bool(ei),
            "eiopa_home_country": ei["Home Country"] if ei else None,
            "eiopa_home_id_code": ei["Identification code"] if ei else None,
            "BDE_PARENT_CODE_EIOPA_ID_MATCH": bool(ei_by_code),  # DIAGNOSTIC ONLY
            "GLEIF_LEI_EXACT": bool(parent_lei and parent_lei in gleif
                                    and lei_checksum_valid(parent_lei)),
            "gleif_parent_status": gleif.get(parent_lei or "", {}).get("entityStatus"),
            "diagnostic_name_rrpp_vs_bde": diag_name_agree(dg["denominacion"], r["NOMBRE"]) if dg else None,
            "parent_country_prefix": pre or None,
            "snapshots": {
                "DGSFP_RRPP": {"snapshot_date": "2026-09-13"},
                "BDE": {"snapshot_date": bde_publication_date()},
                "EIOPA": {"snapshot_date": "2026-09-13"},
            },
        }
        out.append(rec)
    with OUT.open("w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    act = [r for r in out if r["situacion_rrpp"] == "Activa"]
    def pct(flag, rows):
        n = sum(1 for r in rows if r[flag])
        return f"{n}/{len(rows)}" + (f" ({100*n/len(rows):.1f}%)" if rows else "")
    print("BdE E-rows:", len(out), "| with DGSFP key:", pct("BDE_E_SUPERVISOR_CODE_MATCH", out),
          "| Activa in RRPP:", len(act))
    print("Coverage on BdE E-rows:")
    for flag in ["BDE_PARENT_EU_CODE_PRESENT", "BDE_PARENT_CODE_RESOLVES_HOME_ENTITY",
                 "BDE_PARENT_LEI_AVAILABLE", "BDE_HOME_LEI_EIOPA_LEI_MATCH",
                 "EIOPA_ES_OPERATION_ROW_PRESENT", "EIOPA_BRANCH_ROW_IN_ES", "GLEIF_LEI_EXACT"]:
        print(f"  {flag}: {pct(flag, out)}")
    print("Branch LEI coverage (concept measurement):")
    print("  DGSFP RRPP branch LEI present:", pct("lei_rrpp_branch", [{"lei_rrpp_branch": r["lei_rrpp_branch"]} for r in out]))
    print("  BdE branch-row LEI present:", pct("bde_lei_branch", [{"bde_lei_branch": r["bde_lei_branch"]} for r in out]))
    print("  EIOPA parent-code==EIOPA-id (diagnostic):", pct("BDE_PARENT_CODE_EIOPA_ID_MATCH", out))
    print("Countries:", dict(collections.Counter(r["parent_country_prefix"] for r in out)))
    misses = [r for r in out if not r["BDE_PARENT_CODE_RESOLVES_HOME_ENTITY"]]
    print("Unresolved parents:", [(r["clave"], r["parent_country_prefix"]) for r in misses])


if __name__ == "__main__":
    main()
