# OpenDGSFP

[![CI](https://github.com/Huntsman1756/OpenDGSFP/actions/workflows/ci.yml/badge.svg)](https://github.com/Huntsman1756/OpenDGSFP/actions/workflows/ci.yml)
[![License: MIT (code)](https://img.shields.io/badge/code%20license-MIT-blue.svg)](LICENSE)

A read-only, reproducible identity and provenance layer for Spanish insurance entities, built over official public registers.

Public sources disagree: names differ between registers, identifiers go stale, snapshots lag each other, and 74.7% of active DGSFP `L` registrations in the frozen G0 snapshot (616/825) do not publish a LEI in RRPP. OpenDGSFP does not fabricate a clean master database: it preserves evidence, conflicts and documented gaps, and only builds canonical identity on **exact official identifiers**.

## Status

- **G0 — frozen**: tag `g0`, commit `42bb59d`; verdict `BUILD_WITH_BOUNDED_GAPS`.
- **v0.1 scope — frozen**: `docs/gates/V0.1.md`.
- **v0.1 canonical core — implemented**: transport-independent model + deterministic JSONL export.
- **CI — active**: tests and golden-export reproducibility run on pull requests and `main`.

OpenDGSFP is currently a development project rather than a tagged v0.1 release. Use an exact commit/tag when citing or consuming results.

## Why it exists

The useful problem is not downloading another register. It is reconciling different official identity systems without silently inventing certainty.

OpenDGSFP combines:

```text
DGSFP RRPP
     |
     +---- Spanish registration / C-M-P-R-E-L keys
     |
Banco de España / Eurosystem IC lists
     |
     +---- statistical codes / branch-parent graph
     |
EIOPA Register of Insurance Undertakings
     |
     +---- home NCA identity / passporting
     |
GLEIF
     |
     +---- LEI reference identity and status
```

The resulting model keeps source assertions, exact crosswalks, unresolved relationships and contradictions separately queryable.

## Design principles

1. **Exact identity only.** Names can generate diagnostics/candidates, never canonical merges.
2. **Authority-scoped identifiers.** DGSFP keys, BdE/Eurosystem codes, EIOPA NCA codes and LEIs remain distinct schemes.
3. **Presence is not automatically a legal person.** Branch/presence nodes remain addressable and link to home undertakings explicitly.
4. **Contradictions are data.** Source disagreement is preserved, not normalized away.
5. **Assertion-level provenance.** Every canonical claim can be traced to a source artifact and snapshot.
6. **Deterministic outputs.** Frozen inputs regenerate the golden export byte-for-byte.
7. **Upstream-first OSS.** Generic donor improvements are proposed upstream where they belong.

## What v0.1 does

- Canonical model over **DGSFP**, **Banco de España/Eurosystem IC lists**, **EIOPA** and **GLEIF**.
- Exact identifier lookups and recorded `merge_basis` for every canonical merge.
- Branch → home-undertaking relations without collapsing the branch presence.
- Cross-border/passporting operations as first-class records.
- `EXACT`, `CONFLICT` and `UNRESOLVED` identity states, separate from source coverage.
- Attribute/identifier conflicts and unresolved cross-register links.
- Assertion-level provenance including source, jurisdiction, URL, snapshot, retrieval time, raw hash and parser version.
- Byte-deterministic canonical JSONL export under `data/derived/v0.1/`.

Representative edge cases are documented in `docs/DATA_MODEL.md`.

## Quick start

Clone with the pinned donor submodule:

```bash
git clone --recurse-submodules https://github.com/Huntsman1756/OpenDGSFP.git
cd OpenDGSFP
```

Run the regression suite:

```bash
python -m pytest tests/ -q
```

Rebuild the canonical v0.1 export:

```bash
python -m scripts.build_v01_export
```

Confirm it reproduces the committed golden:

```bash
git diff --exit-code -- data/derived/v0.1/
```

CI uses Python 3.11. See `docs/REPRODUCIBILITY.md` for the reproducibility contract, cross-platform newline requirements and hash verification.

## Documentation

| Document | Purpose |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Components, data flow, identity boundaries and change control |
| [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) | Entity/relation/assertion/conflict semantics and edge cases |
| [`docs/DATA_SOURCES_AND_PROVENANCE.md`](docs/DATA_SOURCES_AND_PROVENANCE.md) | Source roles, evidence tiers, snapshot alignment and precedence |
| [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) | Clone/build/test/golden/hash reproducibility procedure |
| [`docs/gates/G0.md`](docs/gates/G0.md) | Frozen feasibility/source-access gate |
| [`docs/gates/V0.1.md`](docs/gates/V0.1.md) | Frozen v0.1 identity/provenance contract |
| [`docs/UPSTREAM.md`](docs/UPSTREAM.md) | Donor relationship and upstream contribution policy |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Evidence-based direction and deferred verticals |
| [`GOVERNANCE.md`](GOVERNANCE.md) | Maintainer model and decision/release policy |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Development and contribution workflow |
| [`CHANGELOG.md`](CHANGELOG.md) | Development milestones and release history |
| [`SECURITY.md`](SECURITY.md) | Vulnerability-reporting and security scope |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Participation and technical-discussion expectations |
| [`SUPPORT.md`](SUPPORT.md) | Support boundaries and issue-reporting guidance |
| [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) | Donor attribution and official-data reuse terms |
| [`CITATION.cff`](CITATION.cff) | Software citation metadata |

## Repository layout

```text
opendgsfp/     canonical domain model, build and export logic
scripts/       G0 builders + v0.1 export builder
tests/         G0 invariants + v0.1 contract/regression tests
docs/gates/    frozen evidence/scope contracts
data/raw/      frozen source snapshots (immutable once gated)
data/derived/  reproducible derived artifacts
evidence/      G0 evidence ledger + source manifest
reports/       G0 reports/source hashes
third_party/   pinned insurance-register-ontology submodule
.github/       CI and contribution templates
```

## Data and licensing

The repository deliberately separates software licensing from source-data reuse rights.

- **OpenDGSFP code and project-authored documentation:** MIT; see `LICENSE`.
- **Donor submodule:** upstream license applies (MIT pipeline; CC BY 4.0 ontology/SKOS/SHACL/docs); see `THIRD_PARTY_NOTICES.md`.
- **Official data/captures:** not relicensed by OpenDGSFP. DGSFP, Banco de España, EIOPA and GLEIF material remains subject to the relevant publisher terms. Derived artifacts are covered by the project license only to the extent they do not incorporate/reproduce third-party source data subject to separate terms.

## Contributing

Read `CONTRIBUTING.md` and the frozen v0.1 contract before changing identity/provenance semantics. Small, evidence-backed pull requests are preferred.

For data disagreements, use the Data quality issue template and provide identifiers, source dates and reproducible evidence. For security concerns, follow `SECURITY.md`.

## Upstream work

OpenDGSFP reuses `fabio-rovai/insurance-register-ontology` rather than rebuilding the EIOPA/GLEIF foundation. Generic improvements are proposed upstream where appropriate. Current upstream work and submodule-update rules are tracked in `docs/UPSTREAM.md`.

## Citation

`CITATION.cff` is provided for software citation. Because source systems are live and identity semantics are versioned, cite the exact OpenDGSFP commit/tag used rather than only the repository name.

## Disclaimer

OpenDGSFP is an engineering/research artifact over public sources. It is not an official DGSFP, Banco de España, EIOPA or GLEIF service; it is not legal advice; and it should not be used as a substitute for checking the current authoritative register for operational or legal decisions.
