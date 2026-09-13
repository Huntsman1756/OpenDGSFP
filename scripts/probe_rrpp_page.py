# -*- coding: utf-8 -*-
"""Probe the DGSFP RRPP SPA: extract endpoints from page HTML."""
import re, sys, json

html = open(sys.argv[1], encoding="utf-8").read()
print("=== inline url: patterns ===")
for u in sorted(set(re.findall(r"""url:\s*['"]([^'"]+)['"]""", html))):
    print(u)
print("=== relative paths in quotes ===")
for u in sorted(set(re.findall(r"""['"](/[A-Za-z][^'"]{2,80})['"]""", html))):
    if not u.endswith((".js", ".css", ".png", ".ico", ".jpg", ".woff", ".woff2", ".svg", ".gif")):
        print(u)
print("=== href/src non-asset ===")
for u in sorted(set(re.findall(r"""(?:src|href)=['"]([^'"#][^'"]*)['"]""", html))):
    if not u.endswith((".js", ".css", ".png", ".ico", ".jpg", ".woff", ".woff2", ".svg", ".gif")) and not u.startswith(("http", "mailto", "javascript")):
        print(u)
print("=== jqGrid / ajax calls ===")
for m in re.findall(r"""(?:\$\.get|\$\.post|\$\.getJSON|\.jqGrid)\s*\(\s*['"]([^'"]+)['"]""", html):
    print(m)
print("=== exported/fetch keywords ===")
for m in re.findall(r"""(fetch\(|XMLHttpRequest|Exportar|export|Excel|PDF|Descargar|Descarga)""", html)[:40]:
    print(m)
