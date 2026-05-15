# Risk Reviewer And Matrix Lite

This document defines a lightweight risk review for product, technical, legal, financial, privacy, security, and operational risk.

It is a triage and escalation tool. It is not legal, financial, compliance, privacy, security, or professional advice, and it does not claim regulatory compliance. When a topic may require specialized judgment, stop and require explicit human review or specialist review before proceeding.

## Purpose

Use this review to catch high-impact risks before work proceeds, without turning low-risk learning tests into enterprise risk bureaucracy.

The risk reviewer should:

- identify material risks early
- separate reversible from irreversible actions
- classify likelihood and impact
- define mitigation, owner, trigger, and approval rule
- stop work when required approval is missing
- keep review proportional to the ticket scope

## Risk Reviewer Contract

Purpose: Identify product, technical, legal, financial, privacy, security, and operational risks before execution proceeds.

Triggers:

- a ticket, PR, artifact, or product decision touches approval-gated areas
- MVP scope, architecture, validation, growth, billing, outreach, or production work introduces risk
- a reviewer finds possible P0 or P1 issues
- a decision could create unsupported sensitive claims, customer evidence, revenue claims, market proof, integration claims, or regulated outcomes

Required inputs:

- linked Linear ticket
- source repository artifact or PR
- stated scope and excluded scope
- assumptions and evidence
- approval status
- known dependencies and blockers

Expected outputs:

- risk matrix row for each material risk
- severity and blocker status
- mitigation or acceptance recommendation
- owner and trigger
- approval rule
- follow-up candidate when risk is outside current scope

Allowed actions:

- classify and summarize risk
- recommend mitigation
- require explicit approval before gated actions
- mark work as blocked by unresolved P0/P1 risk
- propose follow-up tickets when approved

Restricted actions:

- accepting high-impact risk without explicit approval
- weakening approval gates
- giving legal, financial, privacy, compliance, or security advice beyond triage
- claiming compliance, market validation, customer evidence, revenue, integrations, or regulated outcomes without source artifacts
- blocking low-risk, reversible learning tests when no approval gate is triggered

Approval triggers:

- accepting unresolved high-risk or irreversible risk
- changing legal, financial, compliance, privacy, security, or sensitive claims
- handling secrets, credentials, customer data, or production data
- customer outreach, external communication, billing, paid ads, or production deployment
- creating Linear tickets or projects, opening PRs, or merging PRs

## Matrix Lite Fields

Use one row per material risk.

| Field | Meaning |
|---|---|
| Risk | Concise description of what could go wrong. |
| Category | Product / Technical / Legal / Financial / Privacy / Security / Operational. |
| Reversibility | Reversible / Hard to reverse / Irreversible. |
| Likelihood | Low / Medium / High. |
| Impact | Low / Medium / High. |
| Severity | P0 / P1 / P2 / P3. |
| Mitigation | Action that reduces likelihood or impact. |
| Owner | Person or agent role accountable for the mitigation. |
| Trigger | Event or condition that makes this risk active. |
| Approval Rule | Approval, acceptance, or specialist review required before proceeding. |
| Status | Open / Mitigated / Accepted / Blocked. |

## Severity Rules

Use the repository severity model from `execution/approval-gates.md`.

| Severity | Use When | Execution Effect |
|---|---|---|
| P0 | Critical, blocking, production risk, security risk, data loss, unsafe external impact, or irreversible high-impact risk. | Stop. Must be mitigated before merge or execution. If business risk acceptance is proposed, document it and require explicit human approval; acceptance does not override unresolved P0 review findings. |
| P1 | Relevant bug, likely regression, important architecture issue, critical missing test, or material approval/risk gap. | Stop. Must be fixed or mitigated before merge or execution. If business risk acceptance is proposed, document it and require explicit human approval; acceptance does not override unresolved P1 review findings. |
| P2 | Important improvement or moderate risk that is not blocking. | Fix only when simple, safe, and inside scope; otherwise record follow-up. |
| P3 | Cosmetic, small process concern, or low-impact improvement. | Does not block. |

## Likelihood And Impact

Likelihood:

- Low: plausible but unlikely during this ticket or current phase
- Medium: credible under normal execution
- High: likely without mitigation

Impact:

- Low: local, reversible, and does not affect approval gates or external parties
- Medium: affects project quality, decision confidence, or workflow reliability
- High: affects customer trust, safety, money, legal/privacy/security posture, production, external communication, sensitive claims, or irreversible decisions

## Reversibility Rule

Reversibility changes how strict the review should be:

- Reversible: can proceed when scoped, validated, and no approval gate is triggered
- Hard to reverse: require a named mitigation and owner
- Irreversible: require explicit human approval or documented acceptance before proceeding

Examples of irreversible or hard-to-reverse actions include external communication, customer outreach, billing activation, paid acquisition, production deployment, handling customer or production data, changing sensitive claims, or accepting unresolved high-impact risk.

## Approval And Specialist Review

Human approval is required for all actions listed in `execution/approval-gates.md`.

Specialist or explicit human review should be requested when:

- legal, financial, compliance, privacy, or security substance is being changed
- the repository would make claims about compliance, regulated outcomes, revenue, customer evidence, integrations, or market validation
- customer data, production data, secrets, credentials, payment, health, legal, or confidential third-party material is involved
- the reviewer cannot determine whether a risk is acceptable from repository artifacts

Do not infer approval from silence, prior chat context, or convenience.

## Risk Matrix Template

```md
## Risk Matrix Lite

| Risk | Category | Reversibility | Likelihood | Impact | Severity | Mitigation | Owner | Trigger | Approval Rule | Status |
|---|---|---|---|---|---|---|---|---|---|---|
|  | Product / Technical / Legal / Financial / Privacy / Security / Operational | Reversible / Hard to reverse / Irreversible | Low / Medium / High | Low / Medium / High | P0 / P1 / P2 / P3 |  |  |  |  | Open / Mitigated / Accepted / Blocked |
```

## Review Output Template

```md
## Risk Review

Reviewer:
Date:
Ticket or PR:
Source artifacts:

## Summary
- Overall status: Clear / Clear with mitigations / Blocked
- Highest severity:
- Approval required: yes/no
- Specialist review recommended: yes/no

## Matrix
<paste Risk Matrix Lite rows>

## Decision
- Proceed:
- Proceed after mitigation:
- Stop:
- Explicit acceptance needed:

## Follow-ups
- Needed:
- Reason:
- Owner:
```

## Low-Risk Learning Tests

Do not block low-risk learning tests only because they are imperfect.

A learning test can proceed when:

- it is reversible
- it does not trigger approval gates
- it does not involve secrets, customer data, production data, billing, paid ads, external communication, or sensitive claims
- assumptions and evidence gaps are recorded
- validation expectations are clear

## Done Criteria

Risk review is complete when:

- material risks have matrix rows
- likelihood, impact, severity, mitigation, owner, trigger, approval rule, and status are filled
- P0/P1 risks are mitigated or blocking; any proposed business risk acceptance is documented separately and does not override unresolved P0/P1 review findings
- high-risk or irreversible items have explicit approval or documented acceptance
- legal, financial, compliance, privacy, and security concerns are treated as triage and escalated when needed
- out-of-scope risks are recorded as follow-up candidates instead of being fixed inside the wrong ticket
