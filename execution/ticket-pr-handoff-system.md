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

For parallel Codex and Claude Code execution, use `execution/parallel-execution-governance.md` before starting branches that may overlap in files, domains, dependencies, or merge order.

## Execution Workflow

1. Read the ticket and relevant repository artifacts.
2. Confirm dependencies and approval state.
3. Confirm `execution/tactical-execution-plan.md` is linked, embedded, or explicitly not applicable when development work is involved.
4. Confirm `execution/development-execution-loop.md` is followed or explicitly not applicable when development work is involved.
5. Move the Linear ticket to In Progress.
6. Create a branch that references the ticket.
7. Implement only the included scope and current approved slice.
8. Avoid unrelated refactors, formatting churn, and template changes outside the ticket.
9. Run available validation commands.
10. Repair relevant failures before expanding scope or requesting review.
11. Commit with the ticket identifier in the message.
12. Push the branch and open a PR linked to the Linear ticket.
13. Request review.
14. Classify review findings as P0, P1, P2, or P3.
15. Fix P0 and P1 in the same PR.
16. Fix P2 only when simple, safe, and inside scope.
17. Do not block merge on P3.
18. Revalidate after changes.
19. Merge only when review, validation, scope, and handoff are complete.
20. Update Linear with the final handoff.

## Pull Request Template

The repository PR template lives at `.github/pull_request_template.md`. PRs should include:

- Linear ticket link
- context
- Tactical Execution Plan link or not-applicable reason when development work is involved
- development loop status, slice, ADR/RFC decision, and follow-up trigger when development work is involved
- included scope
- excluded scope
- validation performed
- review status
- risks and residual concerns
- follow-ups
- handoff notes
- context strategy and known omissions when meaningful repository context was involved

PR descriptions must stay current if review findings, validations, scope, or follow-ups change.

## Review Rules

Every PR must receive review before merge.

Use this review path:

1. Request the configured automated reviewer when one is available for the repository.
2. Check whether Copilot has reviewed the PR.
3. If Codex review is enabled, request Codex review using the repository-approved prompt or workflow.
4. If no automated review appears in a reasonable wait window, use the structured manual fallback only when the user has approved that fallback for the current cycle or the assigned ticket explicitly allows it.
5. If no automated review is available and no manual fallback approval exists, stop and document the blocker in the PR and Linear ticket.

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

## Structured Manual Review Fallback

The structured manual fallback counts as review only when it is explicitly approved for the current execution cycle or by the assigned ticket.

When using the fallback, add a PR comment with:

- why automated review was not used or did not appear
- scope reviewed
- correctness assessment
- Linear ticket alignment
- missing tests or validation gaps
- security risk assessment
- maintainability assessment
- observability assessment when applicable
- documentation and link assessment
- P0, P1, P2, and P3 counts
- fixes made in the PR
- findings intentionally not fixed
- validation results
- merge readiness statement

The fallback review must still block merge when it finds unresolved P0 or P1 issues.

## Review Wait And Stop Rules

For automated review, use a short, reasonable wait window rather than waiting indefinitely. A reasonable wait means:

- check the PR immediately after opening it
- wait briefly and check again when no review has appeared
- proceed to the approved structured fallback if the reviewer still has not appeared

Stop instead of using fallback when:

- the user has not approved structured manual fallback for the cycle
- the ticket requires a specific external reviewer
- branch protection requires a GitHub review state that a PR comment cannot satisfy
- review tooling returns a permission or configuration error that changes merge safety
- the PR includes high-risk security, data, billing, production, customer, legal, compliance, or external communication changes

## Validation Expectations

Run the strongest available validation for the ticket type.

Use `execution/test-oriented-delivery-rule.md` to decide whether BDD-style acceptance examples, TDD/automated tests, E2E/browser evidence, schema checks, or manual documentary evidence are required.

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
- Tactical Execution Plan was followed or explicitly not applicable
- Development Execution Loop was followed or explicitly not applicable
- review is complete
- context choices and known omissions are recorded when meaningful repository context was involved
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

Executor tool:
Branch:
PR:
Merge:
Merge commit:

## Scope and ownership
- Linear ticket:
- Expected write set:
- Actual files changed:
- Restricted files touched:
- Parallelization class:
- Conflict or merge-order notes:

## Summary

## Acceptance criteria result
- Criterion 1:
- Criterion 2:
- Criterion 3:

## Validation
- Command/check:
- Command/check:
- Unavailable validation:

## Review
- Review source:
- P0:
- P1:
- P2:
- P3:
- Fixed in this PR:
- Not fixed:

## Monitoring
- Required follow-up monitoring:
- Owner or agent:
- Trigger or cadence:

## Metrics
- Success metric:
- Current status:
- Follow-up needed:

For multi-agent execution, use `execution/agentic-operations-metrics.md` to keep metrics lightweight, manually collectible, and tied to decisions about throughput, quality, conflicts, readiness, rework, and handoff quality.

## Context and token efficiency
- Context strategy:
- Safety-floor sources:
- Full artifacts read:
- Targeted searches or snippets used:
- Summaries or compression created:
- Known omitted context:
- Omission risk:
- Token/cost/session signal:
- Follow-up needed:

## Follow-ups
- Link:
- Reason:

## Knowledge updates
- Repository artifact updated:
- Decision or learning recorded:

## Residual risks

## Next recommended action
- Ticket:
- Reason:
```

Do not include secrets, credentials, customer data, production data, private source material, or sensitive operational details in the handoff. If there is no follow-up, monitoring action, metric update, knowledge update, residual risk, or next action, say so directly.

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
- token pressure or context omissions would remove safety-critical governance, approval, validation, or review evidence
