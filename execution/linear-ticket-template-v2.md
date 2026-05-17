# Linear Ticket Template V2

This template increments the existing Linear ticket pattern for multi-agent execution.

It preserves the current required fields and adds enough structure for Codex, Claude Code, and future orchestrators to judge readiness, ownership, validation, monitoring, and handoff without relying on conversational memory.

Use this template for new tickets that will be executed by agents. Do not use it to migrate existing tickets unless a separate approved ticket asks for migration.

## Design Rules

- Preserve the current Linear fields as the baseline.
- Add only the fields needed to make the ticket executable, reviewable, and traceable.
- Keep optional and conditional fields lightweight when they do not apply.
- Use one ticket for one reviewable outcome.
- Use one branch and one PR per implementation ticket.
- Treat Linear as the source of truth for execution state, ownership, dependencies, blockers, and handoff.
- Treat the repository as the source of truth for durable strategy, architecture, governance, decisions, and evidence.
- Do not create labels, projects, or migrations from this template alone.

## Field Requirement Levels

| Level | Meaning |
|---|---|
| Required | Must be present in every new executable ticket. |
| Conditional | Required only when the ticket type or risk profile makes it relevant. |
| Optional | Useful context, but not required for readiness. |

Use `execution/ticket-type-field-matrix.md` to decide which fields are required, conditional, or not normally needed by ticket type.

## Fields Preserved From Current Pattern

These fields remain part of the baseline and must not be removed:

- Objective
- Why This Matters or Rationale
- Source Rationale
- C.O.N.T.R.O.L.E. Dimensions Supported
- Included Scope
- Excluded Scope
- Deliverables
- Acceptance Criteria
- GO Conditions
- NO-GO Conditions
- Dependencies
- Approval Requirement
- Suggested Owner/Agent or Owner
- Risk Level
- Notes for Implementation or Handoff Notes

## New Required Fields

Every new executable ticket should include:

- Type
- Executor Tool
- Effort
- Complexity
- Parallelizable
- Parallelization Notes
- Prerequisites
- Expected Write Set
- Restricted Files
- Definition of Ready
- Definition of Done
- Validation Plan
- Monitoring Requirements
- Success Metrics
- Rollback or Mitigation
- Follow-up Ticket Criteria
- Agent Execution Notes

## New Conditional Fields

Add these fields when they apply:

- Technical Dependencies: required for code, infrastructure, automation, observability, and technical governance work.
- Operational Dependencies: required when approvals, merge order, external tools, Linear state, or human decisions affect execution.
- Observability Requirements: required for code, infrastructure, automation, observability, and user-facing product changes.
- KPI Impact: required for product, growth, validation, and user-value tickets.
- Human Decision Required: required when a decision blocks start, PR opening, merge, or Done.
- Post-release Follow-up: required for product, infrastructure, automation, observability, or high-risk changes.
- Rollback Signal: required when rollback, mitigation, or operational monitoring must be triggered by a measurable condition.

## Recommended Labels

Use labels only when they improve execution decisions.

Recommended families:

- `priority:P0`, `priority:P1`, `priority:P2`, `priority:P3`
- `risk:low`, `risk:medium`, `risk:high`
- `type:*`
- `horizon:*`
- `source:*`
- `approval:required`, `approval:granted`, `approval:blocker`
- `agent:codex`, `agent:claude`, `agent:orchestrator-future`
- `parallelizable:yes`, `parallelizable:no`, `parallelizable:partial`
- `complexity:low`, `complexity:medium`, `complexity:high`
- `effort:low`, `effort:medium`, `effort:high`

Do not add labels that imply unsupported customers, revenue, compliance, integrations, validation, or production evidence.

## Title Format

Prefer the existing coded format when a code exists:

```txt
PVB-H2-HARDEN-XX - Ticket name
```

For new backlog without a code, use:

```txt
[Area] Verb + object + expected outcome
```

## Ticket Template

