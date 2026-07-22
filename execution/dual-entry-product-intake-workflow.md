# Dual-Entry Product Intake Workflow

## Purpose

This workflow defines how Pipe starts governance from either a brainstorm (`idea`) or an already-started product (`adopt`) and converges both on `schemas/ProductBaseline.schema.json`.

It is the operational companion to `architecture/adr/adr-001-dual-entry-product-intake.md`.

Origin ticket: PIP-700.

This document is specification-only. It does not implement CLI commands, scan repositories, authenticate connectors, create or update Linear/GitHub records, install runtimes, or authorize external mutations.

## Entry Selection

| Entry | Use when | First governed output | Existing command relationship |
|---|---|---|---|
| `idea` | The primary source is a brainstorm, founder note, guided conversation, or opportunity signal and no implementation baseline must be reconstructed. | `ProductBaseline` with `entryMode: idea` and an IdeaBrief/product-context handoff. | Extends the current `/pipe:idea` contract. |
| `adopt` | A product already has code, Git history, deployments, tickets, PRs, documentation, users, or operational state that must be understood. | `ProductBaseline` with `entryMode: adopt`, as-is inventory, governance gaps, and reconciliation plan. | Adds `/pipe:adopt` before the shared stage map. |

When uncertain, choose `adopt` if implementation or operational history exists. A product may still be early-stage strategically even when its code is advanced.

## Shared Invariants

Both entries must:

- start from an assigned Linear ticket or a human-approved planning request
- preserve the original source artifact or a safe pointer to it
- exclude secrets, credentials, customer data, production data, and unapproved sensitive material
- label facts, inferences, assumptions, conflicts, and missing context separately
- preserve repository, Linear, and GitHub source-of-truth boundaries
- produce a `ProductBaseline` before downstream routing
- record the current stage and the next safe stage independently from implementation maturity
- stop before gated actions without the approval required by the target repository mode
- record what sources do not prove
- remain repeatable without relying on the initiating conversation

## State Model

```txt
requested
  -> source_bounded
  -> inventory_complete
  -> baseline_draft
  -> review_required
  -> accepted | blocked
  -> routed_to_next_stage
```

Terminal meanings:

| State | Meaning |
|---|---|
| `accepted` | Baseline is sufficient for routing. It does not mean all governance gaps are resolved. |
| `blocked` | Required access, approval, sensitive-data boundary, material conflict, or minimum source is missing. |
| `routed_to_next_stage` | A focused agent owns the next allowed action under the existing Pipe lifecycle. |

Re-running intake must supersede or update the prior baseline by stable product identity. It must not silently create an unrelated baseline for the same product.

## Common ProductBaseline Build

### Step 1: Establish the source boundary

Record:

- initiating user request and assigned Linear ticket
- entry mode
- product and repository identity
- approved source locations
- unavailable or intentionally omitted sources
- sensitivity of every source
- connector and access status

If a required source would expose secrets, private customer context, production data, or other absolute-gate material without approval, store only a pointer and return a blocker.

### Step 2: Inventory source artifacts

Map inspectable material to baseline artifacts such as:

- product context
- product requirement
- feature or epic
- ticket
- ADR or decision
- code artifact
- audit finding
- validation or research artifact
- learning record

An artifact record describes existence and provenance. It does not make the artifact accepted or current by default.

### Step 3: Classify material statements

For each stage-impacting or governance-impacting statement:

1. Link the source IDs.
2. Classify it as `fact`, `inference`, `assumption`, `conflict`, or `missing`.
3. State confidence and decision impact.
4. Set its disposition.
5. Mark human review when the statement affects stage, scope, claims, risk, or reconciliation.

Facts require at least one inspectable source. Inferences and assumptions must never be presented as facts in derived documents.

### Step 4: Detect the current lifecycle stage

Use `execution/core-pipeline-map.md` and distinguish:

- strategic stage: which gates and evidence actually exist
- implementation maturity: what code or operational delivery exists
- next allowed stage: the next action that is safe under current gaps

