# -*- coding: utf-8 -*-
import re, sys
import html as H

doc = open(sys.argv[1], encoding="utf-8").read()
pairs = re.findall(r'<label class="label-literal">([\s\S]*?)</label>\s*<label[^>]*aria-label="([^"]*)"[^>]*>([\s\S]*?)</label>', doc)
for lit, aria, val in pairs[:40]:
    v = H.unescape(re.sub(r"<[^>]+>", " ", val)).strip()
    lit2 = H.unescape(re.sub(r"<[^>]+>", " ", lit)).strip()
    print(lit2, "=>", H.unescape(aria), "=>", v[:90])
print("---- tab titles ----")
for m in re.finditer(r'data-toggle="tab"[^>]*>([^<]+)', doc):
    print("tab:", H.unescape(m.group(1)).strip())
print("---- any LEI 20-char ----")
print(re.findall(r"\b[0-9A-Z]{20}\b", doc)[:6])
