# Validation Scorecard

Use this scorecard after `product/founder-focus.md` and `product/controle-evaluation.md`.

This template decides whether an idea has enough measurable validation to move toward PRD, build tickets, growth, or monetization. It cannot be satisfied by internal opinion, synthetic personas, or founder excitement alone.

Use `validation/venture-validation-framework.md` before scoring when the idea needs clearer adoption, innovation-pattern, or PMF-triad questions. MAYA, the 8 Innovation Flavors, and PMF triad are heuristics for validation design; they are not scores and do not replace C.O.N.T.R.O.L.E.

Before creating downstream PRD, architecture, implementation, growth, monetization, or customer-facing build tickets, apply `validation/market-validation-before-code-gate.md`.

## Required Inputs

- Founder focus artifact:
- C.O.N.T.R.O.L.E. artifact:
- C.O.N.T.R.O.L.E. verdict:
- Date:
- Evaluator:
- Target market:
- Primary problem:
- Offer:
- Primary channel:
- PMF triad - what to sell:
- PMF triad - to whom:
- PMF triad - how to reach:
- MAYA adoption risk:
- Primary innovation flavor:

Only continue if the C.O.N.T.R.O.L.E. verdict is Attack or Refine with human approval.

## Evidence Rules

- Customer behavior is stronger than stated interest.
- Exact customer language is stronger than paraphrased interpretation.
- Repeated urgency is stronger than one-off curiosity.
- Willingness to pay or commit time is stronger than praise.
- Synthetic persona output may help generate hypotheses, but it is not validation evidence.
- MAYA, the 8 Innovation Flavors, and PMF triad help frame questions, but they do not count as validation evidence by themselves.
- Paid ads, automated outreach, and build work remain blocked until explicitly approved.

## Upstream Validation Lenses

Summarize the lenses used before scoring.

| Lens | Summary | Evidence or assumption | Risk if wrong |
|---|---|---|---|
| MAYA | What is advanced yet acceptable about the idea? |  |  |
| 8 Innovation Flavors | Which flavor best describes the opportunity? |  |  |
| PMF triad | What to sell, to whom, and how to reach them? |  |  |

If these lenses are based only on internal reasoning, keep the relevant scorecard categories low until external evidence exists.

## Scorecard

Score each category from 0 to 3.

- 0: no evidence
- 1: weak signal or internal assumption
- 2: plausible external signal that needs more proof
- 3: strong external evidence from observed behavior, repeated patterns, or commitment

| Category | Pressure-test question | Score | Evidence required | Notes/source |
|---|---|---:|---|---|
| Pain intensity | Does the target user describe the pain as urgent, costly, repeated, or emotionally salient? |  | Customer quote, observed behavior, support request, forum thread, manual discovery note |  |
| Status quo | Is the user already trying to solve this with a workaround, tool, spreadsheet, agency, manual process, or internal process? |  | Existing workaround, spend, time cost, process artifact, competitor usage |  |
| ICP specificity | Can we identify exactly who has the problem, when it occurs, and why this segment first? |  | Segment definition, trigger event, role, context, exclusion criteria |  |
| Wedge clarity | Is the initial wedge narrow enough to test manually without becoming a broad platform? |  | One focused use case, explicit non-goals, first channel, first offer |  |
| Observed evidence | Have we observed behavior beyond opinions or compliments? |  | Interview notes, waitlist with qualification, manual request, usage of workaround, pilot request |  |
| Willingness to engage | Will the user spend time, share data/context, join a pilot, introduce others, or help shape the solution? |  | Scheduled call, pilot participation, data sample, intro, repeated follow-up |  |
| Willingness to pay | Is there evidence of budget, existing spend, explicit paid intent, pre-order, paid pilot, or clear economic buyer? |  | Budget signal, current spend, paid pilot, LOI, pre-order, procurement path |  |
| C.O.N.T.R.O.L.E. alignment | Does the evidence strengthen the C.O.N.T.R.O.L.E. verdict instead of contradicting it? |  | Link to verdict rationale, changed assumptions, revised score, approval record |  |

## Thresholds

Calculate:

- Total score:
- Average score:
- Lowest scoring category:
- Highest scoring category:

Interpretation:

| Result | Threshold | Meaning | Allowed next action |
|---|---:|---|---|
| GO | 20-24 and no category below 2 | Strong enough to draft PRD or MVP scope with human approval | Move to PRD/Working Backwards readiness review |
| CONDITIONAL GO | 15-19 and no category below 1 | Promising but incomplete | Run targeted validation before PRD/build tickets |
| REFINE | 9-14 | Weak or uneven evidence | Refine focus, offer, channel, or validation plan |
| NO-GO | 0-8 or any critical category at 0 | Not enough validation | Stop build path; record learning and next research question |

Critical categories:

- Pain intensity
- ICP specificity
- Observed evidence
- C.O.N.T.R.O.L.E. alignment

If any critical category is 0, do not create PRD, growth, monetization, or build tickets.

## Pressure-Test Questions

Answer directly.

- What painful behavior have we observed, not just heard?
- What is the current workaround and why is it insufficient?
- Who is excluded from the first ICP?
- What makes the idea acceptable enough for the user to adopt now?
- Which innovation flavor is being tested, and what observable friction supports it?
- What is the PMF triad in one sentence: what to sell, to whom, and how to reach them?
- What is the smallest wedge that can prove the promise?
- What evidence would change the C.O.N.T.R.O.L.E. verdict?
- What would make this idea a Kill decision?
- What has the user committed: time, data, access, money, introduction, or repeated attention?
- What evidence is still only founder opinion?

## Decision

- Score interpretation:
- Decision: GO / CONDITIONAL GO / REFINE / NO-GO
- Rationale:
- Market Validation Before Code gate decision:
- Required human approval before build-ticket creation:
- Approval record or blocker:
- Next validation action:
- Next repository artifact:
- Linear ticket to create or update:

## NO-GO Rules

Do not advance to PRD, build, growth, or monetization when:

- validation is based only on internal opinion
- synthetic persona output is the strongest evidence
- willingness to engage or pay is unknown
- the ICP is still broad
- the wedge is still a platform-sized idea
- the C.O.N.T.R.O.L.E. verdict is Pivot or Kill
- any critical category scores 0

## Handoff

- Source artifacts reviewed:
- Evidence links:
- Customer-language snippets:
- Assumptions still open:
- Follow-up tickets:
