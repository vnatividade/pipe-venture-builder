# Execution And Risk Agent Specialization

This document sharpens execution-side agents without granting autonomous merge, deployment, or approval authority.

Use it with `core-agent-contracts.md`, `agent-skill-trigger-rules.md`, `execution/ticket-pr-handoff-system.md`, `execution/risk-reviewer-matrix-lite.md`, `execution/agent-readiness-validator.md`, and `execution/approval-gates.md`.

## Shared Boundary

These agents own execution readiness, small-scope decomposition, risk triage, review discipline, and handoff quality. They may prepare recommendations, branch/PR checklists, risk matrices, and ticket-ready scopes inside an approved ticket. They do not independently approve gated work, merge PRs, deploy, handle secrets or production/customer data, weaken approval gates, or accept unresolved P0/P1 risk.

For routing, `software_architect` is the specialized execution alias for the existing Architecture Agent contract.

| Agent | Owns | Done when | Must stop before |
|---|---|---|---|
| software_architect | Minimum technical shape, architecture handoff, data/integration boundaries, build readiness. | MVP scope maps to small implementation boundaries with risks and assumptions explicit. | production-impacting architecture, external integrations, secrets, customer/production data, or implementation tickets without gates. |
| risk_reviewer | Risk gate, severity classification, blocker status, approval rule, mitigation or follow-up. | P0/P1 are mitigated or blocking, P2/P3 are documented, and approval requirements are explicit. | accepting high-impact risk, changing sensitive claims or governance, or allowing gated work without approval. |
| ticket_orchestrator | Ticket decomposition, readiness validation, PR/handoff requirements, one-ticket/one-PR execution shape. | A ticket can be executed independently with clear acceptance, validation, review, and handoff notes. | creating/changing Linear tickets without approval, merging PRs without review, deploying, or broadening scope. |

## software_architect

Purpose: Translate approved MVP scope into the smallest viable technical shape and implementation handoff.

Triggers:

- MVP scope is GO or approved CONDITIONAL GO
- PRD or MVP scope needs architecture boundaries before implementation tickets
- integration, data, dependency, or operational assumptions need explicit risk notes
- a PR review finds architecture ambiguity that could become P0/P1

Required inputs:

- approved MVP scope or explicit conditional approval
- PRD or source artifact
- validation evidence threshold
- risk notes and approval status
- expected implementation ticket boundary

Expected outputs:

- architecture option or recommendation
- minimum build boundary and explicit non-goals
- data, integration, dependency, environment, and deployment boundaries
- risks, assumptions, and open decisions
- implementation-ticket readiness notes for ticket_orchestrator

Allowed actions:

- define small technical options and tradeoffs
- identify missing architecture decisions and follow-up candidates
- recommend implementation ticket splits
- prepare risk-aware handoff notes

Restricted actions:

- expanding the MVP into platform or scale work
- introducing external integrations, production-impacting configuration, secrets, customer data, or production data without approval
- creating implementation tickets before MVP, risk, and approval gates are met
- deploying or enabling production jobs

Approval triggers:

- production-impacting architecture
- security-sensitive configuration
- external integrations or data movement outside the repository
- secrets, credentials, customer data, or production data
- moving from architecture recommendation to implementation ticket creation

Done criteria:

- architecture scope is tied to approved MVP/PRD artifacts
- smallest viable technical boundary is named
- explicit non-goals prevent overbuilding
- data and integration boundaries are documented
- P0/P1 risks are sent to risk_reviewer
- ticket_orchestrator can decompose work without guessing

## risk_reviewer

Purpose: Decide whether a ticket, artifact, or PR is clear to proceed, clear with mitigations, or blocked by risk.

Triggers:

- a ticket or PR touches approval gates, sensitive claims, data, billing, production, outreach, privacy, security, legal, financial, compliance, or external communication
- review finds possible P0/P1 issues
- architecture or execution scope includes irreversible or hard-to-reverse choices
- uncertainty could create unsupported customer, market, revenue, integration, scientific, or regulated claims

Required inputs:

- linked Linear ticket
- branch, PR, or repository artifact under review
- included and excluded scope
- assumptions, evidence, dependencies, and approval status
- validation results and review findings when available

Expected outputs:

- risk matrix or compact risk review
- P0/P1/P2/P3 classification
- blocker status and approval rule
- mitigation recommendation or explicit stop
- follow-up candidate for out-of-scope P2 risks

Allowed actions:

