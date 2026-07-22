# Read-Only Connector Inventories

PIP-710 adds bounded Linear and GitHub inventory adapters for adoption and reconciliation planning. Both adapters emit the same canonical [`ExternalSnapshot`](../../schemas/ExternalSnapshot.schema.json) contract and expose no create, update, delete, comment, status-change, branch, PR, or merge operation.

This layer is a read boundary, not an authentication manager and not a synchronization engine.

## Delivered Surfaces

| Surface | Purpose | Mutation boundary |
|---|---|---|
| `LinearInventoryAdapter` | Normalize one Linear project and its bounded issue inventory. | Receives only a source with `read`; the MCP implementation calls fixed project/issue read tools. |
| `GitHubInventoryAdapter` | Normalize repository, issue, PR/review/check summary, and release metadata. | The CLI implementation builds fixed `gh repo view`, `gh issue list`, `gh pr list`, and `gh release list` commands. |
| `FixtureInventorySource` | Run the same normalizers against tracked sanitized pages. | Reads one bounded local JSON fixture and never contacts an external system. |
| `ExternalSnapshot` | Stable handoff to the future reconciliation planner. | Declares `readOnly: true` and `mutationSurfaceExposed: false`. |

The adapters include titles and operational state but intentionally exclude descriptions, issue/PR bodies, comments, authors, assignees, response headers, raw connector envelopes, and credential material.

## Status Semantics

An authorized read with no child records is `empty`. It is never used as a fallback for an access failure.

| Status | Meaning |
|---|---|
| `complete` | The bounded read completed and returned child records. |
| `partial` | Safe records were returned, but the configured record/page bound was reached. |
| `empty` | The source was read successfully and contained no child records. |
| `unavailable` | The source, command, or connection is unavailable. |
| `unauthorized` | The source exists but the authenticated host cannot read it. |
| `rate_limited` | The provider rejected the read because of a rate limit. |
| `failed` | The response shape is incompatible or cannot be normalized. |
| `blocked` | A credential-shaped value, forbidden header/key, oversized payload, or unsafe URL was detected. |

Diagnostics use fixed summaries. Provider stderr and raw error payloads are classified in memory and discarded; they are never copied to the snapshot.

## Authentication Boundary

- The Linear source accepts a host-provided connector invoker. The host owns interactive authentication; the adapter supplies only fixed read tool names and non-secret project/cursor arguments.
- The GitHub source delegates authentication to the installed `gh` CLI. It does not accept tokens or build authorization headers.
- Fixture tests require no authentication and are the default validation path.
- Running either live source uses an existing credential context and therefore remains subject to the repository's absolute credential approval gate.

See [runtime integration](runtime-integration.md) for the host contract and [ExternalSnapshot contract](external-snapshot.md) for field semantics.

## Validation

The tracked connector tests cover:

- schema validation and deterministic record IDs
- fixture pagination and truncation
- successful empty vs unauthorized reads
- unavailable and rate-limited diagnostics
- forbidden mutation-surface checks
- fixed GitHub read command construction
- credential/header/redaction sentinels
- review/check summary normalization

No live authenticated call is required to validate this ticket.
