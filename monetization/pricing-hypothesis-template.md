# Pricing Hypothesis Template

Use this template after validation shows enough evidence to ask pricing and willingness-to-pay questions.

This template does not authorize billing, payment collection, subscriptions, invoices, paid pilots, Stripe setup, checkout, tax/accounting automation, or external customer communication. It only structures a pricing hypothesis and the evidence needed before billing work can be considered.

## Boundary

Pricing validation is not billing implementation.

Allowed by this template:

- define a buyer and economic decision-maker hypothesis
- define a value anchor
- define a pricing metric
- identify existing spend, budget, time cost, or manual workaround cost
- design a manual willingness-to-pay test after approval
- define GO / NO-GO thresholds
- record evidence gaps and risks

Not allowed by this template:

- implement Stripe, checkout, subscriptions, invoices, payment links, tax, accounting, or entitlement logic
- collect payment details or pricing commitments without explicit approval
- send external pricing messages, proposals, or paid-pilot offers without explicit approval
- claim revenue, willingness to pay, customer commitments, or pricing validation without source artifacts
- treat competitor pricing, synthetic personas, or founder opinion as proof of willingness to pay

## Required Inputs

- Product or idea:
- Origin ticket:
- Owner:
- Date:
- Founder focus artifact:
- C.O.N.T.R.O.L.E. evaluation:
- Validation scorecard:
- Market Validation Before Code gate decision:
- ICP profile:
- MVP scope or core loop:
- Distribution or channel artifact, if relevant:
- Customer discovery or research artifacts:
- Approval record for any external pricing test:

Only continue when validation has at least one sourced signal related to budget, existing spend, time cost, manual workaround cost, economic buyer, paid substitute, paid pilot interest, or procurement path.

If the strongest signal is internal opinion, synthetic persona output, or competitor pricing alone, mark this template as `NO-GO` and return to validation.

## Buyer And Value Hypothesis

| Field | Hypothesis | Source artifact | Confidence | Evidence gap |
|---|---|---|---|---|
| Primary user |  |  | Low / Medium / High |  |
| Economic buyer |  |  | Low / Medium / High |  |
| Approver or procurement path |  |  | Low / Medium / High |  |
| Current paid substitute or workaround |  |  | Low / Medium / High |  |
| Current time, labor, budget, or risk cost |  |  | Low / Medium / High |  |
| Value anchor |  |  | Low / Medium / High |  |
| Urgency or trigger event |  |  | Low / Medium / High |  |

## Value Anchor

Define the concrete value the buyer might pay for.

- Primary value anchor:
- Value category: time saved / cost reduced / revenue enabled / risk reduced / quality improved / workflow speed / compliance support / other
- Current cost of the problem:
- Current workaround:
- Why this value matters now:
- What evidence supports the value anchor:
- What remains assumption:

Do not use broad value language such as "AI productivity" or "platform efficiency" without a specific buyer outcome and source artifact.

## Pricing Metric

Choose one primary pricing metric for the first hypothesis.

| Candidate metric | When it fits | Risk |
|---|---|---|
| Per user / seat | Value scales with number of active users. | Can mismatch buyer value when usage is team-wide but buyer wants outcome pricing. |
| Per workflow / case / job | Value ties to completed work units. | Requires clear definition of a unit. |
| Per document / report / output | Output is the core deliverable. | Can encourage volume over quality. |
| Per account / workspace | Buyer values team access and administration. | Can be too abstract before MVP value is proven. |
| Usage-based | Cost and value scale with usage. | Can create uncertainty for early buyers. |
| Flat monthly fee | Simple first commercial test. | May hide whether value scales with outcome. |
| Manual paid pilot | Useful for learning before productized billing. | Requires explicit approval and careful scope. |

Selected metric:

- Metric:
- Unit definition:
- Why this metric matches buyer value:
- Why other metrics are excluded for now:
- Risk if wrong:
- Revisit trigger:

## Price Range Hypothesis

This section captures a hypothesis, not validated pricing.

| Field | Low | Target | High | Source or rationale |
|---|---:|---:|---:|---|
| Price range |  |  |  |  |
| Buyer value estimate |  |  |  |  |
| Current workaround cost |  |  |  |  |
| Substitute price, if sourced |  |  |  |  |
| Manual delivery cost |  |  |  |  |

- Why the target price could be acceptable:
- What would make it too high:
- What would make it too low to sustain:
- What evidence is missing:

Do not publish, quote, charge, invoice, or collect this price unless a later approved ticket explicitly authorizes it.

## Willingness-To-Pay Evidence

Use evidence strength from strongest to weakest.

