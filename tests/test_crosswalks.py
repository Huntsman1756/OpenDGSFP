# -*- coding: utf-8 -*-
"""Crosswalk spot checks: documented chains re-derived from raw inputs only."""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from bde_loader import load_bde, norm_dgsfp_key  # noqa: E402
from g0_lib import load_bde_home, load_eiopa, load_gleif, lei_checksum_valid  # noqa: E402


def rrpp_detail(clave):
    doc = (ROOT / f"data/raw/dgsfp/rrpp_details/{clave}.html").read_text(encoding="utf-8", errors="replace")
    import re
    import html as H
    pairs = re.findall(r'<label class="label-literal">([\s\S]*?)</label>\s*<label[^>]*>([\s\S]*?)</label>', doc)
    out = {}
    for a, b in pairs:
        k = H.unescape(re.sub(r"<[^>]+>", " ", a)).strip()
        v = H.unescape(re.sub(r"<[^>]+>", " ", b)).strip()
        if k and k not in out and v:
            out[k] = v
    return out


def _field(d, *fragments):
    for k, v in d.items():
        if all(f.lower() in k.lower() for f in fragments):
            return v
    return None


def test_documented_chain_E0193():
    """E0193 -> DEA00PQ -> Allianz Global Corporate & Specialty SE -> F240A7PWJB2BLKELB442."""
    d = rrpp_detail("E0193")
    assert _field(d, "Clave") == "E0193"
    bde_es = load_bde(str(ROOT / "data/raw/bde/lista-ic-es.csv"))
    row = next(r for r in bde_es if norm_dgsfp_key(r["CÓDIGO DE SUPERVISOR"]) == "E0193")
    assert row["ENTIDAD MATRIZ"] == "DEA00PQ"
    home = load_bde_home("de")
    parent = next(r for r in home if r["CÓDIGO EUROPEO"] == "DEA00PQ")
    assert "ALLIANZ GLOBAL CORPORATE" in parent["NOMBRE"].upper()
    assert parent["LEI"] == "F240A7PWJB2BLKELB442"
    assert lei_checksum_valid(parent["LEI"])


def test_spanish_insurer_C0001_full_chain():
    d = rrpp_detail("C0001")
    lei_rrpp = _field(d, "LEI")
    assert lei_rrpp == "9598003REPS2DQZC4946"
    bde_es = load_bde(str(ROOT / "data/raw/bde/lista-ic-es.csv"))
    row = next(r for r in bde_es if norm_dgsfp_key(r["CÓDIGO DE SUPERVISOR"]) == "C0001")
    assert row["LEI"] == lei_rrpp
    eiopa = load_eiopa()
    home = next(r for r in eiopa if r["Home Country"] == "ES"
                and r["Cross border status"] == "Domestic undertaking"
                and r["Identification code"] == "C0001")
    assert home["LEI"].strip().upper() == lei_rrpp
    gleif = load_gleif()
    assert lei_rrpp in gleif
    assert gleif[lei_rrpp]["entityStatus"] in ("ACTIVE", "RETIRED")


def test_lps_keys_exposed_live():
    d1 = rrpp_detail("L0419")
    assert _field(d1, "Clave") == "L0419"
    assert "ALLIANZ GLOBAL CORPORATE" in _field(d1, "Denominaci").upper()
    d2 = rrpp_detail("L1160")
    assert _field(d2, "Clave") == "L1160"
    assert _field(d2, "Origen") == "Liechtenstein"


def test_g0b2_population_numbers_stable():
    rows = [json.loads(l) for l in (ROOT / "data/derived/g0b2_checks.jsonl").open(encoding="utf-8")]
    act = [r for r in rows if r["situacion"] == "Activa"]
    assert len(act) == 825
    lei_rows = [r for r in act if r["LEI"]]
    assert len(lei_rows) == 209
    exact = [r for r in act if r["crosswalk_result"] == "PASS_EXACT"]
    assert len(exact) >= 150


def test_g0a_population_all_exact():
    rows = [json.loads(l) for l in (ROOT / "data/derived/g0a_checks.jsonl").open(encoding="utf-8")]
    assert len(rows) == 137
    for flag in ["DGSFP_KEY_BDE_SUPERVISOR_CODE_EXACT", "DGSFP_KEY_EIOPA_ID_EXACT",
                 "BDE_LEI_EIOPA_LEI_EXACT", "GLEIF_LEI_EXACT", "all_leis_consistent"]:
        assert all(r[flag] for r in rows), flag


def test_ledger_policy_no_fuzzy_canonical():
    ledger = json.loads((ROOT / "evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    for e in ledger["edges"]:
        if e["canonical"]:
            ident = (e["identifier_used"] or "").lower()
            assert any(t in ident for t in ("lei", "clave", "code", "matriz", "postback", "api")), \
                f"canonical edge without exact identifier: {e['edge_id']} {ident}"
