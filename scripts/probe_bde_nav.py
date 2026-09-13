# -*- coding: utf-8 -*-
import requests, re

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)"})
for url in ["https://www.bde.es/wbe/es/datos/",
            "https://www.bde.es/wbe/es/datos/estadisticas/",
            "https://www.bde.es/wbe/es/estadisticas/"]:
    try:
        r = s.get(url, timeout=60)
        print("==", url, r.status_code, len(r.text))
        if r.status_code == 200:
            hits = sorted(set(re.findall(r'href="([^"]*entidad[^"]*)"', r.text, re.I)))
            for h in hits:
                print("   ", h[:130])
            hits2 = sorted(set(re.findall(r'href="([^"]*(?:segur|reaseg)[^"]*)"', r.text, re.I)))
            for h in hits2:
                print("  S", h[:130])
    except Exception as e:
        print("==", url, "EXC", str(e)[:100])
