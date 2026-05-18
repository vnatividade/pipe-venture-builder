# Orchestration Readiness Analysis

This analysis evaluates whether the `pipe-venture-builder` repository is ready to be operated by a future orchestrator (the architecture plan names Hermes and OpenClaw as candidate orchestrators; this analysis treats those as placeholders for the general orchestrator class until a specific tool is evaluated).

It is the deliverable for PIP-137 (MUD-012 in `architecture/agentic-multi-agent-codex-claude-plan.md`).

This document does NOT authorize orchestrator implementation, installation, configuration, scheduling, automated dispatch, automatic conflict resolution, automatic ticket creation, or any external integration. The analysis is the entire deliverable; concrete adaptation work is proposed but not created.

## Record

- ID: orchestration-readiness-analysis-2026-05-18
- Date: 2026-05-18
- Owner: Claude Code executor under PIP-137; reviewed by project lead via PR merge.
- Origin Linear ticket: PIP-137.
- Status: Initial baseline analysis.

## Purpose

Compare the operating requirements of a general orchestrator (the class that Hermes, OpenClaw, or equivalent tools would belong to) against the actual implemented baseline of `pipe-venture-builder`, identify gaps and risks, and propose adaptation work as candidate tickets without creating them.

## Scope boundary (explicit)

- IN scope: inventory of baseline capabilities, comparison against generic orchestrator needs, gap analysis, risk assessment, proposed adaptation tickets, references.
- OUT of scope: installing or configuring any orchestrator; writing scheduler, dispatcher, or automation code; creating new Linear tickets for the adaptation work; vendor-specific evaluation of Hermes or OpenClaw without a separate approval; modifying approval gates or governance files; importing third-party orchestrator libraries.

## Baseline inventory (what exists today)

The Codex + Claude Code baseline (MUD-001 through MUD-011 in the architecture plan) is implemented and validated by recent execution:

### Operating protocol layer

- `AGENTS.md` — repository safety rules and approval gates.
- `CLAUDE.md` — Claude Code adapter pointing to the shared protocol.
- `execution/multi-agent-operating-protocol.md` — shared executor protocol (one ticket → one branch → one PR, branch ownership including the recent gitBranchName clarification, approval boundaries, parallel execution rules, conflict handling, handoff requirements).
- `execution/approval-gates.md` — severity model (P0/P1/P2/P3), required approvals, NO-GO conditions, evidence rules.
- `execution/ticket-pr-handoff-system.md` — ticket → branch → PR → review → merge → handoff workflow with delivery-update template.
- `execution/context-routing-protocol.md` — read-first rules per ticket type.
- `execution/parallel-execution-governance.md` — parallelization classes, shared high-risk files list, ownership, conflict types.
- `execution/linear-governance-model.md` and `execution/linear-ticket-template-v2.md` — Linear ticket structure for multi-agent execution.
- `execution/ticket-type-field-matrix.md` — required and conditional fields per ticket type.
- `execution/agent-readiness-validator.md` — checklist that classifies tickets as `READY`, `READY WITH APPROVAL`, `NOT READY`, `BLOCKED`.
- `execution/agentic-operations-metrics.md` — lightweight manual metrics for throughput, execution quality, parallelization health, readiness, and handoff.

### Tool / executor layer

- Codex: `.codex/agents/*` agent contracts and specializations; historical execution evidence in merged PRs #1–#56 (most of the foundation and templates) and #57–#62 (recent governance increments PIP-130–135).
- Claude Code: `CLAUDE.md` adapter (PIP-127); `.claude/settings.local.json` permission set; durable autonomy grants captured in Claude Code memory at `~/.claude/projects/...`; recent execution evidence in PRs #63 (PIP-139), #64 (PIP-140), #65 (PIP-141), #66 (PIP-143), #67 (PIP-144).
- Shared skills: `.agents/skills/core-skill-contracts.md` and related contracts.

### Repository governance state

- Branch protection on `main` enabled (PIP-140): requires 1 approving review, dismisses stale reviews, requires conversation resolution, blocks force-push and deletion, allows admin override under `enforce_admins: false`.
- Documented admin override path in `.github/branch-protection-policy.md`.
- Documented Copilot reviewer operational state in `.github/copilot-review-setup.md`.
- Reviewer guidance for Copilot in `.github/instructions/pr-review.instructions.md` (PIP-144).
- Knowledge artifacts: `knowledge/kdr-002-restore-pr-flow.md` (the decision that re-established PR flow), `knowledge/rca-001-pr-flow-regression-root-cause.md` (the corrected diagnostic).

