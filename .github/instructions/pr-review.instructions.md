---
applyTo: "**"
---

# Repository-Specific PR Review Instructions

This file gives the GitHub Copilot pull-request reviewer the governance context it needs to review PRs in this repository. The canonical rules live in the files referenced below; this file is the reviewer's checklist.

## Repository context

`pipe-venture-builder` is a governance/protocol repository for an agentic venture-builder pipeline. It is almost entirely Markdown today (no runtime, no tests). Reviews should focus on governance adherence, scope discipline, and documentation integrity.

## PR body must include

The PR description must follow `.github/pull_request_template.md`. Flag the PR if any of these required sections is missing:

- **Linear Ticket** link (`https://linear.app/pipe-venture-builder/issue/PIP-NNN/...`).
- **Context** — why the PR exists and what authorizing artifact or ticket produced it.
- **Included Scope** — explicit list matching the actual diff.
- **Excluded Scope** — explicit list of what was preserved or deferred.
- **Validation Performed** — concrete commands or checks run; "n/a — documentation-only repo" is acceptable.
- **Review Status** — primary reviewer (Copilot or human) and any fallback authorization.
- **Risks And Residual Concerns** — if zero, state that.
- **Follow-Ups** — list of follow-up tickets created, or "No follow-ups identified."
- **Handoff Notes** — branch, acceptance-criteria result, knowledge updates, residual risks.

## Shared high-risk governance files

A PR that modifies any of these files must serialize and include an explicit per-ticket carve-out statement in the PR body. The canonical list lives in `execution/parallel-execution-governance.md` "Shared High-Risk Files":

- `AGENTS.md`
- `CLAUDE.md`
- `execution/approval-gates.md`
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/multi-agent-operating-protocol.md`
- `execution/context-routing-protocol.md`
- `execution/parallel-execution-governance.md`
- the global Linear ticket template (`execution/linear-ticket-template-v2.md`)
- shared agent contracts in `.codex/agents/`
- shared skill contracts in `.agents/skills/`
- architecture decision records
- top-level `README.md`

Without an explicit carve-out, raise a **P0** finding. A normal carve-out statement looks like: *"This PR edits `<file>`, which is normally serialized as a shared high-risk file. Project lead granted explicit per-ticket carve-out on `<date>`; documented in the Linear ticket start comment."*

The Linear ticket template defines a separate field called **Restricted Files** with a stricter meaning: files listed there MUST NOT appear in the diff at all (no carve-out path; the ticket explicitly forbade them). Verify the diff against the ticket's `Restricted Files` and raise **P0** if violated.

## Branch naming

Branch must start with one of: `claude/`, `codex/`, `feature/`, `fix/`, `chore/`. The canonical rules are in `execution/multi-agent-operating-protocol.md` "Branch Ownership", `CLAUDE.md` (for `claude/<ticket>-...`), and `AGENTS.md` (for `codex/<ticket>-...`). Reject branches under `vnatiivis/` (Linear-auto-generated) or any personal prefix; the Linear `gitBranchName` field is informational only.

## Scope discipline

Compare the diff against the Linear ticket's `Expected Write Set`. Files outside that set are scope deviation. Acceptable only when the PR body documents the deviation explicitly with rationale. Otherwise raise a P2 finding.

## KDR / RCA conventions

- KDR files (`knowledge/kdr-*.md`) follow `knowledge/kdr-dar-template.md`. Once a KDR is merged as `Accepted`, do not change its substantive content (Decision, Context, Options Considered, Evidence, Risks, Revisit Trigger, etc.).
- The Status and Supersession fields are an explicit exception: per `knowledge/decision-conflict-protocol.md`, when a new KDR supersedes a prior one the prior KDR's `Status:` becomes `Superseded` and `Superseded by:` is set to the new record. Updating those fields is required and is not a content edit.
- RCA files (`knowledge/rca-*.md`) are evidence/learning artifacts; minor in-place corrections (typos, count fixes, factual refinements that don't change conclusions) are acceptable when called out in the PR body.
- Status field on a new KDR must match approval state: `Proposed` while awaiting human approval; flipped to `Accepted` in the same PR's final commit if the PR's merge constitutes that approval.

## Severity classification

When raising findings, use:

- **P0** — critical, blocking, production/security risk, data loss, governance-rule violation, shared-high-risk-file edit without carve-out, or any change to a file listed in the ticket's Restricted Files.
- **P1** — relevant correctness issue, likely regression, missing test on critical flow, factual error in governance documentation.
- **P2** — important improvement that's not blocking; fix only if simple, safe, and in-scope.
- **P3** — cosmetic, style, small improvement.

P0 and P1 block merge. P2 fixed only if trivial and in scope. P3 does not block merge. See `execution/approval-gates.md`.

## Manual fallback awareness

If Copilot's own review fails (returns "Copilot encountered an error..."), the Structured Manual Review Fallback in `execution/ticket-pr-handoff-system.md` may be used ONLY when:

- the user has explicitly approved structured manual fallback for the current execution cycle, OR
- the assigned Linear ticket explicitly allows the fallback.

Otherwise the correct action is to stop and document the blocker per `execution/ticket-pr-handoff-system.md` "Review Wait And Stop Rules". When reviewing a PR that did use the fallback, verify the cycle/ticket approval is referenced in the fallback comment; flag absence of that reference as **P1**.

When a Claude Code-led PR uses the documented admin merge override (`gh pr merge --admin`) per `.github/branch-protection-policy.md` "Override path", the override usage and rationale must be recorded as a Linear comment on the originating ticket (mirroring this in the PR body is optional but recommended). Flag absence of the Linear audit record as **P1**.

## References

- `AGENTS.md` — non-negotiable safety rules and approval gates.
- `CLAUDE.md` — Claude Code adapter (branch naming rules included).
- `execution/multi-agent-operating-protocol.md` — shared executor protocol; "Branch Ownership" section.
- `execution/parallel-execution-governance.md` — canonical "Shared High-Risk Files" list.
- `execution/ticket-pr-handoff-system.md` — review path, structured manual fallback rules, review wait/stop rules.
- `execution/approval-gates.md` — severity model and gated actions.
- `execution/linear-ticket-template-v2.md` — Linear ticket field semantics (Expected Write Set, Restricted Files).
- `.github/pull_request_template.md` — PR body template (canonical section list).
- `.github/branch-protection-policy.md` — branch protection configuration and override path (Linear audit requirement).
- `.github/copilot-review-setup.md` — Copilot operational state and fallback policy.
- `knowledge/kdr-dar-template.md` — KDR/DAR format and example.
- `knowledge/decision-conflict-protocol.md` — KDR supersession protocol (Status, Superseded by fields).
