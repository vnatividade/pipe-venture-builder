# ADR-001: Converge idea and existing-product intake on ProductBaseline

## Record

- ADR ID: ADR-001
- Title: Converge idea and existing-product intake on ProductBaseline
- Date: 2026-07-20
- Status: Proposed
- Owner: Architecture Agent
- Linear ticket: PIP-700
- PR: Not opened
- Related architecture review: PIP-700 documentation review
- Supersedes: None
- Superseded by: None

## Context

Pipe currently describes a greenfield path that begins with one raw idea and advances through founder focus, C.O.N.T.R.O.L.E., validation, PRD, MVP scope, architecture, Linear, delivery, and learning.

The founder also needs to bring already-started products under the same governance. Those products may have code, releases, Git history, GitHub issues or pull requests, Linear work, and partial documentation without having followed Pipe's earlier gates.

Forcing an existing product through the greenfield path as if no work existed would discard useful history. Treating existing implementation as proof that earlier validation occurred would fabricate evidence. Maintaining two complete downstream pipelines would create governance drift.

The system also needs to move between computers. Pipe must therefore define which state is canonical, which state is local and recoverable, and how executors such as Codex, Claude Code, and Hermes receive the same governed context. Agent Atelier is already a registered internal capability and must travel through that distribution model without user-specific paths.

Constraints:

- Repository artifacts remain canonical for product strategy, validation, architecture, governance, and durable knowledge.
- Linear remains canonical for execution state, priority, blockers, ownership, and handoff.
- GitHub remains canonical for code delivery evidence: branches, commits, pull requests, review, and merge.
- A local control plane may retain runs, events, checkpoints, and approval requests, but this state must be recoverable or reconcilable.
- Conversation memory, model output, code existence, and synthetic material are not customer or market evidence.
- External mutations and sensitive actions remain governed by `AGENTS.md`, `.pipe/mode.json`, and `execution/approval-gates.md`.

Evidence or source artifacts:

- `execution/core-pipeline-map.md`
- `execution/pipe-command-catalog.md`
- `execution/conversational-founder-guide.md`
- `execution/guided-session-artifact.md`
- `execution/linear-governance-model.md`
- `architecture/orchestration-readiness-analysis.md`
- `architecture/capability-adapter-contract.md`
- `architecture/context-pack-builder-spec.md`
- `setup/template-initialization-workflow.md`
- `.agents/skills/atelier/SKILL.md`
- `capabilities/entries/capability.internal.atelier.json`

- Human review required: yes
- Approval record or blocker: PIP-700 authorizes the proposed architecture and documentation. PR opening and merge remain separately gated.

## Options Considered

| Option | Pros | Cons | Why accepted/rejected |
|---|---|---|---|
| Keep only the greenfield pipeline | No new entry contract. | Erases brownfield reality or encourages invented historical gates. | Rejected. It cannot govern products already under development safely. |
| Maintain separate greenfield and brownfield lifecycles end to end | Each route can be optimized independently. | Duplicates gates, agent contracts, commands, and state transitions; invites drift. | Rejected. Differences belong at intake and normalization, not across the entire lifecycle. |
| Use dual entry adapters that converge on one `ProductBaseline` | Preserves entry-specific discovery while giving every downstream consumer one contract. | Requires a canonical schema and an explicit convergence gate. | Accepted. |
| Make Hermes or another orchestrator the source of truth | Central runtime can present a unified UI and event stream. | Creates vendor lock-in and conflicts with repository, Linear, and GitHub authority. | Rejected. Runtime state is operational and recoverable, not canonical product truth. |
| Copy the entire base repository into every product indefinitely | Simple initial cloning. | Causes governance drift and makes upgrades difficult. | Rejected as the long-term distribution model; allowed only as a bootstrap technique until a versioned distribution exists. |

## Decision

### 1. Two entry modes

Pipe defines two explicit intake modes:

- `idea`: ingest a brainstorm, founder note, guided session, or source bundle for a product that has not yet established an implementation baseline.
- `adopt`: inspect an existing product and reconstruct its present state from repository, Linear, GitHub, approved documentation, and other source artifacts.

`/pipe:idea` remains the greenfield front door. `/pipe:adopt` is added as the brownfield front door. Both names are specification contracts until a later runtime ticket implements them.

### 2. One convergence contract

Both entry modes must emit `schemas/ProductBaseline.schema.json` before downstream orchestration treats the product as governed.

The baseline records:

- entry mode and current lifecycle stage
- product identity and governed system references
- source manifest and sensitivity boundaries
- statements classified as fact, inference, assumption, conflict, or missing
- artifact inventory and relationships
- validation/evidence posture
- governance gaps
- proposed reconciliation actions
- approval state, next actions, and stop conditions

A `ProductBaseline` is a current-state control artifact. It is not proof that historical gates were completed.

### 3. Evidence classification is mandatory

Every material statement derived during intake or adoption is classified:

| Classification | Meaning | Decision use |
|---|---|---|
| `fact` | Directly supported by one or more inspectable sources. | May describe only the scope proven by those sources. |
| `inference` | Reasoned interpretation of sourced facts. | Advisory until reviewed or converted into a decision. |
| `assumption` | Founder or agent belief without sufficient source support. | Input to validation; never evidence. |
| `conflict` | Sources disagree or current behavior contradicts a declared artifact. | Blocks affected decisions until disposition is recorded. |
| `missing` | Required context or evidence is absent. | Creates a gap or next action; cannot be silently defaulted. |

Code, commits, releases, tickets, and PRs can prove implementation or delivery history. They cannot by themselves prove customer demand, willingness to pay, product-market fit, or that an upstream strategic gate occurred.

### 4. Brownfield adoption is forward-looking remediation

