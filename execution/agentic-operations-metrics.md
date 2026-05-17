# Agentic Operations Metrics

This document defines lightweight operational metrics for Codex, Claude Code, and future multi-agent execution.

The goal is decision usefulness, not dashboard theater. Metrics should reveal whether parallel agent execution improves throughput and quality or creates hidden rework, conflicts, review burden, and weak handoffs.

## Operating Decision

Record metrics manually at first in PR descriptions and final Linear handoff comments.

Use repository knowledge files only when a metric produces durable learning, a changed operating decision, or a recurring pattern that future agents need. Do not create dashboards, external analytics, automation jobs, or telemetry from this document alone.

## Source Fields

Use existing handoff fields from `execution/ticket-pr-handoff-system.md`:

- executor tool
- branch
- PR
- merge status
- expected write set
- actual files changed
- restricted files touched
- parallelization class
- conflict or merge-order notes
- validation results
- review source
- P0 / P1 / P2 / P3 counts
- monitoring
- metrics
- follow-ups
- residual risks
- next recommended action

Use readiness fields from `execution/agent-readiness-validator.md` when available:

- READY
- READY WITH APPROVAL
- NOT READY
- BLOCKED
- reasons
- required fix, approval, or unblock condition

## Metric Table

| Metric | Meaning | Source | Cadence | Alert Signal | Decision It Supports |
|---|---|---|---|---|---|
| Ticket throughput | Count of tickets completed with merged PRs in a period. | Linear Done status and merged PRs. | Weekly or per execution batch. | Throughput rises while review findings, rework, or conflicts also rise. | Whether parallel execution is improving real delivery. |
| Cycle time | Time from In Progress to Done. | Linear timestamps and PR merge time. | Weekly or per execution batch. | Cycle time grows after adding parallel agents. | Whether tickets are sized and sequenced well. |
| Review time | Time from PR open to review completion or fallback review. | PR comments and Linear handoff. | Per PR, summarized weekly. | Review time becomes the dominant delay. | Whether review process, PR size, or reviewer availability needs adjustment. |
| P0/P1 findings | Count of blocking review findings. | PR review or structured manual fallback. | Per PR, summarized weekly. | Any P0, repeated P1, or P1 caused by stale context. | Whether readiness, validation, or context routing needs tightening. |
| P2 findings | Count of important non-blocking improvements. | PR review or structured manual fallback. | Per PR, summarized weekly. | Same P2 theme repeats across tickets. | Whether to create focused follow-ups or improve templates. |
| Readiness failures | Count of NOT READY or BLOCKED classifications and reasons. | Readiness validator comments or handoffs. | Weekly or before batch planning. | Same missing field or dependency appears repeatedly. | Whether Linear template, matrix, or ticket creation needs improvement. |
| READY WITH APPROVAL count | Count of tickets ready except for a named approval. | Readiness validator and Linear comments. | Weekly or per batch. | Tickets sit waiting for recurring approval type. | Whether approval timing or ticket sequencing needs adjustment. |
| Merge conflicts | Count and severity of file or domain conflicts. | PR handoff conflict notes. | Per PR, summarized weekly. | Conflicts touch shared high-risk files or repeat across agents. | Whether parallelization rules or ownership need tightening. |
| Write-set drift | Difference between expected write set and actual files changed. | PR description and Linear handoff. | Per PR. | Frequent undeclared files or broad actual write sets. | Whether ticket scope and readiness are precise enough. |
| Rework after merge | Follow-up fixes caused by incomplete context, missed validation, or review gaps. | Follow-up tickets and PR links. | Weekly or per batch. | Rework repeatedly follows the same ticket type or agent. | Whether validation plans or handoffs need improvement. |
| Handoff quality | Whether final handoff lets another agent resume without chat memory. | Linear final handoff. | Per ticket, sampled weekly. | Future agent asks for context already expected in handoff. | Whether handoff template is being used well. |
| Validation coverage | Whether planned checks were executed or explicitly unavailable. | PR validation section and final handoff. | Per PR. | Unavailable checks appear without rationale, or critical flows lack validation. | Whether tooling or test coverage needs a follow-up. |
| Follow-up quality | Whether follow-ups are specific, sourced, and acceptance-driven. | Linear follow-up tickets and PR handoff. | Weekly or per batch. | Follow-ups become vague or too numerous. | Whether review findings are being converted into useful backlog. |
| Residual risk clarity | Whether residual risk is explicit and non-blocking. | Final Linear handoff. | Per ticket. | Residual risks are vague, repeated, or later become rework. | Whether risk review or readiness needs improvement. |
| Agent mix | Which executor completed the ticket: Codex, Claude Code, human, or future orchestrator. | Executor tool handoff field. | Weekly or per batch. | One tool repeatedly gets blocked, creates rework, or lacks context. | Whether task routing between Codex and Claude Code should change. |

