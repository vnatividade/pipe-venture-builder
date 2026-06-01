# Geography Ranking Rubric

Use this rubric when comparing how strongly one idea fits different countries, regions, cities, or local markets before prioritizing validation, PRD, MVP, growth, monetization, or build work.

Geography can change market maturity, pain intensity, regulation, local payment behavior, channel access, competitive density, and founder fit. It can also create false confidence when agents make broad country or city claims without current sources.

## Boundary

This rubric does not authorize:

- legal, regulatory, tax, financial, privacy, or compliance advice
- unsupported geographic claims
- automatic prioritization changes
- launch, pricing, billing, paid acquisition, or market entry decisions
- scraping local directories, communities, or lead lists
- contacting prospects or partners
- storing private customer or market data

Expert or human review is required before relying on regulatory, legal, compliance, tax, privacy, financial, healthcare, safety, or sensitive local-market claims.

## Required Inputs

Before ranking a geography, link:

- origin Linear ticket
- idea or venture name
- target persona or ICP hypothesis
- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `validation/icp-profile.md`
- `validation/persona-ranking-rubric.md`, when persona fit affects geography choice
- `validation/validation-scorecard.md`, when validation confidence may change
- source log with citations, publication dates, access dates, and reviewer notes

If a geography claim lacks a current source, mark it `NO-GO: unsupported geography claim` and do not use it for prioritization.

## Current-Source Rule

Geography scoring must use current, citable sources.

| Claim type | Minimum source expectation | Review requirement |
|---|---|---|
| Regulatory, legal, compliance, privacy, tax, or sector restriction | Current official source, expert source, or legal/compliance review note | Human/expert review required |
| Market maturity or category adoption | Recent market report, public data, sourced research, or customer evidence | Human review required when changing priority |
| Payment behavior or purchasing process | Customer interview, public report, payment/provider source, or observed local workflow | Human review required when monetization may change |
| Channel access or local distribution | Manual channel evidence, public community/source, interview, or experiment result | Human review required before outreach or spend |
| Competition or substitutes | Current competitor/source scan with access date | Human review before priority change |
| Founder fit or local edge | Founder context, network evidence, language/cultural capability, or operational constraint | Human review before market selection |

Do not use stale sources for fast-changing categories, AI tooling, regulation, payments, platforms, or distribution behavior without a freshness note.

## Evidence Strength

Use the strongest applicable evidence type for each score.

| Evidence type | Strength | Use as |
|---|---|---|
| Current official/regulatory source with access date | Strong for claim existence, not legal advice | Constraint evidence |
| Real customer interview or local operator evidence | Strong | Pain, workflow, channel, buying, payment evidence |
| Observed local behavior, workaround, spend, pilot request, or commitment | Strong | Validation evidence |
| Recent cited market research or public dataset | Medium | Market context |
| Current competitor/substitute scan | Medium | Competitive context |
| Founder/operator experience with source note | Medium | Local edge or constraint hypothesis |
| AI summary, old article, unsourced trend, or internal opinion | Weak | Question generator only |
| Unsupported country/city narrative | Invalid | Do not score |

## Scoring Scale

Score each category from 0 to 3.

- 0: no source, invalid source, or contradicted by current evidence
- 1: weak signal, stale source, internal assumption, or source mismatch
- 2: plausible current source or limited local evidence
- 3: strong current evidence from official sources, local customer/operator evidence, observed behavior, or repeated patterns

Every score must include source citation, source date or access date, evidence type, confidence, and reviewer note.

## Geography Ranking Categories

| Category | Question | Score | Evidence type | Confidence | Source and date |
|---|---|---:|---|---|---|
| Market maturity | Is the category understood enough locally for adoption without excessive education? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Pain intensity | Is there local evidence that this problem is urgent, frequent, costly, or risky? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| ICP density | Are enough first-ICP prospects likely present in this geography? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Distribution feasibility | Can the founder reach the ICP through credible local channels? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Payment behavior | Does local buying, payment, procurement, or willingness-to-pay behavior fit the wedge? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Regulatory friction | Are local legal, privacy, tax, compliance, or sector constraints understood and acceptable? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Competitive density | Are competitors, substitutes, or local incumbents mapped enough to assess differentiation? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Language and culture fit | Can the founder and product communicate credibly in local buyer/user language and norms? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Operational feasibility | Can support, onboarding, fulfillment, timezone, and service expectations be handled? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Founder edge | Does the founder have network, knowledge, trust, credibility, or speed advantage in this geography? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |

