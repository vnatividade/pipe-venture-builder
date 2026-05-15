# Linear Governance Model

This model defines how Linear is used to orchestrate approved execution for this repository.

Linear is the source of truth for execution state, priority, ownership, dependencies, blockers, and handoff. Repository artifacts remain the source of truth for strategy, evidence, architecture, governance rules, and decisions.

## Governance Principles

- Use one confirmed Linear project as the execution container before creating scoped tickets.
- Execute one approved ticket at a time, with one branch and one PR per ticket.
- Keep tickets small enough to review independently and trace back to repository artifacts.
- Require human approval before creating Linear projects, creating Linear tickets, opening PRs, merging PRs, or taking any action listed in `execution/approval-gates.md`.
- Do not use Linear to bypass product, validation, risk, or approval gates.

## Project-First Rule

Tickets must not be created without project context.

Before creating execution tickets, the Linear project must be confirmed or explicitly approved for creation. The project record should define:

- product or repository scope
- current milestone sequence
- included and excluded work
- validation or strategy artifacts that authorize the backlog
- approval status for ticket creation
- owner accountable for backlog integrity

If project context is missing, create or execute the setup ticket that establishes it before adding implementation tickets.

## Project Template

Use this structure for the project description or source artifact that governs a Linear project.

```md
## Purpose
What this project exists to coordinate.

## Repository Source Of Truth
- Strategy:
- Validation:
- MVP scope:
- Architecture:
- Approval record:

## Included Scope
- Item 1
- Item 2
- Item 3

## Excluded Scope
- Item 1
- Item 2
- Item 3

## Milestones
- Milestone 1:
- Milestone 2:
- Milestone 3:

## Ticket Creation Rule
Tickets may be created only when they reference approved scope, include acceptance criteria, and identify owner and dependencies.

## Approval Requirements
- Linear project creation:
- Linear ticket creation:
- PR opening:
- PR merge:
- Other gated actions:

## Operating Risks
- Risk:
- Mitigation:
```

## Milestone Rules

Milestones should describe a reviewable operating outcome, not a vague phase.

Recommended foundation milestones:

- Strategy and validation gates
- MVP scope and risk review
- Linear governance workflow
- Architecture readiness
- Ticket execution and handoff

Each milestone should have:

- a concrete outcome
- the artifact or Linear state that proves completion
- explicit dependencies
- an owner or accountable agent role
- clear GO / NO-GO criteria for moving to the next milestone

## Label Rules

Labels should help future agents decide priority, scope, risk, approval needs, and work type without reading conversational history.

Use these label families:

| Family | Examples | Purpose |
|---|---|---|
| Priority | `priority:P0`, `priority:P1`, `priority:P2` | Execution urgency and sequencing. |
| Horizon | `horizon:foundation`, `horizon:mvp`, `horizon:validation` | Where the work fits in the venture pipeline. |
| Type | `type:product`, `type:validation`, `type:linear-governance`, `type:architecture`, `type:implementation` | Primary work category. |
| Risk | `risk:low`, `risk:medium`, `risk:high` | Review and approval sensitivity. |
| Approval | `approval:required`, `approval:granted`, `approval:blocker` | Whether a gated action is present and its current state. |
| Source | `source:user-request`, `source:base-analysis`, `source:follow-up`, `source:review` | Why the ticket exists. |

Do not add labels that imply unsupported evidence, customers, integrations, revenue, or validation.

## Dependency Rules

Dependencies should preserve the venture pipeline order.

- Strategy, validation, MVP scope, risk review, and architecture tickets must precede implementation tickets when those gates are relevant.
- Tickets that create governance or source-of-truth artifacts should block tickets that rely on those rules.
- Follow-up tickets should reference the originating ticket and PR.
- Blocked tickets should state the exact dependency and the unblock condition.
- Do not mark a dependency complete based only on conversational memory.

## Issue Lifecycle

Keep statuses simple and execution-oriented.

| Status | Meaning | Entry Rule | Exit Rule |
|---|---|---|---|
| Backlog | Approved candidate work not yet being executed. | Ticket exists with sufficient context but is not started. | Owner selects it as the one active ticket. |
| Todo | Ready to execute next. | Dependencies and approval state are clear. | Branch work starts. |
| In Progress | Active branch work is underway. | One executor is working the ticket. | PR is opened or work is blocked. |
| In Review | PR exists and review/checks are pending. | PR links the ticket and includes validation notes. | P0/P1 are resolved and PR is ready to merge, or work returns to In Progress. |
| Done | Scope is merged or documentary work is explicitly complete. | PR is merged, or the ticket is documentary/investigative and acceptance criteria are met. | No further work on the ticket. Create follow-ups for new scope. |
| Canceled | Work is no longer valid. | Rationale is documented. | No further work unless a new approved ticket replaces it. |

Do not close implementation tickets without a merged PR.

## Required Ticket Fields

Every Linear ticket should include:

- objective
- rationale or source reason
- included scope
- excluded scope
- deliverables
- acceptance criteria
- GO conditions
- NO-GO conditions
- dependencies
- owner or accountable agent role
- approval requirement
- risk level

## Ticket Description Template

```md
## Objective

## Rationale

## Included Scope

## Excluded Scope

## Deliverables

## Acceptance Criteria
- Criterion 1
- Criterion 2
- Criterion 3

## GO Conditions
- Condition 1
- Condition 2

## NO-GO Conditions
- Condition 1
- Condition 2

## Dependencies
- Dependency 1

## Owner

## Approval Requirement

## Risk Level

## Handoff Notes
```

## Approval Labels

Use approval labels to make gated actions visible:

- `approval:required` means a gated action is present and approval has not yet been recorded.
- `approval:granted` means approval is explicit in the current thread, assigned ticket, PR, or repository artifact.
- `approval:blocker` means the ticket cannot proceed until approval is supplied.

When approval status changes, update the ticket comment or description with the source of approval. Do not replace missing approval with assumptions.

## Review And Merge Rules

Every PR should link the Linear ticket and state:

- ticket context
- included scope
- excluded scope
- validation performed
- review status
- risks and residual concerns
- follow-ups created or intentionally not needed

Review findings are classified using `execution/approval-gates.md`:

- P0 and P1 block merge and must be fixed in the same PR.
- P2 should be fixed only when simple, safe, and inside ticket scope.
- P3 does not block merge.

Do not merge when review is absent, checks have relevant failures, the PR is not linked to the correct ticket, P0/P1 findings are open, required follow-ups are missing, or the PR description is stale.

## Completion Handoff

After merge, update the Linear ticket with:

- branch
- PR
- merge status
- implementation summary
- validations performed
- review result and severity counts
- follow-ups created
- residual risks
- next recommended ticket, if known

Move the ticket to Done only after the handoff is complete.
