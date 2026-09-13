# -*- coding: utf-8 -*-
"""Print sha256 table for key raw sources (for reports/G0-results.md)."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(".")
KEY_FILES = [
    "data/raw/dgsfp/rrpp_home_2026-09-13.html",
    "data/raw/dgsfp/site.min.js",
    "data/raw/dgsfp/rrpp_ayuda.html",
    "data/raw/dgsfp/rrpp_details/_capture_log.jsonl",
    "data/raw/dgsfp/rrpp_pensions/_capture_log_fondo.jsonl",
    "data/raw/dgsfp/rrpp_pensions/_capture_log_plan.jsonl",
    "data/raw/dgsfp/rrpp_gestoras.json",
    "data/raw/dgsfp/rrpp_fondos.json",
    "data/raw/dgsfp/rrpp_depositarias.json",
    "data/raw/dgsfp/rrpp_mediadores.json",
    "data/raw/dgsfp/rrpp_pensions/F0021.html",
    "data/raw/bde/lista-ic-es.csv",
    "data/raw/bde/lista-ic-de.csv",
    "data/raw/bde/lista-ic-fr.csv",
    "data/raw/bde/lista-ic-lu.csv",
    "data/raw/bde/lista-ic-ie.csv",
    "data/raw/bde/lista-ic-be.csv",
    "data/raw/bde/lista-ic-pt.csv",
    "data/raw/bde/lista-pf-es.csv",
    "data/raw/eiopa/eiopa_register.csv",
    "data/raw/gleif/gleif_records.jsonl",
    "data/derived/dgsfp_rrpp_entities.jsonl",
    "data/derived/g0a_checks.jsonl",
    "data/derived/g0b1_checks.jsonl",
    "data/derived/g0b2_checks.jsonl",
    "data/derived/g0c_checks.jsonl",
    "evidence/evidence-ledger.json",
]
rows = []
for f in KEY_FILES:
    p = ROOT / f
    if p.exists():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        rows.append((f, p.stat().st_size, h))
    else:
        rows.append((f, None, "MISSING"))
out = [{"file": f, "bytes": b, "sha256": h} for f, b, h in rows]
pathlib.Path("reports/g0-source-hashes.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for f, b, h in rows:
    print(f"{h}  {b if b else '-':>10}  {f}")
