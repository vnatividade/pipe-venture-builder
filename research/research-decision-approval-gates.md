# Research Decision Approval Gates

This policy defines approval gates for research-driven decisions so automated discovery can recommend next actions without directly triggering build work, outreach, billing, sensitive claims, roadmap changes, or external actions.

Use it with `AGENTS.md`, `execution/approval-gates.md`, `research/research-orchestrator-workflow.md`, `research/research-synthesis-template.md`, `research/idea-ranking-engine-design.md`, `research/market-signal-ingestion-template.md`, and `.codex/agents/research-validation-specialization.md`.

## Authority

`AGENTS.md` and `execution/approval-gates.md` remain the governing approval policies for this repository.

This document narrows those gates for research-driven decisions. It does not weaken or replace existing approval requirements.

When this document conflicts with `AGENTS.md` or `execution/approval-gates.md`, follow the stricter gate.

## Boundary

Research automation may:

- summarize approved sources
- propose hypotheses
- recommend customer discovery questions
- recommend research synthesis
- recommend ranking updates
- recommend follow-up tickets
- flag risks, contradictions, and sensitive claims

Research automation must not directly:

- create Linear tickets
- open or merge PRs
- create build or implementation work
- contact customers or communities
- send external communications
- enable billing, pricing collection, paid ads, or paid acquisition
- change legal, financial, compliance, privacy, security, scientific, customer-evidence, or regulated claims
- change PRD, MVP scope, roadmap, backlog priority, growth, monetization, or public positioning
- handle secrets, credentials, customer data, production data, private keys, or tokens

Read-only research summaries are allowed when they stay inside approved source boundaries and do not claim decision authority.

## Approval Matrix

| Research-driven output or recommendation | Research may do without additional approval | Human approval required before |
|---|---|---|
| Source summary | Summarize approved, inspectable sources with citations, dates, confidence, and limitations. | Using summary to change claims, strategy, PRD, MVP scope, roadmap, or tickets. |
| Research synthesis | Recommend interpretation, next test, or handoff with uncertainty visible. | Treating synthesis as decision authority or changing product artifacts. |
| Evidence score | Provide advisory score and confidence limits. | Using score for ranking, prioritization, validation thresholds, or scope decisions. |
| Idea ranking | Produce advisory ranking with source traceability and confidence. | Prioritizing one idea over another or changing backlog order. |
| Market signal | Tag, source, and route the signal to ranking, synthesis, source log, rejected, or blocked. | Changing roadmap, backlog, claims, or outreach based on the signal. |
| Follow-up ticket recommendation | Draft title, context, scope, and acceptance criteria in a PR/Linear comment. | Creating the Linear ticket. |
| Customer discovery question | Draft questions and evidence needs. | Contacting customers, communities, or third parties. |
| Outreach recommendation | Identify why outreach may be useful. | Sending messages, emails, DMs, surveys, forms, or automated follow-ups. |
| Build recommendation | State what could be built after gates are satisfied. | Creating build tickets, implementation work, architecture tickets, or PRD/MVP changes. |
| Billing or pricing hypothesis | Record as assumption or research question. | Enabling billing, checkout, pricing collection, paid pilots, subscriptions, or invoices. |
| Growth or paid acquisition hypothesis | Record as assumption or research question. | Running paid ads, paid acquisition, public campaigns, or external distribution tests. |
| Sensitive claim review | Flag unsupported, risky, or regulated claims. | Adding, changing, publishing, or relying on legal, financial, compliance, privacy, security, scientific, health, customer-evidence, market-validation, or regulated claims. |
| External tool or MCP use | Plan source needs and approval blockers. | Configuring connectors, credentials, paid/private tools, scraping, sync, or automated ingestion. |
| Data handling recommendation | Identify data risk and minimization need. | Reading, storing, exporting, sharing, or processing customer, production, confidential, sensitive, credentialed, or private data. |

## Decision States

Use these states in research artifacts:

