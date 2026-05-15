# Ticket, PR, And Handoff System

This system defines how an approved Linear ticket becomes a branch, pull request, review, merge, handoff, and knowledge update.

It complements `execution/linear-governance-model.md`. Linear tracks execution state; GitHub tracks branch review and merge; repository artifacts preserve durable strategy, decisions, and learning.

## Execution Rule

Execute one ticket scope at a time.

Each execution ticket should have:

- one Linear ticket
- one branch
- one pull request
- one review thread
- one merge or explicit non-merge handoff
- one final Linear update

Do not combine unrelated tickets into one PR. Do not split one ticket across multiple PRs unless the split is explicitly documented and approved.

## Ticket Readiness Checklist

Before starting branch work, confirm the ticket has:

- project context
- objective
- rationale
- included scope
- excluded scope
- deliverables
- acceptance criteria
- GO conditions
- NO-GO conditions
- dependencies
- owner or accountable agent role
- approval requirement
- risk level

If any required field is missing and the gap affects execution safety, stop and update the ticket or ask for clarification before implementation.

## Ticket Template

Use this template for implementation, documentation, governance, validation, or architecture tickets.

```md
## Objective
What this ticket should accomplish.

## Rationale
Why this work matters now and what source created it.

## Included Scope
- Item 1
- Item 2
- Item 3

## Excluded Scope
- Item 1
- Item 2
- Item 3

## Deliverables
- Deliverable 1
- Deliverable 2

## Acceptance Criteria
- Criterion 1
- Criterion 2
- Criterion 3

## GO Conditions
- Condition 1
- Condition 2

## NO-GO Conditions
- Condition 1
- Condition 2

## Dependencies
- Dependency 1

## Owner
Role, agent, or person accountable for completion.

## Approval Requirement
State any approval needed before Linear writes, PR opening, merge, deployment, external communication, billing, sensitive claims, or data handling.

## Risk Level
Low / Medium / High, with reason.

## Handoff Notes
Context future agents need after execution.
```

## Branch Rules

Create the branch from an up-to-date base branch after confirming the ticket is ready.

Branch names should reference the Linear ticket:

```txt
codex/<ticket>-short-description
feature/<ticket>-short-description
fix/<ticket>-short-description
chore/<ticket>-short-description
```

Examples:

```txt
codex/pip-66-ticket-pr-handoff-system
feature/pip-72-first-validation-form
fix/pip-84-scorecard-threshold-copy
```

Do not reuse a branch for a second ticket after merge. Start a new branch for the next ticket.

## Execution Workflow

1. Read the ticket and relevant repository artifacts.
2. Confirm dependencies and approval state.
3. Move the Linear ticket to In Progress.
4. Create a branch that references the ticket.
5. Implement only the included scope.
6. Avoid unrelated refactors, formatting churn, and template changes outside the ticket.
7. Run available validation commands.
8. Commit with the ticket identifier in the message.
9. Push the branch and open a PR linked to the Linear ticket.
10. Request review.
11. Classify review findings as P0, P1, P2, or P3.
12. Fix P0 and P1 in the same PR.
13. Fix P2 only when simple, safe, and inside scope.
14. Do not block merge on P3.
15. Revalidate after changes.
16. Merge only when review, validation, scope, and handoff are complete.
17. Update Linear with the final handoff.

## Pull Request Template

The repository PR template lives at `.github/pull_request_template.md`. PRs should include:

- Linear ticket link
- context
- included scope
- excluded scope
- validation performed
- review status
- risks and residual concerns
- follow-ups
- handoff notes

PR descriptions must stay current if review findings, validations, scope, or follow-ups change.

## Review Rules

Every PR must receive review before merge.

Review should cover:

- correctness
- linked Linear ticket scope
- missing tests or validations
- security risks
- maintainability
- observability when applicable
- documentation quality and links

Classify findings using `execution/approval-gates.md`:

| Severity | Blocks Merge | Rule |
|---|---|---|
| P0 | Yes | Critical, production, security, data loss, or unsafe external impact. |
| P1 | Yes | Relevant bug, likely regression, important architecture issue, or missing test on critical flow. |
| P2 | No, unless trivial and in scope to fix | Important improvement that is not blocking. |
| P3 | No | Cosmetic, style, or small improvement. |

If automated review is unavailable, use a documented structured review only when the user has approved that fallback for the cycle.

## Validation Expectations

Run the strongest available validation for the ticket type.

Examples:

- Documentation-only: `git diff --check`, link/path sanity, scope review against the Linear ticket.
- Frontend or app code: lint, typecheck, tests, build, and targeted UI verification when available.
- Backend or data changes: unit tests, integration tests, migration checks, and rollback notes when applicable.
- Governance changes: consistency check against `AGENTS.md`, `execution/approval-gates.md`, and related execution docs.

If a command does not exist, record that explicitly in the PR and Linear handoff. Do not imply unrun validation passed.

## Done Criteria

A ticket is done only when:

- acceptance criteria are met
- included scope is complete
- excluded scope was not added
- validations are run or explicitly unavailable
- review is complete
- P0 and P1 findings are resolved
- P2 findings are either resolved or documented as non-blocking
- required follow-up tickets exist, or no follow-ups are needed
- PR is merged when the ticket involves repository changes
- Linear has the final handoff comment
- repository learning or decision artifacts are updated when the ticket produced durable learning

Implementation tickets must not be closed without a merged PR.

## Status Update Expectations

Linear status should reflect the real execution state:

- Backlog: not selected for active execution.
- Todo: ready to execute after dependencies and approval are clear.
- In Progress: branch work is active.
- In Review: PR is open and waiting on review, checks, or review fixes.
- Done: merged and handed off, or documentary/investigative acceptance criteria are complete.
- Canceled: no longer valid, with rationale recorded.

Add comments when:

- work starts
- a blocker appears
- scope changes
- review finds P0 or P1 issues
- validation fails
- a follow-up ticket is created
- the ticket is ready for merge
- the ticket is complete

## Handoff Protocol

The final Linear handoff should include:

```md
## Final execution handoff

Branch:
PR:
Merge:
Merge commit:

## Summary

## Acceptance criteria result
- Criterion 1:
- Criterion 2:
- Criterion 3:

## Validation
- Command/check:
- Command/check:

## Review
- Review source:
- P0:
- P1:
- P2:
- P3:
- Fixed in this PR:
- Not fixed:

## Follow-ups
- Link:

## Knowledge updates
- Repository artifact updated:
- Decision or learning recorded:

## Residual risks
```

If there is no follow-up or residual risk, say so directly.

## Knowledge Update Rules

Update `knowledge/` only when the ticket creates durable learning, a decision record, reusable customer language, or future-agent context that belongs outside the current PR or Linear ticket.

Do not create knowledge artifacts for routine implementation notes that are already captured in the PR and Linear handoff.

## NO-GO Conditions

Do not merge when:

- the PR is not linked to the correct Linear ticket
- review is absent
- P0 or P1 findings remain open
- relevant validation failed
- the PR includes out-of-scope changes
- required follow-up tickets are missing
- the PR description is stale
- the Linear handoff would omit tests, risks, acceptance criteria, or review result
