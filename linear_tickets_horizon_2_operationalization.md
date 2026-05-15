# Linear Tickets - Horizon 2 Operationalization

These tickets make the system repeatable after the H1 foundation is usable. They should not block the first repository skeleton, but they are needed for a reliable first product trial and future product runs.

## PVB-H2-AGENT-01-define-core-agent-contracts

- Title: Define core agent contracts.
- Milestone: Core Agent System.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Define compact agents with purpose, triggers, inputs, outputs, reads-first files, and approval rules.
- Why this matters: Small composable agents are safer than a master agent.
- Source rationale: Baseline agent system plus incremental warning against importing 31 agents.
- C.O.N.T.R.O.L.E. dimensions supported: N, E.
- Included scope: idea_intake, product_strategist, customer_discovery, mvp_scope_reviewer, research_orchestrator, market_intelligence, scientific_validation, software_architect, risk_reviewer, roadmap_orchestrator, ticket_orchestrator, linear_project_orchestrator, knowledge_curator, growth_experiment, content_strategy, billing_strategy.
- Excluded scope: implementation of all specialized future agents.
- Deliverables: core agent contract file(s).
- Acceptance criteria: each agent has bounded scope and explicit approval triggers.
- GO conditions: AGENTS.md and pipeline exist.
- NO-GO conditions: a single agent owns the whole process.
- Dependencies: PVB-H1-FOUND-04, PVB-H1-FOUND-05.
- Approval requirement: human review.
- Suggested owner/agent: roadmap_orchestrator.
- Risk level: Medium.
- Notes for implementation: Keep agents generic and template-safe.

## PVB-H2-SKILL-02-define-core-skill-contracts

- Title: Define core skill contracts.
- Milestone: Core Agent System.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Define reusable SKILL.md-style workflows for validation, PRD, Linear governance, handoff, research, and knowledge updates.
- Why this matters: Skills let workflows load on demand instead of bloating the main context.
- Source rationale: Previous analysis recommends converting playbooks into skills; incremental analysis warns not to import all 59 skills.
- C.O.N.T.R.O.L.E. dimensions supported: C, N, L, E.
- Included scope: skill purpose, trigger, inputs, outputs, files read, approval rules.
- Excluded scope: copying the full solo-founder skill tree.
- Deliverables: skill contract template and initial skill list.
- Acceptance criteria: every skill has a narrow trigger and expected output.
- GO conditions: core agents are defined.
- NO-GO conditions: skills duplicate entire source repos.
- Dependencies: PVB-H2-AGENT-01.
- Approval requirement: human review.
- Suggested owner/agent: knowledge_curator.
- Risk level: Low.
- Notes for implementation: Use progressive disclosure.

## PVB-H2-AGENT-03-define-trigger-rules

- Title: Define agent and skill trigger rules.
- Milestone: Core Agent System.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Specify when agents and skills should activate.
- Why this matters: Prevents context overload and accidental late-stage workflows.
- Source rationale: Incremental analysis recommends a lightweight context router from product-architect.
- C.O.N.T.R.O.L.E. dimensions supported: N, E.
- Included scope: request type detection, phase routing, max loaded agents/templates, escalation rules.
- Excluded scope: full scoring engine or autonomous orchestration.
- Deliverables: trigger rule document.
- Acceptance criteria: broad requests are phased; no more than a small relevant set is loaded by default.
- GO conditions: core agent and skill contracts exist.
- NO-GO conditions: all agents are loaded for every task.
- Dependencies: PVB-H2-AGENT-01, PVB-H2-SKILL-02.
- Approval requirement: human review.
- Suggested owner/agent: roadmap_orchestrator.
- Risk level: Medium.
- Notes for implementation: This can later become the context router.

## PVB-H2-AGENT-04-define-agent-handoff-protocol

