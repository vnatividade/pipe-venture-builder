# Fake-Door And Landing Page Validation Workflow

Use this workflow to design ethical fake-door, smoke-test, and landing-page validation experiments before committing to a production build.

Use it with `validation/validation-scorecard.md`, `validation/icp-profile.md`, `validation/customer-data-retention-policy.md`, `growth/distribution-strategy-framework.md`, `growth/channel-experiment-template.md`, `growth/growth-experiment-backlog-template.md`, and `execution/approval-gates.md`.

## Boundary

This workflow is for demand validation. It does not authorize production builds, billing, paid ads by default, deceptive collection, automated outreach, scraping, external publishing, customer contact, sensitive claims, or customer/private data handling.

Human approval is required before publishing any page, sending traffic to it, contacting interested users, collecting pricing signals, using paid acquisition, or storing identifiable customer data.

If a test would mislead users or has no follow-up plan after signup or expressed interest, mark it `NO-GO` and do not publish it.

## Required Inputs

- ICP profile
- validation scorecard
- target persona
- problem and trigger moment
- offer or promise to test
- selected traffic source
- primary metric
- GO threshold
- NO-GO threshold
- ethical disclosure plan
- follow-up plan after signup or interest
- approval state before publishing

Do not run this workflow when:

- ICP is unclear or unsupported
- validation scorecard is missing or has unresolved critical zeroes
- page/message includes unsupported claims
- the test implies a product exists when it does not
- the test collects payment, sensitive data, or private files
- paid ads, publishing, outreach, or community posting lacks approval
- there is no plan for what happens after signup, click, reply, or interest

## Test Types

| Test type | Use when | Must disclose |
|---|---|---|
| Landing page interest test | You need to test whether a persona understands and wants the offer. | The current availability state and what happens after interest. |
| Fake-door feature test | You need to test demand for a specific feature before building it. | That the feature is not yet available or is being considered. |
| Waitlist test | You need a low-friction signal from qualified users. | What joining means, what communication may follow, and privacy expectations. |
| Concierge/manual pilot request | You need behavioral commitment before automation or product build. | That the first version may be manual, limited, or exploratory. |
| Message/offer smoke test | You need to compare one positioning hypothesis. | The real scope and any limits of the offer. |

Avoid tests whose only signal is vanity traffic, generic clicks, or curiosity without qualification.

## What Users See

Every test must define the user-facing experience before publication.

Required user-facing fields:

- headline or offer
- target problem
- who it is for
- what is available now
- what is not available yet
- expected next step after interest
- data collected
- privacy note
- no-payment note, unless a separate approval explicitly allows pricing collection
- contact or follow-up expectation

Ethical disclosure guidance:

- Do not claim the product, feature, integration, customer result, metric, revenue, compliance posture, or availability exists unless there is traceable evidence.
- Use clear availability language such as `early access`, `manual pilot`, `research preview`, `join the waitlist`, or `request a discovery call` when accurate.
- Do not hide material limitations behind vague language.
- Do not create urgency, scarcity, guarantees, or social proof without evidence.
- Tell users what will happen after they express interest.

## What Is Measured

Choose one primary metric that maps to validation or MVP learning.

Good primary metrics:

- qualified request for discovery
- qualified waitlist signup with role and problem fit
- request for manual pilot
- reply explaining the current workaround
- permission to inspect workflow or sample context after approval
- repeat interest from the target persona
- intro to another qualified persona

Weak primary metrics:

- raw page views
- impressions
- likes
- generic clicks
- unqualified email collection
- bounce rate without qualification
- synthetic persona score

Secondary metrics can explain behavior, but GO/NO-GO must use the primary metric.

## After Signup Or Interest

Every experiment must define the follow-up before it runs.

Allowed follow-up states:

| State | User expectation | Required action |
|---|---|---|
| Thank-you only | User is told the product/feature is not yet available or is in early exploration. | Record aggregate learning only; do not contact unless approved. |
| Discovery invitation | User opts into a human follow-up. | Contact only after approval and using approved messaging. |
| Manual pilot consideration | User asks to try a manual or concierge version. | Review risk, data, and scope before any pilot. |
| Waitlist update | User opts into future updates. | Do not send updates until external communication approval exists. |
| Blocked | Follow-up would require unapproved outreach, data handling, billing, or sensitive claims. | Stop and record blocker. |

Do not leave interested users with a false impression that access is immediate when no access exists.

## Approval And Safety Gates

