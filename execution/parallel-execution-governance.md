# Parallel Execution Governance

This protocol defines how Codex, Claude Code, and future executors may work in parallel without creating file, branch, domain, or decision conflicts.

Use it with `AGENTS.md`, `execution/multi-agent-operating-protocol.md`, `execution/context-routing-protocol.md`, `execution/ticket-pr-handoff-system.md`, `execution/linear-governance-model.md`, and the assigned Linear tickets.

It does not authorize automated orchestration, Linear label creation, approval-gate changes, broad refactors, or conflict resolution by overwriting user or other-agent work.

## Core Decision

Parallel execution is allowed only when ownership, write set, dependencies, approval state, validation, and merge order are explicit.

If any of those are unclear, serialize the work.

## Unit Of Parallelization

The unit of parallel work is one approved Linear ticket.

Each parallel ticket must have:

- one primary executor
- one branch
- one PR
- one declared expected write set
- one clear source of truth for dependencies and blockers
- one final handoff

Do not split a single ticket across multiple agents unless the split is explicit in Linear and each agent has a disjoint write set.

## Parallelization Classes

| Class | Meaning | Required handling |
|---|---|---|
| `parallelizable:yes` | Safe to execute alongside other active tickets. | Write set is disjoint, dependencies are clear, risk is low/medium, and validation is independent. |
| `parallelizable:partial` | Can run in parallel only with sequencing or ownership constraints. | Declare files, domains, merge order, and blocker conditions before work starts. |
| `parallelizable:no` | Must be serialized. | Use one executor and merge before dependent or overlapping work starts. |

If the ticket does not declare a class, treat it as `parallelizable:no` when it touches shared governance, templates, architecture decisions, or high-risk files.

## Ownership Rules

Every active ticket must declare:

- primary executor tool or human owner
- accountable agent role
- expected write set
- restricted files
- related domain
- dependencies
- review expectation
- handoff destination

Ownership is not permission to edit nearby files. It only covers the included scope and expected write set.

If another file becomes necessary, update the PR and Linear handoff. If the file is outside scope or shared high-risk, stop and propose a follow-up or serialize the change.

## Expected Write Set Rules

The expected write set should name files or bounded directories likely to change.

Good examples:

```txt
CLAUDE.md
execution/context-routing-protocol.md
validation/customer-interview-template.md
product/mvp-scope.md
```

Weak examples:

```txt
execution/
all docs
agent files
repo cleanup
```

Broad write sets require serialization unless the ticket explicitly decomposes ownership by file.

## Shared High-Risk Files

Changes to these files or artifact families should be serialized by default:

- `AGENTS.md`
- `CLAUDE.md`
- `execution/approval-gates.md`
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/multi-agent-operating-protocol.md`
- `execution/context-routing-protocol.md`
- `execution/parallel-execution-governance.md`
- global Linear ticket templates
- shared agent contracts in `.codex/agents/`
- shared skill contracts in `.agents/skills/`
- architecture decision records
- top-level `README.md`

A PR touching any of these should explain why the change belongs in the current ticket and what other active tickets may be affected.

## When Parallel Execution Is Allowed

A ticket may run in parallel when all are true:

- dependency state is clear in Linear
- approval state is clear
- expected write set is disjoint from other active tickets
- domain ownership is distinct
- validation can run independently
- no shared high-risk file is edited
- no global template or approval rule changes
- merge order does not matter or is explicitly declared
- the ticket is low or medium risk

## When Parallel Execution Is Not Allowed

Do not parallelize when the ticket:

- changes approval gates
- changes `AGENTS.md`, `CLAUDE.md`, or shared execution protocols
- changes global Linear templates or lifecycle rules
- performs broad refactors
- changes shared agent or skill contracts
- changes architecture decisions that other tickets depend on
- handles secrets, credentials, production data, customer data, billing, paid acquisition, external communication, or sensitive claims
- requires the same files as another active ticket
- has unresolved P0/P1 risk or unclear validation

High-risk tasks cannot be parallelized without explicit approval and review requirements recorded in Linear.

## Partial Parallelization

Use partial parallelization only when parallel work has a clear handoff boundary.

Examples:

- two tickets update different domain templates after a shared protocol has merged
- one ticket drafts a new document while another updates unrelated docs
- one ticket prepares a follow-up proposal while another completes implementation

Partial parallelization must state:

- what can start now
- what must wait for merge
- which files are reserved
- which ticket owns the shared decision
- what happens if both tickets need the same file

## Merge Order Rules

Merge order must follow dependency order.

Use this default order:

1. approval gates and repository policy
2. shared execution protocols
3. context routing and parallelization rules
4. Linear templates and readiness validators
5. agent or skill adapters
6. domain documents
7. implementation code
8. observability and metrics updates

When a lower-order PR needs a higher-order file, stop and re-evaluate scope before merging.

## Branch Sync Rules

Before opening a PR:

- branch from current `main`
- check active PRs for overlapping files when feasible
- keep commits scoped to the ticket

Before resolving review or merge conflicts:

- sync with `main`
- preserve user and other-agent work
- resolve only within the ticket scope
- document any conflict and resolution in the PR and Linear handoff

Never use destructive Git commands to erase work unless the user explicitly requested that exact operation.

## Conflict Types

| Conflict type | Signal | Response |
|---|---|---|
| File conflict | two branches edit the same file | serialize, choose one owner, or split by explicit section ownership |
| Domain conflict | tickets make competing decisions in the same product/governance area | stop and record blocker until the decision owner resolves it |
| Dependency conflict | a ticket starts before a blocking artifact is merged | pause the dependent ticket or convert work to draft-only |
| Validation conflict | one PR invalidates another PR's validation | re-run validation and update handoff before merge |
| Approval conflict | one ticket relies on approval not recorded for another | stop until approval source is explicit |

## Refactor Rules

Broad refactors need their own approved ticket.

Do not include refactors as cleanup inside documentation, governance, prompt, skill, or feature tickets unless the refactor is required to complete the ticket safely.

If a refactor is discovered during review:

- classify the risk
- fix only P0/P1 issues required for this PR
- create or propose a follow-up for larger cleanup
- record the decision in PR and Linear handoff

## Linear Coordination Rules

Use Linear as the source of truth for:

- ownership
- dependencies
- blockers
- parallelization class
- active branch
- PR link
- review status
- residual risk
- follow-ups

Do not coordinate parallel work only through chat memory.

When a ticket becomes blocked by another branch or decision, comment in Linear with:

- blocker type
- blocking ticket or PR
- affected files or domain
- unblock condition
- next recommended action

## PR Handoff Requirements

Every PR in a parallel execution cycle should include:

- expected write set
- actual files changed
- whether the ticket was `yes`, `partial`, or `no` for parallelization
- active conflicts encountered
- conflict resolution, if any
- dependency or merge-order notes
- follow-ups created or not needed

If the actual changed files differ materially from the expected write set, explain why.

## Monitoring Signals

Track these signals in PR and Linear handoffs:

- merge conflicts
- PRs touching undeclared files
- tickets blocked by ownership ambiguity
- repeated edits to shared high-risk files
- P0/P1 review findings caused by stale context
- rework after merge due to dependency order

These signals should feed future ticket template and readiness-validator improvements.

## Done Criteria

Parallel execution governance is working when:

- active tickets declare ownership and expected write set
- shared high-risk files are serialized by default
- PRs explain deviations from expected write set
- conflicts are recorded instead of hidden
- Codex and Claude Code can work in parallel only where dependencies and files are clear
- future orchestration work has concrete ownership and conflict signals to inspect
