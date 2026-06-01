# Venture Intelligence Memory Layer

This design defines a Markdown-first memory layer for relating ideas, signals, personas, geographies, evidence, scores, KDR/DAR decisions, and revisit triggers.

It is a data design and operating contract. It does not implement a database, pgvector index, external sync, live ingestion, scraping, connector automation, or autonomous roadmap updates.

## Purpose

Venture intelligence memory should help future agents answer:

- what ideas have been evaluated
- which evidence supports or weakens each idea
- which personas, geographies, and channels are connected to each idea
- which ranking or validation scores changed and why
- which KDR/DAR decisions constrain future recommendations
- when an idea, signal, score, or decision should be revisited

The memory layer should make accumulated context useful without letting weak signals or synthetic outputs drive execution.

## Boundary

This layer does not authorize:

- storing sensitive, identifiable, private, regulated, confidential, production, or raw customer data
- storing exact customer quotes unless approved by `validation/customer-data-retention-policy.md`
- live scraping, market monitoring, connector sync, pgvector implementation, or external database writes
- automatic ranking changes, roadmap changes, PRD/MVP changes, ticket creation, or build prioritization
- treating market signals, synthetic personas, or AI summaries as customer evidence
- replacing KDR/DAR records, validation scorecards, or source artifacts

Privacy/security review is required before implementing this as a database, vector store, MCP, connector, scheduled job, or external sync.

## Source Artifacts

Use this design with:

- `knowledge/kdr-dar-template.md`
- `knowledge/decision-conflict-protocol.md`
- `knowledge/knowledge-curator-workflow.md`
- `research/idea-ranking-engine-design.md`
- `research/market-signal-ingestion-template.md`
- `research/evidence-scoring-system.md`
- `research/source-quality-and-citation-rules.md`
- `validation/validation-scorecard.md`
- `validation/persona-ranking-rubric.md`
- `validation/geography-ranking-rubric.md`
- `validation/synthetic-persona-schema.md`
- `validation/synthetic-vs-real-interview-comparison-template.md`

## Memory Entity Model

### Core Entities

| Entity | Purpose | Canonical source | Required fields |
|---|---|---|---|
| Idea | The venture or product hypothesis being tracked. | Founder focus, C.O.N.T.R.O.L.E., product context, ranking batch. | ID, title, problem, ICP, C.O.N.T.R.O.L.E. verdict, status, owner, source artifacts. |
| Signal | External or internal signal that may affect the idea. | Market signal ingestion template, research synthesis, interview synthesis. | Signal ID, source, date, type, persona, geography, confidence, limitation, routing decision. |
| Persona | Target user/buyer hypothesis or evidence-backed segment. | ICP profile, persona rubric, interviews, synthetic persona schema. | Persona ID, source basis, segment, JTBD, evidence type, confidence, forbidden uses. |
| Geography | Country, city, region, or local-market context. | Geography ranking rubric, market research, signal ingestion. | Geography ID, source, maturity, regulation/trust notes, channel context, confidence. |
| Evidence | Traceable proof, observation, research, or assumption affecting an idea. | Evidence scoring system, validation scorecard, raw interview synthesis, research synthesis. | Evidence ID, type, source, date, strength, directness, confidence, limitation, affected claim. |
| Score | Advisory ranking or validation score. | Idea ranking engine, validation scorecard, persona/geography rubrics. | Score ID, score type, dimensions, confidence, sources, risk if wrong, approval status. |
| Decision | KDR/DAR, gate decision, or accepted strategic constraint. | KDR/DAR template, decision conflict protocol, Linear handoff. | Decision ID, status, rationale, evidence, risks, supersession, revisit trigger. |
| Revisit Trigger | Event or condition that should reopen a memory record. | KDR/DAR, ranking, research, validation, PR handoff. | Trigger ID, condition, owner, source, deadline or phase, action when triggered. |

### Relationship Types

| Relationship | Meaning | Example |
|---|---|---|
| `idea_has_signal` | Signal may affect an idea. | Idea A has signal S-001 about competitor pricing. |
| `idea_targets_persona` | Idea is aimed at a persona. | Idea A targets persona P-Driver-01. |
| `idea_has_geography` | Idea is evaluated in a geography. | Idea A has geography G-Florianopolis. |
| `evidence_supports_claim` | Evidence supports a specific claim. | Interview synthesis supports problem urgency. |
| `evidence_contradicts_claim` | Evidence weakens or contradicts a claim. | Market signal contradicts channel assumption. |
| `score_uses_evidence` | Score depends on evidence. | Ranking score uses E-003 and E-004. |
| `decision_constrains_idea` | KDR/DAR limits future action. | KDR says keep MVP manual before automation. |
| `trigger_reopens_record` | Revisit trigger applies to an entity. | New interviews reopen persona confidence. |
| `synthetic_requires_real_test` | Synthetic output created a real validation need. | Synthetic objection maps to interview question. |

