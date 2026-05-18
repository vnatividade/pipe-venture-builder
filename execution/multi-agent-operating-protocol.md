# Multi-Agent Operating Protocol

This protocol defines the common operating layer for Codex, Claude Code, and any future agent executor working in this repository.

Use it with `AGENTS.md`, `execution/approval-gates.md`, `execution/linear-governance-model.md`, `execution/ticket-pr-handoff-system.md`, `.codex/agents/README.md`, and the assigned Linear ticket.

## Purpose

Codex and Claude Code must operate from the same repository rules instead of maintaining separate execution policies.

This protocol is a shared operating contract. It does not replace `AGENTS.md`, weaken approval gates, create Linear tickets, open PRs, merge PRs, deploy, contact users, handle secrets, or authorize external actions.

When this protocol conflicts with `AGENTS.md`, `execution/approval-gates.md`, or the assigned Linear ticket, follow the stricter rule.

## Source Of Truth

| Area | Source of truth | Notes |
|---|---|---|
| Repository policy | `AGENTS.md` | Highest repository-level authority for agents. |
| Execution state | Linear | Status, priority, blockers, dependencies, handoff, and follow-ups. |
| Operational work | Git and GitHub | Branch, commit, PR, review, checks, merge state, and diff history. |
| Product and strategy context | Repository artifacts | Product, validation, research, architecture, growth, knowledge, and execution docs. |
| Approvals | Current thread, Linear ticket, PR, or repository artifact | Approval must be explicit and scoped. |
| Durable decisions | `knowledge/` or `architecture/adr/` | Use when future agents need the decision without chat memory. |

Do not use conversational memory as the only source for a decision future agents need.

## Shared Rules For Codex And Claude Code

- Work from one approved Linear ticket at a time.
- Keep one branch and one PR per ticket unless a split is explicitly approved.
- Implement only the included scope.
- Preserve excluded scope.
- Read the assigned ticket before editing.
- Read only the smallest useful repository context for the ticket type.
- Prefer repository protocols and local patterns over tool-specific habits.
- Do not create a second policy system for a specific tool.
- Do not invent customers, metrics, evidence, integrations, revenue, validation, or sensitive claims.
- Do not bypass human approval gates.
- Do not rely on chat memory for handoff.

## Execution Flow

Use this flow for both Codex and Claude Code:

1. Read the assigned Linear ticket.
2. Confirm dependencies, approval state, risk, and expected write set.
3. Read the relevant repository artifacts.
4. Move the ticket to `In Progress` only when it is actually selected for execution.
5. Create a branch that references the ticket.
6. Make scoped changes.
7. Run the strongest available validations for the ticket type.
8. Open a PR linked to the Linear ticket.
9. Request review.
10. Classify review findings as P0, P1, P2, or P3.
11. Fix P0 and P1 before merge.
12. Fix P2 only when simple, safe, and inside scope.
13. Do not block merge on P3.
14. Update PR and Linear handoff with validations, review result, follow-ups, and residual risk.
15. Merge only when the ticket, validation, review, and handoff are complete.
16. Move the Linear ticket to `Done` after merge and final handoff.

If any gate is missing or ambiguous, stop and document the blocker in Linear or the PR.

## Branch Ownership

Branch names should identify the executor or work type and the Linear ticket.

Recommended patterns:

```txt
codex/<ticket>-short-description
claude/<ticket>-short-description
feature/<ticket>-short-description
fix/<ticket>-short-description
chore/<ticket>-short-description
```

Use `codex/` for Codex-led work and `claude/` for Claude Code-led work unless the ticket asks otherwise.

Do not reuse a branch after its ticket is merged.

### Linear `gitBranchName` field is informational

Linear auto-generates a `gitBranchName` value on every issue, by default `<displayName>/<ticket>-<slug>` (for example `vnatiivis/pip-141-...`). This value is informational only and does not override the executor-prefixed conventions above. When creating a branch:

- Claude Code-led work uses `claude/<ticket>-short-description` (per `CLAUDE.md` "Operating Rules").
- Codex-led work uses `codex/<ticket>-short-description` (per `AGENTS.md` "Branching").
- Other work uses `feature/`, `fix/`, or `chore/` per the recommended patterns above.

