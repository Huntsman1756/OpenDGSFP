# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "scripts")
from bde_loader import load_bde

es = load_bde("data/raw/bde/lista-ic-es.csv")
empty = [r for r in es if not r["CÓDIGO DE SUPERVISOR"].strip()]
print("rows with empty supervisor code:", len(empty))
for r in empty:
    print("  ", r["CÓDIGO EUROPEO"], "|", r["LEI"], "|", r["NOMBRE"][:60], "| matriz:", r["ENTIDAD MATRIZ"], "| tipo:", r["TIPO DE SEGURO"])
