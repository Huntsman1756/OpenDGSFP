# -*- coding: utf-8 -*-
"""G0-B2: LPS entities (L-keys) — the critical gate.

Canonical path (exact identifiers only):
  DGSFP L-key --(LEI published in RRPP detail, exact)--> EIOPA home undertaking
             --(LEI exact)--> GLEIF
Non-canonical candidates (name/country only) are recorded as DOCUMENTED_GAP.
Counting units kept separate:
  DGSFP L-keys = LPS registrations in ES
  EIOPA 'EEA FPS' rows = cross-border operations into ES
"""
import collections
import json
import pathlib
import sys

sys.path.insert(0, "scripts")
from g0_lib import (load_dgsfp, load_eiopa, load_gleif, lei_checksum_valid,
                    diag_name_agree, bde_publication_date)

OUT = pathlib.Path("data/derived/g0b2_checks.jsonl")


def main():
    dgsfp = [e for e in load_dgsfp() if e["tipo"] == "L"]
    eiopa = load_eiopa()
    gleif = load_gleif()

    # EIOPA home undertaking rows keyed by LEI
    ei_home_by_lei = {}
    for r in eiopa:
        if r["Cross border status"].strip() == "Domestic undertaking":
            lei = r["LEI"].strip().upper()
            if lei:
                ei_home_by_lei.setdefault(lei, []).append(r)
    # EIOPA ES operations (FTS) keyed by LEI
    ei_es_ops = collections.defaultdict(list)
    for r in eiopa:
        if (r["EU Country where the entity operates"].strip() == "ES"
                and r["Cross border status"].strip() in ("EEA FPS", "FPS for EEA Branches")):
            lei = r["LEI"].strip().upper()
            if lei:
                ei_es_ops[lei].append(r)

    out = []
    for e in dgsfp:
        lei = e["lei"].strip().upper() or None
        homes = ei_home_by_lei.get(lei, []) if lei else []
        home = homes[0] if len(homes) == 1 else (homes[0] if homes else None)
        country_ok = None
        if home and e["pais_origen"]:
            import unicodedata
            po = unicodedata.normalize("NFKD", e["pais_origen"])
            po = "".join(c for c in po if not unicodedata.combining(c))
            ctry = {"Alemania": "DE", "Francia": "FR", "Irlanda": "IE", "Luxemburgo": "LU",
                    "Belgica": "BE", "Malta": "MT", "Paises Bajos": "NL", "Suecia": "SE",
                    "Italia": "IT", "Liechtenstein": "LI", "Portugal": "PT", "Austria": "AT",
                    "Dinamarca": "DK", "Finlandia": "FI", "Grecia": "EL", "Hungria": "HU",
                    "Noruega": "NO", "Polonia": "PL", "Reino Unido": "GB", "Chipre": "CY",
                    "Croacia": "HR", "Eslovaquia": "SK", "Eslovenia": "SI", "Bulgaria": "BG",
                    "Republica Checa": "CZ", "Rumania": "RO", "Estonia": "EE", "Letonia": "LV",
                    "Lituania": "LT", "Islandia": "IS", "Espana": "ES"}.get(po)
            country_ok = (home["Home Country"].strip() == ctry) if ctry else None
        ops = ei_es_ops.get(lei, []) if lei else []
        g = gleif.get(lei or "", {})
        rec = {
            "gate": "G0-B2",
            "clave": e["clave"],
            "denominacion": e["denominacion"],
            "pais_origen": e["pais_origen"],
            "situacion": e["situacion"],
            "RRPP_L_KEY_EXPOSED_LIVE": True,
            "RRPP_L_EXPORT_FIELDS": "clave,denominacion,pais_origen,lei,nif,situacion,direccion,fechas",
            "RRPP_L_DETAIL_FIELDS": "same (no server-side bulk export; SPA client-side export only)",
            "RRPP_L_LEI_AVAILABLE": bool(lei),
            "LEI": lei,
            "EIOPA_HOME_EXACT_BY_LEI": bool(home),
            "EIOPA_HOME_COUNTRY_MATCH": country_ok,
            "EIOPA_HOME_ID_CODE": home["Identification code"] if home else None,
            "EIOPA_HOME_NCA": home["Name of NCA"] if home else None,
            "EIOPA_HOME_LEI": (home["LEI"].strip().upper() if home else None),
            "EIOPA_ES_OPERATION_PRESENT": bool(ops),
            "GLEIF_LEI_EXACT": bool(lei and lei in gleif and lei_checksum_valid(lei)),
            "gleif_status": g.get("entityStatus"),
            "diagnostic_name_dgsfp_vs_eiopa": diag_name_agree(e["denominacion"], home["Official name of the entity"]) if home else None,
            "crosswalk_result": ("PASS_EXACT" if (lei and home and country_ok and ops)
                                 else "PASS_EXACT_NO_ES_OP" if (lei and home)
                                 else "DOCUMENTED_GAP_NO_EXACT_ID"),
            "snapshots": {
                "DGSFP_RRPP": {"snapshot_date": "2026-09-13"},
                "EIOPA": {"snapshot_date": "2026-09-13"},
            },
        }
        out.append(rec)
    with OUT.open("w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    act = [r for r in out if r["situacion"] == "Activa"]
    def pct(flag, rows):
        n = sum(1 for r in rows if r[flag])
        return f"{n}/{len(rows)}" + (f" ({100*n/len(rows):.1f}%)" if rows else "")
    print("DGSFP L-keys total:", len(out), "| Activa:", len(act))
    print("Activa metrics:")
    print("  RRPP_L_LEI_AVAILABLE:", pct("RRPP_L_LEI_AVAILABLE", act))
    print("  EIOPA_HOME_EXACT_BY_LEI:", pct("EIOPA_HOME_EXACT_BY_LEI", act))
    print("  EIOPA_HOME_COUNTRY_MATCH (among LEI+home):",
          pct("EIOPA_HOME_COUNTRY_MATCH", [r for r in act if r["EIOPA_HOME_EXACT_BY_LEI"]]))
    print("  EIOPA_ES_OPERATION_PRESENT:", pct("EIOPA_ES_OPERATION_PRESENT", act))
    print("  GLEIF_LEI_EXACT:", pct("GLEIF_LEI_EXACT", act))
    print("  results:", dict(collections.Counter(r["crosswalk_result"] for r in act)))
    print("  diagnostic name mismatch (LEI-joined):",
          sum(1 for r in act if r["diagnostic_name_dgsfp_vs_eiopa"] == "different"))
    # counting units
    print("Counting units: DGSFP L Activa =", len(act),
          "| EIOPA unique LEIs with ES FTS op =", len(ei_es_ops))


if __name__ == "__main__":
    main()
