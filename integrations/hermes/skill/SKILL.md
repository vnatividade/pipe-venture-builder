---
name: pipe-product-delivery
description: Use when the founder asks Hermes to start, resume, inspect, or hand off a governed Pipe product-delivery run from an idea or adopted product. Binds the active Hermes session to Pipe's local control plane without making Hermes a policy authority.
version: 0.1.0
author: Pipe Venture Builder
license: Proprietary
platforms: [linux, macos]
metadata:
  hermes:
    tags: [pipe, product-delivery, governance, approvals, checkpoints]
    related_skills: []
---

# Pipe Product Delivery Runtime

## Overview

This skill makes the active Hermes session a supervised Pipe runtime. Repository artifacts remain canonical product truth, Linear remains canonical execution state, GitHub remains canonical code-review history, and Pipe's local control plane owns approvals and checkpoints.

Hermes supplies interaction and session continuity. A Hermes approval prompt is never authority to execute a Pipe action.

## When to Use

Use this skill when the founder asks to:

- start or continue an `idea` or `adopt` delivery flow after a reviewed reconciliation plan exists;
- resume a Pipe run after a runtime interruption;
- report a normalized tool or runtime event;
- hand an approval request to the Pipe control plane;
- inspect the current redacted Pipe/Hermes checkpoint.

Do not use it to deploy, handle credentials or customer/production data, send messages, schedule work, enable billing, or bypass repository/Linear rules.

## Hard Boundaries

- Never use Hermes `--oneshot`/`-z`, `--yolo`, or `--accept-hooks` for a Pipe run. Those flags can bypass or broaden runtime approval behavior.
- Never infer approval. Only a valid `ApprovalRecord` produced by the Pipe control plane can satisfy `approval.granted`.
- Never place prompt text, tool output, source contents, credentials, customer data, or production data in an adapter event. Record a stable reference and SHA-256 fingerprint only.
- Never start when the assigned Linear ticket, ProductBaseline, reconciliation plan, or canonical artifact references are missing.
- Never execute an external mutation from this skill. A separately governed adapter and approval are required.

## Required Local Inputs

The operator supplies these machine-local values:

```text
PIPE_CONTROL_STORE      absolute path to control-plane.sqlite3
PIPE_HERMES_STATE       absolute directory for Hermes handoff checkpoints
PIPE_PRODUCT_ROOT       absolute product repository root
PIPE_PRODUCT_ID         ProductManifest productId
PIPE_LINEAR_TICKET      assigned PIP-* ticket
PIPE_RECONCILIATION_PLAN absolute reviewed ReconciliationPlan JSON
```

The active Hermes runtime supplies `${HERMES_SESSION_ID}`. If it is absent, stop; do not invent a session identifier.

## Start Flow

1. Run the credential-free compatibility check:

   ```bash
   python -m pipe_venture_builder.adapters.hermes probe
   ```

   Continue only when `compatible` is `true`.

2. Run `pipe doctor "$PIPE_PRODUCT_ROOT" --json`. Continue only when required checks are not blocked. An external connector may remain `unauthorized`; do not authenticate it from this skill.

3. Confirm every `--artifact` is a reviewed repository-relative file. Do not pass directories, symlinks, `..`, private sources, or generated raw output.

4. Bind the active session. Use a stable external event ID so a retry is idempotent:

   ```bash
   python -m pipe_venture_builder.adapters.hermes begin \
     --store "$PIPE_CONTROL_STORE" \
     --checkpoint-dir "$PIPE_HERMES_STATE" \
     --plan "$PIPE_RECONCILIATION_PLAN" \
     --product-root "$PIPE_PRODUCT_ROOT" \
     --product-id "$PIPE_PRODUCT_ID" \
     --ticket-id "$PIPE_LINEAR_TICKET" \
     --workflow adopt \
     --artifact README.md \
     --session-id "${HERMES_SESSION_ID}" \
     --event-id "begin-${HERMES_SESSION_ID}"
   ```

   The step is complete only when the JSON result has `state: running`, the expected `runId`, and only canonical artifact references.

## Runtime Event Flow

For a tool lifecycle, emit only the normalized tool name and optional result reference/fingerprint:

