# Context Routing Protocol

This protocol defines how Codex, Claude Code, and future executors should choose the smallest useful repository context for a Linear ticket.

Use it with `AGENTS.md`, `execution/multi-agent-operating-protocol.md`, `.codex/agents/agent-skill-trigger-rules.md`, `.agents/skills/core-skill-contracts.md`, and the assigned Linear ticket.

It is a routing table, not a repository inventory. Do not load every folder, agent, skill, template, or historical artifact by default.

## Purpose

Agents should start from the ticket type, expected write set, and approval state, then load only the documents needed to execute safely.

Good context routing should reduce:

- decisions based on chat memory
- broad reading before narrow work
- duplicate agent-specific prompts
- out-of-scope edits caused by irrelevant context
- conflicting interpretations between Codex and Claude Code

## Default Routing Rules

For every ticket:

1. Read `AGENTS.md`.
2. Read the assigned Linear ticket.
3. Read `execution/multi-agent-operating-protocol.md`.
4. Read the relevant row in this protocol.
5. Read only the listed read-first files and the files in the expected write set.
6. Add agent contracts or skills only when the ticket type needs them.
7. Stop when a required source artifact is missing or approval state is unclear.

When a ticket has multiple types, use the highest-risk or most execution-specific type first.

Priority order for mixed tickets:

```txt
code / infrastructure / automation
observability
governance / workflow
architecture
product
validation / research
prompt / skill
documentation
orchestration-prep
```

## Stop Conditions

Stop and document a blocker in Linear or the PR when:

- the assigned ticket is missing or not approved for execution
- the ticket type is unclear and affects required context
- required source artifacts do not exist
- approval is missing for a gated action
- the expected write set is not declared for a shared or high-risk file
- the task requires secrets, production data, customer data, billing, paid acquisition, external communication, or sensitive claims
- the work would require loading unrelated repositories or importing broad reference libraries
- the next needed change is outside the current ticket scope

Do not fill missing evidence, metrics, customers, integrations, or validation claims from memory.

## Agent Contracts Vs Skills Vs Workflow Docs

Use workflow docs when the ticket needs repository operating rules.

Use agent contracts when the ticket needs role-specific judgment such as product strategy, validation, architecture, risk, ticket orchestration, or knowledge curation.

Use skills when the ticket needs a reusable workflow with a narrow trigger and expected output.

Do not load a skill only because it is nearby. The trigger in `.agents/skills/core-skill-contracts.md` must match the ticket.

Do not load more than one primary agent contract by default. Add a supporting risk reviewer only when the ticket touches approval gates, P0/P1 risk, security, privacy, billing, production, customer data, external communication, or sensitive claims.

## Ticket Type Routing Map

