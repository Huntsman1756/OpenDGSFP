# -*- coding: utf-8 -*-
"""Consolidate evidence/source-manifest.json: one entry per raw artifact with sha256."""
import hashlib
import json
import pathlib
import datetime

RAW_DIRS = ["data/raw/dgsfp", "data/raw/bde", "data/raw/eiopa", "data/raw/gleif"]
SKIP = {"_capture_log.jsonl"}  # logs are provenance themselves; per-file hashes inside
OUT = pathlib.Path("evidence/source-manifest.json")

entries = []
for d in RAW_DIRS:
    base = pathlib.Path(d)
    if not base.exists():
        continue
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.name not in SKIP:
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            entries.append({
                "source_system": p.parent.parent.name.upper() if p.parent.parent.name in ("dgsfp", "bde", "eiopa", "gleif") else p.parent.name.upper(),
                "raw_file": p.as_posix(),
                "bytes": p.stat().st_size,
                "content_sha256": h,
                "note": "captured log entry with per-request provenance" if p.name.endswith(".jsonl") else None,
                "registered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })

# keep previously recorded fetch events (EIOPA/manifests logs) and merge
old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
fetch_events = [e for e in old if e.get("source_system") in ("EIOPA", "EIOPA_IORP", "GLEIF", "BDE") and e.get("source_url")]
out = {"_meta": {
            "project": "OpenDGSFP",
            "gate": "G0",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "policy": "raw inputs immutable; every artifact sha256-pinned; derived data regenerable from raw",
            "counts": {"files": len(entries), "fetch_events": len(fetch_events)},
        },
        "files": entries,
        "fetch_events": fetch_events}
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print("manifest files:", len(entries), "| fetch events:", len(fetch_events))
