# -*- coding: utf-8 -*-
"""Extract visible text + table structure from a RRPP detail page."""
import re, sys, html as H

p = sys.argv[1]
doc = open(p, encoding="utf-8").read()
# strip scripts/styles
doc = re.sub(r"<script[\s\S]*?</script>", " ", doc)
doc = re.sub(r"<style[\s\S]*?</style>", " ", doc)
# table cells and dt/dd
rows = re.findall(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", doc)
cells = [H.unescape(re.sub(r"<[^>]+>", " ", c)).strip() for c in rows]
cells = [c for c in cells if c]
print("TABLE CELLS:")
for c in cells:
    print(" |", c[:120])
# div labels pattern
labels = re.findall(r"<(?:label|dt|span|b|strong)[^>]*>\s*([^<>]{3,60})\s*</(?:label|dt|span|b|strong)>", doc)
print("\nLABELS:")
print(sorted(set(H.unescape(l).strip() for l in labels))[:80])
# any LEI-shaped strings
print("\nLEI-shaped strings:", re.findall(r"\b[0-9A-Z]{20}\b", doc)[:10])
# clave mentions
print("\nKey mentions:", re.findall(r"\b[CLMPR]?\d{4}[A-Z]?\b", doc)[:15])
