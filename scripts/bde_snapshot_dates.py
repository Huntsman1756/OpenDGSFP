# -*- coding: utf-8 -*-
import re, html as H

for f, tag in [("data/raw/bde/bde_listas_seguros_page.html", "seguros"),
               ("data/raw/bde/bde_listas_fondospen_page.html", "fondos-pensiones"),
               ("data/raw/bde/bde_listas_instituciones_page.html", "instituciones")]:
    try:
        doc = open(f, encoding="utf-8").read()
    except FileNotFoundError:
        continue
    txt = H.unescape(re.sub(r"<[^>]+>", " ", doc))
    txt = re.sub(r"\s+", " ", txt)
    hits = re.findall(r"(?:[Uu]ltima(?:s)? actualizaci[oó]n(?:es)?|actualizado|Actualizado|fecha de (?:los )?datos)[^.|]{0,120}", txt)
    print("==", tag)
    for h in hits[:6]:
        print("   ", h.strip()[:140])
    # look for date-like patterns near 'lista'
    dts = re.findall(r"(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})", txt)
    print("   date-like tokens:", dts[:12])
