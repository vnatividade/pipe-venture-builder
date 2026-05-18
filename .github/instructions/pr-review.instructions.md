---
applyTo: "**"
---

# Repository-Specific PR Review Instructions

This file gives the GitHub Copilot pull-request reviewer the governance context it needs to review PRs in this repository. The canonical rules live in the files referenced below; this file is the reviewer's checklist.

## Repository context

`pipe-venture-builder` is a governance/protocol repository for an agentic venture-builder pipeline. It is almost entirely Markdown today (no runtime, no tests). Reviews should focus on governance adherence, scope discipline, and documentation integrity.

## PR body must include

The PR description must follow `.github/pull_request_template.md`. Flag the PR if any of these are missing:

- **Linear Ticket** link (`https://linear.app/pipe-venture-builder/issue/PIP-NNN/...`).
- **Included Scope** — explicit list matching the actual diff.
- **Excluded Scope** — explicit list of what was preserved or deferred.
- **Validation Performed** — concrete commands or checks run; "n/a — documentation-only repo" is acceptable.
- **Review Status** — primary reviewer (Copilot or human) and any fallback authorization.
- **Risks And Residual Concerns** — if zero, state that.
- **Handoff Notes** — branch, acceptance-criteria result, knowledge updates, residual risks.

## Restricted files

A PR that modifies any of these files must include an explicit per-ticket carve-out statement in the PR body referencing the project lead's approval. Without that statement, raise a P0 finding:

- `AGENTS.md`
- `CLAUDE.md`
- `execution/approval-gates.md`
- `execution/multi-agent-operating-protocol.md`
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- global Linear ticket templates under `execution/linear-ticket-template-v2.md`

A normal carve-out statement looks like: *"This PR edits <file>, which is normally restricted. Project lead granted explicit per-ticket carve-out on <date>; documented in the Linear ticket start comment."*

## Branch naming

Branch must start with one of: `claude/`, `codex/`, `feature/`, `fix/`, `chore/`. Reject branches under `vnatiivis/` (Linear-auto-generated) or any other personal prefix — see `execution/multi-agent-operating-protocol.md` "Branch Ownership" and `.github/branch-protection-policy.md`. The Linear `gitBranchName` field is informational only.

## Scope discipline

Compare the diff against the Linear ticket's `Expected Write Set`. Files outside that set are scope deviation. Acceptable only when the PR body documents the deviation explicitly with rationale. Otherwise raise a P2 finding.

`Restricted Files` listed in the ticket must not appear in the diff at all.

## KDR / RCA conventions

- KDR files (`knowledge/kdr-*.md`) follow `knowledge/kdr-dar-template.md`. Once a KDR is merged as `Accepted`, do not edit it. New decisions create a new KDR record with `Supersedes:` set, per `knowledge/decision-conflict-protocol.md`.
- RCA files (`knowledge/rca-*.md`) are evidence/learning artifacts; minor corrections (typos, count fixes, factual refinements that don't change conclusions) are acceptable in-place when called out in the PR body.
- Status field on a KDR must match approval state: `Proposed` while awaiting human approval; flipped to `Accepted` in the same PR's final commit if the PR's merge constitutes that approval.

## Severity classification

When raising findings, use:

- **P0** — critical, blocking, production/security risk, data loss, governance-rule violation, restricted-file edit without carve-out.
- **P1** — relevant correctness issue, likely regression, missing test on critical flow, factual error in governance documentation.
- **P2** — important improvement that's not blocking; fix only if simple, safe, and in-scope.
- **P3** — cosmetic, style, small improvement.

P0 and P1 block merge. P2 fixed only if trivial and in scope. P3 does not block merge. See `execution/approval-gates.md`.

## Manual fallback awareness

If Copilot's own review fails (returns "Copilot encountered an error..."), the PR author is expected to post a Structured Manual Review Fallback comment per `execution/ticket-pr-handoff-system.md`. When you are reviewing such a PR successfully, also look at any prior fallback comment to confirm self-reported findings match what you see in the diff.

When a Claude Code-led PR uses the documented admin merge override (`gh pr merge --admin`), the PR body or handoff must record the override usage and rationale. Flag absence of that audit record as a P1 finding.

## References

- `AGENTS.md` — non-negotiable safety rules and approval gates.
- `CLAUDE.md` — Claude Code adapter.
- `execution/multi-agent-operating-protocol.md` — shared executor protocol.
- `execution/ticket-pr-handoff-system.md` — review and handoff rules.
- `execution/approval-gates.md` — severity model and gated actions.
- `.github/pull_request_template.md` — PR body template.
- `.github/branch-protection-policy.md` — branch protection configuration and override path.
- `.github/copilot-review-setup.md` — Copilot operational state and fallback policy.
- `knowledge/kdr-dar-template.md` — KDR/DAR format and example.
- `knowledge/decision-conflict-protocol.md` — KDR supersession protocol.
