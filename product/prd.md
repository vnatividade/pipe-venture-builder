# Lean PRD Template

Use this template only after founder focus, C.O.N.T.R.O.L.E., validation scorecard, ICP, and MVP scope exist.

A PRD translates validated learning into product decisions. It must not invent customer evidence, requirements, integrations, metrics, revenue, or roadmap commitments.

Do not create this PRD when validation is still internal opinion, synthetic persona output, or an unresolved C.O.N.T.R.O.L.E. Pivot / Kill.

Before creating this PRD, apply `validation/market-validation-before-code-gate.md`. Continue only when the gate decision is GO or an explicitly approved CONDITIONAL GO.

## Required Inputs

- Product or idea name:
- Date:
- Owner:
- Founder focus artifact:
- C.O.N.T.R.O.L.E. evaluation:
- C.O.N.T.R.O.L.E. verdict:
- Validation scorecard:
- Validation decision:
- Market Validation Before Code gate decision:
- Market Validation Before Code approval record or blocker:
- Data moat strategy, if applicable:
- API dependency risk assessment, if applicable:
- ICP profile:
- Customer-language memory:
- MVP scope gate:
- MVP core loop:
- Risk review:
- Human approval before architecture or implementation tickets:
- Approval record or blocker:

Only continue if validation supports GO or approved CONDITIONAL GO and the MVP core loop is explicit.

## Problem Evidence

State the problem using sourced evidence.

| Evidence | Type | Source artifact | Confidence | Product implication |
|---|---|---|---|---|
|  | Customer quote / observed behavior / workaround / spend / validation score / assumption |  | Low / Medium / High |  |

- Primary customer problem:
- Current workaround or status quo:
- Trigger event:
- Cost of inaction:
- What is still assumption:

Do not treat assumptions as requirements.

## PMF Triad

Summarize the market validation that justifies creating this PRD.

| Element | Decision | Source artifact | Remaining uncertainty |
|---|---|---|---|
| What to sell |  |  |  |
| To whom |  |  |  |
| How to reach them |  |  |  |

If any element is broad, unsourced, or only internally assumed, stop and return to validation.

## Data Moat Hypothesis

Use `architecture/proprietary-data-moat-strategy.md` when the venture depends on proprietary data, workflow learning, personalization, accumulated evidence, or operational feedback.

| Field | Decision | Source artifact | Risk or uncertainty |
|---|---|---|---|
| Data moat hypothesis |  |  |  |
| Why it compounds |  |  |  |
| Data category | Strategic learning / operational workflow data / customer evidence / sensitive / prohibited / synthetic / Public/reference data |  |  |
| Allowed capture |  |  |  |
| Data explicitly avoided |  |  |  |
| Learning loop |  |  |  |
| Promotion criteria |  |  |  |
| Retention expectation |  |  |  |
| Privacy/trust risk |  |  |  |
| Mitigation |  |  |  |

If the MVP does not depend on a data moat yet, state that explicitly. Do not convert synthetic examples, internal assumptions, or generic model output into customer evidence.

## API Dependency Risk

Use `architecture/api-dependency-risk-assessment.md` when the venture depends on public APIs, model providers, third-party platforms, marketplaces, app stores, enterprise systems, or integration partners.

| Field | Decision | Source artifact | Risk or uncertainty |
|---|---|---|---|
| External dependency |  |  |  |
| Dependency role | Core value / workflow support / infrastructure / optional enhancement |  |  |
| MVP necessity | Required for MVP / can be manual / can be deferred |  |  |
| Risk level | Low / Medium / High |  |  |
| Substitution risk | Low / Medium / High |  |  |
| Provider-change risk | Pricing / rate limits / policy / model behavior / roadmap / availability / permissions |  |  |
| Defensibility beyond API | Workflow depth / proprietary data / UX / compliance / distribution / integration moat / trust / switching cost |  |  |
| Mitigation |  |  |  |
| Fallback path |  |  |  |
| Revisit trigger |  |  |  |

Medium or high API dependency risk without explicit mitigation is a blocker before architecture or implementation tickets. If the MVP does not materially depend on external APIs, state that explicitly.

## ICP And User Boundary

- Initial ICP:
- Primary user:
- Buyer or approver, if different:
- Excluded users or segments:
- First channel or access path:
- Privacy, trust, or data constraints:

