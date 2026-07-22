# Hermes Runtime Adapter

PIP-713 adds a bounded integration between Hermes Agent 0.17+ and Pipe's local control plane. Hermes remains an operator-facing runtime; it does not become a source of product truth, execution priority, approval policy, or code-review state.

The integration direction is deliberately `Hermes → Pipe`. An active Hermes session loads the portable skill and calls the Python module adapter with its `HERMES_SESSION_ID`. Pipe does not launch Hermes in one-shot, YOLO, gateway, cron, or unattended mode. This avoids implicit credential loading and the approval-bypass behavior documented by the local Hermes CLI for one-shot execution.

## Components

| Component | Responsibility |
|---|---|
| `integrations/hermes/skill/SKILL.md` | Operator/runtime procedure loaded by Hermes. |
| `integrations/hermes/install.sh` | Plan-first, no-overwrite copy into an explicitly selected Hermes home. It is not run automatically. |
| `pipe_venture_builder.adapters.hermes` | Validates context, binds sessions, maps events, verifies approvals, and exposes the module CLI. |
| `HermesCheckpointStore` | Writes one atomic, fingerprinted, mode-0600 JSON checkpoint per Pipe run in a mode-0700 machine-local directory. |
| `LocalControlPlaneStore` | Keeps the canonical local run/event audit chain and canonical Pipe ApprovalRecords. |

No component reads `~/.hermes/config.yaml`, `.env`, session history, provider credentials, gateway state, Slack, WhatsApp, or customer/production data.

## Authority Boundary

```text
repository artifacts ── canonical product/architecture/decision state
Linear               ── canonical execution state, blockers and handoff
GitHub               ── canonical code and review history
Pipe control plane   ── recoverable run/checkpoint/approval audit
Hermes               ── session runtime and operator interaction only
```

An `approval.requested` Hermes event interrupts the Pipe run. An `approval.granted` event is rejected unless the caller supplies an exact, valid, action-scoped Pipe `ApprovalRecord`. Recording that approval does not execute a mutation.

## Event Mapping

The current `RunEvent` schema predates the Hermes adapter. Runtime event identity is therefore stored in the event's nullable safe `idempotencyKey` reference as an `HE-*` identifier. This makes recovery and deduplication durable without changing the canonical schema inside this ticket.

| Hermes event | Pipe event | Run/checkpoint result |
|---|---|---|
| `run.started`, `run.resumed` | `run.resumed` | running |
| `run.completed` | `run.completed` | completed |
| `run.failed` | `run.failed` | failed / `adapter_failed` |
| `tool.started`, `tool.succeeded` | `run.resumed` | running; no raw tool payload |
| `tool.failed` | `run.interrupted` | interrupted / `adapter_failed` |
| `approval.requested` | `run.interrupted` | waiting / `approval_missing` |
| valid `approval.granted` | `approval.recorded`, then `run.resumed` | approval granted |
| `approval.denied` | `run.interrupted` | denied / `approval_not_granted` |
| `runtime.unavailable`, `runtime.timeout` | `run.interrupted` | runtime blocker / `adapter_failed` |

Events are ordered by RFC 3339 timestamp, idempotent by stable Hermes event ID, and fail closed when the Pipe event chain or Hermes checkpoint fingerprint is invalid.

## Supported Flow

The PIP-712 control plane registers a `ReconciliationPlan`, so the Hermes binding begins after either entry path has produced and reviewed its ProductBaseline, external inventory, and reconciliation plan:

```text
pipe idea/adopt → reviewed ProductBaseline → snapshots → ReconciliationPlan
  → Hermes begin → runtime/tool events → Pipe approval handoff → resume/complete
```

Early brainstorm and brownfield inventory commands can be run interactively from Hermes, but their durable runtime binding starts only when the reconciliation plan exists. The adapter does not manufacture a placeholder plan or treat conversation memory as canonical state.

## Install And Operate

See [operator-runbook.md](operator-runbook.md). Installation into a live Hermes home is not performed by repository setup or tests. The local smoke check calls only `hermes --version` with a minimal environment and no shell.

## Deliberate Exclusions

- no programmatic Hermes inference call;
- no provider, token, config, memory, session-history, Slack, or WhatsApp access;
- no gateway, cron, hook, MCP, ACP, profile, or plugin mutation;
- no unauthenticated route or network listener;
- no live Linear/GitHub/repository apply adapter;
- no automatic approval, PR action, deployment, communication, or production action.
