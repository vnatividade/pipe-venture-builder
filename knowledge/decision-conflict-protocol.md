# Decision Conflict And Supersession Protocol

Use this protocol when a new strategic decision may contradict, narrow, replace, or reactivate a prior KDR/DAR.

It prevents silent drift. It does not automatically rewrite old decisions.

## When To Run

Run a conflict scan before accepting a KDR/DAR that changes:

- product strategy, ICP, offer, channel, pricing, or growth posture
- validation path, evidence threshold, GO / NO-GO status, or MVP scope
- architecture direction, data boundary, integration posture, or technical constraint
- risk acceptance, approval gate, privacy/security stance, or operational policy
- agent, skill, Linear, GitHub, or knowledge governance

Do not run this protocol for trivial edits, typo fixes, routine handoffs, or decisions that do not affect future execution.

## Conflict Scan

Before marking a new KDR/DAR as accepted:

1. Search existing KDR/DAR records, decision logs, ADRs, MVP scope, risk review, PRD, and relevant validation artifacts.
2. Identify active decisions with overlapping topic, phase, artifact, assumption, evidence, or risk.
3. Compare the new decision against each active decision.
4. Classify the relationship.
5. Update the new KDR/DAR conflict fields.
6. Add supersession links when the new decision replaces or narrows a prior decision.
7. Escalate unresolved or high-risk conflicts before merge or execution.

Suggested repository searches:

```txt
rg -n "KDR-|DAR-|Status: Accepted|Supersedes|Superseded by|Conflict status" knowledge product validation architecture execution
rg -n "<decision topic or key assumption>" knowledge product validation architecture execution
```

## Relationship Types

| Relationship | Meaning | Required action |
|---|---|---|
| No conflict | New decision does not change an active prior decision. | Set conflict status to `None`. |
| Clarifies | New decision explains or narrows a prior decision without changing intent. | Link the prior decision in context or evidence. |
| Supersedes | New decision replaces a prior active decision. | Set `Supersedes`, update or propose update to prior record as `Superseded`, and explain what changed. |
| Partial supersession | New decision replaces part of a prior decision. | Link both records and state the still-active part. |
| Potential conflict | Evidence is incomplete or scope overlap is unclear. | Set conflict status to `Potential conflict` and create or link the follow-up needed. |
| Conflict unresolved | New decision contradicts a prior active decision and cannot be resolved inside the ticket. | Set conflict status to `Conflict unresolved`, stop high-risk execution, and require human review. |

## Authority Hierarchy

When decisions conflict, use this hierarchy to decide what can override what:

1. System, developer, and current human instructions.
2. Repository approval gates and `AGENTS.md`.
3. Assigned Linear ticket scope and acceptance criteria.
4. Approved source artifacts in the current pipeline phase.
5. Prior accepted KDR/DAR records and ADRs.
6. Repository documentation and templates.
7. Conversation memory.

Conversation memory cannot supersede repository artifacts by itself. If a human decision changes strategy, capture it in a KDR/DAR or the relevant source artifact before future agents rely on it.

## Supersession Markers

Use these fields in the KDR/DAR record:

```md
## Conflict Scan

- Prior decisions checked:
- Relationship: No conflict / Clarifies / Supersedes / Partial supersession / Potential conflict / Conflict unresolved
- Conflict summary:
- Authority used:
- Human review needed: yes/no

## Supersession

- Supersedes:
- Superseded by:
- Conflict status: None / Potential conflict / Conflict unresolved
```

When a decision is superseded, the old record should eventually show:

- `Status: Superseded`
- `Superseded by: <new KDR/DAR id or artifact link>`
- the reason the prior decision is no longer active

If the current ticket cannot safely update the old record, create a follow-up ticket and mark the new decision as `Potential conflict` or `Conflict unresolved`.

## Escalation Rules

Escalate before merge or execution when:

- the conflict touches approval gates, sensitive claims, customer data, production data, billing, paid acquisition, external communication, legal, financial, compliance, privacy, or security posture
- the prior and new decisions would guide agents to incompatible next actions
- the conflict changes a GO / NO-GO, MVP scope, risk acceptance, architecture boundary, or customer evidence interpretation
- the risk reviewer would classify the conflict as P0 or P1

High-risk conflicts must not be resolved without human review.

## Risk Reviewer Handoff

Ask the risk reviewer to classify the conflict when:

- reversibility is unclear
- the conflict may create unsafe execution
- impact could be medium or high
- approval status is ambiguous

Use `execution/risk-reviewer-matrix-lite.md` for severity and blocker status. If the result is P0 or P1, treat the current ticket as blocked until the conflict is mitigated, explicitly accepted, or moved into a scoped follow-up with human approval.

## Done Criteria

A strategic decision is conflict-ready when:

- prior KDR/DAR and related source artifacts were checked
- relationship type is recorded
- superseded decisions are linked when applicable
- unresolved conflicts have an owner, escalation path, and follow-up ticket when needed
- high-risk conflicts have human review before execution
- no old decision remains silently active when it has been replaced
