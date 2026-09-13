# -*- coding: utf-8 -*-
"""Parse captured RRPP detail HTML (raw) into a derived JSONL dataset.

Raw inputs : data/raw/dgsfp/rrpp_details/*.html + _capture_log.jsonl
Derived out: data/derived/dgsfp_rrpp_entities.jsonl
Reproducible from raw only.
"""
import hashlib
import html as H
import json
import pathlib
import re

RAW = pathlib.Path("data/raw/dgsfp/rrpp_details")
OUT = pathlib.Path("data/derived/dgsfp_rrpp_entities.jsonl")
PARSER_VERSION = "rrpp_detail_parser/0.2"

PAIR_RE = re.compile(
    r'<label class="label-literal">([\s\S]*?)</label>\s*'
    r'<label[^>]*aria-label="([^"]*)"[^>]*>([\s\S]*?)</label>')


def clean(x):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", x))).strip()


def parse_file(path):
    doc = path.read_bytes().decode("utf-8", "replace")
    fields = {}
    for lit, aria, val in PAIR_RE.findall(doc):
        key = clean(aria)
        val_clean = clean(val)
        # keep first non-empty occurrence of each field
        if key and val_clean and key not in fields:
            fields[key] = val_clean
        elif key and key not in fields:
            fields[key] = ""
    return fields, doc


def main():
    log = {}
    for line in (RAW / "_capture_log.jsonl").open(encoding="utf-8"):
        rec = json.loads(line)
        log[rec["clave"]] = rec
    n = 0
    with OUT.open("w", encoding="utf-8") as out:
        for clave, cap in sorted(log.items()):
            f = RAW / cap["captured_file"]
            fields, doc = parse_file(f)
            # verify hash matches capture log (raw immutability check)
            sha = hashlib.sha256(f.read_bytes()).hexdigest()
            assert sha == cap["content_sha256"], f"hash mismatch for {clave}"
            rec = {
                "clave": clave,
                "tipo": clave[0] if not clave.startswith("RE") else "RE",
                "denominacion": fields.get("Descripcion", ""),
                "lei": fields.get("Código LEI", fields.get("Codigo LEI", "")),
                "nif": fields.get("NIF", ""),
                "situacion": fields.get("Situacion", ""),
                "pais_origen": fields.get("Pais de origen", ""),
                "pais": fields.get("Pais", ""),
                "comunidad": fields.get("Comunidad", ""),
                "provincia": fields.get("Provincia", ""),
                "municipio": fields.get("Municipio", ""),
                "ambito": fields.get("Ambito", ""),
                "fecha_autorizacion": fields.get("FechaAutorizacion", ""),
                "direccion": fields.get("Direccion", ""),
                "source": {
                    "source_system": "DGSFP_RRPP",
                    "source_url": cap["endpoint"],
                    "source_snapshot_date": cap["retrieved_at_utc"][:10],
                    "retrieved_at": cap["retrieved_at_utc"],
                    "content_sha256": cap["content_sha256"],
                    "parser_version": PARSER_VERSION,
                    "raw_file": f"raw/dgsfp/rrpp_details/{cap['captured_file']}",
                },
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    print("parsed", n, "->", OUT)


if __name__ == "__main__":
    main()
