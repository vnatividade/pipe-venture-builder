# MVP Scope Gate

Use this template after founder focus, C.O.N.T.R.O.L.E., validation scorecard, and ICP/customer-language artifacts.

The MVP is the smallest ethical test of the riskiest business assumption. It is not the smallest feature set, a launch backlog, or a platform foundation.

Before this artifact creates architecture or implementation tickets, apply `validation/market-validation-before-code-gate.md`.

## Required Inputs

- Founder focus:
- C.O.N.T.R.O.L.E. verdict:
- Validation scorecard result:
- Market Validation Before Code gate decision:
- Market Validation Before Code approval record or blocker:
- Branding And Prototype Readiness gate decision:
- Branding/prototype caveats or blocker:
- ICP profile:
- Customer-language memory:
- Date:
- Owner:

Only continue if validation evidence supports GO or approved CONDITIONAL GO.

## Core Value Loop

Define the loop in one pass.

| Element | Definition |
|---|---|
| Core user |  |
| Core job |  |
| Core action |  |
| Core result |  |
| Core feedback signal |  |
| Learning loop |  |

If the loop cannot be described without secondary audiences or multiple jobs, refine scope before proceeding.

## Riskiest Assumption

- Riskiest business assumption:
- Why this is the riskiest assumption:
- What evidence currently supports it:
- What evidence is missing:
- What would falsify it:

## Smallest Ethical Test

- Test name:
- Test format:
- Manual or technical implementation needed:
- Customer exposure:
- Customer-facing prototype or screen artifact needed:
- Data or privacy risk:
- Approval needed:
- Why this is ethical:
- Why this is smaller than building the full product:

Do not run a test that hides material risk, misleads customers, mishandles data, or implies unavailable capability.

Before any real user or external participant touches the test, apply `validation/pre-user-security-privacy-readiness-gate.md`.

## Evidence Threshold

Define the minimum evidence needed before architecture or implementation tickets.

Use `validation/pmf-evidence-metrics.md` when defining activation, core result, continuation, willingness to commit, and false-positive warnings. The MVP threshold should prove the next narrow learning step, not full product-market fit.

| Signal | Threshold | Source |
|---|---|---|
| Activation or first-use behavior |  |  |
| Core result achieved |  |  |
| Feedback or learning signal |  |  |
| Willingness to continue |  |  |
| Willingness to pay or commit |  |  |
| Risk or objection resolved |  |  |

## Explicit Cuts

List what is intentionally excluded.

| Cut | Why it is excluded | Follow-up condition |
|---|---|---|
| Full feature backlog | MVP must test the riskiest assumption first | Evidence threshold is met |
| Scalability work | Premature before repeated use exists | Repeated use creates real constraint |
| Advanced personalization | Adds complexity before core loop is proven | Core loop works for first ICP |
| Billing | Excluded unless payment is the riskiest assumption | Willingness-to-pay test requires it |
| Growth automation | Premature before validated retention or willingness exists | Manual channel shows repeatable signal |

Add product-specific cuts:

- Not building:
- Not integrating:
- Not automating:
- Not personalizing:
- Not monetizing:
- Not scaling:

## GO / NO-GO Condition

Choose one.

| Decision | Condition | Next action |
|---|---|---|
| GO | Core loop is clear, risk is ethical, evidence threshold is measurable, and cuts are explicit | Create architecture or implementation tickets after approval |
| CONDITIONAL GO | Scope is mostly clear but one evidence or risk item needs targeted validation | Create validation follow-up before build tickets |
| NO-GO | Scope is a feature wishlist, bypasses customer evidence, or cannot test the riskiest assumption ethically | Refine validation, ICP, or C.O.N.T.R.O.L.E. |

- Selected decision:
- Rationale:
- Human approval before architecture or implementation tickets:
- Approval record or blocker:

## Ticketing Boundary

Architecture or implementation tickets may be created only when:

- MVP decision is GO or approved CONDITIONAL GO
- evidence threshold is explicit
- customer evidence is linked
- core loop is defined
- explicit cuts are recorded
- privacy and risk concerns are understood
- Branding And Prototype Readiness is classified when the MVP requires customer-facing screens, prototype sharing, landing pages, onboarding, or claims
- Linear project is confirmed

## Handoff

- Repository artifacts to update next:
- Architecture questions:
- Implementation ticket candidates:
- Validation follow-ups:
- Known risks:
