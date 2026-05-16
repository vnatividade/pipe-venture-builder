# Research Synthesis Template

Use this template to convert reviewed research into a decision-ready synthesis that changes an assumption, validation plan, PRD/MVP scope, KDR/DAR, backlog item, or next test.

Use it with `research/research-orchestrator-workflow.md`, `research/source-quality-and-citation-rules.md`, `research/evidence-scoring-system.md`, `validation/validation-scorecard.md`, `knowledge/kdr-dar-template.md`, and `execution/approval-gates.md`.

## Boundary

This template is for concise synthesis, not a long literature review by default.

It does not approve strategic changes, validate demand, create public claims, replace customer discovery, replace expert review, or authorize implementation tickets. Human review is required before strategic changes, PRD/MVP changes, ranking use, sensitive claims, growth, monetization, or build prioritization.

If the synthesis has no decision implication, do not create it. Keep the raw notes in the source log or record that no reusable synthesis was produced.

## When To Use

Use this template when research should affect:

- validation questions or scorecard interpretation
- PRD, MVP scope, or risk review inputs
- KDR/DAR creation or update
- backlog prioritization or follow-up tickets
- customer discovery plan
- market, scientific, or source-quality confidence
- an assumption that future agents might otherwise reuse incorrectly

Do not use it when:

- sources are unreviewed or untraceable
- there is no clear decision question
- the result is only a collection of links
- the output would create unsupported customer, market, scientific, legal, financial, compliance, privacy, security, or regulated claims

## Required Inputs

- origin Linear ticket
- research owner
- decision question
- product phase
- source log or cited source IDs
- evidence score, when available
- relevant validation, PRD, MVP, KDR/DAR, or backlog artifact
- approval state
- intended decision owner

## Template

```md
# Research Synthesis - <decision question>

## Metadata

- Origin ticket:
- Research owner:
- Date:
- Product phase:
- Decision owner:
- Approval state:
- Human review required before decision use: yes/no

## Decision Question

- Question:
- Why this question matters:
- Decision or artifact this informs:
- What would change the decision:
- What evidence would be insufficient:

## Source Summary

| Source ID | Source | Type | Date | Freshness | Confidence | Risk if wrong | Limitation |
|---|---|---|---|---|---|---|---|
| S-001 |  |  |  | Current / Dated / Stale / Unknown | Low / Medium / High | Low / Medium / High |  |

## Evidence Score Summary

- Strongest evidence lane:
- Customer evidence present: yes/no
- Advisory evidence score, if used:
- Score limitation:
- Contradictions or conflicts:
- Confidence:
- What this does not prove:

## Findings

- Strongest supporting finding:
- Strongest contradicting finding:
- Open assumption:
- Source-quality concern:
- Risk if wrong:

## What Changed

- Assumption changed:
- Confidence changed: Increased / Decreased / Unchanged
- Validation changed:
- PRD or MVP scope changed:
- KDR/DAR needed: yes/no
- Backlog changed:

## Decision Implication

- Recommended interpretation:
- Decision impact: Validation / PRD / MVP / KDR-DAR / Backlog / No change
- Human review required: yes/no
- Strategic change blocked until review: yes/no
- Sensitive claim or regulated-risk flag: yes/no
- If no decision implication, stop and do not use this synthesis:

## Next Test Or Action

- Next test:
- Owner:
- Target artifact:
- Linear follow-up needed: yes/no
- Follow-up title, if needed:
- Done condition:

## Handoff

- Update validation scorecard: yes/no
- Update PRD or MVP scope: yes/no
- Create or update KDR/DAR: yes/no
- Create or update backlog item: yes/no
- Update knowledge artifact: yes/no
- Risk reviewer needed: yes/no
```

## Decision Impact Rules

Every completed synthesis must produce at least one of:

- a validation scorecard update or blocker
- a PRD or MVP scope input that needs human review
- a KDR/DAR candidate
- a backlog follow-up or deprioritization note
- a next customer discovery or research test
- a risk-review handoff
- a knowledge update that changes future execution

If none of these applies, the synthesis is incomplete and should not be committed as a durable artifact.

## What-Changed Rules

The `What Changed` section is mandatory.

Use it to state:

- which assumption became stronger, weaker, or unchanged
- whether confidence increased, decreased, or stayed the same
- whether validation, PRD, MVP scope, KDR/DAR, or backlog should change
- what is still blocked by missing evidence or human review

Do not write "nothing changed" unless the output is explicitly a no-change note in Linear or a source log, not a committed synthesis artifact.

## Source And Evidence Rules

Each synthesis must:

- cite source IDs from `research/source-quality-and-citation-rules.md`
- include source type, date, freshness, confidence, and risk if wrong
- include evidence score summary when scoring was used
- name contradictions instead of averaging them away
- state what the evidence does not prove
- preserve missing customer evidence as a visible limitation

Raw source summaries are not enough. The synthesis must explain the decision implication.

## Human Review Gate

Human review is required before the synthesis changes:

- validation thresholds or scorecard interpretation
- PRD commitments
- MVP scope
- KDR/DAR status
- backlog priority
- pricing, growth, monetization, or build sequencing
- public positioning or external claims
- legal, financial, compliance, privacy, security, scientific, customer-evidence, or regulated claims

If review is missing, mark the synthesis as blocked for decision use and route the next action through Linear.

## Done Criteria

This template is complete when:

- the decision question is explicit
- sources include type, date, freshness, confidence, risk if wrong, and limitation
- findings include support, contradiction, open assumption, confidence, and risk
- `What Changed` is mandatory
- the synthesis updates validation, PRD, KDR/DAR, backlog, a next test, or a risk handoff
- no long literature review is required by default
- human review gates block strategic or sensitive changes
