# BuilderPulse Monitoring Workflow

Use this workflow when BuilderPulse publications may provide external market, builder ecosystem, product pattern, or opportunity signals for Pipe venture discovery.

BuilderPulse signals are advisory. They can influence research questions, opportunity comparison, persona hypotheses, channel hypotheses, and contradiction review, but they do not replace customer discovery, sourced research, validation scorecards, C.O.N.T.R.O.L.E., or human prioritization.

Source URL:

- `https://github.com/BuilderPulse/BuilderPulse`

## Boundary

This workflow does not authorize:

- live scraping
- automated repository access
- scheduled polling jobs
- external API calls
- automated issue creation from BuilderPulse signals
- automated outreach
- treating BuilderPulse publications as customer proof
- bypassing `validation/market-validation-before-code-gate.md`
- changing roadmap priority without human review

Any automation, connector, scraper, scheduled job, or external data ingestion requires a separate approved Linear ticket and risk review.

## Purpose

BuilderPulse may surface useful directional signals about what builders, AI-native teams, tools, workflows, or markets are discussing.

The risk is false confidence: a publication can be interesting without proving demand, pain intensity, channel access, willingness to pay, or founder fit.

This workflow keeps BuilderPulse useful but bounded:

- capture source-backed signals
- classify each signal by type
- record date, citation, relevance, and confidence
- compare signals against existing Pipe assumptions
- identify what evidence is still missing
- decide whether a research, discovery, or validation follow-up is justified

## Required Inputs

Before using a BuilderPulse signal, link:

- origin Linear ticket
- BuilderPulse publication URL
- publication date or observed date
- reviewer
- related idea, market, persona, channel, or assumption
- `product/founder-focus.md`, when the signal may affect founder fit
- `product/controle-evaluation.md`, when the signal may affect strategic fit
- `validation/validation-scorecard.md`, when the signal may affect validation confidence
- `validation/respondent-targeting-and-interview-planner.md`, when the signal suggests personas to find manually
- `growth/idea-browser-validation-workflow.md`, when the signal overlaps with idea-comparison input
- `knowledge/knowledge-curator-workflow.md`, when repeated signals may become durable venture intelligence

If the publication cannot be cited with a stable source URL and observed date, treat the signal as an unverified note and do not update scoring, priority, or roadmap.

## Signal Types

Classify each signal before using it.

| Signal type | Examples | Can influence | Cannot prove |
|---|---|---|---|
| Builder behavior | Repeated builder workflows, tool adoption patterns, development practices | Research questions, operational assumptions, capability hypotheses | Customer demand or willingness to pay |
| Market pattern | A recurring category, problem area, or product wedge | Market map, competitor scan, opportunity comparison | Market attractiveness by itself |
| Persona hint | Roles, founder types, operators, teams, or buyers mentioned | Manual respondent targeting, ICP hypotheses | Persona pain intensity |
| Channel hint | Communities, launch paths, distribution surfaces, ecosystem channels | Channel hypothesis, manual experiment ideas | Channel reachability or conversion |
| Product pattern | UX, workflow, agent, tool, automation, or monetization patterns | PRD questions, differentiation hypotheses, MAYA framing | That Pipe should build the same thing |
| Objection or risk | Trust, integration, cost, data, adoption, security, compliance, or workflow friction | Risk review, interview prompts, contradiction review | Actual blocker severity |
| Traction proxy | Stars, mentions, launches, public attention, usage claims, community activity | Research priority, false-positive warning | PMF, retention, revenue, or demand |
| Contradiction signal | Evidence that an idea is crowded, weak, hard to reach, or dependent on public APIs | Confidence decrease, follow-up research | Kill decision without stronger evidence |

## Signal Capture Template