| Gate | Required before |
|---|---|
| Publishing approval | Making the page, form, post, or test externally visible. |
| Traffic source approval | Sending users from a channel, community, partner, or outreach path. |
| Paid spend approval | Running any paid ad, sponsorship, or paid acquisition test. |
| Outreach approval | Contacting signups, waitlist members, prospects, communities, or referrals. |
| Sensitive claim review | Publishing claims about outcomes, customers, integrations, compliance, security, legal, financial, health, or regulated areas. |
| Customer/private data review | Collecting anything beyond minimal contact and qualification fields. |
| Pricing collection approval | Asking for payment, deposits, card details, invoices, binding commitments, or explicit willingness-to-pay signals. |
| Automation/scraping approval | Using automated traffic, scraping, automated messaging, or enrichment. |

If approval is missing, keep the test as a draft or mark it `Blocked`.

## Workflow Template

```md
# Fake-Door / Landing Page Validation - <persona / offer / channel>

## Metadata

- Origin ticket:
- Owner:
- Date:
- Product phase:
- ICP profile:
- Validation scorecard:
- Distribution strategy:
- Growth backlog item:
- Human approval before publishing: yes/no

## Experiment Scope

- Test type:
- Target persona:
- Primary problem:
- Trigger moment:
- Offer or promise:
- Page/message hypothesis:
- Traffic source:
- External action involved: yes/no
- Paid spend involved: yes/no
- Production build involved: no
- Sensitive claim involved: yes/no
- Customer/private data involved: yes/no

## User-Facing Experience

- Headline:
- Supporting message:
- Call to action:
- What users are told is available now:
- What users are told is not available yet:
- Data collected:
- Privacy note:
- No-payment note:
- Follow-up expectation:
- Ethical disclosure:

## Metric And Thresholds

| Item | Definition |
|---|---|
| Primary metric |  |
| Qualification rule |  |
| GO threshold |  |
| NO-GO threshold |  |
| Minimum sample or attempt count |  |
| Timebox |  |
| Maximum cost |  |
| Stop condition |  |

## Approval And Safety

| Gate | Status | Link or note |
|---|---|---|
| Publishing approval | Approved / Blocked / Not needed |  |
| Traffic source approval | Approved / Blocked / Not needed |  |
| Paid spend approval | Approved / Blocked / Not needed |  |
| Outreach approval | Approved / Blocked / Not needed |  |
| Sensitive claim review | Approved / Blocked / Not needed |  |
| Customer/private data review | Approved / Blocked / Not needed |  |
| Pricing collection approval | Approved / Blocked / Not needed |  |
| Automation/scraping review | Approved / Blocked / Not needed |  |

## Follow-Up Plan

- After signup/interest:
- User receives:
- Human follow-up required: yes/no
- Follow-up approval source:
- Data storage location:
- Retention/deletion expectation:
- If no follow-up is allowed:

## Result

- Experiment status: Draft / Approved / Running / Complete / Blocked / Stopped
- Actual user-facing message:
- Traffic source used:
- Primary metric result:
- Qualified signal count:
- Sample or attempt count:
- Cost:
- Objections or risks:
- Data captured: none / anonymized / identifiable / sensitive blocker

## GO / NO-GO Decision

- Decision: GO / NO-GO / INCONCLUSIVE / BLOCKED
- Rationale:
- Threshold met: yes/no
- What users saw:
- What was measured:
- What happened after signup/interest:
- What this does not prove:
- Human review required before next action: yes/no

## Learning Update

- Learning:
- Evidence source:
- Confidence: Low / Medium / High
- Impact on validation scorecard:
- Impact on ICP profile:
- Impact on distribution strategy:
- Impact on MVP scope:
- Knowledge update needed: yes/no
- Follow-up ticket needed: yes/no
- Next action:
```

## Interpretation Rules

| Decision | Use when | Next action |
|---|---|---|
| GO | The qualified primary metric meets the GO threshold, ethical gates were respected, and the signal maps to validation or MVP learning. | Human-reviewed next validation step, manual pilot review, or MVP scope update proposal. |
| NO-GO | The NO-GO threshold is met, the audience is wrong, or the message/offer fails with qualified users. | Capture learning and refine or kill the hypothesis. |
| INCONCLUSIVE | Traffic was too small, qualification was weak, the metric was noisy, or the page/message was ambiguous. | Redesign the test; do not count it as validation. |
| BLOCKED | Publishing, outreach, paid spend, data, pricing, claim, privacy, or follow-up approval is missing. | Stop until approval or scope change. |

A GO does not authorize production build, paid acquisition, billing, automated outreach, or public claims. It only creates evidence for the next reviewed decision.

## Done Criteria

This workflow is complete when:

- every test defines hypothesis, offer, page/message, traffic source, metric, thresholds, and ethics note
- the workflow defines what users see
- the workflow defines what is measured
- the workflow defines what happens after signup or interest
- misleading tests are blocked
- tests without follow-up plans are blocked
- paid ads, publishing, outreach, production build, pricing collection, automation, sensitive claims, and customer/private data handling remain gated
