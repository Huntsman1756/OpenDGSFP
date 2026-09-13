# Roadmap

This roadmap is directional, not a promise or release schedule. Work is accepted when evidence and consumer need justify it; scope is not expanded merely to make the repository look feature-rich.

## Current: v0.1 hardening

Completed foundations:

- G0 source-access/identity feasibility gate frozen;
- exact identity fabric over DGSFP, BdE/Eurosystem, EIOPA and GLEIF;
- canonical read-only domain model;
- conflict/unresolved/provenance semantics;
- deterministic JSONL golden export;
- contract/regression tests;
- GitHub Actions reproducibility gate;
- OSS licensing/governance baseline.

Remaining release-quality work is primarily documentation/review/release hygiene rather than new product layers.

## Candidate next work

### 1. Upstream generic improvements

Prefer contributing generic improvements to `insurance-register-ontology` where they belong. Current candidate: GLEIF lifecycle/successor metadata and cache migration (upstream issue #1).

### 2. Snapshot refresh/versioning design

Before live/incremental ingestion, define a new gate for:

- versioned raw snapshots;
- source-specific refresh cadence;
- snapshot-to-snapshot deltas;
- tombstones/end-dates rather than destructive overwrite;
- reproducible historical lookup;
- changed-identity/conflict reporting.

No production scheduler should be added before this contract exists.

### 3. Consumer/query surface

Only after a concrete consumer exists, expose the core through the smallest useful transport (for example a local Python query layer or CLI). API/MCP/frontend are not automatic milestones.

The domain model must remain transport-independent.

## Deferred verticals

Evidence from G0 shows viable expansion paths, but they are outside v0.1:

- pensions: gestoras, fondos, planes, depositarias and IORP relationships;
- intermediaries/PUI: large Spanish-only population with no equivalent EIOPA entity dataset;
- financial/statistical series: DGSFP balances/accounts and EIOPA Solvency II data;
- historical regulatory-state changes.

Each vertical requires its own bounded gate before entering the canonical product.

## Explicit non-goals without a demonstrated need

- LLM/agent identity resolution;
- fuzzy canonical matching;
- vector database/RAG as identity infrastructure;
- cloud deployment merely for demonstration;
- complex frontend before there is a stable consumer contract;
- replacing official registers or representing OpenDGSFP as authoritative legal status.

## Release criteria

A future tagged release should have:

- green CI on the release commit;
- deterministic golden export;
- schema/version decision documented;
- updated changelog;
- current third-party notices;
- citation metadata;
- no undocumented identity-semantic change;
- release notes that identify source snapshot dates and known bounded gaps.