For `adopt`, these may differ. Example: code may show `ticket_execution` maturity while validation posture remains `unproven`. The baseline records both the stage rationale and the gap; it does not backfill a false GO decision.

### Step 5: Identify governance gaps

Create gaps only when they affect future decisions or operability. Classify severity with the existing P0-P3 model.

Typical gaps:

- missing or contradictory product context
- unsupported customer or market claims
- missing validation boundary
- absent or stale PRD/MVP scope
- architecture decision embedded only in code
- repository work not traceable to Linear
- Linear issue not traceable to code or PR
- missing review or delivery evidence
- unportable path, adapter, or capability installation
- unclear operating mode or approval state

Avoid documentation theater. Do not require artifacts that would not change a decision, risk, or handoff.

### Step 6: Build a reconciliation plan

The plan may target repository, Linear, or GitHub and may propose:

- `create`: a required record does not exist
- `update`: a confirmed record is stale or incomplete
- `link`: records exist but are not connected
- `ignore`: difference is intentional and documented
- `investigate`: match or authority is uncertain

Each action must include source artifact IDs, match strategy, confidence, stable idempotency key, approval requirement, expected effect, and status.

### Step 7: Review the convergence gate

A baseline may be accepted when:

- product identity and repository are confirmed
- at least one source was inspected
- material statements have provenance and classification
- current stage rationale is visible
- customer/demand evidence boundary is explicit
- P0/P1 conflicts and sensitive-data blockers are either resolved or recorded as blocking
- external mutations remain proposed unless authorized
- the next safe owner and command are explicit

It must be blocked when:

- product identity cannot be established
- required sources are inaccessible and no safe partial baseline is useful
- the task would require unapproved sensitive access
- a material conflict makes the next action unsafe
- the user asks the baseline to certify evidence it does not contain

## `/pipe:idea` Entry

### Accepted inputs

- brainstorm document
- current conversation summarized through `execution/guided-session-artifact.md`
- founder note or voice-transcript artifact approved for use
- source bundle with explicit provenance
- existing `product/product-context.md` draft

The raw source stays a source. The normalized baseline and IdeaBrief are derived outputs.

### Workflow

1. Capture the founder's goal and what they should not need to manage manually.
2. Select or confirm the solution path: market-facing, own-pain, or specific-person.
3. Extract target, problem, desired result, proposed mechanism, first channel, constraints, and unknowns.
4. Convert founder statements into facts only when supported by inspectable sources; otherwise record assumptions.
5. Record the strongest available evidence lane and the demand-validation boundary.
6. Produce `ProductBaseline` with `entryMode: idea`.
7. Route to `/pipe:discover`, or block/refine when the idea cannot yet be narrowed.

### Required outputs

- source manifest
- ProductBaseline
- IdeaBrief/product-context destination
- selected or unresolved solution path
- assumptions and unknowns
- next founder-facing question or `/pipe:discover` handoff

### Stop conditions

- the source contains sensitive/private material that has no approved capture boundary
- the user wants research, model synthesis, or brainstorm content treated as market proof
- multiple unrelated products cannot be separated safely
- implementation, outreach, billing, or production is requested before the relevant gate

## `/pipe:adopt` Entry

### Accepted inputs

- local repository path or approved GitHub repository reference
- approved Linear project or issue references
- product documentation and architecture notes
- Git history, release history, issues, and pull requests
- deployment metadata that contains no secret or production/customer data
- prior founder conversations as non-canonical source artifacts

### Default access posture

Adoption is read-only by default.

It may inspect approved local files and read external operational state through configured connectors. It must not:

- read or print secrets and credentials
- access customer or production data without explicit approval
- modify Linear, GitHub, repositories, deployments, or local runtime configuration during inventory
- infer validation from implementation
- rewrite Git history
- close, cancel, merge, or delete records

### Workflow

#### 1. Repository inventory

Inspect only the source classes relevant to the product:

- README, AGENTS/CLAUDE instructions, `.pipe/`, and product documentation
- source and configuration structure without revealing secret values
- tests, build configuration, package metadata, and architecture files
- Git branches, commit messages, tags, and release references
- explicit issue/PR/ADR/ticket identifiers
- capability and agent artifacts

Record omissions. A broad repository dump is not a baseline.

#### 2. Product reconstruction

Derive candidates for:

- current product promise and user
- implemented feature map
- active and obsolete requirements
- architecture and data boundaries
- decisions visible in code or history
- operating stage
- validation claims and their actual sources

Every derived candidate remains an inference until supported and reviewed.

#### 3. External execution inventory

When connectors are available and authorized, read:

- Linear project, active/backlog/done issues, dependencies, and handoffs
- GitHub issues, pull requests, review state, merge state, releases, and linked commits

Connector failure is recorded as `not_available` or `not_authorized`; it is not silently treated as empty external state.

#### 4. Relationship mapping

Match in this order:

1. explicit artifact link or identifier
2. stable external ID
3. Git branch, commit, or PR relationship
4. unique repository path plus corroborating source
5. semantic similarity as an `investigate` candidate only

Do not auto-apply semantic matches.

#### 5. Governance debt assessment

Compare the reconstructed state with the artifacts and gates needed for the next intended action, not with a theoretical requirement for perfect documentation.

Outputs may include:

- as-is Product Context or PRD candidate
- architecture inventory and ADR candidates
- unproven validation claims
- missing MVP/current-scope boundary
- unlinked implementation work
- documentation or portability gaps
- P0/P1 blockers and P2/P3 remediation

#### 6. Reconciliation proposal

Produce a human-readable summary and schema-shaped action list. No action is applied as part of `/pipe:adopt` unless a later approved execution explicitly includes mutation.

#### 7. Forward routing

Choose the smallest next action:

- `/pipe:discover` when product framing is missing or contradictory
- `/pipe:validate` when strategy is clear but evidence is absent or stale
- `/pipe:prd` when evidence permits requirements work and the as-is PRD needs consolidation
- `/pipe:plan` when product/validation scope is sufficient but architecture or ticket plan is missing
- `/pipe:build` only for an approved, ready ticket
- `/pipe:learn` when adoption only reveals reusable historical learning

### Required outputs

- ProductBaseline with `entryMode: adopt`
- as-is artifact inventory and relationships
- evidence/claim boundary
- governance gap report
- reconciliation plan
- proposed document updates
- next-stage handoff and stop conditions

### Stop conditions

- repository identity or ownership is uncertain
- required access would cross a secrets, customer-data, production-data, or sensitive-claim gate
- source history is being requested as invented customer validation
- reconciliation target cannot be confirmed
- P0/P1 conflict makes mapping or next-stage routing unsafe
- proposed changes exceed the assigned adoption ticket

## Linear And GitHub Reconciliation Contract

### Separation of read, plan, approval, and apply

| Phase | Allowed behavior | Output |
|---|---|---|
| Read | Fetch approved metadata and relationships. | Source records with access status and timestamps. |
| Plan | Match, classify differences, and propose actions. | `reconciliationPlan` entries in ProductBaseline. |
| Approval | Evaluate `.pipe/mode.json`, absolute gates, and action-specific approval. | `approved`, `blocked`, or unchanged `proposed` status. |
| Apply | Execute only approved actions through a dedicated adapter. | External reference, result, validation, and audit event. |
| Verify | Re-read target state and compare expected effect. | `applied`, `skipped`, or `blocked` with reason. |

### Idempotency

Recommended key shape:

```txt
<target-system>:<target-container>:<entity-type>:<source-artifact-id>:<action-version>
```

Before applying an action, the future adapter must check:

- whether the key already succeeded
- whether the target changed after planning
- whether source evidence changed
- whether approval is still valid
- whether a conflict or duplicate now exists

### Never automatic during adoption

- deletion or archival
- ticket closure or cancellation
- priority/status rewriting based only on inferred code state
- PR creation, merge, release, or deployment
- rewriting Git history
- customer communication
- sensitive claim changes
- linking a low-confidence semantic match as confirmed

