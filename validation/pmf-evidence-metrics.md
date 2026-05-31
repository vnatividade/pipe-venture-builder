# PMF Evidence Metrics

Use this guide before treating MVP traction as product-market fit, launch readiness, scale readiness, or billing readiness.

This guide does not implement analytics, instrumentation, dashboards, billing, paid pilots, outreach, paid acquisition, production monitoring, or external communication. It defines evidence categories and false-positive warnings that future validation, launch, growth, monetization, and learning artifacts should use.

## Purpose

The Pipe should not confuse early interest with product-market fit.

AI agents can produce product work quickly, so PMF evidence must stay explicit, sourced, and stage-aware before the system creates launch, scale, growth, or monetization work.

This guide protects against:

- treating compliments as demand
- treating unqualified signups as adoption
- treating one successful test as repeatability
- treating usage without a core result as value
- treating founder interpretation as retention or willingness to pay
- scaling channels before a narrow ICP and offer show repeatable signal

## Evidence Boundary

PMF evidence must point to source artifacts.

Acceptable sources include:

- approved customer discovery notes
- validation scorecards
- MVP scope evidence thresholds
- fake-door or channel experiment results
- trial observations
- pricing hypothesis artifacts
- support or objection logs
- approved analytics exports, when instrumentation exists
- Linear or GitHub delivery evidence only when it records a real validation result

Do not use these as PMF proof by themselves:

- internal opinion
- synthetic persona output
- AI critique
- generic market research
- impressions, likes, follower count, or unqualified page visits
- one-off praise
- a completed PRD, MVP, or implementation ticket

## Stage-Aware Metrics

Use metrics that match the current stage. Do not force launch or scale metrics onto pre-MVP idea validation.

| Stage | Primary question | Useful metrics | Evidence threshold guidance |
|---|---|---|---|
| Idea | Is the problem real, specific, and worth validating? | Pain intensity, current workaround, ICP specificity, willingness to talk, source-backed urgency | Enough to justify validation, not PRD or build by default |
| MVP | Does the smallest ethical test create the intended core result? | Activation, core action completed, core result achieved, willingness to continue, objection resolved, effort invested | Enough to justify the next narrow test or implementation step |
| Launch | Can a narrow audience adopt through a plausible channel? | Qualified channel response, onboarding completion, repeated use, referral/reference, willingness to pay or commit, support burden | Enough to justify a controlled launch or next channel experiment |
| Scale | Can the product, channel, and operation repeat without founder heroics? | Retention, repeat purchase or repeated workflow use, revenue or paid commitment, referral loop, support volume, reliability signal, unit economics | Enough to justify scoped scale, automation, reliability, or growth tickets |

## Metric Categories

### Activation

Activation means the target user reaches the first meaningful moment of value, not merely signs up, clicks, or opens a page.

- Definition:
- Source artifact:
- Baseline, if known:
- Positive threshold:
- Negative threshold:
- What this does not prove:

### Core Result

Core result means the user receives the promised outcome or completes the core job defined in MVP scope.

- Core job:
- Core action:
- Core result:
- Evidence source:
- Quality bar:
- Failure mode:

### Continuation Or Retention

Continuation means the user returns, asks to continue, repeats the workflow, or invests more time after the first result.

- Continuation behavior:
- Time horizon:
- Repeat threshold:
- Source artifact:
- Alternative explanation:

### Referral Or Reference

Referral/reference means the user is willing to introduce another relevant person, act as a reference, share the result, or invite a collaborator.

- Referral/reference action:
- Persona relevance:
- Source:
- Trust signal:
- What remains unproven:

### Willingness To Pay Or Commit

Willingness to pay can include budget discussion, existing spend, paid substitute, paid pilot interest, explicit procurement path, or meaningful commitment of time/data/access.

- Buyer or approver:
- Value anchor:
- Existing spend or time cost:
- Commitment type:
- Pricing hypothesis artifact:
- Billing status: excluded / manual test / separately approved

Billing, payment collection, paid pilots, invoices, checkout, and pricing claims remain blocked unless separately approved.

### Effort Invested

Effort invested means the user spends scarce time, context, data, workflow access, introductions, or internal political capital to continue learning with the Pipe venture.

- Effort type:
- Why it is costly:
- Source:
- Confidence:
- Risk or privacy boundary:

## False-Positive Traction Warnings

Treat these as warnings, not PMF:

- users say the idea is interesting but do not share workflow detail
- waitlist signups are unqualified
- users try once but do not ask to continue
- the user likes the output but would not trust it in the real workflow
- the buyer and user are different and the buyer signal is missing
- channel response is curiosity, not adoption intent
- the product requires founder heroics to create every result
- growth looks strong only because the audience is broad or poorly qualified
- willingness to pay is inferred from competitor pricing only

If a warning appears, record it in the validation scorecard, channel experiment, MVP scope, pricing hypothesis, or learning update before advancing.

## Decision Guidance

| Decision | Use when | Allowed next action |
|---|---|---|
| GO | Stage-appropriate evidence meets the predefined threshold and has sourced artifacts. | Advance to the next narrow stage with human approval when required. |
| CONDITIONAL GO | Evidence is promising but one important gap remains and the next step is narrow. | Run the approved targeted validation, launch, or pricing test. |
| REFINE | Evidence is mixed, weak, or contradicted by user behavior. | Tighten ICP, offer, workflow, channel, or evidence threshold. |
| NO-GO | Critical evidence is missing, contradicted, or based on internal/synthetic signals. | Stop downstream build, launch, growth, monetization, or scale path. |
| BLOCKED | External action, billing, customer data, claims, production exposure, or sensitive work needs approval. | Stop until approval or scope changes. |

## Handoff Template

```md
## PMF Evidence Metrics

- Product or venture:
- Stage: Idea / MVP / Launch / Scale
- Evaluator:
- Date:
- Source artifacts:

## Stage question
- Primary question:
- Current answer:
- Confidence: Low / Medium / High

## Metrics
| Category | Metric | Threshold | Result | Source | Decision impact |
|---|---|---|---|---|---|
| Activation |  |  |  |  |  |
| Core result |  |  |  |  |  |
| Continuation or retention |  |  |  |  |  |
| Referral or reference |  |  |  |  |  |
| Willingness to pay or commit |  |  |  |  |  |
| Effort invested |  |  |  |  |  |

## False-positive warnings
- Warning:
- Evidence:
- Mitigation or next test:

## Decision
- Decision: GO / CONDITIONAL GO / REFINE / NO-GO / BLOCKED
- Rationale:
- Allowed next action:
- Blocked actions:
- Human approval required:
- Follow-up needed:
```

## Relationship To Existing Artifacts

- Use `product/mvp-scope.md` to define activation, core result, continuation, willingness to commit, and objection thresholds for the smallest ethical test.
- Use `growth/channel-experiment-template.md` to measure channel response without counting vanity engagement as adoption.
- Use `monetization/pricing-hypothesis-template.md` before treating willingness to pay as billing readiness.
- Use `knowledge/learning-record-policy.md` when repeated PMF evidence or false-positive patterns become reusable learning.
