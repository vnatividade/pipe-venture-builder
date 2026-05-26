# Knowledge Runtime Architecture

## Purpose

This document defines the first architecture boundary for the Pipe Knowledge Runtime.

The central decision is:

- Markdown repository artifacts are the canonical memory.
- Linear and GitHub are the canonical execution state and delivery evidence surfaces.
- pgvector, embeddings, and future retrieval services are recall infrastructure, not the source of truth.

This architecture prepares future context-pack, pgvector, and Knowledge MCP work without implementing a database, Docker Compose, embeddings, or MCP server in this ticket.

## Non-Goals

This document does not:

- implement Postgres, pgvector, embeddings, or vector search
- define Docker Compose or local runtime infrastructure
- implement a Knowledge MCP
- create automatic memory promotion
- replace `knowledge/learning-record-policy.md`
- replace Linear handoffs or GitHub PR history

## Source Of Truth Boundaries

| Layer | Role | Canonical? | Examples | Notes |
|---|---|---:|---|---|
| Repository Markdown | Durable product, architecture, governance, validation, and knowledge memory | Yes | `knowledge/*.md`, `architecture/*.md`, `execution/*.md`, `validation/*.md`, `product/*.md` | This is the primary canonical memory for future agents. |
| Repository schemas | Machine-readable contracts for canonical record shapes | Yes | `schemas/LearningRecord.schema.json`, `schemas/DeliveryEvidence.schema.json` | Schemas define valid structure, not persistence. |
| Linear | Execution state, priority, blockers, ownership, ticket handoff | Yes for execution | Issue status, comments, labels, links, delivery updates | Linear is not a replacement for durable repository decisions. |
| GitHub | Delivery evidence, PR discussion, review state, merge history | Yes for delivery | PR body, review comments, merge commit, branch links | PR history proves what changed and how it was reviewed. |
| pgvector / retrieval index | Semantic recall and context discovery | No | Embedded records, source pointers, search metadata | It must point back to canonical artifacts. It must not become hidden memory. |
| Agent conversation memory | Short-lived local context | No | Current chat state, temporary notes | Future agents must not need this to continue execution. |

## Memory Classes

### Canonical Memory

Canonical memory is durable, reviewed, source-linked, and safe for future agents to rely on.

Canonical memory belongs in repository artifacts or approved execution systems:

- decisions and decision conflicts in `knowledge/`
- architecture boundaries and technical decisions in `architecture/`
- execution rules and operating protocols in `execution/`
- validation artifacts and evidence policy in `validation/`
- product strategy and PRD surfaces in `product/`
- schemas in `schemas/`
- ticket execution state and handoff in Linear
- PR delivery evidence and review history in GitHub

### Recoverable Memory

Recoverable memory helps agents find relevant canonical artifacts faster.

Recoverable memory can include:

- embeddings of approved repository artifacts
- indexes over Linear handoffs and PR summaries
- keyword/path metadata
- capability metadata
- source pointers and freshness timestamps

Recoverable memory must never become the only place where a decision, rule, customer claim, approval, validation result, or execution dependency exists.

### Operational State

Operational state is the current execution truth:

- assigned Linear ticket
- ticket status, priority, dependencies, and blockers
- active branch
- PR review and merge state
- validation evidence for the current delivery

Operational state can be indexed for retrieval, but the active system of record remains Linear and GitHub.

### Conversational Memory

Conversational memory is useful for the current session only.

It can guide immediate execution, but any decision future agents need must be promoted into Linear, GitHub, or repository artifacts.

## Record Types

The Knowledge Runtime should recognize these record types before any storage implementation exists.