### Linear state

- Single team (`PIP`), single primary project (`Pipe Venture Builder Base Repository`).
- ~144 issues created to date; the multi-agent baseline tickets (PIP-126 through PIP-144) are all Done.
- Ticket template v2 in active use.
- Labels include `agent:codex`, `agent:claude`, `parallelizable:*`, `complexity:*`, `effort:*`, severity/risk/horizon tags.

## Required orchestrator capabilities (general)

A general orchestrator that dispatches work between Codex and Claude Code (and possibly other executors) must be able to:

1. **Read tickets** — pull approved Linear tickets in priority/dependency order; parse the template v2 fields (especially Type, Executor Tool, Expected Write Set, Restricted Files, Dependencies, Prerequisites, Parallelizable, Definition of Ready).
2. **Resolve readiness** — apply `execution/agent-readiness-validator.md` to decide whether a ticket can start now or needs approval, fixing, or a blocker.
3. **Choose executor** — match ticket Executor Tool field to an available agent (Codex, Claude Code, or other), respecting branch naming conventions and per-agent capability.
4. **Respect ownership** — refuse to dispatch a ticket whose Expected Write Set overlaps another in-flight ticket per `execution/parallel-execution-governance.md`, or sequence them.
5. **Trigger the executor** — start the agent in the correct repository state (branch from main, ticket context loaded per `execution/context-routing-protocol.md`).
6. **Observe execution** — watch for PR open, commits, review state, merge state via GitHub events.
7. **Validate progress** — confirm that validation commands listed in the ticket were run, that no restricted file was edited, that the write set matches.
8. **Record progress** — write Linear comments at key gates (start, PR open, review, merge, handoff) using the templates in `execution/ticket-pr-handoff-system.md`.
9. **Handle conflicts** — detect merge conflicts, file/domain overlap, dependency conflicts per `execution/parallel-execution-governance.md` "Conflict Types"; pause and request human resolution rather than auto-resolving.
10. **Generate follow-ups** — when a ticket surfaces a new issue, draft a follow-up ticket using `execution/linear-ticket-template-v2.md` and stop at the human-approval gate before creation.
11. **Respect approval gates** — never bypass `AGENTS.md` "Non-Negotiable Safety Rules" or `execution/approval-gates.md` "Required Approval Matrix". Detect when an action would cross a gate and pause for human.
12. **Maintain audit trail** — every dispatch, every override, every gate decision recorded in Linear so a human can reconstruct the execution without conversation memory.

## Gap analysis (capability vs current baseline)

| Capability | Current state | Gap | Severity |
|---|---|---|---|
| Read tickets via Linear API | Linear API is accessible (used in this session via MCP); template v2 fields are populated on recent tickets. | Older tickets (pre-PIP-130) lack v2 fields; orchestrator would need backfill or be limited to v2-compliant tickets. | Medium |
| Resolve readiness | Validator exists as a checklist document, applied manually. | No automated runner; orchestrator would need to encode the validator's logic or call out to a service that does. | High — but mitigable by keeping validator declarative and orchestrator-readable |
| Choose executor | Executor Tool field exists in template; recent tickets have it populated. | No mapping from Executor Tool to a running agent process; no agent registry. | High — orchestrator needs an agent registry that doesn't exist |
| Respect ownership | Parallelization rules documented; shared high-risk files enumerated; PR write-set deviation flagged in review (now Copilot does this per PIP-144). | No machine-readable lock or check before dispatch; ownership conflicts surface at PR review, not at dispatch time. | High |
| Trigger executor | Manual today (project lead opens Claude Code session, runs Codex). | No remote-trigger mechanism for Codex or Claude Code from a third process. Claude Code Routines exist (Anthropic-side) for Claude; Codex has its own dispatch model. | High — vendor-specific work needed per executor |
| Observe execution | GitHub API + Linear API provide events; manually consumed today. | No event consumer wiring; would require webhook handlers or polling. | Medium |
| Validate progress | Validation commands listed per ticket; humans verify on PR review (or self-review fallback). | No automated runner; Copilot review now functional but is general-purpose, not validation-command-runner. | Medium |
| Record progress | Linear comments are the canonical record; Claude Code wrote 8 sequential handoff comments this week. | Recording is reliable when Claude Code executes; orchestrator would need to produce equivalent comments per gate. | Low (pattern is clear) |
| Handle conflicts | Conflict types and resolution rules documented; this week's execution had zero merge conflicts in 5 Claude PRs. | Conflict detection is post-hoc (PR-time, not dispatch-time). Orchestrator would need a pre-dispatch overlap check. | Medium |
| Generate follow-ups | Pattern proven this session (PIP-138, PIP-143, PIP-144 all created as follow-ups during execution); creation gated by human approval. | Orchestrator would need to draft, not create, and stop at the human gate consistently. | Low (gate is well-defined; orchestrator must respect it) |
| Respect approval gates | Gates listed in `execution/approval-gates.md` and `AGENTS.md`; durable autonomy grants captured per-executor (Claude Code memory file). | Gates are textual; orchestrator would need to encode each as a stop condition. Per-executor grants are not currently centralized in Linear or repo. | Medium |
| Audit trail | Linear comments + git log + PR descriptions cover the audit trail for this week's work. | Sufficient for human review; orchestrator would need to enforce comment-on-every-gate by construction. | Low |