| Ticket type | Read first after defaults | Agent contract or skill trigger | Stop or escalate when |
|---|---|---|---|
| `architecture` | `architecture/`, `execution/core-pipeline-map.md`, `execution/risk-reviewer-matrix-lite.md` | Architecture agent; risk reviewer if production, data, security, integration, or approval risk appears | source architecture is missing, risk is unreviewed, or the ticket implies implementation without a build ticket |
| `documentation` | target document, nearest folder `README.md`, `execution/ticket-pr-handoff-system.md` | No skill by default; execution handoff skill near PR/Done | documentation would create unsupported claims, change policy, or broaden scope |
| `prompt` | target prompt or agent doc, `.codex/agents/agent-skill-trigger-rules.md`, `.agents/skills/core-skill-contracts.md` | Prompt-specific owner if named; risk reviewer if the prompt can authorize gated work | prompt duplicates `AGENTS.md`, changes approval gates, or creates unsupported autonomy |
| `skill` | `.agents/skills/core-skill-contracts.md`, `.agents/skills/README.md`, related workflow doc | Skill contract workflow; primary agent for the supported workflow | skill trigger is broad, overlaps another skill, or lacks stop conditions |
| `workflow` | `execution/`, `execution/ticket-pr-handoff-system.md`, `execution/linear-governance-model.md` | Ticket orchestrator; Linear governance or execution handoff skill when status/PR handoff is involved | workflow creates a second policy system or weakens approval gates |
| `governance` | `AGENTS.md`, `execution/approval-gates.md`, `execution/linear-governance-model.md`, `execution/multi-agent-operating-protocol.md` | Risk reviewer and ticket orchestrator | governance touches approval gates, Linear project structure, labels, or shared templates without explicit scope |
| `code` | expected write set, local package docs, tests near changed files, relevant architecture note | Software architecture role if design is unclear; risk reviewer for security/data/production | tests are unavailable for critical behavior, write set is ambiguous, or code needs secrets/production data |
| `infrastructure` | expected infrastructure files, `execution/approval-gates.md`, relevant architecture/security docs | Architecture agent plus risk reviewer | change could deploy, expose secrets, alter environments, enable billing, or affect production |
| `automation` | target automation files, `execution/approval-gates.md`, `execution/ticket-pr-handoff-system.md` | Risk reviewer if automation can act externally or mutate state | automation contacts users, changes Linear/GitHub state, deploys, schedules jobs, or handles data without approval |
| `observability` | target service/workflow docs, existing logs/metrics docs, `execution/ticket-pr-handoff-system.md` | Execution handoff skill; architecture role if technical signals are unclear | metrics imply unsupported customer/product claims or require production data |
| `product` | `product/`, `validation/`, `execution/core-pipeline-map.md`, related PRD/MVP artifacts | Product strategist; validation planning skill when assumptions need evidence | product claim lacks source artifacts, MVP scope broadens, or implementation is requested before gates |
| `validation` | `validation/`, `research/`, `execution/core-pipeline-map.md` | Validation planning or research synthesis skill | outreach, identifiable data handling, or claims require approval or evidence is missing |
| `research` | `research/`, validation artifact that asks the question, source plan when present | Research synthesis skill | source quality is insufficient, citations are missing, or conclusions would become sensitive claims |
| `orchestration-prep` | `architecture/agentic-multi-agent-codex-claude-plan.md`, `execution/multi-agent-operating-protocol.md`, completed multi-agent tickets and handoffs | Roadmap/ticket orchestrator only; no executor dispatch | baseline Codex + Claude Code has not run, metrics are missing, or the work starts implementing an orchestrator |

## Context Load Limits

Use these limits unless the ticket explicitly requires more:

| Task shape | Default limit |
|---|---|
| Narrow documentation update | assigned ticket, target file, nearest `README.md`, relevant execution protocol |
| Governance or workflow update | assigned ticket, `AGENTS.md`, relevant `execution/` files, one agent contract if needed |
| Product or validation update | assigned ticket, relevant `product/` or `validation/` artifacts, core pipeline map |
| Technical implementation | assigned ticket, expected write set, local tests, relevant architecture note |
| Broad planning request | assigned ticket or source artifact, architecture plan, roadmap/ticket orchestrator workflow |

If more context seems necessary, name why in the PR or Linear handoff.

## Missing Context Handling

When a source artifact is missing:

1. Do not invent the missing context.
2. Check whether the ticket explicitly says the artifact may not exist yet.
3. If the artifact is required for safe execution, stop and record a blocker.
4. If the artifact is useful but not required, proceed narrowly and record a follow-up candidate.

Create or propose a follow-up only when the gap has clear impact, scope, and acceptance criteria.

## Handoff Expectations

Final handoff should state:

- ticket type used for routing
- files read as source context
- agent contracts or skills loaded, if any
- required context that was missing, if any
- whether additional context was intentionally not loaded
- follow-ups created or not needed

This lets future Codex, Claude Code, or orchestrator work understand why a specific context path was used.

## Maintenance Rule

Keep this document concise. Add a new routing row only when an approved ticket introduces a recurring ticket type or a repeated context failure.
