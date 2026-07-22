# ADR-002: Use a Python 3.11 CLI as the portable Pipe execution foundation

## Record

- ADR ID: ADR-002
- Title: Use a Python 3.11 CLI as the portable Pipe execution foundation
- Date: 2026-07-21
- Status: Proposed
- Owner: Architecture Agent
- Linear ticket: PIP-706
- PR: Pending validation and approval
- Related architecture review: ADR-001 and PIP-706 delivery review
- Supersedes: None
- Superseded by: None

## Context

- Product or MVP context: ADR-001 defines `idea` and `adopt` entry modes that converge on `ProductBaseline`, but the repository had no executable command foundation.
- Decision trigger: PIP-706 requires an installable `pipe` command, project-root discovery, stable errors/exit codes, version reporting, and Draft 2020-12 ProductBaseline validation.
- Constraints:
  - work across developer machines without founder-specific paths
  - keep repository schemas canonical
  - avoid coupling the CLI to Hermes, Codex, Claude Code, Linear, or GitHub
  - preserve read-only behavior in this first runtime slice
  - emit useful errors without echoing potentially sensitive instance values
  - leave `idea`, `adopt`, manifests, connectors, reconciliation, and persistence to their approved tickets
- Evidence or source artifacts:
  - `architecture/adr/adr-001-dual-entry-product-intake.md`
  - `schemas/ProductBaseline.schema.json`
  - `setup/portable-bootstrap-and-runtime-boundaries.md`
  - `execution/dual-entry-product-intake-workflow.md`
  - `execution/test-oriented-delivery-rule.md`
- Human review required: yes
- Approval record or blocker: implementation is authorized by PIP-706; PR opening and merge remain restricted-mode approval gates.

## Options Considered

| Option | Pros | Cons | Why accepted/rejected |
|---|---|---|---|
| Python 3.11 package with a `pipe` console script | Portable, mature CLI and JSON Schema ecosystem, readable by all supported executors, straightforward isolated installation. | Requires Python 3.11+ and a small runtime dependency set. | Accepted as the smallest portable foundation. |
| Node.js/TypeScript CLI | Strong packaging and future UI ecosystem. | Adds compilation/build-tool choices before any UI or Node-specific requirement exists. | Rejected for the foundation; can be reconsidered if a future product surface requires it. |
| Shell scripts only | Minimal bootstrap on Unix-like systems. | Weak Windows portability, structured error handling, tests, and schema validation. | Rejected. |
| Implement commands directly as Hermes plugins | Immediate runtime integration. | Makes Hermes a prerequisite and violates ADR-001's runtime/source-of-truth separation. | Rejected. |

## Decision

- Selected option: package Pipe as a Python 3.11+ project using a `src/` layout and expose `pipe` through the standard console-script entrypoint.
- Runtime dependencies: `jsonschema` Draft 2020-12 validation plus the narrow RFC 3339 validator needed by ProductBaseline date-time fields. Dependencies use compatible upper bounds until a later bootstrap/lock ticket defines distribution locking.
- Root discovery: walk upward from an explicit start or the current directory and require both the canonical ProductBaseline schema and a Pipe marker (`.pipe/` or `AGENTS.md`). No home-directory or founder-specific fallback is allowed.
- Schema authority: load `schemas/ProductBaseline.schema.json` from the discovered product/toolkit root. PIP-709 owns packaged toolkit resolution and `.pipe/project.json`; this ticket does not duplicate the canonical schema inside the Python package.
- Output contract: commands render concise human output by default and stable JSON with `--json`. Validation findings expose schema paths and rules but never raw instance values.
- Initial commands:
  - `pipe --help`
  - `pipe --version` and `pipe version`
  - `pipe root`
  - `pipe baseline validate <file>`
- Stable exit codes:

| Code | Meaning |
|---|---|
| `0` | Success. |
| `2` | Command usage error from the CLI parser. |
| `3` | Pipe root or canonical schema unavailable. |
| `4` | Input file unavailable or unreadable. |
| `5` | Input or schema is not valid JSON. |
| `6` | ProductBaseline does not satisfy the schema. |
| `7` | Canonical ProductBaseline schema is internally invalid. |

- What this enables: later tickets can add `idea`, `adopt`, manifest/bootstrap/doctor, connectors, reconciliation, checkpoints, Hermes, and Atelier adapters behind one tested entrypoint.
- What this intentionally does not solve: distribution outside a cloned Pipe/product repository, credentials, external reads/writes, persistent control-plane state, or orchestration.

## Consequences

- Positive consequence: a clean Python 3.11 environment can install one package and receive deterministic command, root, validation, and error behavior.
- Tradeoff accepted: validation currently needs a discovered Pipe root or an explicit schema within that root; PIP-709 will define toolkit/product manifests and cross-install resolution.
- Risk introduced: dependency or Python-version drift across machines.
- Mitigation: bounded dependency versions, explicit runtime check through package metadata, isolated-environment installation tests, and future `pipe doctor` compatibility checks.
- Risk introduced: invalid ProductBaseline content could contain sensitive values.
- Mitigation: the renderer uses sanitized schema-rule messages and tests that sentinel values never appear in output.
- Follow-up tickets: PIP-707 through PIP-715, in the dependency graph established by PIP-700.

## Acceptance Examples

```txt
Given a clean Python 3.11 environment
When the repository package is installed
Then `pipe --help` and `pipe version` run without user-specific configuration.
```

```txt
Given a ProductBaseline that satisfies the canonical schema
When `pipe baseline validate` runs inside the Pipe repository
Then it exits 0 and reports that the baseline is valid.
```

```txt
Given an invalid baseline containing a sentinel secret-like value
When validation fails
Then the command exits 6 with actionable schema paths
And the sentinel value is absent from stdout and stderr.
```

## Review Trigger

Review this ADR when:

- PIP-709 implements toolkit distribution or `.pipe/project.json`
- a supported machine cannot install Python 3.11+
- a second language runtime becomes necessary for a validated product surface
- schema resolution needs multiple active contract versions
- a P0/P1 safety, validation, packaging, or redaction failure appears

## Links

- Linear: https://linear.app/pipe-venture-builder/issue/PIP-706/runtime-implement-portable-pipe-cli-foundation
- PR: Pending validation and approval
- Architecture review: ADR-001 and PIP-706 delivery review
- KDR/DAR: Not required; this ADR records the durable runtime choice.
