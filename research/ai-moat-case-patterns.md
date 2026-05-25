# AI Moat Case Pattern Library

Use this library to translate AI moat examples into reusable venture patterns.

This is not a deep research report on the companies cited. It is a pattern library for Pipe venture validation, PRD thinking, Data Moat strategy, and architecture review. Do not treat these cases as proof that a Pipe venture has market validation, customer evidence, or defensibility.

Use with:

- `architecture/proprietary-data-moat-strategy.md`
- `architecture/api-dependency-risk-assessment.md`
- `product/prd.md`
- `validation/venture-validation-framework.md`

## Source Boundary

The case notes below use public source material and company/public case descriptions. They should be treated as directional examples, not independently verified performance claims.

| Case | Source boundary |
|---|---|
| Pindrop | Public company materials describe fraud, deepfake defense, liveness, and identity verification for voice/video/digital interactions: https://www.pindrop.com/ and https://www.globenewswire.com/news-release/2026/03/12/3254709/0/en/pindrop-zoom-integration-embeds-real-time-deepfake-detection-and-identity-verification-in-zoom-contact-center.html |
| Doxel | Public company materials describe AI/computer-vision progress tracking from 360 video against project plans/models: https://doxel.ai/ and https://doxel.ai/faqs |
| McLaren / Rescale / NVIDIA | Rescale describes an AI/HPC engineering platform using NVIDIA infrastructure for McLaren engineering and simulation workflows: https://rescale.com/blog/rescale-gtc-2026-agentic-era-begins-nvidia-mclaren-leading-way/ |
| Autonomous logistics | NVIDIA describes Serve Robotics using AI-powered sidewalk delivery robots for urban last-mile delivery: https://www.nvidia.com/en-gb/case-studies/serve-robotics/ |

## Pattern Index

| Pattern | Source case | Core moat | Best venture fit |
|---|---|---|---|
| Signal detection | Pindrop | Proprietary signal, threat detection, trust boundary | Fraud, identity, trust, compliance, security workflows |
| AI-detecting-AI | Pindrop | Adversarial detection loop | Deepfake, fraud, content integrity, verification workflows |
| Reality-vs-plan comparison | Doxel | Field reality capture compared to plan/model | Construction, field ops, project management, inspections |
| Work-in-place progress intelligence | Doxel | Workflow state extraction from operational data | Physical operations, asset-heavy workflows, project tracking |
| Simulation loop | McLaren / Rescale / NVIDIA | Simulation data, engineering feedback, design iteration | Engineering, manufacturing, R&D, performance optimization |
| Last-mile mapping | Autonomous logistics / Serve Robotics | Local environment data, route memory, operational autonomy | Logistics, field service, delivery, local operations |
| Workflow-integrated intelligence | Cross-case | AI embedded in existing operational loop | Vertical SaaS, compliance ops, internal tooling |

## Pattern 1 - Signal Detection

**Source case:** Pindrop.

**Concept:** Capture domain-specific signals that indicate risk, identity, intent, anomaly, or trustworthiness.

**Moat mechanism:** The value comes from knowing which signals matter, collecting them in the right workflow context, and improving detection as more cases are reviewed.

**Data moat link:** Strategic learning, operational workflow data, and customer evidence categories from `architecture/proprietary-data-moat-strategy.md`.

**Potential venture types:**

- fraud detection for a vertical workflow
- compliance monitoring
- contact-center quality/risk tools
- identity verification
- transaction risk review

**Applicability questions:**

- What signal is hard for a generic model or API to observe?
- Does the workflow produce repeated examples of true/false positives?
- Can the product improve from operator review or confirmed outcomes?
- Is the signal allowed to be captured under the privacy/trust boundary?

**Anti-applicability:**

- Do not apply when there is no repeated signal stream.
- Do not apply when detection labels cannot be verified.
- Do not apply when the signal is sensitive/prohibited and no approval boundary exists.
- Do not claim accuracy without source artifacts and validation.

## Pattern 2 - AI-Detecting-AI

**Source case:** Pindrop.

**Concept:** Use AI to detect synthetic or adversarial AI-generated behavior, media, or signals.

**Moat mechanism:** The moat is not generic detection. It is an adversarial learning loop tied to a high-trust workflow where false positives and false negatives have clear consequences.

