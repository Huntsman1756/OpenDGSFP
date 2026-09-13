# Contributing

OpenDGSFP is a small, evidence-preserving project. Before writing code, read:

1. `docs/gates/V0.1.md` — frozen semantic contract;
2. `docs/ARCHITECTURE.md` — system boundaries and change control;
3. `docs/DATA_MODEL.md` — entity/relation/assertion semantics;
4. `docs/DATA_SOURCES_AND_PROVENANCE.md` — source and provenance rules;
5. `GOVERNANCE.md` — decision and upstream policy.

## Development setup

Clone with the pinned submodule:

```bash
git clone --recurse-submodules https://github.com/Huntsman1756/OpenDGSFP.git
cd OpenDGSFP
```

CI uses Python 3.11. Run the suite with:

```bash
python -m pytest tests/ -q
```

Rebuild the canonical export with:

```bash
python -m scripts.build_v01_export
git diff --exit-code -- data/derived/v0.1/
```

See `docs/REPRODUCIBILITY.md` for the complete reproducibility procedure.

## Non-negotiable rules

1. **Exact identity only.** Canonical edges/merges require an exact official identifier (DGSFP key, BdE code, EIOPA code, LEI) or an explicit official bridge. Name similarity may generate candidates or diagnostics — never canonical identity. Every merge must carry a `merge_basis` entry (`SHARED_LEI`, `SHARED_DGSFP_KEY`, `SHARED_AUTHORITY_SCOPED_ID`, `OFFICIAL_BRIDGE`).
2. **Preserve contradictions.** Source disagreements are first-class conflicts/assertions; never normalize them away. Absence of an identifier is not a conflict.
3. **Preserve subject semantics.** A branch/presence is not collapsed into a home undertaking merely because a record publishes the home LEI. Prove what an identifier identifies before attaching it canonically.
4. **Provenance on every assertion.** Record source system, jurisdiction, URL, snapshot date, `retrieved_at`, `content_sha256`, raw file and parser version. There is no global source snapshot date.
5. **Determinism.** `data/derived/` must be byte-reproducible from frozen inputs. No wall-clock timestamps or platform-dependent line endings inside canonical hashed material.
6. **Raw is immutable.** Never rewrite frozen `data/raw/` or G0 artifacts under `evidence/` to make a later result pass.
7. **Contract before semantics.** If identity/conflict/provenance semantics need to change, update the relevant gate/contract before implementation.
8. **Prefer upstream reuse.** Generic donor fixes should be proposed upstream when appropriate rather than maintained indefinitely as downstream divergence.

## Branch and PR workflow

Prefer small pull requests with one concern:

- `fix/...`
- `feat/...`
- `docs/...`
- `chore/...`

Use the repository pull-request template. A PR that changes the golden export must report the semantic reason, relevant count deltas and the new manifest hash.

The minimum local verification floor is:

```bash
python -m pytest tests/ -q
python -m scripts.build_v01_export
git diff --exit-code -- data/derived/v0.1/
```

CI must also be green before merge. A green local run is not a substitute for the GitHub Actions result.

## Data-quality contributions

When reporting a register disagreement or missing crosswalk, include:

- exact identifier(s);
- source system(s);
- source/snapshot dates;
- URL/file path;
- hashes where available;
- what each source asserts;
- whether the issue could be snapshot lag rather than identity disagreement.

Use the Data quality issue template where possible.

## Third-party work

Do not copy upstream code into OpenDGSFP without preserving its license/attribution. The donor is kept as a pinned submodule; generic improvements should follow `docs/UPSTREAM.md`.

Adding a dependency or external dataset may require updating `THIRD_PARTY_NOTICES.md`.

## Security and conduct

- Security-sensitive reports: `SECURITY.md`.
- Participation expectations: `CODE_OF_CONDUCT.md`.

Do not include credentials, secrets or unnecessary personal data in issues, fixtures or pull requests.