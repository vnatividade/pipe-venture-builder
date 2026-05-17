# Agent Handoff Protocol

Use this protocol when one agent role passes work, context, risks, or next steps to another agent role.

The handoff must be explicit enough for a future agent to continue without relying on chat memory. It is not an automated multi-agent execution system.

## When To Use

Use an agent handoff when:

- a ticket moves from strategy to validation, research, architecture, risk, execution, Linear, or knowledge work
- a PR or Linear ticket leaves unresolved questions for another owner
- a trial or artifact creates KDR, learning, or follow-up context
- work stops because approval, evidence, dependency, or scope is missing

Do not use this protocol to bypass review, approval gates, Linear status, PR handoff, or human decisions.

## Handoff Rules

- Name the sending agent and receiving agent.
- Cite repository artifacts, Linear tickets, PRs, or source links instead of conversation memory.
- Separate decisions, evidence, assumptions, and unresolved questions.
- Include approval status for every gated action.
- Include risks and whether they block the next owner.
- Include done criteria for the next owner.
- State whether a KDR or knowledge update is needed.
- Stop if the next step would require approval that is missing.

## Required Handoff Fields

```md
## Agent Handoff

From agent:
To agent:
Date:
Origin ticket:
Origin PR:
Repository branch:
Executor tool:
Expected write set:
Actual files changed:
Restricted files touched:

## Context
- What was completed:
- Why this handoff is needed:
- Current pipeline phase:

## Sources
- Repository artifacts:
- Linear tickets:
- PRs:
- External sources:

## Decisions
- Decision:
- Rationale:
- Decision owner:
- Supersedes or conflicts with:

## Evidence
- Evidence used:
- Evidence gaps:
- Assumptions still active:
- Claims that must not be treated as evidence:

## Risks
- P0/P1 risks:
- P2/P3 risks:
- Approval-gated risks:
- Mitigations or blockers:
- Residual risk after handoff:

## Approval Status
- Customer outreach:
- External communication:
- Billing or pricing collection:
- Paid ads or acquisition:
- Production deployment:
- Secrets or credentials:
- Customer or production data:
- Legal/financial/compliance/privacy/security/sensitive claims:
- Linear project or ticket creation:
- PR opening or merge:

## Required Artifacts
- Existing artifacts the next owner must read:
- Missing artifacts:
- Artifact updates needed:

## Validation, Monitoring, And Metrics
- Validations executed:
- Validations unavailable:
- Monitoring required:
- Success metrics affected:
- Metrics follow-up needed:

## Unresolved Questions
- Question:
- Why it matters:
- Owner:
- Blocking status:

## Next Owner Scope
- Next owner:
- Included scope:
- Excluded scope:
- Done criteria:
- Validation or review needed:
- Next recommended action:

## KDR / Knowledge Update
- KDR needed: yes/no
- Knowledge artifact to update:
- Revisit trigger:
- Customer-language or private-data concerns:

## Stop Conditions
- Stop if:
- Escalate to:
```

## Minimum Handoff By Transition

| Transition | Required Emphasis |
|---|---|
| Idea intake -> product strategy | raw idea, assumptions, privacy boundaries, evidence gaps |
| Product strategy -> validation | focused market/problem/offer/channel, C.O.N.T.R.O.L.E. verdict, riskiest assumptions |
| Validation -> research | research questions, claim boundaries, source quality needs |
| Validation -> MVP scope | scorecard result, ICP, customer language, evidence threshold |
| MVP scope -> architecture | core loop, explicit cuts, risk notes, implementation blockers |
| Architecture -> risk review | technical choices, data/integration boundaries, failure modes |
| Risk review -> ticketing | accepted risks, blockers, mitigations, approval status |
| Ticketing -> execution | ticket scope, dependencies, acceptance criteria, excluded scope |
| Execution -> Linear steward | executor tool, branch, PR, expected write set, actual files changed, restricted files touched, validation, review, merge, monitoring, metrics, follow-ups, residual risks, next recommended action |
| Execution -> knowledge curator | durable decision, evidence, learning, KDR need, revisit trigger |

## Approval Handling

If approval is missing:

1. Do not continue the gated action.
2. Record the missing approval in the handoff.
3. Identify the owner who can approve or clarify.
4. Document the blocker in Linear or the PR when relevant.

Approval must be explicit before:

- creating Linear projects or tickets
- opening or merging PRs
- customer outreach or external communication
- production deployment
- billing, pricing collection, paid ads, or paid acquisition
- handling secrets, customer data, or production data
- changing legal, financial, compliance, privacy, security, or sensitive claims

## KDR Continuity

Create or recommend a KDR update when the handoff includes:

- a strategic decision
- a change in confidence or GO / NO-GO status
- a superseded assumption
- a risk acceptance decision
- a follow-up sequence that future agents must understand

Do not create a KDR for routine branch, PR, or status details already captured in PR and Linear handoffs.

## Done Criteria For A Handoff

A handoff is complete only when:

- source artifacts are linked
- decisions and evidence are separated from assumptions
- risks and approvals are explicit
- unresolved questions have owners
- next owner and included scope are named
- excluded scope is named
- done criteria for the next owner are clear
- KDR need is stated
- no required context exists only in chat memory

## Alignment With PR And Linear Handoff

For execution tickets, the agent handoff should not replace the final Linear handoff. Use it to transfer context between roles, then preserve final execution state in the Linear handoff required by `execution/ticket-pr-handoff-system.md`.

Execution handoffs must stay safe for repository context. Do not include secrets, credentials, customer data, production data, private source material, or sensitive operational details.
