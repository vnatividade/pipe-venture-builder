# Core Venture Pipeline Map

This map defines the required sequence from raw idea intake to first product trial. It prevents implementation, billing, growth, or autonomous outreach from moving ahead of validation.

## Pipeline Rule

Do not create implementation tickets until:

- the idea has passed intake and founder focus
- the solution path has been confirmed when the idea could proceed as market-facing, own-pain, or specific-person work
- C.O.N.T.R.O.L.E. has produced an explicit verdict
- research and validation work has defined what must be learned
- Working Backwards, PRD, MVP scope, anti-goals, and risk review exist
- a Tactical Execution Plan exists or is explicitly marked not applicable for the work
- the Linear project has been confirmed or approved for creation

If a required artifact does not exist yet, execute the setup or validation ticket that creates it.

## Phase Map

| Phase | Input | Output | Owner | Approval requirement | Linear impact | Next step |
|---|---|---|---|---|---|---|
| 1. Idea intake | Raw idea, founder notes, observed problem | Initial idea record with selected solution path, target, problem, promise, assumptions, and unknowns | Founder or idea intake agent | Approval required only before external action or ticket creation | No implementation tickets; create only an approved setup or intake ticket if needed | Founder focus |
| 2. Founder focus | Idea intake record | `product/founder-focus.md` with one market, one problem, one offer, one channel, one-year focus, anti-goals, and expansion constraints | Founder or product strategist | Human review when target, problem, offer, or channel is ambiguous | Linear may track setup/strategy tickets only | C.O.N.T.R.O.L.E. evaluation |
| 3. C.O.N.T.R.O.L.E. evaluation | Founder focus artifact and assumptions | `product/controle-evaluation.md` with Attack, Refine, Pivot, or Kill verdict, rationale, MVP implication, validation implication, and next action | Product strategist or validation agent | Human approval required before advancing on Attack or Refine | Linear may track validation tickets after verdict; no build tickets yet | Research and validation plan |
| 4. Research and validation plan | C.O.N.T.R.O.L.E. verdict and unknowns | Research questions, discovery plan, `validation/validation-scorecard.md`, experiment plan, source needs, confidence gaps | Researcher or validation lead | Approval required before customer outreach or external communications | Create validation/research tickets only after project confirmation or approval | Working Backwards |
| 5. Working Backwards | Validated problem framing and intended customer outcome | Press release, FAQ, promise, constraints, launch narrative, non-goals | Product strategist | Human review before treating claims as accepted | Linear may track product definition tickets | PRD |
| 6. PRD | Working Backwards artifact and validation plan | Product requirements, user journeys, functional scope, constraints, assumptions, evidence links | Product strategist or PM agent | Human review before implementation ticket creation | Linear may track PRD completion and review | MVP scope review |
| 7. MVP scope review | PRD, anti-goals, validation evidence, constraints | `product/mvp-scope.md` with core loop, riskiest assumption, smallest ethical test, explicit cuts, evidence threshold, and GO/NO-GO condition | Founder and product strategist | Human approval required before creating architecture or implementation tickets | Implementation tickets remain blocked until this phase is accepted | Risk review |
| 8. Risk review | MVP scope, architecture notes, sensitive claims, data/billing/outreach needs | Risk register, required mitigations, approval blockers, follow-up tickets | Risk reviewer | Approval required for any gated action listed in `execution/approval-gates.md` | Create follow-ups for risks; unblock build tickets only when P0/P1 risks are handled or accepted | Architecture |
| 9. Architecture | MVP scope and risk review | Minimum viable technical shape, standards, constraints, ADRs as needed | Architecture agent or engineer | Human review before production-impacting architecture changes | Linear may track architecture tickets and blockers | Linear project confirmation |
| 10. Linear project confirmation | Approved product scope and execution plan | Confirmed Linear project, milestones, labels, and execution backlog boundary | Linear project orchestrator | Human approval required before creating or changing Linear projects/tickets | Confirm one source-of-truth project before implementation tickets | Ticket creation |
| 11. Ticket creation | Approved MVP scope, risk review, architecture, Linear project, Tactical Execution Plan when required | Small, sequenced Linear tickets or stories with acceptance criteria, dependencies, validation plan, ADR needs, docs, and evidence expectations | Roadmap orchestrator | Human approval required before creating tickets | Tickets become the execution source of truth | Ticket execution |
| 12. Ticket execution | One approved Linear ticket and linked Tactical Execution Plan or not-applicable reason | One scoped branch, one PR, validations, review, merge, Linear update | Assigned execution agent | Approval required before opening and merging PRs | Ticket moves through In Progress, review notes, Done after merge | Feedback and learning |
| 13. First product trial | Merged MVP scope and validation plan | Trial-ready artifact, trial instructions, known risks, measurement plan | Founder, validation lead, execution agent | Approval required before outreach, external communication, billing, ads, or production deployment | Linear tracks trial tasks and blockers | Feedback loop |
| 14. Feedback and learning | Trial observations, validation results, support notes, metrics with sources | Learning cards, decision log updates, GO/NO-GO recommendation, follow-up tickets | Validation lead or knowledge steward | Human review before changing strategy or claims | Linear receives follow-ups, blockers, pivots, or next-cycle tickets | Next iteration or stop |

## Stage Exit Criteria

These stage exits translate the detailed phase map into the four operating stages agents should use when deciding whether a venture can advance. They are additive to the existing gates. They do not replace C.O.N.T.R.O.L.E., validation scorecard, Market Validation Before Code, MVP scope, risk review, approval gates, Linear, or GitHub.

Agents must not treat a completed document as evidence by itself. A stage can advance only when the required artifacts distinguish sourced evidence, assumptions, unknowns, and approval state.

### Idea Stage

**Goal:** Decide whether a raw idea is focused and strategically coherent enough to enter structured validation.

**Required artifacts:**

- `product/product-context.md` or equivalent idea intake record
- `product/solution-path-decision.md` or equivalent solution-path section when the path changes discovery or evidence requirements
- `product/founder-focus.md`
- `product/controle-evaluation.md`

**Exit criteria:**

- One target market, one initial persona or segment, one primary problem, one promised result, and one first channel hypothesis are explicit.
- The solution path is confirmed as market-facing, own-pain, or specific-person when the idea could follow more than one route.
- Assumptions, known evidence, and unknowns are separated.
- C.O.N.T.R.O.L.E. has an Attack or Refine verdict with rationale and human approval before advancing.
- Pivot or Kill decisions record the rationale and stop downstream PRD, build, growth, monetization, and launch work.

**Allowed next actions:**

- Create or execute research, validation, focus, or evidence-gathering tickets.
- Draft validation questions and research plans.

**Forbidden premature actions:**

- PRD, architecture, implementation, growth, monetization, billing, or customer-facing claims.
- Treating synthetic output, founder excitement, or market-size research as customer validation.

### MVP Stage

**Goal:** Decide whether a validated problem and focused scope justify a smallest ethical test.

**Required artifacts:**

- `validation/validation-scorecard.md`
- `validation/market-validation-before-code-gate.md`
- `validation/icp-profile.md`
- `product/prd.md`, when product definition is ready
- `product/mvp-scope.md`
- risk review notes when data, claims, billing, outreach, privacy, security, or production exposure appears

**Exit criteria:**

- Market Validation Before Code is GO or explicitly approved CONDITIONAL GO.
- The PMF triad is answerable: what to sell, to whom, and how to reach them.
- The MVP core loop, riskiest assumption, smallest ethical test, evidence threshold, and explicit cuts are recorded.
- Critical evidence categories are not based only on internal reasoning or synthetic personas.
- P0/P1 risks are resolved, mitigated, or explicitly accepted before implementation tickets.

**Allowed next actions:**

- Create scoped architecture or implementation tickets tied to the validated MVP loop.
- Run approved manual, concierge, fake-door, prototype, or first-use tests that respect approval gates.

