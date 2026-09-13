# Changelog

All notable project changes are documented here. OpenDGSFP has not yet published a formal v0.1 release; entries below describe development milestones on `main`.

## Unreleased

### Documentation / governance

- Comprehensive architecture, data-model, provenance, reproducibility and upstream documentation.
- Security policy, code of conduct, governance model and GitHub contribution templates.
- Citation metadata and project documentation index.

## Development milestones — 2026-09-13

### G0 frozen — `42bb59d` / tag `g0`

- Completed source-access and exact-identity feasibility work.
- Froze evidence ledger, source manifest, raw snapshots and reproducible derived evidence.
- Formal verdict: `BUILD_WITH_BOUNDED_GAPS`.

### v0.1 contract — `ab6f4da`

- Froze the read-only v0.1 identity/provenance contract.
- Defined authority-scoped identifiers, entity/relation separation, conflict policy, deterministic export and no-fuzzy canonical identity.

### v0.1 core — `ac5e317`

- Implemented the transport-independent canonical domain model.
- Added deterministic JSONL export and v0.1 contract tests.
- Preserved branch/home subject semantics, unresolved LPS links, conflicts and assertion-level provenance.

### OSS governance — `30b51ab`

- Added MIT software license scope, third-party notices, README and contribution policy.
- Separated software licensing from official-source data reuse terms.

### Reproducible CI — `96c63b7`

- Added GitHub Actions verification for the test suite and deterministic golden rebuild.
- Fixed platform-dependent CRLF/LF serialization of `manifest.json`; canonical derived files are now written with explicit LF bytes across Windows/Linux.

## Versioning notes

- `g0` is an immutable evidence milestone, not a software release.
- Export compatibility is governed by `schema_version` (`opendgsfp/0.1` in the current core).
- Future tagged releases should reference the exact source snapshots and canonical export manifest used.