# -*- coding: utf-8 -*-
"""EIOPA Register of Insurance Undertakings bulk CSV export.

Mechanism reused from donor OSS fabio-rovai/insurance-register-ontology
(pipeline/fetch_eiopa.py, MIT licence): SharePoint ASP.NET postback replay.
Adapted for OpenDGSFP G0: raw capture + provenance manifest.
"""
import datetime
import hashlib
import html
import json
import pathlib
import re
import urllib.parse
import urllib.request

URL = "https://register.eiopa.europa.eu/registers/register-of-insurance-undertakings"
EXPORT_TARGET = "ctl00$ctl34$g_3217d152_792c_4dd6_9a62_51a782ee2349$lkbtnExport"
OUT = pathlib.Path("data/raw/eiopa/eiopa_register.csv")
MANIFEST = pathlib.Path("evidence/source-manifest.json")

cj = __import__("http.cookiejar", fromlist=["CookieJar"]).CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "opendgsfp-g0 (research; identity crosswalk study)")]


def field(page, name):
    m = re.search(r'id="%s" value="([^"]*)"' % name, page)
    return html.unescape(m.group(1)) if m else None


def main():
    page = op.open(URL, timeout=90).read().decode("utf-8", "replace")
    data = {"__EVENTTARGET": EXPORT_TARGET, "__EVENTARGUMENT": ""}
    for f in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION", "__REQUESTDIGEST"):
        v = field(page, f)
        if v is not None:
            data[f] = v
    req = urllib.request.Request(URL, urllib.parse.urlencode(data).encode(), method="POST")
    resp = op.open(req, timeout=300)
    body = resp.read()
    disp = resp.headers.get("Content-Disposition", "")
    if "attachment" not in disp:
        raise SystemExit(f"export postback did not return a file ({disp!r})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(body)
    rec = {
        "source_system": "EIOPA",
        "source_url": URL,
        "method": "POST (ASP.NET postback replay, donor mechanism fabio-rovai/insurance-register-ontology)",
        "jurisdiction": "EU/EEA",
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "content_sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body),
        "raw_file": str(OUT).replace("\\", "/"),
        "content_disposition": disp,
        "response_headers": dict(resp.headers),
    }
    m = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else []
    m.append(rec)
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
    print("saved", OUT, f"{len(body):,} bytes", rec["content_sha256"][:16])


if __name__ == "__main__":
    main()
