# -*- coding: utf-8 -*-
"""Probe pension + mediador sections of the RRPP SPA."""
import re
import requests

BASE = "https://rrpp.dgsfp.mineco.es"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)"})
for sec in ["Gestora", "Fondo", "Plan", "Depositaria", "Mediador", "CCAA"]:
    r = s.get(f"{BASE}/{sec}", timeout=60)
    if r.status_code != 200:
        print(sec, "HTTP", r.status_code)
        continue
    urls = sorted(set(re.findall(r'url:\s*[\'"]([^\'"]+)[\'"]', r.text)))
    title = re.search(r"<title>([^<]*)", r.text)
    print(f"== /{sec} [{title.group(1) if title else '?'}] endpoints:", urls)
    init = re.findall(r"initVistaBuscador\(([^)]*)\)", r.text)
    if init:
        print("   initVistaBuscador args:", init[0][:200])
    detail = re.findall(r"loadDetalle\s*=\s*function|urlVerDetalle", r.text)
    # form fields
    forms = re.findall(r'<form id="([^"]+)"', r.text)
    print("   forms:", forms)
    open(f"data/raw/dgsfp/rrpp_{sec.lower()}_page.html", "w", encoding="utf-8").write(r.text)
