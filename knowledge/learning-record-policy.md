# Learning Record Policy

This policy defines when to create a `LearningRecord`, what it must contain, and how a learning candidate can be promoted into a canonical rule.

The canonical machine-readable contract is `schemas/LearningRecord.schema.json`.

This policy does not create a database, embeddings, automatic promotion, or a new `KNOWLEDGE.md` surface.

## Purpose

Use a LearningRecord when an execution, validation, review, incident, or capability usage produces a reusable lesson that should change how future agents work.

LearningRecords prevent important lessons from living only in chat history, PR comments, or one-off Linear handoffs.

## When A LearningRecord Is Required

Create or propose a LearningRecord when at least one condition is true:

- a failure or near miss changes future execution policy
- a recurring pattern appears across tickets, reviews, validations, or agent handoffs
- a capability, skill, MCP, prompt, or workflow produces reusable operating knowledge
- a validation or product learning changes future gate criteria, PRD assumptions, or MVP scope
- a review finding exposes a governance, quality, observability, security, or handoff gap that may recur
- a decision record, RCA, or delivery handoff contains a lesson that future agents should consume directly

Do not create a LearningRecord for:

- routine delivery summaries already captured in Linear
- isolated cosmetic review comments
- unvalidated product opinions
- customer claims without source artifacts
- sensitive or private data that has not passed human review
- lessons that do not change future execution

## Required Learning Fields

Every LearningRecord must identify:

- schema version, record ID, title, and learning type
- source: ticket, PR, artifact, review, validation result, incident, or manual observation
- scope: domains, agents, ticket types, horizon, and limits
- agent: recorder, role, and intended consumers
- capability: related skill, MCP, workflow, prompt, schema, tool, or manual process
- confidence: level, score, and rationale
- importance: level, score, and rationale
- tags: searchable lowercase tags
- summary: factual lesson
- insight: why it matters
- evidence: at least one source artifact
- recommendation: what should happen next
- promotion: state, target artifact, human review requirement, human review status, automatic-promotion flag, and rationale
- sensitivity: customer-evidence flag, sensitive-data flag, redaction flag, human review status, and notes

## Learning Types

Use the smallest accurate type:

| Type | Use When |
|---|---|
| `execution_learning` | A ticket or PR changes future execution behavior. |
| `failure` | A defect, regression, incident, or missed gate explains what failed. |
| `recurring_pattern` | A repeated signal appears across multiple tickets or reviews. |
| `capability_usage` | A skill, MCP, prompt, schema, or workflow produces reusable guidance. |
| `decision_learning` | A decision record produces a lesson beyond the decision itself. |
| `validation_learning` | Research, discovery, or validation changes future gates or assumptions. |
| `customer_learning` | Sourced customer evidence changes product or validation direction. |
| `risk_learning` | A risk review or mitigation changes future safeguards. |

## Promotion States

LearningRecords are not automatically canonical rules.

| State | Meaning |
|---|---|
| `candidate` | Captured for possible reuse; not yet proposed as a rule. |
| `proposed` | Proposed for promotion into a canonical artifact. |
| `approved_for_promotion` | Human approved promotion, but the target artifact is not updated yet. |
| `promoted` | Target canonical artifact was updated via ticket and PR. |
| `rejected` | Human or owner rejected promotion. |
| `parked` | Useful later, not actionable now. |
| `superseded` | Replaced by a newer learning or decision. |

Promotion to a canonical rule always requires human review. Automatic promotion is not allowed.

`proposed`, `approved_for_promotion`, and `promoted` records must name a concrete target canonical artifact. `approved_for_promotion` and `promoted` records must also have `humanReviewStatus: approved`.

## Promotion Targets

Valid target artifacts include:

- `AGENTS.md`
- `execution/*.md`
- `knowledge/*.md`
- `architecture/*.md`
- `schemas/*.schema.json`
- `.codex/agents/*`
- `CLAUDE.md`
- `.agents/skills/*`
- `templates/*`

If the target is unclear, keep the record as `candidate` and create a follow-up ticket only when the impact is concrete.

## Modeling KDR-002 And RCA-001 As Learning Candidates

PIP-150 uses KDR-002 and RCA-001 as modeling examples without changing those source artifacts.

### KDR-002 Candidate

- Source: `knowledge/kdr-002-restore-pr-flow.md`
- Learning type: `decision_learning`
- Summary: PR and review enforcement is a governance requirement for future merges to `main`.
- Insight: Multi-agent execution needs a durable PR review gate, not only local convention.
- Possible target artifact: `execution/ticket-pr-handoff-system.md`
- Promotion state: already reflected by current governance, so a new LearningRecord would likely be `candidate` or `promoted` depending on whether the repository later stores concrete records.

### RCA-001 Candidate

- Source: `knowledge/rca-001-pr-flow-regression-root-cause.md`
- Learning type: `failure`
- Summary: A PR review object can exist even when no substantive review happened because Copilot errored.
- Insight: Agents need to classify review quality, not only review existence.
- Possible target artifact: `execution/ticket-pr-handoff-system.md`
- Promotion state: `candidate` until a ticket explicitly updates the review policy.

## Relationship To Existing Knowledge Workflow

Use this policy with:

- `knowledge/knowledge-curator-workflow.md`
- `knowledge/kdr-dar-template.md`
- `knowledge/decision-conflict-protocol.md`
- `architecture/canonical-schema-policy.md`
- `schemas/LearningRecord.schema.json`

The knowledge curator workflow decides whether a knowledge update is useful. The LearningRecord schema defines the normalized structure when the answer is yes.

## Human Review And Sensitive Data

Human review is required before a LearningRecord:

- promotes a lesson into a canonical rule
- stores customer evidence
- stores sensitive, regulated, confidential, or private operational data
- changes execution policy, approval gates, security posture, product claims, legal/compliance text, or customer-facing claims

Schema-valid records that contain customer evidence or sensitive data must set `sensitivity.redactionRequired: true` and `sensitivity.humanReviewStatus: approved`.

LearningRecords must not invent customer evidence, metrics, revenue, integrations, or validation results.

## Validation Expectations

A LearningRecord schema change should be validated by:

- JSON syntax validation
- schema policy alignment check
- example modeling against at least one real KDR/RCA, without mutating source records
- review for sensitive-data and unsupported-claim risk

Runtime validation, CI enforcement, persistence, embeddings, and retrieval are out of scope until a dedicated ticket approves them.
