# Proprietary Data Moat Strategy

Use this strategy when a venture idea, PRD, or architecture review claims defensibility from data, workflow learning, accumulated evidence, or operational feedback.

This document does not authorize collecting customer data, production data, secrets, credentials, regulated data, or confidential business records. It defines how to think about data moat potential before build work, while preserving the approval gates in `AGENTS.md`, `execution/approval-gates.md`, and `validation/customer-data-retention-policy.md`.

## Purpose

Pipe-generated ventures should not rely only on generic model access or public API availability for defensibility.

Before architecture or implementation tickets are created, the venture should identify:

- what useful data or learning could compound over time
- whether the data is allowed, sensitive, prohibited, or synthetic
- what loop turns usage into better decisions, workflows, or product quality
- what must stay out of the repository and out of early MVP scope
- what evidence is still missing

Data moat claims are hypotheses until validated by source artifacts. Do not invent customers, metrics, usage patterns, integrations, or market evidence.

## Data Categories

| Category | Definition | Examples | Repository treatment | Approval posture |
|---|---|---|---|---|
| Strategic learning | Reusable conclusions about market, ICP, workflow, objections, or positioning. | Validated ICP pattern, repeated objection, discovered workflow bottleneck. | May be stored as anonymized synthesis with source links. | Normal review, unless sensitive source material is involved. |
| Operational workflow data | Data created by users or operators while running the product workflow. | Task status, workflow step, review outcome, completion signal, error pattern. | Define expected capture in PRD/architecture; do not store real data before approval. | Requires explicit boundary and retention expectation before implementation. |
| Customer evidence | Quotes, interviews, commitments, observed behavior, workaround evidence, willingness signals. | Interview notes, anonymized quote, repeated manual workaround. | Follow `validation/customer-data-retention-policy.md`; prefer anonymized summaries. | Identifiable or raw evidence requires explicit approval. |
| Sensitive data | Data that could create privacy, legal, financial, security, compliance, or customer-trust risk. | Personal data, confidential workflows, regulated records, private files. | Do not store in repository. Record only non-sensitive blocker or pointer when approved. | Stop and request approval before handling. |
| Prohibited data | Data that should not be collected for the current venture or MVP. | Secrets, credentials, payment details, private keys, unapproved production/customer data. | Never store in repository. Delete accidental capture when safe and document non-sensitive blocker. | No-go unless a dedicated approved policy/ticket changes the boundary. |
| Synthetic data | Artificial examples used for design, tests, prompts, or validation-question generation. | Synthetic personas, generated records, fake transcripts, mock workflow logs. | May be stored when clearly labeled synthetic. | Must never be treated as customer evidence or market proof. |
| Public/reference data | Publicly available docs, reports, APIs, benchmark references, or open datasets. | Official docs, public pricing pages, reputable reports. | May be linked or summarized with source. | Cite source; respect license and usage limits. |

## Required Data Moat Fields

Add these fields to venture planning, PRD, and architecture review when the venture depends on learning, workflow data, personalization, evidence accumulation, or proprietary signals.

| Field | Required answer |
|---|---|
| Data moat hypothesis | What data or learning could become more useful as the venture is used? |
| Why it compounds | How does repeated use improve decision quality, workflow fit, trust, speed, cost, or defensibility? |
| Data category | Strategic learning / operational workflow data / customer evidence / sensitive / prohibited / synthetic / Public/reference data. |
| Source artifact | Which validation, PRD, interview, research, or architecture artifact supports the claim? |
| Allowed capture | What may be captured now, if anything? |
| Data explicitly avoided | What must not be collected, stored, or inferred? |
| Learning loop | What input becomes what decision, recommendation, workflow improvement, or product change? |
| Promotion criteria | What evidence is required before moving from assumption to reusable knowledge, PRD requirement, or implementation ticket? |
| Retention expectation | How long should captured data or learning remain useful? |
| Privacy/trust risk | What could make this unsafe, creepy, legally risky, or trust-eroding? |
| Mitigation | What boundary, anonymization, manual review, deletion rule, or approval gate reduces the risk? |

If the data moat hypothesis is vague, unsourced, or based only on generic model output, record it as an assumption and keep build scope narrow.

## Learning Loop Model

Use this loop to make data moat claims concrete:

