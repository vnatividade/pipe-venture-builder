# `pipe adopt`

`pipe adopt` reconstructs a schema-valid, review-required `ProductBaseline` from one existing local repository. It is the repository-only brownfield entry point defined by PIP-707 and ADR-001.

The command inventories local metadata only. It does not call Linear or GitHub, use credentials, inspect customer or production data, mutate the source repository, or apply reconciliation actions.

## Generate A Baseline

Return the generated baseline in the stable JSON response envelope:

```bash
pipe adopt /path/to/existing-product --root /path/to/pipe-toolkit --json
```

Write the canonical baseline object to an explicit new file:

```bash
pipe adopt /path/to/existing-product \
  --root /path/to/pipe-toolkit \
  --output /path/to/product-baseline.json
```

`--root` resolves the Pipe toolkit that owns `schemas/ProductBaseline.schema.json`. Until PIP-709 implements the portable manifest/bootstrap contract, run the command from a Pipe clone or provide that root explicitly.

One of `--json` or `--output` is required. Output files are created with non-overwriting semantics; an existing file produces `ADOPT_OUTPUT_EXISTS` and is left unchanged.

## Inspected Sources

The first implementation is intentionally allowlist-first and bounded:

- root README metadata (`README.md`, `.rst`, or `.txt`)
- root package metadata (`pyproject.toml`, `package.json`, `Cargo.toml`, or `go.mod`)
- test-path names and counts, without reading test contents
- local Git worktree presence, HEAD, commit count, and HEAD timestamp

Git inspection uses read-only, argument-based commands. It does not read remotes, diffs, blobs, commit messages, credentials, or hooks. The requested repository must be the Git top-level; an incidental parent repository is not attributed to it.

Inventory traversal is capped by depth, entry count, metadata file size, and test-file count. Cache, dependency, build, VCS, and vendor directories are pruned.

## Sensitive-Data Boundary

Likely secret-bearing paths such as `.env`, private keys, credentials, tokens, and passwords are outside the allowlist and are never emitted. Allowlisted metadata is rejected as a whole if it is binary, oversized, invalid UTF-8, symlinked, or contains a recognized secret-shaped value.

Rejected paths and values are not included in the baseline or error messages. The baseline reports only a generic safety omission and blocks any claim that the inventory is complete. Inspecting an excluded sensitive source requires a separate, explicit human approval.

This is defensive filtering, not a general secret scanner or security certification.

## Determinism And Stable IDs

For an unchanged Git repository, `generatedAt` is the normalized HEAD commit timestamp. For a repository without an exact local Git root or commit history, the deterministic sentinel `1970-01-01T00:00:00Z` is used rather than the wall clock.

Product, source, statement, artifact, gap, and next-action IDs derive from stable product names and normalized relative source classes. Lists are sorted before output. Two unchanged runs therefore produce semantically identical output.

## Evidence And Governance Behavior

The generated baseline always keeps implementation maturity separate from market evidence:

- package, test, and Git metadata may support `ticket_execution` implementation maturity
- `customerEvidencePresent` remains `false`
- `demandValidationStatus` remains `unproven`
- `strongestEvidenceLane` remains `none`
- a demand-evidence gap routes the product toward `/pipe:validate`

The baseline status is `review_required`. It does not certify historical governance, customer demand, willingness to pay, product-market fit, or launch readiness.

Linear/GitHub reads, relationship reconciliation, mutation planning, portable toolkit resolution, and persistent execution state remain assigned to PIP-710, PIP-711, PIP-709, and later tickets.

## Validation

From the repository's Python 3.11 environment:

```bash
python -m unittest discover -v
python -m compileall -q src tests
python -m pip check
```

The adoption suite covers canonical schema validation, golden output, stable reruns and IDs, fake-secret redaction, sensitive filenames, paths with spaces, explicit non-overwriting output, and local Git history.