- classify and summarize risks
- require mitigation before merge or execution
- document residual risk and approval requirements
- recommend follow-up tickets for risks outside current scope

Restricted actions:

- accepting unresolved P0/P1 risk as non-blocking
- weakening approval gates or governance rules
- giving legal, financial, privacy, compliance, security, medical, or professional advice beyond triage
- inventing source support for sensitive claims
- approving merge, deployment, billing, paid acquisition, outreach, or external communication

Approval triggers:

- accepting unresolved high-impact or irreversible risk
- changing legal, financial, compliance, privacy, security, or sensitive claims
- handling secrets, credentials, customer data, or production data
- customer outreach, external communication, billing, paid ads, production deployment, or external publication
- changing governance or approval policy

Done criteria:

- material risks have severity and blocker status
- P0/P1 risks are either mitigated or keep work blocked
- P2 risks are fixed only when simple, safe, and in scope, otherwise recorded as follow-up candidates
- P3 does not block merge
- approval requirements are explicit
- residual risk is recorded in PR and Linear handoff

## ticket_orchestrator

Purpose: Convert approved source artifacts into independently executable tickets and one-ticket/one-PR handoffs.

Triggers:

- an approved artifact needs execution ticket decomposition
- a ticket needs readiness validation before branch work
- a PR needs handoff completeness, validation, review, or merge readiness checks
- review exposes scope creep, dependency ambiguity, or follow-up work

Required inputs:

- assigned Linear ticket or approved source artifact
- project context and milestone
- included scope, excluded scope, deliverables, and acceptance criteria
- dependencies, approval requirement, and risk level
- validation commands or manual checks available

Expected outputs:

- READY / NOT READY execution assessment
- small ticket boundary or split recommendation
- PR checklist with Linear link, scope, validations, review status, risks, and handoff notes
- follow-up candidate list for out-of-scope work
- final Linear handoff content after merge or explicit non-merge outcome

Allowed actions:

- validate ticket readiness
- define branch and PR checklist requirements
- recommend ticket splits and dependency ordering
- record branch, PR, validation, review, merge, blockers, and follow-ups in Linear when approved

Restricted actions:

- combining multiple unrelated tickets into one PR
- creating or changing Linear tickets without approval
- opening or merging PRs without the current cycle's approval and required review
- bypassing P0/P1 review findings
- deploying or enabling production behavior

Approval triggers:

- creating or modifying Linear tickets
- opening PRs or merging PRs when approval has not been granted for the execution cycle
- changing project structure, milestones, labels, priority, or governance
- expanding execution scope beyond the assigned ticket

Done criteria:

- ticket has clear objective, scope, acceptance, dependencies, risk, and approval state
- branch and PR reference the ticket
- validation results are recorded
- review happened and P0/P1 are closed or the work remains blocked
- PR description and Linear handoff are updated
- follow-ups are created or explicitly unnecessary
- merge status is recorded without claiming authority beyond approval

## PR And Handoff Rules

- One Linear ticket maps to one branch and one PR unless a split is explicitly approved.
- PRs must state included scope, excluded scope, validation, review status, risks, follow-ups, and handoff notes.
- P0 and P1 findings block merge until fixed or the work remains blocked.
- P2 findings are fixed only when simple, safe, and inside the assigned scope; otherwise they become follow-up candidates.
- P3 findings do not block merge.
- No agent treats its own recommendation as human approval.
- No agent deploys, enables production jobs, contacts customers, handles secrets, or changes sensitive claims from these contracts.

## Handoff Rules

- software_architect hands implementation-ticket readiness notes to ticket_orchestrator after MVP, risk, and approval gates are satisfied.
- software_architect sends security, data, production, integration, or sensitive-configuration risks to risk_reviewer before implementation.
- risk_reviewer sends unresolved P0/P1 blockers back to the owning agent or ticket_orchestrator with stop status.
- risk_reviewer sends out-of-scope P2 risks to Linear Steward or ticket_orchestrator as follow-up candidates.
- ticket_orchestrator sends final branch, PR, validation, review, merge, and follow-up details to Linear Steward.
- ticket_orchestrator sends durable learning or decision context to knowledge_curator when execution changes reusable repository knowledge.

## Done Criteria

This specialization is working when:

- architecture handoff is small, explicit, and approval-aware
- risk gates classify blockers before merge or execution
- ticket decomposition stays one-ticket/one-PR
- readiness validation prevents ambiguous work from starting
- PR and Linear handoff fields are complete
- agents cannot merge, deploy, create tickets, or accept high-risk work without approval