**Forbidden premature actions:**

- Broad platform buildout, scalability work, advanced automation, billing, growth automation, or production deployment unless they are the approved riskiest assumption to test.
- Expanding scope because agentic coding makes implementation easy.

### Launch Stage

**Goal:** Decide whether the MVP has enough evidence, operational readiness, and measurement to be exposed beyond the first controlled test.

**Required artifacts:**

- accepted MVP scope and merged implementation evidence, when software exists
- validation or trial learning artifacts
- launch readiness checklist, when available
- distribution or channel experiment artifact, when launch depends on a channel
- pricing hypothesis artifact, when willingness to pay or paid pilot is part of the test
- security, privacy, data, claims, and support readiness notes

**Exit criteria:**

- The target user, promise, offer, first channel, proof, onboarding path, support path, and learning loop are explicit.
- Measurement exists for the learning goal, such as activation, core-result completion, repeated use, qualified reply, willingness to continue, willingness to pay, referral, or objection resolution.
- Security, privacy, data handling, customer-facing claims, external communication, and billing implications are reviewed before user exposure.
- Launch scope is narrow enough to learn; one early positive signal is not treated as product-market fit.

**Allowed next actions:**

- Run an approved launch, trial, channel experiment, or manual sales test inside the stated scope.
- Update learning records, validation scorecards, MVP scope, and backlog based on sourced results.

**Forbidden premature actions:**

- Multi-channel growth, paid acquisition, autonomous outreach, unsupported claims, billing infrastructure, or broad public launch without explicit approval and evidence.
- Declaring PMF from compliments, unqualified waitlists, one-off usage, or internal interpretation.

### Scale Stage

**Goal:** Decide whether repeated evidence and operational maturity justify increasing reach, automation, reliability requirements, or organizational complexity.

**Required artifacts:**

- post-launch learning loop or equivalent sourced results
- repeated usage, retention, revenue, referral, reference, paid commitment, operational load, or support evidence, as applicable
- updated risk review and architecture notes
- knowledge updates for reusable decisions, customer language, and failure patterns

**Exit criteria:**

- There is repeated evidence that the venture creates value for a specific ICP and can be reached through a repeatable channel.
- Unit economics, willingness to pay, retention, or repeat engagement are understood enough for the next scale step.
- Operational bottlenecks, support needs, reliability expectations, security/privacy posture, and founder-only decisions are visible.
- Proprietary learning, customer language, workflow depth, or data advantage is being captured in canonical repository or approved execution artifacts.

**Allowed next actions:**

- Create scoped tickets for reliability, observability, support playbooks, growth experiments, integrations, or automation only when evidence supports them.
- Promote reusable learning into `knowledge/` or architecture artifacts through ticket, PR, and review.

**Forbidden premature actions:**

- Building an autonomous operating layer, scheduled agents, broad MCP/integration surface, enterprise compliance program, or OpenClaw-style orchestration before Codex and Claude Code have produced comparable delivery evidence and handoff quality.
- Scaling a channel, product, or automation path that has not shown repeatability.

## Gates That Block Implementation

Implementation tickets are blocked until these are true:

- C.O.N.T.R.O.L.E. verdict is Attack or Refine with human approval.
- `product/controle-evaluation.md` distinguishes evidence from assumptions and records rationale.
- The validation plan identifies what the MVP must prove.
- `validation/validation-scorecard.md` meets GO or approved CONDITIONAL GO thresholds.
- PRD and MVP scope define included and excluded work.
- `product/mvp-scope.md` defines the core loop, cut list, evidence threshold, and GO/NO-GO condition.
- Risk review does not contain unresolved P0/P1 blockers.
- Linear project is confirmed.
- `execution/tactical-execution-plan.md` exists, is embedded in the ticket, or is explicitly marked not applicable with a reason.
- The implementation ticket is approved and scoped.
- The selected solution path does not contradict the evidence standard used to justify build work.

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
