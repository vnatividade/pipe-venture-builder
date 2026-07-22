# ExternalSnapshot Contract

`schemas/ExternalSnapshot.schema.json` is the canonical, versioned output shared by the Linear and GitHub inventory adapters.

## Contract Intent

The snapshot provides just enough execution metadata for PIP-711 to compare repository, Linear, and GitHub state without treating raw connector output as canonical evidence.

Each snapshot contains:

- stable snapshot, source-container, source-record, and source-key identifiers
- capture time and source-created/updated/closed timestamps
- bounded pagination evidence
- normalized operational fields such as state, priority, labels, branch/commit references, review decision, and aggregate check state
- relationships such as `belongs_to`, `child_of`, `blocks`, and `blocked_by`
- explicit access/failure diagnostics
- machine-readable assertions that the surface is read-only and stores neither credentials nor raw payloads

## Data Minimization

Allowed metadata is deliberately narrower than either provider's full API response.

Excluded from the schema:

- tokens, credentials, cookies, authorization headers, and request headers
- issue/PR bodies, comments, review bodies, and raw connector errors
- people, authors, assignees, emails, or customer records
- production data or private source material
- arbitrary provider fields through `additionalProperties`

The adapters scan the source envelope before normalization and scan the normalized records again before returning them. A secret-shaped value or forbidden key produces `blocked` with a fixed diagnostic and zero records.

## Identity And Idempotency

`sourceId` preserves the provider's stable entity identifier. `sourceKey` keeps the operator-facing key such as `PIP-710`, PR number, repository name, or release tag. `recordId` is derived from source system, entity type, and `sourceId`.

`snapshotId` is derived from source system, container, status, and normalized records. The `capturedAt`/`observedAt` timestamp remains part of a capture's normalized record set, so a new observation can be distinguished from an older one even when external state is unchanged.

PIP-711 owns reconciliation idempotency keys and difference planning. An `ExternalSnapshot` never grants permission to apply a difference.

## Bounded Reads

- `limit` is between 1 and 1000 child records.
- `max_pages` is between 1 and 100 source pages.
- Linear honors source cursors until either boundary is reached.
- GitHub uses bounded `gh ... list --limit` reads and conservatively reports `partial` when a collection reaches the configured limit.
- Cursors and response headers are not persisted.

The container itself is represented as a record for relationship mapping but is not counted in `pagination.returnedCount`.

## Compatibility

The initial schema version is `0.1.0`. Consumers must validate the exact version before reconciliation. Breaking field or enum changes require the schema migration process in [`docs/install/migrations.md`](../install/migrations.md).
