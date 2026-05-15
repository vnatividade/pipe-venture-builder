# Linear Tickets - Horizon 4 Distribution / Growth

These tickets should activate only after validation and MVP scope gates exist. They are not MVP foundation work.

## PVB-H4-GROWTH-01-define-distribution-strategy-framework

- Title: Define distribution strategy framework.
- Milestone: Distribution & Growth System.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define how one validated product chooses one primary channel before expanding.
- Why this matters: Founder-led distribution requires focus, not channel sprawl.
- Source rationale: Baseline founder rule and incremental solo-founder stage guidance.
- C.O.N.T.R.O.L.E. dimensions supported: O, T, R, O, L.
- Included scope: target persona, channel hypothesis, reachability, trust path, proof, first conversion metric.
- Excluded scope: multi-channel campaigns and paid ads automation.
- Deliverables: distribution strategy framework.
- Acceptance criteria: framework enforces one channel and requires validation evidence.
- GO conditions: MVP scope and ICP exist.
- NO-GO conditions: no evidence of demand or unclear target persona.
- Dependencies: PVB-H1-VALID-10, PVB-H1-MVP-11.
- Approval requirement: human approval before external execution.
- Suggested owner/agent: distribution_strategist_agent.
- Risk level: Medium.
- Notes for implementation: Keep paid growth explicitly gated.

## PVB-H4-GROWTH-02-add-channel-experiment-template

- Title: Add channel experiment template.
- Milestone: Distribution & Growth System.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define testable channel experiments with hypothesis, metric, threshold, and learning card.
- Why this matters: Growth should become a learning loop, not activity volume.
- Source rationale: Baseline experiment system and Strategyzer-style test/learning logic from previous analysis.
- C.O.N.T.R.O.L.E. dimensions supported: O, L, E.
- Included scope: hypothesis, channel, audience, message, metric, threshold, cost, approval, result.
- Excluded scope: running ads or outreach automatically.
- Deliverables: channel experiment template.
- Acceptance criteria: every experiment has a GO/NO-GO threshold and learning update.
- GO conditions: distribution strategy framework exists.
- NO-GO conditions: experiment lacks measurable outcome.
- Dependencies: PVB-H4-GROWTH-01.
- Approval requirement: approval before publishing, outreach, or paid spend.
- Suggested owner/agent: growth_experiment_agent.
- Risk level: Medium.
- Notes for implementation: Use manual tests first.

## PVB-H4-GROWTH-03-create-growth-experiment-backlog

- Title: Create growth experiment backlog model.
- Milestone: Distribution & Growth System.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define how validated growth experiments are captured, prioritized, and sequenced.
- Why this matters: Keeps future growth ideas visible without polluting MVP execution.
- Source rationale: Prompt requires growth experiment backlog.
- C.O.N.T.R.O.L.E. dimensions supported: O, L, E.
- Included scope: backlog columns, priority rules, evidence links, stage gates, approval labels.
- Excluded scope: executing backlog items automatically.
- Deliverables: growth experiment backlog template.
- Acceptance criteria: backlog separates idea, approved experiment, running, learned, and killed.
- GO conditions: channel experiment template exists.
- NO-GO conditions: backlog includes unvalidated growth work as P0.
- Dependencies: PVB-H4-GROWTH-02.
- Approval requirement: human approval before external actions.
- Suggested owner/agent: growth_experiment_agent.
- Risk level: Low/Medium.
- Notes for implementation: Use Linear labels/views later.

## PVB-H4-GROWTH-04-add-fake-door-landing-page-validation

- Title: Add fake-door and landing page validation workflow.
- Milestone: Validation & Discovery Pipeline.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define ethical fake-door and landing-page tests for demand validation.
- Why this matters: Some ideas need behavioral evidence before build.
- Source rationale: Incremental solo-founder validation recommends smoke tests, fake doors, and landing pages.
- C.O.N.T.R.O.L.E. dimensions supported: O, L, E.
- Included scope: hypothesis, offer, page/message, traffic source, metric, thresholds, ethics note.
- Excluded scope: deceptive collection, paid ads by default, production build.
- Deliverables: fake-door/landing-page validation workflow.
- Acceptance criteria: workflow defines what users see, what is measured, and what happens after signup/interest.
- GO conditions: ICP and validation scorecard exist.
- NO-GO conditions: test is misleading or lacks follow-up plan.
- Dependencies: PVB-H1-VALID-09, PVB-H1-VALID-10.
- Approval requirement: human approval before publishing.
- Suggested owner/agent: customer_discovery_agent and growth_experiment_agent.
- Risk level: High.
- Notes for implementation: Include ethical disclosure guidance.