**Data moat link:** Operational workflow data, customer evidence, sensitive data, and prohibited data boundaries from `architecture/proprietary-data-moat-strategy.md`.

**Potential venture types:**

- deepfake detection in meetings or hiring
- synthetic review or bot detection
- fraud prevention
- content provenance workflows
- trust/safety tooling

**Applicability questions:**

- What attack pattern is actually present in the workflow?
- Who confirms whether detection was correct?
- What happens when the model is uncertain?
- What manual review or escalation path exists?

**Anti-applicability:**

- Do not apply as a generic "AI detector" without a concrete workflow.
- Do not use when false positives would harm legitimate users without review.
- Do not assume the detector will remain ahead of adversaries.
- Do not store sensitive media without explicit approval.

## Pattern 3 - Reality-Vs-Plan Comparison

**Source case:** Doxel.

**Concept:** Compare observed reality against an expected plan, schedule, model, or intended state.

**Moat mechanism:** The moat comes from connecting field capture, planned state, actual state, variance detection, and workflow action.

**Data moat link:** Operational workflow data, public/reference data, and strategic learning categories from `architecture/proprietary-data-moat-strategy.md`.

**Potential venture types:**

- construction progress tracking
- retail execution
- facilities inspection
- field service QA
- inventory and planogram compliance
- implementation audits

**Applicability questions:**

- Is there a clear expected state to compare against?
- Can reality be captured cheaply and repeatedly?
- Does the variance trigger a decision, escalation, or workflow?
- Can repeated comparisons improve planning, prediction, or prioritization?

**Anti-applicability:**

- Do not apply when there is no plan/model/reference baseline.
- Do not apply when capture cost is higher than the decision value.
- Do not apply when variance does not change action.
- Do not overbuild computer vision when manual sampling validates faster.

## Pattern 4 - Work-In-Place Progress Intelligence

**Source case:** Doxel.

**Concept:** Convert observed operational state into measurable progress and production-rate intelligence.

**Moat mechanism:** Repeated work-in-place measurement creates a learning loop around progress, bottlenecks, schedule risk, and operational forecasting.

**Data moat link:** Operational workflow data, retention expectation, learning loop, and promotion criteria from `architecture/proprietary-data-moat-strategy.md`.

**Potential venture types:**

- project control systems
- contractor/vendor performance visibility
- installation progress tracking
- operations planning
- SLA or field execution monitoring

**Applicability questions:**

- What unit of progress is objectively measurable?
- What source confirms progress is complete enough?
- Who acts on a delay or variance?
- Does history improve future estimates or interventions?

**Anti-applicability:**

- Do not apply when progress is subjective and unreviewed.
- Do not apply when the operator cannot act on the signal.
- Do not turn progress monitoring into worker surveillance without explicit trust boundaries.

## Pattern 5 - Simulation Loop

**Source case:** McLaren / Rescale / NVIDIA.

**Concept:** Use simulation and performance prediction to shorten design/engineering feedback loops.

**Moat mechanism:** The moat is a compounding loop of simulation data, engineering context, performance outcomes, and decision speed.

**Data moat link:** Strategic learning, operational workflow data, public/reference data, and promotion criteria from `architecture/proprietary-data-moat-strategy.md`.

**Potential venture types:**

- engineering design optimization
- manufacturing process tuning
- product configuration testing
- supply-chain scenario planning
- financial/operational scenario simulation

**Applicability questions:**

- Is there a modelable system with measurable outcomes?
- Does simulation reduce time, cost, or risk before physical execution?
- Can results be compared to real-world outcomes?
- Does each run improve a future decision?

**Anti-applicability:**

- Do not apply when the model cannot be calibrated against reality.
- Do not use simulation to avoid customer validation.
- Do not build HPC/AI infrastructure before the workflow and decision loop are validated.
- Do not treat synthetic results as market evidence.

## Pattern 6 - Last-Mile Mapping

**Source case:** Autonomous logistics / Serve Robotics.

**Concept:** Build local operational intelligence from repeated navigation, routing, environment, exception, and delivery data.

**Moat mechanism:** Repeated operation creates environment-specific knowledge that can improve routing, safety, reliability, and exception handling.

**Data moat link:** Operational workflow data, sensitive/prohibited data boundaries, retention expectation, and privacy/trust risk from `architecture/proprietary-data-moat-strategy.md`.

**Potential venture types:**