## Ranking Matrix

Use this matrix to compare geographies for one idea and one persona.

```md
# Geography Ranking Review

## Metadata

- Idea or venture:
- Origin ticket:
- Reviewer:
- Date:
- Persona / ICP:
- Human review required before prioritization change: yes
- Expert review required for regulatory claims: yes/no

## Source Artifacts

- Founder focus:
- C.O.N.T.R.O.L.E.:
- ICP profile:
- Persona ranking:
- Validation scorecard:
- Source log:

## Geography Scores

| Geography | Geography level | Total score | Lowest category | Strongest evidence | Weakest evidence | Regulatory review needed | Confidence | Priority proposal |
|---|---|---:|---|---|---|---|---|---|
|  | Country / region / city / local market |  |  |  |  | yes/no | Low / Medium / High | P1 / P2 / P3 / Do not pursue |

## Category Detail

| Geography | Category | Score | Evidence type | Source citation | Source date / access date | Confidence | Reviewer note |
|---|---|---:|---|---|---|---|---|
|  | Market maturity / pain / ICP density / distribution / payment / regulation / competition / language / operations / founder edge |  | Strong / Medium / Weak / Invalid |  |  | Low / Medium / High |  |

## Ranking Interpretation

- Best geography to validate next:
- Geography to exclude or defer:
- Strongest source-backed signal:
- Weakest or stale source:
- Regulatory or expert review needed:
- Local discovery still needed:
- Scorecard impact:
- C.O.N.T.R.O.L.E. impact:
- Priority change proposal:
- Human approval status:
```

## Interpretation Rules

Use total score only after checking source quality and the lowest category.

| Result | Use when | Allowed next action |
|---|---|---|
| Prioritize for research | Geography has promising signals but needs more source verification. | Create focused research questions. |
| Prioritize for discovery | Geography has strong persona fit, reachable channels, and no unresolved high-risk blockers. | Update respondent targeting or discovery plan after approval. |
| Keep as secondary geography | Some promise, but weak channel/payment/operational evidence. | Park until stronger evidence exists. |
| Needs expert review | Regulatory, legal, tax, privacy, compliance, or sector claim affects feasibility. | Stop priority change until review. |
| Exclude for now | Geography is unsupported, stale, inaccessible, too regulated, or outside founder fit. | Document exclusion rationale. |
| Blocked | Claims lack current sources or source dates. | Do not rank until source log is fixed. |

Regulatory friction should be treated as a feasibility question, not as advice. Agents may identify review needs; they must not conclude legality or compliance safety.

## Follow-Up Ticket Criteria

Create or recommend a follow-up ticket only when the ranking produces a concrete next action:

- source-review a named geography claim
- research a named local channel, competitor, payment behavior, or regulatory constraint
- update respondent targeting for a specific geography and persona
- run an approved manual channel test in a named geography
- update validation scorecard after source-backed geography evidence
- request expert/human review for a specific regulatory or compliance uncertainty
- document a durable decision if a geography is accepted, deferred, or excluded with strong rationale

Do not create follow-ups for broad country curiosity, unsupported local narratives, stale trend claims, or synthetic-only geography assumptions.

## Done Criteria

This rubric is complete when:

- country, region, city, and local-market comparison fields exist
- source citation and confidence labels are required for each score
- market maturity, regulation, payment behavior, local channels, competition, and founder fit are represented
- unsupported geographic claims are blocked
- regulatory/legal/compliance claims require expert or human review
- prioritization changes require human review
- follow-up criteria are concrete and validation-oriented

## Relationship To Existing Artifacts

- Use `validation/persona-ranking-rubric.md` before geography ranking when persona fit is not clear.
- Use `validation/icp-profile.md` to keep geography tied to a specific ICP hypothesis.
- Use `validation/respondent-targeting-and-interview-planner.md` when a geography changes which respondent profiles the founder should seek manually.
- Use `validation/validation-scorecard.md` before changing validation confidence.
- Use `growth/builderpulse-idea-ranking-contrast-workflow.md` if BuilderPulse signals affect geography ranking as advisory inputs.
