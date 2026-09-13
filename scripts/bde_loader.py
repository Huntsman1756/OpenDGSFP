# -*- coding: utf-8 -*-
"""Canonical loader for BdE lista-ic / lista-pf CSV files."""
import csv
import re

def norm_key(k):
    return re.sub(r"\s+", " ", k).strip().upper()

def load_bde(path):
    with open(path, encoding="utf-8-sig") as f:
        rdr = csv.reader(f)
        header = next(rdr)
        cols = [norm_key(c) for c in header]
        rows = []
        for r in rdr:
            if not any(x.strip() for x in r):
                continue
            d = {cols[i]: (r[i] if i < len(r) else "").strip() for i in range(len(cols))}
            rows.append(d)
    return rows

def norm_dgsfp_key(code):
    """Normalize a BdE 'Código de supervisor' to a DGSFP clave (letter + 4 digits)."""
    c = re.sub(r"\s+", "", code).upper()
    m = re.match(r"^([A-Z]+)\s*0*(\d+)$", c)
    if not m:
        return c
    return f"{m.group(1)}{int(m.group(2)):04d}"
