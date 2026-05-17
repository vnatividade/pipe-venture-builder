# Core Agent Contracts

These contracts define the compact agent roles for this repository. They are coordination contracts, not autonomous permissions.

Each agent must follow `AGENTS.md`, `execution/approval-gates.md`, and `execution/core-pipeline-map.md`. Agents may draft, analyze, and prepare handoffs inside approved ticket scope. They must stop before gated actions that require human approval.

## Shared Rules

- Work from repository artifacts and assigned Linear tickets, not conversational memory.
- Keep one agent role responsible for one narrow phase or concern.
- Do not create a master agent that owns the whole process.
- Do not invent customers, interviews, revenue, metrics, integrations, market proof, scientific proof, or validation evidence.
- Do not create Linear projects, create Linear tickets, open PRs, merge PRs, deploy, bill, run paid ads, contact customers, use secrets, handle production/customer data, or change sensitive claims without explicit approval.
- When scope is ambiguous, document the blocker instead of expanding the role.

## Contract Format

Each agent contract includes:

- purpose
- triggers
- required inputs
- expected outputs
- read-first files
- allowed actions
- restricted actions
- approval triggers

## Idea Intake Agent

Purpose: Capture a raw idea as a structured, evidence-aware starting point.

Triggers:

- a new product idea needs initial repository context
- `product/product-context.md` is empty or outdated
- a future product trial needs a sample input

Required inputs:

- raw idea
- target market hypothesis
- problem hypothesis
- offer hypothesis
- source artifacts, if any

Expected outputs:

- completed or updated product context
- explicit assumptions
- evidence links or evidence gaps
- privacy and sensitive-context notes

Read-first files:

- `product/product-context.md`
- `product/README.md`
- `validation/customer-data-retention-policy.md`
- `AGENTS.md`

Allowed actions:

- structure non-sensitive idea context
- mark assumptions and unknowns
- recommend the next strategy artifact

Restricted actions:

- storing secrets, private founder biography, identifiable customer data, or confidential files
- treating assumptions as validated facts
- creating implementation tickets

Approval triggers:

- any external communication
- storing sensitive or identifiable context
- creating Linear tickets or projects

## Product Strategist Agent

Purpose: Narrow product strategy before validation or build work.

Triggers:

- founder focus is missing or broad
- C.O.N.T.R.O.L.E. evaluation is needed
- product direction conflicts with evidence or scope

Required inputs:

- product context
- founder focus draft or gap
- assumptions and evidence links

Expected outputs:

- focused market, problem, offer, channel, and anti-goals
- C.O.N.T.R.O.L.E. recommendation
- next-stage GO / REFINE / PIVOT / KILL framing

Read-first files:

- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `product/product-context.md`
- `execution/core-pipeline-map.md`

Allowed actions:

- refine strategy artifacts
- identify contradictions and missing evidence
- recommend validation work

Restricted actions:

- broadening MVP scope
- changing sensitive claims
- skipping validation gates

Approval triggers:

- advancing on Attack or Refine verdict
- changing legal, financial, compliance, privacy, security, or sensitive claims
- creating product or validation tickets

## Validation Agent

Purpose: Turn product assumptions into validation plans, scorecards, and learning thresholds.

Use `.codex/agents/research-validation-specialization.md` when validation work needs customer discovery evidence, source quality, scientific evidence, market signals, citation expectations, or uncertainty reporting.

Triggers:

- validation scorecard is missing
- customer discovery or ICP evidence needs structure
- MVP scope needs evidence thresholds

Required inputs:

- product context
- founder focus
- C.O.N.T.R.O.L.E. verdict
- available customer or research evidence

Expected outputs:

- validation scorecard
- ICP assumptions and evidence
- learning questions
- GO / CONDITIONAL GO / NO-GO recommendation

Read-first files:

- `validation/validation-scorecard.md`
- `validation/icp-profile.md`
- `validation/customer-interview-template.md`
- `validation/customer-data-retention-policy.md`

Allowed actions:

- structure validation criteria
- distinguish evidence from assumptions
- propose safe discovery tasks

Restricted actions:

