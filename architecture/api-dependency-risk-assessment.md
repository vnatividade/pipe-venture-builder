# API Dependency Risk Assessment

Use this assessment when a venture depends on public APIs, model providers, third-party platforms, marketplaces, app stores, enterprise systems, or integration partners.

This document does not prohibit public APIs. It helps distinguish healthy leverage from fragile dependency before PRD, architecture, or implementation tickets treat an API-backed product as defensible.

## Purpose

Pipe-generated ventures should avoid becoming thin wrappers around generic model access or public platform features.

Before build work, identify:

- which external capabilities are required for the MVP test
- what would break if the provider changed pricing, policy, model behavior, ranking, permissions, or product roadmap
- whether Big Tech or the platform itself could substitute the product
- what defensibility exists beyond the external API
- what manual or low-tech fallback can validate the riskiest assumption faster

API dependency risk is not automatically bad. It becomes risky when the API is the product, the workflow is shallow, and the venture has no proprietary learning, distribution, trust, compliance, integration depth, or switching cost.

## Risk Levels

| Level | Meaning | Required action |
|---|---|---|
| Low | API supports convenience, but the core value, workflow, learning, or customer relationship does not depend on one provider. | Record dependency and fallback. |
| Medium | API is important to the MVP experience, but there is a plausible mitigation or alternative path. | Define explicit mitigation before architecture or implementation tickets. |
| High | API is central to the product value, hard to replace, or likely to be copied/substituted by the provider or Big Tech. | Stop or narrow scope until mitigation, validation, or human approval is explicit. |

## Acceptable API Leverage

API usage is usually acceptable when:

- the API accelerates validation of a real customer workflow
- the MVP can fall back to a manual or alternate provider path
- the venture owns a customer relationship, workflow, data loop, or distribution path
- the API is infrastructure, not the full product promise
- switching providers would hurt, but would not invalidate the product thesis
- the PRD states what is learned beyond API capability

## Fragile API Dependency

Dependency is fragile when:

- the product is mostly a prompt, UI, or workflow around a single public model/API
- the provider can add the same feature natively with better distribution
- the venture has no proprietary data, customer workflow depth, trust layer, or switching cost
- pricing, rate limits, policy changes, or model behavior would break unit economics or reliability
- the MVP requires broad integration before the riskiest assumption is validated
- the product claim depends on unsupported API performance, availability, or roadmap assumptions

## Substitution Risk

Assess whether a platform, model provider, or Big Tech incumbent could make the product unnecessary.

| Question | Risk signal |
|---|---|
| Could the provider ship this as a native feature? | High if the value is generic and UI-level. |
| Does the provider already own the distribution channel? | High if customers can adopt the native version without switching cost. |
| Does the product depend on a feature that is moving into base models or platform defaults? | Medium or high depending on workflow depth. |
| Would customers still need this if the model/API improved dramatically? | High if answer is no. |
| Does the venture own a vertical workflow, trust boundary, evidence loop, or proprietary data? | Lower risk when yes and sourced. |

## Mitigation Categories

Medium or high API dependency risk requires one or more explicit mitigations.

| Mitigation | What it means | Evidence or design question |
|---|---|---|
| Workflow depth | The product solves a repeated, domain-specific job, not a generic API call. | What workflow steps, exceptions, handoffs, and approvals exist outside the API? |
| Proprietary data | The product accumulates allowed learning or evidence that improves outcomes. | Link to `architecture/proprietary-data-moat-strategy.md`. |
| UX or operational fit | The product reduces friction in a specific context better than the provider can. | What user behavior or workflow evidence supports this? |
| Compliance or trust | The product handles governance, auditability, review, or risk controls the provider does not. | What trust boundary or approval gate matters to the ICP? |
| Distribution | The venture has a channel, community, embedded workflow, or access path the provider lacks. | What source artifact supports access to users? |
| Integration moat | The value comes from connecting systems, data, permissions, or operations in a hard-to-replace way. | Which integration is essential, and what manual fallback exists? |
| Switching cost | Repeated use creates configuration, records, workflows, or training that users do not want to abandon. | What retained value compounds over time? |
| Multi-provider resilience | Architecture can swap providers if needed without changing the product promise. | What abstraction is needed now, and what can defer? |