## PVB-H4-GROWTH-05-define-content-strategy-agent

- Title: Define content strategy agent.
- Milestone: Distribution & Growth System.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define an agent that turns validated positioning into founder-led content ideas.
- Why this matters: Content should amplify evidence-backed positioning, not create generic posts.
- Source rationale: Baseline includes content_strategy_agent and prompt requires content strategy agent.
- C.O.N.T.R.O.L.E. dimensions supported: O, T, L.
- Included scope: triggers, inputs, outputs, approval requirements, customer-language use.
- Excluded scope: auto-posting or external publication.
- Deliverables: content strategy agent contract.
- Acceptance criteria: agent requires ICP, offer, channel, and customer language before output.
- GO conditions: distribution framework and ICP memory exist.
- NO-GO conditions: agent can publish or contact users without approval.
- Dependencies: PVB-H4-GROWTH-01, PVB-H1-VALID-10.
- Approval requirement: approval before publication.
- Suggested owner/agent: content_strategy_agent.
- Risk level: Medium.
- Notes for implementation: Tie to exact customer language.

## PVB-H4-GROWTH-06-define-distribution-and-growth-agents

- Title: Define distribution strategist and growth experiment agents.
- Milestone: Agent/Skill Specialization.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Specialize distribution_strategist_agent and growth_experiment_agent.
- Why this matters: Distribution and growth need different rules than product validation.
- Source rationale: Prompt requires distribution strategist and growth experiment agent specialization.
- C.O.N.T.R.O.L.E. dimensions supported: O, R, L, E.
- Included scope: channel strategy, experiment design, approvals, learning loop, external action restrictions.
- Excluded scope: autonomous outreach, paid ads, or account creation.
- Deliverables: specialized agent contracts.
- Acceptance criteria: agents can propose tests but cannot execute external actions without approval.
- GO conditions: channel experiment template exists.
- NO-GO conditions: growth agents can bypass validation evidence.
- Dependencies: PVB-H4-GROWTH-02.
- Approval requirement: human approval before any external action.
- Suggested owner/agent: growth_experiment_agent.
- Risk level: High.
- Notes for implementation: Mark as do-not-automate by default.

## PVB-H4-GROWTH-07-add-founder-led-distribution-playbook

- Title: Add founder-led distribution playbook.
- Milestone: Distribution & Growth System.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define practical founder-led distribution actions by stage.
- Why this matters: Solo-founder growth should start with direct learning and narrow channels.
- Source rationale: Incremental solo-founder repository provides stage-aware growth and launch guidance.
- C.O.N.T.R.O.L.E. dimensions supported: O, T, L, E.
- Included scope: warm outreach, communities, content, partnerships, manual sales, feedback capture.
- Excluded scope: spam, automated outreach, paid campaigns without approval.
- Deliverables: founder-led distribution playbook.
- Acceptance criteria: playbook is stage-aware and approval-gated for external contact.
- GO conditions: distribution strategy framework exists.
- NO-GO conditions: broad multi-channel playbook is treated as immediate execution.
- Dependencies: PVB-H4-GROWTH-01.
- Approval requirement: approval before contacting customers.
- Suggested owner/agent: distribution_strategist_agent.
- Risk level: High.
- Notes for implementation: Keep sample scripts as drafts only.

## PVB-H4-GROWTH-08-add-launch-readiness-checklist