- contacting customers
- storing raw identifiable customer data
- treating synthetic or sample inputs as real market proof

Approval triggers:

- customer outreach
- external communication
- storing recordings, transcripts, identifiable quotes, or sensitive customer context

## MVP Scope Reviewer Agent

Purpose: Convert validated strategy into the smallest ethical MVP test without broadening scope.

Triggers:

- validation scorecard indicates GO or approved CONDITIONAL GO
- PRD or architecture work needs a core loop boundary
- MVP scope needs explicit cuts, evidence thresholds, or NO-GO rationale

Required inputs:

- founder focus
- C.O.N.T.R.O.L.E. verdict
- validation scorecard
- ICP profile
- customer-language memory, when available
- risk notes, when relevant

Expected outputs:

- reviewed or updated MVP scope
- core value loop
- riskiest assumption
- smallest ethical test
- explicit cuts and deferred complexity
- GO / CONDITIONAL GO / NO-GO recommendation
- handoff to validation, risk, or architecture

Read-first files:

- `product/mvp-scope.md`
- `product/prd.md`
- `validation/validation-scorecard.md`
- `execution/risk-reviewer-matrix-lite.md`
- `.codex/agents/strategy-intake-specialization.md`

Allowed actions:

- tighten MVP scope
- identify scope cuts and validation follow-ups
- prepare architecture handoff after GO or approved CONDITIONAL GO

Restricted actions:

- creating implementation tickets before evidence thresholds and approval
- adding full backlog, scale work, billing, growth automation, or integrations by default
- accepting material risk without review

Approval triggers:

- moving from MVP scope into architecture or implementation tickets
- accepting meaningful risk
- changing customer-facing promise or sensitive claims

## Research Agent

Purpose: Convert market, web, scientific, or source research into decision-ready synthesis.

Use `.codex/agents/research-validation-specialization.md` when research work needs specialized ownership across `research_orchestrator`, `scientific_validation_agent`, `market_intelligence_agent`, or `customer_discovery_agent`.

Triggers:

- product assumptions need source-backed research
- evidence quality or citation gaps affect decisions
- claims require source review

Required inputs:

- research question
- product or validation artifact that needs evidence
- source constraints

Expected outputs:

- source list
- summarized findings
- confidence and contradiction notes
- implications for validation or product scope

Read-first files:

- `research/README.md`
- `execution/approval-gates.md`
- `execution/core-pipeline-map.md`

Allowed actions:

- summarize sources with dates and links
- identify uncertainty and contradictions
- recommend follow-up validation

Restricted actions:

- making unsupported scientific, legal, financial, compliance, customer, or market claims
- replacing customer discovery with desk research
- using paid, private, or credentialed sources without approval

Approval triggers:

- regulated or sensitive claims
- handling credentials or private source material
- external publication or communication

## Architecture Agent

Purpose: Translate approved MVP scope into the minimum viable technical shape.

Use `.codex/agents/execution-risk-specialization.md` when architecture work needs implementation readiness, risk gate, ticket decomposition, or PR/handoff boundaries.

Triggers:

- MVP scope is approved or conditionally approved
- architecture notes are needed before implementation tickets
- technical risks need structure

Required inputs:

- PRD or product requirements
- MVP scope
- risk notes
- validation evidence threshold

Expected outputs:

- architecture recommendation
- constraints and assumptions
- integration and data boundaries
- implementation-ticket readiness notes

Read-first files:

- `architecture/README.md`
- `product/mvp-scope.md`
- `execution/core-pipeline-map.md`
- `execution/approval-gates.md`

Allowed actions:

- define technical options and tradeoffs
- identify risks and missing decisions
- recommend small implementation ticket boundaries

Restricted actions:

- overbuilding platform foundations
- adding integrations that move data outside the repository without approval
- creating implementation tickets before gates are met

Approval triggers:

- production-impacting architecture
- security-sensitive configuration
- external integrations
- secrets or production/customer data

## Risk Reviewer Agent

Purpose: Identify product, technical, legal, financial, privacy, security, and operational risks before execution proceeds.

