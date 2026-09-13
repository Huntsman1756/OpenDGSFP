# -*- coding: utf-8 -*-
"""v0.1 contract tests — the 14 preregistered checks from docs/gates/V0.1.md SS9,
materialized against the frozen G0 snapshot (tag g0, commit 42bb59d).

The dataset is built once per test session (module-scoped fixture).
"""
import hashlib
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent

import sys
sys.path.insert(0, str(ROOT))

from opendgsfp.build import build_dataset            # noqa: E402
from opendgsfp.export import to_jsonl_bytes          # noqa: E402
from opendgsfp.sources import norm_name              # noqa: E402


@pytest.fixture(scope="module")
def ds():
    return build_dataset()


@pytest.fixture(scope="module")
def ents(ds):
    by_clave = {}
    by_lei = {}
    for e in ds["entities"]:
        for i in e["identifiers"]:
            if i["scheme"] == "dgsfp:clave":
                by_clave[i["value"]] = e
            if i["scheme"] == "lei":
                by_lei[i["value"]] = e
    return by_clave, by_lei


PROV_REQUIRED = ("source_system", "jurisdiction", "source_url",
                 "source_snapshot_date", "retrieved_at", "content_sha256",
                 "parser_version", "raw_file", "evidence_tier")


# ---- 1. deterministic export -------------------------------------------------
def test_export_deterministic_bytes(ds):
    ds2 = build_dataset()
    b1, b2 = to_jsonl_bytes(ds), to_jsonl_bytes(ds2)
    assert b1 == b2
    assert hashlib.sha256(b1).hexdigest() == hashlib.sha256(b2).hexdigest()
    # no wall-clock material inside canonical bytes
    assert ds["generated_at"] == "2026-09-13"   # derived: max source snapshot date


# ---- 2. raw integrity / hash pinning ----------------------------------------
def test_raw_integrity_pinned(ds):
    referenced = {a["provenance"]["raw_file"]
                  for e in ds["entities"] for a in e["source_assertions"]}
    for raw in referenced:
        p = ROOT / raw
        assert p.exists(), raw
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        provs = {a["provenance"]["content_sha256"]
                 for e in ds["entities"] for a in e["source_assertions"]
                 if a["provenance"]["raw_file"] == raw}
        assert provs == {actual}, raw


# ---- 3. no fuzzy canonical ---------------------------------------------------
def test_no_fuzzy_canonical(ds):
    allowed = {"DGSFP_KEY", "LEI", "BDE_PARENT_CODE", "OFFICIAL_BRIDGE", "NONE"}
    exact_bases = {"SHARED_LEI", "SHARED_DGSFP_KEY",
                   "SHARED_AUTHORITY_SCOPED_ID", "OFFICIAL_BRIDGE"}
    for r in ds["relations"]:
        assert set(r["resolution_method"]) <= allowed
        assert "NAME" not in str(r["resolution_method"]).upper()
        if r["link_status"] == "EXACT":
            assert r["resolution_method"] != ["NONE"]
            assert r["evidence"], r
    # EVERY_CANONICAL_MERGE_HAS_EXACT_BASIS: merges are only possible through
    # merge_into(), which requires an exact basis; every merge event must be
    # recorded with a basis in the allowed set and a real identifier.
    presence = {"DGSFP_RRPP", "BDE", "EIOPA"}
    for e in ds["entities"]:
        for m in e["merge_basis"]:
            assert m["basis"] in exact_bases, (e["entity_id"], m)
            assert m["identifier"] and m["evidence"]
        systems = ({r["system"] for r in e["registrations"]}
                   | {o["asserted_by"] for o in e["cross_border_operations"]}
                   & presence)
        if len(systems) >= 2:
            assert e["merge_basis"], \
                f"multi-source entity without merge basis: {e['entity_id']}"
    # successor candidates are UNRESOLVED by construction — never canonical
    for r in ds["relations"]:
        if r["relation_type"] == "IDENTIFIER_SUCCESSOR_CANDIDATE":
            assert r["link_status"] == "UNRESOLVED"
            assert r["resolution_method"] == ["NONE"]
    # no self-referential edges
    for r in ds["relations"]:
        eids = [ep.get("entity_id") for ep in r["endpoints"]]
        assert len(set(eids)) == len(eids) or len(eids) == 1, r["edge_id"]


