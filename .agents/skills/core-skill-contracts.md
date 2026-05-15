# Core Skill Contracts

These contracts define the initial reusable skill set for this repository. They describe when a workflow should be loaded and what it should produce; they do not create executable automation or a full skill tree.

Skills should be small, composable, and loaded only when their trigger matches the current task. Use progressive disclosure: keep the main skill concise and point to repository artifacts for detail.

## Shared Skill Rules

- A skill supports one workflow, not an entire venture-building phase.
- A skill must name its trigger narrowly enough to avoid loading on unrelated work.
- A skill must produce a concrete output or stop condition.
- A skill must read repository artifacts before relying on memory.
- A skill must state approval gates when the workflow touches Linear, PRs, customer data, external communication, billing, production, or sensitive claims.
- A skill must not duplicate whole source repositories, broad playbooks, or future/evolution workflows.

## Skill Contract Template

Use this template before creating a future `SKILL.md`.

```md
# <Skill Name>

## Purpose

One sentence describing the workflow this skill supports.

## Trigger

Use when:

- specific trigger 1
- specific trigger 2

Do not use when:

- nearby but out-of-scope task
- future/evolution workflow

## Inputs

- required input 1
- required input 2
- source artifact or ticket

## Files To Read First

- `path/to/artifact.md`
- linked Linear ticket or PR, when applicable

## Workflow

1. Step one.
2. Step two.
3. Stop or hand off if approval is missing.

## Expected Output

- concrete artifact, recommendation, checklist, or handoff
- explicit blocker when work cannot proceed

## Approval Rules

Stop before:

- gated action 1
- gated action 2

## Restrictions

- things this skill must not do
```

## Initial Skill List

| Skill | Narrow Trigger | Expected Output | Primary Agent |
|---|---|---|---|
| Validation planning | Product assumptions need validation questions or a scorecard path. | Validation plan outline or scorecard update guidance. | Validation Agent |
| PRD drafting | Validated product framing needs PRD-ready structure. | PRD outline tied to evidence, goals, non-goals, and requirements. | Product Strategist Agent |
| Linear governance | Work needs Linear project, ticket, status, dependency, or handoff rules. | Linear action checklist or blocker. | Linear Steward Agent |
| Execution handoff | A branch, PR, or ticket needs final handoff. | Final handoff checklist with validation, review, merge, risks, and follow-ups. | Ticket Orchestrator Agent |
| Research synthesis | A decision needs source-backed findings and confidence. | Research synthesis with sources, confidence, contradictions, and implications. | Research Agent |
| Knowledge update | A ticket creates durable decision or learning context. | KDR, learning note, or explicit no-update rationale. | Knowledge Curator Agent |

## Validation Planning Skill Contract

Purpose: Turn product assumptions into a validation workflow without starting outreach.

Trigger:

- use when a product context, founder focus, or C.O.N.T.R.O.L.E. verdict needs validation questions, scorecard criteria, or evidence thresholds
- do not use for customer outreach execution or growth experiments

Inputs:

- product context
- founder focus
- C.O.N.T.R.O.L.E. verdict
- existing validation artifacts

Files to read first:

- `validation/validation-scorecard.md`
- `validation/icp-profile.md`
- `validation/customer-interview-template.md`
- `validation/customer-data-retention-policy.md`
- `execution/core-pipeline-map.md`

Expected output:

- validation questions
- evidence gaps
- scorecard or experiment guidance
- GO / CONDITIONAL GO / NO-GO implications
- approval blockers before outreach or data handling

Approval rules:

- stop before contacting customers
- stop before storing identifiable customer data
- stop before external communication
- stop before changing sensitive claims

## PRD Drafting Skill Contract

Purpose: Convert validated product framing into a lean PRD structure.

Trigger:

- use when Working Backwards, validation evidence, or MVP scope needs PRD-ready organization
- do not use before validation artifacts identify what must be learned

Inputs:

- product context
- founder focus
- validation scorecard
- MVP scope notes, if available
- evidence links

Files to read first:

- `product/product-context.md`
- `product/founder-focus.md`
- `product/mvp-scope.md`
- `validation/validation-scorecard.md`
- `execution/core-pipeline-map.md`

Expected output:

- PRD outline
- goals and non-goals
- user stories or requirements
- assumptions and evidence links
- unresolved blockers

Approval rules:

- stop before treating unsupported claims as accepted
- stop before creating implementation tickets
- stop before broadening MVP scope

## Linear Governance Skill Contract

Purpose: Apply Linear governance rules to ticket and status decisions.

Trigger:

- use when selecting a ticket, updating status, linking a PR, documenting blockers, or preparing Linear handoff
- do not use to create new Linear projects or tickets unless approval is explicit

Inputs:

- Linear ticket
- repository branch or PR
- validation and review results
- blocker or follow-up context

Files to read first:

- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/approval-gates.md`
- assigned Linear ticket

Expected output:

- status recommendation
- required Linear comment or handoff
- PR link and branch traceability
- approval or blocker note

Approval rules:

- stop before creating Linear projects
- stop before creating Linear tickets
- stop before changing project structure, milestones, or governance labels

## Execution Handoff Skill Contract

Purpose: Produce complete handoff for a branch, PR, or completed ticket.

Trigger:

- use before marking a ticket Done
- use before or after PR merge when validation, review, or follow-ups must be summarized
- do not use as a substitute for PR review

Inputs:

- Linear ticket
- branch name
- PR link
- validation results
- review findings
- merge status
- follow-up decisions

Files to read first:

- `execution/ticket-pr-handoff-system.md`
- `.github/pull_request_template.md`
- linked PR
- assigned Linear ticket

Expected output:

- final handoff comment
- validation summary
- review summary with P0 / P1 / P2 / P3 counts
- follow-up list or explicit none
- residual risks

Approval rules:

- stop before PR merge if review is absent
- stop before Done if P0/P1 findings remain
- stop before creating follow-up tickets unless approval exists

## Research Synthesis Skill Contract

Purpose: Convert source material into decision-ready research without overstating evidence.

Trigger:

- use when a product, validation, architecture, or risk decision needs external or repository source synthesis
- do not use to replace customer discovery or make unsupported market-proof claims

Inputs:

- research question
- source links or repository artifacts
- decision that depends on the research

Files to read first:

- `research/README.md`
- `execution/approval-gates.md`
- relevant product or validation artifact

Expected output:

- source list with dates where available
- findings
- confidence level
- contradictions or missing evidence
- implications for the next repository artifact

Approval rules:

- stop before using paid/private sources
- stop before making legal, financial, compliance, privacy, security, scientific, or sensitive claims
- stop before publishing or external communication

## Knowledge Update Skill Contract

Purpose: Decide whether durable knowledge should be recorded and create the smallest useful update.

Trigger:

- use when a ticket creates a durable decision, learning, evidence pointer, customer-language update, or KDR output
- do not use for routine implementation details already captured in PR and Linear handoff

Inputs:

- source ticket or PR
- decision or learning
- source artifacts
- residual risks or revisit trigger

Files to read first:

- `knowledge/README.md`
- `knowledge/customer-language-memory.md`
- `validation/customer-data-retention-policy.md`
- `execution/ticket-pr-handoff-system.md`

Expected output:

- KDR or learning update
- customer-language update when safe and sourced
- explicit no-update rationale when knowledge artifact is unnecessary
- revisit trigger

Approval rules:

- stop before storing customer data
- stop before preserving private context beyond approved retention
- stop before changing sensitive claims

## Skill Creation Rule

Create a concrete `SKILL.md` only through a dedicated approved ticket. Until then, these contracts define the intended workflow boundaries.