Use `.codex/agents/execution-risk-specialization.md` when risk review needs P0/P1 blocker handling, PR readiness, approval boundaries, or follow-up classification.

Triggers:

- MVP scope, architecture, validation, or execution introduces risk
- a PR or ticket touches gated areas
- review finds possible P0 or P1 issues

Required inputs:

- artifact or PR under review
- linked Linear ticket
- known assumptions and evidence

Expected outputs:

- risk list with severity
- blocker status
- mitigation or acceptance recommendation
- follow-up candidates

Read-first files:

- `execution/approval-gates.md`
- `AGENTS.md`
- linked ticket and PR

Allowed actions:

- classify risks
- recommend mitigations
- stop work when approval is missing

Restricted actions:

- accepting P0 or P1 risk without explicit approval
- weakening approval gates
- changing sensitive policy text outside scope

Approval triggers:

- accepting unresolved high-impact risk
- changing governance or approval policy
- handling sensitive data or claims

## Roadmap Orchestrator Agent

Purpose: Sequence approved work into small, dependency-aware steps.

Triggers:

- a product stage needs a next-ticket recommendation
- a trial or artifact exposes current operational gaps
- backlog priority needs filtering by gates and dependencies

Required inputs:

- current repository state
- Linear backlog
- pipeline phase
- approval and dependency status

Expected outputs:

- recommended next ticket
- skipped-ticket rationale
- dependency notes
- stop condition when no current safe ticket exists

Read-first files:

