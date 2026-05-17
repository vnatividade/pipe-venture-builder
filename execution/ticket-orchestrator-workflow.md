# Ticket Orchestrator Workflow

This workflow defines how approved PRD, MVP scope, architecture, risk, and validation artifacts become small Linear issue proposals.

It does not authorize direct Linear ticket creation. Creating or modifying Linear tickets requires explicit approval according to `execution/approval-gates.md` and `execution/linear-governance-model.md`.

## Purpose

The ticket orchestrator turns approved repository artifacts into executable ticket proposals that are small, dependency-aware, reviewable, and safe for agent execution.

Use this workflow to prevent:

- mega-tickets
- hidden dependencies
- implementation before validation gates
- ambiguous acceptance criteria
- missing owners
- missing approval gates
- future/evolution work entering the current execution cycle

## Required Inputs

Before proposing tickets, read:

- approved PRD or product requirements artifact
- approved MVP scope or validation artifact
- architecture notes, when technical work is involved
- risk review or risk matrix, when applicable
- Linear project context
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/agent-readiness-validator.md`

If any required source artifact is missing, stop and propose the missing setup or review step instead of inventing ticket scope.

## Readiness Gate

The orchestrator may propose tickets only when:

- the Linear project is confirmed
- source artifacts are approved or explicitly accepted for the current phase
- implementation gates in `execution/core-pipeline-map.md` are satisfied for build work
- risks are reviewed or marked for review
- ticket creation approval is present before writing to Linear

If approval is missing, produce a ticket proposal artifact only. Do not create or update Linear tickets.

## Now / Next / Later Separation

Classify every candidate ticket before writing it.

| Bucket | Meaning | Linear Action |
|---|---|---|
| Now | Current-cycle work needed to unblock approved scope or governance. | May be proposed for creation after approval. |
| Next | Sequenced work that depends on Now tickets or near-term artifacts. | Keep as proposal until dependencies are done. |
| Later | Future, speculative, improvement, or evolution work. | Do not execute in current-only cycles. |

Rules:

- Now tickets must be tied to an approved source artifact and current milestone.
- Next tickets must name their dependency and unblock condition.
- Later tickets must not be executed when the cycle forbids future/evolution work.
- If a candidate has `horizon:future`, `source:future-evolution`, or clearly speculative scope, classify it as Later.

## Decomposition Rules

Create one ticket proposal per reviewable outcome.

A good ticket:

- has one objective
- updates one artifact family or one bounded behavior
- can be implemented in one branch and one PR
- has explicit included and excluded scope
- names dependencies
- names owner or accountable agent role
- names approval requirement
- names validation or review expectation

Split a candidate when:

- it spans multiple pipeline phases
- it combines strategy, validation, architecture, implementation, and learning
- it mixes unrelated artifacts
- it needs different reviewers or approval gates
- part of the work is future/evolution
- part of the work is blocked while another part is ready

Do not split so small that tickets become clerical noise. Each ticket should still produce a meaningful artifact, decision, or bounded change.

## Dependency Mapping

Every ticket proposal should state:

- direct dependencies
- unblock condition
- whether the dependency is repository artifact, Linear ticket, approval, review, or external action
- whether the dependency blocks start, PR opening, merge, or Done

Dependency rule:

```txt
strategy / validation / MVP scope / risk / architecture
-> project confirmation
-> ticket creation approval
-> ticket execution
-> review and merge
-> learning handoff
```

Do not mark dependencies complete based only on chat memory. Link the repository artifact, Linear ticket, PR, or approval comment.

## Acceptance Criteria Rules

Acceptance criteria must be observable.

Use criteria that answer:

- What file, artifact, state, or behavior changes?
- What must be explicitly included?
- What must remain excluded?
- What validation or review proves completion?
- What approval gate must be recorded?

Avoid criteria like:

- "Improve the workflow"
- "Make it better"
- "Add robust support"
- "Handle everything"

Prefer criteria like:

- "`execution/foo.md` defines X, Y, and Z."
- "The PR links the originating Linear ticket."
- "The workflow states that ticket creation requires approval."
- "The validator can mark the ticket READY / NOT READY with reasons."

## Owner Assignment

Assign one accountable owner or agent role per ticket proposal.

Default owner mapping:

| Work Type | Owner / Agent Role |
|---|---|
| Product context, founder focus, PRD | Product Strategist Agent |
| Validation scorecards, ICP, evidence thresholds | Validation Agent |
| Research synthesis | Research Agent |
| Architecture notes and constraints | Architecture Agent |
| Risk review and mitigations | Risk Reviewer Agent |
| Linear state, labels, status, handoff | Linear Steward Agent |
| Ticket decomposition and sequencing | Ticket Orchestrator Agent |
| KDR, learning, customer language memory | Knowledge Curator Agent |
| Growth or content strategy | Growth Strategist Agent / Content Strategy Agent |
| Billing strategy | Billing Strategy Agent |

If more than one owner seems necessary, split the ticket or name the primary owner and supporting reviewer.

## Approval Labels

Recommended labels for proposed tickets:

- priority: `priority:P0`, `priority:P1`, `priority:P2`
- horizon: `horizon:foundation`, `horizon:operationalization`, `horizon:mvp`, `horizon:validation`, or `horizon:future`
- type: `type:product`, `type:validation`, `type:research`, `type:architecture`, `type:linear-governance`, `type:agent`, `type:implementation`, `type:knowledge-base`
- risk: `risk:low`, `risk:medium`, `risk:high`
- approval: `approval:required`, `approval:granted`, `approval:blocker`
- source: `source:user-request`, `source:base-analysis`, `source:incremental-analysis`, `source:review`, `source:follow-up`, or `source:future-evolution`

Do not use labels to imply unsupported evidence, customers, revenue, integrations, market validation, or compliance.

## Ticket Proposal Template

Use this template before creating a Linear issue when a lightweight proposal is enough.

For new tickets intended for Codex, Claude Code, or future orchestrator consumption, use `execution/linear-ticket-template-v2.md` instead. The v2 template preserves the fields below and adds readiness, parallelization, write-set, validation, monitoring, metrics, rollback, follow-up, and agent execution fields. Do not use the v2 template to migrate existing tickets unless a separate approved ticket asks for that migration.

```md
## Source Artifact
- Artifact:
- Origin ticket or PR:
- Approval source:

## Now / Next / Later
- Bucket:
- Reason:

## Objective

## Why This Matters

## Included Scope
- Item 1
- Item 2
- Item 3

## Excluded Scope
- Item 1
- Item 2
- Item 3

## Deliverables
- Deliverable 1

## Acceptance Criteria
- Criterion 1
- Criterion 2
- Criterion 3

## Dependencies
- Dependency:
- Unblock condition:

## Owner / Agent Role

## Approval Requirement
- Linear ticket creation:
- PR opening:
- PR merge:
- Other gated actions:

## Risk Level
- Low / Medium / High:
- Reason:

## Suggested Labels
- priority:
- horizon:
- type:
- risk:
- approval:
- source:

## Validation Expectation
- Command/check:
- Manual review:

## Handoff Notes
- What future agents need:
```

## Linear Write Rule

Before writing to Linear:

1. Confirm the Linear project.
2. Confirm ticket creation approval.
3. Confirm the proposal is Now or explicitly approved Next.
4. Confirm no future/evolution scope is being executed in the current cycle.
5. Confirm the issue is small enough for one branch and PR.

If any item fails, do not create the ticket. Record the blocker or keep the proposal in the repository/PR handoff.

## Done Criteria

Ticket orchestration is complete when:

- proposed tickets each map to one outcome
- each proposal cites a source artifact
- dependencies and unblock conditions are explicit
- acceptance criteria are observable
- owner or agent role is named
- approval requirements and labels are explicit
- Now / Next / Later classification is clear
- no direct Linear write occurs without approval
