# Approval Gates

This policy defines actions that require human approval before an agent proceeds.

## Authority

Approval gates protect founder control, legal and financial risk, customer trust, and operational traceability.

Agents may prepare drafts, summarize options, or propose changes without approval. Agents must not execute gated actions until approval is explicit in the current conversation, recorded in the assigned Linear ticket, or granted as a standing pre-approval by the repository's declared operating mode (`execution/operating-modes.md`).

## Operating Modes

`execution/operating-modes.md` parameterizes this policy per repository:

- In a repository that explicitly declares `exploration` mode (`.pipe/mode.json`, human-activated), the gates marked **mode-sensitive** below carry a standing founder pre-approval: agents execute them autonomously with mandatory logging.
- In `restricted` mode — or when no valid mode file exists — every gate below requires per-action human approval. Restricted is the fail-safe default.
- Gates marked **absolute** require human approval in both modes, always.

Before any real user, prospect, customer, partner, community member, or external participant touches a product, prototype, manual test, form, workflow, dataset, prompt output, trial, or validation artifact, apply `validation/pre-user-security-privacy-readiness-gate.md`.

## Required Approval Matrix

| Action | Approval required before | Mode sensitivity |
|---|---|---|
| Linear project creation | Creating the project | Mode-sensitive |
| Linear ticket creation | Creating the ticket | Mode-sensitive |
| Pull request opening | Opening the PR | Mode-sensitive |
| Pull request merge | Merging the PR | Mode-sensitive (exploration review path still applies; P0/P1 still block) |
| Non-production deployment | Deploying to preview, staging, development, or demo targets | Mode-sensitive |
| Production deployment | Deploying or enabling production execution | Absolute |
| Paid ads or acquisition spend | Activating, scheduling, or increasing spend | Absolute |
| Billing or pricing collection | Enabling billing, payments, subscriptions, invoices, or checkout | Absolute |
| Secrets and credentials | Reading, storing, rotating, using, or transmitting secrets | Absolute |
| Customer outreach | Sending external messages, emails, DMs, or automated follow-ups | Absolute |
| External communications | Publishing, posting, announcing, or contacting third parties | Absolute |
| Legal, financial, compliance, privacy, or security content | Changing the substance of the content | Absolute |
| Sensitive claims | Adding or changing claims about evidence, customers, integrations, metrics, validation, or regulated outcomes | Absolute |
| Production/customer data | Accessing, exporting, modifying, deleting, or sharing data | Absolute |
| Operating mode changes | Creating, editing, or deleting `.pipe/mode.json`; changing this policy | Absolute (human-only) |

## Review Severity Rules

- P0: critical, blocking, production risk, security risk, data loss, or unsafe external impact.
- P1: relevant bug, likely regression, important architecture issue, or missing test on critical flow.
- P2: important improvement that is not blocking.
- P3: cosmetic suggestion, style preference, or small improvement.

P0 and P1 findings block merge. P2 findings are fixed only when simple, safe, and inside the current ticket scope. P3 findings do not block merge.

## NO-GO Conditions

Do not proceed when:

- approval is required and missing
- the ticket scope is ambiguous
- the work would bypass validation gates
- the work would create unsupported customer, metric, revenue, integration, or market evidence
- the change would broaden MVP scope without an approved ticket
- the action would expose secrets, customer data, or private operational details
- review found unresolved P0 or P1 issues

## Handling Out-Of-Scope Findings

When an agent finds a relevant issue outside the current ticket scope:

1. Do not fix it in the current PR unless it is required to complete the ticket safely.
2. Create a Linear follow-up ticket with context, impact, suggested scope, acceptance criteria, and origin.
3. Reference the follow-up in the PR and in the current Linear ticket.

## Evidence Rules

Repository claims must be traceable. Agents must not invent:

- customers
- interviews
- research findings
- conversion data
- revenue
- willingness-to-pay evidence
- third-party integrations
- operational metrics
- scientific or regulated validation

If evidence is missing, state that it is missing and create or execute the relevant validation ticket.
