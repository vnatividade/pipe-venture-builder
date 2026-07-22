# Supervised Apply And Durable Audit Checkpoints

PIP-712 adds a machine-local control plane for reviewed reconciliation actions. It persists the plan fingerprint, one-action approvals, state-machine checkpoints, normalized results, and an append-only event chain before and after a local fixture mutation.

This ticket does not implement live Linear, GitHub, or repository mutation. `FixtureApplyAdapter` is the only provided adapter implementation. The generic protocol exists so a separately approved pilot can add a real adapter later without weakening the service gate.

## Storage Decision

The local store uses SQLite from the Python standard library because it is portable, transactional, inspectable, and requires no daemon or credential. The database is machine-local recoverable state, not the source of truth for product strategy, execution priority, or delivery history.

Product usage must place it in machine-local state outside the product clone, such as:

```text
<machine-local-state>/pipe/<product-id>/control-plane.sqlite3
```

Do not commit this database or make it the only durable source of a decision; `sourceRef` must point to the canonical approval evidence, such as the assigned Linear ticket. The store creates its parent directory, rejects a database or immediate parent that is a symlink, enables foreign keys, uses WAL for file-backed databases, sets a busy timeout, and sets the database file to mode `0600`. No token, secret, raw connector response, customer data, or production data belongs in it.

## Durable Records

### ApprovalRecord

An approval is bound to:

- exact plan ID and action ID;
- action version and idempotency key;
- target system, container, action type, source artifacts, and target records;
- ProductBaseline fingerprint and expected target fingerprint;
- a declared human actor, decision time, expiry, and source reference.

The record fingerprint detects accidental or direct modification. Every absolute-gate field is fixed to `false`; an approval generated here cannot authorize production, secrets, customer data, or destructive behavior. `denied` and `revoked` records are auditable but never executable.

### RunEvent

Events contain only normalized IDs, fixed status/reason codes, checkpoint state, attempt count, and SHA-256 fingerprints. Each event includes the prior event hash and its own hash. `audit` recomputes the entire event chain and every checkpoint fingerprint, then fails when either was changed.

The chain is tamper-evident, not a digital signature or remote trust service. SQLite remains local recoverable state.

### Checkpoint

Each `(run, action)` checkpoint persists:

- current state and attempt;
- exact idempotency key and approval ID;
- source and expected-target fingerprints;
- normalized result reference and result fingerprint after apply.

Each checkpoint also has a fingerprint over all stored fields. Checkpoint and corresponding action event transitions are written in one SQLite transaction. Execution refuses to call an adapter when either the checkpoint fingerprint or the run event chain is invalid.

## Apply State Machine

```text
plan registered
  → approval validated
  → source fingerprint rechecked
  → target inspected and compared
  → precondition_passed
  → applying
  → applied
  → verifying
  → verified
```

Controlled alternatives:

- missing, mismatched, denied, future, or expired approval → `blocked` before adapter access;
- non-mutating, low-confidence, blocked, or terminal action → `blocked` before adapter access;
- changed source or target → `blocked` without apply;
- adapter conflict → `blocked`;
- adapter failure → `failed` with fixed diagnostics;
- verification failure → result remains checkpointed and a later run retries verification only;
- pause after a persisted result → `interrupted`, then resume at verification without apply;
- interruption with uncertain result → retry the same idempotency key, then verify;
- already verified → `skipped` and no duplicate adapter call.

For `create`, the precondition requires no existing target and no target fingerprint. For `update` and `link`, a target fingerprint is mandatory and must still match.

## Fixture-Only CLI

PIP-712 stays inside its ticket write set by exposing a module CLI:

```bash
python -m pipe_venture_builder.apply approve \
  --store /absolute/machine-local/pipe/example/control-plane.sqlite3 \
  --plan reconciliation-plan.json \
  --action RA-000000000000 \
  --actor founder \
  --source-ref linear:PIP-712 \
  --at 2026-07-21T13:00:00Z \
  --expires-at 2026-07-21T15:00:00Z \
  --output approval.json
```

This command records a decision supplied by the human operator. It does not infer or auto-grant approval. Existing approval files are never overwritten.

Execute one fixture action:

```bash
python -m pipe_venture_builder.apply execute \
  --store /absolute/machine-local/pipe/example/control-plane.sqlite3 \
  --plan reconciliation-plan.json \
  --approval approval.json \
  --fixture fixture-apply.json \
  --action RA-000000000000 \
  --source-fingerprint sha256:0000000000000000000000000000000000000000000000000000000000000000
```

Verify the local event chain:

```bash
python -m pipe_venture_builder.apply audit \
  --store /absolute/machine-local/pipe/example/control-plane.sqlite3 \
  --run-id RUN-000000000000
```

Exit codes are `0` for verified/skipped/successful audit, `8` for a controlled refusal, `9` for a failed contract/state/audit operation, and `10` for an intentional or recoverable interruption.

## Fixture Contract

The fixture file is deliberately narrow:

```json
{
  "schemaVersion": "0.1.0",
  "adapter": "fixture",
  "actions": [
    {
      "actionId": "RA-000000000000",
      "beforeExists": false,
      "beforeFingerprint": null,
      "afterFingerprint": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "resultRef": "fixture:RA-000000000000",
      "applyBehavior": "success",
      "verifyBehavior": "success"
    }
  ]
}
```

Allowed apply behaviors are `success`, `interrupt_once`, `fail`, and `conflict`. Allowed verification behaviors are `success`, `fail_once`, and `fail`. The adapter keeps state in memory and offers an explicit local `rollback(actionId)` test helper; the service never performs an automatic rollback or touches an external system.

## Future Live Adapter Gate

A real adapter must be a separate ticket and pilot. It must provide provider-native idempotency or an equivalent durable guarantee, re-read normalized state, use existing user-controlled authentication without persisting it, enforce repository operating mode and absolute gates, and receive explicit approval for any required credential use or live mutation. Installing this control plane alone grants none of those permissions.
