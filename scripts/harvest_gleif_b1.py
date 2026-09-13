# -*- coding: utf-8 -*-
"""Harvest GLEIF records for B1 parent LEIs (from home BdE lists)."""
import json
import sys

sys.path.insert(0, "scripts")
from harvest_gleif import harvest

rows = [json.loads(l) for l in open("data/derived/g0b1_checks.jsonl", encoding="utf-8")]
# parent LEIs need to be re-derived: read from builder output
leis = []
for r in rows:
    # parent lei isn't stored; recompute quickly from home lists
    pass

# simpler: rebuild parent lei set directly
from bde_loader import load_bde, norm_dgsfp_key
from g0_lib import load_bde_home
bde_es = load_bde("data/raw/bde/lista-ic-es.csv")
HOME_LISTS = {"DE": "de", "FR": "fr", "LU": "lu", "IE": "ie", "BE": "be",
              "PT": "pt", "SE": "se", "IT": "it", "MT": "mt"}
for r in bde_es:
    if not r["CÓDIGO DE SUPERVISOR"].strip().startswith("E"):
        continue
    matriz = r["ENTIDAD MATRIZ"].strip()
    pre = matriz[:2]
    if pre in HOME_LISTS:
        home = load_bde_home(HOME_LISTS[pre])
        hits = [h for h in home if h["CÓDIGO EUROPEO"] == matriz]
        if hits and hits[0]["LEI"].strip():
            leis.append(hits[0]["LEI"].strip().upper())
        if hits and hits[0]["LEI"].strip() == "" and False:
            pass
print("parent LEIs to harvest:", len(set(leis)))
harvest(leis)
