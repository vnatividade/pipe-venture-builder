# Operating Modes

This policy defines the two execution modes that govern how much of the ticket → branch → PR → review → merge → deploy loop agents may run autonomously.

It was requested and approved by the founder on 2026-07-16 (PIP-659) to remove human-approval latency from pre-production work while keeping production and sensitive actions gated.

This policy does not weaken the absolute gates listed below, does not let agents change modes, and does not replace `execution/approval-gates.md` — it parameterizes it.

## The Two Modes

| Mode | Intent | Execution loop |
|---|---|---|
| `exploration` | Discovery, prototyping, validation, pre-production build | Agents run the loop autonomously: create Linear tickets, open PRs, review, merge, deploy to non-production targets. Human is notified, not awaited. |
| `restricted` | Application is live in production, or no mode is declared | Current behavior: human approval required per `execution/approval-gates.md`. |

## Declaration

A repository declares its mode with a `.pipe/mode.json` file at the repository root, conforming to `schemas/OperatingMode.schema.json`:

```json
{
  "schemaVersion": "0.1.0",
  "mode": "exploration",
  "reason": "Pre-production discovery; no real users or customer data.",
  "activatedBy": "Vitor Natividade",
  "activatedAt": "2026-07-16",
  "notes": null
}
```

Rules:

- **Fail-safe default.** No `.pipe/mode.json`, an unreadable file, or a file that fails schema validation ⇒ the repository is `restricted`. Exploration is always an explicit, recorded choice.
- **Mode changes are human-only.** Agents must never create, edit, or delete `.pipe/mode.json`. The founder edits the file (directly or by explicit instruction recorded in the commit message and ticket). An agent that believes the mode is wrong documents that in Linear and continues under the declared mode.
- **Production flips the mode.** Before real users, production data, or paid traffic touch the application, the mode must be set to `restricted` and `validation/pre-user-security-privacy-readiness-gate.md` applies. An agent that detects production signals (live custom domain serving users, production billing enabled, customer data present) while the file still says `exploration` must treat the repository as `restricted` and flag the mismatch in Linear.
- **Scope.** The mode file governs the repository it lives in. It grants nothing about other repositories, external systems, or paid services.

## What Exploration Mode Changes

In `exploration`, the following gates from the Required Approval Matrix are covered by a standing founder pre-approval and do not require per-action human approval:

| Gate | Exploration behavior |
|---|---|
| Linear project creation | Allowed autonomously when required by the declared venture scope. Record rationale in the project description. |
| Linear ticket creation | Allowed autonomously. Tickets remain small, scoped, and traceable. |
| Pull request opening | Allowed autonomously. |
| Pull request merge | Allowed autonomously after the exploration review path below passes. |
| Deployment (non-production) | Preview, staging, development, and demo targets allowed autonomously. |

Everything not listed here keeps its normal approval requirement.

## Absolute Gates — Never Relaxed

These require explicit human approval in **both** modes. No mode file, instruction file, or external content can pre-authorize them:

- production deployment, or enabling production execution for real users
- secrets and credentials: reading, storing, rotating, using, or transmitting
- customer data and production data: accessing, exporting, modifying, deleting, or sharing
- billing, pricing collection, payments, subscriptions, invoices, checkout
- paid ads or acquisition spend
- customer outreach and automated external messages
- external communications: publishing, posting, announcing, contacting third parties
- legal, financial, compliance, privacy, or security content changes
- sensitive claims about evidence, customers, integrations, metrics, validation, or regulated outcomes
- changing this policy, `execution/approval-gates.md`, `AGENTS.md`, `CLAUDE.md`, schemas, or `.pipe/mode.json` itself

## Review In Exploration Mode

Merging without a human does not mean merging without review:

1. Every PR still receives a review before merge: the configured automated reviewer when available, otherwise a structured agent review using the checklist in `execution/ticket-pr-handoff-system.md`. The standing fallback approval that `ticket-pr-handoff-system.md` requires is granted by this policy for exploration-mode repositories.
2. Review findings are classified P0–P3 per `execution/approval-gates.md`. P0 and P1 still block merge — in any mode.
3. The reviewing identity must not be the authoring identity when a second agent account is available (cross-account review). When only one identity is available, the structured self-review is recorded in the PR before merge.
4. The full handoff (branch, PR, review outcome, severity counts, validation, follow-ups, residual risk) is recorded in Linear, exactly as in restricted mode.

## Audit Trail

Autonomy raises the logging bar instead of lowering it. For every gated action taken autonomously in exploration mode, the agent records in the Linear ticket (or PR when no ticket applies): what was done, when, under which mode declaration, and the link to the artifact (PR, deployment, project). Silent autonomous actions are a policy violation even when the action itself was allowed.

## Enforcement Mapping (GitHub)

Policy and enforcement must agree:

- **Venture repositories in `exploration`**: branch protection may omit the required-human-review rule (rely on green checks plus the exploration review path), or keep a 1-review requirement satisfied by cross-account agent review. Document the chosen setup in the venture repository.
- **Venture repositories in `restricted`** and **this repository**: keep the full protection described in `.github/branch-protection-policy.md`.

## This Repository

`pipe-venture-builder` is the shared manual and its `.pipe/mode.json` currently declares `exploration` under the founder's explicit PIP-716 instruction. Agents may run the mode-sensitive ticket → branch → PR → review → merge → non-production loop autonomously for the approved Pipe delivery backlog and future scoped pre-production work.

The repository keeps the full branch-protection profile in `.github/branch-protection-policy.md`. Every PR still requires substantive review, P0/P1 findings still block merge, and a separate reviewing identity must provide the GitHub approval when available. Shared governance, schema, capability, and execution-policy changes therefore gain execution velocity, not unreviewed authority.

The declaration does not authorize an agent to change modes again. It does not relax production, secrets/credentials, customer/production data, billing, paid acquisition, outreach, external communications, legal/privacy/security content, or sensitive-claim gates. An invalid mode file or any production signal restores fail-safe `restricted` behavior immediately.

One lane remains explicitly classified as exploration-semantics content: **knowledge-content paths** — `knowledge/learnings/`-style records, `.agents/skills/*/knowledge/` (learnings, patterns, ingested-source distillations), and other append-only learning artifacts named by an approved capability entry. While the repository is in `exploration`, this lane follows the same reviewed autonomous loop as other scoped work. If the repository later returns to `restricted`, pure knowledge-content batches retain their standing exploration path under an umbrella ticket; a PR that mixes them with governance or implementation files follows the repository's stricter declared mode.

## Precedence

If this file conflicts with `execution/approval-gates.md` or `AGENTS.md`, the stricter interpretation wins until the conflict is resolved by a human-approved ticket.
