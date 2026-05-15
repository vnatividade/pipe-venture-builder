# Approval Gates

This policy defines actions that require human approval before an agent proceeds.

## Authority

Approval gates protect founder control, legal and financial risk, customer trust, and operational traceability.

Agents may prepare drafts, summarize options, or propose changes without approval. Agents must not execute gated actions until approval is explicit in the current conversation or recorded in the assigned Linear ticket.

## Required Approval Matrix

| Action | Approval required before |
|---|---|
| Linear project creation | Creating the project |
| Linear ticket creation | Creating the ticket |
| Pull request opening | Opening the PR |
| Pull request merge | Merging the PR |
| Production deployment | Deploying or enabling production execution |
| Paid ads or acquisition spend | Activating, scheduling, or increasing spend |
| Billing or pricing collection | Enabling billing, payments, subscriptions, invoices, or checkout |
| Secrets and credentials | Reading, storing, rotating, using, or transmitting secrets |
| Customer outreach | Sending external messages, emails, DMs, or automated follow-ups |
| External communications | Publishing, posting, announcing, or contacting third parties |
| Legal, financial, compliance, privacy, or security content | Changing the substance of the content |
| Sensitive claims | Adding or changing claims about evidence, customers, integrations, metrics, validation, or regulated outcomes |
| Production/customer data | Accessing, exporting, modifying, deleting, or sharing data |

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
