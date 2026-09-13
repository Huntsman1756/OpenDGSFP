# Data sources and provenance

OpenDGSFP is built from public regulatory/statistical sources. The project does not treat any source as a complete master database. Each source is retained with its own scope, snapshot date, identifiers and known limitations.

Licensing/reuse terms are summarized in `THIRD_PARTY_NOTICES.md`. This document describes technical semantics, not legal advice or a grant of rights.

## DGSFP RRPP

Role in OpenDGSFP:

- Spanish administrative keys (`C/M/P/R/E/L`);
- registration state and Spanish supervisory facts;
- branch/LPS presence in Spain;
- NIF and LEI where the public record publishes them.

Important semantics:

- `E0000` / `L0000` are search-category/bucket semantics, not the identity of every foreign entity;
- individual `Exxxx` and `Lxxxx` keys exist;
- a LEI displayed on an `E` record can describe the home undertaking rather than the branch-presence node, so identifier subject is resolved before canonical assignment;
- many active `L` registrations do not publish a LEI in RRPP.

The G0 snapshot captured 2,759 individual RRPP detail pages and pinned their hashes.

## Banco de España / Eurosystem IC lists

Role in OpenDGSFP:

- Spanish `CÓDIGO DE SUPERVISOR` crosswalk to DGSFP keys;
- `CÓDIGO EUROPEO` statistical identifiers;
- `ENTIDAD MATRIZ` links for Spanish branches;
- home-country IC-list resolution;
- LEI where published.

Important semantics:

- `bde:european_code` is a statistical/Eurosystem identifier, not the same namespace as EIOPA's NCA `Identification code`;
- each national IC list has its own publication/Last-Modified date;
- no single global "BdE snapshot date" exists;
- coverage varies by country and entity type;
- source lag versus DGSFP is expected and must not be treated automatically as an identity failure.

## EIOPA Register of Insurance Undertakings

Role in OpenDGSFP:

- home NCA identification code;
- home country and NCA;
- LEI where populated;
- cross-border branch/FPS operations and dates.

Important semantics:

- EIOPA rows mix home registrations and cross-border operations; counting rows is not counting undertakings;
- Spanish domestic `Identification code` can equal the DGSFP key, but this is not generalized outside Spain;
- EIOPA explicitly states that national-register information should prevail in case of discrepancy;
- cross-border operation identity can be exact even if a Spanish DGSFP `L` registration cannot be linked exactly.

## GLEIF

Role in OpenDGSFP:

- LEI checksum/reference validation;
- legal name and jurisdiction;
- entity/registration status.

GLEIF is authoritative for the LEI reference record, not for insurance authorization or passporting.

OpenDGSFP's current v0.1 snapshot uses the fields harvested in G0. Lifecycle/successor enrichment is being proposed upstream to the donor project and is not silently assumed in the current canonical model.

## Provenance block

Every source assertion carries at least:

```text
source_system
jurisdiction
source_url
source_snapshot_date
retrieved_at
content_sha256
parser_version
raw_file
evidence_tier
```

`source_snapshot_date` is the source's effective/publication date when available. `retrieved_at` is capture time. They are intentionally distinct.

## Evidence tiers

The project uses the G0 evidence convention:

- `T0_PRIMARY_DIRECT`: directly structured primary data/API/bulk export.
- `T1_PRIMARY_DOCUMENT`: official published document or official downloadable file.
- `T2_PRIMARY_UI`: official public UI/detail page.
- `T3_DERIVED_REPRODUCIBLE`: exact deterministic derivation from primary evidence.
- `T4_DONOR`: reusable mechanism/claim inherited from the pinned donor and independently bounded.
- `T5_MANUAL_REVIEW`: human review where automation cannot provide equivalent evidence.

Evidence tier is not a confidence score. It describes how the evidence was obtained.

## Snapshot alignment

Cross-source comparison must record snapshot skew explicitly. A row present in DGSFP but absent from an older BdE national list can be a temporal difference rather than a failed identity link.

Population reconciliation should therefore report:

```text
source A snapshot date
source B snapshot date
unit counted
filters applied
unmatched residuals
```

before interpreting a count difference.

## Source precedence

Precedence is domain-specific:

- Spanish supervisory status/registration: DGSFP first.
- LEI reference status: GLEIF first.
- EEA register/passporting view: EIOPA.
- statistical IC-list relationships/codes: BdE/Eurosystem.

Precedence never means deletion of conflicting assertions. The lower-precedence assertion remains in the evidence model.

## Raw and derived material

`data/raw/`
: Frozen source captures. Immutable once admitted into a frozen gate/snapshot.

`data/derived/`
: Regenerable outputs, including parsed source representations and the canonical v0.1 export.

`evidence/source-manifest.json`
: Hash and retrieval metadata for source artifacts.

`evidence/evidence-ledger.json`
: G0 evidence statements and demonstrated edges/gaps.

## Adding or refreshing a source

A future source refresh must not overwrite a frozen historical snapshot in place. The expected workflow is:

1. capture the new source artifact;
2. record retrieval and source dates;
3. hash the raw artifact;
4. parse into a new derived snapshot;
5. compare counts and residuals against the previous snapshot;
6. rerun identity/conflict invariants;
7. version the resulting dataset or gate explicitly.

Incremental/live source-refresh infrastructure is intentionally outside v0.1.