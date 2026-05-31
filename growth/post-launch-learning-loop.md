# Post-Launch Learning Loop

Use this loop after an approved launch step, manual pilot, fake-door test, landing page, channel experiment, waitlist test, or MVP exposure produces results.

The goal is to make growth compound into durable learning, not activity. Every launch or experiment should end with a learning card, decision update, and clear next action.

## Boundary

This workflow does not authorize:

- roadmap changes without human review
- automatic backlog reprioritization
- automatic product scope changes
- public claims based on weak evidence
- publishing, outreach, paid spend, billing, automation, scraping, or production changes
- customer data storage beyond approved retention rules

If a result suggests a product, roadmap, pricing, growth, claim, privacy, or data-handling change, create or update the relevant Linear ticket and require human review before execution.

## Required Inputs

Before running this loop, link:

- `growth/launch-readiness-checklist.md`
- `growth/distribution-strategy-framework.md`
- `growth/channel-experiment-template.md`, when a channel experiment ran
- `growth/fake-door-landing-page-validation-workflow.md`, when a fake-door, landing page, or waitlist test ran
- `growth/growth-experiment-backlog-template.md`
- `validation/pmf-evidence-metrics.md`
- `validation/validation-scorecard.md`
- `validation/customer-data-retention-policy.md`, when customer/private data was captured
- `knowledge/knowledge-curator-workflow.md`
- origin Linear ticket and PR, when applicable

## Learning Inputs

Capture only sourced results.

| Input | Examples | Required handling |
|---|---|---|
| Metric result | Qualified replies, requests, activation, conversion, continuation, support burden | Compare against GO/NO-GO threshold. |
| Customer feedback | Objections, exact language, confusion, requests, trust concerns | Anonymize and separate quote from synthesis. |
| Support issue | Bug, question, failed expectation, onboarding friction, stop/delete request | Link to ticket or create follow-up. |
| Risk signal | Unsupported claim, privacy issue, compliance concern, data retention issue | Stop if P0/P1; create risk follow-up. |
| Channel signal | Source quality, trust path, permission fit, conversion quality | Update distribution strategy or backlog state. |
| Product signal | Core result achieved, repeated use, requested workflow, willingness to continue/pay | Update MVP scope, PMF metrics, or validation scorecard only with source evidence. |
| Operational signal | Manual effort, support load, founder bottleneck, cost, setup friction | Update backlog or knowledge if it changes future execution. |

Do not use impressions, likes, raw traffic, unqualified signups, or praise as strong evidence unless they map to a predefined primary metric and qualification rule.

## Decision Model

Each launch or experiment must end in one decision.

| Decision | Use when | Required next action |
|---|---|---|
| KEEP | The result met the GO threshold, risk is controlled, and the same narrow path should continue. | Define the next approved iteration or follow-up experiment. |
| CHANGE | The result produced useful learning but requires ICP, offer, channel, message, onboarding, support, metric, or scope adjustment. | Update source artifacts and create follow-up tickets. |
| KILL | The result hit a NO-GO threshold, contradicted a critical assumption, or exposed unacceptable risk. | Close or kill the experiment and document why. |
| PAUSE | Evidence is inconclusive or the next step requires unresolved approval, data, claim, or risk review. | Record blocker and required decision. |
| ESCALATE | P0/P1 risk, sensitive data issue, misleading claim, customer trust issue, billing/privacy/security concern, or production risk appears. | Stop, document non-sensitive summary, and create/raise a risk ticket. |

## Learning Card Template

Copy this card into the relevant launch artifact, Linear update, or knowledge artifact.

```md
# Post-Launch Learning Card

## Metadata

- Launch or experiment:
- Origin ticket:
- Owner:
- Date:
- Product phase:
- Source artifacts:
- Approval record:

## Result Summary

- Status: Complete / Stopped / Blocked / Inconclusive
- Primary metric:
- GO threshold:
- NO-GO threshold:
- Actual result:
- Threshold met: yes/no/partial
- Sample or attempt count:
- Cost:
- Timebox:
- Data captured: none / anonymized / identifiable / sensitive blocker

## Feedback And Evidence

| Signal | Type | Source | Confidence | Decision impact |
|---|---|---|---|---|
|  | Metric / quote / objection / support issue / risk / product behavior / channel signal |  | Low / Medium / High |  |

## Customer Language

| Quote or phrase | Anonymized source | Topic | Repository-safe? |
|---|---|---|---|
|  |  |  | Yes / No / Needs approval |

## Objections And Support Issues

| Issue | Type | Severity | Owner | Follow-up |
|---|---|---|---|---|
|  | Objection / bug / support / data / claim / trust / onboarding | P0 / P1 / P2 / P3 |  |  |

## Interpretation

- What got stronger:
- What got weaker:
- What changed:
- What did not change:
- What remains uncertain:
- What this does not prove:

## Decision

- Decision: KEEP / CHANGE / KILL / PAUSE / ESCALATE
- Rationale:
- Human review required before next action: yes/no
- Allowed next action:
- Blocked actions:

## Artifact Updates

- Validation scorecard:
- PMF evidence metrics:
- ICP profile:
- Customer language memory:
- MVP scope:
- Distribution strategy:
- Growth experiment backlog:
- KnowledgeRecord / KDR / DAR candidate:
- Linear follow-up:

## Data And Privacy Handoff

- Customer/private data captured:
- Raw data retained:
- Raw data deleted:
- Retention owner:
- Review/deletion date:
- Residual privacy risk:
```

