# Guided Session Artifact And Handoff

This document defines the durable artifact shape for a guided Pipe conversation.

Use it with:

- `execution/conversational-founder-guide.md`
- `.codex/agents/conversational-founder-guide-specialization.md`
- `.codex/agents/agent-handoff-protocol.md`
- `architecture/knowledge-runtime-architecture.md`
- `architecture/context-pack-builder-spec.md`
- `knowledge/venture-intelligence-memory-layer.md`
- `knowledge/learning-record-policy.md`
- `schemas/LearningRecord.schema.json`

This is a Markdown-first handoff contract. It does not implement storage, pgvector, Knowledge MCP, UI, database writes, autonomous memory promotion, or customer-data ingestion.

## Purpose

A guided session artifact lets future agents understand a founder conversation without relying on chat memory.

It records:

- user intent
- inferred pipeline stage
- stage rationale
- durable knowledge consulted
- capability route
- approval gates
- user-facing output
- blocked actions
- evidence gaps
- next owner or artifact
- reusable learning or follow-up candidates

The user should still experience a simple conversation. The artifact is for internal traceability, handoff, and future knowledge routing.

## When To Create

Create or update this artifact shape when:

- the conversation changes Pipe stage
- the agent asks a question that becomes important future context
- the user provides new product, validation, evidence, or decision context
- the session creates a blocker, approval need, or follow-up candidate
- the session hands off from the conversational front door to a focused agent
- the session should update KDR/DAR, LearningRecord, venture memory, customer-language memory, Linear, or a repository artifact

Do not create it for:

- trivial status answers
- small clarifying exchanges with no durable learning
- routine PR or Linear delivery already covered by `execution/ticket-pr-handoff-system.md`
- private or sensitive material that lacks approval for capture

## Storage Boundary

Until a future ticket approves concrete storage, the artifact may be captured as:

- a Linear comment
- a PR handoff note
- a repository Markdown artifact explicitly named by a ticket
- a KDR/DAR, LearningRecord candidate, or venture memory record when the session creates reusable knowledge

Do not create a new persistent session folder, database table, vector index, or external sync from this document alone.

## Artifact Template

Use this shape when a guided session needs durable handoff.

```md
# Guided Session Artifact - <short title or session id>

## Metadata

- Session date:
- Operating agent:
- User-facing mode: conversational founder guide
- Origin Linear ticket:
- Origin PR:
- Related branch:
- Related repository artifacts:
- Sensitivity: public-safe / internal / sensitive pointer only / blocked
- Capture location:

## User Goal

- User stated goal:
- Normalized goal:
- User constraints:
- What the user should not need to manage manually:

## Pipeline Route

- Inferred pipeline stage:
- Stage rationale:
- Earlier stages checked:
- Later-stage actions intentionally blocked:
- Next allowed stage:

## User-Facing Output

- Question asked or action proposed:
- Plain-language reason:
- Follow-up answer received:
- User-visible promise made:
- Claims explicitly not made:

## Durable Knowledge Checked

- Repository artifacts:
- Linear tickets or comments:
- GitHub PRs or reviews:
- KDR/DAR/ADR/RCA:
- LearningRecord candidates:
- Venture memory:
- Customer-language memory:
- Context pack:
- Omitted context and reason:

## Capability Route

- Need type:
- Candidate capabilities:
- Selected capability:
- Capability lifecycle and review state:
- Approval required:
- Data, cost, network, or mutation boundary:
- Fallback used:
- Capability output recorded:
- Blocked capabilities:

## Approval Gates

- Linear project or ticket creation:
- PR opening or merge:
- Customer outreach:
- External communication:
- Billing, pricing collection, paid ads, or paid acquisition:
- Production deployment:
- Secrets or credentials:
- Customer, production, private, or sensitive data:
- Legal, financial, compliance, privacy, security, or sensitive claims:
- Approval owner:
- Approval status:

## Evidence And Assumptions

- Evidence used:
- Assumptions still active:
- Evidence gaps:
- Synthetic or research output boundaries:
- Claims that must not be treated as evidence:

## Outputs And Next Artifacts

- Artifact updated:
- Artifact proposed:
- Linear follow-up candidate:
- KDR/DAR needed:
- LearningRecord candidate:
- Venture memory update:
- Customer-language memory update:
- No durable update reason:

## Handoff

- From:
- To:
- Next owner:
- Included scope:
- Excluded scope:
- Next recommended action:
- Done criteria for next owner:
- Stop conditions:

## Risks And Blockers

- P0/P1 risks:
- P2/P3 risks:
- Approval blockers:
- Privacy or sensitive-data blockers:
- Evidence blockers:
- Capability blockers:
- Residual risk:

## Validation Of Session Capture

- Source artifacts linked:
- User-facing response stayed conversational:
- Capability route recorded:
- Knowledge route recorded:
- Approval gates recorded:
- Sensitive data excluded or pointer-only:
- Future agent can continue without chat memory:
```

## Required Fields

Every guided session handoff must include:

- user goal
- inferred pipeline stage
- user-facing question or safe action
- durable knowledge checked or explicitly missing
- capability route or explicit no-capability route
- approval gates and blocked actions
- evidence gaps and assumptions
- next owner or next artifact
- sensitivity status

If any required field is unknown, write `unknown` and explain whether it is a blocker or a clarifying-question target.

## Safe Capture Rules

Do not store:

- names, emails, phone numbers, identifiers, raw interview notes, transcripts, recordings, screenshots, private messages, or confidential details without explicit approval
- secrets, credentials, tokens, private keys, production data, or customer data exports
- legal, financial, compliance, privacy, security, regulated, or sensitive claims not already approved as source material
- unsupported claims about customers, revenue, willingness to pay, integrations, validation, or metrics

When sensitive context matters, capture only:

- a pointer
- approval status
- retention status
- why the context matters
- blocker or next owner

## Handoff Destination Rules

Use the smallest destination that preserves continuity:

| Situation | Destination |
|---|---|
| Routine execution status | Linear delivery comment |
| Front-door conversation creates next-step context | Guided session artifact block in Linear or repository artifact named by ticket |
| Reusable strategic decision | KDR/DAR candidate |
| Reusable technical decision | ADR candidate |
| Reusable operational learning | LearningRecord candidate |
| Idea/persona/evidence/revisit relationship | Venture memory record candidate |
| Approved customer wording | Customer-language memory update |
| Sensitive/private context | Pointer-only blocker until approval |

Do not promote session notes into canonical rules automatically.

## Consumer Rules

Future agents should use this artifact to:

- continue the conversation without asking the user to repeat known context
- understand which stage was inferred and why
- see which capabilities were considered or blocked
- see which knowledge sources were checked or omitted
- respect approval gates and evidence boundaries
- choose the next focused agent or artifact

Future agents must not use this artifact to:

- override repository policy
- treat assumptions as evidence
- bypass validation gates
- create tickets, PRs, outreach, billing, production, or sensitive changes without approval
- promote learning into canonical rules without ticket, PR, review, and merge

## Done Criteria

This format is working when:

- a future agent can reconstruct the guided session route from durable sources
- the user-facing conversation stays simple
- internal stage, capability, knowledge, approval, and evidence boundaries are explicit
- sensitive material is excluded or pointer-only
- reusable learning has a clear candidate destination
- no future agent needs the original chat transcript to continue safely