Overall: the **declarative layer** (rules, templates, fields, validator) is in place and exercised. The **runtime layer** (dispatcher, agent registry, event consumer, automation hooks) does not exist and is intentionally not built per the architecture plan.

## Baseline-readiness evidence

`execution/agentic-operations-metrics.md` "Baseline For Future Orchestration" lists seven questions that must be answered with stable evidence before evaluating an orchestrator. Current evidence from this session's batch (PIP-139, PIP-140, PIP-141, PIP-143, PIP-144 — 5 Claude Code PRs in 8 hours):

| Question | Evidence | Answer |
|---|---|---|
| Tickets consistently READY before branch work? | All 5 Claude PRs had ticket fields populated per template v2; PIP-138 was identified as a stale blocker and closed before its dependent (PIP-136) proceeded. | **Yes for recent tickets**, with the caveat that the recent batch was all Claude-authored or Claude-drafted; mixed-author evidence is thin. |
| Expected write sets accurate? | PIP-139 (1 file, matched), PIP-140 (2 files, matched), PIP-141 (1 file, matched), PIP-143 (3 files, 1 scope-deviation documented), PIP-144 (1 file, matched). | **Mostly yes**; one deliberate scope deviation (RCA-001 corrections in PIP-143) was caught and documented. |
| Dependencies and approvals explicit enough for dispatch? | Each ticket's PR body listed Dependencies + Approval Requirement; the autonomous loop stopped at every approval gate; per-ticket carve-outs were recorded when needed (PIP-141). | **Yes for explicit gates**; nuanced cases (carve-outs, admin override) needed Claude Code memory to apply, not Linear-encoded. Orchestrator would need this captured durably. |
| Handoffs sufficient for another agent to resume? | Each PR's Linear handoff comment used the full template with executor, branch, PR, merge commit, scope, validation, review, monitoring, metrics, follow-ups, residual risks, next recommended action. | **Yes** — the handoffs are exhaustive and self-describing. |
| Validation results recorded consistently? | `git diff --check`, scope match, markdown sanity, template completeness recorded in each PR + handoff. | **Yes for documentation-only work**; runtime/test validation not exercised because no runtime exists in this repo. |
| Merge conflicts rare and explainable? | Zero merge conflicts across the 5 Claude PRs and the 8 Copilot-iteration commits on PIP-144. | **Yes for serial Claude-only execution**; parallel Codex + Claude evidence is absent. |
| Follow-ups specific and traceable? | PIP-138, PIP-143, PIP-144 all created as follow-ups during execution with full template fields and origin links. | **Yes**. |

The data is favorable but limited: it represents one author (Claude Code) executing serially over a short window. The architecture plan is correct that more evidence is needed before evaluating a specific orchestrator — specifically:

- Mixed-agent parallel execution evidence (Codex + Claude on overlapping or near-overlapping work).
- Evidence from longer time windows, not a single multi-hour session.
- Evidence on code (not just documentation) tickets, once the repo has runtime code.
- Evidence of READY-WITH-APPROVAL and NOT-READY classifications being formally produced by the readiness validator, not just inferred.