## MVP Core Loop

Copy the core loop from `product/mvp-scope.md`.

| Element | Decision |
|---|---|
| Core user |  |
| Core job |  |
| Core action |  |
| Core result |  |
| Core feedback signal |  |
| Learning loop |  |

If the PRD adds a second core user, job, or result, stop and revise MVP scope before continuing.

## Goals

Goals must connect to the evidence and MVP core loop.

| Goal | Evidence or MVP link | Success signal |
|---|---|---|
|  |  |  |

## Non-Goals

Non-goals are binding scope controls for this PRD.

| Non-goal | Why excluded | Revisit condition |
|---|---|---|
| Enterprise staffing plan | Outside lean PRD scope | Separate operating model ticket after product evidence |
| Speculative long roadmap | Premature before MVP learning | Revisit after repeated validated use |
| Broad platform scope | MVP must prove one core loop first | Revisit when core loop threshold is met |
| Billing | Excluded unless payment is the riskiest assumption | Revisit when willingness-to-pay evidence requires it |
| Growth automation | Premature before validated retention or willingness exists | Revisit after manual channel signal |
|  |  |  |

## Metrics And Evidence Thresholds

Use metrics only when their source and threshold are clear.

| Metric or signal | Threshold | Source | Decision it informs |
|---|---|---|---|
| Activation or first-use behavior |  | MVP scope / validation scorecard |  |
| Core result achieved |  | MVP scope / validation scorecard |  |
| Feedback or learning signal |  | MVP scope / validation scorecard |  |
| Willingness to continue |  | validation scorecard / ICP |  |
| Risk or objection resolved |  | risk review / ICP |  |

Do not invent baseline metrics, market proof, revenue, willingness to pay, or customer commitments.

## User Stories

Keep stories tied to the core loop.

| Story | User | Evidence source | Priority | Acceptance signal |
|---|---|---|---|---|
| As a ..., I want ..., so that ... |  |  | Must / Should / Later |  |

## Requirements

### Functional Requirements

| Requirement | Linked story or evidence | Priority | Acceptance criteria |
|---|---|---|---|
|  |  | Must / Should / Later |  |

### Non-Functional Requirements

| Requirement | Why it matters | Risk or constraint | Acceptance criteria |
|---|---|---|---|
|  |  |  |  |

## States And Edge Cases

Define the minimum states needed for architecture and implementation planning.

| State or edge case | Expected behavior | Evidence or risk source | Acceptance criteria |
|---|---|---|---|
| Empty state |  |  |  |
| Loading or waiting |  |  |  |
| Error or failed path |  |  |  |
| Manual review needed |  |  |  |
| Privacy or data boundary |  |  |  |

## Risks

Use `execution/risk-reviewer-matrix-lite.md` for material risks.

| Risk | Category | Severity | Mitigation | Owner | Status |
|---|---|---|---|---|---|
|  | Product / Technical / Legal / Financial / Privacy / Security / Operational | P0 / P1 / P2 / P3 |  |  | Open / Mitigated / Accepted / Blocked |

P0 and P1 risks must be mitigated or remain blocking before architecture or implementation tickets proceed. Any proposed risk acceptance requires explicit human approval and does not override unresolved P0/P1 review findings.

## Acceptance Criteria

The PRD is ready for architecture review when:

- C.O.N.T.R.O.L.E. verdict is linked and not Pivot or Kill
- validation scorecard is linked and supports GO or approved CONDITIONAL GO
- Market Validation Before Code gate decision is GO or approved CONDITIONAL GO
- PMF triad is specific and sourced
- data moat hypothesis is completed or explicitly marked not applicable
- API dependency risk is completed or explicitly marked not applicable
- API dependency risk is Low, or Medium/High risk has explicit mitigation and fallback
- ICP profile is linked and specific
- MVP core loop is copied from `product/mvp-scope.md`
- non-goals are explicit and binding
- requirements trace back to evidence, MVP scope, or risk review
- states and edge cases are sufficient for architecture review
- P0/P1 risks are handled or blocking
- human approval before architecture or implementation tickets is recorded

## Handoff

- Architecture questions:
- Implementation ticket candidates:
- Validation follow-ups:
- KDR/DAR update needed:
- Decision conflict scan needed:
- Known residual risks:
