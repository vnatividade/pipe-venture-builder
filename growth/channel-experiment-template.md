# Channel Experiment Template

Use this template to run one manual, measurable channel experiment after the distribution strategy framework selects one primary channel.

Use it with `growth/distribution-strategy-framework.md`, `validation/validation-scorecard.md`, `product/mvp-scope.md`, `knowledge/knowledge-curator-workflow.md`, and `execution/approval-gates.md`.

## Boundary

This template does not authorize ads, outreach, publishing, external communications, paid spend, scraping, automated messaging, or growth automation.

Every experiment must be approved before any external action. Manual tests come first by default.

## Required Inputs

- distribution strategy artifact
- target persona
- selected primary channel
- validation evidence or evidence gap
- MVP scope or smallest ethical test
- approval state
- risk or claim review state

Do not run a channel experiment when:

- the target persona is unclear
- the channel strategy is missing
- the experiment has no measurable outcome
- the message contains unsupported claims
- the experiment requires outreach, publishing, or paid spend without approval
- customer, private, or sensitive data handling is unresolved

## Experiment Design Rules

Each experiment must define:

- one channel
- one target audience
- one message or offer hypothesis
- one primary metric
- one GO threshold
- one NO-GO threshold
- one learning question
- one result interpretation
- one learning update

Avoid activity-volume goals such as posting more, sending more, or getting more impressions unless they connect to a qualified conversion or learning threshold.

## Metric Guidance

Good primary metrics:

- qualified reply from target persona
- scheduled discovery call
- permission to inspect workflow
- request for manual test
- repeated engagement from ICP
- qualified referral
- willingness to share time, context, or approved data sample

Weak primary metrics:

- impressions
- likes
- generic site visits
- unqualified waitlist signups
- follower count
- synthetic persona score
- vanity engagement

Secondary metrics may provide context, but the GO/NO-GO decision must use the primary metric.

## Approval Rules

Approval is required before:

- publishing content
- sending outreach
- contacting customers or communities
- using paid ads or paid acquisition
- collecting payment or pricing signals
- using private, customer, or production data
- making public claims
- using automation or scraping

If approval is missing, mark the experiment as `Blocked` and keep it as a draft.

## Template

```md
# Channel Experiment - <channel / persona / hypothesis>

## Metadata

- Origin ticket:
- Owner:
- Date:
- Product phase:
- Distribution strategy artifact:
- Approval state:
- Human approval before external execution: yes/no

## Experiment Scope

- Target persona:
- Primary channel:
- Channel type:
- Audience source:
- Message or offer hypothesis:
- Trust/proof required:
- External action involved: yes/no
- Paid spend involved: yes/no
- Automation involved: yes/no
- Sensitive claim involved: yes/no

## Hypothesis

- We believe:
- For this persona:
- In this channel:
- This message/offer will:
- Because:
- What would prove us wrong:

## Metric And Threshold

| Item | Definition |
|---|---|
| Primary metric |  |
| Baseline, if known |  |
| GO threshold |  |
| NO-GO threshold |  |
| Minimum sample or attempt count |  |
| Maximum cost |  |
| Timebox |  |
| Stop condition |  |

## Approval And Safety

| Gate | Status | Notes |
|---|---|---|
| External execution approval | Approved / Blocked / Not needed |  |
| Publishing approval | Approved / Blocked / Not needed |  |
| Outreach approval | Approved / Blocked / Not needed |  |
| Paid spend approval | Approved / Blocked / Not needed |  |
| Sensitive claim review | Approved / Blocked / Not needed |  |
| Customer/private data review | Approved / Blocked / Not needed |  |
| Automation/scraping review | Approved / Blocked / Not needed |  |

## Result

- Experiment status: Draft / Approved / Running / Complete / Blocked / Stopped
- Actual result:
- Primary metric result:
- Cost:
- Sample or attempt count:
- Qualitative signal:
- Unexpected observation:
- Risk or objection:

## GO / NO-GO Decision

- Decision: GO / NO-GO / INCONCLUSIVE / BLOCKED
- Rationale:
- Threshold met: yes/no
- What changed:
- What did not change:
- What this does not prove:
- Human review required before next action: yes/no

## Learning Card

- Learning:
- Evidence source:
- Confidence: Low / Medium / High
- Impact on validation scorecard:
- Impact on distribution strategy:
- Impact on MVP scope:
- Knowledge update needed: yes/no
- Follow-up ticket needed: yes/no
- Next experiment or action:
```

## Result Interpretation

| Decision | Use when | Next action |
|---|---|---|
| GO | GO threshold is met, risk is acceptable, and signal maps to validation/MVP evidence. | Human-reviewed continuation or next manual experiment. |
| NO-GO | NO-GO threshold is met or risk/objection invalidates the channel hypothesis. | Refine or stop the channel; capture learning. |
| INCONCLUSIVE | Sample is too small, metric was weak, or execution was flawed. | Redesign the experiment; do not count it as validation. |
| BLOCKED | Approval, claim, data, privacy, paid spend, or outreach gate is unresolved. | Stop until approval or scope change. |

Do not treat a GO as permission to scale paid growth, automate outreach, or expand channels without a new approval decision.

## Learning Update Rules

Every completed experiment must create a learning update in Linear or the appropriate repository artifact.

The update must include:

- result
- threshold comparison
- what changed
- confidence
- implication for validation, distribution, or MVP scope
- next action

If no learning can be extracted, mark the experiment as flawed and do not use it for prioritization.

## Done Criteria

This template is complete when:

- every experiment requires hypothesis, channel, audience, message, metric, threshold, cost, approval, and result
- every experiment has GO/NO-GO thresholds
- every completed experiment requires a learning card
- manual tests are the default first step
- ads, outreach, publishing, paid spend, and automation remain gated
- experiments without measurable outcomes are blocked
