# Linear Tickets - Horizon 1 Foundation / MVP

These tickets make `pipe-venture-builder` usable and governable. They should be created before operationalization, intelligence, growth, or future evolution tickets.

## Ticket Format

Each ticket includes: title, milestone, horizon, priority, objective, why this matters, source rationale, C.O.N.T.R.O.L.E. dimensions supported, included scope, excluded scope, deliverables, acceptance criteria, GO conditions, NO-GO conditions, dependencies, approval requirement, suggested owner/agent, risk level, and notes for implementation.

## PVB-H1-PLAN-01-consolidate-blueprint-delta

- Title: Consolidate blueprint delta into approved execution plan.
- Milestone: Blueprint Consolidation.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Approve the final blueprint deltas before creating Linear issues or changing repository structure.
- Why this matters: Prevents duplicate, contradictory, or overbuilt execution.
- Source rationale: Both source analyses say the baseline should remain, with focused additions from the incremental analysis.
- C.O.N.T.R.O.L.E. dimensions supported: C, N, L, E.
- Included scope: accepted deltas, rejected imports, first implementation sequence, P0/P1 boundary.
- Excluded scope: code edits, Linear mutation, branch creation.
- Deliverables: approved blueprint decision note and ticket creation readiness note.
- Acceptance criteria: baseline and incremental deltas are reconciled; future evolution stays out of MVP; open decisions are listed.
- GO conditions: user approves this plan.
- NO-GO conditions: user wants a different strategic direction or rejects the split by horizon.
- Dependencies: source analyses.
- Approval requirement: explicit human approval.
- Suggested owner/agent: knowledge_curator.
- Risk level: Low.
- Notes for implementation: This is the first ticket if Linear is used.

## PVB-H1-LINEAR-01-confirm-project-before-issues

- Title: Confirm or create Linear project before issue creation.
- Milestone: Blueprint Consolidation.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Search for an existing `pipe-venture-builder` Linear project and avoid duplicate project creation.
- Why this matters: The baseline explicitly requires project-before-ticket governance.
- Source rationale: Previous analysis and prompt require Linear project confirmation before issues.
- C.O.N.T.R.O.L.E. dimensions supported: E, L.
- Included scope: project search, project recommendation, approval request.
- Excluded scope: creating issues, changing statuses, writing code.
- Deliverables: confirmed project ID or approved project creation result.
- Acceptance criteria: project existence is known; no duplicate project is created; milestones can be attached to a single project.
- GO conditions: user explicitly authorizes Linear access and mutation.
- NO-GO conditions: no Linear permission, unavailable connector, or ambiguous target team.
- Dependencies: PVB-H1-PLAN-01.
- Approval requirement: explicit approval before any Linear write.
- Suggested owner/agent: linear_project_orchestrator.
- Risk level: Medium.
- Notes for implementation: If Linear is unavailable, keep this as a manual checklist.

## PVB-H1-FOUND-02-create-base-repo-skeleton

- Title: Create base repository skeleton.
- Milestone: Base Repository Foundation.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Establish the reusable folder structure for the template repository.
- Why this matters: All later tickets depend on predictable locations for product, validation, research, architecture, execution, growth, monetization, knowledge, agents, and examples.
- Source rationale: Previous analysis recommended the base architecture; incremental analysis confirms it.
- C.O.N.T.R.O.L.E. dimensions supported: N, E.
- Included scope: top-level folders, placeholder docs, template intent notes.
- Excluded scope: full agent implementation, MCP workflows, product-specific content.
- Deliverables: base folder tree and minimal placeholders.
- Acceptance criteria: repo can be navigated by a new founder; folders map to the pipeline; no product-specific assumptions are baked in.
- GO conditions: blueprint approved.
- NO-GO conditions: target repository unclear or skeleton already accepted.
- Dependencies: PVB-H1-PLAN-01.
- Approval requirement: human review before merge.
- Suggested owner/agent: roadmap_orchestrator.
- Risk level: Low.
- Notes for implementation: Reconcile with any existing skeleton rather than recreating it.

## PVB-H1-FOUND-03-write-readme-and-operating-manual

- Title: Write README and operating manual.
- Milestone: Base Repository Foundation.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Explain what the template is, how to use it, and what actions are approval-gated.
- Why this matters: A template without clear operating instructions becomes ad hoc prompt storage.
- Source rationale: Baseline requires a GitHub Template Repository with practical governance.
- C.O.N.T.R.O.L.E. dimensions supported: O, N, E.
- Included scope: README, operating manual outline, first-run path, approval warnings.
- Excluded scope: long theory essays, product-specific examples beyond a minimal sample.
- Deliverables: README and operating manual docs.
- Acceptance criteria: a new user knows how to start with idea intake and when not to proceed.
- GO conditions: base skeleton exists.
- NO-GO conditions: README tries to cover all future roadmap items in detail.
- Dependencies: PVB-H1-FOUND-02.
- Approval requirement: human review before merge.
- Suggested owner/agent: product_strategist.
- Risk level: Low.
- Notes for implementation: Keep concise; link to deeper templates.