Do not invent mitigations. If mitigation is only a hope, mark it as an assumption.

## Required Assessment Fields

Use these fields in PRD and architecture review when external APIs or provider capabilities materially affect the MVP.

| Field | Required answer |
|---|---|
| External dependency | Which API, model, platform, integration, or provider is required? |
| Dependency role | Core value / workflow support / infrastructure / optional enhancement. |
| MVP necessity | Required for MVP / can be manual / can be deferred. |
| Risk level | Low / Medium / High, with reason. |
| Substitution risk | Low / Medium / High, with reason. |
| Provider-change risk | Pricing / rate limits / policy / model behavior / roadmap / availability / permissions. |
| Defensibility beyond API | Workflow depth / proprietary data / UX / compliance / distribution / integration moat / trust / switching cost. |
| Mitigation | What reduces medium/high risk before implementation? |
| Fallback path | Manual path, alternate provider, reduced scope, or no-go. |
| Revisit trigger | What event or evidence should reopen this assessment? |

Medium or high risk without mitigation is a blocker for architecture or implementation tickets.

## PRD Integration

In `product/prd.md`, include API dependency risk when:

- the user-facing value depends on a public API or model provider
- the product needs an external platform, marketplace, app store, or enterprise system
- a provider's native feature could substitute the product
- cost, rate limits, policy, or model behavior may affect the MVP promise

If not applicable, state why the MVP does not materially depend on external APIs.

## Architecture Integration

In `architecture/architecture-review.md`, use this assessment to:

- keep non-essential integrations deferred
- require fallback paths for medium/high risk dependencies
- prevent provider abstraction work before it is needed
- define the smallest architecture that validates the riskiest assumption
- flag high substitution risk before implementation tickets proceed

## Synthetic Application Checks

### LLM Wrapper

| Check | Example answer |
|---|---|
| Dependency | Single LLM provider for core output. |
| Risk | High if the product is only prompt + UI. |
| Substitution risk | High because model provider could ship the feature directly. |
| Mitigation | Must add workflow depth, proprietary data, trust/auditability, distribution, or vertical context. |
| Fallback | Manual expert workflow or narrower validation before product build. |
| Decision | Do not build as generic wrapper without sourced mitigation. |

### Vertical SaaS With Proprietary Data

| Check | Example answer |
|---|---|
| Dependency | LLM API supports summarization or classification. |
| Risk | Medium if the workflow can degrade gracefully or use manual review. |
| Substitution risk | Lower when proprietary workflow data, approvals, and user context matter. |
| Mitigation | Link to Data Moat strategy; keep manual review and provider fallback. |
| Fallback | Operator-assisted workflow for early validation. |
| Decision | API leverage acceptable if customer workflow and learning loop are validated. |

### Enterprise Integration Product

| Check | Example answer |
|---|---|
| Dependency | CRM, ERP, messaging, or identity APIs. |
| Risk | Medium or high depending on permissions, platform policy, and customer procurement. |
| Substitution risk | Medium if platform can add feature; lower if cross-system workflow matters. |
| Mitigation | Integration moat, auditability, compliance controls, and manual export/import fallback. |
| Fallback | CSV/manual workflow or limited pilot with one approved integration. |
| Decision | Do not build broad integration set until one workflow proves value. |

## Anti-Patterns

- Treating API access as defensibility.
- Creating provider abstraction before risk justifies it.
- Blocking useful APIs because of abstract platform fear.
- Building broad integrations before a single workflow is validated.
- Assuming model quality, pricing, or policy will stay stable.
- Claiming proprietary data moat without source artifacts.
- Ignoring manual fallback when it would validate faster.

## Handoff Checklist

When a ticket touches API dependency risk, record:

- External dependency:
- Dependency role:
- Risk level:
- Substitution risk:
- Provider-change risk:
- Mitigation:
- Fallback path:
- Revisit trigger:
- Follow-up ticket needed: yes/no