| Record type | Purpose | Canonical home | Retrieval home | Promotion target examples |
|---|---|---|---|---|
| `learning` | Reusable lesson from execution, validation, review, incident, or capability use | `schemas/LearningRecord.schema.json`, `knowledge/learning-record-policy.md`, future concrete learning records | future retrieval index | `execution/*.md`, `knowledge/*.md`, `architecture/*.md`, schemas |
| `decision` | Accepted, rejected, superseded, or pending decision with rationale | `knowledge/kdr-dar-template.md`, concrete KDR/DAR files, `architecture/adr/` | future retrieval index | architecture docs, governance docs, product docs |
| `capability` | Skill, MCP, workflow, agent, or external tool metadata | `capabilities/`, `architecture/capability-registry-policy.md` | future retrieval index | capability registry entries, adapter contracts |
| `idea` | Venture idea, thesis, validation status, assumptions, and scope | `product/`, `validation/`, future idea-intake artifacts | future retrieval index | PRD, validation plan, MVP scope |
| `run` | Ticket execution, validation, PR, review, and merge handoff | Linear ticket, GitHub PR, optional `DeliveryEvidence` | future retrieval index | Linear delivery update, PR body, DeliveryEvidence |
| `failure` | Incident, RCA, regression, near miss, or failed gate | `knowledge/*rca*.md`, LearningRecord candidate, PR/Linear evidence | future retrieval index | execution rules, review policy, validation gates |
| `pattern` | Recurring signal across tickets, reviews, validations, users, or capabilities | LearningRecord candidate, knowledge synthesis, strategy docs | future retrieval index | policy, template, scoring model, capability guidance |

## Promotion Levels

Promotion must be explicit. Higher levels require stronger evidence and more human review.

| Level | Name | Meaning | Human approval required? | Example |
|---|---|---|---:|---|
| L0 | Observation | A raw note, comment, PR finding, or execution fact exists. | No, unless sensitive | A PR comment notes a recurring handoff gap. |
| L1 | Candidate | A reusable lesson is proposed but not yet trusted as a rule. | No for capture; yes if sensitive | A LearningRecord candidate from an RCA. |
| L2 | Validated Learning | Evidence supports reuse across future work, but no canonical rule has changed yet. | Usually yes when it affects process | A failure pattern confirmed across multiple PRs. |
| L3 | Canonical Repository Memory | A repository artifact was updated through ticket, PR, and review. | Yes through the normal PR/review gate | `knowledge/learning-record-policy.md` or `execution/*.md` updated. |
| L4 | Canonical Rule / Gate | A future agent must obey the promoted rule or gate. | Always | Approval gates, merge rules, sensitive-data rules, validation gates. |

Canonical rule promotion always requires human approval. Automatic promotion to L3 or L4 is not allowed.

This aligns with `schemas/LearningRecord.schema.json`, where `humanReviewRequiredForPromotion` is always `true` and `automaticPromotionAllowed` is always `false`.

## Promotion Loop

Use this loop until a dedicated Knowledge Runtime exists:

1. Capture the source artifact.
   - Examples: Linear ticket, PR, KDR, RCA, validation artifact, review finding, capability run.
2. Classify the record.
   - Use the smallest accurate type: learning, decision, capability, idea, run, failure, or pattern.
3. Decide whether it is reusable.
   - If it is routine delivery, keep it in Linear/PR handoff only.
   - If future agents need it, propose a LearningRecord or update the relevant canonical artifact through a ticket.
4. Keep evidence attached.
   - Every promoted record needs source paths, PR links, ticket links, or validation artifacts.
5. Promote only through ticket and PR.
   - Promotion into canonical repository memory requires scoped implementation, validation, review, and merge.
6. Require human approval for canonical rules.
   - Approval gates, execution rules, sensitive claims, product claims, privacy/security posture, and customer-evidence handling cannot be promoted automatically.
7. Index after promotion.
   - Future pgvector or retrieval indexes should ingest promoted artifacts and keep pointers back to source files.
8. Revisit and supersede when needed.
   - Use KDR/DAR supersession and conflict protocols rather than silently overwriting memory.

## Hybrid Retrieval Model

Future retrieval should combine:

- exact path and file-name matching
- repository keyword search
- record metadata filters
- Linear issue IDs and labels
- GitHub PR numbers and merge refs
- capability names and maturity
- vector similarity over approved canonical artifacts

The retrieval output should return a context pack with:

- source artifact path or URL
- record type
- confidence and freshness
- promotion level
- sensitivity status
- known supersession or conflict notes
- reason the artifact was selected

Retrieval must prefer small, source-linked context over broad prompt stuffing.

## Mapping Examples

These mappings validate the proposed record model against existing artifacts without changing them.

| Source | Record type | Canonical source | Why it fits | Promotion status |
|---|---|---|---|---|
| KDR-002 | `decision`, `learning` | `knowledge/kdr-002-restore-pr-flow.md` | It records an accepted governance decision and a reusable lesson about PR/review enforcement. | Already accepted as a KDR; any LearningRecord representation should point to the KDR rather than duplicate it as hidden memory. |
| RCA-001 | `failure`, `learning` | `knowledge/rca-001-pr-flow-regression-root-cause.md` | It explains the actual review-gate failure mode and refines KDR-002 evidence without superseding the decision. | Candidate until a ticket explicitly promotes review-quality classification into execution policy. |
| Recent Linear handoffs | `run`, sometimes `learning` | Linear delivery comments and GitHub PRs | They preserve branch, PR, merge, validation, findings, follow-ups, and residual risk for each ticket. | Routine handoffs stay operational; reusable lessons should become LearningRecord candidates. |
| Capability Registry entries | `capability` | `capabilities/entries/*.json` | They describe tool/agent capability metadata that future routing can retrieve. | Canonical once schema-valid and merged. |
| DeliveryEvidence schema usage | `run`, `learning` | `schemas/DeliveryEvidence.schema.json`, PR bodies, Linear updates | It normalizes proof that a delivery was validated. | Canonical schema exists; concrete records are ticket-dependent. |

## Relationship To Existing Artifacts

Use this architecture with:

- `knowledge/learning-record-policy.md`
- `schemas/LearningRecord.schema.json`
- `schemas/DeliveryEvidence.schema.json`
- `architecture/canonical-schema-policy.md`
- `architecture/capability-registry-policy.md`
- `architecture/capability-adapter-contract.md`
- `execution/pipe-check-command-spec.md`
- `execution/context-routing-protocol.md`
- `execution/multi-agent-operating-protocol.md`
- `knowledge/decision-conflict-protocol.md`

This document provides the runtime boundary. The existing files provide the schema, promotion, conflict, capability, and execution rules.

## Human Approval Rules

Human approval is required before:

- promoting any learning into a canonical rule or gate
- changing approval gates
- changing PR/review/merge policy
- storing customer evidence, private data, regulated data, secrets, or sensitive operational data
- changing legal, financial, compliance, privacy, security, or customer-facing claims
- converting a retrieval result into a repository rule
- letting a future orchestrator promote memory autonomously

If approval is missing, keep the record at L0, L1, or L2 and create a follow-up ticket when the impact is concrete.

## Validation Expectations

A future implementation ticket should validate this architecture by checking:

- every retrieved item points back to a canonical source
- `LearningRecord` candidates cannot auto-promote
- pgvector retrieval can be rebuilt from canonical sources
- sensitive records are excluded or redacted before indexing
- context packs distinguish canonical rules from candidate learnings
- Linear/GitHub operational state remains linked to repo artifacts

For this architecture-only ticket, validation is limited to:

- confirming KDR-002 and RCA-001 map cleanly into the record taxonomy
- confirming recent Linear handoffs map to the `run` record type
- confirming no database, Docker, embeddings, or MCP implementation is introduced

## Future Ticket Hooks

This architecture intentionally sets up later work:

- Context Pack Builder contract: define how retrieval output is packaged for agents.
- Local pgvector spike: prove recall value without changing canonical memory.
- Knowledge MCP spec: expose approved retrieval surfaces without direct database coupling.
- LearningRecord concrete storage: decide whether records live as Markdown, JSON, or both.
- Promotion workflow automation: assist capture and validation while keeping human approval for canonical rules.

## Operating Rule

If an agent cannot answer "where is the canonical source for this memory?", the memory is not canonical and must not be treated as a rule.
