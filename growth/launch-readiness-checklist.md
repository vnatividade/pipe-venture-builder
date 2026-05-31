# Launch Readiness Checklist

Use this checklist before any product, MVP, manual pilot, fake-door test, landing page, channel experiment, or public distribution step is treated as launch-ready.

Launch readiness means the Pipe has enough validation, positioning, channel, offer, support, measurement, and approval clarity to run the next narrow launch step. It does not mean the product has product-market fit, scale readiness, billing readiness, or permission to automate growth.

## Boundary

This checklist is a readiness gate. It does not authorize:

- production deployment
- public launch
- publishing
- outreach
- paid ads
- paid acquisition
- billing or pricing collection
- automated messaging
- scraping
- customer data handling
- broad multi-channel campaigns
- unsupported customer, revenue, integration, security, privacy, legal, financial, or compliance claims

Human approval is required before any external action.

## Required Inputs

Complete or link these before assessing readiness:

- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `validation/validation-scorecard.md`
- `validation/market-validation-before-code-gate.md`
- `validation/pmf-evidence-metrics.md`
- `validation/icp-profile.md`
- `knowledge/customer-language-memory.md`, when customer language exists
- `product/mvp-scope.md`
- `growth/distribution-strategy-framework.md`
- `growth/channel-experiment-template.md`, when a channel test is planned
- `validation/pre-user-security-privacy-readiness-gate.md`, when real users or external participants are involved
- `validation/customer-data-retention-policy.md`, when any customer/private data may be captured
- `execution/approval-gates.md`

## Launch Readiness Dimensions

Every launch candidate must be checked across these dimensions:

| Dimension | Readiness question | Required evidence |
|---|---|---|
| Target | Do we know exactly who this launch is for and who is excluded? | ICP profile, respondent evidence, exclusion criteria |
| Problem | Is the pain specific, repeated, and supported by evidence? | Validation scorecard, interview synthesis, status quo evidence |
| Offer | Is the first promise concrete and narrow? | MVP scope, PMF triad, distribution strategy |
| Proof | Can we support the claims being made? | Customer language, manual test result, approved source artifacts |
| Channel | Is one primary channel selected with a trust path? | Distribution strategy framework |
| Conversion | Is there one primary conversion or learning metric? | PMF evidence metrics, channel experiment template |
| Onboarding | Does the user know what happens next? | User-facing flow, follow-up plan, support path |
| Support | Is there an owner for questions, issues, and stop/delete requests? | Support owner, participant expectation, data handling plan |
| Analytics | Can we observe the result without over-collecting data? | Metric definition, storage boundary, retention plan |
| Risk | Are claims, privacy, security, legal, compliance, billing, and data risks handled? | Pre-user gate, risk review, approval gate |
| Learning loop | Is the post-launch learning path defined? | Linear update, repository artifact updates, follow-up criteria |
| Approval | Has a human approved the exact launch step? | Approval record and allowed next action |

## Readiness Checklist

Use `Ready`, `Blocked`, or `N/A`. Any `Blocked` item blocks launch readiness.

| Area | Check | Status | Evidence / link | Not ready because |
|---|---|---|---|---|
| Target | ICP is specific and excludes bad-fit users. | Ready / Blocked / N/A |  |  |
| Target | Buyer, user, approver, and influencer roles are clear enough for this launch step. | Ready / Blocked / N/A |  |  |
| Problem | Pain intensity is backed by customer behavior, quotes, workarounds, spend, or repeated urgency. | Ready / Blocked / N/A |  |  |
| Problem | Contradictory evidence has been recorded and does not invalidate the launch step. | Ready / Blocked / N/A |  |  |
| Offer | The promise is one concrete outcome, not a broad platform claim. | Ready / Blocked / N/A |  |  |
| Offer | The MVP scope states what is available now and what is intentionally excluded. | Ready / Blocked / N/A |  |  |
| Proof | Public or user-facing claims are sourced and do not imply unsupported results. | Ready / Blocked / N/A |  |  |
| Proof | Customer quotes, logos, metrics, revenue, integrations, or compliance claims are excluded unless approved and sourced. | Ready / Blocked / N/A |  |  |
| Channel | One primary channel is selected. | Ready / Blocked / N/A |  |  |
| Channel | Channel trust path, permission fit, and first conversion metric are defined. | Ready / Blocked / N/A |  |  |
| Conversion | The primary metric measures qualified behavior or learning, not vanity activity. | Ready / Blocked / N/A |  |  |
| Conversion | GO, NO-GO, and stop thresholds are defined. | Ready / Blocked / N/A |  |  |
| Onboarding | The user-facing experience explains availability, limitations, next step, and follow-up expectation. | Ready / Blocked / N/A |  |  |
| Support | A support/contact/stop path exists for participants or users. | Ready / Blocked / N/A |  |  |
| Data | Customer/private data capture is minimized and retention/deletion is defined. | Ready / Blocked / N/A |  |  |
| Data | Recordings, transcripts, identifiable quotes, private files, and sensitive data are excluded unless explicitly approved. | Ready / Blocked / N/A |  |  |
| Analytics | Measurement can be captured without hidden, excessive, or unapproved data collection. | Ready / Blocked / N/A |  |  |
| Risk | Pre-user security and privacy readiness gate is GO, CONDITIONAL GO, or NOT APPLICABLE with rationale. | Ready / Blocked / N/A |  |  |
| Risk | Billing, pricing collection, paid pilot, paid ads, production, automation, scraping, and outreach approvals are recorded when relevant. | Ready / Blocked / N/A |  |  |
| Learning | Post-launch learning artifact and Linear update path are defined. | Ready / Blocked / N/A |  |  |
| Approval | Human approval exists for the exact launch step and blocked actions are named. | Ready / Blocked / N/A |  |  |