## Hermes/OpenClaw note

The architecture plan and several execution docs name "Hermes" and "OpenClaw" as candidate orchestrators. The repository contains no specification, vendor link, capability matrix, integration guide, or proof-of-concept for either tool. Cross-repo grep confirms they appear only as named placeholders in this repo.

Recommendation: do not commit to "Hermes" or "OpenClaw" by name before a separate, scoped evaluation ticket is approved. A specific-tool evaluation should answer at minimum:

- What is the tool's dispatch model? (event-driven, polling, scheduler, manual trigger)
- How does it model executors? (process, container, API call, vendor-specific)
- How does it consume Linear-like tickets? (native, via plugin, via custom adapter)
- What's its governance model for approval gates? (configurable, hard-coded, none)
- What's its license, hosting, data residency, and security posture? (this is approval-gated by `AGENTS.md`)
- Does it support the per-executor capability we use today (Claude Code Routines, Codex CLI, etc.)?

Until those questions are answered, the orchestration discussion should remain about the generic orchestrator class as described in this analysis.

## Risks of adding orchestration prematurely

- **Hides operational immaturity.** An orchestrator that wraps an unstable baseline will not stabilize it; it will spread brittleness across more tickets faster.
- **Pulls forward governance debt.** Approval gates that work in human-paced execution may fail at orchestrator pace (e.g., admin merge override used by Claude Code is currently bounded by Claude self-review; an unbounded orchestrator using the same override would weaken the gate significantly).
- **Creates a second source of truth.** If the orchestrator stores execution state outside Linear, divergence is inevitable; recovery becomes hard.
- **Vendor lock-in by accident.** Adopting one orchestrator's ticket model can make migrating away expensive even if the tool turns out to be a poor fit.
- **Distracts from the venture-building purpose.** This repo's purpose is the venture-builder pipeline (idea → MVP), not orchestration tooling. Time on orchestrator infrastructure is time not spent on `product/`, `validation/`, `growth/`.

## Adaptation plan (candidate tickets, not created)

The following are proposed for the orchestration horizon. They are NOT created now per PIP-137's "Do not execute now" boundary. Listed in suggested dependency order.

### Candidate A — Collect mixed-executor evidence before tool evaluation

- **Type:** observability, workflow.
- **Priority:** P2 if orchestration is on the horizon, P3 if it can wait.
- **Scope:** Run at least 3 tickets where Codex executes and 3 where Claude Code executes in the same week, with at least one pair that would normally be parallelizable. Collect metrics per `execution/agentic-operations-metrics.md`. Update knowledge with the cross-executor pattern.
- **Rationale:** the current evidence base is Claude-only and short. Mixed-author, longer-window evidence is required by the metrics doc before specific-tool evaluation.

### Candidate B — Formalize the readiness validator as a runnable checklist

- **Type:** workflow, governance.
- **Priority:** P2.
- **Scope:** Convert `execution/agent-readiness-validator.md` from a prose checklist into a structured artifact (table or YAML) that a human or orchestrator could run mechanically. Validate against the recent batch of tickets.
- **Rationale:** any orchestrator would need the readiness check to be machine-callable. Even without an orchestrator, structured validator output would improve human triage.

### Candidate C — Pre-dispatch overlap check

- **Type:** workflow, governance.
- **Priority:** P3.
- **Scope:** Define a check that compares a proposed ticket's Expected Write Set against all in-flight tickets' Expected Write Sets and flags overlap before branch work starts. Today this surfaces at PR review; pre-dispatch would prevent some PR-time conflicts.
- **Rationale:** addresses the "ownership conflict surfaces post-hoc" gap identified above.

### Candidate D — Centralize per-executor durable grants

- **Type:** governance, documentation.
- **Priority:** P2.
- **Scope:** Move durable per-executor permission grants (currently in Claude Code memory at `~/.claude/projects/.../memory/feedback_durable_permissions.md`) into a checked-in artifact (e.g., `execution/executor-grants.md`) with explicit scope, expiry, and audit trail. Apply equivalent capture for Codex if grants exist.
- **Rationale:** an orchestrator cannot read per-executor session-local memory; grants must be discoverable from the repo for any new agent or human reviewer.

### Candidate E — Define an executor capability registry

