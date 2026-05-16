# Idea Ranking Engine Design

This design defines a first-version rubric for ranking product ideas using structured evidence, C.O.N.T.R.O.L.E., validation readiness, market context, founder advantage, distribution feasibility, and risk.

Use it with `product/controle-evaluation.md`, `product/founder-focus.md`, `validation/validation-scorecard.md`, `research/evidence-scoring-system.md`, `research/research-synthesis-template.md`, `research/source-quality-and-citation-rules.md`, `research/market-research-workflow.md`, and `execution/approval-gates.md`.

## Boundary

This is an advisory ranking design. It does not select products automatically, override C.O.N.T.R.O.L.E. verdicts, approve build tickets, approve PRD/MVP scope, validate demand, authorize outreach, or create public claims.

Human approval is required before a ranking changes prioritization, PRD/MVP scope, backlog order, validation thresholds, resource allocation, growth, monetization, or build sequencing.

## Gate Rules

Ranking may only be used when:

- each idea has a founder focus artifact or equivalent snapshot
- each idea has a C.O.N.T.R.O.L.E. evaluation
- evidence sources are traceable through source IDs or repository artifacts
- evidence confidence and limitations are visible
- the intended decision owner is named
- human approval is available before prioritization decisions

Ranking must not override:

- `Kill` verdicts
- `Pivot` verdicts
- missing customer evidence
- unresolved high-risk findings
- blocked sensitive claims
- absent source traceability

If C.O.N.T.R.O.L.E. is `Kill`, the idea is excluded from ranking unless a new approved framing exists.

If C.O.N.T.R.O.L.E. is `Pivot`, the current framing cannot be prioritized. Create or evaluate the related direction as a separate idea.

If C.O.N.T.R.O.L.E. is `Refine`, the idea may be ranked only for validation planning, not build priority.

If C.O.N.T.R.O.L.E. is `Attack`, the idea may be ranked for validation or PRD readiness after human review.

## Ranking Dimensions

Score each dimension from 0 to 5.

- 0: absent, blocked, contradicted, or unsafe to use
- 1: weak, assumption-heavy, or mostly synthetic
- 3: plausible with some traceable evidence and visible limitations
- 5: strong, narrow, evidence-backed, and actionable after review

| Dimension | Weight | What to score | Required evidence |
|---|---:|---|---|
| Persona and ICP specificity | 1.2 | Clear first user/buyer, excluded segments, trigger context. | `product/founder-focus.md`, ICP artifact, customer or market evidence. |
| Problem intensity | 1.5 | Urgency, frequency, cost of inaction, pain salience. | Customer behavior/language preferred; market signals are weaker. |
| Willingness to pay or commit | 1.5 | Existing spend, budget owner, paid intent, time/data/access commitment. | Customer or budget evidence; generic market size is insufficient. |
| Channel reachability | 1.2 | Founder-accessible first channel without paid acquisition by default. | Channel evidence, communities, search intent, founder access, market research. |
| Competition and substitutes | 1.0 | Clear substitutes, differentiated wedge, manageable switching friction. | Substitute map, competitor/source review, customer status quo. |
| Geography and local context | 0.8 | Country/city feasibility, language, local substitutes, payment behavior. | Market research with source date and confidence. |
| Regulation and trust risk | 1.2 | Legal, compliance, privacy, safety, procurement, and trust constraints. | Risk review, source quality, expert/scientific review where needed. |
| MVP speed and ethical testability | 1.3 | Smallest ethical test, manual feasibility, fast learning loop. | MVP scope gate, validation scorecard, founder focus. |
| Founder advantage | 1.0 | Access, domain insight, credibility, distribution leverage, execution fit. | Founder focus artifact, validated access, explicit assumptions. |
| Context and timing | 1.0 | Why this market, workflow, regulation, behavior, or tool shift matters now. | C.O.N.T.R.O.L.E. timing rationale, market research, validation learning. |
| Distribution context | 1.0 | Repeatable reach, channel constraints, partnership potential, non-paid path. | Market/channel evidence and validation learning. |
| Evidence strength | 1.6 | Evidence score, source quality, recency, directness, contradictions. | `research/evidence-scoring-system.md` and source quality rules. |
| C.O.N.T.R.O.L.E. alignment | 1.7 | Strength across C, O, N, T, R, O, L, E and verdict consistency. | `product/controle-evaluation.md` with verdict and rationale. |

## Confidence Layer

Each dimension must include confidence.

| Confidence | Use when |
|---|---|
| Low | Score depends on assumptions, synthetic input, stale sources, weak ICP match, or unreviewed contradictions. |
| Medium | Score has traceable sources but customer behavior, geography, or decision impact remains incomplete. |
| High | Score is supported by recent, direct, inspectable sources and reviewed customer or validation evidence for the exact scope. |

Overall ranking confidence is the lowest confidence among:

- C.O.N.T.R.O.L.E. alignment
- evidence strength
- problem intensity
- willingness to pay or commit
- channel reachability
- regulation and trust risk

Do not average these away. A high total score with Low confidence remains a Low-confidence ranking.

## Evidence Requirements

Every ranked dimension must cite:

- source ID or repository artifact
- source type
- date or access date
- confidence
- risk if wrong
- limitation