## Not-Ready-Because Output

If any item is `Blocked`, produce this output before creating launch, growth, publishing, outreach, or production work.

```md
## Launch Readiness - Not Ready Because

- Launch candidate:
- Origin ticket:
- Evaluator:
- Date:
- Decision: BLOCKED / NO-GO / REFINE

## Blockers

| Blocker | Dimension | Why it blocks launch | Required evidence or action | Owner | Follow-up ticket |
|---|---|---|---|---|---|
|  | Target / Problem / Offer / Proof / Channel / Conversion / Onboarding / Support / Data / Analytics / Risk / Learning / Approval |  |  |  |  |

## Blocked actions

- External launch:
- Publishing:
- Outreach:
- Paid spend:
- Billing or pricing collection:
- Customer/private data capture:
- Automation or scraping:
- Production deployment:

## Allowed next action

- TBD

## Follow-up required

- Linear ticket:
- Repository artifact:
```

## Decision

Choose one.

| Decision | Use when | Allowed next action |
|---|---|---|
| GO | All applicable checklist items are Ready, evidence is sourced, risk is controlled, and approval is recorded. | Run only the approved launch step. |
| CONDITIONAL GO | One non-critical gap has a narrow mitigation and human approval accepts the limited launch step. | Run only the approved limited step after mitigation. |
| REFINE | Offer, ICP, proof, channel, metric, or follow-up is too fuzzy. | Refine artifacts before launch work. |
| BLOCKED | Approval, risk, claims, data, billing, outreach, publishing, automation, or production boundary is unresolved. | Stop and create/update follow-up tickets. |
| NO-GO | Launch would be misleading, unsupported, unsafe, too broad, or impossible to learn from. | Do not launch; revise validation or MVP scope. |

## Launch Readiness Template

```md
# Launch Readiness - <venture / MVP / channel>

## Metadata

- Origin ticket:
- Owner:
- Date:
- Launch candidate:
- Product phase:
- Human approval before launch: yes/no

## Source Artifacts

- Founder focus:
- C.O.N.T.R.O.L.E. evaluation:
- Validation scorecard:
- Market Validation Before Code gate:
- PMF evidence metrics:
- ICP profile:
- Customer language memory:
- MVP scope:
- Distribution strategy:
- Channel experiment:
- Pre-user gate:
- Customer data retention policy:
- Approval gate:

## Launch Step

- Target persona:
- Problem:
- Offer or promise:
- Primary channel:
- User-facing action:
- Primary metric:
- GO threshold:
- NO-GO threshold:
- Stop condition:
- What is available now:
- What is not available:
- Follow-up expectation:

## Checklist Summary

| Dimension | Status | Evidence | Not ready because |
|---|---|---|---|
| Target | Ready / Blocked / N/A |  |  |
| Problem | Ready / Blocked / N/A |  |  |
| Offer | Ready / Blocked / N/A |  |  |
| Proof | Ready / Blocked / N/A |  |  |
| Channel | Ready / Blocked / N/A |  |  |
| Conversion | Ready / Blocked / N/A |  |  |
| Onboarding | Ready / Blocked / N/A |  |  |
| Support | Ready / Blocked / N/A |  |  |
| Data | Ready / Blocked / N/A |  |  |
| Analytics | Ready / Blocked / N/A |  |  |
| Risk | Ready / Blocked / N/A |  |  |
| Learning | Ready / Blocked / N/A |  |  |
| Approval | Ready / Blocked / N/A |  |  |

## Decision

- Decision: GO / CONDITIONAL GO / REFINE / BLOCKED / NO-GO
- Rationale:
- Allowed next action:
- Blocked actions:
- Required approvals:
- Required mitigations:
- Residual risk:

## Learning And Handoff

- What will be measured:
- Where result will be recorded:
- Repository artifacts to update:
- Linear follow-up:
- Owner:
- Review date:
```

## Done Criteria

This checklist is complete when:

- launch cannot proceed without validation evidence and approval
- target, positioning, channel, offer, proof, onboarding, support, analytics, risk, and learning loop are checked
- unsupported claims and premature paid/automated growth are blocked
- every blocked item produces a `Not Ready Because` output
- the next action is explicit and narrow

## Relationship To Existing Artifacts

- Use `product/mvp-scope.md` to confirm the smallest ethical test and explicit cuts.
- Use `validation/pmf-evidence-metrics.md` to avoid mistaking early interest for PMF.
- Use `growth/distribution-strategy-framework.md` to select one primary channel.
- Use `growth/channel-experiment-template.md` to run a measurable manual channel test after readiness approval.
- Use `growth/fake-door-landing-page-validation-workflow.md` when the launch step is a fake-door, smoke test, landing page, or waitlist.
- Use `validation/pre-user-security-privacy-readiness-gate.md` before any external participant touches the flow.
- Use `execution/approval-gates.md` before publishing, outreach, paid spend, billing, automation, or production deployment.
