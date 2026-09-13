# Canonical data model

This document is a reader-oriented companion to the frozen v0.1 contract in `docs/gates/V0.1.md`. The gate document is normative; this file explains how to interpret the exported records.

## Entity

An entity represents a legal undertaking or a regulatory presence that must remain independently addressable.

Core fields:

```text
entity_id
entity_kind
identity_status
source_coverage
identifiers[]
registrations[]
cross_border_operations[]
source_assertions[]
conflicts[]
snapshots[]
diagnostics[]
merge_basis[]
```

### `entity_kind`

Current v0.1 values:

- `INSURANCE_UNDERTAKING`
- `REINSURANCE_UNDERTAKING`
- `EEA_BRANCH`
- `UNDERTAKING`

`EEA_BRANCH` is a presence node. It is deliberately not collapsed into its home undertaking merely because the branch record publishes the home LEI.

### `identity_status`

`EXACT`
: Identity is supported by exact official identifiers.

`CONFLICT`
: Official evidence attributes incompatible identity identifiers to the same asserted subject. This is stronger than an attribute disagreement.

`UNRESOLVED`
: A real registered entity/presence exists, but public evidence is insufficient to resolve its external identity exactly.

### `source_coverage`

`MULTI_SOURCE`
: At least two regulatory/statistical source systems assert the entity/presence.

`SOURCE_ONLY`
: Only one such source asserts it in the current snapshot.

GLEIF validates an identifier but is not counted as regulatory presence for this dimension.

## Identifier

Identifiers are authority-scoped. The same lexical value under different schemes is not automatically equivalent.

Current schemes include:

- `dgsfp:clave`
- `bde:supervisor_code`
- `bde:european_code`
- `eiopa:identification_code`
- `lei`
- `es:nif`

Country context is retained where required, especially for BdE/Eurosystem and NCA-scoped identifiers.

An identifier can be asserted by multiple source assertions. For LEIs, checksum validity is recorded separately from identity semantics.

## Registration

A registration records a source-specific regulatory/statistical registration rather than creating a new legal person by itself.

Examples:

- DGSFP `C0001`
- DGSFP `E0245`
- DGSFP `Lxxxx`
- EIOPA home undertaking registration
- BdE IC-list record

Registration state (`situacion`) and source registration type remain source assertions; the core does not silently normalize divergent source vocabularies.

## Cross-border operation

A cross-border operation records an undertaking operating into a host country under a particular regime.

Examples include EIOPA EEA FPS and branch operations and DGSFP LPS assertions.

Operation identity is distinct from legal-entity identity. An EIOPA operation into Spain can be exact even when the crosswalk to a DGSFP `Lxxxx` registration is unresolved.

## Relation

Relations are first-class records.

Core fields:

```text
edge_id
relation_type
endpoints[]
link_status
resolution_method[]
evidence[]
detail
```

### `link_status`

- `EXACT`: relation is supported by exact evidence.
- `UNRESOLVED`: relation is expected or a candidate exists, but no exact bridge is available.
- `CONFLICT`: authoritative evidence about the relation is incompatible.

### `resolution_method`

Current methods:

- `DGSFP_KEY`
- `LEI`
- `BDE_PARENT_CODE`
- `OFFICIAL_BRIDGE`
- `NONE`

`NONE` is valid only for unresolved relations. Names are never a canonical resolution method.

### Important relation types

`DGSFP_KEY_BDE_SUPERVISOR_CODE_EXACT`
: DGSFP key equals the supervisor code published by the Spanish BdE IC list.

`DGSFP_KEY_EIOPA_ID_EXACT`
: Spanish domestic EIOPA identification code equals DGSFP key; this equivalence is not generalized to other countries.

`BRANCH_PARENT_CODE_RESOLVES_HOME_ENTITY`
: `ENTIDAD MATRIZ` in the Spanish IC list resolves to the corresponding `CÓDIGO EUROPEO` in the home-country IC list.

`BRANCH_OF`
: A branch-presence node links to a distinct home undertaking.

`HOME_LEI_MATCHES_EIOPA_HOME_UNDERTAKING`
: Home undertaking LEI from the BdE/Eurosystem chain equals the EIOPA home undertaking LEI.

`LPS_REGISTER_KEY_PUBLISHES_LEI`
: A DGSFP LPS record publishes a LEI that resolves exactly to the home undertaking.

`LPS_REGISTRATION_LINK`
: Used as `UNRESOLVED` when an EIOPA FTS operation into Spain cannot be linked exactly to a DGSFP L key.

`IDENTIFIER_SUCCESSOR_CANDIDATE`
: Diagnostic/candidate relation only. It remains `UNRESOLVED` unless an official exact succession bridge exists.

## Assertion

An assertion is one claim by one source about one subject. Assertions are the atomic provenance unit.

Conceptually:

```text
subject
predicate
object
provenance
assertion_id
```

The same factual field may appear in multiple incompatible assertions. The canonical layer preserves them rather than overwriting one with another.

## Conflict

A conflict references the assertions that disagree.

Current categories include:

- identity-level conflicts, such as incompatible LEI assertions;
- attribute conflicts, such as home-country disagreement;
- identifier-assignment uncertainty, where a source publishes an identifier but its subject cannot be proven.

A missing value is not automatically a conflict.

## Merge basis

Whenever records are canonically merged into one entity, the entity records how that happened.

Allowed exact bases:

- `SHARED_LEI`
- `SHARED_DGSFP_KEY`
- `SHARED_AUTHORITY_SCOPED_ID`
- `OFFICIAL_BRIDGE`

The test suite enforces that canonical multi-source merges are backed by one of these exact bases.

## Representative edge cases

### L1522

DGSFP and EIOPA/GLEIF expose different LEIs for what appears to be the same undertaking. Without a formal exact successor bridge, the records are not silently merged by name. The project preserves the lifecycle conflict and candidate relation.

### L1319

Identity resolves exactly through a shared LEI, while sources disagree on home country. The entity remains `EXACT`; the country disagreement is an attribute conflict.

### E0245

A DGSFP branch record publishes the home undertaking's LEI. The branch remains an `EEA_BRANCH`; that LEI is evidence about the home undertaking and does not collapse branch and home nodes.

## Export semantics

The canonical JSONL export contains a manifest header followed by entity, relation and observation records. Object-key order and record order are deterministic. Consumers should treat `schema_version` as the compatibility boundary and should not infer semantics from display names when an exact identifier or status field exists.