# -*- coding: utf-8 -*-
import csv, collections

def load(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))

es = load("data/raw/bde/lista-ic-es.csv")
print("ES rows:", len(es))
print("columns:", list(es[0].keys()))

# rows whose supervisor code starts with E (EEE branches)
e_rows = [r for r in es if r["CÓDIGO DE SUPERVISOR"].strip().startswith("E")]
print("\nrows with supervisor code starting E:", len(e_rows))
for r in e_rows[:12]:
    print("  ", r["CÓDIGO DE SUPERVISOR"].strip(), "|", r["CÓDIGO EUROPEO"].strip(), "|",
          r["NOMBRE"][:55], "| matriz:", r["ENTIDAD MATRIZ"].strip(), "| lei:", r["LEI"].strip())

# distribution of supervisor code shapes
shapes = collections.Counter()
for r in es:
    c = r["CÓDIGO DE SUPERVISOR"].strip()
    if not c:
        shapes["<empty>"] += 1
        continue
    pref = c[:2] if not c[0].isalpha() else c[0]
    shapes[(c[0], len(c))] += 1
print("\nsupervisor code (letter,len) distribution:", dict(shapes))

# entidad matriz values across the ES file
mv = collections.Counter()
for r in es:
    m = r["ENTIDAD MATRIZ"].strip()
    if m:
        mv[m[:2]] += 1
print("entidad matriz prefixes:", dict(mv))

# LEI coverage in ES list
lei = sum(1 for r in es if r["LEI"].strip())
print("LEI present:", lei, "/", len(es))
