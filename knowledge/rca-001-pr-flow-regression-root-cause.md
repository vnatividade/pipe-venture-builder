# RCA-001 — PR-Flow Regression Root Cause (PIP-130 through PIP-135)

## Record

- ID: RCA-001
- Date: 2026-05-18
- Owner: Claude Code executor under PIP-140; investigated for KDR-002 follow-up.
- Origin Linear ticket: PIP-140.
- Status: Final.
- Document type: Root Cause Analysis (evidence/learning artifact, not a decision).

## Summary

KDR-002 framed the PIP-130 through PIP-135 regression as "committed directly to `main` without PR/review." Investigation under PIP-140 found that framing partially incorrect: PRs DID exist for all six tickets, but the review gate failed in a different way — the Copilot pull-request reviewer errored on every single PR and no human approving review was recorded before merge. This RCA refines the diagnosis without superseding KDR-002's corrective decision.

## Original framing (KDR-002, Accepted 2026-05-17)

Stated that `git log --oneline -15` showed PIP-130 through PIP-135 as "direct commits to `main` (no `Merge pull request` lines)" and inferred that the PR + review gate had been bypassed entirely. The absence of `Merge pull request ...` subject lines was the visual signal.

## Investigation

Executed during PIP-140 on 2026-05-18 from the repository root.

### Commands

```bash
# Branch protection state
gh api repos/vnatividade/pipe-venture-builder/branches/main/protection
# → 404 Branch not protected

# PR association per commit
for sha in 08edd0d ff13856 1a069f1 fe0fe25 1605c16 e1cb5ce; do
  gh api "repos/vnatividade/pipe-venture-builder/commits/${sha}/pulls"
done

# Review state and bodies per PR
for n in 57 58 59 60 61 62; do
  gh api "repos/vnatividade/pipe-venture-builder/pulls/$n"
  gh api "repos/vnatividade/pipe-venture-builder/pulls/$n/reviews"
done
```

### Findings

| PIP ticket | Commit | PR | Copilot review state | Copilot review body | Human reviews | Merged by | Merge strategy |
|---|---|---|---|---|---|---|---|
| PIP-130 | `08edd0d` | #57 | COMMENTED | "Copilot encountered an error and was unable to review this pull request." | none | vnatividade | squash |
| PIP-131 | `ff13856` | #58 | COMMENTED | same | none | vnatividade | squash |
| PIP-132 | `1a069f1` | #59 | COMMENTED | same | none | vnatividade | squash |
| PIP-133 | `fe0fe25` | #60 | COMMENTED | same | none | vnatividade | squash |
| PIP-134 | `1605c16` | #61 | COMMENTED | same | none | vnatividade | squash |
| PIP-135 | `e1cb5ce` | #62 | COMMENTED | same | none | vnatividade | squash |

Branch protection on `main`: not configured (`404 Branch not protected`).

## Actual root cause

The regression has four contributing factors, none of which match the original "direct commit" framing:

1. **PRs existed** for all six tickets (#57–#62). The ticket → branch → PR flow was followed.
2. **Copilot reviewer is broken in this repository.** Every single Copilot review request returned the same generic error. The same failure pattern was observed independently on PIP-139 / PR #63. This is a repository-level integration failure, not a one-off transient.
3. **No human approving review** was recorded on any of the six PRs. With Copilot erroring, there was no second pair of eyes between author and merge.
4. **Squash merge strategy** produces a single commit on `main` with no `Merge pull request` subject, which is what KDR-002 visually misread as a direct push.
5. **No branch protection** on `main`. The repository-level policy in `execution/ticket-pr-handoff-system.md` ("every PR must be reviewed before merge") is text-only; nothing in GitHub enforces it. The author can self-merge immediately after a Copilot error response.

The PR flow technically passed the letter of the rule ("PR must receive review before merge" — Copilot did submit a review object), but failed the spirit (no substantive review of content occurred).

## Implications for KDR-002

KDR-002's diagnosis is partially inaccurate but its corrective decision remains correct and is **not** superseded:

- The decision to "reinstate PR + review enforcement and address the gap via branch protection" stands.
- The evidence section of KDR-002 should be read alongside this RCA. KDR-002 is immutable as accepted; this RCA is the authoritative refinement.
- KDR-002's recommended Option B (PR flow + branch protection) is the right action; this RCA strengthens the case by showing the gap is structural (Copilot fails AND no branch protection AND no human review) rather than procedural (people skipping the PR).

## Recommended actions (in scope of PIP-140)

1. **Enable branch protection on `main`** requiring at least one approving review, blocking direct pushes, and forbidding force pushes and deletions. Apply via `gh api PUT /repos/.../branches/main/protection` after the PIP-140 PR is merged (to avoid locking the PIP-140 PR itself out before protection is in place).
2. **Document the enforcement state** at `.github/branch-protection-policy.md`.
3. **Open a follow-up Linear ticket** to investigate and fix the Copilot pull-request reviewer integration (out of PIP-140 scope; it is a precondition for the automated portion of the review gate to function, but it is its own work).

## Recommended actions (out of scope; future)

- Adopt a merge-commit strategy for governance tickets so review history is preserved in main's git log, complementing branch protection. Optional; can stay squash if PR template is good enough.
- Require resolving review conversation threads before merge (set `required_conversation_resolution: true` in branch protection).
- Consider adding a CODEOWNERS file once the team grows; today, with a single human owner, it would add friction without benefit.

## References

- KDR-002 — `knowledge/kdr-002-restore-pr-flow.md` (Accepted; refined by this RCA, not superseded).
- Policy source — `execution/ticket-pr-handoff-system.md` "Review Rules" and "Structured Manual Review Fallback".
- Policy source — `AGENTS.md` "Pull Requests" section.
- PRs investigated — #57, #58, #59, #60, #61, #62 (all on `vnatividade/pipe-venture-builder`).
- PIP tickets — PIP-130, PIP-131, PIP-132, PIP-133, PIP-134, PIP-135 (all Done).
- Related Copilot failure on Claude Code pilot — PR #63 (PIP-139).