# ---- 4. lookup by DGSFP key --------------------------------------------------
def test_lookup_by_dgsfp_key(ds, ents):
    by_clave, _ = ents
    assert by_clave["C0001"]["entity_kind"] == "INSURANCE_UNDERTAKING"
    assert by_clave["E0210"]["entity_kind"] == "EEA_BRANCH"
    assert by_clave["L1522"]["entity_kind"] == "UNDERTAKING"
    # every DGSFP clave from the frozen parse resolves to exactly one entity
    raw_claves = {json.loads(l)["clave"]
                  for l in open(ROOT / "data/derived/dgsfp_rrpp_entities.jsonl",
                                encoding="utf-8")}
    assert raw_claves <= set(by_clave)


# ---- 5. lookup by LEI --------------------------------------------------------
def test_lookup_by_lei(ds, ents):
    by_clave, by_lei = ents
    assert by_lei["9598003REPS2DQZC4946"] is by_clave["C0001"]
    # L1522: stale LEI resolves the DGSFP entity; the current EIOPA LEI resolves
    # a *separate* entity — joined only by an UNRESOLVED successor candidate.
    assert by_lei["7245004QN0BFE9Q9EV42"] is by_clave["L1522"]
    other = by_lei["724500D3EHHJWKLWY913"]
    assert other["entity_id"] != by_clave["L1522"]["entity_id"]
    cand = [r for r in ds["relations"]
            if r["relation_type"] == "IDENTIFIER_SUCCESSOR_CANDIDATE"
            and {ep["entity_id"] for ep in r["endpoints"]}
            == {by_clave["L1522"]["entity_id"], other["entity_id"]}]
    assert cand and cand[0]["link_status"] == "UNRESOLVED"


# ---- 6. branch -> home undertaking -------------------------------------------
def test_branch_to_home(ds, ents):
    by_clave, _ = ents
    e = by_clave["E0210"]
    rel = next(r for r in ds["relations"]
               if r["relation_type"] == "BRANCH_OF"
               and r["endpoints"][0]["entity_id"] == e["entity_id"])
    assert set(rel["resolution_method"]) <= {"BDE_PARENT_CODE", "LEI"}
    assert len(rel["evidence"]) >= 2    # both IC lists: ES row + home-country row
    parent = next(x for x in ds["entities"]
                  if x["entity_id"] == rel["endpoints"][1]["entity_id"])
    assert any(i["scheme"] == "bde:european_code" for i in parent["identifiers"])
    # divergent branch LEIs (E0245: DGSFP ficha publishes the parent's LEI while
    # BdE asserts another) are preserved as IDENTIFIER_ASSIGNMENT conflicts —
    # subject undetermined — not identity conflicts.
    e245 = by_clave["E0245"]
    assert any(c["kind"] == "IDENTIFIER_SUBJECT_UNDETERMINED"
               for c in e245["conflicts"])


# ---- 7. conflicts preserved --------------------------------------------------
def test_conflicts_preserved(ds, ents):
    by_clave, _ = ents
    e1319 = by_clave["L1319"]
    assert e1319["identity_status"] == "EXACT"          # attribute conflict only
    assert any(c["kind"] == "HOME_COUNTRY_DISAGREEMENT"
               and c["level"] == "ATTRIBUTE" for c in e1319["conflicts"])
    e1522 = by_clave["L1522"]
    assert e1522["identity_status"] == "CONFLICT"       # identity-level conflict
    assert any(c["kind"] == "IDENTIFIER_LIFECYCLE_CONFLICT"
               for c in e1522["conflicts"])
    # conflicts may cite assertions from other entities (cross-source disputes);
    # every cited assertion must exist somewhere in the dataset.
    all_aids = {a["assertion_id"] for e in ds["entities"]
                for a in e["source_assertions"]}
    for e in ds["entities"]:
        for c in e["conflicts"]:
            assert set(c["assertions"]) <= all_aids, (e["entity_id"], c["kind"])


# ---- 8. unresolved LPS preserved ---------------------------------------------
def test_unresolved_lps_preserved(ds):
    l_no_lei_activa = [
        e for e in ds["entities"]
        if any(i["scheme"] == "dgsfp:clave" and i["value"].startswith("L")
               for i in e["identifiers"])
        and not any(i["scheme"] == "lei" for i in e["identifiers"])
        and any(r["system"] == "DGSFP_RRPP" and r["situacion"] == "Activa"
                for r in e["registrations"])]
    assert len(l_no_lei_activa) == 616
    for e in l_no_lei_activa:
        assert e["identity_status"] == "UNRESOLVED"
        assert e["source_coverage"] == "SOURCE_ONLY"
        assert any(o["regime"] == "LPS" and o["asserted_by"] == "DGSFP_RRPP"
                   for o in e["cross_border_operations"])