`adopt` creates an as-is baseline, identifies governance debt, and recommends the smallest forward path. It must not rewrite history to make the product appear compliant.

An existing product may continue to receive narrowly scoped maintenance when safely justified. New product expansion, customer claims, billing, production changes, or material scope growth remain blocked when relevant evidence, risk, or approval gaps are unresolved.

### 5. Reconciliation is plan-first, non-destructive, and idempotent

Linear and GitHub reconciliation has two separate phases:

1. Read and propose: inventory external state, match records, and produce actions such as `create`, `update`, `link`, `ignore`, or `investigate`.
2. Apply: execute only approved actions under the target repository's operating mode and absolute gates.

Every proposed action carries a stable idempotency key, source references, reason, expected effect, confidence, approval requirement, and current application status. Re-running adoption must update the plan rather than duplicate work.

Automatic deletion, history rewriting, forced closure, merge, deployment, or conversion of uncertain matches is outside this decision.

### 6. Responsibility boundaries

| Surface | Canonical responsibility | Must not become |
|---|---|---|
| Product repository | Product, validation, architecture, governance, schemas, decisions, durable learning | Live ticket status or secret store |
| Linear | Execution state, backlog, priority, owner, dependency, blocker, handoff | Product evidence repository or code history |
| GitHub | Code, commits, branches, PRs, review, merge, delivery evidence | Product strategy authority |
| Pipe control plane | Workflow runs, events, checkpoints, approvals, reconciliation cache | Sole source of product truth |
| Hermes | Governed executor/runtime and optional control-surface adapter | Policy authority or canonical memory |
| Codex and Claude Code | Ticket-scoped execution through shared contracts | Independent governance systems |
| Capability Registry | Capability availability, routing, lifecycle, boundary, fallback | Permission grant by itself |

### 7. Portable distribution uses a thin product manifest

The long-term distribution model is:

- a versioned Pipe toolkit containing policies, schemas, workflows, capabilities, and adapters
- a small product-local `.pipe/project.json` manifest that binds a product repository to a Pipe version and approved external references
- machine-local installation state for runtimes, dependencies, connector authentication, caches, and checkpoints

The manifest must contain identifiers and non-sensitive configuration only. Secrets and credentials remain in user-controlled environment or keychain storage and are never copied by Pipe.

Until an implementation ticket creates this distribution, the existing template flow remains valid for greenfield initialization.

### 8. Agent Atelier is part of the capability distribution

Atelier is confirmed at:

- `.agents/skills/atelier/SKILL.md`
- `.codex/agents/atelier-specialization.md`
- `capabilities/entries/capability.internal.atelier.json`

Its current lifecycle is `pilot` with approved review status. Portability requires its installer and adapters to resolve paths relative to the installed module or registered capability, not a specific user's `~/Developer` directory. Its current Claude-oriented installer is evidence of a working adapter path, not yet a cross-runtime bootstrap.

### 9. One downstream lifecycle

After the convergence gate, both modes use the existing stage owners and commands:

```txt
idea ─┐
      ├─> ProductBaseline ─> discover/validate/prd/plan/build/check/review/ship/learn
adopt ┘
```

The baseline's `currentStage` determines the next safe command. Adoption may classify a product at a later operational stage while still recording unresolved earlier governance gaps. Stage detection does not waive those gaps.

## Consequences

Positive consequences:

- Existing products can enter governance without losing or falsifying history.
- New ideas and existing products share schemas, agent contracts, approvals, and downstream lifecycle.
- Linear/GitHub reconciliation can be retried safely.
- Hermes can execute Pipe workflows without owning Pipe policy or memory.
- Portability becomes testable through declared bootstrap and doctor contracts.

Tradeoffs accepted:

- Adoption produces uncertainty and gaps instead of a deceptively complete product record.
- Initial implementation will require read-only adapters before mutation automation.
- The current template and Atelier installer remain transitional until portability tickets are implemented.

Risks introduced:

- A baseline may be mistaken for validation approval.
- Semantic matching may suggest incorrect Linear or GitHub relationships.
- Product manifests may drift from the installed Pipe version.
- A runtime dashboard could expose mutation routes or sensitive state incorrectly.

Mitigations:

- Explicit evidence and gate fields in `ProductBaseline`.
- Proposed matches require confidence, sources, and approval before application.
- `pipe doctor` must validate version, adapter, capability, and manifest compatibility.
- Runtime adapters must inherit the capability adapter and approval contracts.

Follow-up candidates, in dependency order:

1. Implement a repository-only `ProductBaseline` generator with fixture tests.
2. Implement read-only Git, repository, Linear, and GitHub inventory adapters.
3. Define and implement `.pipe/project.json`, `pipe bootstrap`, and `pipe doctor`.
4. Make Atelier adapters path-independent and add Codex/Hermes installation adapters.
5. Implement the reconciliation planner and approval UI.
6. Implement supervised reconciliation mutations.
7. Evaluate a persistent Pipe control plane and Hermes adapter against real execution evidence.

These are candidates only. PIP-700 does not authorize creating their Linear tickets.

## Review Trigger

Review this ADR when:

- a runtime implementation proves the `ProductBaseline` contract insufficient
- a third entry mode cannot be expressed as intake plus normalization
- Linear or GitHub source-of-truth responsibilities change
- the product manifest or versioning strategy is implemented
- Atelier leaves pilot lifecycle or gains new runtime adapters
- production, customer-data, or security requirements materially change the portability boundary
- a P0/P1 reconciliation or evidence-classification failure appears

## Links

- Linear: https://linear.app/pipe-venture-builder/issue/PIP-700/define-dual-entry-product-intake-architecture-idea-adopt
- PR: Not opened
- Architecture review: PIP-700 acceptance review
- KDR/DAR: Not required; this ADR is the canonical technical decision candidate