- local logistics
- field service route optimization
- inspection routing
- delivery operations
- on-site operational agents

**Applicability questions:**

- What local context improves with repeated operation?
- What exceptions are hard to capture in generic maps or APIs?
- What safety, privacy, or permission boundary exists?
- Can a manual or semi-manual route validate the workflow first?

**Anti-applicability:**

- Do not apply when generic routing is sufficient.
- Do not apply when local data cannot be captured safely or legally.
- Do not start with autonomy when manual/semi-automated operation validates faster.
- Do not create hardware/robotics roadmap from this pattern alone.

## Pattern 7 - Workflow-Integrated Intelligence

**Source case:** Cross-case pattern.

**Concept:** AI is strongest when embedded into a repeated operational workflow with source data, operator feedback, decision thresholds, and handoff.

**Moat mechanism:** The defensibility comes from workflow ownership and learning loops, not the model call itself.

**Data moat link:** Data moat hypothesis, learning loop, promotion criteria, and mitigation fields from `architecture/proprietary-data-moat-strategy.md`.

**Potential venture types:**

- vertical SaaS
- internal operations tools
- compliance workflows
- risk review workflows
- AI-assisted project control

**Applicability questions:**

- What repeated workflow owns the data and decision?
- What user action closes the loop?
- What gets better after 10, 100, or 1,000 uses?
- What part is hard for a generic provider to copy?

**Anti-applicability:**

- Do not apply when the workflow is a one-off task.
- Do not apply when the user would rather stay in the existing tool.
- Do not call a workflow a moat without evidence of repeated use or switching cost.

## Synthetic Venture Mapping

### Venture A - AI Vendor Risk Reviewer

| Pattern | Fit | Why |
|---|---|---|
| Signal detection | High | Repeated vendor documents and risk exceptions can create a labeled review loop. |
| AI-detecting-AI | Medium | Useful if vendors submit AI-generated claims or suspicious evidence, but not core at MVP. |
| Reality-vs-plan comparison | Medium | Compare vendor claims against required controls or policy baseline. |
| Simulation loop | Low | Not needed unless scenario modeling becomes a validated buying reason. |
| Last-mile mapping | Low | Not a physical routing or local ops problem. |

**Likely Data Moat:** anonymized risk patterns, repeated objections, review outcomes, and control-to-evidence mapping.

### Venture B - Construction Delay Early Warning

| Pattern | Fit | Why |
|---|---|---|
| Reality-vs-plan comparison | High | Core value is comparing field reality to schedule/model. |
| Work-in-place progress intelligence | High | Progress signals can improve production-rate estimates. |
| Signal detection | Medium | Delay signals may emerge from repeated variance patterns. |
| Simulation loop | Medium | Useful after observed data calibrates delay scenarios. |
| Last-mile mapping | Low | Not core unless field routing becomes the bottleneck. |

**Likely Data Moat:** operational progress history, variance labels, delay causes, and intervention outcomes.

### Venture C - Local Service Dispatch Optimizer

| Pattern | Fit | Why |
|---|---|---|
| Last-mile mapping | High | Local route exceptions, timing, and context can compound. |
| Workflow-integrated intelligence | High | Dispatch decisions improve when embedded into daily operations. |
| Signal detection | Medium | Detect recurring bottlenecks, no-shows, and high-risk jobs. |
| Reality-vs-plan comparison | Medium | Compare planned schedule to actual route/service completion. |
| Simulation loop | Low | Defer until enough operating history exists. |

**Likely Data Moat:** local route history, service duration variance, exception handling, and operator feedback.

## Decision Rules For Pipe

- Use these patterns to generate validation questions, not to justify build work.
- Connect any data moat claim to `architecture/proprietary-data-moat-strategy.md`.
- Connect any external API/provider dependency to `architecture/api-dependency-risk-assessment.md`.
- Prefer manual or lightweight validation before expensive capture, simulation, autonomy, or infrastructure.
- Store only anonymized, allowed learning unless explicit approval exists.
- Create Linear follow-ups only when a pattern reveals a concrete gap, risk, or reusable artifact need.

## Handoff Checklist

When a venture uses this library, record:

- selected pattern:
- source case:
- why applicable:
- anti-applicability check:
- data moat hypothesis:
- data categories:
- learning loop:
- validation question created:
- follow-up ticket needed: yes/no