- Title: Define agent handoff protocol.
- Milestone: Core Agent System.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Define how one agent passes context, decisions, risks, and next steps to another.
- Why this matters: Handoffs preserve continuity and reduce conversation-memory dependence.
- Source rationale: Baseline imports miles-app handoff concepts; incremental analysis adds KDR continuity.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: handoff fields, required artifacts, unresolved questions, approval status, KDR update.
- Excluded scope: automated multi-agent execution.
- Deliverables: agent handoff protocol.
- Acceptance criteria: handoff includes source files, decisions, evidence, risks, next owner, and done criteria.
- GO conditions: agent contracts exist.
- NO-GO conditions: handoff relies on unstated chat context.
- Dependencies: PVB-H2-AGENT-01.
- Approval requirement: human review.
- Suggested owner/agent: ticket_orchestrator.
- Risk level: Low/Medium.
- Notes for implementation: Align with PR handoff.

## PVB-H2-EXEC-05-add-agent-readiness-validator

- Title: Add agent readiness validator.
- Milestone: Core Agent System.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Validate whether a ticket is ready for agent execution.
- Why this matters: Prevents agents from implementing unclear, unsafe, or dependency-blocked work.
- Source rationale: Baseline references readiness validators from miles-app.
- C.O.N.T.R.O.L.E. dimensions supported: E, L.
- Included scope: checklist for scope, dependencies, approval, acceptance criteria, risk level, files, tests.
- Excluded scope: automated enforcement without human override.
- Deliverables: readiness validator template.
- Acceptance criteria: tickets can be marked READY/NOT READY with reasons.
- GO conditions: issue template exists.
- NO-GO conditions: validator becomes a long bureaucratic form.
- Dependencies: PVB-H1-EXEC-13.
- Approval requirement: human review.
- Suggested owner/agent: risk_reviewer.
- Risk level: Medium.
- Notes for implementation: Keep it short and binary where possible.

## PVB-H2-RISK-06-define-risk-reviewer-and-risk-matrix

- Title: Define risk reviewer and risk matrix lite.
- Milestone: Risk Review and Approval Gates.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Add a lightweight risk review system for product, technical, legal, financial, privacy, and operational risk.
- Why this matters: Catches high-impact risks without enterprise risk bureaucracy.
- Source rationale: Incremental analysis recommends product-architect risk matrix and authority hierarchy.
- C.O.N.T.R.O.L.E. dimensions supported: R, E.
- Included scope: likelihood, impact, mitigation, owner, trigger, approval rule.
- Excluded scope: full enterprise risk registry.
- Deliverables: risk matrix lite and risk reviewer contract.
- Acceptance criteria: high-risk items require explicit approval or documented acceptance.
- GO conditions: approval gates exist.
- NO-GO conditions: risk review blocks low-risk learning tests unnecessarily.
- Dependencies: PVB-H1-FOUND-04.
- Approval requirement: human review.
- Suggested owner/agent: risk_reviewer.
- Risk level: Medium/High.
- Notes for implementation: Separate reversible from irreversible risks.

## PVB-H2-EXEC-07-define-ticket-orchestrator

- Title: Define ticket orchestrator workflow.
- Milestone: Linear Governance Workflow.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Define how approved PRD/MVP/architecture artifacts become small Linear issues.
- Why this matters: Prevents mega-tickets and keeps agent work executable.
- Source rationale: Baseline includes ticket_orchestrator and Linear project-first workflow.
- C.O.N.T.R.O.L.E. dimensions supported: N, L, E.
- Included scope: issue decomposition rules, dependency mapping, acceptance criteria, owner assignment, approval labels.
- Excluded scope: direct ticket creation without approval.
- Deliverables: ticket orchestration workflow.
- Acceptance criteria: every ticket is scoped to one outcome and includes dependencies and approval gates.
- GO conditions: Linear governance model exists.
- NO-GO conditions: ticket orchestrator creates issues before project confirmation.
- Dependencies: PVB-H1-LINEAR-12.
- Approval requirement: approval before Linear write.
- Suggested owner/agent: ticket_orchestrator.
- Risk level: Medium.
- Notes for implementation: Include now/next/later separation.

## PVB-H2-KNOW-08-define-knowledge-curator

