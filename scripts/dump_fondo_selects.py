# -*- coding: utf-8 -*-
import re
import html as H

doc = open("data/raw/dgsfp/rrpp_fondo_page.html", encoding="utf-8").read()
for m in re.finditer(r"<select[^>]*>", doc):
    print(m.group(0)[:120])
print("=== selects with options ===")
for m in re.finditer(r'<select[^>]*id="([^"]+)"[\s\S]*?</select>', doc):
    opts = re.findall(r"<option[^>]*>", m.group(0))
    if opts:
        print("--", m.group(1))
        for o in opts[:8]:
            print("   ", H.unescape(o)[:100])
