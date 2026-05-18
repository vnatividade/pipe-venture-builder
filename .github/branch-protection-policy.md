# Branch Protection Policy — `main`

This file documents the operational enforcement state of the `main` branch. The substantive review policy lives in `execution/ticket-pr-handoff-system.md`; this file describes how GitHub enforces it.

## Effective configuration (target state)

Applied via `gh api --method PUT repos/vnatividade/pipe-venture-builder/branches/main/protection` after PIP-140 merges:

| Setting | Value | Rationale |
|---|---|---|
| `required_pull_request_reviews.required_approving_review_count` | `1` | At least one approving review (human or trusted bot) before merge. Closes the PIP-130–135 gap where author-self-merge was possible. |
| `required_pull_request_reviews.dismiss_stale_reviews` | `true` | New pushes invalidate prior approvals. Prevents a stale review from authorizing later, unreviewed changes. |
| `required_pull_request_reviews.require_code_owner_reviews` | `false` | No CODEOWNERS file today; single-owner repo. Revisit when the team grows. |
| `required_pull_request_reviews.require_last_push_approval` | `false` | Allows the same reviewer to re-approve after their own follow-up commits. Useful for the solo + agentic flow. |
| `required_conversation_resolution` | `true` | Force resolving review threads before merge. Tightens the loop on review feedback. |
| `enforce_admins` | `false` | Owners and admins can override in emergencies. The intent is to prevent accidental bypass, not to make merges impossible if review tooling fails. |
| `required_status_checks` | `null` | No CI is configured. Update when CI is introduced. |
| `restrictions` | `null` | Anyone with write access may open PRs. |
| `allow_force_pushes` | `false` | Protects history. |
| `allow_deletions` | `false` | Protects the branch from accidental deletion. |
| `required_linear_history` | `false` | Allow merge commits. Squash merges also remain allowed; merge strategy is a separate operational decision. |

## How it interacts with the policy in `execution/ticket-pr-handoff-system.md`

The repository policy requires every PR to be reviewed before merge and defines a Structured Manual Review Fallback when automated reviewers are unavailable. Branch protection enforces a count (≥1 approving review) but does not know about the fallback path. Operational implication:

- When Copilot review errors (as observed on PIP-130–135 and PIP-139 — see `knowledge/rca-001-pr-flow-regression-root-cause.md` and `.github/copilot-review-setup.md`), the author must perform a Structured Manual Review Fallback comment AND obtain an explicit approving review. GitHub does not let PR authors approve their own PRs; for solo work, the approving review must come from a separate account (the project lead, a teammate, or a trusted reviewing bot). When no separate approver is available, use the documented admin override path below.
- For Claude Code executor PRs: the project lead reviews and approves. The Claude Code self-review fallback comment is supplementary documentation, not a substitute for the GitHub approving review state.

## Override path

When branch protection legitimately needs to be bypassed (e.g., recovering from a broken state, applying a security fix that cannot wait for review):

1. The repository owner uses GitHub's admin override on the PR ("Merge without waiting for requirements") or temporarily disables the protection rule.
2. Document the override in a Linear comment on the originating ticket with: timestamp, override reason, who applied it, and a follow-up ticket if any policy gap was exposed.
3. Restore the protection rule immediately after if it was disabled.

Routine PRs MUST NOT use the override path.

## Related artifacts

- `execution/ticket-pr-handoff-system.md` — the substantive review and merge policy.
- `knowledge/kdr-002-restore-pr-flow.md` — the strategic decision to enforce PR + review on `main`.
- `knowledge/rca-001-pr-flow-regression-root-cause.md` — root cause of the PIP-130–135 review gap.
- `AGENTS.md` "Pull Requests" — high-level rules for PRs in this repository.
- `.github/pull_request_template.md` — the PR description template that must be populated for every PR.

## Change log

- 2026-05-18: Initial policy. Applied via `gh api` under PIP-140 (PR #TBD). Configuration as documented above.
