# Pre-User Security And Privacy Readiness Gate

Use this gate before any real user, prospect, customer, partner, community member, or external participant touches a Pipe-generated product, prototype, manual test, workflow, dataset, prompt output, trial, or validation artifact.

This is a lightweight operating gate. It is not legal, privacy, compliance, or security advice, and it does not claim GDPR, LGPD, SOC 2, HIPAA, PCI, or other regulatory compliance.

## Purpose

The Pipe should validate quickly without exposing people, customer trust, private data, sensitive claims, secrets, billing flows, or production systems prematurely.

This gate protects against:

- running discovery or trials without approval
- collecting customer data before retention rules are clear
- exposing secrets or credentials in a prototype
- making unsupported product, security, privacy, legal, financial, customer, revenue, or validation claims
- using external communication or outreach without approval
- launching a test that cannot be safely stopped, deleted, or explained

## When This Gate Applies

Apply this gate before:

- customer discovery involving real people
- manual validation tests with external participants
- fake-door pages, landing pages, forms, surveys, or waitlists
- prototype sharing
- product trials
- concierge or manual service delivery
- paid-pilot discussion or willingness-to-pay test
- any flow that stores, processes, copies, summarizes, or transmits customer/private data
- any public or external-facing claim
- any use of production data, credentials, secrets, or private files

Do not use this gate as a blocker for:

- blank templates
- internal-only planning docs
- synthetic examples clearly marked as examples
- repository governance work that does not authorize user exposure
- code or documentation changes that do not touch external participants, data, production, billing, claims, or outreach

For non-user-facing internal work, record `Gate decision: NOT APPLICABLE` when useful.

## Required Source Checks

Review these before a test or exposure:

- `execution/approval-gates.md`
- `validation/customer-data-retention-policy.md`
- `execution/risk-reviewer-matrix-lite.md`
- `product/mvp-scope.md`
- `validation/market-validation-before-code-gate.md`, when the exposure is tied to downstream product/build/growth/monetization work
- `validation/branding-prototype-readiness-gate.md`, when the exposure is a prototype, landing page, onboarding flow, customer-facing UI, or product trial surface
- `validation/pmf-evidence-metrics.md`, when the exposure is meant to prove traction, launch readiness, scale readiness, or willingness to pay

## Readiness Checklist

| Area | Question | Status | Required action if not ready |
|---|---|---|---|
| User exposure | Will a real external person interact with this? | Ready / Blocked / N/A | Get explicit approval before contact, sharing, posting, or trial. |
| External communication | Will the agent send, publish, post, message, schedule, or invite? | Ready / Blocked / N/A | Stop until external communication or outreach approval is recorded. |
| Customer data | Will any personal, customer, private, confidential, or sensitive data be captured or processed? | Ready / Blocked / N/A | Apply customer data retention policy and get approval for capture/storage. |
| Raw notes or recordings | Will notes, transcripts, recordings, screenshots, files, or direct quotes be retained? | Ready / Blocked / N/A | Define storage location, owner, retention reason, and deletion/review date. |
| Secrets or credentials | Are secrets, tokens, private keys, credentials, API keys, or production config involved? | Ready / Blocked / N/A | Stop. Do not handle without explicit approval and scoped procedure. |
| Auth and access | Does the prototype need login, permissions, roles, or restricted access? | Ready / Blocked / N/A | Define access boundary before sharing. |
| Billing or payment | Is payment, invoicing, checkout, pricing collection, paid pilot, tax, or subscription involved? | Ready / Blocked / N/A | Stop until explicit monetization/billing approval exists. |
| Sensitive claims | Does the artifact claim evidence, customers, security, privacy, compliance, integrations, revenue, regulated outcomes, or market validation? | Ready / Blocked / N/A | Remove or source the claim; require human review before external use. |
| Logging and observability | Will logs, metrics, analytics, forms, or recordings capture user data? | Ready / Blocked / N/A | Minimize capture, define storage, and document retention. |
| Deletion path | Can captured data or exposed artifacts be removed if the test stops? | Ready / Blocked / N/A | Define deletion owner and trigger before proceeding. |
| Support path | Does the participant know how to ask questions, report issues, or stop participation? | Ready / Blocked / N/A | Add a lightweight support/stop path before exposure. |
| Brand/prototype clarity | Could unclear naming, copy, screen flow, or visual fidelity make the test misleading? | Ready / Blocked / N/A | Apply Branding And Prototype Readiness and record caveats. |
| Scope control | Is the test narrow enough to avoid implying a launched product? | Ready / Blocked / N/A | Re-scope as a validation test or stop. |

