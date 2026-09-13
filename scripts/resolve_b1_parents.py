# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "scripts")
from bde_loader import load_bde, norm_dgsfp_key

# parent ids observed in lista-ic-es.csv for E-rows
es = load_bde("data/raw/bde/lista-ic-es.csv")
e_rows = [r for r in es if r["CÓDIGO DE SUPERVISOR"].strip().startswith("E")]
parents = [(norm_dgsfp_key(r["CÓDIGO DE SUPERVISOR"]), r["ENTIDAD MATRIZ"], r["NOMBRE"], r["LEI"])
           for r in e_rows if r["ENTIDAD MATRIZ"].strip()]
print("branches with parent id:", len(parents), "/", len(e_rows))

# group by country prefix of parent id
import collections
by_ctry = collections.Counter(p[1][:2] for p in parents)
print("parent country prefixes:", dict(by_ctry))

ctry_map = {"DE": "de", "FR": "fr", "LU": "lu", "IE": "ie", "BE": "be", "PT": "pt",
            "GB": "gb", "SE": "se", "IT": "it", "MT": "mt", "MX": None, "LI": "li"}

lists = {}
for pre, code in [("DE", "de"), ("FR", "fr"), ("LU", "lu"), ("IE", "ie"), ("BE", "be"),
                  ("PT", "pt"), ("SE", "se"), ("IT", "it"), ("MT", "mt"), ("LI", "li")]:
    try:
        lists[pre] = load_bde(f"data/raw/bde/lista-ic-{code}.csv")
        print(f"loaded {pre}: {len(lists[pre])} rows | cols: {list(lists[pre][0].keys())[:7]}")
    except FileNotFoundError:
        print(f"no list for {pre}")

# try to resolve each parent id into its home list: match against CÓDIGO EUROPEO first
resolved, unresolved = 0, []
for bkey, pid, bname, blei in parents:
    pre = pid[:2]
    lst = lists.get(pre)
    if not lst:
        unresolved.append((bkey, pid, bname, "no home list"))
        continue
    hit = [r for r in lst if r["CÓDIGO EUROPEO"] == pid]
    if not hit:
        # try supervisor code column too
        hit = [r for r in lst if norm_dgsfp_key(r["CÓDIGO DE SUPERVISOR"]) == pid]
    if hit:
        h = hit[0]
        resolved += 1
        if resolved <= 20:
            print(f"  RESOLVED {bkey} -> {pid} | parent: {h['NOMBRE'][:50]} | LEI: {h['LEI']} | code: {h['CÓDIGO EUROPEO']}")
    else:
        unresolved.append((bkey, pid, bname, "not in home list"))
print("\nresolved:", resolved, "unresolved:", len(unresolved))
for u in unresolved:
    print("  UNRESOLVED", u[0], u[1], u[2][:50], "|", u[3])