| Evidence type | Present? | Source artifact | Notes |
|---|---|---|---|
| Paid commitment, pre-order, signed paid pilot, or LOI | Yes / No |  |  |
| Existing spend on substitute, agency, consultant, software, labor, or manual process | Yes / No |  |  |
| Buyer explicitly discusses budget, procurement, or payment path | Yes / No |  |  |
| User commits time, data, workflow access, or pilot participation | Yes / No |  |  |
| Repeated pain with measurable cost or urgency | Yes / No |  |  |
| Sourced competitor/substitute pricing | Yes / No |  |  |
| Internal assumption or synthetic persona output | Yes / No |  | Not sufficient by itself. |

Minimum evidence before pricing GO:

- There is an identified buyer or approver.
- There is at least one sourced willingness-to-pay, budget, spend, time-cost, or paid-substitute signal.
- The pricing metric is tied to a concrete value anchor.
- The next test does not require billing infrastructure by default.
- Any external pricing conversation, paid pilot, or proposal has explicit human approval.

## Pricing Test Design

Use the smallest approved test that can reduce uncertainty.

| Test method | Use when | Approval needed | Output |
|---|---|---|---|
| Discovery question | Need to understand existing spend, budget, buyer, or procurement path. | Customer discovery approval if external. | Buyer economics and objections. |
| Manual offer review | Need reaction to a manually scoped offer. | External communication approval. | Objections, perceived value, price sensitivity. |
| Fake-door pricing copy | Need non-payment intent signal. | Public claim/growth approval before publishing. | Qualified interest, but not payment proof. |
| Concierge paid pilot | Need paid validation before productized billing. | Explicit paid pilot and payment handling approval. | Strong WTP evidence, if executed safely. |
| Substitute pricing research | Need market context. | Research approval when external research is required. | Context only, not customer proof. |

Selected test:

- Test method:
- Hypothesis:
- Target buyer or persona:
- External action involved: yes/no
- Approval required: yes/no
- Approval record or blocker:
- Test script or artifact:
- Evidence to collect:
- Privacy or sensitive data concerns:
- What would count as a positive signal:
- What would count as a negative signal:

## GO / NO-GO Thresholds

Define thresholds before running the test.

| Decision | Condition | Allowed next action |
|---|---|---|
| GO | Strong sourced willingness-to-pay signal exists, buyer is clear, value anchor is concrete, and no billing is needed yet or billing has separate approval. | Update validation/PRD/MVP artifacts and create a scoped follow-up ticket. |
| CONDITIONAL GO | Buyer/value/metric are plausible but one evidence gap remains and a narrow test is approved. | Run only the approved next pricing validation step. |
| REFINE | Pricing metric, buyer, or value anchor is unclear. | Return to discovery, validation scorecard, or market research. |
| NO-GO | Pricing is speculative, buyer is unclear, evidence is internal/synthetic only, or billing/payment collection is requested before validation. | Do not create billing or monetization implementation tickets. |
| BLOCKED | External action, paid pilot, sensitive data, legal/financial claim, or payment handling is needed without approval. | Stop and request human approval. |

Thresholds for this hypothesis:

- GO threshold:
- CONDITIONAL GO threshold:
- REFINE trigger:
- NO-GO trigger:
- BLOCKED trigger:

## Approval And Risk

- Does this touch billing, payment collection, paid pilot, invoice, subscription, checkout, tax, or accounting? yes/no
- Does this require external customer communication? yes/no
- Does this mention financial, legal, compliance, privacy, security, or sensitive claims? yes/no
- Does this handle customer data, payment details, credentials, or production data? yes/no
- Approval required before next step: yes/no
- Approval source:
- Risk level: Low / Medium / High
- Risk reviewer needed: yes/no
- Blocker:

If any answer introduces billing, payment collection, external customer communication, customer data, paid acquisition, sensitive claims, or legal/financial/compliance implications, stop unless explicit approval exists.

## PRD And Backlog Handoff

Carry forward only sourced decisions.

- PRD field affected:
- MVP scope implication:
- Validation scorecard update needed:
- Distribution/channel implication:
- Knowledge record needed:
- Follow-up Linear ticket needed:
- Follow-up ticket title:
- Follow-up scope:
- Explicitly blocked from follow-up:

Do not create a billing implementation ticket unless:

- willingness-to-pay evidence is sourced;
- buyer and value anchor are clear;
- billing is the next riskiest assumption to test;
- legal/financial/privacy/security risks are reviewed when relevant;
- human approval explicitly authorizes billing/payment handling.

## Completion Check

- Buyer or economic decision-maker is named.
- Value anchor is concrete and sourced or marked as assumption.
- Pricing metric is selected and justified.
- Willingness-to-pay evidence is separated from assumptions.
- Test method is narrow and approved when external.
- GO / NO-GO / BLOCKED thresholds are explicit.
- Billing implementation remains excluded unless separately approved.
- No revenue, willingness-to-pay, or customer-commitment claim is invented.