1. **Capture:** Identify the minimum allowed signal needed to learn.
2. **Classify:** Mark the signal as evidence, assumption, synthesis, synthetic, sensitive, or prohibited.
3. **Use:** Explain the immediate product, workflow, validation, or decision benefit.
4. **Improve:** Define how repeated use changes the product, prompt, workflow, ICP, or prioritization.
5. **Promote:** Move the learning into PRD, architecture, KDR/DAR, customer-language memory, or backlog only when source artifacts justify it.
6. **Retire:** Delete, archive, or downgrade data that is stale, unsafe, unsupported, or no longer useful.

Learning that changes future strategic decisions should use `knowledge/kdr-dar-template.md`. Customer language should use `knowledge/customer-language-memory.md`. Routine execution handoff should stay in Linear and PR comments.

## Promotion Criteria

Do not promote a data moat claim into PRD or implementation scope unless it has at least one of:

- repeated customer evidence from approved discovery artifacts
- observed workflow behavior from an approved MVP/trial
- cited research or market evidence relevant to the ICP
- architecture/risk review showing that the data boundary is safe enough for the intended test
- explicit human approval for any sensitive or identifiable data handling

Synthetic examples can promote better questions. They cannot promote market proof.

## PRD Integration

In `product/prd.md`, Data Moat fields should be completed when:

- the venture claims defensibility from proprietary data, workflow learning, personalization, or accumulated evidence
- the MVP captures user, customer, workflow, or operational signals
- the product experience changes based on repeated use
- the PRD proposes storing customer evidence, quotes, or behavior

If not applicable, state why the MVP does not depend on a data moat yet.

## Architecture Integration

In `architecture/architecture-review.md`, the architecture must preserve the data boundary:

- list data captured and data avoided
- identify where data would be stored if implementation is approved
- define retention expectations
- flag sensitive/prohibited data as blockers
- keep manual workflow paths when they validate faster or reduce risk
- avoid database/vector/runtime work until the PRD and approval gates justify it

## Synthetic Application Checks

### B2B SaaS Example

| Check | Example answer |
|---|---|
| Data moat hypothesis | Repeated workflow reviews reveal which operational bottlenecks block task completion. |
| Data category | Operational workflow data plus strategic learning. |
| Learning loop | Task outcomes and operator notes improve prioritization, onboarding prompts, and exception handling. |
| Data avoided | Customer secrets, private files, credentials, and identifiable employee performance data. |
| Promotion criteria | Repeated anonymized workflow evidence across approved discovery or MVP runs. |
| Risk | Users may perceive monitoring as surveillance. |
| Mitigation | Capture only workflow-level signals; document retention and avoid individual performance claims. |

### Marketplace Example

| Check | Example answer |
|---|---|
| Data moat hypothesis | Matching quality improves as supply/demand constraints, failed matches, and trust signals accumulate. |
| Data category | Operational workflow data, customer evidence, and public/reference data. |
| Learning loop | Failed match reasons improve qualification, ranking, and channel focus. |
| Data avoided | Payment data, private communications, sensitive identity data, and unsupported claims about liquidity. |
| Promotion criteria | Validated supply/demand interactions, not synthetic marketplace simulations alone. |
| Risk | Prematurely claiming marketplace liquidity or network effects. |
| Mitigation | Separate assumptions from evidence and require source artifacts before PMF claims. |

### Internal Tooling Example

| Check | Example answer |
|---|---|
| Data moat hypothesis | Repeated internal agent execution creates reusable patterns for ticket readiness, validation gaps, and review blockers. |
| Data category | Strategic learning and agentic operations learning. |
| Learning loop | PR and Linear handoffs improve future ticket templates, agent prompts, and governance rules. |
| Data avoided | Secrets, credentials, private customer data, and unapproved production data. |
| Promotion criteria | Recurring pattern across multiple completed tickets, not one-off preference. |
| Risk | Process documentation grows faster than actual execution learning. |
| Mitigation | Store only learning that changes future decisions or execution behavior. |

## Anti-Patterns

- Treating public API access as a moat.
- Treating synthetic personas as customer evidence.
- Capturing more data than the MVP needs.
- Storing raw customer notes in the repository by default.
- Building pgvector, memory, or analytics infrastructure before the learning loop is validated.
- Claiming proprietary data before data exists.
- Confusing operational logs with strategic learning.
- Keeping stale learning because it once supported a decision.

## Handoff Checklist

When a ticket touches data moat strategy, PRD, architecture, or knowledge promotion, record:

- Data moat hypothesis:
- Data category:
- Source artifacts:
- Allowed capture:
- Data explicitly avoided:
- Learning loop:
- Promotion criteria:
- Retention expectation:
- Privacy/trust risk:
- Approval needed: yes/no
- Follow-up ticket needed: yes/no