## PVB-H1-FOUND-04-define-agents-md-and-approval-gates

- Title: Define AGENTS.md and approval gates.
- Milestone: Base Repository Foundation.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Define mandatory read-first rules, execution constraints, and approval gates for agents.
- Why this matters: Agent autonomy must remain bounded before any ticket execution.
- Source rationale: Previous analysis reuses miles-app governance; incremental analysis adds authority hierarchy.
- C.O.N.T.R.O.L.E. dimensions supported: E, L.
- Included scope: AGENTS.md, approval matrix, risky-action list, human review rules.
- Excluded scope: full agent marketplace or autonomous deployment rules.
- Deliverables: AGENTS.md and approval gate doc.
- Acceptance criteria: external actions, Linear writes, PRs, deploys, ads, billing, secrets, outreach, and sensitive claims require approval.
- GO conditions: README/operating manual direction is accepted.
- NO-GO conditions: approval gates are vague or optional.
- Dependencies: PVB-H1-FOUND-03.
- Approval requirement: human review.
- Suggested owner/agent: risk_reviewer.
- Risk level: Medium.
- Notes for implementation: Put safety rules near the top, not buried in appendices.

## PVB-H1-FOUND-05-map-core-pipeline

- Title: Map core venture pipeline.
- Milestone: Base Repository Foundation.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Document the required sequence from idea intake to first product trial.
- Why this matters: The order prevents growth, billing, or implementation from jumping ahead of validation.
- Source rationale: Both analyses define a sequential pipeline with C.O.N.T.R.O.L.E., validation, PRD, MVP, architecture, Linear, execution, feedback, and knowledge.
- C.O.N.T.R.O.L.E. dimensions supported: O, N, L, E.
- Included scope: pipeline map, stage outputs, required approvals, Linear impact.
- Excluded scope: advanced intelligence and distribution details.
- Deliverables: execution pipeline map.
- Acceptance criteria: every phase has input, output, owner, approval requirement, and next step.
- GO conditions: AGENTS.md and approval gates exist.
- NO-GO conditions: pipeline permits tickets before validation or project confirmation.
- Dependencies: PVB-H1-FOUND-04.
- Approval requirement: human review.
- Suggested owner/agent: roadmap_orchestrator.
- Risk level: Medium.
- Notes for implementation: Use the baseline pipeline as the source.

## PVB-H1-FOUND-06-define-product-context-template

- Title: Define product context template.
- Milestone: Base Repository Foundation.
- Horizon: H1 - Foundation / MVP.
- Priority: P1.
- Objective: Create a reusable template for product-specific context when a new idea starts.
- Why this matters: Keeps the base repo generic while allowing each product run to capture target, problem, offer, channel, stage, and evidence.
- Source rationale: Incremental analysis recommends stage fields and customer-language memory.
- C.O.N.T.R.O.L.E. dimensions supported: C, O, L.
- Included scope: idea, target market, problem, offer, channel, stage, constraints, assumptions, evidence links.
- Excluded scope: private founder biography or secrets.
- Deliverables: product context template.
- Acceptance criteria: template distinguishes assumptions from evidence and includes stage.
- GO conditions: pipeline map exists.
- NO-GO conditions: template stores sensitive personal or customer data without rules.
- Dependencies: PVB-H1-FOUND-05.
- Approval requirement: human review before public template merge.
- Suggested owner/agent: idea_intake_agent.
- Risk level: Low.
- Notes for implementation: Add a note for private/local context storage.

## PVB-H1-VALID-07-add-controle-gate-template