## Memory Record Template

```md
# Venture Memory Record - <ID>

## Metadata

- Memory ID:
- Entity type: Idea / Signal / Persona / Geography / Evidence / Score / Decision / Revisit Trigger
- Origin ticket:
- Origin PR or artifact:
- Owner:
- Created:
- Last reviewed:
- Status: Candidate / Active / Superseded / Rejected / Blocked
- Sensitivity: Public-safe / Internal / Sensitive pointer only / Blocked

## Summary

- What this record captures:
- Why it matters:
- What future agents should do with it:

## Source Basis

| Source artifact | Source type | Date or access date | Confidence | Limitation |
|---|---|---|---|---|
|  | customer / research / market signal / validation / ranking / KDR-DAR / synthetic / assumption |  | Low / Medium / High |  |

## Relationships

| Relationship | Target ID or artifact | Rationale | Confidence |
|---|---|---|---|
| idea_has_signal / evidence_supports_claim / evidence_contradicts_claim / score_uses_evidence / decision_constrains_idea / trigger_reopens_record / synthetic_requires_real_test |  |  | Low / Medium / High |

## Decision And Score Impact

- Affected ranking dimension:
- Affected validation score:
- Affected KDR/DAR:
- Confidence change: Increase / Decrease / No change / Unknown
- Human review required before priority change: yes

## Privacy And Safety

- Contains customer-derived material: yes/no
- Contains sensitive or identifiable data: yes/no
- Retention policy followed: yes/no/not applicable
- Raw data stored: no
- Sensitive details stored as pointer only:
- Approval or blocker:

## Revisit Trigger

- Revisit when:
- Trigger source:
- Owner:
- Suggested action:
- Do not use after:

## Forbidden Uses

- Do not treat as customer evidence unless source type is real customer evidence.
- Do not use synthetic output as validation evidence.
- Do not change roadmap, PRD, MVP, build, pricing, launch, or outreach priority without human review.
- Do not use sensitive pointers without approval.
```

## Update Triggers

Create or update a memory record when:

- a new idea passes C.O.N.T.R.O.L.E. into validation planning
- market signal ingestion routes a signal to ranking or research synthesis
- persona or geography ranking changes with source-backed rationale
- validation scorecard changes because real evidence changed
- synthetic persona output creates a real-world validation question
- a synthetic-vs-real comparison finds a material miss or contradiction
- a KDR/DAR is accepted, superseded, or creates a revisit trigger
- a merged PR changes a durable workflow, evidence boundary, or decision rule

Do not update memory for:

- routine PR handoffs with no reusable learning
- unsupported synthetic enthusiasm
- weak market noise that was rejected
- unreviewed private notes
- signals without source/date/persona/geography context
- cosmetic or mechanical documentation changes

## Retrieval Rules

When a future agent evaluates an idea, ranking, validation plan, or decision, retrieve:

1. active Idea records for the same problem, ICP, or workflow
2. Evidence records linked to the same claim or score dimension
3. Persona and Geography records linked to the idea
4. Signals routed to ranking or research synthesis
5. Decisions that constrain the idea, including supersession status
6. Revisit triggers that are due, stale, or activated by new evidence
7. Synthetic records only as hypothesis context, never as validation evidence

Retrieval output must separate:

- customer evidence
- research or market signal evidence
- validated score updates
- assumptions
- synthetic hypotheses
- stale or superseded decisions
- blocked sensitive pointers

## Privacy And Security Boundaries

Allowed in repository:

- anonymized synthesis
- source links and non-sensitive summaries
- confidence, limitation, and risk notes
- pointers to approved private storage without copying sensitive content
- synthetic hypotheses clearly marked as synthetic

Not allowed in repository without explicit approval:

- names, emails, phone numbers, addresses, personal identifiers
- recordings, transcripts, raw interview notes, exact quotes, screenshots of private conversations
- confidential business details
- credentials, tokens, secrets, production data, customer data exports
- legal, financial, health, compliance, or regulated personal data

If a record needs sensitive material, store only:

- a pointer
- approval status
- retention status
- reason the sensitive material is needed
- blocker if approval is missing

## Implementation Readiness Gate

Before turning this design into a database, vector index, MCP, connector, scheduled job, or external sync, require:

- privacy/security review
- data classification for every entity
- deletion and retention policy
- access control decision
- migration and rollback plan
- test plan for no sensitive data leakage
- human approval for external tools or data movement

Until that exists, this layer remains Markdown-first.

## Done Criteria

This design is complete when:

- ideas, signals, personas, geographies, evidence, scores, decisions, and revisit triggers are modeled
- relationships connect evidence to decisions and revisit triggers
- update triggers and retrieval rules are explicit
- privacy boundaries prevent sensitive data storage by default
- synthetic outputs are hypothesis-only and require real-world tests
- database implementation and external sync remain out of scope