The Linear-suggested name may be used as a slug source, but the executor prefix takes precedence. Do not push branches under the auto-generated `<displayName>/` prefix when an executor convention applies.

## Context Boundary

Agents should load the smallest useful context set.

Default context order:

1. `AGENTS.md`
2. assigned Linear ticket
3. `execution/context-routing-protocol.md`
4. relevant `execution/` protocol
5. relevant domain folder such as `product/`, `validation/`, `research/`, `architecture/`, `growth/`, or `knowledge/`
6. relevant `.agents/skills/` or `.codex/agents/` contract

Do not load all agents, all skills, or all templates by default.

If required source context is missing, do not fill the gap with assumptions. Record the blocker or create an approved follow-up.

## Approval Boundaries

Human approval remains required before:

- creating Linear projects
- creating Linear tickets
- opening PRs
- merging PRs
- deploying production
- enabling billing, pricing collection, paid ads, or paid acquisition
- handling secrets, credentials, tokens, private keys, customer data, or production data
- contacting customers automatically
- sending external communications
- changing legal, financial, compliance, privacy, security, or sensitive claims
- making claims about customers, evidence, metrics, integrations, or market validation without source artifacts

Approval must be explicit and scoped. Do not treat silence, prior memory, or model inference as approval.

## Parallel Execution Rules

Use `execution/parallel-execution-governance.md` for detailed ownership, write set, merge order, and conflict rules.

A ticket may be parallelized only when:

- dependencies are clear
- expected write set is disjoint from other active tickets
- ownership is explicit
- approval state is clear
- risk is low or medium and review requirements are clear
- the ticket does not change global governance, approval gates, or shared high-risk files

A ticket should not be parallelized when it changes:

- `AGENTS.md`
- `execution/approval-gates.md`
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/multi-agent-operating-protocol.md`
- future `CLAUDE.md`
- global ticket templates
- shared agent contracts

When a shared file must change, prefer serialized tickets or one owner with explicit review.

## Conflict Handling

When a conflict appears:

1. Stop broad edits.
2. Identify whether the conflict is file-level, domain-level, dependency-level, or decision-level.
3. Preserve user and other-agent work.
4. Update from the base branch before attempting resolution.
5. Resolve only within the assigned ticket scope.
6. If resolution requires out-of-scope changes, create or propose a follow-up.
7. Record the resolution in the PR and Linear handoff.

Never use destructive Git commands to erase work unless the user explicitly requested that exact operation.

## Handoff Requirements

Every completed ticket should leave enough context for a future agent to continue without reading chat history.

Final Linear handoff should include:

- Linear ticket
- executor tool
- branch
- PR
- merge status and commit
- summary of delivery
- included scope delivered
- excluded scope preserved
- files changed
- validation commands and results
- review source and severity counts
- monitoring or metrics, when applicable
- follow-ups created or not needed
- residual risks
- next recommended action

Do not include private customer data, secrets, credentials, or sensitive details in handoff.

## Tool-Specific Layers

### Codex

Codex-specific instructions may live in `.codex/`.

Codex-specific files may adapt execution to Codex capabilities, but they must not redefine approval gates, Linear governance, or branch/PR rules.

### Claude Code

Claude Code should use future `CLAUDE.md` as a short adapter into this shared protocol.

Claude-specific files should exist only when Claude Code needs a real tool-specific convention. They must not duplicate `AGENTS.md` or create a separate execution policy.

### Future Orchestrator

Future Hermes/OpenClaw or other orchestrator work is not authorized by this protocol.

An orchestrator readiness analysis should happen only after Codex and Claude Code have both executed real tickets with comparable handoff and metrics.

## Done Criteria

This protocol is usable when:

- Codex and Claude Code can follow the same ticket-first workflow
- Linear and Git source-of-truth roles are explicit
- approval gates are preserved
- branch, PR, review, and handoff expectations are clear
- context boundaries prevent loading every agent or skill
- parallel execution is bounded by ownership and write set
- future orchestration is deferred rather than implemented
