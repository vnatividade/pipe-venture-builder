# Knowledge Curator Workflow

This workflow defines how decisions, learning, evidence, and customer language are captured so knowledge compounds across product runs and agent sessions.

It does not define a complex knowledge graph, external MCP sync, or mandatory logging for trivial edits.

## Purpose

The knowledge curator keeps reusable context durable, traceable, and useful for future execution.

Use this workflow to prevent:

- decisions living only in chat history
- customer evidence being mixed with assumptions
- direct quotes being rewritten as synthesis
- stale learnings surviving after new evidence
- sensitive customer context leaking into public docs
- documentation that does not change future execution

## Source Artifacts

Before updating knowledge, read the relevant source artifacts:

- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `product/mvp-scope.md`
- `validation/validation-scorecard.md`
- `validation/customer-interview-template.md`
- `validation/icp-profile.md`
- `knowledge/customer-language-memory.md`
- `execution/ticket-pr-handoff-system.md`
- the assigned Linear ticket and merged PR

Do not use conversation memory as the only source for a durable knowledge update.

## Knowledge Surfaces

| Surface | Purpose | Update Trigger |
|---|---|---|
| Decision log | Records strategic or execution decisions and rationale. | Gate verdicts, PRD/MVP approval, architecture choice, risk acceptance. |
| Learning log | Records what changed because of validation, trial, review, or execution. | Customer discovery, scorecard results, trial feedback, failed assumptions. |
| Evidence repository | Stores links and summaries for source artifacts. | New research, interviews, validation signals, scorecard inputs. |
| Customer-language memory | Preserves exact customer language separately from synthesis. | Real interviews, approved source artifacts, customer objections or triggers. |
| Handoff notes | Keeps future agents able to continue without chat memory. | Every merged PR or completed Linear ticket. |
| Agentic operations learning | Captures recurring execution metrics or operating patterns from Codex, Claude Code, or future agents. | Batch-level pattern changes future sequencing, readiness, validation, parallelization, handoff, or orchestration decisions. |

## Update Cadence By Phase

| Phase | Required Knowledge Update |
|---|---|
| Idea intake | Record raw assumptions and source context only if the idea advances. |
| Founder focus | Record chosen focus, anti-goals, and rejected expansion paths. |
| C.O.N.T.R.O.L.E. | Record verdict, rationale, biggest risk, and revisit trigger. |
| Research and validation | Record evidence, confidence, open assumptions, and source links. |
| Customer discovery | Update exact quotes, status quo patterns, trigger events, objections, and ICP assumptions. |
| Validation scorecard | Record score interpretation, critical gaps, and GO/NO-GO rationale. |
| Working Backwards / PRD | Record accepted claims, unresolved claims, and evidence links. |
| MVP scope | Record riskiest assumption, smallest ethical test, cuts, and threshold. |
| Risk review | Record accepted risks, blocked risks, and required mitigations. |
| Architecture | Record decisions, tradeoffs, constraints, and ADR links. |
| Ticket execution | Record branch, PR, validations, review findings, merge status, and follow-ups. |
| Agentic operations review | Record only recurring metric patterns that change future execution decisions. Routine per-ticket metrics stay in Linear handoffs. |
| Trial / feedback | Record observed behavior, learning, decision impact, and next action. |

If a phase produces no reusable knowledge, state that in the Linear handoff instead of creating empty documentation.

For agentic operations metrics, use `execution/agentic-operations-metrics.md`. Keep the initial metric record in PR and Linear handoffs. Update `knowledge/` only when a batch summary or repeated signal changes future execution.

## Update Workflow

1. Identify the originating Linear ticket and PR.
2. Identify whether the update is a decision, learning, evidence, customer language, or handoff.
3. Verify the source artifact exists.
4. Separate quote, evidence, assumption, and synthesis.
5. Redact sensitive details before writing to repository docs.
6. Update the smallest relevant knowledge surface.
7. Link the source ticket, PR, or artifact.
8. Record any follow-up ticket needed for unresolved risk, stale context, or missing evidence.

For strategic decisions, use `knowledge/kdr-dar-template.md` instead of burying the rationale in a generic handoff note.

Before accepting a new strategic decision, run `knowledge/decision-conflict-protocol.md` to check prior KDRs, ADRs, MVP scope, risk review, PRD, and validation artifacts. Mark supersession or unresolved conflict in the KDR/DAR when needed.

## Evidence Separation Rules

| Type | Definition | Allowed Source |
|---|---|---|
| Quote | Exact words from a real customer or approved source. | Interview notes, customer messages, approved source artifact. |
| Evidence | Observable behavior, commitment, spend, workaround, or validated source. | Discovery notes, scorecard, trial result, research source. |
| Assumption | Belief that still needs validation. | Founder hypothesis, agent synthesis, synthetic persona hypothesis. |
| Synthesis | Interpretation across quotes, evidence, and assumptions. | Knowledge curator analysis tied to sources. |

Synthetic persona output may help create assumptions or questions. It must not be stored as real customer evidence.

## Redaction And Sensitivity Guidance

Human review is required before storing sensitive data.

Redact or avoid:

- real customer names unless explicitly approved
- emails, phone numbers, addresses, payment data, credentials, tokens, or private keys
- health, legal, financial, compliance, or regulated personal data
- confidential customer business details
- identifiable quotes intended for external use
- production or customer data copied from systems

Use anonymized labels such as `ICP-A interview 2026-05-15` when possible.

If the data must remain private or local, record only a pointer to the approved private storage location and the reason.

## Knowledge Quality Gate

A knowledge update is useful only when it changes future execution.

Before committing a knowledge update, answer:

- What future decision does this support?
- What source proves or motivates it?
- What assumption is now weaker or stronger?
- What should future agents do differently?
- What should be revisited, and when?

If the answer is unclear, do not create new knowledge documentation. Add the relevant note to the Linear handoff instead.

## Handoff Checklist

Every completed ticket should record:

- Linear ticket:
- PR:
- Merge reference:
- Decision or learning:
- Evidence source:
- Customer-language update needed: yes/no
- Sensitive data involved: yes/no
- Redaction completed: yes/no/not applicable
- Follow-up tickets:

## Out Of Scope

- complex graph database modeling
- external Notion/MCP synchronization
- automatic customer-data ingestion
- public publishing of customer quotes
- making unsupported claims from weak evidence
