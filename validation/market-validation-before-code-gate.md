# Market Validation Before Code Gate

Use this gate before creating PRD, architecture, implementation, growth, monetization, or build tickets for a venture idea.

This gate turns market validation into an explicit execution control. It does not replace founder focus, C.O.N.T.R.O.L.E., customer discovery, the validation scorecard, ICP, or MVP scope. It checks whether those artifacts contain enough evidence to justify moving from upstream learning into downstream build work.

## Purpose

The Pipe should validate market risk before investing agentic execution capacity in product definition or implementation.

This gate protects against:

- building from founder excitement instead of customer evidence
- treating synthetic persona output as validation
- advancing broad ICPs or platform-sized wedges
- creating PRD or build tickets without a clear channel
- skipping human approval when evidence is incomplete
- using documentation or governance tickets as if they required customer validation

## When This Gate Applies

Apply this gate to:

- PRD creation for a product or venture idea
- MVP scope that enables architecture or implementation tickets
- architecture tickets tied to a specific venture/product build
- implementation, code, automation, integration, growth, monetization, pricing, billing, or customer-facing tickets
- tickets that create or change customer-facing product claims

Do not apply this gate as a blocker to:

- repository setup
- governance-only documentation
- agent operating protocols
- Linear workflow improvements
- internal validation templates
- research-only tickets
- analysis or synthesis artifacts that do not authorize build work

For non-product repository work, record `Gate decision: NOT APPLICABLE` and use the rationale field to note the non-product, governance, documentation, research, template, or internal operating scope.

## Required Inputs

Complete or link the strongest available versions of:

- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `validation/validation-scorecard.md`
- `validation/icp-profile.md`
- customer discovery or research artifacts, when available
- `product/mvp-scope.md`, when moving toward architecture or implementation
- explicit human approval record, when evidence is incomplete or conditional

Do not use conversational memory as the only source for any required input.

## Minimum Evidence Standard

Before PRD or build work, the evidence must answer the PMF triad:

| PMF element | Minimum evidence needed | Acceptable sources |
|---|---|---|
| What to sell | A narrow offer, job, or promised result tied to a real pain | Validation scorecard, customer quote, observed workaround, research synthesis, founder focus |
| To whom | A specific ICP, buyer/user distinction, trigger event, and exclusions | ICP profile, discovery notes, validation scorecard, market research |
| How to reach them | A plausible first channel or access path with a testable engagement signal | Product context, validation scorecard, channel experiment, customer discovery |

The evidence does not need to prove full product-market fit. It must be strong enough to justify the next step and specific enough to prevent building a vague platform.

## Evidence Quality Rules

Evidence strength, from strongest to weakest:

1. observed customer behavior, current workaround, spend, repeated request, pilot participation, or paid commitment
2. exact customer language from approved, retained discovery artifacts
3. qualified waitlist, intro, scheduled call, or willingness to share relevant context
4. credible market research or source-cited external signal
5. internal assumption, founder opinion, or synthetic persona output

Internal assumptions and synthetic personas may generate hypotheses. They do not satisfy this gate by themselves.

## Gate Decision

Choose one decision.

| Decision | Condition | Allowed next action |
|---|---|---|
| GO | Validation scorecard is GO; PMF triad is answered; ICP is specific; channel hypothesis is explicit; no critical evidence category is 0 | Create PRD, MVP scope, architecture, or build tickets with human approval |
| CONDITIONAL GO | Validation scorecard is CONDITIONAL GO; gaps are named; a human approves the next limited step | Create only the approved narrow PRD, MVP, architecture, or validation-supporting ticket |
| REFINE | Evidence is incomplete, uneven, or too broad; next learning step is clear | Create validation/research/focus tickets only |
| NO-GO | Critical category is 0, C.O.N.T.R.O.L.E. is Pivot/Kill, ICP is broad, or strongest evidence is internal/synthetic | Stop build path; record learning and next research question |
| NOT APPLICABLE | Ticket is non-product governance, documentation, research, template, or internal operating work | Proceed under normal ticket readiness and validation rules |

## Human Approval Rules

Human approval is required before creating or executing downstream product/build tickets when:

- decision is GO or CONDITIONAL GO
- evidence is incomplete but a narrow next step is desired
- the next step changes customer-facing claims
- the next step touches growth, monetization, pricing, billing, customer outreach, external communication, production data, customer data, legal, privacy, compliance, or security-sensitive material

Approval must name:

- what gap is accepted
- what action is approved
- what remains blocked
- where the approval is recorded

Silence, inferred intent, or old conversation context is not enough.

## Ticket Creation Rules

Product, architecture, implementation, integration, growth, or monetization tickets should include:

- Market Validation Before Code gate decision
- linked validation scorecard
- linked ICP profile
- PMF triad summary
- evidence gaps
- approval record or blocker
- explicit NO-GO conditions

If the gate result is REFINE or NO-GO, create only validation, research, focus, or learning tickets.

## Manual Gate Template

```md
## Market Validation Before Code Gate

- Product or idea:
- Evaluator:
- Date:
- Ticket or artifact requesting downstream work:

## Source artifacts
- Founder focus:
- C.O.N.T.R.O.L.E. evaluation:
- Validation scorecard:
- ICP profile:
- MVP scope, if applicable:
- Customer discovery or research:

## PMF triad
- What to sell:
- To whom:
- How to reach them:

## Evidence quality
- Strongest evidence:
- Weakest required evidence:
- Assumptions still open:
- Synthetic or internal-only evidence:

## Decision
- Gate decision: GO / CONDITIONAL GO / REFINE / NO-GO / NOT APPLICABLE
- Rationale:
- Human approval required:
- Approval record or blocker:

## Allowed next action
- Allowed:
- Not allowed:
- Follow-up validation needed:
```

## Example Outcomes

### Documentation-only governance ticket

- Gate decision: NOT APPLICABLE
- Reason: no product, customer-facing claim, build, growth, monetization, or architecture decision is being authorized
- Allowed next action: proceed with documentation validation

### Technical feature for a validated MVP

- Gate decision: GO or CONDITIONAL GO
- Required evidence: linked validation scorecard, ICP, MVP core loop, evidence threshold, and approval record
- Allowed next action: architecture or implementation ticket scoped to the validated MVP loop

### New product idea with founder opinion only

- Gate decision: NO-GO or REFINE
- Required next action: founder focus, C.O.N.T.R.O.L.E., customer discovery, research, or validation scorecard
- Not allowed: PRD, implementation, growth automation, monetization, or build tickets

## Handoff

When this gate changes the next action, record the decision in the relevant Linear ticket or handoff:

- gate decision
- source artifacts reviewed
- approval record or blocker
- allowed next action
- blocked actions
- follow-up validation tickets, if needed
