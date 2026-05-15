# Core Venture Pipeline Map

This map defines the required sequence from raw idea intake to first product trial. It prevents implementation, billing, growth, or autonomous outreach from moving ahead of validation.

## Pipeline Rule

Do not create implementation tickets until:

- the idea has passed intake and founder focus
- C.O.N.T.R.O.L.E. has produced an explicit verdict
- research and validation work has defined what must be learned
- Working Backwards, PRD, MVP scope, anti-goals, and risk review exist
- the Linear project has been confirmed or approved for creation

If a required artifact does not exist yet, execute the setup or validation ticket that creates it.

## Phase Map

| Phase | Input | Output | Owner | Approval requirement | Linear impact | Next step |
|---|---|---|---|---|---|---|
| 1. Idea intake | Raw idea, founder notes, observed problem | Initial idea record with target, problem, promise, assumptions, and unknowns | Founder or idea intake agent | Approval required only before external action or ticket creation | No implementation tickets; create only an approved setup or intake ticket if needed | Founder focus |
| 2. Founder focus | Idea intake record | Narrow founder focus: market, problem, offer, channel, constraints, anti-sprawl notes | Founder or product strategist | Human review before expanding scope | Linear may track setup/strategy tickets only | C.O.N.T.R.O.L.E. evaluation |
| 3. C.O.N.T.R.O.L.E. evaluation | Founder focus artifact and assumptions | `product/controle-evaluation.md` with Attack, Refine, Pivot, or Kill verdict, rationale, MVP implication, validation implication, and next action | Product strategist or validation agent | Human approval required before advancing on Attack or Refine | Linear may track validation tickets after verdict; no build tickets yet | Research and validation plan |
| 4. Research and validation plan | C.O.N.T.R.O.L.E. verdict and unknowns | Research questions, discovery plan, experiment plan, source needs, confidence gaps | Researcher or validation lead | Approval required before customer outreach or external communications | Create validation/research tickets only after project confirmation or approval | Working Backwards |
| 5. Working Backwards | Validated problem framing and intended customer outcome | Press release, FAQ, promise, constraints, launch narrative, non-goals | Product strategist | Human review before treating claims as accepted | Linear may track product definition tickets | PRD |
| 6. PRD | Working Backwards artifact and validation plan | Product requirements, user journeys, functional scope, constraints, assumptions, evidence links | Product strategist or PM agent | Human review before implementation ticket creation | Linear may track PRD completion and review | MVP scope review |
| 7. MVP scope review | PRD, anti-goals, validation evidence, constraints | Explicit MVP scope, excluded scope, release boundary, success criteria | Founder and product strategist | Human approval required before creating build tickets | Implementation tickets remain blocked until this phase is accepted | Risk review |
| 8. Risk review | MVP scope, architecture notes, sensitive claims, data/billing/outreach needs | Risk register, required mitigations, approval blockers, follow-up tickets | Risk reviewer | Approval required for any gated action listed in `execution/approval-gates.md` | Create follow-ups for risks; unblock build tickets only when P0/P1 risks are handled or accepted | Architecture |
| 9. Architecture | MVP scope and risk review | Minimum viable technical shape, standards, constraints, ADRs as needed | Architecture agent or engineer | Human review before production-impacting architecture changes | Linear may track architecture tickets and blockers | Linear project confirmation |
| 10. Linear project confirmation | Approved product scope and execution plan | Confirmed Linear project, milestones, labels, and execution backlog boundary | Linear project orchestrator | Human approval required before creating or changing Linear projects/tickets | Confirm one source-of-truth project before implementation tickets | Ticket creation |
| 11. Ticket creation | Approved MVP scope, risk review, architecture, Linear project | Small, sequenced Linear tickets with acceptance criteria and dependencies | Roadmap orchestrator | Human approval required before creating tickets | Tickets become the execution source of truth | Ticket execution |
| 12. Ticket execution | One approved Linear ticket | One scoped branch, one PR, validations, review, merge, Linear update | Assigned execution agent | Approval required before opening and merging PRs | Ticket moves through In Progress, review notes, Done after merge | Feedback and learning |
| 13. First product trial | Merged MVP scope and validation plan | Trial-ready artifact, trial instructions, known risks, measurement plan | Founder, validation lead, execution agent | Approval required before outreach, external communication, billing, ads, or production deployment | Linear tracks trial tasks and blockers | Feedback loop |
| 14. Feedback and learning | Trial observations, validation results, support notes, metrics with sources | Learning cards, decision log updates, GO/NO-GO recommendation, follow-up tickets | Validation lead or knowledge steward | Human review before changing strategy or claims | Linear receives follow-ups, blockers, pivots, or next-cycle tickets | Next iteration or stop |

## Gates That Block Implementation

Implementation tickets are blocked until these are true:

- C.O.N.T.R.O.L.E. verdict is Attack or Refine with human approval.
- `product/controle-evaluation.md` distinguishes evidence from assumptions and records rationale.
- The validation plan identifies what the MVP must prove.
- PRD and MVP scope define included and excluded work.
- Risk review does not contain unresolved P0/P1 blockers.
- Linear project is confirmed.
- The implementation ticket is approved and scoped.

## Linear Impact Rules

- Linear stores execution state, priority, blockers, milestones, and handoff.
- Repository artifacts store strategy, evidence, decisions, and reusable templates.
- Linear tickets must reference the repository artifact they implement or update.
- Build tickets must not be created before validation and MVP scope are accepted.
- Follow-up tickets must be specific, contextual, and tied to the originating ticket or PR.

## Approval Summary

Human approval is required before:

- creating Linear projects or tickets
- opening or merging PRs
- production deployment
- billing, paid ads, or paid acquisition
- customer outreach or external communication
- handling secrets or production/customer data
- changing sensitive legal, financial, compliance, privacy, security, or evidence claims

For full policy, see `execution/approval-gates.md`.

## Out Of Scope For This Map

This map does not define:

- specialized agent marketplace behavior
- automated growth or distribution systems
- advanced intelligence or synthetic persona workflows
- billing implementation
- production deployment automation

Those areas require later tickets after the foundation and validation gates exist.
