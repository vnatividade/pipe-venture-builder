# Branding And Prototype Readiness Gate

Use this optional gate before customer-facing code, prototype sharing, landing pages, onboarding flows, product trials, or interface implementation when brand, UI, or user-perception ambiguity could create avoidable learning noise.

This gate is contextual. It does not replace `validation/market-validation-before-code-gate.md`, `validation/pre-user-security-privacy-readiness-gate.md`, PRD, MVP scope, or human approval gates.

## Purpose

Pipe should not build customer-facing surfaces when the team cannot tell whether user feedback is about the problem, offer, workflow, wording, trust signal, or an unfinished visual/prototype layer.

This gate protects against:

- starting customer-facing UI before the brand or product promise is understandable
- testing with confusing placeholder copy or generic names that distort validation
- implementing screens before critical UX assumptions are named
- presenting an interface that implies unsupported maturity, security, privacy, compliance, integrations, billing, or market proof
- forcing branding work onto internal governance, research, documentation, or back-office tickets

## Gate Relationship

The Market Validation Before Code gate remains the upstream business-evidence gate.

This gate only checks whether a customer-facing surface has enough brand, prototype, and UX clarity for the next approved step.

If Market Validation Before Code is `REFINE`, `NO-GO`, or missing when it applies, this gate cannot make the work ready. Record the branding/prototype result as informational and return to validation.

## When This Gate Applies

Classify this gate for tickets that create or materially change:

- customer-facing screens
- onboarding, landing pages, fake-door tests, forms, surveys, or waitlists
- clickable prototypes or prototype-sharing flows
- external product demos
- product trial surfaces
- customer-facing copy, names, promises, claims, or trust signals
- design-system or visual foundations required for a customer-facing MVP

Do not use this gate as a blocker for:

- internal governance or operating docs
- research-only or validation-planning tickets
- backend, data, or infrastructure work with no user-visible surface
- agent workflow docs that are not exposed to external participants
- documentation templates that do not authorize a product build
- early idea intake before the venture has reached a customer-facing test

For internal, documentation, research, governance, or back-office tickets, record `Gate decision: NOT APPLICABLE` when useful.

## Decision Options

| Decision | Use when | Allowed next action |
|---|---|---|
| REQUIRED | Customer-facing build or sharing would be misleading, hard to test, or high-ambiguity without brand/prototype readiness. | Complete the missing readiness items before the customer-facing build or exposure. |
| OPTIONAL | Brand/prototype clarity would improve learning quality, but the next step can proceed with explicit caveats. | Proceed only if caveats, assumptions, and residual UX risks are recorded. |
| NOT APPLICABLE | The work is internal, documentary, research-only, non-user-facing, or does not authorize customer exposure. | Proceed under normal ticket readiness and validation rules. |
| BLOCKED | Missing brand/prototype clarity would create unsafe claims, privacy/security confusion, unsupported maturity, or unusable validation. | Stop until scope, claims, prototype, or approval is fixed. |

## Readiness Checks

Complete only the checks relevant to the current stage.

| Area | Question | Status | Required action if not ready |
|---|---|---|---|
| Product name or label | Can a participant understand what the thing is called for this test? | Ready / Gap / N/A | Define a working name or neutral label. |
| Promise clarity | Does the surface state the promised result without unsupported claims? | Ready / Gap / N/A | Rewrite as sourced promise, hypothesis, or prototype copy. |
| Audience fit | Does copy and visual framing match the current ICP and excluded users? | Ready / Gap / N/A | Align with ICP or mark assumptions. |
| Trust signal | Are privacy, data, safety, billing, or credibility expectations clear enough for the test? | Ready / Gap / N/A | Add lightweight trust/support/disclaimer copy or stop. |
| Basic design tokens | Are minimum colors, type, spacing, and component states defined enough to avoid visual churn? | Ready / Gap / N/A | Define simple tokens or reuse an existing design system. |
| Screen prototype | Is there a sketch, wireframe, clickable prototype, or screen description for the user-facing path? | Ready / Gap / N/A | Create the smallest useful prototype artifact before implementation. |
| Core user flow | Is the first interaction path clear enough to build or test? | Ready / Gap / N/A | Map the core screen sequence or stop. |
| UX assumptions | Are unknowns about comprehension, trust, effort, and motivation named? | Ready / Gap / N/A | Record assumptions and validation questions. |
| Prototype fidelity | Is the fidelity appropriate for the learning goal? | Ready / Gap / N/A | Lower or raise fidelity intentionally. |
| Claim boundary | Does the surface avoid implying unavailable product maturity, validation, integrations, security, privacy, compliance, or billing readiness? | Ready / Gap / N/A | Remove, source, or gate the claim. |

## Required Inputs

When this gate is `REQUIRED` or `OPTIONAL`, link or summarize:

- Market Validation Before Code gate decision
- PRD or Working Backwards artifact, if available
- MVP scope and smallest ethical test
- ICP or target participant
- customer-facing copy or promise draft
- screen sketch, prototype, wireframe, or screen description
- design tokens or design-system source, when relevant
- assumptions and caveats that should be tested
- Pre-User Security And Privacy gate, when real users or external participants will touch the artifact

## Manual Gate Template

```md
## Branding And Prototype Readiness Gate

- Product or idea:
- Origin ticket:
- Evaluator:
- Date:
- Customer-facing surface:

## Source artifacts
- Market Validation Before Code gate:
- PRD or Working Backwards:
- MVP scope:
- ICP or participant:
- Prototype or screen artifact:
- Copy or promise draft:
- Design tokens or design source:
- Pre-user security/privacy gate, if applicable:

## Readiness summary
- Product name or label:
- Promise clarity:
- Audience fit:
- Trust signal:
- Basic design tokens:
- Screen prototype:
- Core user flow:
- UX assumptions:
- Prototype fidelity:
- Claim boundary:

## Decision
- Gate decision: REQUIRED / OPTIONAL / NOT APPLICABLE / BLOCKED
- Rationale:
- Required before customer-facing build or exposure:
- Caveats if proceeding:
- Approval record or blocker:
- Follow-up needed:
```

## Handoff Rules

When this gate applies, the Linear ticket, PR, or validation artifact should record:

- gate decision
- whether the gate is required, optional, or not applicable for the ticket
- source artifacts reviewed
- missing readiness items
- caveats if proceeding without a full prototype or brand pass
- relationship to Market Validation Before Code
- relationship to Pre-User Security And Privacy Readiness when external people are involved
- blocked claims or unsupported maturity signals
- follow-up ticket if brand/prototype work is needed later

Do not include private customer data, secrets, production data, or unsupported claims in prototype artifacts or handoffs.

## Example Outcomes

### Internal governance ticket

- Gate decision: NOT APPLICABLE
- Reason: no customer-facing surface, brand signal, or prototype exposure is being authorized
- Allowed next action: proceed with normal documentation validation

### Fake-door landing page

- Gate decision: REQUIRED
- Reason: user response will be distorted if promise, trust signal, and screen copy are unclear
- Required before exposure: working name, sourced promise, page wireframe, privacy/data capture boundary, Market Validation Before Code result, and Pre-User gate

### Backend implementation for a validated MVP

- Gate decision: NOT APPLICABLE or OPTIONAL
- Reason: no direct user-visible surface changes, or prototype already exists
- Caveat: if backend behavior changes visible claims or onboarding, re-run the gate
