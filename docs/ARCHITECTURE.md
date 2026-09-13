# Architecture

OpenDGSFP is a read-only identity and provenance layer over public insurance-register data. The core design goal is not to manufacture a single clean master record; it is to preserve what each official source asserts, link records only through exact evidence, and expose unresolved or contradictory cases explicitly.

## System boundary

v0.1 consumes frozen snapshots from four source families:

- DGSFP RRPP: Spanish regulatory keys and registrations (`C/M/P/R/E/L`).
- Banco de España / Eurosystem IC lists: statistical entity codes, supervisor codes, branch-parent links and LEIs where published.
- EIOPA Register of Insurance Undertakings: NCA identification codes, home undertakings and cross-border operations.
- GLEIF: LEI validation and legal-entity reference data.

The core under `opendgsfp/` is transport-independent. There is no API, CLI, MCP server, database or frontend in v0.1.

## Data flow

```text
official source snapshots
        |
        v
  source loaders
  opendgsfp/sources.py
        |
        v
source assertions + registrations + operations
        |
        v
 exact identity/crosswalk build
  opendgsfp/build.py
        |
        +----> entities
        +----> relations
        +----> conflicts
        +----> diagnostics
        |
        v
 deterministic serializer
  opendgsfp/export.py
        |
        v
 data/derived/v0.1/
```

`data/raw/` is immutable input evidence. `data/derived/` is reproducible output. `evidence/` contains the G0 source manifest and evidence ledger. The frozen design contract is `docs/gates/V0.1.md`.

## Identity model

Canonical identity is based only on exact, authority-scoped evidence. Supported merge bases are:

- `SHARED_LEI`
- `SHARED_DGSFP_KEY`
- `SHARED_AUTHORITY_SCOPED_ID`
- `OFFICIAL_BRIDGE`

Name similarity is diagnostic-only. It may generate a candidate relation, but it cannot create a canonical entity merge.

Each canonical merge records `merge_basis`, the identifier used, and evidence assertions. The contract test suite enforces that multi-source canonical entities have an exact merge basis.

## Entity and presence separation

The model deliberately distinguishes a legal undertaking from a regulatory or market presence.

A DGSFP `E` registration remains an `EEA_BRANCH` node even when the DGSFP branch record publishes the home undertaking's LEI. The branch is linked to a distinct home undertaking through `BRANCH_OF`; a home LEI observed on the branch record is evidence about the home undertaking, not a reason to collapse both nodes.

Likewise, an LPS registration is a registration/operation of an undertaking, not a separate legal-person type.

## Identity and linkage states

Entity identity and source coverage are orthogonal:

```text
identity_status = EXACT | CONFLICT | UNRESOLVED
source_coverage = MULTI_SOURCE | SOURCE_ONLY
```

Relations have their own state:

```text
link_status = EXACT | UNRESOLVED | CONFLICT
```

This permits cases such as an exactly identified EIOPA undertaking whose relationship to a DGSFP `Lxxxx` registration is still unresolved.

## Assertions, provenance and conflicts

Every source claim is an assertion with provenance. Derived relations point back to the assertions that justify them. Conflicts are not resolved by choosing a preferred value inside the core; they remain first-class records.

Examples:

- identifier lifecycle conflict: DGSFP publishes a stale LEI while another source publishes a different current LEI;
- attribute conflict: sources disagree on home country while identity remains exact;
- identifier-subject uncertainty: a register publishes an LEI but the evidence is insufficient to prove whether it identifies the branch presence or the home undertaking.

## Source precedence

Source precedence is contextual, not a global master-source rule. For Spanish supervisory facts, DGSFP is the primary national source; EIOPA itself states that national-register information prevails in case of discrepancy. GLEIF is authoritative for LEI reference-record status, not for insurance authorization. Banco de España IC lists provide a separate statistical identity layer.

A higher-precedence source does not erase lower-precedence assertions; precedence guides interpretation while provenance preserves both.

## Determinism

Stable output is a design invariant:

- content-derived IDs;
- stable ordering of entities, relations and assertions;
- canonical UTF-8 JSON serialization;
- no wall-clock timestamps in hashed canonical material;
- `generated_at` derived from input snapshot dates;
- committed golden export rebuilt in CI and compared byte-for-byte.

The v0.1 schema is `opendgsfp/0.1`; parser/core version is declared in `opendgsfp/__init__.py`.

## Change control

The project uses contract-before-code development for identity semantics:

1. establish evidence and failure modes;
2. freeze a gate/scope document;
3. implement against that contract;
4. preregister and run invariants;
5. update the contract first if semantics must change.

G0 remains frozen at tag `g0`. Changes to identity, conflict, provenance or canonical-merge semantics require an explicit update to `docs/gates/V0.1.md` before implementation.