Use `Unknown` when a field is missing, then reduce confidence.

If a score has no source, mark the score as `0` or `Assumption only` and route it to the assumptions register or a research/validation follow-up.

## Weighted Score

Calculate a weighted advisory score:

```txt
dimension score * dimension weight = weighted dimension score
sum(weighted dimension scores) = raw ranking score
```

Use the raw score only after applying gates:

1. Exclude `Kill`.
2. Exclude current `Pivot` framing.
3. Block unresolved High risk if wrong.
4. Block absent source traceability.
5. Cap ranking confidence by the confidence layer.
6. Require human approval before prioritization.

## Ranking Bands

| Band | Meaning | Allowed use |
|---|---|---|
| Priority candidate | Strong relative score, traceable evidence, no blocking gate, Medium/High confidence. | Human-reviewed prioritization or deeper validation planning. |
| Validation candidate | Promising but evidence gaps, Low/Medium confidence, or Refine verdict. | Customer discovery, research synthesis, or focus refinement. |
| Watchlist | Interesting but weak evidence, poor channel clarity, or unresolved assumptions. | Backlog with explicit revisit trigger. |
| Blocked | Kill/Pivot current framing, high-risk unresolved issue, missing traceability, or sensitive claim blocker. | Do not prioritize until blocker is resolved. |

Ranking bands do not approve build work.

## Tie-Breakers

Apply tie-breakers only after gates and confidence are visible.

Prefer the idea with:

1. stronger customer behavior or commitment evidence
2. clearer C.O.N.T.R.O.L.E. Attack/Refine rationale
3. faster ethical validation test
4. lower regulation, privacy, security, or trust risk
5. clearer founder-accessible channel
6. narrower wedge and sharper ICP
7. stronger founder advantage
8. fewer unresolved contradictions

Do not use generic TAM, trendiness, backlog size, or agent excitement as tie-breakers.

## Ranking Template

```md
# Idea Ranking - <ranking batch or decision question>

## Metadata

- Origin ticket:
- Ranking owner:
- Date:
- Decision owner:
- Ideas compared:
- Approval state:
- Human approval before prioritization: yes/no

## Gate Check

| Idea | C.O.N.T.R.O.L.E. verdict | Source traceability | High-risk blockers | Ranking status | Notes |
|---|---|---|---|---|---|
|  | Attack / Refine / Pivot / Kill | Complete / Partial / Missing | None / Blocked | Eligible / Validation only / Watchlist / Blocked |  |

## Rubric

| Idea | Dimension | Score | Weight | Weighted score | Confidence | Source IDs / artifacts | Risk if wrong | Limitation |
|---|---|---:|---:|---:|---|---|---|---|
|  | Persona and ICP specificity | 0-5 | 1.2 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Problem intensity | 0-5 | 1.5 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Willingness to pay or commit | 0-5 | 1.5 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Channel reachability | 0-5 | 1.2 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Competition and substitutes | 0-5 | 1.0 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Geography and local context | 0-5 | 0.8 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Regulation and trust risk | 0-5 | 1.2 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | MVP speed and ethical testability | 0-5 | 1.3 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Founder advantage | 0-5 | 1.0 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Context and timing | 0-5 | 1.0 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Distribution context | 0-5 | 1.0 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | Evidence strength | 0-5 | 1.6 |  | Low / Medium / High |  | Low / Medium / High |  |
|  | C.O.N.T.R.O.L.E. alignment | 0-5 | 1.7 |  | Low / Medium / High |  | Low / Medium / High |  |

## Ranking Result

| Idea | Raw ranking score | Overall confidence | Band | Tie-breaker notes | Human review required | Decision use allowed |
|---|---:|---|---|---|---|---|
|  |  | Low / Medium / High | Priority candidate / Validation candidate / Watchlist / Blocked |  | yes/no | yes/no |

## Decision Notes

- Recommended ranking interpretation:
- What changed versus prior ranking:
- Strongest evidence:
- Weakest evidence:
- Missing customer evidence:
- Material contradictions:
- Risk if wrong:
- What this ranking does not prove:
- Human approval record or blocker:

## Handoff

- Validation update needed:
- Research synthesis needed:
- KDR/DAR needed:
- Backlog change proposed:
- Follow-up ticket needed:
- Next review trigger:
```

## Human Approval Gate

Human approval is required before using ranking to:

- prioritize one idea over another
- change backlog order
- change validation thresholds
- change PRD or MVP scope
- create build tickets
- change growth, monetization, pricing, or distribution strategy
- accept medium/high-risk tradeoffs
- override an existing strategic decision

If approval is missing, ranking can only be recorded as analysis context.

## Done Criteria

This design is complete when:

- dimensions cover persona, problem, willingness to pay, channel, competition, geography, regulation, MVP speed, founder advantage, context/distribution, evidence, and C.O.N.T.R.O.L.E.
- weights, confidence, evidence requirements, and tie-breakers are explicit
- ranking cannot override C.O.N.T.R.O.L.E. Kill/Pivot outcomes without a new approved evaluation
- source traceability is required for every scored dimension
- missing customer evidence remains visible
- human approval is required before prioritization decisions
