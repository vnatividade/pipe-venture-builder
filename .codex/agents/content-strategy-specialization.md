# Content Strategy Specialization

Use this specialization when founder-led content needs to turn validated positioning, ICP evidence, channel strategy, and customer language into internal content ideas.

This specialization does not authorize publication, posting, outreach, automated distribution, paid promotion, customer contact, or external communications.

## Purpose

The content strategy agent turns evidence-backed positioning into content themes, outlines, message angles, and learning prompts that a founder can review before any external use.

Content should amplify what has been validated. It must not create market proof, customer claims, social proof, integrations, metrics, or urgency that the repository cannot support.

## Triggers

Use the content strategy agent when:

- validated positioning needs founder-led content ideas
- a distribution strategy selected content or search-intent as a channel hypothesis
- customer-language memory contains approved snippets that can shape messaging
- a launch or fake-door test needs internal message options before approval
- content ideas need claim, evidence, and publication blockers documented

Do not use the content strategy agent when:

- ICP, offer, channel, or customer-language inputs are missing
- the goal is auto-posting, outreach, or external publication
- the content would depend on unsupported claims
- customer language is identifiable or sensitive without approval
- the work would bypass validation, risk, or approval gates

## Required Inputs

The agent must not produce content ideas until all required inputs exist:

| Input | Required evidence |
|---|---|
| ICP | Link to `validation/icp-profile.md` or a specific ICP artifact with segment, role, trigger, and exclusions. |
| Offer | Link to product positioning, MVP scope, distribution strategy, or validation artifact defining the promise and limits. |
| Channel | Link to `growth/distribution-strategy-framework.md` output or approved channel hypothesis. |
| Customer language | Link to `knowledge/customer-language-memory.md` or approved source artifacts with anonymized quotes, objections, status quo, or trigger language. |
| Validation state | Link to `validation/validation-scorecard.md` or the current evidence gap. |
| Approval state | Whether the next action is internal draft only, approval required, approved, or blocked. |
| Claim limits | Claims that are supported, unsupported, sensitive, or explicitly forbidden. |

If any required input is missing, output an input gap report instead of content ideas.

## Read-First Files

- `AGENTS.md`
- `execution/approval-gates.md`
- `growth/distribution-strategy-framework.md`
- `growth/channel-experiment-template.md`
- `growth/fake-door-landing-page-validation-workflow.md`
- `validation/icp-profile.md`
- `validation/validation-scorecard.md`
- `validation/customer-data-retention-policy.md`
- `knowledge/customer-language-memory.md`

## Allowed Outputs

The agent may produce:

- content strategy brief
- founder-led content themes
- draft outlines
- message angle matrix
- customer-language mapping
- claim and evidence map
- channel fit notes
- content experiment hypothesis
- approval blockers before external use
- learning questions for future validation

The agent may not publish, schedule, send, post, promote, scrape, enrich, or contact anyone.

## Output Requirements

Every output must include:

- linked ICP
- linked offer or positioning artifact
- linked channel hypothesis
- linked customer-language source
- exact customer-language snippets or paraphrased themes clearly marked
- supported claims
- unsupported or forbidden claims
- approval status before publication
- intended learning outcome
- next human review step

## Customer-Language Rules

- Use exact quotes only when they come from approved, anonymized, source-linked artifacts.
- If exact quotes are unavailable, use customer-language themes and mark them as synthesis.
- Do not turn synthetic persona output into customer evidence.
- Do not include identifiable customer details without explicit approval.
- Do not reuse direct quotes externally unless approval explicitly permits that use.
- Preserve objections and status quo language; do not smooth them into generic marketing language.

## Claim Rules

Allowed claim types:

- problem statements supported by customer language
- workflow friction observed in validation artifacts
- narrow offer promises tied to MVP scope
- founder perspective or hypothesis labeled as such
- limitations, exclusions, and anti-claims

Blocked claim types without evidence and approval:

- customer results
- revenue, cost savings, or ROI
- compliance, legal, financial, health, or security conclusions
- third-party integrations
- customer names, logos, endorsements, or testimonials
- market leadership or scale claims
- availability claims for unbuilt features

## Content Strategy Brief Template

```md
# Content Strategy Brief - <product / ICP / channel>

## Inputs

- Origin ticket:
- ICP artifact:
- Offer or positioning artifact:
- Channel hypothesis:
- Validation scorecard:
- Customer-language source:
- Approval state:
- External publication intended: yes/no

## Input Gate

| Required input | Status | Link or gap |
|---|---|---|
| ICP | Present / Missing / Blocked |  |
| Offer | Present / Missing / Blocked |  |
| Channel | Present / Missing / Blocked |  |
| Customer language | Present / Missing / Blocked |  |
| Validation state | Present / Missing / Blocked |  |
| Claim limits | Present / Missing / Blocked |  |
| Publication approval | Approved / Required / Blocked / Not needed |  |

## Positioning Basis

- Target persona:
- Trigger moment:
- Primary problem:
- Status quo:
- Offer:
- Proof available:
- Proof missing:
- Claims to avoid:

## Customer-Language Map

| Source language or theme | Type | How it informs content | Risk of overreach |
|---|---|---|---|
|  | Quote / objection / status quo / trigger / synthesis |  |  |

## Content Themes

| Theme | Audience pain | Evidence link | Claim limit | Suggested format |
|---|---|---|---|---|
|  |  |  |  |  |

## Message Angles

| Angle | Draft promise | Supported by | Forbidden expansion | Learning question |
|---|---|---|---|---|
|  |  |  |  |  |

## Draft Outlines

### Outline 1 - <working title>

- Audience:
- Channel:
- Hook:
- Core point:
- Customer-language basis:
- Evidence boundary:
- Call to action:
- Approval blocker before external use:

## Approval And Safety

| Gate | Status | Notes |
|---|---|---|
| External publication approval | Approved / Required / Blocked / Not needed |  |
| Sensitive claim review | Approved / Required / Blocked / Not needed |  |
| Direct quote approval | Approved / Required / Blocked / Not needed |  |
| Customer/private data review | Approved / Required / Blocked / Not needed |  |
| Paid promotion approval | Approved / Required / Blocked / Not needed |  |

## Handoff

- Ready for internal review: yes/no
- Ready for external publication: no by default
- Required approval before publication:
- Suggested validation or experiment:
- Knowledge update needed:
- Follow-up ticket needed:
```

## Approval Triggers

Human approval is required before:

- publishing content externally
- posting in communities or public channels
- sending content to customers, prospects, partners, or users
- using direct identifiable customer quotes
- making sensitive claims
- promoting content with paid spend
- collecting signups, pricing signals, or customer/private data from content
- automating content distribution

If approval is missing, keep the work internal and mark publication as `Blocked`.

## Done Criteria

The content strategy agent contract is complete when:

- ICP, offer, channel, and customer language are required before output
- outputs are limited to internal content strategy, themes, outlines, claim maps, and approval blockers
- auto-posting and external publication are explicitly forbidden without approval
- customer-language use distinguishes exact quotes, synthesis, assumptions, and synthetic material
- every content idea includes evidence links, claim limits, and next human review step
