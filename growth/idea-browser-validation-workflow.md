# Idea Browser Validation Workflow

Use this workflow when Idea Browser or a similar idea-comparison surface provides signals that may help rank, compare, or refine venture ideas.

Idea Browser output is advisory. It can influence questions, ranking hypotheses, research priorities, and validation plans, but it does not replace customer discovery, validation scorecards, ICP evidence, PMF evidence, or human prioritization review.

## Boundary

This workflow does not authorize:

- treating Idea Browser output as real customer proof
- bypassing `validation/validation-scorecard.md`
- bypassing `validation/market-validation-before-code-gate.md`
- creating PRD, MVP, growth, monetization, or build tickets from Idea Browser output alone
- changing roadmap priority without human review
- publishing claims, outreach, paid spend, scraping, automation, or customer data handling

Idea Browser signals are not interviews, commitments, spend, customer behavior, or PMF evidence.

## Purpose

Idea Browser can be useful when the Pipe needs to compare idea patterns, identify market or channel hypotheses, surface similar products, inspect positioning, or find contradictions before spending founder time on deeper discovery.

It is dangerous when agents treat it as validation proof.

This workflow keeps Idea Browser useful but bounded:

- capture signals
- classify signal type
- compare against existing repository evidence
- mark what is sufficient for advisory use
- mark what is insufficient for validation
- decide whether interviews, research, fake-door tests, or manual channel tests are required

## Required Inputs

Before using Idea Browser output, link:

- origin Linear ticket
- source Idea Browser artifact or exported summary
- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `validation/venture-validation-framework.md`, when PMF triad or MAYA questions are involved
- `validation/validation-scorecard.md`, when scoring may change
- `validation/icp-profile.md`, when persona or segment assumptions may change
- `growth/distribution-strategy-framework.md`, when channel assumptions may change
- `knowledge/knowledge-curator-workflow.md`, when a durable learning update is considered

If no source artifact exists, treat the Idea Browser output as an unverified note and do not update scoring or priority.

## Signal Types

Classify each signal before using it.

| Signal type | Examples | Can influence | Cannot prove |
|---|---|---|---|
| Similar idea pattern | Comparable products, common workflows, repeated problem framings | Research questions, differentiation hypotheses | Demand, willingness to pay, ICP fit |
| Market cluster | Many related ideas in a space | Market map, category naming, competitor scan | That the founder should enter the market |
| Persona hint | Suggested buyer/user/segment | Respondent targeting, ICP hypothesis | That the persona has pain or budget |
| Channel hint | Suggested acquisition path or distribution surface | Channel hypothesis, manual source ideas | Channel reachability or conversion |
| Positioning language | Repeated phrasing, category labels, promise patterns | Messaging hypotheses | Customer language or proof |
| Objection or risk hint | Trust, privacy, compliance, adoption, competition signals | Risk review, interview questions | Actual blocker severity |
| Traction proxy | Likes, launches, rankings, reviews, mentions | Research priority, false-positive warning | PMF, adoption, retention, revenue |
| Contradiction signal | Evidence that an idea may be crowded, weak, hard to reach, or low-trust | Contradiction review | Kill decision without stronger evidence |

## Sufficient vs Insufficient Use

### Idea Browser is sufficient for

- generating discovery questions
- identifying comparable ideas to research
- proposing ICP hypotheses
- proposing channel hypotheses
- surfacing possible objections
- creating contradiction prompts
- deciding which idea needs deeper validation first
- lowering confidence when signals contradict unsupported assumptions
- creating a research or discovery follow-up ticket

### Idea Browser is not sufficient for

- raising validation scorecard categories above weak external signal without supporting evidence
- satisfying critical validation categories by itself
- proving pain intensity
- proving willingness to engage or pay
- proving PMF
- proving channel reachability
- proving market size or demand
- making customer-facing claims
- creating build, PRD, monetization, pricing, billing, or launch tickets
- replacing interviews, manual tests, fake-door tests, or sourced research

## Signal Review Procedure

### 1. Capture Source

- Origin ticket:
- Idea Browser artifact:
- Date:
- Reviewer:
- Idea or venture:
- Source quality:
- Known limitations:

### 2. Classify Signals

| Signal | Type | Source detail | Confidence | Repository artifact affected | Notes |
|---|---|---|---|---|---|
|  | Similar idea / market cluster / persona / channel / positioning / objection / traction proxy / contradiction |  | Low / Medium / High |  |  |

### 3. Compare Against Existing Evidence

| Existing assumption | Idea Browser signal | Supports / contradicts / expands / unclear | Decision impact | Evidence still needed |
|---|---|---|---|---|
|  |  |  |  |  |

### 4. Insufficiency Check

