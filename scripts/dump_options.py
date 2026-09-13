# -*- coding: utf-8 -*-
import re
html = open("data/raw/dgsfp/rrpp_home_2026-09-13.html", encoding="utf-8").read()
for sid in ["cmbOperadorClave", "Situacion", "cmbAmbito", "cmbTiposEntidades", "cmbPaisesOrg", "cmbOperadorDescripcion", "cmbActividades"]:
    m = re.search(r'<select[^>]*id="%s"[\s\S]*?</select>' % sid, html)
    if m:
        print("==== %s ====" % sid)
        for om in re.finditer(r"<option[^>]*>", m.group(0)):
            print(om.group(0)[:140])
