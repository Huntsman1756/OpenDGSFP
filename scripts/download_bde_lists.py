# -*- coding: utf-8 -*-
"""Extract full CSV URLs from saved BdE pages and download the needed lists."""
import re, json, pathlib, hashlib, datetime
import requests

BASE = "https://www.bde.es"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (research; opendgsfp-g0)"})

html = open("data/raw/bde/bde_listas_seguros_page.html", encoding="utf-8").read()
urls = sorted(set(re.findall(r'href="(/webbe/[^"]+/lista-ic-[^"]+\.csv[^"]*)"', html)))
print("IC csv urls found:", len(urls))
for u in urls:
    print("  ", u)

htmlpf = open("data/raw/bde/bde_listas_fondospen_page.html", encoding="utf-8").read()
urlspf = sorted(set(re.findall(r'href="(/webbe/[^"]+/lista-pf-[^"]+\.csv[^"]*)"', htmlpf)))
print("PF csv urls found:", len(urlspf))
for u in urlspf[:5]:
    print("  ", u)

manifest = pathlib.Path("evidence/source-manifest.json")
mlist = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []


def dl(u, dest):
    r = s.get(BASE + u, timeout=120)
    p = pathlib.Path(dest)
    p.write_bytes(r.content)
    rec = {
        "source_system": "BDE",
        "source_url": BASE + u,
        "jurisdiction": "ES",
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "http_status": r.status_code,
        "content_sha256": hashlib.sha256(r.content).hexdigest(),
        "bytes": len(r.content),
        "raw_file": dest,
        "response_headers": {k: v for k, v in r.headers.items() if k.lower() in ("content-type", "last-modified", "content-length", "etag")},
    }
    mlist.append(rec)
    print("downloaded", dest, r.status_code, len(r.content), "sha256", rec["content_sha256"][:16])


for u in urls:
    name = u.split("/")[-1].split("?")[0]
    dl(u, f"data/raw/bde/{name}")
for u in urlspf:
    name = u.split("/")[-1].split("?")[0]
    if any(c in name for c in ("espana", "españa", "esp")) or True:
        dl(u, f"data/raw/bde/{name}")

manifest.write_text(json.dumps(mlist, indent=2, ensure_ascii=False), encoding="utf-8")
print("manifest entries:", len(mlist))
