# Hermes Operator Runbook

## 1. Validate The Runtime

From the versioned Pipe toolkit environment:

```bash
python -m pipe_venture_builder.adapters.hermes probe
```

The probe invokes only `hermes --version`, without a shell and with a minimal environment. Expected result for the validated local installation:

```json
{"available":true,"command":"hermes","compatible":true,"reason":null,"version":"0.17.0"}
```

This is a binary compatibility check, not a provider, credential, gateway, or security certification.

Run the fixture-only start/block/resume smoke path:

```bash
python integrations/hermes/smoke.py
```

It calls `hermes --version`, then uses temporary local state and the in-process fixture boundary. It does not start inference, read Hermes configuration/history, contact a gateway, or mutate an external system. Expected fields include `startedState: running`, `blockedState: runtime_blocked`, `resumedState: running`, `attempt: 2`, and `auditChainValid: true`.

## 2. Review The Skill Installation Plan

Choose the Hermes home explicitly. The default command is plan-only:

```bash
sh integrations/hermes/install.sh \
  --hermes-home /absolute/path/to/hermes-home \
  --plan
```

Apply only after reviewing the destination:

```bash
sh integrations/hermes/install.sh \
  --hermes-home /absolute/path/to/hermes-home \
  --apply
```

The installer copies one `SKILL.md`, never overwrites an existing destination, and never changes Hermes config, tools, hooks, providers, credentials, gateway, or services. Open a new Hermes session before loading the installed skill.

## 3. Prepare Machine-Local State

Use locations outside the product clone:

```text
<machine-local>/pipe/<product-id>/control-plane.sqlite3
<machine-local>/pipe/<product-id>/hermes-checkpoints/
```

The database and checkpoint directory are recoverable operational state. Canonical product artifacts stay in the repository; execution and handoff stay in Linear/GitHub. Do not commit machine-local state.

## 4. Start Hermes Interactively

Start an interactive session with the Pipe skill and session identity enabled:

```bash
hermes --pass-session-id --skills pipe-product-delivery
```

Do not add `--oneshot`, `-z`, `--yolo`, or `--accept-hooks`. The adapter does not require those modes. In the session, provide the non-secret local paths and ask Hermes to follow the skill's Start Flow.

## 5. Validate Start And Resume

The begin result must show:

- the expected `PIP-*` ticket and `RP-*` plan;
- `state: running`;
- the current Hermes session ID;
- repository-relative artifact references only;
- all credential/customer/production/mutation constraints set to `false`.

After an intentional `runtime.unavailable` fixture event, resume from the same or a new Hermes session. `attempt` must increase, session lineage must move forward, and `status` must return `auditChainValid: true`.

## 6. Handle Approvals

A Hermes prompt or `/approve` response is not sufficient. Record `approval.requested`, obtain the reviewed action-scoped `ApprovalRecord` through Pipe, then attach it together with the exact registered reconciliation plan using the skill's Approval Handoff command. A denied, revoked, expired, future, mismatched, missing, wrong-action, changed-plan, or tampered approval remains blocked.

## 7. Troubleshooting

| Result | Meaning | Action |
|---|---|---|
| `runtime_unavailable` | `hermes` is not on PATH. | Install/select Hermes locally, then rerun probe. |
| `runtime_version_unsupported` | Runtime is older than 0.17.0. | Upgrade through the user's normal Hermes process; this adapter does not update it. |
| `HERMES_SESSION_ID_REQUIRED` | Session identity was not supplied. | Start Hermes with `--pass-session-id`; do not invent an ID. |
| `HERMES_HANDOFF_REJECTED` | Contract, order, approval, audit, or checkpoint mismatch. | Run `status`, inspect canonical artifacts, and repair the source mismatch rather than deleting state. |
| `runtime_blocked` | Hermes was unavailable or timed out. | Restore the runtime, then use `resume` with a stable event ID. |

Never repair by deleting the control-plane database, rewriting Git history, editing a fingerprint, or bypassing approval.