- Title: Add C.O.N.T.R.O.L.E. gate template.
- Milestone: Validation & Discovery Pipeline.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Make C.O.N.T.R.O.L.E. a required strategic evaluation before PRD or ticket creation.
- Why this matters: It prevents idea sprawl, shallow automation, weak AI wrappers, and premature execution.
- Source rationale: C.O.N.T.R.O.L.E. is central in both source analyses.
- C.O.N.T.R.O.L.E. dimensions supported: C, O, N, T, R, O, L, E.
- Included scope: scorecard, verdict, biggest strength/weakness, MVP implication, validation implication, next step.
- Excluded scope: automated scoring or bypass rules.
- Deliverables: C.O.N.T.R.O.L.E. evaluation template.
- Acceptance criteria: template outputs Attack/Refine/Pivot/Kill and is referenced before PRD/ticketing.
- GO conditions: pipeline map exists.
- NO-GO conditions: C.O.N.T.R.O.L.E. is treated as optional decoration.
- Dependencies: PVB-H1-FOUND-05.
- Approval requirement: human approval before advancing on Attack/Refine.
- Suggested owner/agent: product_strategist and risk_reviewer.
- Risk level: Medium.
- Notes for implementation: Keep exact dimensions visible.

## PVB-H1-VALID-08-add-founder-focus-template

- Title: Add founder focus template.
- Milestone: Validation & Discovery Pipeline.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Enforce the founder solo rule: one market, one problem, one offer, one channel before expansion.
- Why this matters: It keeps the template from encouraging multi-audience or platform-first thinking too early.
- Source rationale: Baseline C.O.N.T.R.O.L.E. framework and solo-founder incremental analysis.
- C.O.N.T.R.O.L.E. dimensions supported: O, N, T, E.
- Included scope: target market, problem, offer, channel, one-year focus, anti-goals.
- Excluded scope: broad platform roadmap and multi-channel launch.
- Deliverables: founder focus template.
- Acceptance criteria: every new idea must declare focus and anti-goals.
- GO conditions: C.O.N.T.R.O.L.E. gate exists.
- NO-GO conditions: founder focus permits multiple initial audiences.
- Dependencies: PVB-H1-VALID-07.
- Approval requirement: human review if focus is ambiguous.
- Suggested owner/agent: product_strategist.
- Risk level: Low.
- Notes for implementation: This should be short and strict.

## PVB-H1-VALID-09-add-validation-scorecard

- Title: Add validation scorecard and pressure-test questions.
- Milestone: Validation & Discovery Pipeline.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Require measurable validation before PRD, build, growth, or monetization.
- Why this matters: It converts founder excitement into evidence-based GO/NO-GO decisions.
- Source rationale: Incremental analysis recommends the solo-founder validation pressure test and scorecard.
- C.O.N.T.R.O.L.E. dimensions supported: C, O, L, E.
- Included scope: pain, status quo, ICP specificity, wedge, observed evidence, willingness to engage/pay, score interpretation.
- Excluded scope: fake certainty, paid ads, automated outreach.
- Deliverables: validation scorecard template.
- Acceptance criteria: scorecard has clear thresholds and links to C.O.N.T.R.O.L.E. verdict.
- GO conditions: founder focus and C.O.N.T.R.O.L.E. are complete.
- NO-GO conditions: validation is based only on internal opinion.
- Dependencies: PVB-H1-VALID-07, PVB-H1-VALID-08.
- Approval requirement: human approval before build-ticket creation.
- Suggested owner/agent: customer_discovery_agent.
- Risk level: Medium.
- Notes for implementation: Synthetic persona output cannot satisfy this ticket by itself.

## PVB-H1-VALID-10-add-customer-discovery-and-icp-memory

- Title: Add customer discovery and ICP memory templates.
- Milestone: Validation & Discovery Pipeline.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Capture customer interviews, exact language, ICP assumptions, and learning loops.
- Why this matters: Customer language becomes proprietary context and improves future PRD, launch, and positioning work.
- Source rationale: Incremental analysis recommends the `MY-ICP.md` pattern and customer-language memory.
- C.O.N.T.R.O.L.E. dimensions supported: C, O, L.
- Included scope: interview script, ICP profile, exact quotes, trigger events, status quo, objections, evidence log.
- Excluded scope: automated outreach, storing sensitive customer data without approval.
- Deliverables: customer interview template, ICP profile, customer-language memory template.
- Acceptance criteria: templates distinguish quotes, evidence, assumptions, and synthesis.
- GO conditions: validation scorecard exists.
- NO-GO conditions: fictional personas are treated as real interviews.
- Dependencies: PVB-H1-VALID-09.
- Approval requirement: approval before contacting customers or storing sensitive data.
- Suggested owner/agent: customer_discovery_agent and knowledge_curator.
- Risk level: Medium.
- Notes for implementation: Include privacy guidance.

## PVB-H1-MVP-11-add-mvp-core-loop-and-scope-gate

- Title: Add MVP core loop and scope gate.
- Milestone: Product Architecture Pipeline.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Define the smallest ethical test of the riskiest business assumption.
- Why this matters: The MVP should validate the riskiest assumption, not merely minimize build effort.
- Source rationale: Incremental analysis combines product-architect MVP core loop with solo-founder prioritization.
- C.O.N.T.R.O.L.E. dimensions supported: N, T, L, E.
- Included scope: core user, core job, core action, core result, core feedback loop, riskiest assumption, explicit cuts.
- Excluded scope: full feature backlog, scalability work, billing unless core to validation.
- Deliverables: MVP scope gate template.
- Acceptance criteria: every MVP has a core loop, cut list, evidence threshold, and GO/NO-GO condition.
- GO conditions: validation scorecard and ICP memory exist.
- NO-GO conditions: MVP scope is a feature wishlist.
- Dependencies: PVB-H1-VALID-09, PVB-H1-VALID-10.
- Approval requirement: human approval before architecture or implementation tickets.
- Suggested owner/agent: mvp_scope_reviewer.
- Risk level: Medium.
- Notes for implementation: Include examples of what to cut.

## PVB-H1-LINEAR-12-define-linear-governance-model

- Title: Define Linear governance model.
- Milestone: Linear Governance Workflow.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Define project, milestone, label, dependency, approval, and issue lifecycle rules.
- Why this matters: Linear should orchestrate execution, not become a static planning archive.
- Source rationale: Previous analysis emphasizes Linear project before tickets and miles-app execution patterns.
- C.O.N.T.R.O.L.E. dimensions supported: L, E.
- Included scope: project template, milestones, labels, dependencies, status rules, approval labels.
- Excluded scope: actual Linear creation without explicit approval.
- Deliverables: Linear governance template.
- Acceptance criteria: project-first rule is explicit; tickets include source rationale, acceptance criteria, GO/NO-GO, dependencies, and owner.
- GO conditions: base pipeline and MVP gate exist.
- NO-GO conditions: tickets can be created without project context.
- Dependencies: PVB-H1-FOUND-05, PVB-H1-MVP-11.
- Approval requirement: explicit approval before Linear write actions.
- Suggested owner/agent: linear_project_orchestrator.
- Risk level: Medium.
- Notes for implementation: Keep statuses simple.

## PVB-H1-EXEC-13-add-ticket-pr-handoff-system

- Title: Add ticket, PR, and handoff system.
- Milestone: Linear Governance Workflow.
- Horizon: H1 - Foundation / MVP.
- Priority: P0.
- Objective: Define how a ticket becomes a branch, PR, review, handoff, and knowledge update.
- Why this matters: Execution must remain traceable from Linear to GitHub to learning.
- Source rationale: Previous analysis recommends reusing miles-app task contracts and handoff protocol.
- C.O.N.T.R.O.L.E. dimensions supported: L, E.
- Included scope: ticket template, PR template, handoff protocol, done criteria, status update expectations.
- Excluded scope: CI implementation and production deployment automation.
- Deliverables: ticket template, PR template, handoff protocol.
- Acceptance criteria: every implementation ticket can be executed and reviewed without hidden context.
- GO conditions: Linear governance model exists.
- NO-GO conditions: handoff omits tests, risks, or acceptance criteria.
- Dependencies: PVB-H1-LINEAR-12.
- Approval requirement: human review before merge.
- Suggested owner/agent: ticket_orchestrator.
- Risk level: Medium.
- Notes for implementation: Include one-ticket-per-branch guidance.

## PVB-H1-TRIAL-14-define-first-product-trial-protocol

- Title: Define first product trial protocol.
- Milestone: First Product Trial Run.
- Horizon: H1 - Foundation / MVP.
- Priority: P1.
- Objective: Specify how one sample product idea will test the entire pipeline.
- Why this matters: The template is not proven until it can process a real or sample idea end to end.
- Source rationale: Both analyses recommend a first trial after foundation and validation gates.
- C.O.N.T.R.O.L.E. dimensions supported: C, O, N, L, E.
- Included scope: sample input, required artifacts, success/failure criteria, KDR output, follow-up issue creation.
- Excluded scope: real customer outreach, production deploy, billing, paid ads.
- Deliverables: first product trial protocol.
- Acceptance criteria: protocol covers idea intake, C.O.N.T.R.O.L.E., validation scorecard, ICP, MVP loop, PRD, architecture review, Linear proposal, KDR.
- GO conditions: H1 P0 tickets are complete.
- NO-GO conditions: trial requires external actions before approval.
- Dependencies: PVB-H1-VALID-10, PVB-H1-MVP-11, PVB-H1-EXEC-13.
- Approval requirement: human approval before using a real business idea externally.
- Suggested owner/agent: roadmap_orchestrator and knowledge_curator.
- Risk level: Low/Medium.
- Notes for implementation: Use a sample idea first.