| State | Meaning | Allowed next action |
|---|---|---|
| Draft research | Sources or synthesis are incomplete. | Continue read-only research or source review. |
| Advisory recommendation | Research suggests an action but approval is not granted. | Record recommendation and approval blocker. |
| Blocked for approval | Action would cross an approval gate. | Stop and request human approval or create approved follow-up path. |
| Approved for execution | Human approval is explicit in Linear, PR, or current thread. | Execute only the approved action and scope. |
| Rejected or deferred | Human reviewer declines or postpones action. | Record rationale and avoid repeated execution attempts. |

Do not treat silence, prior chat memory, or a model inference as approval.

## Sensitive Claim Gate

Research must flag human review before any claim that implies:

- customer validation
- customer commitments
- market proof
- willingness to pay
- revenue, conversion, adoption, usage, or operational metrics
- third-party integration availability
- scientific, clinical, legal, financial, compliance, privacy, security, safety, or regulated conclusions
- product capability that has not been implemented or verified

If a source supports only a narrow claim, wording must stay narrow. If the source trail is weak, mark the claim as unsupported or blocked.

## External Action Gate

Research may recommend external action, but explicit human approval is required before:

- contacting customers, prospects, communities, competitors, analysts, experts, or partners
- publishing research or claims externally
- creating surveys, forms, campaigns, ads, or public tests
- using paid tools, private workspaces, credentialed databases, or connectors
- scraping or automating source collection
- sending emails, DMs, posts, comments, or announcements

If approval is missing, record the recommendation as blocked.

## Ticket And Roadmap Gate

Research may recommend follow-ups, but must not create tickets or change roadmap without approval.

Before a research-driven ticket or roadmap change is executed, record:

- source artifact or research synthesis
- decision owner
- recommended action
- risk if wrong
- approval source
- scope boundary
- excluded actions
- follow-up or rollback condition when relevant

Automated research must not create Linear tickets, close tickets, change ticket priority, or contact customers.

## Build, Billing, And Growth Gate

Research can identify a promising idea, channel, pricing hypothesis, or MVP test.

It cannot directly trigger:

- implementation tickets
- architecture tickets
- code changes
- deployment
- billing setup
- checkout or payment collection
- pricing collection
- paid acquisition
- growth automation
- customer outreach

Build, billing, and growth decisions must pass the existing product, validation, MVP, risk, and approval gates.

## Approval Record Template

Use this block in research synthesis, ranking, PR, or Linear comments when approval is needed.

```md
## Research Decision Approval

- Research artifact:
- Recommended action:
- Approval gate triggered:
- Decision owner:
- Risk if wrong:
- Sensitive claim involved: yes/no
- External action involved: yes/no
- Customer/production/private data involved: yes/no
- Approval status: Draft / Advisory recommendation / Blocked for approval / Approved for execution / Rejected or deferred
- Approval source:
- Approved scope:
- Explicit exclusions:
- Follow-up or rollback condition:
```

## Review Checklist

Before acting on research, confirm:

- Is this still read-only research, or does it change execution?
- Are source IDs, dates, confidence, limitations, and risk if wrong visible?
- Does this affect PRD, MVP scope, backlog, ranking, growth, monetization, claims, or external communication?
- Does it involve customers, communities, third parties, paid tools, connectors, credentials, or private data?
- Does it create or modify tickets, PRs, deployments, billing, or paid acquisition?
- Is the approval source explicit and current?
- Is the action narrow enough to match the approval?

If any answer is unclear, stop and record the approval blocker.

## Done Criteria

This gate is complete when:

- research can recommend actions without executing them
- approval matrix covers research-driven changes, sensitive claims, and external actions
- read-only research summaries remain allowed
- automated research cannot create tickets, contact customers, trigger build work, enable billing, or change claims
- approval records name the action, gate, owner, risk, approval status, source, scope, and exclusions
- the policy explicitly ties back to `AGENTS.md` and `execution/approval-gates.md`
