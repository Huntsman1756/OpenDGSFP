# -*- coding: utf-8 -*-
"""Raw integrity: every capture hash matches; derived data regenerable claims."""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def test_rrpp_capture_log_hashes():
    log = ROOT / "data/raw/dgsfp/rrpp_details/_capture_log.jsonl"
    assert log.exists()
    n = 0
    for line in log.open(encoding="utf-8"):
        rec = json.loads(line)
        f = ROOT / "data/raw/dgsfp/rrpp_details" / rec["captured_file"]
        assert f.exists(), rec["captured_file"]
        assert sha(f) == rec["content_sha256"], rec["captured_file"]
        n += 1
    assert n >= 2700  # full enumeration captured


def test_manifest_covers_bde_and_eiopa():
    m = json.loads((ROOT / "evidence/source-manifest.json").read_text(encoding="utf-8"))
    files = {e["raw_file"]: e["content_sha256"] for e in m["files"]}
    for needed in ["data/raw/bde/lista-ic-es.csv", "data/raw/bde/lista-ic-de.csv",
                   "data/raw/eiopa/eiopa_register.csv", "data/raw/gleif/gleif_records.jsonl",
                   "data/raw/dgsfp/rrpp_mediadores.json", "data/raw/dgsfp/rrpp_fondos.json"]:
        assert needed in files, needed
        assert sha(ROOT / needed) == files[needed], needed


def test_rrpp_enumeration_uniqueness():
    keys = set()
    for line in (ROOT / "data/raw/dgsfp/rrpp_details/_capture_log.jsonl").open(encoding="utf-8"):
        rec = json.loads(line)
        assert rec["clave"] not in keys, f"duplicated capture: {rec['clave']}"
        keys.add(rec["clave"])
