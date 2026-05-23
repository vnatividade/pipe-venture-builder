# Agent Readiness Validator

Use this short validator before starting branch work on a Linear ticket.

The output must be one of `READY`, `READY WITH APPROVAL`, `NOT READY`, or `BLOCKED`. Record the result and reasons in Linear before starting branch work.

Use this validator with:

- `execution/linear-ticket-template-v2.md`
- `execution/ticket-type-field-matrix.md`
- the assigned Linear ticket

## Readiness Result

- Ticket:
- Validator:
- Date:
- Executor tool: Codex / Claude Code / Human / Future Orchestrator / Unassigned
- Result: READY / READY WITH APPROVAL / NOT READY / BLOCKED
- Reasons:
- Required before branch work:
- Required before PR opening:
- Required before merge:

## Readiness Outputs

| Result | Meaning | Branch Work Rule |
|---|---|---|
| READY | The ticket has enough scope, approvals, dependencies, ownership, write set, validation, and risk context to start. | Branch work may start. |
| READY WITH APPROVAL | The ticket is otherwise ready, but a named human approval is required before the next gated action. | Branch work may start only if the required approval is already explicit for branch work; otherwise stop. |
| NOT READY | The ticket is incomplete, ambiguous, or missing required readiness fields, but the issue is fixable without external dependency resolution. | Do not start branch work. Update the ticket or request clarification. |
| BLOCKED | A dependency, approval, risk, external action, or missing source artifact blocks safe execution. | Do not start branch work. Record the blocker and unblock condition in Linear. |

## Multi-Agent Checklist

| Check | READY When | Result |
|---|---|---|
| Ticket Type | Type is present and belongs to the approved type list in `execution/ticket-type-field-matrix.md`. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Scope | Included and excluded scope are explicit and fit one branch and PR. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Objective And Deliverables | Objective, why/rationale, source rationale, deliverables, and acceptance criteria are observable. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Dependencies | Dependencies are done, not required, or have explicit unblock conditions. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Approval | Required approvals are explicit for the next action, or the ticket is marked ready only after approval. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Definition of Ready | DoR states the minimum conditions to start work and no start blocker remains open. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Definition of Done | DoD states objective completion, validation, review, handoff, and merge expectations. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Validation Plan | Expected validation commands, manual checks, and unavailable checks are clear. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Market Validation Before Code | Product PRD, architecture, implementation, growth, monetization, and customer-facing build tickets link a GO or approved CONDITIONAL GO from `validation/market-validation-before-code-gate.md`; non-product governance, documentation, research, or internal operating tickets explicitly record `Gate decision: NOT APPLICABLE`. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Parallelization | Parallelizable value and notes explain whether work is yes, no, or partial. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Write Set | Expected write set and restricted files are declared and narrow enough. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Risk Level | Risk level is stated and no unresolved P0/P1 risk blocks execution. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Conditional Fields | Type-specific required and conditional fields from the matrix are present or explicitly not applicable. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Monitoring And Metrics | Monitoring requirements and success metrics match the ticket type. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |
| Agent Execution Notes | Executor tool, suggested owner/agent, and agent execution notes are clear enough for Codex or Claude Code. | READY / READY WITH APPROVAL / NOT READY / BLOCKED |

## Type-Specific Field Check

Use `execution/ticket-type-field-matrix.md` to check conditional requirements.

- For `code`, `infrastructure`, `automation`, and `observability`, require technical dependencies, observability requirements, rollback or mitigation, and runtime-oriented validation.
- For `product`, require KPI Impact, monitoring, success metrics, validation, and post-release follow-up when applicable.
- For `architecture`, `governance`, `documentation`, `prompt`, `skill`, and `workflow`, require affected artifact or protocol, agent consumers when applicable, ambiguity or duplication problem, validation, monitoring, and success metrics tied to adherence or traceability.
- For `orchestration-prep`, require a statement that runtime orchestration is not being implemented and that the Codex + Claude Code baseline dependency is satisfied or explicitly deferred.

## READY Conditions

Mark `READY` only when:

- the ticket has a clear objective and deliverable
- ticket type is present and supported
- included scope is narrow enough for one branch and PR
- excluded scope prevents adjacent work from leaking in
- dependencies and approval state are clear
- Definition of Ready and Definition of Done are usable
- acceptance criteria are testable or reviewable
- risk level is understood
- expected write set and restricted files are declared
- parallelization class and notes are usable
- relevant files or artifacts can be found
- validation expectations can be recorded in the PR and Linear handoff
- monitoring and success metrics match the ticket type
- type-specific fields are present or explicitly not applicable

## READY WITH APPROVAL Conditions

Mark `READY WITH APPROVAL` when:

- the ticket is otherwise ready
- a gated action is explicit and approval is needed before starting branch work, opening the PR, merging, or taking another named action
- the required approver, action, and timing are stated
- no dependency, risk, or missing source artifact blocks execution after approval

Do not treat `READY WITH APPROVAL` as permission. If the required approval is absent for the next action, stop and record the approval blocker in Linear.

## NOT READY Conditions

Mark `NOT READY` when:

- scope is ambiguous or too broad
- ticket type is missing or unsupported
- baseline Linear v2 fields are missing
- conditional fields required by the ticket type are missing
- Definition of Ready or Definition of Done is missing or vague
- approval need is unclear
- acceptance criteria are not reviewable
- risk level is missing or understated
- expected write set or restricted files are missing
- parallelizable value or notes are missing for shared or high-risk work
- likely files or source artifacts cannot be identified
- validation expectations are unknown
- monitoring requirements or success metrics are missing
- executor tool, owner, or agent execution notes are unclear

## BLOCKED Conditions

Mark `BLOCKED` when:

- required dependencies are not complete and no explicit unblock condition exists
- approval is required for branch work and absent
- a P0/P1 risk blocks execution
- the work would require secrets, customer data, production data, billing, paid ads, external communication, or sensitive claims without approval
- the ticket appears to be future/evolution work when the current cycle forbids it
- required source artifacts do not exist
- the ticket would require automation, Linear status changes, label creation, project changes, production deployment, or other gated work outside its scope

## Minimal Readiness Comment

Use this note in Linear when readiness is not plain `READY`:

```md
## Readiness result

Result: READY WITH APPROVAL / NOT READY / BLOCKED

## Reasons
- Reason:

## Required fix, approval, or unblock condition
- Item:

## Owner

## Can proceed after

## Notes for executor
```

## Human Override

A human may explicitly accept a readiness gap. Record the approval source and the exact gap accepted before starting work.

Do not treat silence, inferred intent, or old conversation context as approval.

Human override cannot bypass repository safety rules for secrets, customer data, production data, billing, paid ads, external communication, production deployment, sensitive claims, missing review, or unresolved P0/P1 risk.

## Monitoring

Track readiness outcomes in Linear comments or handoffs when useful:

- count of READY tickets
- count of READY WITH APPROVAL tickets and approval type
- count of NOT READY tickets by missing field
- count of BLOCKED tickets by blocker type
- recurring missing fields or ambiguous ticket types

Create a follow-up ticket only when repeated readiness failures show that the template, matrix, workflow, or automation needs improvement.

## Relationship To Execution Handoff

This validator happens before execution. It does not replace PR review, final Linear handoff, or the done criteria in `execution/ticket-pr-handoff-system.md`.
