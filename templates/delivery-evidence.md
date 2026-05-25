# Delivery Evidence

Use this template when a ticket needs a standalone human-readable evidence package that mirrors `schemas/DeliveryEvidence.schema.json`.

This template supports PR and Linear handoff. It does not replace PR review, approval gates, or the final Linear delivery update.

## Ticket

- Linear ID:
- Linear URL:
- Branch:
- Pull request URL:
- Merge commit:
- Delivery type:

## Implementation Summary

### Summary

What changed.

### Files Changed

- File:

### Included Scope Delivered

- Item:

### Excluded Scope Preserved

- Item:

## Expected Behavior

### Description

What should now be true.

### User Or Agent Visible Change

What a user, reviewer, or future agent should observe.

### Non-Goals

- Item:

## Acceptance Criteria

| Criterion | Status | Evidence |
|---|---|---|
| Criterion | passed / failed / not_applicable / not_checked | Evidence |

## Tests

For documentation-only work, tests may be `not_applicable` when the reason is explicit.

- Required for delivery: true/false
- Not applicable reason:

| Command or check | Result | Evidence |
|---|---|---|
| Command/check | passed / failed / not_run / not_applicable | Evidence |

## E2E

For documentation-only work, Playwright/browser E2E should not be required unless the ticket changes a user-facing flow.

- Required for delivery: true/false
- Not applicable reason:

| Command or check | Result | Evidence |
|---|---|---|
| Command/check | passed / failed / not_run / not_applicable | Evidence |

## Artifacts

Do not include secrets, customer data, production data, or private operational data.

| Type | Path or URL | Description |
|---|---|---|
| file / pull_request / linear_comment / screenshot / report / other | Path or URL | Description |

## Risks

| Risk | Severity | Mitigation or reason accepted | Follow-up |
|---|---|---|---|
| Risk | P0 / P1 / P2 / P3 / none | Mitigation | Link or none |

## Manual Validation

| Item | Status | Evidence |
|---|---|---|
| Item | passed / failed / not_applicable / not_checked | Evidence |

## Recommendation

- Status: ready_for_review / ready_to_merge / blocked / needs_changes / do_not_merge
- Rationale:
- Next action:

## Delivery-Type Evidence Expectations

| Delivery type | Minimum evidence expectation | E2E expectation |
|---|---|---|
| documentation / architecture / governance / workflow | `git diff --check`, link/path sanity, scope check against Linear ticket, review result | Not required unless user-facing flow changes |
| research / validation / product | Source quality, evidence-vs-assumption separation, validation or KPI rationale, scope check | Not required unless user-facing flow changes |
| prompt / skill | Trigger/scope check, stop conditions, consumer alignment, risk review when autonomy expands | Not required unless user-facing flow changes |
| code | Relevant tests, lint/typecheck/build when available, manual behavior check, rollback or mitigation | Required for user-facing flows when feasible |
| infrastructure / automation / observability | Config/runtime validation plan, rollback or mitigation, operational risk check, observability signal | Required when user-facing or runtime behavior changes |
| orchestration-prep | Explicit no-runtime boundary, readiness criteria, future-evaluation scope check | Not required |

## Documentation-Only Sample

- Linear ID: PIP-148
- Delivery type: architecture
- Tests required for delivery: no
- Tests not applicable reason: documentation-only architecture policy; validation is `git diff --check`, targeted search, review, and scope comparison.
- E2E required for delivery: no
- E2E not applicable reason: no user-facing flow or runtime behavior changed.
- Recommendation: ready_to_merge after review findings are resolved.

## Hypothetical Code Sample

- Linear ID: PIP-XXX
- Delivery type: code
- Tests required for delivery: yes
- Example tests: `npm test`, `npm run lint`, or nearest available project-specific checks.
- E2E required for delivery: yes when the change affects a user-facing browser flow; otherwise explain why not applicable.
- Recommendation: ready_to_merge only after tests, relevant manual checks, review, and P0/P1 resolution.
