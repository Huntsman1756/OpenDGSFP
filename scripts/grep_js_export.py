# -*- coding: utf-8 -*-
import re

js = open("data/raw/dgsfp/site.min.js", encoding="utf-8").read()
print("--- export-like functions ---")
for m in re.finditer(r"function\s+(\w*(?:[Ee]xport|[Dd]escarg|\w*[Ii]nforme)\w*)\s*\(([^)]*)\)", js):
    print(m.group(0)[:160])
print("--- strings with export/descarga/excel/pdf/informe ---")
for u in sorted(set(re.findall(r"""["']([^"']{0,90}(?:xport|escarg|xcel|Pdf|PDF|nforme)[^"']{0,90})["']""", js))):
    print(u)
