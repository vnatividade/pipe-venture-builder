# AGENTS.md - pipe-venture-builder

## Non-Negotiable Safety Rules

Agents operating in this repository must preserve founder solo velocity, strategic focus, traceability, and human approval gates.

Stop and request human approval before:

- creating Linear projects
- creating Linear tickets
- opening PRs
- merging PRs
- deploying to production
- enabling billing, pricing collection, paid ads, or paid acquisition
- handling secrets, credentials, tokens, private keys, customer data, or production data
- contacting customers automatically
- sending external communications
- changing legal, financial, compliance, privacy, security, or sensitive claims
- making claims about customers, evidence, metrics, integrations, or market validation without source artifacts

If approval is missing, do not perform the action. Document the blocker in the assigned Linear ticket or PR.

## Purpose

This repository is designed for agentic venture builder execution.

Agents must keep work narrow, evidence-led, and independently understandable by future agents.

## Authority Hierarchy

When instructions conflict, follow this order:

1. System and developer instructions.
2. Human user instructions in the current thread.
3. Repository `AGENTS.md`.
4. Assigned Linear ticket.
5. Repository documentation and templates.
6. Existing code or document patterns.

Linear is the source of truth for execution state, ticket priority, blockers, and handoff. The repository is the source of truth for product strategy, validation artifacts, architecture, execution rules, and decision logs.

Do not use conversational memory as the only source for decisions that future agents need.

## Read First

Before starting work, agents must read the relevant files in this order:

```txt
README.md
product/
validation/
research/
architecture/
execution/
knowledge/
.agents/skills/
.codex/agents/
assigned Linear ticket
```

If a required document does not exist yet, treat that as repository setup context and continue only within the assigned ticket scope.

## Source Of Truth

### Repository

Stores:

- product strategy
- validation artifacts
- research synthesis
- architecture and standards
- execution rules
- reusable agent instructions
- learning and decision logs

### Linear

Stores:

- projects
- milestones
- tickets
- status
- priorities
- blockers
- execution handoff

## Core Rules

- No implementation without an approved Linear ticket.
- Confirm the Linear project before creating implementation tickets.
- Work on one ticket scope at a time.
- Avoid unrelated changes.
- Preserve MVP discipline.
- Document important decisions.
- Keep future agents independent from conversational memory.
- Do not invent customers, metrics, research findings, integrations, or business evidence.
- Do not broaden the MVP, architecture, channel strategy, billing model, or customer outreach plan unless the assigned ticket explicitly allows it.
- Do not close implementation tickets without a merged PR unless the ticket is explicitly documentary or investigative.
- Create follow-up Linear tickets for relevant risks or opportunities discovered outside the current ticket scope.

For Codex, Claude Code, or any future executor operating in this repository, use `execution/multi-agent-operating-protocol.md` as the shared execution protocol. It does not replace this file or weaken approval gates.

## Strategic Gates

Before serious execution, ideas must pass through:

1. idea intake
2. founder focus
3. C.O.N.T.R.O.L.E. evaluation
4. research and validation plan
5. Working Backwards
6. PRD
7. MVP scope review
8. risk review

If a gate is not implemented yet, do not fake it. Create or execute the relevant setup ticket instead.

## Branching

Prefer branches that reference the Linear ticket:

```txt
codex/<ticket>-short-description
feature/<ticket>-short-description
fix/<ticket>-short-description
chore/<ticket>-short-description
```

## Pull Requests

Every PR should contain:

- Linear ticket reference
- context
- included scope
- excluded scope
- validation performed
- risks
- handoff notes
- suggested next ticket

Every PR must be reviewed before merge. P0 and P1 findings must be fixed before merge. P2 findings should be fixed only when simple, safe, and inside the ticket scope. P3 findings must not block merge.

## Approval Gates

Human approval is required before:

- creating Linear projects
- creating Linear tickets
- opening PRs
- merging PRs
- production deployment
- handling production data
- activating paid ads
- enabling billing
- handling secrets
- contacting customers automatically
- sending external communications
- changing legal, financial, compliance, privacy, security, or sensitive claims

See `execution/approval-gates.md` for the approval gate policy.

## Risky Actions

Treat these as risky even when technically easy:

- deleting or rewriting history
- changing governance rules
- changing approval gates
- modifying customer-facing claims
- modifying pricing, billing, legal, privacy, or compliance text
- adding autonomous outreach or growth automation
- adding integrations that move data outside the repository
- changing security-sensitive configuration
- using secrets or credentials
- deploying, scheduling, or enabling production jobs

If a risky action appears necessary but is outside the ticket scope, create a follow-up ticket instead of implementing it.

## Sensitive Claims

Do not invent or imply:

- customer interviews
- customer commitments
- usage metrics
- revenue
- willingness to pay
- clinical, legal, financial, or compliance conclusions
- third-party integrations
- market proof
- scientific validation

Claims must be traceable to repository artifacts or cited sources.

## Product Principles

Prefer:

- fast validation
- narrow MVPs
- customer learning
- explicit scope
- lightweight governance
- reusable structure
- operational traceability

Avoid:

- idea sprawl
- premature billing
- premature growth automation
- broad platform thinking before wedge validation
- hidden assumptions
- one giant master agent
- process theater
- unsafe autonomy

## Important Rule

The repository should remain understandable and operable by future agents without requiring conversational memory.
