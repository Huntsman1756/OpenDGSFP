# Upstream relationship

OpenDGSFP deliberately reuses existing open-source work instead of rebuilding the EIOPA/GLEIF foundation from scratch.

## Donor project

Upstream:

`fabio-rovai/insurance-register-ontology`

Location in this repository:

`third_party/insurance-register-ontology`

The donor is a git submodule pinned to an exact upstream commit. The pinned SHA is part of repository state and should only move through an explicit pull request.

See `THIRD_PARTY_NOTICES.md` for licensing and attribution.

## What OpenDGSFP reuses

The donor informed/reuses generic mechanisms including:

- EIOPA bulk-register export/postback handling;
- LEI checksum validation;
- the general discipline of treating identifiers and cross-register disagreement as first-class data.

OpenDGSFP's Spanish DGSFP/BdE integration, canonical JSONL model, gate/evidence process and source-specific crosswalks are downstream-specific work.

## What should go upstream

A change is a good upstream candidate when it is:

- independent of Spanish DGSFP/BdE semantics;
- useful to other users of the donor;
- compatible with the donor's ontology/pipeline goals;
- small enough to review independently;
- supported by reproducible evidence or fixtures.

Examples include generic GLEIF lifecycle handling, cache correctness, cross-register provenance or defensive matching logic.

## Contribution workflow

1. identify the generic defect/gap downstream;
2. confirm it exists in upstream `main`;
3. open an upstream issue before a design-heavy PR when scope is not obvious;
4. prepare/test a minimal local spike if useful;
5. wait for maintainer scope guidance when the issue asks a design question;
6. fork/push only when there is a reasonable contribution shape;
7. keep the upstream PR free of OpenDGSFP-specific requirements;
8. after upstream acceptance, update the submodule SHA in a separate OpenDGSFP PR;
9. document any downstream behavior change caused by the new pin.

## Current upstream work

Donor issue #1 proposes preserving GLEIF lifecycle/successor metadata currently discarded by the harvester:

`Preserve GLEIF lifecycle and successor metadata in harvested LEI records`

The proposed scope is intentionally generic: expiration data, successor declarations, relevant legal-entity events, cache migration and an informational governance-report breakdown. It must not infer successor identity where GLEIF does not formally declare it.

Until an upstream PR is accepted/merged, OpenDGSFP must describe this work as a proposal rather than an upstream capability. Experimental downstream/local spikes are implementation evidence only; they do not change the pinned donor behavior on `main`.

## Submodule updates

Do not run a casual `git submodule update --remote` and commit whatever upstream currently returns.

A submodule bump should state:

- old SHA;
- new SHA;
- upstream issue/PR/release motivating the bump;
- behavior affected in OpenDGSFP;
- tests run;
- whether the canonical export changed.

If an upstream change modifies semantics rather than implementation details, review `docs/gates/V0.1.md` before updating the pin.