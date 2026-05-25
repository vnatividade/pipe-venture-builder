# Worktree Isolation Protocol

This protocol defines how Codex, Claude Code, and future executors should use Git worktrees when multiple agents may operate in this repository at the same time.

Use it with `AGENTS.md`, `execution/multi-agent-operating-protocol.md`, `execution/parallel-execution-governance.md`, `execution/context-routing-protocol.md`, and the assigned Linear ticket.

It does not authorize parallel execution by itself. Linear remains the source of truth for ticket state, ownership, dependencies, blockers, and merge order.

## Core Decision

Use a separate worktree for each active executor when two or more agents may edit the repository during the same execution window.

A worktree isolates filesystem state. It does not replace:

- one Linear ticket per work item
- one branch per ticket
- one PR per ticket
- explicit ownership
- review before merge
- approval gates

If ownership, write set, dependency, or approval state is unclear, serialize the work before creating or using parallel worktrees.

## When Worktrees Are Required

Use a dedicated worktree when any of these are true:

- Codex and Claude Code are active at the same time.
- A human or another agent has uncommitted local changes in the main checkout.
- The ticket may take longer than one short execution session.
- The executor needs to run validations that create local artifacts.
- The ticket depends on another active branch but can safely draft non-overlapping work.
- The repository is being used for review/merge work while another ticket is being implemented.

Use the main checkout only for short, serialized work when no other agent or human has active local edits.

## When Worktrees Are Not Enough

Do not use worktrees as a workaround for unsafe parallelism.

Serialize the ticket when it changes:

- `AGENTS.md`
- `CLAUDE.md`
- `execution/approval-gates.md`
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/multi-agent-operating-protocol.md`
- `execution/context-routing-protocol.md`
- `execution/parallel-execution-governance.md`
- global ticket templates
- shared agent contracts
- shared skill contracts
- architecture decision records
- top-level `README.md`

If one of these files must change, assign one owner, one branch, and one PR. Other agents may review or prepare notes, but they should not edit competing branches against the same file.

## Naming Convention

Worktree directory names should make ownership and ticket scope obvious.

Recommended pattern:

```txt
../pipe-vb-worktrees/<executor>/<ticket>-<short-description>
```

Examples:

```txt
../pipe-vb-worktrees/codex/pip-146-worktree-isolation-protocol
../pipe-vb-worktrees/claude/pip-147-executor-capability-matrix
```

Branch names still follow the repository branch convention:

```txt
codex/<ticket>-short-description
claude/<ticket>-short-description
feature/<ticket>-short-description
fix/<ticket>-short-description
chore/<ticket>-short-description
```

Do not use the worktree path as the branch name. Do not reuse a worktree for a different Linear ticket after merge.

## Worktree Lifecycle

### Before Creating A Worktree

Confirm:

- the Linear ticket is selected and ready for execution
- dependencies are clear
- owner/executor is explicit
- expected write set is declared or can be inferred narrowly
- parallelization class is `parallelizable:yes` or `parallelizable:partial`
- no active ticket owns the same files
- approval state is clear for any gated action

If the ticket is `parallelizable:no`, do not create a parallel worktree unless the worktree is only used to inspect or review without editing.

### Creating A Worktree

Create the worktree from current `main` unless the ticket explicitly depends on another branch.

Record in Linear:

- worktree owner
- branch name
- expected write set
- dependency or merge-order note
- known blockers

### During Work

Each worktree must keep changes scoped to the assigned ticket.

Do not:

- edit another ticket's reserved files
- stage generated files unrelated to the ticket
- resolve conflicts by overwriting another agent's work
- run broad formatting across shared directories
- use the worktree to bypass approval or review gates

If the ticket needs an undeclared shared file, stop and update the PR or Linear handoff before editing. If the file is high-risk, serialize the work or create a follow-up.

### Before Opening A PR

Before opening a PR from a worktree:

- sync the branch against current `main` when feasible
- check active PRs for overlapping files
- run relevant validations
- confirm actual changed files match the expected write set
- document any difference between expected and actual files

### After Merge

After the PR is merged:

- update Linear with PR, merge commit, validations, review result, follow-ups, and residual risk
- remove or archive the local worktree only after any needed local artifacts are no longer required
- do not reuse the branch or worktree path for a new ticket

## Branch Sync Rules

Default rule:

1. Fetch latest `main`.
2. Create or update the worktree branch from current `main`.
3. Keep the branch narrow.
4. Revalidate after syncing or resolving conflicts.
5. Record any conflict resolution in the PR and Linear handoff.

If another PR merges first and changes a file in the current worktree's write set:

- pause broad edits
- inspect the merged change
- decide whether the current ticket still owns the file
- re-run validations after rebasing, merging, or manually applying the required update
- document the conflict and resolution

Never delete, reset, or overwrite another executor's worktree to resolve a conflict unless the user explicitly requested that exact operation.

## Cleanup And Stale Worktrees

A worktree is stale when:

- its Linear ticket is Done, Canceled, or superseded
- its branch was merged or closed
- it has not been updated and no owner is active
- its base branch is far behind and the work is no longer safe to continue

Before cleanup:

- confirm no uncommitted ticket-relevant work remains
- confirm the branch state in GitHub
- confirm Linear has final handoff or blocker notes
- preserve any needed artifact by committing it, moving it into the correct ticket branch, or recording a follow-up

Do not clean up worktrees that contain unexplained uncommitted changes from another human or agent. Record the stale state in Linear or ask the owner to resolve it.

## Conflict Rules

Use `execution/parallel-execution-governance.md` for the full conflict model.

Worktree-specific handling:

- File conflict: serialize and assign one file owner.
- Domain conflict: stop until the decision owner resolves the conflict.
- Dependency conflict: pause the dependent worktree or keep it draft-only.
- Validation conflict: re-run validation after syncing with merged changes.
- Approval conflict: stop until approval source is explicit.

If a conflict requires out-of-scope work, create or propose a follow-up ticket instead of expanding the current PR.

## Future Orchestrator Expectations

A future orchestrator may create, assign, inspect, or retire worktrees only after the repository has:

- stable Codex and Claude Code execution patterns
- reliable Linear ownership and dependency fields
- consistent PR handoffs
- conflict and stale-worktree metrics
- explicit approval boundaries for automated actions

Until then, humans or explicitly assigned agents own worktree decisions.

## Manual Dry Run

### Scenario A - Safe Parallel Pair

Ticket A:

- Owner: Codex
- Branch: `codex/pip-146-worktree-isolation-protocol`
- Write set: `execution/worktree-isolation-protocol.md`, `execution/README.md`

Ticket B:

- Owner: Claude Code
- Branch: `claude/pip-147-executor-capability-matrix`
- Write set: `execution/executor-capability-matrix.md`, `execution/README.md`

Result:

- Partial parallelization only.
- The primary documents are disjoint, but both touch `execution/README.md`.
- Merge order must be declared.
- The second PR must sync after the first merge and adjust the README link if needed.

### Scenario B - Unsafe Parallel Pair

Ticket A:

- Owner: Codex
- Write set: `execution/approval-gates.md`

Ticket B:

- Owner: Claude Code
- Write set: `AGENTS.md`, `execution/multi-agent-operating-protocol.md`

Result:

- Do not parallelize.
- These are shared high-risk policy files.
- Assign one owner and serialize by merge order.
- Other agents may review, but should not edit competing branches.

## PR And Linear Handoff Requirements

When a ticket uses a worktree, the PR and Linear handoff should include:

- worktree path or owner label, when relevant
- branch name
- expected write set
- actual changed files
- parallelization class
- active conflicts, if any
- cleanup status
- stale-worktree risk, if any
- merge-order notes
- residual risk

If no worktree was used, note why serialized execution was safe.

## Done Criteria

This protocol is working when:

- Codex and Claude Code can work without sharing the same dirty checkout
- each active branch maps to one Linear ticket
- high-risk shared files remain serialized by default
- stale worktrees are detectable and safely retired
- PRs document write set, conflicts, and merge order
- future orchestrator work can rely on explicit ownership rather than chat memory
