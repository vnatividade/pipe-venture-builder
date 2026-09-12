# Branch Protection Policy — `main`

This file documents the operational enforcement state of the `main` branch. The substantive review policy lives in `execution/ticket-pr-handoff-system.md`; this file describes how GitHub enforces it.

## Effective configuration

**Measured on 2026-09-12, before any change:** `GET /repos/vnatividade/pipe-venture-builder/branches/main/protection` returned **404** and `GET /repos/.../rules/branches/main` returned an **empty list**. The `main` branch had **no protection and no ruleset at all** — the table under "Target state, never applied" below was written in 2026-05-18 and never reached the repository.

That mattered beyond documentation: `src/pipe_venture_builder/mission/delivery.py` disables git hooks (`core.hooksPath=/dev/null`) and treats `delivery.requireChecks` as its net. Until this date that net was only the mission supervisor polling `gh pr checks` — GitHub itself would have accepted a merge with red CI.

**Applied on 2026-09-12** — repository ruleset `main: CI verde obrigatória`, id `23056388`, `enforcement: active`, targeting `refs/heads/main`:

| Rule | Parameters | Rationale |
|---|---|---|
| `required_status_checks` | `runtime (node)`, `toolkit (python)`, `governança gerada em sincronia`; `strict: false` | The three jobs of `.github/workflows/ci.yml`. This is what makes `delivery.requireChecks` a real gate instead of a convention. `strict: false` so a PR is not forced to rebase onto every new `main` commit. |
| `pull_request` | `required_approving_review_count: 0` | **Measured, and it does not read like what it does.** PR #200 — the first PR under this ruleset — sat at `mergeStateStatus: BLOCKED` / `reviewDecision: REVIEW_REQUIRED` with all three checks green, and only became `CLEAN` after an approving review. With the `pull_request` rule present, GitHub requires *a* review even at count `0`. The cross-account path (author/merge `agents-natiivis`, review `vnatividade`) is therefore **structural**, not merely disciplinary. A single-account solo merge is blocked, because GitHub does not let an author approve their own PR — drop the `pull_request` rule if that ever has to change. |
| `pull_request` → `require_extra_approval_for_unattributed_changes` | `false` | **Turned off deliberately, after it bit.** GitHub defaults it to `true`. Every commit from an autonomous executor carries `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`, an address with no linked GitHub account — so GitHub classifies the change as *unattributed* even though the commit author is `agents-natiivis`, and **dismisses the standing approval on every push**. Measured on PR #200: the approval came back as `state: DISMISSED` while `dismiss_stale_reviews_on_push` was already `false`. With the trailer mandatory for executor commits, leaving this on would demand a fresh approval after each push. |
| `non_fast_forward` | — | Protects history. |
| `deletion` | — | Protects the branch from accidental deletion. |

Read the live state with:

```
gh api repos/vnatividade/pipe-venture-builder/rules/branches/main --jq '.[].type'
```

Note: creating or changing the ruleset requires **admin**, which only the `vnatividade` account has (`agents-natiivis` has push/triage but `admin: false`).

## Target state, never applied

The table below was the 2026-05-18 intent, written for the legacy branch-protection API. It is kept for history — **it was never the effective configuration**. Where it disagrees with the ruleset above, the ruleset wins.

| Setting | Value | Rationale |
|---|---|---|
| `required_pull_request_reviews.required_approving_review_count` | `1` | At least one approving review (human or trusted bot) before merge. Closes the PIP-130–135 gap where author-self-merge was possible. |
| `required_pull_request_reviews.dismiss_stale_reviews` | `true` | New pushes invalidate prior approvals. Prevents a stale review from authorizing later, unreviewed changes. |
| `required_pull_request_reviews.require_code_owner_reviews` | `false` | No CODEOWNERS file today; single-owner repo. Revisit when the team grows. |
| `required_pull_request_reviews.require_last_push_approval` | `false` | Allows the same reviewer to re-approve after their own follow-up commits. Useful for the solo + agentic flow. |
| `required_conversation_resolution` | `true` | Force resolving review threads before merge. Tightens the loop on review feedback. |
| `enforce_admins` | `false` | Owners and admins can override in emergencies. The intent is to prevent accidental bypass, not to make merges impossible if review tooling fails. |
| `required_status_checks` | `null` | Was true when written; CI has existed since 2026-08-05. Superseded by the ruleset above. |
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

## Operating modes and protection profiles

`execution/operating-modes.md` (PIP-659) defines per-repository execution modes. Protection must match the declared mode:

| Repository state | Protection profile |
|---|---|
| This repository (`pipe-venture-builder`) | Always the full configuration above. Knowledge-content-lane PRs (see `execution/operating-modes.md`) satisfy the 1-review requirement via cross-account agent review; they never touch governance files. |
| Venture repo in `restricted` mode | Full configuration above (≥1 human-or-trusted-bot approving review). |
| Venture repo in `exploration` mode | Either omit `required_pull_request_reviews` and rely on green status checks plus the exploration review path recorded in the PR, or keep `required_approving_review_count: 1` satisfied by cross-account agent review. Document the chosen profile in the venture repository. |

Absolute gates (production deploy, secrets, billing, customer data, external communications) are enforced by policy and operator behavior, not by branch protection — a merged PR still must not trigger them without human approval.

## Related artifacts

- `execution/operating-modes.md` — per-repository execution modes (exploration vs restricted).
- `execution/ticket-pr-handoff-system.md` — the substantive review and merge policy.
- `knowledge/kdr-002-restore-pr-flow.md` — the strategic decision to enforce PR + review on `main`.
- `knowledge/rca-001-pr-flow-regression-root-cause.md` — root cause of the PIP-130–135 review gap.
- `AGENTS.md` "Pull Requests" — high-level rules for PRs in this repository.
- `.github/pull_request_template.md` — the PR description template that must be populated for every PR.

## Change log

- 2026-05-18: Initial policy written under PIP-140. **Never applied** — confirmed by measurement on 2026-09-12 (404 on the protection endpoint, empty ruleset list).
- 2026-09-12: Ruleset `main: CI verde obrigatória` (id `23056388`) created and verified active under PIP-914: required status checks (the three CI jobs), pull request required, no deletion, no force-push. Zero *nominal* approvals — which, measured on PR #200, still require one review. To undo: `gh api -X DELETE repos/vnatividade/pipe-venture-builder/rulesets/23056388` with the `vnatividade` account.