```md
# Title

## Objective

## Why This Matters

## Source Rationale

## C.O.N.T.R.O.L.E. Dimensions Supported

## Type
- architecture / documentation / prompt / skill / workflow / governance / code / infrastructure / automation / observability / product / orchestration-prep

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
- Deliverable 2

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

## Prerequisites
- Prerequisite 1

## Technical Dependencies
- Required when technical artifacts, infrastructure, code, automation, or observability are affected.

## Operational Dependencies
- Required when approvals, Linear state, merge order, external tools, or human decisions affect execution.

## Approval Requirement
- Linear ticket creation:
- PR opening:
- PR merge:
- Other gated actions:

## Human Decision Required
- Decision:
- Options:
- Recommendation:
- Required before:

## Suggested Owner/Agent

## Executor Tool
- Codex / Claude Code / Human / Future Orchestrator / Unassigned

## Risk Level
- Low / Medium / High:
- Reason:

## Effort
- Low / Medium / High

## Complexity
- Low / Medium / High

## Parallelizable
- Yes / No / Partial

## Parallelization Notes
- Expected active conflicts:
- Merge-order constraints:
- Work that can run in parallel:
- Work that must be serialized:

## Expected Write Set
- File or bounded directory 1
- File or bounded directory 2

## Restricted Files
- File or artifact family that must not be changed

## Definition of Ready
- Dependency state is clear.
- Approval state is clear.
- Expected write set is declared.
- Validation plan is known.
- Human decisions required before start are resolved or explicitly marked as blockers.

## Definition of Done
- Included scope is complete.
- Excluded scope was not added.
- Acceptance criteria are met.
- Validation plan was executed or unavailable checks are documented.
- Review was completed.
- P0 and P1 findings are resolved.
- Follow-ups were created when required.
- PR is merged when repository changes are part of the ticket.
- Linear final handoff is complete.

## Validation Plan
- Command/check:
- Manual review:
- Unavailable validation:

## Monitoring Requirements
- What should be monitored after implementation:
- Owner or agent responsible for checking:
- Review cadence or trigger:

## Observability Requirements
- Logs:
- Events:
- Metrics:
- Traces:
- Audit trail:
- Healthcheck:

## Success Metrics
- Technical, operational, governance, or product metric 1
- Metric 2
- Metric 3

## KPI Impact
- Required for product, growth, validation, and user-value tickets.
- Primary KPI:
- Secondary KPI:
- Conversion event:
- Adoption metric:
- Retention metric:
- Baseline:
- Post-release follow-up:

## Rollback or Mitigation
- Rollback path:
- Mitigation if rollback is not possible:
- Rollback signal:

## Notes for Implementation
- Important constraints:
- Relevant source artifacts:
- Known pitfalls:

## Follow-up Ticket Criteria
- Create a follow-up if:
- Do not create a follow-up for:

## Agent Execution Notes
- Context to read first:
- Agent-specific constraints:
- Handoff expectation:
```

## Conditional Guidance By Ticket Type

`execution/ticket-type-field-matrix.md` is the durable source for field requirements by ticket type. The guidance below summarizes the most common requirements and should not contradict the matrix.

### Technical, Code, Infrastructure, Automation, And Observability Tickets

Required:

- Technical Dependencies
- Operational Dependencies when approvals, merge order, or external tools matter
- Expected Write Set
- Restricted Files
- Definition of Ready
- Definition of Done
- Validation Plan
- Monitoring Requirements
- Observability Requirements
- Success Metrics
- Rollback or Mitigation
- Follow-up Ticket Criteria

Success Metrics should cover applicable logs, events, traces, operational metrics, expected error behavior, latency, healthcheck, auditability, and rollback signal.

### Architecture, Governance, Documentation, Prompt, Skill, And Workflow Tickets

Required:

- Source Rationale
- Affected protocol, artifact, prompt, skill, or governance surface
- Agent consumers
- Definition of Done
- Validation Plan
- Monitoring Requirements for adoption or adherence
- Success Metrics tied to ambiguity, duplication, handoff, traceability, conflicts, protocol adherence, or ownership clarity
- Follow-up Ticket Criteria

Observability Requirements may be marked not applicable when there is no runtime behavior.

### Product And User-Value Tickets

Required:

- KPI Impact
- Monitoring Requirements
- Success Metrics
- Validation Plan
- Post-release Follow-up
- Rollback or Mitigation when there is a feature flag, critical path, customer-facing workflow, operational risk, pricing, billing, legal, privacy, or sensitive claim impact

Success Metrics should cover primary KPI, secondary KPI, conversion event, expected baseline, adoption, retention when applicable, perceived quality when applicable, and post-release follow-up.

### Orchestration-Prep Tickets

Required:

- Dependency on the Codex + Claude Code baseline unless explicitly waived
- Clear statement that runtime orchestration is not being implemented
- Future orchestrator consumer assumptions
- Definition of Ready that prevents premature execution
- Definition of Done that produces an analysis or adaptation plan, not an orchestrator implementation
- Success Metrics tied to dependency readability, ownership clarity, task distribution readiness, validation routing, conflict handling, and follow-up generation

## Delivery Update Comment Template

Use this final Linear comment after merge or documentary completion.

```md
## Final execution handoff

Branch:
PR:
Merge:
Merge commit:

## Summary

## Acceptance criteria result
- Criterion 1:
- Criterion 2:
- Criterion 3:

## Validation
- Command/check:
- Command/check:

## Review
- Review source:
- P0:
- P1:
- P2:
- P3:
- Fixed in this PR:
- Not fixed:

## Monitoring
- Required follow-up monitoring:
- Owner or agent:
- Trigger or cadence:

## Metrics
- Success metric:
- Current status:
- Follow-up needed:

## Follow-ups
- Link:
- Reason:

## Knowledge updates
- Repository artifact updated:
- Decision or learning recorded:

## Residual risks

## Next recommended action
- Ticket:
- Reason:
```

If no follow-up, monitoring action, knowledge update, or residual risk exists, say that directly.
