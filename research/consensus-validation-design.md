# Consensus Validation Design

This design note describes how a future Consensus-style research workflow could support scientific evidence validation while keeping evidence summaries separate from decisions, advice, and public claims.

Use it with `research/scientific-validation-workflow.md`, `research/research-orchestrator-workflow.md`, `execution/risk-reviewer-matrix-lite.md`, and `execution/approval-gates.md`.

## Boundary

This is a planning artifact only. It does not implement a Consensus connector, call external tools, configure credentials, provide medical/legal/financial advice, or approve scientific claims for public use.

Consensus-style outputs may become evidence inputs. They are not decision authority.

## Intended Use

Use a Consensus-style workflow only to:

- query scientific or research-backed claims
- identify stronger source trails than general web search
- compare source quality, recency, directness, and contradictions
- prepare evidence summaries for `scientific_validation_agent`
- flag claims that require professional, expert, or human review

Do not use it to:

- make clinical, legal, financial, compliance, safety, privacy, or security conclusions
- publish public claims
- replace expert review
- replace the scientific validation workflow
- automate GO / NO-GO, PRD, MVP, risk, or implementation decisions

## Claim Query Design

Start with one exact claim.

Required query fields:

- claim ID
- exact claim text
- claim type: Mechanism / Outcome / Comparative / Regulated / Implementation
- intended use
- target audience
- product artifact affected
- sensitive domain: yes/no
- expected evidence type
- exclusion terms or scope boundaries

Good query:

- "Does source evidence support that structured customer interviews improve early B2B problem validation accuracy compared with founder intuition?"

Avoid:

- "Prove this is scientifically valid."
- "Find studies that support our claim."
- "Can we say this is clinically proven?"

## Evidence Input Fields

Every source returned or selected for review must include:

- source title
- source URL or identifier
- publication date
- source type
- study type or evidence type, when available
- population or setting
- claim matched
- directness to the product claim
- limitation
- contradiction note
- citation status

If the underlying source cannot be inspected directly, mark it as `citation unavailable` and do not use it for sensitive claims.

## Evidence Grading

Consensus-style evidence should be graded before synthesis.

| Dimension | Rating | Notes |
|---|---|---|
| Source tier | Tier 1 / 2 / 3 / 4 | Use the tiers in `research/scientific-validation-workflow.md`. |
| Directness | Low / Medium / High | Does it evaluate the exact claim, population, context, and outcome? |
| Recency | Current / Dated / Stale / Unknown | Use domain-specific judgment; stale sources need caution. |
| Method clarity | Low / Medium / High | Is the method understandable enough to evaluate? |
| Replication | None / Partial / Strong | Are independent sources consistent? |
| Applicability | Low / Medium / High | Does it apply to this product, ICP, geography, and workflow? |
| Contradiction | None / Some / Material | Are there credible conflicts or caveats? |
| Risk if wrong | Low / Medium / High | Would a bad claim affect safety, money, trust, compliance, or legal/privacy/security posture? |

High risk if wrong always requires `risk_reviewer` plus human or expert review before decision-critical or public use.

## Evidence Summary Versus Decision Recommendation

Keep these outputs separate.

Evidence summary may say:

- what sources were reviewed
- what the sources appear to support
- what the sources contradict
- source tiers and limitations
- confidence and uncertainty
- whether professional review is required

Evidence summary must not say:

- "therefore we should launch"
- "therefore this is compliant"
- "therefore this is clinically/legally/financially valid"
- "therefore customers will buy"
- "therefore build tickets are approved"

Decision recommendations belong to the appropriate human-reviewed product, risk, validation, or strategy workflow after the evidence summary is reviewed.

## Citation Rules

Every evidence summary must include:

- claim ID
- source title
- URL or identifier
- publication date
- source tier
- directness rating
- applicability rating
- limitation
- confidence
- review status

Do not cite AI-generated summaries as source evidence. Cite the underlying source.

Do not use long quotes. Summarize narrowly and preserve the link.

## Professional Review Flags

Flag professional or explicit human review when:

- the claim touches medical, mental health, legal, financial, compliance, privacy, security, safety, or regulated outcomes
- the evidence is Tier 3 or Tier 4 for a sensitive claim
- source directness or applicability is Low
- contradiction is Material
- risk if wrong is High
- public copy, sales material, PRD commitments, investor material, or customer-facing promises would change
- the reviewer cannot evaluate the claim from repository artifacts

If a flag is present, the evidence summary is blocked for decision-critical or public use until review is complete.

## Output Template

```md
# Consensus Evidence Summary - <claim ID>

## Metadata

- Origin ticket:
- Owner:
- Date:
- Claim ID:
- Exact claim:
- Intended use:
- Sensitive domain:
- Approval state:

## Query Design

- Query:
- Inclusion scope:
- Exclusion scope:
- Expected evidence type:

## Evidence Table

| Source | Date | Tier | Directness | Applicability | Contradiction | Risk if wrong | Confidence | Limitation |
|---|---|---|---|---|---|---|---|---|
|  |  | Tier 1 / 2 / 3 / 4 | Low / Medium / High | Low / Medium / High | None / Some / Material | Low / Medium / High | Low / Medium / High |  |

## Evidence Summary

- What sources appear to support:
- What sources contradict:
- Key limitations:
- Confidence:
- What this does not prove:
- Professional/human review required:

## Decision Boundary

- This is evidence input, not decision authority:
- Decision owner:
- Risk reviewer needed:
- Claim blocked from public/decision-critical use: yes/no
- Next workflow:
```

## Approval Gates

Approval is required before:

- implementing or configuring a Consensus connector
- using paid, private, credentialed, or confidential source access
- storing credentials or secrets
- publishing scientific evidence summaries externally
- using evidence summaries to change public claims, PRD commitments, MVP scope, risk posture, pricing, growth, or implementation tickets
- making medical, legal, financial, compliance, safety, privacy, security, or regulated claims

If approval is missing, keep the output as a draft evidence input and record the blocker.

## Done Criteria

This design is complete when:

- claim queries start from exact claim text
- evidence grading covers source tier, directness, recency, method clarity, replication, applicability, contradiction, and risk if wrong
- citation rules point to underlying sources, not summaries
- evidence summary is separate from decision recommendation
- sensitive claims have professional/human review flags
- approval gates block live integration, credentials, external publication, and decision-critical use without review
