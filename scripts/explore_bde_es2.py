# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "scripts")
from bde_loader import load_bde, norm_dgsfp_key
import collections

es = load_bde("data/raw/bde/lista-ic-es.csv")
print("ES rows:", len(es), "| columns:", list(es[0].keys()))

e_rows = [r for r in es if r["CÓDIGO DE SUPERVISOR"].strip().startswith("E")]
print("\nrows with supervisor code starting E:", len(e_rows))
for r in e_rows[:14]:
    print("  ", norm_dgsfp_key(r["CÓDIGO DE SUPERVISOR"]), "|", r["CÓDIGO EUROPEO"], "|",
          r["NOMBRE"][:52], "| matriz:", r["ENTIDAD MATRIZ"], "| lei:", r["LEI"])

shapes = collections.Counter()
for r in es:
    c = r["CÓDIGO DE SUPERVISOR"].strip()
    shapes[(c[:1], len(c))] += 1 if c else 0
print("\nsupervisor (letter,len):", dict(shapes))

mv = collections.Counter()
for r in es:
    m = r["ENTIDAD MATRIZ"].strip()
    if m:
        mv[m[:2]] += 1
print("entidad matriz prefixes:", dict(mv))
lei = sum(1 for r in es if r["LEI"])
print("LEI present:", lei, "/", len(es))