## Quality Buckets

Group metrics into four buckets when summarizing a batch.

### Throughput

- ticket throughput
- cycle time
- review time
- agent mix

Use these only with quality metrics. Faster delivery is not improvement if P0/P1 findings, rework, or conflicts rise.

### Execution Quality

- P0/P1 findings
- P2 findings
- validation coverage
- residual risk clarity
- rework after merge

Use these to decide whether readiness, tests, review, or scope discipline needs tightening.

### Parallelization Health

- merge conflicts
- write-set drift
- parallelization class accuracy
- conflict or merge-order notes

Use these to decide whether tickets can safely run in parallel or should be serialized.

### Readiness And Handoff

- readiness failures
- READY WITH APPROVAL count
- handoff quality
- follow-up quality

Use these to improve Linear ticket creation, field matrix usage, and final handoffs.

## Manual Collection Protocol

For every merged PR, capture metrics in the final Linear handoff:

```md
## Metrics
- Ticket throughput: counted in current batch
- Cycle time:
- Review time:
- P0/P1 findings:
- Readiness result:
- Write-set drift:
- Merge conflicts:
- Rework/follow-up created:
- Handoff quality:
- Residual risk clarity:
- Agent mix:
```

If a value is not available, write `not measured` and explain why only when the gap affects a decision.

## Review Cadence

Use a lightweight cadence:

- Per PR: record metrics in the final Linear handoff.
- Weekly or after 5 merged agentic tickets: summarize patterns if they affect execution decisions.
- Before Claude Code pilot review: compare Codex-only baseline with mixed Codex + Claude Code execution.
- Before orchestration analysis: review whether metrics show enough stable handoff, readiness, and conflict data to justify evaluating Hermes, OpenClaw, or another orchestrator.

Do not create a repository knowledge update for every PR. Create one only when a batch summary changes future execution.

## Alert Signals

Treat these as operational alerts:

- any P0 finding
- repeated P1 findings in the same ticket type
- repeated NOT READY reasons caused by missing template fields
- repeated BLOCKED tickets caused by unclear dependencies or approvals
- repeated write-set drift into shared high-risk files
- merge conflicts between parallel agents
- review time consistently longer than implementation time
- follow-ups repeatedly created for the same missing validation
- handoffs that do not let another agent resume without chat memory
- residual risks that later become rework

Alert signals should create a focused follow-up ticket only when the problem is specific, recurring, and actionable.

## Baseline For Future Orchestration

Before analyzing Hermes, OpenClaw, or another orchestrator, collect enough manual evidence to answer:

- Are tickets consistently READY before branch work?
- Are expected write sets accurate?
- Are dependencies and approvals explicit enough for dispatch?
- Are handoffs sufficient for another agent to resume?
- Are validation results recorded consistently?
- Are merge conflicts rare and explainable?
- Are follow-ups specific and traceable?

If the answer is no, improve the baseline before adding an orchestrator.

## Out Of Scope

- dashboards
- external analytics
- telemetry implementation
- automation jobs
- secrets or production data access
- customer data analysis
- individual agent performance scoring for compensation or sensitive people decisions

## Maintenance

Simplify these metrics if they are not used in decisions.

Add a metric only when it changes ticket sequencing, readiness, validation, review, parallelization, handoff, or future orchestration decisions.
