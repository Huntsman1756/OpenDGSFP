# -*- coding: utf-8 -*-
import csv
import sys

sys.path.insert(0, "scripts")
from bde_loader import load_bde, norm_dgsfp_key
from g0_lib import load_bde_home, load_eiopa, load_gleif

bde_es = load_bde("data/raw/bde/lista-ic-es.csv")
eiopa = load_eiopa()
gleif = load_gleif()
HOME_LISTS = {"DE": "de", "FR": "fr", "LU": "lu", "IE": "ie", "BE": "be",
              "PT": "pt", "SE": "se", "IT": "it", "MT": "mt"}

for r in bde_es:
    if not r["CÓDIGO DE SUPercód".replace("ercód", "ERVISOR")].strip().startswith("E"):
        continue
    clave = norm_dgsfp_key(r["CÓDIGO DE SUPERVISOR"])
    matriz = r["ENTIDAD MATRIZ"].strip()
    pre = matriz[:2]
    if pre not in HOME_LISTS:
        continue
    home = load_bde_home(HOME_LISTS[pre])
    hits = [h for h in home if h["CÓDIGO EUROPEO"] == matriz]
    if not (hits and hits[0]["LEI"].strip()):
        continue
    plei = hits[0]["LEI"].strip().upper()
    ei_rows = [x for x in eiopa if x["LEI"].strip().upper() == plei
               and x["EU Country where the entity operates"].strip() == "ES"]
    es_branch = [x for x in ei_rows if x["Cross border status"] == "EEA branch"]
    if es_branch:
        continue
    print(f"{clave} parentLEI={plei}")
    print("   parent:", hits[0]["NOMBRE"][:55], "| gleif:", gleif.get(plei, {}).get("legalName", "?")[:45],
          "| status:", gleif.get(plei, {}).get("entityStatus"))
    for x in ei_rows:
        print("   EIOPA ES row:", x["Cross border status"], "| reg:", x["Registration start date"], "->", x["Registration end date"],
              "| op:", x["Operation Start Date"], "->", x["Operation End Date"])
    if not ei_rows:
        # any rows at all for this LEI?
        any_rows = [x for x in eiopa if x["LEI"].strip().upper() == plei]
        print("   EIOPA rows for LEI (any country):", len(any_rows),
              [(y['EU Country where the entity operates'], y['Cross border status']) for y in any_rows[:5]])
