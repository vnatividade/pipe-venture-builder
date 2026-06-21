# Tactical Execution Plan

Use this artifact before meaningful development work starts.

It turns approved PRD, MVP scope, risk review, architecture direction, and Linear ticket context into an execution-ready plan for one implementation wave or one complex ticket. It does not replace validation, PRD, MVP scope, architecture review, ADRs, Linear tickets, PR review, `/pipe:check`, or `DeliveryEvidence`.

## Purpose

The Tactical Execution Plan exists so agents can answer, before coding:

- What exactly are we building or changing?
- Which approved artifact justifies this work?
- Which tickets, stories, or slices will deliver it?
- Which ADRs, RFCs, or architecture decisions are needed?
- Which tests, manual checks, E2E checks, schema checks, and delivery evidence will prove completion?
- Which docs, observability notes, rollback or mitigation notes, and learning artifacts must be updated?
- What must stop the work before implementation, PR opening, review completion, or merge?

## Applicability

### Required

A Tactical Execution Plan is required before branch work when a ticket or ticket set includes:

- code behavior
- infrastructure
- automation
- observability instrumentation
- customer-facing product behavior
- user-facing UI, prototype, onboarding, billing, or permissions
- data handling, integrations, runtime workflows, deployment, or production exposure
- multiple implementation stories, dependencies, or merge-order constraints
- ADR, RFC, architecture-review, or risk-review decisions that affect implementation

### Conditional

A lightweight Tactical Execution Plan is enough when the work is:

- documentation or governance that defines a new executable development workflow
- architecture or planning work that will immediately create implementation tickets
- a small technical change whose ticket already contains most required fields

In these cases, the plan may be a short section in the Linear ticket, PR body, or repository artifact if it preserves the required decisions.

### Not Applicable

Mark the Tactical Execution Plan as `not applicable` when the ticket is:

- typo, copy, formatting, or link maintenance
- internal research or discovery planning with no build work
- documentation-only clarification that does not create implementation work
- Linear or GitHub handoff bookkeeping
- a future/backlog ticket that explicitly does not authorize implementation

Do not use `not applicable` for code, infrastructure, automation, observability, customer-facing product behavior, or multi-ticket development work.

## Gate Rule

Before `/pipe:build` starts, the executor must record one of:

- `Tactical Execution Plan: required - linked at <path or URL>`
- `Tactical Execution Plan: lightweight - included in <ticket, PRD, architecture review, or PR>`
- `Tactical Execution Plan: not applicable - <reason>`

If the plan is required and missing, the ticket is `NOT READY` or `BLOCKED` in `execution/agent-readiness-validator.md`.

The plan does not authorize gated actions by itself. Human approval is still required for Linear writes, PR opening, merge, production deployment, billing, paid acquisition, external communication, customer data, secrets, production data, sensitive claims, or any other gate in `execution/approval-gates.md`.

## Template

```md
# Tactical Execution Plan - <ticket or implementation wave>

## Metadata

- Origin Linear ticket:
- Date:
- Owner:
- Executor:
- Related PRD:
- Related MVP scope:
- Related risk review:
- Related architecture review:
- Tactical plan status: required / lightweight / not applicable

## Source Inputs

- Approved product or governance source:
- Validation gate or not-applicable reason:
- PRD or blocker:
- MVP scope or blocker:
- Architecture direction or blocker:
- Risk review status:
- Linear project:
- Dependencies:

## Execution Objective

- One outcome:
- User, agent, or system-visible change:
- Non-goals:
- Success signal:

## Ticket And Story Breakdown

| Sequence | Ticket or story | Output | Owner | Expected write set | Dependency | Acceptance check | Evidence required |
|---|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |  |

## ADR And Decision Path

- ADR needed: yes / no
- RFC needed: yes / no
- Existing decisions:
- Candidate decisions:
- No-ADR rationale, if not needed:
- Human decision required:

## Development Loop

Use `execution/development-execution-loop.md` as the operating rule for implementing this plan.

For each story or ticket:

1. Plan the smallest slice.
2. Implement only the approved slice.
3. Validate with the strongest relevant checks.
4. Repair failures before expanding scope.
5. Update docs, evidence, and risks.
6. Prepare review handoff.
7. Record follow-ups only for out-of-scope work.

## Validation And Delivery Evidence Plan

- BDD or acceptance examples:
- Unit tests:
- Integration or contract tests:
- Schema checks:
- Lint, typecheck, build, or static checks:
- E2E or browser checks:
- Manual checks:
- DeliveryEvidence required: yes / no
- DeliveryEvidence path or handoff location:
- Unavailable checks and reason:

## Observability And Runtime Evidence

- Observability required: yes / no
- Signal names or event shapes:
- Owner and threshold:
- Dashboard, monitor, log, metric, or trace reference:
- Data boundary:
- Cost or volume boundary:

## Documentation And Knowledge Updates

- Docs to update:
- PRD or MVP scope update:
- Architecture update:
- ADR/KDR/DAR/LearningRecord candidate:
- Linear handoff notes:

## Risks, Rollback, And Mitigation

- P0/P1 risks:
- P2/P3 risks:
- Rollback or mitigation:
- Stop condition:
- Follow-up ticket trigger:

## GO / NO-GO

- GO when:
- CONDITIONAL GO when:
- BLOCKED when:
- NO-GO when:

## `/pipe:check` And Handoff

- `/pipe:check` evidence to inspect:
- Review readiness:
- Merge readiness:
- Final Linear handoff requirements:
```

## Minimum Lightweight Block

Use this inside a Linear ticket, PR body, or architecture note when a full standalone plan would be unnecessary:

```md
## Tactical Execution Plan

- Status: lightweight / not applicable
- Reason:
- Approved source:
- Scope slices:
- Development loop status:
- ADR/RFC needed:
- Validation plan:
- DeliveryEvidence required:
- Docs/observability updates:
- Stop condition:
```

## Required Cross-Checks

Before implementation starts, check:

- `execution/core-pipeline-map.md` for upstream gates
- `execution/agent-readiness-validator.md` for readiness
- `execution/linear-ticket-template-v2.md` for ticket fields
- `execution/ticket-type-field-matrix.md` for type-specific fields
- `execution/development-execution-loop.md` for plan, implement, validate, repair, document, review, and handoff states
- `architecture/technical-decision-guide.md` for ADR/RFC need
- `execution/test-oriented-delivery-rule.md` for evidence type
- `execution/pipe-check-command-spec.md` for delivery quality checks
- `schemas/DeliveryEvidence.schema.json` when structured delivery evidence is required

## Done Criteria

The Tactical Execution Plan is complete when it:

- identifies the source artifact that authorizes the work
- maps scope into tickets, stories, or implementation slices
- states ADR/RFC needs or no-ADR rationale
- defines validation and DeliveryEvidence expectations
- states documentation and observability updates
- records rollback, mitigation, stop conditions, and follow-up triggers
- is linked from the Linear ticket, PR, or relevant repository artifact