- Title: Define knowledge curator workflow.
- Milestone: Knowledge Base & Memory Layer.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Define how decisions, learning, evidence, and customer language are captured and updated.
- Why this matters: Knowledge should compound instead of disappearing into conversations.
- Source rationale: Baseline includes knowledge loop; incremental analysis adds KDR/DAR and customer-language memory.
- C.O.N.T.R.O.L.E. dimensions supported: C, L.
- Included scope: decision log, learning log, evidence repository, customer-language memory, update cadence.
- Excluded scope: complex knowledge graph or external MCP sync.
- Deliverables: knowledge curator contract and update workflow.
- Acceptance criteria: every major phase has a knowledge update expectation.
- GO conditions: H1 validation and execution templates exist.
- NO-GO conditions: knowledge docs become unrelated documentation theater.
- Dependencies: PVB-H1-VALID-10, PVB-H1-EXEC-13.
- Approval requirement: human review for sensitive data.
- Suggested owner/agent: knowledge_curator.
- Risk level: Medium.
- Notes for implementation: Include redaction/sensitivity guidance.

## PVB-H2-KNOW-09-add-kdr-dar-template

- Title: Add KDR/DAR decision memory template.
- Milestone: Knowledge Base & Memory Layer.
- Horizon: H2 - Operationalization.
- Priority: P0/P1.
- Objective: Capture why strategic decisions were made and when to revisit them.
- Why this matters: It creates durable context across sessions and future product runs.
- Source rationale: Incremental analysis strongly recommends KDR/DAR from product-architect.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: decision, context, options, rationale, evidence, risks, revisit trigger, supersedes, superseded by.
- Excluded scope: a complex dashboard or mandatory record for trivial edits.
- Deliverables: KDR/DAR template and example.
- Acceptance criteria: strategic decisions can be traced and superseded.
- GO conditions: knowledge curator workflow exists.
- NO-GO conditions: KDR is required for every minor change.
- Dependencies: PVB-H2-KNOW-08.
- Approval requirement: human review for strategic decisions.
- Suggested owner/agent: knowledge_curator.
- Risk level: Medium.
- Notes for implementation: Keep the template short.

## PVB-H2-KNOW-10-add-decision-conflict-protocol

- Title: Add decision conflict and supersession protocol.
- Milestone: Knowledge Base & Memory Layer.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Prevent silent contradictions between old decisions and new recommendations.
- Why this matters: Agent systems drift when old decisions remain active after assumptions change.
- Source rationale: Incremental analysis recommends conflict detection and superseded-decision rules.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: conflict scan, authority hierarchy, superseded markers, unresolved conflict escalation.
- Excluded scope: automated rewriting of old decisions.
- Deliverables: decision conflict protocol.
- Acceptance criteria: new strategic decisions check prior KDRs and mark supersession where needed.
- GO conditions: KDR/DAR template exists.
- NO-GO conditions: conflicts are resolved without human review when high-risk.
- Dependencies: PVB-H2-KNOW-09, PVB-H2-RISK-06.
- Approval requirement: human review for unresolved strategic conflicts.
- Suggested owner/agent: knowledge_curator and risk_reviewer.
- Risk level: Medium.
- Notes for implementation: Include "conflict unresolved" status.

## PVB-H2-ARCH-10-add-lean-prd-template

- Title: Add lean PRD template.
- Milestone: Product Architecture Pipeline.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Define a PRD template tied to validation evidence and MVP scope.
- Why this matters: PRDs should translate evidence into product decisions, not invent requirements.
- Source rationale: Baseline includes PRD; incremental analysis recommends adapting product-architect PRD without bloat.
- C.O.N.T.R.O.L.E. dimensions supported: N, L, E.
- Included scope: problem evidence, goals, non-goals, metrics, stories, requirements, states, risks, acceptance criteria.
- Excluded scope: enterprise staffing plans and speculative long roadmaps.
- Deliverables: lean PRD template.
- Acceptance criteria: PRD references C.O.N.T.R.O.L.E., validation scorecard, ICP, and MVP core loop.
- GO conditions: MVP gate exists.
- NO-GO conditions: PRD is created before validation.
- Dependencies: PVB-H1-MVP-11.
- Approval requirement: human review before architecture/tickets.
- Suggested owner/agent: product_strategist.
- Risk level: Medium.
- Notes for implementation: Keep non-goals prominent.

