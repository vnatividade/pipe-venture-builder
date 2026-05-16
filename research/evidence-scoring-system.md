# Evidence Scoring System

This template scores evidence strength across customer, market, scientific, usage, and synthetic inputs so research can inform ranking without hiding uncertainty or automating decisions.

Use it with `research/source-quality-and-citation-rules.md`, `research/research-orchestrator-workflow.md`, `validation/validation-scorecard.md`, `knowledge/knowledge-curator-workflow.md`, and `execution/approval-gates.md`.

## Boundary

Evidence scores are advisory only. They do not create GO / NO-GO decisions, approve PRD changes, approve MVP scope, validate demand, replace customer discovery, replace expert review, or authorize implementation tickets.

Human review is required before using scores for idea ranking, validation thresholds, PRD decisions, MVP scope, public claims, growth, monetization, or build prioritization.

## Evidence Hierarchy

For demand validation, customer evidence outranks synthetic or generic research.

| Evidence lane | Examples | Demand-validation weight | Limit |
|---|---|---:|---|
| Customer behavior | Observed workflow, repeated workaround, pilot request, qualified waitlist behavior, paid or time commitment. | 5 | Limited to the source coverage, segment, consent, and context. |
| Customer language | Approved interview notes, objections, trigger phrases, exact pain descriptions. | 4 | Stated pain is weaker than observed behavior or commitment. |
| Usage or trial signal | Prototype usage, manual concierge result, trial feedback, repeated engagement. | 4 | Can be biased by trial design, sample size, and novelty. |
| Market signal | Competitor/substitute evidence, pricing pages, forum patterns, channel signals, public buyer language. | 3 | Does not prove this ICP wants this wedge. |
| Scientific or expert source | Peer-reviewed source, official guidance, expert consensus, technical documentation. | 3 | Supports claim quality, not customer demand. |
| Synthetic or AI-generated input | Synthetic personas, AI summaries, generated objections, generated market hypotheses. | 1 | Hypothesis input only; not evidence of customer demand. |
| Internal assumption | Founder belief, agent inference, strategy hypothesis. | 0 | Not evidence. Must be tested or sourced. |

Synthetic and internal inputs may create questions. They cannot raise demand-validation confidence above Low unless supported by stronger source lanes.

## Score Dimensions

Score each evidence item from 0 to 3 across the dimensions below.

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Evidence type | Internal assumption | Synthetic or generic source | External non-customer signal | Customer behavior, customer language, or approved usage signal |
| Source quality | Missing, uninspectable, or Tier 4 | Tier 3 or weak provenance | Tier 2 or inspectable direct source | Tier 1 or approved customer/authoritative source |
| Recency | Unknown or stale | Dated | Current enough with caveat | Current and appropriate for the decision window |
| Directness | Does not match question | Indirectly related | Related to ICP/problem but incomplete | Directly matches ICP, problem, geography, and decision |
| Confidence | Low with major gaps | Low with limited support | Medium with corroboration | High within a narrow, sourced scope |
| Contradiction handling | Contradictions ignored | Contradictions noted vaguely | Conflicts named and confidence adjusted | Conflicts resolved or explicitly blocked for decision use |
| Risk adjustment | Risk if wrong unknown | Risk recorded but not reflected | Medium/high risk reduces score or blocks use | Risk reviewed and accepted for the intended use |

## Weighted Advisory Score

Use this formula for a lightweight advisory score:

```txt
Base evidence weight
+ evidence type score
+ source quality score
+ recency score
+ directness score
+ confidence score
+ contradiction handling score
+ risk adjustment score
= advisory evidence score
```

Maximum score depends on lane weight. Use the score to compare evidence strength within the same decision question, not across unrelated product ideas.

Interpretation:

| Advisory score | Meaning | Allowed use |
|---:|---|---|
| 0-7 | Weak or assumption-heavy | Assumptions register or research question only. |
| 8-13 | Useful hypothesis support | Can inform discovery planning with limitations visible. |
| 14-19 | Stronger evidence input | Can inform human-reviewed ranking or validation synthesis. |
| 20+ | Strong evidence input for a narrow claim | Can support human-reviewed decisions inside the proven scope. |