```md
# BuilderPulse Signal Review

## Metadata

- Origin ticket:
- Reviewer:
- Review date:
- BuilderPulse source URL:
- Publication date:
- Related idea or venture:
- Related repository artifact:
- Human review required before priority change: yes

## Source Summary

- What BuilderPulse showed:
- Source quality:
- Known limitations:
- Potential false-confidence risk:

## Signals

| Signal | Type | Source detail | Relevance | Confidence | Affected assumption | Evidence still needed |
|---|---|---|---|---|---|---|
|  | Builder behavior / market pattern / persona hint / channel hint / product pattern / objection or risk / traction proxy / contradiction |  | Low / Medium / High | Low / Medium / High |  |  |

## Comparison Against Pipe Evidence

| Existing assumption | BuilderPulse signal | Supports / contradicts / expands / unclear | Decision impact | Evidence still needed |
|---|---|---|---|---|
|  |  |  |  |  |

## Insufficiency Check

| Question | Answer | Required next evidence |
|---|---|---|
| Does this signal come from target customers? | yes/no/unknown | Customer interviews, observed behavior, or approved customer evidence |
| Does it show pain intensity? | yes/no/unknown | Customer quote, repeated workaround, urgent request, support thread |
| Does it show willingness to engage or pay? | yes/no/unknown | Discovery call, pilot request, budget signal, paid substitute |
| Does it prove channel reachability? | yes/no/unknown | Manual channel test, qualified replies, discovery meetings |
| Does it support a public/customer-facing claim? | yes/no/unknown | Sourced proof and human review |
| Could it create false confidence? | yes/no | Contradiction review and score cap |

## Decision

- Decision: Advisory input / Research follow-up / Discovery follow-up / Ranking adjustment proposal / Blocked-insufficient
- Rationale:
- Allowed next action:
- Blocked actions:
- Scorecard impact:
- Human review required:
- Follow-up ticket:
```

## Sufficient vs Insufficient Use

### BuilderPulse signals are sufficient for

- generating research questions
- identifying comparable products, categories, or builder workflows
- suggesting manual respondent targeting hypotheses
- suggesting interview questions
- identifying possible channel hypotheses
- surfacing risks, objections, and contradictions
- creating a specific research or discovery follow-up ticket
- lowering confidence when signals contradict unsupported assumptions

### BuilderPulse signals are not sufficient for

- raising critical validation scorecard categories alone
- proving market demand
- proving pain intensity
- proving willingness to engage or pay
- proving product-market fit
- proving channel reachability
- making customer-facing claims
- creating build, monetization, pricing, billing, launch, or paid acquisition tickets
- replacing customer interviews, fake-door tests, manual validation, or sourced research

When in doubt, cap BuilderPulse influence at score `1` in `validation/validation-scorecard.md` until stronger evidence exists.

## Manual Review Cadence

Default cadence:

- review manually only when a Linear ticket asks for it
- prefer focused review tied to a specific idea, market, persona, or channel question
- avoid open-ended browsing that produces unowned signal noise

Optional cadence after future approval:

- weekly or biweekly manual review by a market intelligence owner
- no automation unless an approved ticket defines source access, rate limits, privacy, security, observability, and stop conditions

## Follow-Up Ticket Criteria

Create a follow-up ticket only when the signal produces a specific next action:

- research a named market, competitor, claim, source, channel, or workflow
- test a named persona or objection through manual discovery
- update a validation plan with concrete questions
- compare a concrete BuilderPulse signal against an existing idea ranking
- propose a human-reviewed ranking change

Do not create follow-ups for:

- generic trend watching
- vanity traction
- unsupported hype
- broad market curiosity
- automated scraping or polling
- automatic Linear ticket creation
- priority changes without source artifacts

## Done Criteria

This workflow is complete when:

- BuilderPulse has a bounded manual monitoring process
- every signal can be logged with source, date, relevance, confidence, and type
- signals remain advisory unless stronger evidence exists
- scorecard influence is capped
- follow-up criteria are explicit
- automation remains excluded unless separately approved

## Relationship To Existing Artifacts

- Use `validation/respondent-targeting-and-interview-planner.md` when BuilderPulse suggests personas to find manually.
- Use `validation/validation-scorecard.md` for evidence scoring and insufficiency checks.
- Use `validation/market-validation-before-code-gate.md` before downstream PRD, build, growth, monetization, or customer-facing work.
- Use `growth/builderpulse-idea-ranking-contrast-workflow.md` when a captured signal needs to strengthen, weaken, question, or have no impact on an internal idea ranking.
- Use `growth/idea-browser-validation-workflow.md` when BuilderPulse signals overlap with idea-comparison surfaces.
- Use `knowledge/knowledge-curator-workflow.md` if repeated BuilderPulse patterns should become durable knowledge.