## PVB-H2-ARCH-11-add-architecture-review-template

- Title: Add architecture review template.
- Milestone: Product Architecture Pipeline.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Define how MVP scope becomes a technical architecture recommendation.
- Why this matters: Architecture must support the MVP test without overbuilding.
- Source rationale: Baseline includes system design; incremental analysis adds edge-case stress review.
- C.O.N.T.R.O.L.E. dimensions supported: T, R, E.
- Included scope: constraints, system shape, integrations, data, risks, failure modes, edge cases.
- Excluded scope: production-grade architecture by default.
- Deliverables: architecture review template.
- Acceptance criteria: architecture references MVP assumptions and flags deferred complexity.
- GO conditions: lean PRD exists.
- NO-GO conditions: architecture proposes scale before validation.
- Dependencies: PVB-H2-ARCH-10.
- Approval requirement: human review before implementation tickets.
- Suggested owner/agent: software_architect.
- Risk level: Medium.
- Notes for implementation: Add explicit "not needed yet" section.

## PVB-H2-ARCH-12-add-adr-rfc-engineering-standards

- Title: Add ADR, RFC, and engineering standards templates.
- Milestone: Product Architecture Pipeline.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Provide lightweight technical decision and standards templates.
- Why this matters: Structural technical decisions need durable rationale, but not heavy process.
- Source rationale: Previous analysis recommends ADR and engineering standards from source repos.
- C.O.N.T.R.O.L.E. dimensions supported: C, T, E.
- Included scope: ADR template, RFC template, engineering standards outline, when-to-use guidance.
- Excluded scope: exhaustive enterprise engineering handbook.
- Deliverables: ADR/RFC/standards templates.
- Acceptance criteria: docs are short, versionable, and linked to tickets when used.
- GO conditions: architecture review template exists.
- NO-GO conditions: every small edit requires an ADR.
- Dependencies: PVB-H2-ARCH-11.
- Approval requirement: human review for structural decisions.
- Suggested owner/agent: software_architect.
- Risk level: Low/Medium.
- Notes for implementation: Favor nearby docs over central bureaucracy.

## PVB-H2-AGENT-13-specialize-strategy-agents

- Title: Specialize strategy and intake agents.
- Milestone: Agent/Skill Specialization.
- Horizon: H2 - Operationalization.
- Priority: P2.
- Objective: Evolve idea_intake_agent, product_strategist, and mvp_scope_reviewer into more specific contracts.
- Why this matters: Strategy work is where founder focus and scope control are won or lost.
- Source rationale: Prompt requires future evolution for more specific skills and agents.
- C.O.N.T.R.O.L.E. dimensions supported: O, N, T, L.
- Included scope: specialization for idea intake, product strategy, MVP scope review, outputs, triggers, approvals.
- Excluded scope: autonomous strategy decisions without approval.
- Deliverables: specialized agent contract updates.
- Acceptance criteria: each agent has clear boundaries and hands off to validation or architecture.
- GO conditions: core agent contracts exist.
- NO-GO conditions: specialization creates a mega-agent.
- Dependencies: PVB-H2-AGENT-01.
- Approval requirement: human review.
- Suggested owner/agent: roadmap_orchestrator.
- Risk level: Low/Medium.
- Notes for implementation: Keep specialization additive.

## PVB-H2-AGENT-14-specialize-research-validation-agents