## Artifact Update Rules

Use the smallest durable update that changes future execution.

| Result changes | Update |
|---|---|
| ICP or persona quality changed | `validation/icp-profile.md` |
| Evidence score changed | `validation/validation-scorecard.md` |
| PMF, activation, retention, commitment, or false-positive signal changed | `validation/pmf-evidence-metrics.md` |
| Customer language, objections, status quo, or trigger language changed | `knowledge/customer-language-memory.md` |
| MVP scope, explicit cuts, threshold, or riskiest assumption changed | `product/mvp-scope.md` |
| Channel, trust path, proof, or first conversion metric changed | `growth/distribution-strategy-framework.md` or source artifact |
| Experiment state or priority changed | `growth/growth-experiment-backlog-template.md` or Linear |
| Reusable rule or operating lesson changed | `knowledge/learning-record-policy.md`, KDR, or DAR candidate |
| Risk, claim, privacy, support, or approval blocker appeared | Linear follow-up and relevant risk artifact |

Do not update roadmap, MVP scope, pricing, public claims, or execution policy without human review.

## Backlog Update Rules

After the learning card:

- move successful narrow experiments to `Learned`
- mark invalidated experiments as `Killed`
- mark unresolved approval/risk/data/claim items as `Blocked`
- create follow-ups only when the next action is specific, sourced, and has acceptance criteria
- avoid creating generic "improve growth" tickets
- never convert activity volume into priority without evidence

## Follow-Up Ticket Criteria

Create a follow-up ticket when:

- a support issue needs product or documentation work
- a validated objection changes MVP or onboarding
- the channel needs a new approved experiment
- a risk needs mitigation before continuation
- a customer-language pattern should be promoted into positioning
- a metric result changes validation scorecard or PMF evidence
- a launch result requires human roadmap decision
- a privacy, retention, claim, security, billing, or trust issue appears

Do not create a follow-up ticket for:

- isolated vanity metrics
- weak praise without behavior
- cosmetic wording preferences
- speculative scale ideas without validation evidence
- future automation unless the manual loop has proven the need

## Linear Delivery Update Template

Use this in the origin ticket or launch/experiment ticket.

```md
## Post-launch learning update

- Launch/experiment:
- Source artifacts:
- Result:
- Primary metric:
- Threshold met:
- Decision: KEEP / CHANGE / KILL / PAUSE / ESCALATE

## Learning

- What got stronger:
- What got weaker:
- What changed:
- What did not change:
- What remains uncertain:

## Artifact updates

- Validation scorecard:
- PMF evidence metrics:
- ICP profile:
- Customer language memory:
- MVP scope:
- Distribution strategy:
- Growth backlog:
- Knowledge update:

## Follow-ups

- Ticket:
- Reason:

## Approval and risk

- Human review required:
- Blocked actions:
- Residual risk:
- Customer/private data captured:
- Retention/deletion status:
```

## Done Criteria

The post-launch loop is complete when:

- the result is compared against the predefined primary metric and thresholds
- a learning card exists
- the decision is KEEP, CHANGE, KILL, PAUSE, or ESCALATE
- support issues, objections, and risk signals are classified
- artifact updates are named or explicitly marked unnecessary
- follow-up tickets are specific and evidence-linked
- human review is required before roadmap, MVP, pricing, public claim, data, or policy changes

## Relationship To Existing Artifacts

- Use `growth/launch-readiness-checklist.md` before running the launch step.
- Use `growth/channel-experiment-template.md` and `growth/fake-door-landing-page-validation-workflow.md` for source results.
- Use `growth/growth-experiment-backlog-template.md` to update experiment state.
- Use `validation/pmf-evidence-metrics.md` to avoid mistaking early interest for PMF.
- Use `knowledge/knowledge-curator-workflow.md` to decide whether learning deserves a durable knowledge update.
- Use `knowledge/learning-record-policy.md` only when the learning changes future execution, validation, product, or risk decisions.
