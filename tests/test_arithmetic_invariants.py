# -*- coding: utf-8 -*-
"""Arithmetic invariants: document-consistency gates.

These tests ensure that the narrative numbers in G0-results.md and
evidence-ledger.json reconcile with the derived data. They fail if
a future code change breaks the arithmetic without updating the report.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def test_b2_lei_plus_gap_equals_activa():
    """B2: 209 (LEI) + 616 (no LEI) = 825 Activa.

    Regression guard: a previous report said 617 DOCUMENTED_GAP, which
    implied 209 + 617 = 826.  The correct split is 209 LEI + 616 no-LEI
    = 825.  L1522 has a LEI but no EIOPA home match, so it is counted
    in DOCUMENTED_GAP despite having LEI — the total DOCUMENTED_GAP is
    617, but the *no-LEI* subset is 616.
    """
    rows = [json.loads(l) for l in
            (ROOT / "data/derived/g0b2_checks.jsonl").open(encoding="utf-8")]
    act = [r for r in rows if r["situacion"] == "Activa"]
    lei_avail = [r for r in act if r["RRPP_L_LEI_AVAILABLE"]]
    no_lei = [r for r in act if not r["RRPP_L_LEI_AVAILABLE"]]
    assert len(act) == 825, f"Activa count: expected 825, got {len(act)}"
    assert len(lei_avail) == 209, f"LEI available: expected 209, got {len(lei_avail)}"
    assert len(no_lei) == 616, f"No LEI: expected 616, got {len(no_lei)}"
    assert len(lei_avail) + len(no_lei) == len(act)


def test_b2_documented_gap_includes_l1522():
    """L1522 has LEI but no EIOPA home; it is DOCUMENTED_GAP, not PASS_*."""
    rows = [json.loads(l) for l in
            (ROOT / "data/derived/g0b2_checks.jsonl").open(encoding="utf-8")]
    l1522 = next(r for r in rows if r["clave"] == "L1522")
    assert l1522["RRPP_L_LEI_AVAILABLE"], "L1522 should have LEI"
    assert l1522["crosswalk_result"] == "DOCUMENTED_GAP_NO_EXACT_ID"


def test_l_filter_1580_to_825():
    """Universe L: 1,580 total → 825 Activa (situacion='Activa' filter)."""
    rows = [json.loads(l) for l in
            (ROOT / "data/derived/g0b2_checks.jsonl").open(encoding="utf-8")]
    total_l = len(rows)
    activa_l = sum(1 for r in rows if r["situacion"] == "Activa")
    assert total_l == 1580, f"Total L: expected 1580, got {total_l}"
    assert activa_l == 825, f"Activa L: expected 825, got {activa_l}"


def test_edge_sum_reconciles():
    """A 44 + B1 48 + B2 12 + C 17 = 121 gate edges + 2 mechanisms = 123 total."""
    ledger = json.loads((ROOT / "evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    counts = ledger["counts"]
    assert counts["edges"] == 123
    by_gate = counts["by_gate"]
    gate_sum = by_gate["G0-A"] + by_gate["G0-B1"] + by_gate["G0-B2"] + by_gate["G0-C"]
    assert gate_sum == 121, f"Gate sum: expected 121, got {gate_sum}"
    assert by_gate["mechanisms"] == 2
    assert gate_sum + by_gate["mechanisms"] == counts["edges"]


def test_canonical_vs_total_edges():
    """120 canonical + 3 documented_gap = 123 total (mechanisms are canonical)."""
    ledger = json.loads((ROOT / "evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    edges = ledger["edges"]
    canonical = sum(1 for e in edges if e["canonical"])
    non_canonical = sum(1 for e in edges if not e["canonical"])
    assert canonical == 120, f"Canonical: expected 120, got {canonical}"
    assert non_canonical == 3, f"Non-canonical: expected 3, got {non_canonical}"
    assert canonical + non_canonical == len(edges)


def test_b2_crosswalk_result_partition():
    """B2 Activa: 166 PASS_EXACT + 42 PASS_EXACT_NO_ES_OP + 617 DOCUMENTED_GAP = 825."""
    rows = [json.loads(l) for l in
            (ROOT / "data/derived/g0b2_checks.jsonl").open(encoding="utf-8")]
    act = [r for r in rows if r["situacion"] == "Activa"]
    from collections import Counter
    c = Counter(r["crosswalk_result"] for r in act)
    assert c["PASS_EXACT"] == 166
    assert c["PASS_EXACT_NO_ES_OP"] == 42
    assert c["DOCUMENTED_GAP_NO_EXACT_ID"] == 617
    assert sum(c.values()) == 825


def test_b2_gap_scope_matches_derived_data():
    """Ledger narrative must reconcile: NO-IDENTIFIER scope == no-LEI count.

    GAP-B2-DGSFP-LPS-NO-IDENTIFIER covers keys with NO identifier (616).
    L1522 has a LEI and is tracked under GAP-B2-L1522-STALE-LEI, so the
    no-identifier scope must be 616, not 617. If data or narrative drift,
    this fails.
    """
    import re
    rows = [json.loads(l) for l in
            (ROOT / "data/derived/g0b2_checks.jsonl").open(encoding="utf-8")]
    act = [r for r in rows if r["situacion"] == "Activa"]
    no_lei = sum(1 for r in act if not r["RRPP_L_LEI_AVAILABLE"])
    gap_total = sum(1 for r in act if r["crosswalk_result"] == "DOCUMENTED_GAP_NO_EXACT_ID")

    ledger = json.loads((ROOT / "evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    gaps = {g["id"]: g for g in ledger["documented_gaps"]}
    m = re.match(r"(\d+) of (\d+)", gaps["GAP-B2-DGSFP-LPS-NO-IDENTIFIER"]["scope"])
    assert m, "scope must start with '<n> of <denom>'"
    assert int(m.group(1)) == no_lei, \
        f"NO-IDENTIFIER scope {m.group(1)} != derived no-LEI count {no_lei}"
    assert int(m.group(2)) == len(act)
    # total unresolved = no-identifier + stale-LEI (L1522 is its own gap entry)
    assert "GAP-B2-L1522-STALE-LEI" in gaps
    assert no_lei + 1 == gap_total


def test_noncanonical_edges_are_exactly_the_b2_gaps():
    """The only non-canonical edges are the 3 documented B2 gaps."""
    ledger = json.loads((ROOT / "evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    nc = [e for e in ledger["edges"] if not e["canonical"]]
    assert {e["origin"]["id"] for e in nc} == {"L0419", "L1160", "L1522"}
    assert all(e["edge_id"].startswith("B2") for e in nc)
    assert all(e["validation"]["result"] == "DOCUMENTED_GAP" for e in nc)