## Agent Responsibilities

| Responsibility | Primary owner | Required handoff |
|---|---|---|
| Entry detection and founder conversation | Conversational Founder Guide | Entry mode, source boundary, user goal |
| Brainstorm structuring | Idea Intake Agent | Idea baseline and assumptions |
| Existing-product reconstruction | Architecture Agent | As-is inventory, technical facts/inferences, gaps |
| Evidence classification | Validation Agent | Evidence posture and validation gaps |
| Stage and scope decision | Product Strategist or MVP Scope Reviewer | Current stage, next allowed stage, blocked expansion |
| Risk and sensitive boundary | Risk Reviewer | Severity, blockers, mitigations, approval needs |
| Linear/GitHub action plan | Linear Steward with Ticket/Roadmap Orchestrator | Reconciliation plan; no mutation by default |
| Durable decision and learning | Knowledge Curator | ADR/KDR/DAR/LearningRecord candidate when warranted |
| UI capability routing | Atelier when a verified interface task exists | Design Brief, visual evidence, audit, LearningRecord |

No role is a master agent. The ProductBaseline is the handoff contract between focused owners.

## Event And Synchronization Model

Future runtime implementations may react to these events:

| Event | Trigger | Required result |
|---|---|---|
| `intake.requested` | Human starts `idea` or `adopt`. | Source boundary and ticket/approval context. |
| `source.discovered` | A repository, Linear, GitHub, or document source is found. | Source record with sensitivity and access status. |
| `baseline.drafted` | Minimum inventory is normalized. | Schema-valid ProductBaseline draft. |
| `baseline.review_required` | Material inference, conflict, stage decision, or mutation proposal exists. | Human/role review queue. |
| `baseline.accepted` | Convergence gate passes. | Next-stage route. |
| `reconciliation.proposed` | External differences are detected. | Idempotent plan; no mutation. |
| `reconciliation.approved` | Mode and human approval allow named actions. | Apply-ready actions only. |
| `reconciliation.applied` | Adapter changes target state. | Re-read verification and audit log. |
| `artifact.changed` | Repository/Linear/GitHub state changes after baseline. | Staleness flag and selective re-baseline. |

Runtime events are operational state. They do not replace the canonical artifacts they reference.

## Paper Walkthrough: Brainstorm

```txt
Founder conversation
-> safe Guided Session Artifact
-> /pipe:idea
-> ProductBaseline(entryMode=idea, currentStage=idea_intake)
-> product context / IdeaBrief
-> /pipe:discover
```

Expected boundary: founder statements are assumptions unless linked to evidence; the conversation is not customer proof.

## Paper Walkthrough: Existing Product

```txt
Existing repository + read-only Linear/GitHub state
-> /pipe:adopt
-> source and artifact inventory
-> facts/inferences/assumptions/conflicts/missing
-> ProductBaseline(entryMode=adopt)
-> governance gaps + reconciliation proposal
-> review
-> smallest safe existing Pipe command
```

Expected boundary: implementation can be confirmed while demand validation remains `unproven`.

## Definition Of Done For An Intake Run

An intake run is complete when:

- entry mode and product identity are explicit
- ProductBaseline validates against the canonical schema
- every material fact links to an inspected source
- evidence and historical-gate limitations are visible
- artifact relationships are traceable
- current stage and next allowed stage are distinct and justified
- governance gaps have severity, owner, and remediation
- reconciliation remains plan-first and idempotent
- approvals and stop conditions are recorded
- a future focused agent can continue without the original conversation

## Follow-Up Implementation Sequence

1. Repository-only baseline generator and fixtures.
2. Read-only repository and Git inventory.
3. Read-only Linear and GitHub adapters.
4. Product manifest plus bootstrap/doctor.
5. Reconciliation planner.
6. Approval-aware mutation adapters.
7. Persistent run/event/checkpoint layer and Hermes adapter.

Do not create these tickets automatically. Use the Roadmap Orchestrator to propose the next smallest ticket and request approval under the target repository mode.
