# KDR / DAR Template

Use this template for strategic decisions that future agents may need to understand, revisit, or supersede.

Do not create a KDR/DAR for trivial edits, typo fixes, mechanical formatting, or routine ticket handoff.

## When To Use

Create a KDR/DAR when a decision:

- changes product strategy, validation path, MVP scope, architecture, risk posture, growth, monetization, or governance
- accepts or rejects meaningful evidence
- resolves a strategic tradeoff
- changes assumptions future agents may otherwise reuse incorrectly
- supersedes a prior strategic decision

## Record

- ID:
- Date:
- Owner:
- Origin Linear ticket:
- Origin PR or artifact:
- Status: Proposed / Accepted / Superseded / Rejected

## Decision

- Decision:
- Decision type: Product / Validation / Research / Architecture / Risk / Growth / Monetization / Governance
- Short rationale:

## Context

- Trigger:
- Current phase:
- Relevant artifacts:
- Constraints:

## Options Considered

| Option | Pros | Cons | Why accepted/rejected |
|---|---|---|---|
|  |  |  |  |

## Evidence

| Evidence | Type | Source | Confidence |
|---|---|---|---|
|  | Customer / research / validation / architecture / risk / assumption |  | Low / Medium / High |

## Risks

- Risk accepted:
- Risk rejected:
- Mitigation:
- Follow-up ticket:

## Revisit Trigger

Revisit this decision when:

- Evidence changes:
- Metric or threshold changes:
- Customer segment changes:
- Risk changes:
- Date or phase:

## Supersession

- Supersedes:
- Superseded by:
- Conflict status: None / Potential conflict / Conflict unresolved

When superseding a decision, link both records and explain what changed.

## Human Review

- Human review required: yes/no
- Review source:
- Approval or objection:

## Example

```md
# KDR-001 - Keep MVP Manual Before Building Automation

## Record

- ID: KDR-001
- Date: 2026-05-15
- Owner: knowledge_curator
- Origin Linear ticket: PIP-56
- Origin PR or artifact: product/mvp-scope.md
- Status: Accepted

## Decision

- Decision: The first MVP test should prove the riskiest assumption manually before automation work is proposed.
- Decision type: Product / Validation
- Short rationale: The validation scorecard and MVP scope gate prioritize observed customer behavior over premature build effort.

## Context

- Trigger: MVP scope gate creation.
- Current phase: MVP scope review.
- Relevant artifacts: product/mvp-scope.md, validation/validation-scorecard.md.
- Constraints: No implementation tickets before evidence threshold and human approval.

## Options Considered

| Option | Pros | Cons | Why accepted/rejected |
|---|---|---|---|
| Manual test first | Faster learning, lower build risk | Less scalable | Accepted because the MVP must test the riskiest assumption first |
| Build automation first | Looks more complete | Premature complexity, weak evidence | Rejected because it bypasses validation |

## Evidence

| Evidence | Type | Source | Confidence |
|---|---|---|---|
| MVP scope requires smallest ethical test | Governance artifact | product/mvp-scope.md | High |

## Risks

- Risk accepted: Manual test may not represent final scalability.
- Risk rejected: Building full automation without customer evidence.
- Mitigation: Create implementation tickets only after GO or approved CONDITIONAL GO.
- Follow-up ticket: None.

## Revisit Trigger

Revisit this decision when:

- Evidence changes: repeated manual tests show the same workflow and bottleneck.
- Metric or threshold changes: validation scorecard reaches GO.
- Customer segment changes: ICP changes materially.
- Risk changes: manual test introduces unacceptable privacy or operational risk.
- Date or phase: before architecture ticket creation.

## Supersession

- Supersedes: None.
- Superseded by:
- Conflict status: None.

## Human Review

- Human review required: yes.
- Review source: PR review and Linear approval.
- Approval or objection: Approved by merge.
```