| Question | Answer | Required next evidence |
|---|---|---|
| Does this signal come from real target customers? | yes/no/unknown | Interviews, observed behavior, or approved customer evidence |
| Does it show pain intensity? | yes/no/unknown | Customer quote, workaround, spend, repeated urgency |
| Does it show willingness to engage or pay? | yes/no/unknown | Commitment, pilot request, budget signal, paid substitute |
| Does it prove channel reachability? | yes/no/unknown | Manual channel test, qualified replies, discovery calls |
| Does it support a public/customer-facing claim? | yes/no/unknown | Sourced proof and human review |
| Could it create false confidence? | yes/no | Contradiction review and score cap |

### 5. Decision

Choose one.

| Decision | Use when | Allowed next action |
|---|---|---|
| Advisory input | Signals are useful but not enough to change priority or scoring. | Add questions to validation plan. |
| Research follow-up | Signals identify a specific source, market, competitor, or claim to verify. | Create research ticket or update research plan. |
| Discovery follow-up | Signals suggest a persona, channel, objection, or contradiction to test. | Create interview/respondent targeting or manual validation ticket. |
| Ranking adjustment proposal | Signals materially change relative attractiveness but need human review. | Propose priority change; do not auto-change roadmap. |
| Blocked / insufficient | Signals are weak, unsourced, vanity-based, or misleading. | Do not update score or priority. |

## Scorecard Influence Rules

Idea Browser output may appear in the validation scorecard only as:

- weak external signal
- assumption input
- research source
- contradiction prompt
- note/source for why a question matters

It must not:

- satisfy critical categories alone
- raise `Observed evidence` above weak signal
- raise `Willingness to engage` or `Willingness to pay` without real behavior
- override customer discovery
- replace C.O.N.T.R.O.L.E. or human approval

When in doubt, cap Idea Browser influence at score `1` until stronger source evidence exists.

## Workflow Template

```md
# Idea Browser Validation Review

## Metadata

- Idea or venture:
- Origin ticket:
- Reviewer:
- Date:
- Idea Browser artifact:
- Human review required before priority change: yes

## Source Summary

- What Idea Browser showed:
- Source quality:
- Known limitations:
- Potential false-confidence risk:

## Signals

| Signal | Type | Confidence | Supports / contradicts | Affected assumption | Evidence still needed |
|---|---|---|---|---|---|
|  | Similar idea / market cluster / persona / channel / positioning / objection / traction proxy / contradiction | Low / Medium / High |  |  |  |

## Validation Impact

- Founder focus impact:
- C.O.N.T.R.O.L.E. impact:
- ICP impact:
- PMF triad impact:
- Channel hypothesis impact:
- Validation scorecard impact:
- Distribution strategy impact:
- Growth backlog impact:

## Insufficiency Rules Applied

- Customer interviews still required:
- Manual validation still required:
- Sourced market research still required:
- Fake-door/channel experiment still required:
- Scorecard category capped:
- Priority change blocked until:

## Decision

- Decision: Advisory input / Research follow-up / Discovery follow-up / Ranking adjustment proposal / Blocked-insufficient
- Rationale:
- Allowed next action:
- Blocked actions:
- Human review required:
- Follow-up ticket:
```

## Follow-Up Ticket Criteria

Create a follow-up ticket only when the signal produces a specific next action:

- research a concrete source, competitor, market, channel, or claim
- test a specific persona or objection through discovery
- run a specific manual channel or fake-door experiment after approval
- update a validation plan with named questions
- propose a human-reviewed ranking change

Do not create follow-ups for:

- generic "explore market" ideas
- vanity traction
- unsupported AI-generated enthusiasm
- broad platform expansion
- automated scraping or outreach
- prioritization changes without source artifacts

## Done Criteria

This workflow is complete when:

- Idea Browser signals are classified by type
- sufficiency and insufficiency rules are explicit
- scorecard influence is capped unless stronger evidence exists
- interviews/manual validation requirements are named
- ranking or roadmap changes require human review
- the workflow remains advisory and cannot bypass validation gates

## Relationship To Existing Artifacts

- Use `validation/validation-scorecard.md` for evidence scoring.
- Use `validation/market-validation-before-code-gate.md` before downstream PRD, build, growth, monetization, or customer-facing work.
- Use `validation/respondent-targeting-and-interview-planner.md` when Idea Browser suggests personas to test.
- Use `growth/distribution-strategy-framework.md` when Idea Browser suggests a channel hypothesis.
- Use `growth/channel-experiment-template.md` or `growth/fake-door-landing-page-validation-workflow.md` only after approval and readiness gates.
- Use `knowledge/knowledge-curator-workflow.md` if repeated Idea Browser comparisons change future validation behavior.
