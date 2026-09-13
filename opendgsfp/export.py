# -*- coding: utf-8 -*-
"""Deterministic JSONL export (contract SS8).

Canonical bytes: UTF-8, sorted keys, compact separators, '\\n' line endings,
explicit nulls, header record first. `generated_at` is derived from source
snapshot dates (SOURCE_DATE_EPOCH-style) — never wall-clock — so identical
frozen inputs produce identical bytes and an identical sha256.
"""
import hashlib
import json
import pathlib

from .model import canon

OUT_DIR = "data/derived/v0.1"


def header_record(ds):
    return {"record_type": "manifest_header",
            "schema_version": ds["schema_version"],
            "parser_version": ds["parser_version"],
            "generated_at": ds["generated_at"],
            "counts": ds["counts"]}


def records(ds):
    """Ordered canonical records: header, entities, relations, observations."""
    yield header_record(ds)
    for e in ds["entities"]:
        rec = dict(e)
        rec["record_type"] = "entity"
        yield rec
    for r in ds["relations"]:
        rec = dict(r)
        rec["record_type"] = "relation"
        yield rec
    for o in ds["observations"]:
        rec = dict(o)
        rec["record_type"] = "observation"
        yield rec


def to_jsonl_bytes(ds):
    return b"\n".join(canon(r) for r in records(ds)) + b"\n"


def dataset_sha256(ds):
    return hashlib.sha256(to_jsonl_bytes(ds)).hexdigest()


def write_export(ds, out_dir=OUT_DIR, root=None):
    """Write opendgsfp-0.1.jsonl + manifest.json; returns their paths."""
    base = pathlib.Path(root) / out_dir if root else pathlib.Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)
    data = to_jsonl_bytes(ds)
    data_path = base / f"opendgsfp-{ds['schema_version'].split('/')[-1]}.jsonl"
    data_path.write_bytes(data)

    snapshots = {}
    for e in ds["entities"]:
        for a in e["source_assertions"]:
            p = a["provenance"]
            key = (p["source_system"], p["jurisdiction"], p["raw_file"])
            snapshots.setdefault(key, {
                "source_system": p["source_system"],
                "jurisdiction": p["jurisdiction"],
                "source_url": p["source_url"],
                "source_snapshot_date": p["source_snapshot_date"],
                "retrieved_at": p["retrieved_at"],
                "content_sha256": p["content_sha256"],
                "parser_version": p["parser_version"],
                "raw_file": p["raw_file"],
                "evidence_tier": p["evidence_tier"],
            })
    manifest = {
        "schema_version": ds["schema_version"],
        "parser_version": ds["parser_version"],
        "generated_at": ds["generated_at"],
        "generated_at_derivation": "max(source_snapshot_date) over input snapshots "
                                   "(deterministic; wall-clock build time excluded)",
        "data_file": data_path.name,
        "data_sha256": hashlib.sha256(data).hexdigest(),
        "data_bytes": len(data),
        "counts": ds["counts"],
        "snapshots": [snapshots[k] for k in sorted(snapshots)],
        "frozen_inputs": {
            "g0_tag": "g0", "g0_commit": "42bb59de4925eabcefdca31e211c63e9ae9e4917",
            "source_manifest": "evidence/source-manifest.json",
        },
    }
    manifest_path = base / "manifest.json"
    # write bytes, not text: '\n' must stay LF on every platform (Windows
    # write_text would translate to CRLF and break byte-reproducibility)
    manifest_path.write_bytes(
        (json.dumps(manifest, ensure_ascii=False, indent=2,
                    sort_keys=True) + "\n").encode("utf-8"))
    return data_path, manifest_path
