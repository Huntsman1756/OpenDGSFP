# -*- coding: utf-8 -*-
"""Canonical record model for OpenDGSFP v0.1 (contract: docs/gates/V0.1.md).

Serialization is canonical: UTF-8, sorted keys, compact separators, '\n' lines.
IDs are content-derived (sha256 of canonical form) => deterministic by construction.
"""
import hashlib
import json

ENTITY_KINDS = ("INSURANCE_UNDERTAKING", "REINSURANCE_UNDERTAKING",
                "EEA_BRANCH", "UNDERTAKING")
IDENTITY_STATUS = ("EXACT", "CONFLICT", "UNRESOLVED")
SOURCE_COVERAGE = ("MULTI_SOURCE", "SOURCE_ONLY")
LINK_STATUS = ("EXACT", "UNRESOLVED", "CONFLICT")
RESOLUTION_METHODS = ("DGSFP_KEY", "LEI", "BDE_PARENT_CODE", "OFFICIAL_BRIDGE", "NONE")

EVIDENCE_TIERS = ("T0_PRIMARY_DIRECT", "T1_PRIMARY_DOCUMENT", "T2_PRIMARY_UI",
                  "T3_DERIVED_REPRODUCIBLE", "T4_DONOR", "T5_MANUAL_REVIEW")

# conflict levels
CL_IDENTITY = "IDENTITY"                # affects identity_status -> CONFLICT
CL_ATTRIBUTE = "ATTRIBUTE"              # entity stays EXACT
CL_IDENTIFIER_ASSIGNMENT = "IDENTIFIER_ASSIGNMENT"
CL_DIAGNOSTIC = "DIAGNOSTIC"

NS_DGSFP = "dgsfp:clave"
NS_LEI = "lei"
NS_BDE_SUP = "bde:supervisor_code"
NS_BDE_EU = "bde:european_code"
NS_EIOPA = "eiopa:identification_code"
NS_NIF = "es:nif"


def canon(obj):
    """Canonical UTF-8 bytes for any record (sorted keys, compact separators)."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def content_id(prefix, obj):
    """Deterministic id derived from the record's canonical content."""
    return f"{prefix}_{hashlib.sha256(canon(obj)).hexdigest()[:16]}"


def make_assertion(subject, predicate, obj, prov):
    """A single sourced claim. prov = full provenance block (contract SS7)."""
    a = {"subject": subject, "predicate": predicate, "object": obj,
         "provenance": prov}
    a["assertion_id"] = content_id("as", a)
    return a


def make_identifier(scheme, value, country=None):
    ident = {"scheme": scheme, "value": value}
    if country:
        ident["country"] = country
    return ident


def ident_key(ident):
    """Hashable key for identifier-based merging (authority-scoped)."""
    return (ident["scheme"], ident["value"], ident.get("country"))


def make_relation(relation_type, endpoints, link_status, methods, evidence, detail=None):
    if link_status not in LINK_STATUS:
        raise ValueError(link_status)
    bad = [m for m in methods if m not in RESOLUTION_METHODS]
    if bad:
        raise ValueError(f"invalid resolution_method {bad}")
    r = {"relation_type": relation_type, "endpoints": endpoints,
         "link_status": link_status, "resolution_method": sorted(set(methods)),
         "evidence": sorted(set(evidence)), "detail": detail}
    r["edge_id"] = content_id("rel", r)
    return r


def make_conflict(kind, level, assertions, detail):
    c = {"kind": kind, "level": level, "assertions": sorted(set(assertions)),
         "detail": detail}
    c["conflict_id"] = content_id("cf", c)
    return c


def empty_entity(entity_kind):
    if entity_kind not in ENTITY_KINDS:
        raise ValueError(entity_kind)
    return {"entity_id": None, "entity_kind": entity_kind,
            "identity_status": None, "source_coverage": None,
            "identifiers": [], "registrations": [],
            "cross_border_operations": [], "source_assertions": [],
            "conflicts": [], "snapshots": [], "diagnostics": [],
            "merge_basis": []}
