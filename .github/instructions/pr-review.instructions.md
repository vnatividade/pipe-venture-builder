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

Changes to these files are serialized by default. Per `execution/parallel-execution-governance.md` "Shared High-Risk Files", a PR touching any of them must explain why the change belongs in the current ticket and what other active tickets may be affected. Canonical list:

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

Without that explanation, raise a **P1** finding. When the project lead has granted an explicit per-ticket carve-out for an autonomous executor (e.g., Claude Code, Codex), that grant is expected in the PR body or Linear ticket start comment (typical form: *"This PR edits `<file>`; project lead granted explicit per-ticket carve-out on `<date>`."*). The "per-ticket carve-out" concept is a session-grant convention used by autonomous executors operating under the project lead's durable permission; it is not separately codified in the canonical repo docs. Apply the same **P1** severity if the explanation is missing for an autonomous-executor PR.

The Linear ticket template defines a separate field called **Restricted Files** with a stricter meaning: files listed there MUST NOT appear in the diff at all (no carve-out path; the ticket explicitly forbade them). Verify the diff against the ticket's `Restricted Files` and raise **P0** if violated.

## Branch naming

Branches should follow the recommended patterns in `execution/multi-agent-operating-protocol.md` "Branch Ownership": `claude/<ticket>-...` for Claude Code-led work (per `CLAUDE.md`), `codex/<ticket>-...` for Codex-led work (per `AGENTS.md`), or `feature/`, `fix/`, `chore/` as appropriate. Per that same section, branches under the auto-generated `<displayName>/` prefix (Linear's `gitBranchName` field, which is informational only) should not be pushed when an executor convention applies. Flag a personal-prefix branch on an executor-led PR as **P2**.

## Scope discipline

Compare the diff against the Linear ticket's `Expected Write Set`. Files outside that set are scope deviation. Acceptable only when the PR body documents the deviation explicitly with rationale. Otherwise raise a P2 finding.

## KDR / RCA conventions

- KDR files (`knowledge/kdr-*.md`) follow `knowledge/kdr-dar-template.md`. Strategic decisions are changed by writing a NEW KDR that supersedes the prior one, per `knowledge/decision-conflict-protocol.md` — not by rewriting the prior KDR's substantive content (Decision, Context, Options Considered, Evidence, Risks, etc.).
- On the prior (superseded) KDR, the Status and Supersession fields ARE expected to be updated per the same protocol: `Status: Superseded`, `Superseded by: <new KDR id>`, plus the reason. These field updates are not content edits.
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

When a Claude Code-led PR uses the documented admin merge override per `.github/branch-protection-policy.md` "Override path" (either via the GitHub web UI's admin override, by temporarily disabling protection, or via `gh pr merge --admin`), the override usage and rationale must be recorded as a Linear comment on the originating ticket. Mirroring this in the PR body is optional but recommended. Flag absence of the Linear audit record as **P1**.

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
