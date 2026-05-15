# Technical Decision Guide

Use the smallest artifact that preserves future understanding.

| Situation | Artifact |
|---|---|
| MVP scope needs technical shape | `architecture/architecture-review.md` |
| Proposal needs review before implementation | `architecture/rfc-template.md` |
| Accepted structural decision needs durable rationale | `architecture/adr/adr-template.md` |
| Strategic product or governance decision needs durable rationale | `knowledge/kdr-dar-template.md` |
| Routine implementation choice inside one ticket | PR description and Linear handoff |

## ADR Needed

Create an ADR when the decision:

- changes architecture boundaries
- selects a durable data model, integration, hosting, or security posture
- accepts a meaningful technical tradeoff
- constrains future implementation tickets
- supersedes a prior ADR or architecture review decision

## RFC Needed

Create an RFC when:

- there are multiple plausible technical approaches
- the decision affects more than one ticket
- risk or reversibility is unclear
- human review is needed before implementation

## No Extra Artifact Needed

Do not create ADRs or RFCs for:

- typo, formatting, or copy edits
- small local refactors inside one PR
- routine dependency or template updates
- implementation details already obvious from a narrow PR
- documentation updates that do not change future technical execution
