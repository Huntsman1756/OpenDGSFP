# Project governance

OpenDGSFP is currently a maintainer-led open-source project. Governance is deliberately lightweight, but changes to identity semantics, source interpretation and reproducibility are evidence-driven and reviewable.

## Maintainer model

The repository owner is the current project maintainer and final integrator for releases and changes to `main`.

Contributions are welcome through GitHub issues and pull requests. There is no committee, voting process or promise of response-time SLA at this stage.

## Decision principles

Technical decisions are evaluated in this order:

1. primary-source evidence;
2. exact/reproducible identifiers and crosswalks;
3. preservation of contradictions and provenance;
4. deterministic/reproducible outputs;
5. minimal complexity;
6. reuse of appropriate upstream open-source work before new implementation.

Convenience, name similarity or aesthetic data cleaning do not override source evidence.

## Contract-before-code changes

Identity, conflict, provenance and canonical merge semantics are governed by frozen gate documents under `docs/gates/`.

For a semantic change:

1. document the observed problem and evidence;
2. update/propose the relevant gate or decision contract;
3. review expected behavior and regression cases;
4. implement only after the contract change is explicit;
5. regenerate the golden export if required;
6. merge with tests and provenance intact.

G0 is frozen at tag `g0` and is historical evidence. It must not be rewritten to make later implementation cleaner.

## Pull request policy

Prefer small pull requests with one concern:

- `fix/...` for corrections;
- `feat/...` for bounded functionality;
- `docs/...` for documentation;
- `chore/...` for CI/governance/tooling.

A PR that changes canonical output should state:

- why bytes changed;
- entity/relation count changes;
- conflict/unresolved count changes where relevant;
- new golden SHA-256;
- test result;
- whether the frozen contract changed.

## Upstream-first policy

OpenDGSFP reuses `fabio-rovai/insurance-register-ontology` as a pinned donor/submodule. Generic fixes that belong in the donor should be proposed upstream when practical rather than permanently maintained as downstream divergence.

Downstream-specific Spanish DGSFP/BdE integration remains in OpenDGSFP.

See `docs/UPSTREAM.md` for the current relationship and contribution workflow.

## Release policy

Until a formal release is tagged, `main` is development state and `schema_version` is the compatibility boundary for exported data.

A release should only be tagged after:

- CI is green;
- golden export is reproducible;
- release notes describe schema/data changes;
- third-party notices are current;
- source snapshot provenance is complete.

Semantic changes to the export require an explicit schema-version decision; they must not be smuggled into an unchanged schema identifier.

## Security and data-quality reports

Security concerns follow `SECURITY.md`.

Data-quality disagreements should include the exact source, identifier, snapshot date and evidence whenever possible. A report that one source is "wrong" is not sufficient without reproducible evidence.

## Scope discipline

The project intentionally avoids adding API, frontend, MCP, LLM/agent or cloud infrastructure merely because those layers are easy to demonstrate. Transport and presentation layers should be introduced only when the read-only canonical core has a concrete consumer and the added complexity is justified.