## Gate Decision

Choose one.

| Decision | Use when | Allowed next action |
|---|---|---|
| GO | All applicable checklist items are Ready, required approvals are recorded, and risk is low or mitigated. | Run only the approved user exposure or test. |
| CONDITIONAL GO | One non-critical item needs a narrow mitigation and human approval accepts the limited next step. | Run only the approved limited test after mitigation. |
| BLOCKED | Approval, data handling, claims, billing, secrets, production, privacy, security, or external communication is unresolved. | Stop until approval, mitigation, or scope change. |
| NO-GO | The test is unsafe, misleading, too broad, cannot protect data, or cannot be ethically stopped/deleted. | Redesign or cancel the exposure. |
| NOT APPLICABLE | Work is internal-only and does not expose users, external parties, data, production, billing, claims, or outreach. | Proceed under normal ticket validation rules. |

## Stop Conditions

Stop immediately when:

- customer data would be captured without a retention plan
- secrets, credentials, private keys, production data, or private files are needed
- external communication, outreach, posting, publishing, or trial invitation lacks approval
- the test implies unavailable product capability
- the artifact makes unsupported sensitive claims
- billing, payment collection, paid pilots, invoices, checkout, or pricing collection appears without approval
- a participant could reasonably believe a validation test is a launched product
- deletion, retention, or support path is unclear for captured data
- a P0/P1 risk appears in the risk review

## Manual Gate Template

```md
## Pre-User Security And Privacy Readiness Gate

- Product or idea:
- Origin ticket:
- Evaluator:
- Date:
- Exposure type:
- External participants involved: yes/no

## Source artifacts
- MVP scope:
- Validation plan or scorecard:
- Customer data retention policy:
- Approval gate reference:
- Risk review:
- PMF evidence metrics, if applicable:
- Branding/prototype readiness, if applicable:

## Checklist summary
- User exposure:
- External communication:
- Customer data:
- Raw notes or recordings:
- Secrets or credentials:
- Auth and access:
- Billing or payment:
- Sensitive claims:
- Logging and observability:
- Deletion path:
- Support path:
- Brand/prototype clarity:
- Scope control:

## Decision
- Gate decision: GO / CONDITIONAL GO / BLOCKED / NO-GO / NOT APPLICABLE
- Rationale:
- Required approvals:
- Approval record or blocker:
- Required mitigations:
- Allowed next action:
- Blocked actions:
- Retention/deletion owner:
- Residual risk:
```

## Handoff Rules

When this gate applies, the Linear ticket, PR, or validation artifact should record:

- decision
- source artifacts reviewed
- approvals or blockers
- data captured or explicitly not captured
- storage location, if private notes exist outside the repository
- anonymization or deletion expectations
- residual risk
- allowed next action
- blocked actions

Do not include private customer details, secrets, credentials, production data, or sensitive raw notes in the handoff.

## Relationship To Existing Artifacts

- Use `execution/approval-gates.md` for actions that require human approval.
- Use `validation/customer-data-retention-policy.md` for customer discovery data handling.
- Use `execution/risk-reviewer-matrix-lite.md` when a material risk needs severity, mitigation, owner, and blocker status.
- Use `product/mvp-scope.md` to keep user exposure tied to the smallest ethical test.
- Use `validation/branding-prototype-readiness-gate.md` when brand, screen, prototype, copy, or UX ambiguity could distort customer-facing learning.
- Use `growth/channel-experiment-template.md` before outreach, publishing, ads, or channel experiments.
- Use `monetization/pricing-hypothesis-template.md` before willingness-to-pay tests, paid pilots, pricing collection, or billing discussions.