- Title: Add launch readiness checklist.
- Milestone: Distribution & Growth System.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define readiness checks for positioning, channel, offer, proof, support, and learning loop.
- Why this matters: Launch should happen only when validation and operational basics are ready.
- Source rationale: Incremental analysis recommends launch positioning/channel/offer checklist.
- C.O.N.T.R.O.L.E. dimensions supported: O, L, E.
- Included scope: target, promise, proof, channel, offer, onboarding, support, analytics, approval.
- Excluded scope: automatic public launch.
- Deliverables: launch readiness checklist.
- Acceptance criteria: checklist blocks launch without validation evidence and approval.
- GO conditions: MVP trial and distribution strategy exist.
- NO-GO conditions: no customer evidence or unclear offer.
- Dependencies: PVB-H1-MVP-11, PVB-H4-GROWTH-01.
- Approval requirement: human approval before launch.
- Suggested owner/agent: growth_experiment_agent and risk_reviewer.
- Risk level: High.
- Notes for implementation: Include "not ready because..." output.

## PVB-H4-GROWTH-09-add-post-launch-learning-loop

- Title: Add post-launch learning loop.
- Milestone: Distribution & Growth System.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define how launch data and customer feedback update the knowledge base and backlog.
- Why this matters: Growth must compound into learning, not just activity.
- Source rationale: Baseline includes feedback and learning loops.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: metrics, feedback, objections, support issues, KDR updates, backlog changes.
- Excluded scope: automated roadmap changes.
- Deliverables: post-launch learning loop template.
- Acceptance criteria: every launch/experiment produces a learning card and decision update.
- GO conditions: launch checklist exists.
- NO-GO conditions: results are not tied to a decision.
- Dependencies: PVB-H4-GROWTH-08, PVB-H2-KNOW-09.
- Approval requirement: human review for roadmap changes.
- Suggested owner/agent: knowledge_curator.
- Risk level: Medium.
- Notes for implementation: Include "kill/keep/change" decision.

## PVB-H4-GROWTH-10-define-idea-browser-validation

- Title: Define Idea Browser validation workflow.
- Milestone: Idea Ranking & Idea Browser Validation.
- Horizon: H4 - Distribution / Growth.
- Priority: P2/P3.
- Objective: Define how an Idea Browser can provide validation input without replacing real discovery.
- Why this matters: Idea Browser signals can help compare ideas, but they can create false confidence.
- Source rationale: Prompt explicitly requires Idea Browser validation workflow.
- C.O.N.T.R.O.L.E. dimensions supported: C, O, L.
- Included scope: what Idea Browser is used for, signal types, comparison rules, ranking influence, insufficiency rules.
- Excluded scope: treating Idea Browser as real customer proof.
- Deliverables: Idea Browser validation workflow.
- Acceptance criteria: workflow states when Idea Browser is sufficient and when interviews are required.
- GO conditions: idea ranking design exists.
- NO-GO conditions: Idea Browser output bypasses validation scorecard.
- Dependencies: PVB-H3-RANK-10.
- Approval requirement: human review before prioritization changes.
- Suggested owner/agent: venture_intelligence_curator.
- Risk level: Medium/High.
- Notes for implementation: Keep as advisory.

## PVB-H4-MONETIZATION-11-add-pricing-hypothesis-template

- Title: Add pricing and willingness-to-pay hypothesis template.
- Milestone: Distribution & Growth System.
- Horizon: H4 - Distribution / Growth.
- Priority: P2.
- Objective: Define pricing hypotheses without implementing billing.
- Why this matters: Monetization should test willingness to pay before payment infrastructure.
- Source rationale: Baseline delays billing; incremental analysis recommends pricing hypothesis only.
- C.O.N.T.R.O.L.E. dimensions supported: T, L, E.
- Included scope: buyer, value anchor, pricing metric, willingness-to-pay evidence, test method, NO-GO threshold.
- Excluded scope: Stripe/payment code, subscriptions, tax/accounting automation.
- Deliverables: pricing hypothesis template.
- Acceptance criteria: template separates pricing validation from billing implementation.
- GO conditions: willingness-to-pay evidence exists.
- NO-GO conditions: pricing is speculative or billing is requested before validation.
- Dependencies: PVB-H1-VALID-09.
- Approval requirement: human approval before billing.
- Suggested owner/agent: billing_strategy_agent.
- Risk level: High.
- Notes for implementation: This is not a payment integration ticket.
