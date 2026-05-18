# GitHub Copilot Code Review — Repository Setup and Operational Notes

This file documents the operational state of the GitHub Copilot pull-request reviewer on this repository, the failure history that motivated PIP-143, and the current verification path.

## Current state (as of 2026-05-18)

GitHub Copilot pull-request reviewer is **operational** on this repository. New PRs receive substantive Copilot reviews when the reviewer is requested via:

- the GitHub web UI ("Request review" → "Copilot"), or
- the CLI: `gh pr edit <pr> --add-reviewer copilot-pull-request-reviewer`.

A representative recent example: PR #65 received the following review at 2026-05-18 03:39:37 UTC:

> "## Pull request overview — Documentation-only change that clarifies branch naming precedence by adding a subsection to the 'Branch Ownership' section..."

PR #64 received an equivalent review at 2026-05-18 03:34:29 UTC, including two inline findings (one count inconsistency and one factually-incorrect statement about GitHub author-approval behavior). Both findings were addressed in PIP-143.

## Observed failure history (resolved)

Between 2026-05-17 17:08 UTC and 2026-05-17 23:49 UTC, every Copilot review request on this repository returned the same generic error:

> "Copilot encountered an error and was unable to review this pull request. You can try again by re-requesting a review."

Eight Copilot review attempts across seven PRs (#57, #58, #59, #60, #61, #62, #63 — the last with two attempts) all returned that body in state `COMMENTED`.

Starting at 2026-05-18 03:34:29 UTC (PR #64), Copilot began returning substantive reviews. No repository-side change was made between the last error (23:49) and the first success (03:34) — branch protection on `main` was applied at 03:30 but that change is orthogonal to Copilot's review path.

**Likely cause:** transient GitHub-side service issue that resolved without intervention. No evidence of repository-level misconfiguration.

This failure pattern motivated KDR-002 (the PR-flow regression decision) and RCA-001 (the corrected root-cause analysis). Both records remain accurate: when the failure window is in effect, the Structured Manual Review Fallback is the only path to a substantive review, and the gate documented in `execution/ticket-pr-handoff-system.md` becomes operator discipline rather than tooling enforcement.

## Verification

To confirm Copilot Code Review is working on a fresh PR:

```bash
# 1. Request review (after the PR is open).
gh pr edit <pr-number> --add-reviewer copilot-pull-request-reviewer

# 2. Wait ~30–90 seconds. Copilot's review is asynchronous.

# 3. Inspect the review body.
gh api repos/vnatividade/pipe-venture-builder/pulls/<pr-number>/reviews \
  -q '.[] | select(.user.login == "copilot-pull-request-reviewer[bot]") | {state, body_first_120: (.body | .[0:120])}'
```

If the body starts with `"Copilot encountered an error"` the integration is failing again. If the body starts with `"## Pull request overview"` or contains substantive findings, Copilot is working.

## What to do if Copilot fails

When Copilot returns the generic error or no review at all within a reasonable wait window:

1. Re-request once: `gh pr edit <pr> --add-reviewer copilot-pull-request-reviewer`.
2. If the second attempt also errors: switch to the Structured Manual Review Fallback documented in `execution/ticket-pr-handoff-system.md`. Cycle approval is the project lead's standing durable grant (documented in `feedback_durable_permissions.md`). Post a structured comment on the PR per the fallback template.
3. Record the failure in the Linear handoff for the affected ticket so the failure history stays auditable.

Do not block the merge waiting indefinitely for Copilot. Branch protection requires one approving review (human or trusted bot); the Structured Manual Review Fallback is supplementary documentation, not a substitute for that approving state. For solo Claude Code PRs the project lead approves, OR Claude Code uses the documented `enforce_admins: false` override path (see `.github/branch-protection-policy.md`).

## Optional enhancement: Copilot custom instructions

Copilot's reviews on PR #64 and #65 included this hint:

> "💡 Add Copilot custom instructions for smarter, more guided reviews."

Custom instructions live at `.github/instructions/*.instructions.md` and tell Copilot how to review PRs in this repository (e.g., "always check that handoff comments follow the template in `execution/ticket-pr-handoff-system.md`", "flag any new file that touches restricted paths in `feedback_autonomous_loop.md`'s stop-hard list").

This enhancement is **out of scope for PIP-143**. It is tracked separately if approved (see follow-ups in the PIP-143 Linear handoff).

## What was NOT changed by PIP-143

- No GitHub repository settings were modified for Copilot. The failure resolved before any such change was attempted.
- No billing or subscription state was changed.
- No GitHub App was installed or uninstalled. The `copilot-pull-request-reviewer` bot was associated with the repository throughout (its presence in `requested_reviewers` confirmed installation; the failure was elsewhere in Copilot's pipeline).

## References

- `execution/ticket-pr-handoff-system.md` — substantive review policy and Structured Manual Review Fallback template.
- `.github/branch-protection-policy.md` — branch protection settings and override path.
- `knowledge/kdr-002-restore-pr-flow.md` — the decision to restore PR + review enforcement.
- `knowledge/rca-001-pr-flow-regression-root-cause.md` — root-cause analysis of the PIP-130–135 review gap (refines KDR-002 with the corrected diagnosis).
- Linear PIP-143 — investigation ticket.
- Linear PIP-140 — branch protection enforcement ticket.

## Change log

- 2026-05-18: Initial. Documents Copilot operational state, the resolved failure window, verification path, fallback policy, and optional enhancement.