- **Type:** architecture, governance.
- **Priority:** P3.
- **Scope:** Document each executor's actual runtime: version, dispatch entry point, supported repository operations, severity ceiling, restricted areas, ticket-type fit. Live in `architecture/` as a discoverable matrix.
- **Rationale:** any orchestrator that chooses executors needs this matrix. Even without one, the matrix would clarify what Codex vs Claude Code should do.

### Candidate F — Vendor evaluation ticket (Hermes / OpenClaw / alternatives)

- **Type:** architecture, governance, orchestration-prep.
- **Priority:** P3 (gated on A through E producing useful evidence).
- **Scope:** Evaluate specific orchestrator tools against the capability matrix and the gap list in this analysis. Produce an ADR with the chosen tool or the decision to defer further.
- **Rationale:** specific-tool decisions should follow generic-orchestrator readiness, not lead it.

### Explicit anti-candidates (not to be created)

- An autonomous orchestrator implementation ticket.
- An "auto-create follow-up tickets" automation.
- A scheduler that runs unattended outside business hours without operator approval per cycle.
- An override-by-default mechanism for any approval gate.
- A "master agent" or "meta-agent" pattern that wraps Codex + Claude under a third agent's prompt.

These are explicitly out of scope per `execution/multi-agent-operating-protocol.md` "Future Orchestrator" and `architecture/agentic-multi-agent-codex-claude-plan.md` section 5 "Camada futura de orquestracao".

## Definition-of-done evidence

PIP-137 acceptance criteria mapped to this document:

- Analysis uses the real implemented baseline, not the current plan alone → met. Baseline inventory references concrete file paths, recent PR numbers, and merge commits from this session.
- Analysis compares orchestrator requirements against actual Linear/Git/handoff/readiness/metrics behavior → met. The gap analysis table and baseline-readiness evidence table tie directly to artifacts in `execution/` and recent execution history.
- Analysis produces recommendations and follow-up tickets, not immediate implementation → met. Candidates A–F are drafted, not created; anti-candidates listed; non-implementation boundary repeated.

## Out-of-scope reaffirmation

This analysis does not:

- create, edit, or schedule any orchestration infrastructure.
- install, configure, or evaluate Hermes, OpenClaw, or any specific orchestrator product.
- create the candidate tickets listed above (those require separate human approval per `AGENTS.md` and the autonomous-loop carve-outs).
- modify any approval gate, governance file, or canonical executor protocol.
- import third-party orchestrator libraries or templates.
- store secrets, credentials, customer data, billing details, or production data.

## References

- `architecture/agentic-multi-agent-codex-claude-plan.md` — canonical plan; MUD-012 specifies this analysis as the deliverable.
- `execution/multi-agent-operating-protocol.md` — operating protocol for current Codex + Claude Code baseline.
- `execution/parallel-execution-governance.md` — shared high-risk files, ownership, conflict types.
- `execution/linear-ticket-template-v2.md` — template fields an orchestrator would consume.
- `execution/ticket-type-field-matrix.md` — required and conditional fields per type.
- `execution/agent-readiness-validator.md` — readiness classification.
- `execution/agentic-operations-metrics.md` — baseline-readiness questions and manual metrics.
- `execution/ticket-pr-handoff-system.md` — handoff template the orchestrator would need to honor.
- `execution/approval-gates.md` — required approval matrix.
- `execution/context-routing-protocol.md` — read-first rules per ticket type.
- `.github/branch-protection-policy.md` — effective branch protection on `main`.
- `.github/copilot-review-setup.md` — Copilot reviewer operational state.
- `.github/instructions/pr-review.instructions.md` — Copilot reviewer guidance.
- `knowledge/kdr-002-restore-pr-flow.md` — decision that restored PR enforcement.
- `knowledge/rca-001-pr-flow-regression-root-cause.md` — corrected root-cause analysis of the PR-flow regression.
- Recent execution evidence: PRs #63 (PIP-139), #64 (PIP-140), #65 (PIP-141), #66 (PIP-143), #67 (PIP-144).
- Linear: PIP-137 (this ticket), PIP-126 through PIP-136 (baseline implementation), PIP-138 through PIP-144 (recent execution).

## Change log

- 2026-05-18: Initial baseline analysis under PIP-137. No prior version. Future revisions should be a new analysis ticket, not in-place edits, when the underlying baseline evolves.
