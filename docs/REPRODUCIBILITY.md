# Reproducibility

OpenDGSFP treats reproducibility as a product requirement, not a convenience. A frozen set of inputs must regenerate the committed canonical export byte-for-byte.

## Reference environment

CI currently uses:

- Ubuntu GitHub-hosted runner;
- Python 3.11;
- `pytest` for the regression suite.

The core itself is intentionally lightweight and transport-independent.

## Clone

The donor repository is a pinned git submodule. Clone with:

```bash
git clone --recurse-submodules https://github.com/Huntsman1756/OpenDGSFP.git
cd OpenDGSFP
```

or initialize after a normal clone:

```bash
git submodule update --init --recursive
```

The submodule commit is part of repository state; do not update it implicitly during verification.

## Verify tests

```bash
python -m pytest tests/ -q
```

The suite combines G0 invariants and v0.1 contract/regression tests. Tests cover, among other things:

- raw hash integrity;
- exact-only canonical identity;
- branch/home separation;
- unresolved LPS preservation;
- conflict preservation;
- provenance completeness;
- deterministic serialization;
- canonical merge basis invariants.

Do not treat a locally green suite as CI success. Pull requests and pushes to `main` are verified by GitHub Actions.

## Rebuild the v0.1 golden export

```bash
python -m scripts.build_v01_export
```

Expected outputs live under:

```text
data/derived/v0.1/opendgsfp-0.1.jsonl
data/derived/v0.1/manifest.json
```

The rebuild must leave the committed golden unchanged:

```bash
git diff --exit-code -- data/derived/v0.1/
```

Any diff is meaningful. Do not normalize it away without first explaining why the canonical bytes changed.

## Hash verification

`manifest.json` is the source of truth for the golden export hash. Consumers should calculate SHA-256 on `opendgsfp-0.1.jsonl` and compare it with the manifest rather than copying a hash into scripts or documentation.

A generic check is:

```python
import hashlib, json, pathlib

base = pathlib.Path("data/derived/v0.1")
manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
actual = hashlib.sha256((base / "opendgsfp-0.1.jsonl").read_bytes()).hexdigest()
assert actual == manifest["data_sha256"]
```

## Canonical serialization

The v0.1 export is deterministic because it uses:

- UTF-8;
- stable record ordering;
- stable object-key ordering;
- explicit JSON `null` for absence;
- LF (`\n`) line endings in canonical files;
- content-derived identifiers;
- `generated_at` derived from source snapshot dates rather than wall-clock build time.

### Cross-platform line endings

Canonical artifacts must not depend on the host platform's default newline behavior. The project writes canonical material explicitly as UTF-8 bytes/LF. This requirement is enforced because a Windows CRLF vs Linux LF difference previously caused a reproducibility gate failure even though domain logic was unchanged.

## Clean-tree expectation

After a verification rebuild, the working tree should remain clean for tracked golden artifacts:

```bash
git status --porcelain
```

A dirty tree after a supposedly deterministic build is a failure signal, not normal output.

## Frozen inputs

The G0 source set is frozen under `data/raw/` and `evidence/`. Reproducibility of v0.1 means regenerating from those frozen inputs, not silently downloading current live sources.

This distinction matters because DGSFP, BdE, EIOPA and GLEIF are living systems. A live refresh is a new snapshot and must be versioned as such.

## CI contract

`.github/workflows/ci.yml` is intentionally small. Its purpose is to prove the current repository state, not to deploy or refresh sources.

At minimum, CI must continue to prove:

```text
tests pass
+ canonical export rebuilds from frozen inputs
+ committed golden does not change
```

Additional checks may be added, but they should not weaken or replace these invariants.

## When the golden legitimately changes

A golden change requires all of the following:

1. an intentional code or contract change;
2. regenerated derived artifacts;
3. passing tests;
4. an explainable semantic diff;
5. updated manifest/hash;
6. PR text stating why entity/relation counts or bytes changed.

For changes to identity/conflict/provenance semantics, update the frozen contract before implementation.