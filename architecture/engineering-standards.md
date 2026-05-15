# Engineering Standards

These standards keep implementation small, reversible, and traceable.

They are not an exhaustive engineering handbook. Prefer nearby documentation, linked tickets, and focused PRs over central bureaucracy.

## When To Use

Use these standards when:

- creating an architecture review, RFC, ADR, or implementation ticket
- changing system boundaries, data handling, integrations, infrastructure, or reliability posture
- reviewing a PR that introduces technical risk
- deciding whether a change needs human review

Do not require ADRs, RFCs, or architecture review for trivial edits, copy changes, formatting, routine cleanup, or local implementation details that do not affect future execution.

## Core Principles

- Validate before scaling.
- Build for the current MVP core loop, not an imagined platform.
- Keep changes reversible unless the ticket explicitly justifies otherwise.
- Prefer manual workflow over automation until the bottleneck is validated.
- Keep data collection minimal and tied to validation or product need.
- Defer integrations unless they are required for the riskiest assumption.
- Link technical decisions to Linear tickets and source artifacts.

## Decision Artifacts

| Artifact | Use when | Required link |
|---|---|---|
| Architecture review | MVP scope becomes a technical recommendation. | Linear ticket and PRD |
| RFC | A technical proposal needs review before implementation. | Linear ticket |
| ADR | A structural decision has been accepted and future agents need durable rationale. | Linear ticket and PR |
| KDR/DAR | A strategic product, validation, risk, or governance decision needs durable rationale. | Linear ticket and source artifact |

## Lightweight Quality Bar

Before implementation tickets proceed:

- MVP core loop and riskiest assumption are linked
- acceptance criteria are testable
- data and integration boundaries are explicit
- P0/P1 risks are mitigated or blocking
- human approval is recorded when required
- deferred complexity is listed rather than quietly implemented

## PR Expectations

Every technical PR should state:

- linked Linear ticket
- included scope
- excluded scope
- validation performed
- risk or approval status
- follow-ups created or explicitly not needed

## Human Review Triggers

Require human review before structural decisions that:

- change architecture boundaries
- change data, privacy, security, billing, production, or integration posture
- accept unresolved risk
- create irreversible or hard-to-reverse operational impact
- broaden MVP scope beyond the PRD or architecture review

## Versioning

Decision docs are versioned through Git and linked PRs.

When updating an ADR, RFC, or standards doc:

- link the Linear ticket
- explain what changed
- preserve old rationale unless it is explicitly superseded
- mark supersession rather than silently deleting context
