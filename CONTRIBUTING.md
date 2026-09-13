# Contributing

Small, evidence-preserving project. Before writing code, read
`docs/gates/V0.1.md` — it is the frozen contract.

## Non-negotiable rules

1. **Exact identity only.** Canonical edges require an exact official
   identifier (DGSFP key, BdE code, EIOPA code, LEI) or a single-artifact
   official bridge. Name similarity may generate candidates or
   diagnostics — never canonical identity. Every merge must carry a
   `merge_basis` entry (`SHARED_LEI`, `SHARED_DGSFP_KEY`,
   `SHARED_AUTHORITY_SCOPED_ID`, `OFFICIAL_BRIDGE`).
2. **Preserve contradictions.** Source disagreements are first-class
   `conflicts` on assertions; never normalize them away. Absence of an
   identifier is not a conflict.
3. **Provenance on every assertion.** source system, jurisdiction, URL,
   snapshot date, retrieved_at, content_sha256, raw_file, parser_version.
   No global snapshot date — each source artifact keeps its own.
4. **Determinism.** `data/derived/` must be byte-reproducible from
   `data/raw/`. No wall-clock timestamps inside canonical hashed material.
5. **Raw is immutable.** Never modify `data/raw/` or G0 artifacts under
   `evidence/`; derived artifacts are regenerable.

## Workflow

- Small PRs, one concern each (e.g. `feat/...`, `chore/...`, `fix/...`).
- `python -m pytest` must stay green — G0 arithmetic invariants and the
  v0.1 contract tests are the regression floor.
- If a change alters the golden export, rebuild via
  `python -m scripts.build_v01_export` and commit the new
  `data/derived/v0.1/` artifacts + hash.
- Changes to the identity/conflict/provenance model require updating
  `docs/gates/V0.1.md` first — contract before code.
