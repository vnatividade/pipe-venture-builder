# KDR-002 - Restore PR + Review Enforcement For All Merges To Main

## Record

- ID: KDR-002
- Date: 2026-05-17
- Owner: Claude Code executor; approved by vnatividade (project lead) via PR merge
- Origin Linear ticket: PIP-139
- Origin PR or artifact: branch `claude/pip-139-kdr-002-restore-pr-flow`; PR https://github.com/vnatividade/pipe-venture-builder/pull/63
- Status: Accepted (human approval 2026-05-17 via PR #63 merge)

## Decision

- Decision: Reinstate the PR + review enforcement for every merge to `main`, as defined in `execution/ticket-pr-handoff-system.md`. PIP-130 through PIP-135 are documented exceptions; future tickets must follow the existing ticket → branch → PR → review → merge flow.
- Decision type: Governance
- Short rationale: Six consecutive governance tickets bypassed the required PR + review gate. The deviation undermines traceability and weakens the multi-agent baseline that PIP-126 through PIP-129 established via PRs #53–#56.

## Context

- Trigger: Readiness review for PIP-136 (Claude Code pilot) by the Claude Code executor on 2026-05-17 identified that PIP-130 through PIP-135 were committed directly to `main` without `Merge pull request` history.
- Current phase: Multi-agent baseline operationalization (Horizon 2).
- Relevant artifacts:
  - `execution/ticket-pr-handoff-system.md`
  - `AGENTS.md`
  - `execution/multi-agent-operating-protocol.md`
  - `execution/approval-gates.md`
  - git commits: `e1cb5ce`, `1605c16`, `fe0fe25`, `1a069f1`, `ff13856`, `08edd0d`
  - Prior PR-flow merge commits: `a3df9cd` (PR #56), `8c062a6` (PR #55), `2bc9d27` (PR #54), `3a51f73` (PR #53)
- Constraints:
  - History on `main` will not be rewritten.
  - PIP-130 through PIP-135 content stays as-is; the decision is forward-looking enforcement only.
  - Enabling GitHub branch protection requires repository admin access and is tracked in the follow-up ticket PIP-140, not in this KDR.

## Options Considered

| Option | Pros | Cons | Why accepted/rejected |
|---|---|---|---|
| A — Reinstate PR flow by convention only, no settings change | Lightweight; no admin work | Relies on operator discipline; the same gap already recurred six times | Rejected — the deviation evidence shows convention alone is insufficient |
| B — Reinstate PR flow + enable GitHub branch protection on `main` requiring PR and review | Hard enforcement; matches existing docs; addresses recurrence | Requires admin settings change and a small operational friction (no direct push) | **Accepted (recommended)** — enforcement work tracked in PIP-140 |
| C — Revert PIP-130 through PIP-135 and re-apply via PRs | Strict historical consistency | High churn; low marginal value; would require history rewrite or six new PRs to re-create review trails | Rejected — out of scope and disproportionate to the value gained |
| D — Accept the new pattern (skip PR for governance-only tickets) | No process change needed | Contradicts `AGENTS.md` and `execution/ticket-pr-handoff-system.md`; weakens multi-agent baseline | Rejected — would explicitly weaken governance |

## Evidence

| Evidence | Type | Source | Confidence |
|---|---|---|---|
| Six direct commits to `main` for PIP-130 through PIP-135 with no merge commit | Validation | `git log --oneline -15` executed on 2026-05-17 from repository root | High |
| Policy mandates PR + review before merge | Governance artifact | `execution/ticket-pr-handoff-system.md` sections "Review Rules" and "NO-GO Conditions"; `AGENTS.md` "Pull Requests" section | High |
| Prior multi-agent baseline tickets used PR merges (#53–#56) | Validation | Merge commits `a3df9cd`, `8c062a6`, `2bc9d27`, `3a51f73` visible in `git log` | High |
| No prior accepted KDR/DAR weakens the PR-review rule | Governance artifact | `knowledge/` directory contains only `kdr-dar-template.md`; no decision records prior to this one | High |

## Risks

- Risk accepted: Reinstating enforcement adds friction for tickets that previously committed directly. Friction is documented and intentional.
- Risk rejected: Continuing to allow ad-hoc direct commits to `main`, which would normalize the deviation and erode traceability.
- Mitigation: The follow-up ticket PIP-140 captures the enforcement implementation (branch protection or equivalent) and requires explicit human approval before changing repository settings.
- Follow-up ticket: PIP-140.

## Revisit Trigger

Revisit this decision when:

- Evidence changes: a documented operational reason emerges for skipping PR review on a defined class of tickets, and the class is small and bounded.
- Metric or threshold changes: review SLAs measurably block execution velocity for a sustained period after PIP-140 is implemented.
- Customer segment changes: not applicable to this governance decision.
- Risk changes: governance regressions fall to zero for at least 10 consecutive tickets without enforcement, suggesting cultural fix sufficed and enforcement can be relaxed.
- Date or phase: at the next horizon transition, or immediately after PIP-140 completes and produces operational data.

## Conflict Scan

- Prior decisions checked: `execution/ticket-pr-handoff-system.md`, `AGENTS.md`, `execution/multi-agent-operating-protocol.md`, `execution/approval-gates.md`, `knowledge/` (no prior KDR/DAR files).
- Relationship: Clarifies. This KDR reaffirms the existing PR-review rule and surfaces a regression rather than introducing a new policy.
- Conflict summary: No conflict. The illustrative `KDR-001` in `knowledge/kdr-dar-template.md` is an inline example about MVP scope and is unrelated to PR-flow governance.
- Authority used: `execution/ticket-pr-handoff-system.md` "Review Rules" and `AGENTS.md` "Pull Requests".
- Human review needed: yes.

## Supersession

- Supersedes: None.
- Superseded by: —
- Conflict status: None.

## Human Review

- Human review required: yes.
- Review source: PR #63 — Copilot automated review attempted (errored both times); structured manual fallback approved by project lead for this cycle; merge by project lead.
- Approval or objection: Approved by project lead on 2026-05-17 via PR #63 merge.

## Numbering Note

This is the first real KDR file in `knowledge/`. It is numbered `002` to match the originating Linear ticket (PIP-139) scope which references `kdr-002-restore-pr-flow.md`. The `KDR-001` identifier appears only as an inline example inside `knowledge/kdr-dar-template.md` and does not correspond to a separate decision record file. Future KDR numbering may renormalize via a separate ticket.