# ---- 9. snapshot provenance complete ------------------------------------------
def test_snapshot_provenance_complete(ds):
    for e in ds["entities"]:
        for a in e["source_assertions"]:
            p = a["provenance"]
            for f in PROV_REQUIRED:
                assert f in p, (e["entity_id"], f)
            assert p["source_system"] in {"DGSFP_RRPP", "BDE", "EIOPA", "GLEIF"}
            assert p["source_snapshot_date"] and p["content_sha256"]
            assert p["parser_version"] and p["raw_file"]


# ---- 10. three-source LEI identity --------------------------------------------
def test_three_source_lei_identity(ds, ents):
    _, by_lei = ents
    ent = by_lei["222100GIQKRF94HI8657"]   # L1319: DGSFP+EIOPA+GLEIF on one LEI
    systems = {a["provenance"]["source_system"] for a in ent["source_assertions"]}
    assert {"DGSFP_RRPP", "EIOPA", "GLEIF"} <= systems
    leis = {i["value"] for i in ent["identifiers"] if i["scheme"] == "lei"}
    assert leis == {"222100GIQKRF94HI8657"}
    assert ent["identity_status"] == "EXACT"   # shared LEI => same entity


# ---- 11. no merge by name -----------------------------------------------------
def test_no_merge_by_name(ds):
    # entities sharing a normalized name but no exact identifier stay separate.
    # Control: same-name EIOPA-vs-DGSFP pairs merged only via identifier evidence.
    seen = {}
    for e in ds["entities"]:
        name = next((a["object"] for a in e["source_assertions"]
                     if a["predicate"] == "PUBLISHES_NAME"), None)
        if not name:
            continue
        key = norm_name(name)
        if key in seen and seen[key]["entity_id"] != e["entity_id"]:
            a_ids = {(i["scheme"], i["value"]) for i in seen[key]["identifiers"]}
            b_ids = {(i["scheme"], i["value"]) for i in e["identifiers"]}
            # if they remain separate entities, they must share no identifier
            # (a shared identifier would have merged them by construction)
            assert not (a_ids & b_ids), "merged only by name would violate policy"
        else:
            seen.setdefault(key, e)


# ---- 12. schema/version stable -------------------------------------------------
def test_schema_version_stable(ds):
    assert ds["schema_version"] == "opendgsfp/0.1"
    header = json.loads(to_jsonl_bytes(ds).split(b"\n")[0])
    assert header["schema_version"] == "opendgsfp/0.1"
    assert header["record_type"] == "manifest_header"
    for e in ds["entities"]:
        assert set(e) >= {"entity_id", "entity_kind", "identity_status",
                          "source_coverage", "identifiers", "registrations",
                          "cross_border_operations", "source_assertions",
                          "conflicts", "snapshots", "diagnostics"}


# ---- 13. four states/dimensions representable ----------------------------------
def test_four_states_representable(ds):
    combos = {(e["identity_status"], e["source_coverage"]) for e in ds["entities"]}
    assert ("EXACT", "MULTI_SOURCE") in combos
    assert ("EXACT", "SOURCE_ONLY") in combos
    assert ("UNRESOLVED", "SOURCE_ONLY") in combos
    assert any(s == "CONFLICT" for s, _ in combos)   # identity-level conflicts exist
    link_statuses = {r["link_status"] for r in ds["relations"]}
    assert {"EXACT", "UNRESOLVED"} <= link_statuses


# ---- 14. source-only strictness -------------------------------------------------
def test_source_only_strict(ds):
    presence = {"DGSFP_RRPP", "BDE", "EIOPA"}        # GLEIF validates, not presence
    for e in ds["entities"]:
        systems = ({r["system"] for r in e["registrations"]}
                   | {o["asserted_by"] for o in e["cross_border_operations"]}
                   & presence)
        if e["source_coverage"] == "SOURCE_ONLY":
            assert len(systems) == 1, e["entity_id"]
        else:
            assert len(systems) >= 2, e["entity_id"]
    # EIOPA FTS entities with exact LEI but no linked L keep EXACT identity;
    # the *link* is what stays UNRESOLVED.
    unresolved_lps = [r for r in ds["relations"]
                      if r["relation_type"] == "LPS_REGISTRATION_LINK"
                      and r["link_status"] == "UNRESOLVED"]
    assert unresolved_lps
    by_id = {e["entity_id"]: e for e in ds["entities"]}
    for r in unresolved_lps:
        ent = by_id[r["endpoints"][0]["entity_id"]]
        assert ent["identity_status"] in ("EXACT", "CONFLICT")
        assert r["resolution_method"] == ["NONE"]