No score alone can approve build work, pricing, public claims, customer outreach, or GO / NO-GO decisions.

## Demand Validation Rule

For demand validation, the strongest score category is capped by the strongest evidence lane:

| Strongest available evidence | Maximum demand-validation interpretation |
|---|---|
| Internal assumption only | No evidence |
| Synthetic or AI-generated input only | Hypothesis only |
| Generic market or scientific research only | External context only |
| Public market signal without customer behavior | Weak to medium hypothesis support |
| Customer language without observed behavior or commitment | Medium validation input |
| Observed customer behavior, repeated workaround, or commitment | Stronger validation input within source coverage |

If customer evidence is absent, the output must say: `Customer evidence missing; demand validation remains unproven.`

## Contradiction And Uncertainty Rules

Scoring must expose uncertainty.

When evidence conflicts:

- record source IDs from `research/source-quality-and-citation-rules.md`
- name what conflicts
- reduce confidence unless the conflict is resolved
- mark decision-impacting conflicts as blocked for human review
- state which additional evidence would resolve the conflict

Do not hide contradictions inside a numeric average.

## Risk Adjustment Rules

Risk if wrong affects how a score may be used.

| Risk if wrong | Score effect | Decision use |
|---|---|---|
| Low | No automatic penalty when limitation is recorded. | Internal planning only unless review is required by another rule. |
| Medium | Subtract 1 from advisory score unless human-reviewed. | Human review required before ranking or scope impact. |
| High | Score is blocked for decision use until reviewed. | Risk reviewer and human or expert review required. |

If risk is unknown, treat it as Medium until reviewed.

## Evidence Scoring Template

```md
# Evidence Score - <decision question>

## Metadata

- Origin ticket:
- Owner:
- Date:
- Decision question:
- Product phase:
- Approval state:
- Human review before ranking use: yes/no

## Evidence Items

| Evidence ID | Source ID | Evidence lane | Summary | Base weight | Type | Quality | Recency | Directness | Confidence | Contradiction | Risk adjustment | Advisory score | Limit |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| E-001 | S-001 | Customer behavior / Customer language / Usage or trial / Market signal / Scientific or expert / Synthetic / Internal assumption |  | 0-5 | 0-3 | 0-3 | 0-3 | 0-3 | 0-3 | 0-3 | Blocked / -1 / 0 / +0 |  |  |

## Confidence Summary

- Strongest evidence lane:
- Customer evidence present: yes/no
- Customer evidence missing statement, if needed:
- Highest-scoring item:
- Lowest-confidence item:
- Material contradictions:
- Risk if wrong:
- What this does not prove:

## Advisory Interpretation

- Suggested interpretation:
- Use allowed before human review:
- Use blocked until human review:
- Validation scorecard impact:
- Knowledge update needed:
- Follow-up ticket needed:
```

## Handoff Rules

| Outcome | Handoff |
|---|---|
| Customer evidence missing or weak | `validation_agent` or `customer_discovery_agent` |
| Market evidence strong but customer proof absent | `market_intelligence_agent` plus validation follow-up |
| Scientific or high-risk evidence affects a claim | `scientific_validation_agent` and `risk_reviewer` |
| Scoring changes durable interpretation of an idea | `knowledge_curator` |
| Score would affect PRD, MVP, ranking, pricing, growth, or build priority | Human review before use |

## Done Criteria

This scoring system is complete when:

- evidence lanes cover customer, market, scientific, usage, synthetic, and internal inputs
- customer evidence outranks synthetic and generic research for demand validation
- scoring includes source quality, recency, directness, confidence, contradiction handling, and risk if wrong
- numeric scores remain advisory and cannot automate final decisions
- uncertainty, limits, and missing customer evidence stay visible
- human review is required before ranking use or decision impact
