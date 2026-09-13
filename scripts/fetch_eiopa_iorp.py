# -*- coding: utf-8 -*-
"""EIOPA IORP register: locate export target and fetch (donor mechanism)."""
import datetime
import hashlib
import json
import pathlib
import re
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

URL = "https://register.eiopa.europa.eu/registers/register-of-iorps"
OUT = pathlib.Path("data/raw/eiopa/eiopa_iorp.csv")
MANIFEST = pathlib.Path("evidence/source-manifest.json")

cj = CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "opendgsfp-g0 (research)")]

page = op.open(URL, timeout=90).read().decode("utf-8", "replace")
pathlib.Path("data/raw/eiopa/iorp_page.html").write_text(page, encoding="utf-8")
targets = re.findall(r"ctl00\$ctl\d+\$g_[a-f0-9_]+\$lkbtnExport", page)
print("export targets:", targets[:3])


def field(name):
    m = re.search(r'id="%s" value="([^"]*)"' % name, page)
    return m.group(1) if m else None


if targets:
    data = {"__EVENTTARGET": targets[0], "__EVENTARGUMENT": ""}
    for f in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION", "__REQUESTDIGEST"):
        v = field(f)
        if v is not None:
            data[f] = v
    req = urllib.request.Request(URL, urllib.parse.urlencode(data).encode(), method="POST")
    resp = op.open(req, timeout=300)
    body = resp.read()
    disp = resp.headers.get("Content-Disposition", "")
    print("postback:", resp.status, len(body), disp[:80])
    if "attachment" in disp:
        OUT.write_bytes(body)
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        m.append({
            "source_system": "EIOPA_IORP",
            "source_url": URL,
            "method": "POST (ASP.NET postback replay, donor mechanism)",
            "jurisdiction": "EU/EEA",
            "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "content_sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body),
            "raw_file": str(OUT).replace("\\", "/"),
        })
        MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        print("saved", OUT)
else:
    print("no export target on IORP page — check page structure")
