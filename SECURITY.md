# Security policy

OpenDGSFP is a read-only research/engineering project over public regulatory data. It does not currently expose a network service, authentication system or write path to source systems, but security issues can still exist in parsers, CI, dependency handling, generated artifacts or future interfaces.

## Supported code

Security fixes target the current `main` branch. Historical tags such as `g0` are immutable evidence snapshots and are not patched in place.

## Reporting a vulnerability

Do not publish exploit details in a normal issue when the report could put users or downstream systems at risk.

Preferred route:

1. use GitHub's private vulnerability-reporting / Security Advisory flow for this repository if it is available;
2. if private reporting is unavailable, open a minimal public issue stating that you have a security concern and avoid including exploit payloads, secrets or sensitive reproduction details until a private channel is agreed.

For non-security data-quality problems, use a normal issue and include the relevant source, identifier, snapshot and reproducible evidence.

## What qualifies as security-sensitive

Examples include:

- arbitrary code execution through parser/input handling;
- path traversal or unsafe file writes;
- CI workflow injection or excessive GitHub token permissions;
- dependency/submodule substitution or supply-chain compromise;
- secret leakage;
- malicious source content causing unsafe behavior in future consumers;
- integrity bypasses that allow derived artifacts to appear reproducible when they are not.

Incorrect regulatory data, stale identifiers or source disagreements are normally data-quality/provenance issues rather than security vulnerabilities unless they can be exploited to compromise software or users.

## Security design principles

Current safeguards include:

- read-only source handling;
- immutable frozen raw snapshots;
- SHA-256 source and artifact integrity checks;
- minimal CI scope;
- no repository secrets required for normal verification;
- pinned donor submodule commit;
- exact-identifier identity policy rather than heuristic canonical merges;
- deterministic derived output checked in CI.

## No warranty / no operational authorization

OpenDGSFP is not an authorization service, sanctions-screening service, insurance supervisory system or source of legal advice. Consumers remain responsible for validating source freshness and fitness for their use case.