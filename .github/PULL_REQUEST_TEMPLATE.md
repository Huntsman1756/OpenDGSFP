## Purpose

Describe the single concern this PR addresses.

## Evidence / issue

- Related issue(s):
- Source/specification evidence, if semantics change:

## Scope

- [ ] One bounded concern
- [ ] No unrelated refactor
- [ ] Frozen G0 artifacts left unchanged
- [ ] Identity/conflict/provenance semantics unchanged, **or** `docs/gates/V0.1.md` updated first

## Canonical-data impact

- [ ] No golden export change
- [ ] Golden export changed intentionally

If changed, report:

```text
entities:
relations:
EXACT / CONFLICT / UNRESOLVED:
old data_sha256:
new data_sha256:
reason for byte/semantic change:
```

## Verification

- [ ] `python -m pytest tests/ -q`
- [ ] `python -m scripts.build_v01_export`
- [ ] `git diff --exit-code -- data/derived/v0.1/` (or intentional diff explained above)
- [ ] CI green
- [ ] New canonical merges have an exact `merge_basis`
- [ ] New assertions/edges carry complete provenance

## Third-party / licensing impact

- [ ] No new dependency/source/license impact
- [ ] `THIRD_PARTY_NOTICES.md` updated where required

## Notes for reviewers

Call out unresolved assumptions, snapshot skew, source disagreements or follow-up work explicitly.