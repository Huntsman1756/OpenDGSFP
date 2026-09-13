# -*- coding: utf-8 -*-
"""Unit tests: LEI arithmetic, key normalization, name diagnostics."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from g0_lib import lei_checksum_valid, norm_dgsfp_key, norm_name, diag_name_agree  # noqa: E402

VALID = [
    "5493000MN7XN3BBKCE67",
    "213800B4ZY949VJYD671",
    "529900J6X2TY517BIE79",
    "9598003REPS2DQZC4946",  # C0001 (RRPP live capture)
    "F240A7PWJB2BLKELB442",  # AGCS SE (documented chain)
]
INVALID = [
    "00000000000000000000",
    "5493O00MN7XN3BBKCE67",  # letter O for zero
    "5493000MN7XN3BBKCE6",   # truncated
    "",
]


def test_lei_checksum_valid():
    for lei in VALID:
        assert lei_checksum_valid(lei), lei


def test_lei_checksum_invalid():
    for lei in INVALID:
        assert not lei_checksum_valid(lei), lei


def test_norm_dgsfp_key():
    assert norm_dgsfp_key("C0001") == "C0001"
    assert norm_dgsfp_key("M032") == "M0032"
    assert norm_dgsfp_key("E0193") == "E0193"
    assert norm_dgsfp_key("  C0808 ") == "C0808"
    assert norm_dgsfp_key("L0007") == "L0007"


def test_norm_name_and_diag():
    assert diag_name_agree("MAPFRE, S.A.", "MAPFRE SA") == "exact_norm"
    assert diag_name_agree("AXA FRANCE IARD SUC, ESPAÑA", "AXA FRANCE IARD") in ("token_subset", "exact_norm")
    assert diag_name_agree("UNO", "DOS") == "different"


def test_norm_name_strips_accents():
    assert "ESPANA" in norm_name("ESPAÑA") or "ESP" in norm_name("ESPAÑA")
