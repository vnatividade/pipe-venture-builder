# Architecture Review Template

Use this template after the lean PRD and MVP scope gate exist.

Architecture should support the smallest ethical MVP test. It must not propose production-grade scale, platform architecture, broad integrations, or complex automation before validation shows those constraints are real.

## Required Inputs

- Product or idea name:
- Date:
- Reviewer:
- Lean PRD:
- Data moat strategy, if applicable:
- MVP scope gate:
- MVP decision: GO / approved CONDITIONAL GO
- MVP core loop:
- Riskiest assumption:
- Evidence threshold:
- Risk review:
- Human approval before implementation tickets:
- Approval record or blocker:

Do not continue if the PRD is missing, the MVP decision is NO-GO, or the MVP core loop is unclear.

## MVP Assumptions To Preserve

Architecture must preserve the MVP assumptions rather than silently expanding them.

| MVP assumption | Source artifact | Architecture implication | Validation risk if wrong |
|---|---|---|---|
|  | product/mvp-scope.md / product/prd.md / validation artifact |  |  |

## Constraints

| Constraint | Source | Impact on architecture | Can defer? |
|---|---|---|---|
| Time or solo-founder capacity |  |  | yes/no |
| Data or privacy boundary |  |  | yes/no |
| Manual workflow boundary |  |  | yes/no |
| Integration boundary |  |  | yes/no |
| Cost or operational limit |  |  | yes/no |
| Approval gate |  |  | yes/no |

## Recommended System Shape

Describe the smallest technical shape that can validate the MVP core loop.

- Primary user entry point:
- Core workflow:
- Manual steps retained:
- Automated steps required:
- Data captured:
- Data avoided:
- Internal operator view needed:
- External integration needed:
- Hosting or runtime assumption:
- Observability needed for the test:

## Data Boundary

| Data | Source | Stored where | Retention expectation | Sensitive? | Approval needed? |
|---|---|---|---|---|---|
|  |  |  |  | yes/no | yes/no |

Do not include secrets, credentials, private keys, production data, or customer data unless explicit approval and storage rules exist.

If the PRD includes a Data Moat Hypothesis, verify it against `architecture/proprietary-data-moat-strategy.md`.

| Data moat field | Architecture decision | Risk or blocker |
|---|---|---|
| Allowed capture |  |  |
| Data explicitly avoided |  |  |
| Learning loop support |  |  |
| Promotion criteria |  |  |
| Retention expectation |  |  |
| Privacy or trust risk |  |  |
| Mitigation |  |  |

Sensitive or prohibited data categories remain blockers unless an explicit approval record and storage boundary exist.

## Integration Boundary

| Integration | Needed for MVP test? | Why | Alternative manual path | Risk |
|---|---|---|---|---|
|  | yes/no |  |  |  |

If an integration is not needed to test the riskiest assumption, defer it.

## Failure Modes And Edge Cases

Use edge cases from `product/prd.md` and add technical failure modes.

| Failure mode or edge case | User impact | Detection | Mitigation | Blocks MVP? |
|---|---|---|---|---|
| Empty state |  |  |  | yes/no |
| Loading or waiting |  |  |  | yes/no |
| Error or failed path |  |  |  | yes/no |
| Manual review needed |  |  |  | yes/no |
| Privacy or data boundary breached |  |  |  | yes/no |
|  |  |  |  |  |

## Risks

Use `execution/risk-reviewer-matrix-lite.md` for material risks.

| Risk | Category | Severity | Mitigation | Owner | Status |
|---|---|---|---|---|---|
|  | Product / Technical / Legal / Financial / Privacy / Security / Operational | P0 / P1 / P2 / P3 |  |  | Open / Mitigated / Accepted / Blocked |

P0 and P1 risks must be mitigated or remain blocking before implementation tickets proceed. Any proposed risk acceptance requires explicit human approval and does not override unresolved P0/P1 review findings.

## Not Needed Yet

Explicitly defer complexity that is not required for the MVP test.

| Deferred complexity | Why not needed yet | Revisit trigger |
|---|---|---|
| Production-grade scale | Validation must prove repeated use first | Core loop threshold is met repeatedly |
| Multi-tenant platform foundation | First MVP should prove one ICP and one core loop | Multiple validated customer segments require it |
| Advanced automation | Manual path can validate the riskiest assumption faster | Manual process becomes validated bottleneck |
| Broad integration set | Integrations should follow validated workflow need | Repeated user demand or risk requires it |
| Billing infrastructure | Excluded unless payment is the riskiest assumption | Willingness-to-pay test requires payment collection |
| Growth automation | Premature before retention or willingness signal | Manual channel shows repeatable signal |
|  |  |  |

## Architecture Recommendation

- Recommended approach:
- Why this is sufficient for the MVP:
- What this intentionally does not solve:
- Main technical tradeoff:
- Main operational tradeoff:
- Reversibility: Reversible / Hard to reverse / Irreversible
- ADR needed: yes/no
- Risk reviewer needed before tickets: yes/no

## Implementation Ticket Boundary

Implementation tickets may be proposed only when:

- lean PRD is linked
- MVP core loop and riskiest assumption are linked
- architecture supports the MVP test without expanding scope
- data, integration, and failure-mode boundaries are explicit
- deferred complexity is listed
- P0/P1 risks are mitigated or blocking
- human approval before implementation tickets is recorded

## Handoff

- Implementation ticket candidates:
- Required validations:
- Required observability:
- Manual operations notes:
- Follow-up architecture questions:
- KDR/DAR update needed:
- Decision conflict scan needed:
- Known residual risks:
