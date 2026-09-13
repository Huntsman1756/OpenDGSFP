# OpenDGSFP

A read-only, reproducible identity and provenance layer for Spanish
insurance entities, built over official public registers.

Public sources disagree: names differ between registers, identifiers go
stale, snapshots lag each other, and ~75% of freedom-of-services operators
have no published LEI at all. OpenDGSFP does not fabricate a clean master
database — it preserves evidence, conflicts and documented gaps, and only
builds canonical identity on **exact official identifiers**.

## Status

- **G0 — frozen** (tag `g0`, commit `42bb59d`): source access + exact
  identity crosswalk verified. Verdict `BUILD_WITH_BOUNDED_GAPS`.
- **v0.1 scope — frozen**: `docs/gates/V0.1.md`.
- **v0.1 core model — merged**: `opendgsfp/` + deterministic JSONL export.

## What it does (v0.1)

- Canonical model over four sources: **DGSFP** RRPP (C/M/P/R/E/L keys),
  **Banco de España** IC lists, **EIOPA** register of undertakings,
  **GLEIF** LEI records.
- Entities merge only through exact, authority-scoped identifiers
  (`dgsfp:clave`, `bde:european_code`, `bde:supervisor_code`,
  `eiopa:identification_code`, `lei`). Every merge records a
  `merge_basis` — name similarity is diagnostic-only, never canonical.
- First-class preservation of: unresolved LPS identities (616 active
  L-keys without LEI), identifier lifecycle conflicts (L1522), attribute
  conflicts (L1319 country disagreement), undetermined-identifier subjects
  (branch LEIs), and unresolved registration links (EIOPA FTS operations
  with no DGSFP L-key).
- Assertion-level provenance: every claim carries source system,
  jurisdiction, URL, snapshot date, retrieval timestamp, content hash,
  raw file and parser version.
- Byte-deterministic JSONL export (`data/derived/v0.1/`), with
  `generated_at` derived from input snapshots — identical inputs produce
  identical bytes and sha256.

## Build & verify

```bash
python -m scripts.build_v01_export   # rebuild data/derived/v0.1/
python -m pytest                     # 38 tests: G0 invariants + v0.1 contract
```

Frozen-input layout: `data/raw/` (immutable snapshots) → `data/derived/`
(regenerable). `evidence/` pins G0 artifacts by hash.

## Repository layout

```
opendgsfp/    canonical domain model (schema, build, export) — no transport
scripts/      G0 builders + v0.1 export builder
tests/        arithmetic invariants + contract tests
docs/gates/   G0 and v0.1 gate documents (frozen decisions)
data/raw/     frozen source snapshots (immutable)
data/derived/ reproducible derived artifacts
evidence/     G0 evidence ledger + source manifest
third_party/  insurance-register-ontology (submodule, see notices)
```

## License & attribution

- **Code:** MIT (see `LICENSE`).
- **Bundled donor submodule:** see `THIRD_PARTY_NOTICES.md`
  (MIT pipeline / CC BY 4.0 ontology-docs).
- **Official data** under `data/`: not MIT-licensed; each source retains
  its publisher's terms (see `THIRD_PARTY_NOTICES.md`).