```bash
python -m pipe_venture_builder.adapters.hermes event \
  --store "$PIPE_CONTROL_STORE" \
  --checkpoint-dir "$PIPE_HERMES_STATE" \
  --run-id "$PIPE_RUN_ID" \
  --kind tool.succeeded \
  --tool-name read_file \
  --result-ref artifact:product-baseline \
  --session-id "${HERMES_SESSION_ID}" \
  --event-id tool-product-baseline-read-1
```

Use `tool.failed`, `runtime.unavailable`, or `runtime.timeout` for failures. The adapter persists an actionable blocker before the flow is resumed.

## Approval Handoff

1. Record the request and stop the affected action:

   ```bash
   python -m pipe_venture_builder.adapters.hermes event \
     --store "$PIPE_CONTROL_STORE" \
     --checkpoint-dir "$PIPE_HERMES_STATE" \
     --run-id "$PIPE_RUN_ID" \
     --kind approval.requested \
     --action-id "$PIPE_ACTION_ID" \
     --session-id "${HERMES_SESSION_ID}" \
     --event-id "approval-request-$PIPE_ACTION_ID"
   ```

2. Ask the operator for the path to an existing, canonical `ApprovalRecord`. Do not generate or approve it inside Hermes.

3. Attach it only through the exact action-scoped handoff:

   ```bash
   python -m pipe_venture_builder.adapters.hermes event \
     --store "$PIPE_CONTROL_STORE" \
     --checkpoint-dir "$PIPE_HERMES_STATE" \
     --run-id "$PIPE_RUN_ID" \
     --kind approval.granted \
     --action-id "$PIPE_ACTION_ID" \
     --approval-id "$PIPE_APPROVAL_ID" \
     --approval "$PIPE_APPROVAL_FILE" \
     --plan "$PIPE_RECONCILIATION_PLAN" \
     --session-id "${HERMES_SESSION_ID}" \
     --event-id "approval-granted-$PIPE_ACTION_ID"
   ```

The handoff is complete only when the checkpoint says `approval_granted`. This records authority; it does not execute a live mutation.

## Resume Flow

After an interrupted runtime or a new Hermes session in the same lineage:

```bash
python -m pipe_venture_builder.adapters.hermes resume \
  --store "$PIPE_CONTROL_STORE" \
  --checkpoint-dir "$PIPE_HERMES_STATE" \
  --run-id "$PIPE_RUN_ID" \
  --session-id "${HERMES_SESSION_ID}" \
  --event-id "resume-${HERMES_SESSION_ID}"
```

Resume is complete only when `state` is `running`, `attempt` increased, and the audit chain remains valid. Completed, failed, denied, tampered, or out-of-order runs remain blocked.

## Status And Completion

Inspect without reading raw Hermes history:

```bash
python -m pipe_venture_builder.adapters.hermes status \
  --store "$PIPE_CONTROL_STORE" \
  --checkpoint-dir "$PIPE_HERMES_STATE" \
  --run-id "$PIPE_RUN_ID"
```

Record `run.completed` only after the assigned workflow's repository artifacts exist and its validation checks pass. Completion of the Hermes session does not close a Linear implementation ticket or merge a PR.

## Common Pitfalls

1. Treating `/approve` in Hermes as Pipe approval. Record `approval.requested`, obtain the Pipe `ApprovalRecord`, then attach it.
2. Passing raw tool output in an event. Store it only in an approved canonical artifact and pass its reference/fingerprint.
3. Starting before reconciliation. Finish `pipe idea` or `pipe adopt`, review the ProductBaseline, inventory external state, and produce the reviewed ReconciliationPlan first.
4. Resuming with an old session ID. Use the current `${HERMES_SESSION_ID}`; the adapter records forward-only lineage.
5. Installing the skill into a live Hermes home automatically. Installation is an explicit operator action and existing files are never overwritten.

## Verification Checklist

- [ ] Hermes 0.17+ probe is compatible.
- [ ] Product root, ticket, plan, and artifact references are exact.
- [ ] Start/resume result contains the expected run and session IDs.
- [ ] Runtime events contain references/fingerprints only.
- [ ] Approval requests stop before action execution.
- [ ] `approval.granted` includes a valid Pipe `ApprovalRecord`.
- [ ] `status` reports `auditChainValid: true`.
- [ ] No external mutation, credential access, communication, scheduling, or production action occurred.