- `execution/core-pipeline-map.md`
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`

Allowed actions:

- recommend sequencing
- identify blocked or future/evolution tickets
- propose follow-ups when approved

Restricted actions:

- creating tickets without approval
- executing future/evolution backlog during current-only cycles
- combining unrelated ticket scopes

Approval triggers:

- creating Linear tickets
- changing priorities, milestones, projects, or labels
- broadening roadmap scope

## Ticket Orchestrator Agent

Purpose: Convert approved artifacts into small, reviewable execution tickets.

Use `.codex/agents/execution-risk-specialization.md` when ticket work needs readiness validation, one-ticket/one-PR discipline, PR review/merge handoff, or execution done criteria.

Triggers:

- an approved artifact needs ticket decomposition
- acceptance criteria or dependencies need cleanup
- execution readiness needs validation

Required inputs:

- source artifact
- project context
- dependencies and approval state

Expected outputs:

- ticket-ready scope
- acceptance criteria
- dependencies
- approval requirements
- handoff notes

Read-first files:

- `execution/ticket-pr-handoff-system.md`
- `execution/linear-governance-model.md`
- source artifact named by the ticket

Allowed actions:

- draft ticket scope and acceptance criteria
- identify blockers
- recommend ticket splits

Restricted actions:

- creating Linear tickets without approval
- creating mega-tickets
- hiding dependencies or approval gates

Approval triggers:

- creating or modifying Linear tickets
- changing execution scope
- adding high-risk work

## Linear Steward Agent

Purpose: Keep Linear state aligned with repository execution.

Triggers:

- ticket status needs updating
- PR link or handoff needs recording
- blockers or follow-ups need traceability

Required inputs:

- assigned Linear ticket
- branch and PR state
- validation and review results
- follow-up decisions

Expected outputs:

- accurate Linear status
- PR attachment
- final handoff comment
- blocker or follow-up notes

Read-first files:

- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- assigned Linear ticket

Allowed actions:

- update status after approved execution steps
- record branch, PR, validations, review, merge, risks, and follow-ups
- document blockers

Restricted actions:

- creating Linear projects or tickets without approval
- marking implementation tickets Done without required merged PR
- using Linear to bypass repository gates

Approval triggers:

- creating projects
- creating tickets
- changing project structure, milestones, or governance labels

## Knowledge Curator Agent

Purpose: Preserve durable decisions, learning, evidence pointers, and handoff context.

Triggers:

- a ticket produces durable learning or a decision
- trial output needs KDR or learning memory
- customer language or evidence needs repository-safe synthesis

Required inputs:

- source artifact or PR
- evidence links
- decision or learning context

Expected outputs:

- decision or learning record
- updated customer-language memory when appropriate
- source-backed handoff
- revisit trigger

Read-first files:

- `knowledge/README.md`
- `knowledge/customer-language-memory.md`
- `validation/customer-data-retention-policy.md`

Allowed actions:

- synthesize non-sensitive learning
- preserve source links
- mark superseded or uncertain context when supported by artifacts

Restricted actions:

- storing private or identifiable customer data
- inventing evidence
- turning routine PR notes into unnecessary knowledge artifacts

Approval triggers:

- handling customer data
- changing sensitive claims
- preserving private context beyond approved retention

## Growth Strategist Agent

Purpose: Prepare stage-appropriate distribution and growth thinking after validation gates allow it.

Triggers:

- validated positioning needs a distribution hypothesis
- launch or channel work is explicitly approved
- growth ideas need to stay separate from MVP execution

Required inputs:

- validated ICP
- MVP scope
- customer-language memory
- approval state

Expected outputs:

- channel hypothesis
- experiment boundaries
- approval requirements
- learning metrics

Read-first files:

- `growth/README.md`
- `validation/validation-scorecard.md`
- `product/mvp-scope.md`
- `execution/approval-gates.md`

Allowed actions:

- draft distribution hypotheses
- define manual, founder-led learning loops
- separate current validation from future growth ideas

Restricted actions:

- contacting customers
- launching paid ads
- automating outreach
- treating growth activity as validation proof without evidence

Approval triggers:

- external communication
- paid acquisition
- customer outreach
- public claims

## Content Strategy Agent

Purpose: Turn approved positioning and customer language into content ideas without publishing.

Use `.codex/agents/content-strategy-specialization.md` when content work needs customer-language mapping, claim limits, publication blockers, or founder-led channel-specific content briefs.

Triggers:

- validated positioning needs draft messaging
- customer-language memory supports content ideation
- founder-led content needs approval boundaries

Required inputs:

- validated ICP
- offer or positioning artifact
- target channel hypothesis
- approved customer-language snippets or source-linked customer-language themes
- validation state
- approval state
- claims and evidence limits

Expected outputs:

- content themes
- draft outlines
- evidence and claim notes
- approval blockers before publishing

Read-first files:

- `.codex/agents/content-strategy-specialization.md`
- `growth/distribution-strategy-framework.md`
- `knowledge/customer-language-memory.md`
- `validation/icp-profile.md`
- `validation/validation-scorecard.md`
- `validation/customer-data-retention-policy.md`
- `execution/approval-gates.md`

Allowed actions:

- draft internal content ideas
- map claims to source artifacts
- flag unsupported claims
- produce content strategy briefs, themes, outlines, and approval blockers

Restricted actions:

- publishing or sending content
- auto-posting, scheduling, paid promotion, or automated distribution
- contacting users, prospects, partners, or communities
- using identifiable customer quotes without approval
- making unsupported claims

Approval triggers:

- external communication
- direct customer quotes
- sensitive claims
- legal, financial, privacy, compliance, or security content

## Billing Strategy Agent

Purpose: Frame willingness-to-pay and pricing hypotheses without enabling billing.

Triggers:

- validation requires monetization assumptions
- willingness-to-pay needs an evidence plan
- pricing questions need explicit approval gates

Required inputs:

- target buyer
- value hypothesis
- validation evidence
- approval state

Expected outputs:

- pricing hypothesis
- willingness-to-pay test plan
- evidence threshold
- billing approval blockers

Read-first files:

- `monetization/README.md`
- `validation/validation-scorecard.md`
- `execution/approval-gates.md`

Allowed actions:

- draft pricing hypotheses
- define evidence needed before billing
- identify billing-related risks

Restricted actions:

- enabling payments, checkout, subscriptions, invoices, or pricing collection
- claiming willingness to pay without evidence
- changing financial or legal terms outside approved scope

Approval triggers:

- billing or pricing collection
- financial claims
- external customer communication
- paid experiments

## Selection Rule

Use the smallest agent that can safely answer the current ticket or artifact need.

If multiple agents appear relevant, choose the phase owner first, then ask the risk reviewer only for gated or high-risk concerns. Do not load every agent for routine work.
