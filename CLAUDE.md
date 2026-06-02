# CLAUDE.md - Claude Code Adapter

This file is the Claude Code entrypoint for `pipe-venture-builder`.

It is an adapter, not a separate policy system. The canonical repository rules remain in `AGENTS.md`, `execution/approval-gates.md`, and the assigned Linear ticket.

## Read First

Before editing, read:

1. `AGENTS.md`
2. assigned Linear ticket
3. `execution/multi-agent-operating-protocol.md`
4. `execution/context-routing-protocol.md`
5. `execution/approval-gates.md`
6. `execution/ticket-pr-handoff-system.md`
7. only the smallest relevant domain files for the ticket scope

Do not load every agent, skill, template, or domain folder by default.

For vague founder-facing requests, raw ideas, validation questions, or "what should I do next?" interactions, also read:

- `execution/conversational-founder-guide.md`
- `.codex/agents/conversational-founder-guide-specialization.md`

Use those files to guide the user through the Pipe front door instead of asking the user to choose Markdown files, gates, skills, MCPs, or agents.

## Operating Rules

Claude Code must follow the shared multi-agent workflow:

- work from one approved Linear ticket at a time
- keep one branch and one pull request per ticket
- implement only the included scope
- preserve excluded scope
- use GitHub for branch, PR, review, checks, and merge state
- use Linear for status, blockers, dependencies, handoff, and follow-ups
- leave enough handoff context for another agent to continue without chat history

Use `claude/<ticket>-short-description` for Claude-led branches unless the ticket says otherwise.

## Approval Boundaries

This file does not authorize Claude Code to bypass approval gates.

Human approval remains required before:

- creating Linear projects or tickets
- opening or merging pull requests
- deploying production
- enabling billing, pricing collection, paid ads, or paid acquisition
- handling secrets, credentials, private keys, customer data, or production data
- contacting customers automatically or sending external communications
- changing legal, financial, compliance, privacy, security, or sensitive claims
- making claims about customers, evidence, metrics, integrations, or market validation without source artifacts

If approval is missing, stop and document the blocker in Linear or the PR.

## Conflict Avoidance

Before editing, confirm the expected write set from the ticket.

Do not parallelize work that changes shared governance files such as:

- `AGENTS.md`
- `CLAUDE.md`
- `execution/approval-gates.md`
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/multi-agent-operating-protocol.md`
- global ticket templates
- shared agent contracts

If a conflict appears, preserve user and other-agent work, sync from the base branch, resolve only inside the assigned ticket scope, and record the resolution in the PR and Linear handoff.

## Review And Handoff

Every PR must be reviewed before merge.

Classify findings using the repository severity model:

- P0 and P1 block merge and must be fixed
- P2 is fixed only when simple, safe, and inside scope
- P3 does not block merge

Final handoff must include the Linear ticket, branch, PR, merge status, validation results, review source, severity counts, files changed, follow-ups, residual risk, and next recommended action.

## What Not To Do

Do not use this file to:

- duplicate `AGENTS.md`
- weaken approval gates
- create a second Linear or Git workflow
- run a Claude Code pilot without a dedicated ticket
- implement future Hermes/OpenClaw orchestration
- invent customer, revenue, validation, integration, or metric evidence
