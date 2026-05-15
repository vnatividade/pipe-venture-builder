# Agent Readiness Validator

Use this short validator before starting branch work on a Linear ticket.

The output must be either `READY` or `NOT READY`. If the answer is `NOT READY`, record the reason in Linear and stop until the blocker is resolved or explicitly accepted.

## Readiness Result

- Ticket:
- Validator:
- Date:
- Result: READY / NOT READY
- Reason:

## Binary Checklist

| Check | READY When | Result |
|---|---|---|
| Scope | Included and excluded scope are explicit. | READY / NOT READY |
| Dependencies | Dependencies are done, not required, or explicitly accepted. | READY / NOT READY |
| Approval | Required approvals are present for the next action. | READY / NOT READY |
| Acceptance Criteria | Completion can be judged without guessing. | READY / NOT READY |
| Risk Level | Risk level is stated and no unresolved P0/P1 risk blocks execution. | READY / NOT READY |
| Files / Artifacts | Likely repository files or source artifacts are identifiable. | READY / NOT READY |
| Validation Checks | Expected validation command or manual check is known, or absence is recordable. | READY / NOT READY |

## READY Conditions

Mark `READY` only when:

- the ticket has a clear objective and deliverable
- included scope is narrow enough for one branch and PR
- excluded scope prevents adjacent work from leaking in
- dependencies and approval state are clear
- acceptance criteria are testable or reviewable
- risk level is understood
- relevant files or artifacts can be found
- validation expectations can be recorded in the PR and Linear handoff

## NOT READY Conditions

Mark `NOT READY` when:

- scope is ambiguous or too broad
- required dependencies are missing
- approval is required and absent
- acceptance criteria are not reviewable
- risk level is missing or understated
- likely files or source artifacts cannot be identified
- validation expectations are unknown
- the work would require secrets, customer data, production data, billing, paid ads, external communication, or sensitive claims without approval
- the ticket appears to be future/evolution work when the current cycle forbids it

## Minimal Remediation Note

When marking `NOT READY`, use this note:

```md
Readiness: NOT READY

Blocking reason:

Required fix or decision:

Owner:

Can proceed after:
```

## Human Override

A human may explicitly accept a readiness gap. Record the approval source and the exact gap accepted before starting work.

Do not treat silence, inferred intent, or old conversation context as approval.

## Relationship To Execution Handoff

This validator happens before execution. It does not replace PR review, final Linear handoff, or the done criteria in `execution/ticket-pr-handoff-system.md`.