- Title: Specialize research and validation agents.
- Milestone: Agent/Skill Specialization.
- Horizon: H2 - Operationalization.
- Priority: P2.
- Objective: Evolve research_orchestrator, scientific_validation_agent, market_intelligence_agent, and customer_discovery_agent.
- Why this matters: Research and validation need different evidence standards and source rules.
- Source rationale: Prompt requires specialized research and validation agents.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, T, E.
- Included scope: source quality, interview evidence, market signals, scientific evidence, uncertainty reporting.
- Excluded scope: automatic customer outreach or external claims.
- Deliverables: specialized contracts and handoff rules.
- Acceptance criteria: each agent states allowed evidence types and confidence limits.
- GO conditions: validation templates exist.
- NO-GO conditions: research output is treated as customer proof.
- Dependencies: PVB-H1-VALID-09, PVB-H1-VALID-10.
- Approval requirement: human review before external research tools or outreach.
- Suggested owner/agent: research_orchestrator.
- Risk level: Medium.
- Notes for implementation: Add citation expectations.

## PVB-H2-AGENT-15-specialize-execution-risk-agents

- Title: Specialize execution and risk agents.
- Milestone: Agent/Skill Specialization.
- Horizon: H2 - Operationalization.
- Priority: P2.
- Objective: Evolve software_architect, risk_reviewer, and ticket_orchestrator into sharper execution roles.
- Why this matters: These roles protect implementation quality and safety.
- Source rationale: Prompt requires software architect, risk reviewer, and ticket orchestrator specialization.
- C.O.N.T.R.O.L.E. dimensions supported: R, E, L.
- Included scope: architecture handoff, risk gate, ticket decomposition, readiness validation.
- Excluded scope: deploy automation, PR merge authority.
- Deliverables: specialized execution/risk contracts.
- Acceptance criteria: each role has clear approval boundaries and done criteria.
- GO conditions: H1 execution governance exists.
- NO-GO conditions: agents can merge or deploy without human approval.
- Dependencies: PVB-H1-EXEC-13, PVB-H2-RISK-06.
- Approval requirement: human review.
- Suggested owner/agent: risk_reviewer.
- Risk level: Medium/High.
- Notes for implementation: Tie to PR/handoff.

## PVB-H2-TEMPLATE-16-define-template-fork-automation

- Title: Define template and fork automation workflow.
- Milestone: Template/Fork Automation.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Define how a new product initializes from the template.
- Why this matters: Reuse must be reliable without contaminating the base repo with product-specific context.
- Source rationale: Baseline recommends GitHub Template Repository strategy.
- C.O.N.T.R.O.L.E. dimensions supported: O, N, E.
- Included scope: template usage, product initialization checklist, Codex initialization, Linear initialization, knowledge initialization.
- Excluded scope: automatic repository creation or secrets setup without approval.
- Deliverables: template/fork automation spec.
- Acceptance criteria: new product setup has steps and approval gates.
- GO conditions: foundation and governance docs exist.
- NO-GO conditions: workflow assumes private credentials or product-specific data.
- Dependencies: PVB-H1-FOUND-05, PVB-H1-LINEAR-12.
- Approval requirement: human approval before any actual automation.
- Suggested owner/agent: linear_project_orchestrator.
- Risk level: Medium.
- Notes for implementation: Prefer GitHub Template Repository over fork for new products.

## PVB-H2-HARDEN-17-audit-bloat-and-duplication

- Title: Audit for bloat, duplication, and premature scope.
- Milestone: Hardening, Documentation & Operating Manual.
- Horizon: H2 - Operationalization.
- Priority: P1.
- Objective: Review the template for imported bloat, duplicate docs, and premature later-stage workflows.
- Why this matters: Both analyzed repositories are useful but too large to copy wholesale.
- Source rationale: Incremental analysis warns against importing 59 skills or 31 agents.
- C.O.N.T.R.O.L.E. dimensions supported: T, E.
- Included scope: duplicate checks, stage-order review, approval gate review, future backlog separation.
- Excluded scope: deleting approved core files without approval.
- Deliverables: hardening audit report.
- Acceptance criteria: report lists keep/adapt/remove recommendations and identifies any unapproved later-stage automation.
- GO conditions: initial template set exists.
- NO-GO conditions: audit becomes a broad rewrite.
- Dependencies: H1 and key H2 templates.
- Approval requirement: human approval before removals.
- Suggested owner/agent: risk_reviewer or chief reviewer.
- Risk level: Medium.
- Notes for implementation: Use this after first trial if possible.
