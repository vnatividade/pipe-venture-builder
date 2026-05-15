# Lean PRD Template

Use this template only after founder focus, C.O.N.T.R.O.L.E., validation scorecard, ICP, and MVP scope exist.

A PRD translates validated learning into product decisions. It must not invent customer evidence, requirements, integrations, metrics, revenue, or roadmap commitments.

Do not create this PRD when validation is still internal opinion, synthetic persona output, or an unresolved C.O.N.T.R.O.L.E. Pivot / Kill.

## Required Inputs

- Product or idea name:
- Date:
- Owner:
- Founder focus artifact:
- C.O.N.T.R.O.L.E. evaluation:
- C.O.N.T.R.O.L.E. verdict:
- Validation scorecard:
- Validation decision:
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
