# -*- coding: utf-8 -*-
"""Diagnose B2 residuals: EIOPA home miss, country mismatches, no-ES-op cases."""
import json
import collections

rows = [json.loads(l) for l in open("data/derived/g0b2_checks.jsonl", encoding="utf-8") if json.loads(l)["situacion"] == "Activa"]

miss = [r for r in rows if r["LEI"] and not r["EIOPA_HOME_EXACT_BY_LEI"]]
print("=== LEI present but no EIOPA home row:", len(miss))
for r in miss:
    print("  ", r["clave"], r["pais_origen"], r["LEI"], "|", r["denominacion"][:50])

cmiss = [r for r in rows if r["EIOPA_HOME_EXACT_BY_LEI"] and r["EIOPA_HOME_COUNTRY_MATCH"] is False]
print("=== country mismatch (RRPP pais_origen vs EIOPA Home Country):", len(cmiss))
for r in cmiss:
    print("  ", r["clave"], "| RRPP:", r["pais_origen"], "| EIOPA:", r["EIOPA_HOME_NCA"], "| id:", r["EIOPA_HOME_ID_CODE"], "|", r["denominacion"][:45])

nm = [r for r in rows if r["EIOPA_HOME_EXACT_BY_LEI"] and r["diagnostic_name_dgsfp_vs_eiopa"] == "different"]
print("=== name diagnostic mismatches among LEI-joined:", len(nm))
for r in nm[:10]:
    print("  ", r["clave"], "| DGSFP:", r["denominacion"][:42], "| EIOPA:", (r.get("diagnostic_name_dgsfp_vs_eiopa"),))

no_es = [r for r in rows if r["EIOPA_HOME_EXACT_BY_LEI"] and not r["EIOPA_ES_OPERATION_PRESENT"]]
print("=== LEI-joined to EIOPA home but no ES operation row:", len(no_es))
cc = collections.Counter(r["pais_origen"] for r in no_es)
print("  by country:", dict(cc))
for r in no_es[:6]:
    print("  ", r["clave"], r["pais_origen"], "|", r["denominacion"][:45], "| EIOPA id:", r["EIOPA_HOME_ID_CODE"])
