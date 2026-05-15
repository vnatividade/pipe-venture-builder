# Linear Tickets - Horizon 3 Intelligence / Discovery Automation

These tickets design stronger discovery, evidence scoring, and research automation. They should not block the MVP foundation and should not create external tool integrations without a later security and approval pass.

## PVB-H3-RESEARCH-01-design-research-orchestrator

- Title: Design research orchestrator workflow.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2.
- Objective: Define how the system combines market, scientific, customer, and web research into one synthesis.
- Why this matters: Research should support decisions without becoming scattered source collection.
- Source rationale: Baseline includes research_orchestrator; prompt requires combined research orchestration.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: research question intake, source plan, synthesis format, confidence labels, human review.
- Excluded scope: live MCP calls or paid tool usage.
- Deliverables: research orchestrator workflow.
- Acceptance criteria: workflow combines source types and explicitly marks uncertainty.
- GO conditions: validation and knowledge templates exist.
- NO-GO conditions: research replaces customer discovery.
- Dependencies: PVB-H1-VALID-09, PVB-H2-KNOW-08.
- Approval requirement: human review before using external tools.
- Suggested owner/agent: research_orchestrator.
- Risk level: Medium.
- Notes for implementation: This is design-only until connectors are approved.

## PVB-H3-RESEARCH-02-define-market-research-workflow

- Title: Define market research workflow.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2.
- Objective: Create a repeatable workflow for market sizing, substitutes, channels, competition, and reachability.
- Why this matters: Founder-market fit depends on reachable buyers and real substitutes, not TAM slides.
- Source rationale: Incremental analysis adds solo-founder market fit and buyer leverage checks.
- C.O.N.T.R.O.L.E. dimensions supported: O, T, R, L.
- Included scope: substitutes, buyer leverage, channel access, competitive density, market maturity.
- Excluded scope: paid research tools by default.
- Deliverables: market research workflow.
- Acceptance criteria: output distinguishes direct, indirect, DIY, and do-nothing substitutes.
- GO conditions: ICP template exists.
- NO-GO conditions: workflow relies only on generic market size.
- Dependencies: PVB-H1-VALID-10.
- Approval requirement: human review.
- Suggested owner/agent: market_intelligence_agent.
- Risk level: Medium.
- Notes for implementation: Include local/country variation hooks for later ranking.

## PVB-H3-RESEARCH-03-define-scientific-validation-workflow

- Title: Define scientific validation workflow.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2.
- Objective: Define how to validate technical, scientific, medical, behavioral, or research-backed claims.
- Why this matters: Public claims and product assumptions need evidence limits.
- Source rationale: Baseline includes scientific_validation_agent; prompt requires Consensus workflow later.
- C.O.N.T.R.O.L.E. dimensions supported: T, R, L, E.
- Included scope: claim extraction, evidence source tiers, uncertainty, citation requirements, professional review flags.
- Excluded scope: giving professional advice or making public claims without review.
- Deliverables: scientific validation workflow.
- Acceptance criteria: workflow flags claims requiring expert review.
- GO conditions: risk gates exist.
- NO-GO conditions: research summaries are treated as verified advice.
- Dependencies: PVB-H2-RISK-06.
- Approval requirement: expert/human review for sensitive claims.
- Suggested owner/agent: scientific_validation_agent.
- Risk level: High.
- Notes for implementation: Add legal/medical/financial disclaimers.

## PVB-H3-MCP-04-design-notebooklm-discovery

- Title: Design NotebookLM discovery MCP workflow.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P3.
- Objective: Design how NotebookLM could organize source collections and synthesize discovery material.
- Why this matters: Source organization can improve research quality if citations and boundaries are preserved.
- Source rationale: Prompt explicitly requires NotebookLM MCP discovery planning.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: source ingestion concept, synthesis output, citation expectations, approval gates.
- Excluded scope: live MCP implementation, credentials, automated decisions.
- Deliverables: NotebookLM MCP design note.
- Acceptance criteria: design states source types, outputs, limitations, and approval rules.
- GO conditions: research orchestrator design exists.
- NO-GO conditions: no permission to use external connectors or credentials.
- Dependencies: PVB-H3-RESEARCH-01.
- Approval requirement: approval before implementation or connector setup.
- Suggested owner/agent: research_orchestrator.
- Risk level: Medium.
- Notes for implementation: Keep as future design until tool availability is confirmed.

## PVB-H3-MCP-05-design-consensus-validation

- Title: Design Consensus validation workflow.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P3.
- Objective: Design how Consensus could support scientific evidence validation.
- Why this matters: Scientific claims need better source quality than general web search.
- Source rationale: Prompt explicitly requires Consensus workflow planning.
- C.O.N.T.R.O.L.E. dimensions supported: T, R, L, E.
- Included scope: claim query design, evidence grading, citation rules, professional review flags.
- Excluded scope: medical/legal/financial advice or live integration.
- Deliverables: Consensus workflow design.
- Acceptance criteria: design separates evidence summary from decision recommendation.
- GO conditions: scientific validation workflow exists.
- NO-GO conditions: sensitive claim lacks professional review path.
- Dependencies: PVB-H3-RESEARCH-03.
- Approval requirement: approval before connector implementation.
- Suggested owner/agent: scientific_validation_agent.
- Risk level: High.
- Notes for implementation: Use as evidence input, not decision authority.

## PVB-H3-MCP-06-design-perplexity-research

- Title: Design Perplexity market and web research workflow.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P3.
- Objective: Design how Perplexity could support current web and market research.
- Why this matters: Market information changes and may require current sources.
- Source rationale: Prompt explicitly requires Perplexity workflow planning.
- C.O.N.T.R.O.L.E. dimensions supported: O, R, L.
- Included scope: research prompts, source citation expectations, freshness checks, synthesis outputs.
- Excluded scope: live web automation or current claims without verification.
- Deliverables: Perplexity workflow design.
- Acceptance criteria: design requires source links, dates, and confidence labels.
- GO conditions: market research workflow exists.
- NO-GO conditions: source quality rules are absent.
- Dependencies: PVB-H3-RESEARCH-02, PVB-H3-RESEARCH-07.
- Approval requirement: approval before connector use.
- Suggested owner/agent: market_intelligence_agent.
- Risk level: Medium.
- Notes for implementation: Avoid using current web data as sole proof of demand.

## PVB-H3-RESEARCH-07-define-source-quality-and-citation-rules

- Title: Define source quality and citation rules.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2.
- Objective: Define how sources are ranked, cited, dated, and challenged.
- Why this matters: Automated research is only useful if source quality is visible.
- Source rationale: Prompt requires source citation and evidence quality scoring.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: source tiers, freshness, conflicts, citation format, confidence labels.
- Excluded scope: guaranteeing truth or replacing expert review.
- Deliverables: source quality rules.
- Acceptance criteria: every research output can show source type, date, confidence, and risk if wrong.
- GO conditions: research orchestrator design is approved.
- NO-GO conditions: sources are summarized without traceability.
- Dependencies: PVB-H3-RESEARCH-01.
- Approval requirement: human review.
- Suggested owner/agent: research_orchestrator.
- Risk level: Medium.
- Notes for implementation: Keep source log simple.

## PVB-H3-RESEARCH-08-add-evidence-scoring-system

- Title: Add evidence scoring system.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2.
- Objective: Score evidence strength across customer, market, scientific, usage, and synthetic inputs.
- Why this matters: Not all evidence should influence decisions equally.
- Source rationale: Prompt requires evidence scoring and idea ranking inputs.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: evidence type, source quality, recency, directness, confidence, contradiction handling.
- Excluded scope: automated final decisions.
- Deliverables: evidence scoring template.
- Acceptance criteria: customer evidence outranks synthetic or generic research for demand validation.
- GO conditions: source quality rules exist.
- NO-GO conditions: scoring hides uncertainty.
- Dependencies: PVB-H3-RESEARCH-07.
- Approval requirement: human review before ranking use.
- Suggested owner/agent: research_orchestrator and knowledge_curator.
- Risk level: Medium.
- Notes for implementation: Use advisory scores only.

## PVB-H3-RESEARCH-09-add-research-synthesis-template

- Title: Add research synthesis template.
- Milestone: Automated Discovery MCP.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2.
- Objective: Convert research into decision-ready synthesis.
- Why this matters: Raw research does not help execution unless it changes assumptions, validation, or scope.
- Source rationale: Baseline requires source logs and research synthesis.
- C.O.N.T.R.O.L.E. dimensions supported: C, L, E.
- Included scope: question, sources, findings, confidence, implications, risks if wrong, next test.
- Excluded scope: long literature review by default.
- Deliverables: research synthesis template.
- Acceptance criteria: synthesis outputs update validation, PRD, KDR, or backlog.
- GO conditions: evidence scoring exists.
- NO-GO conditions: synthesis has no decision implication.
- Dependencies: PVB-H3-RESEARCH-08.
- Approval requirement: human review for strategic changes.
- Suggested owner/agent: research_orchestrator.
- Risk level: Medium.
- Notes for implementation: Require "what changed?" field.

## PVB-H3-RANK-10-design-idea-ranking-engine

- Title: Design idea ranking engine.
- Milestone: Idea Ranking & Idea Browser Validation.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2/P3.
- Objective: Define how ideas are ranked using structured evidence and C.O.N.T.R.O.L.E.
- Why this matters: Ranking helps prioritize without turning backlog size into strategy.
- Source rationale: Prompt requires idea ranking by persona, problem, willingness to pay, channel, competition, country/city, regulation, MVP speed, founder advantage, context potential, distribution, evidence, and C.O.N.T.R.O.L.E.
- C.O.N.T.R.O.L.E. dimensions supported: C, O, N, T, R, O, L, E.
- Included scope: dimensions, weights, confidence, evidence requirements, tie-breakers.
- Excluded scope: automated product selection without human approval.
- Deliverables: idea ranking engine design.
- Acceptance criteria: ranking includes confidence and cannot override C.O.N.T.R.O.L.E. kill/pivot decisions without review.
- GO conditions: evidence scoring exists.
- NO-GO conditions: ranking lacks evidence traceability.
- Dependencies: PVB-H3-RESEARCH-08.
- Approval requirement: human approval before prioritization decisions.
- Suggested owner/agent: venture_intelligence_curator.
- Risk level: Medium/High.
- Notes for implementation: First version can be a spreadsheet-like rubric.

## PVB-H3-INTEL-11-design-market-signal-ingestion

- Title: Design market signal ingestion.
- Milestone: Market Signal Intelligence.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2/P3.
- Objective: Define how external signals become structured opportunity evidence.
- Why this matters: Signals can reveal opportunities, but noise must not drive execution.
- Source rationale: Prompt requires future market signal ingestion.
- C.O.N.T.R.O.L.E. dimensions supported: C, O, L.
- Included scope: signal source, date, geography, persona, market maturity, channel fit, confidence, link to idea ranking.
- Excluded scope: live scraping, automatic ticket creation, BuilderPulse implementation.
- Deliverables: market signal ingestion template.
- Acceptance criteria: signals are tagged, sourced, and routed into ranking or research synthesis.
- GO conditions: source quality rules exist.
- NO-GO conditions: unsourced signals change roadmap.
- Dependencies: PVB-H3-RESEARCH-07.
- Approval requirement: human review before roadmap changes.
- Suggested owner/agent: market_intelligence_agent.
- Risk level: Medium.
- Notes for implementation: BuilderPulse monitoring can use this later.

## PVB-H3-RESEARCH-12-add-human-approval-for-research-decisions

- Title: Add human approval gates for research-driven decisions.
- Milestone: Hardening, Documentation & Operating Manual.
- Horizon: H3 - Intelligence / Discovery Automation.
- Priority: P2.
- Objective: Ensure research automation cannot directly trigger build, outreach, billing, or claims.
- Why this matters: Automated discovery increases risk of false certainty.
- Source rationale: Prompt requires human review before decisions.
- C.O.N.T.R.O.L.E. dimensions supported: R, E.
- Included scope: approval matrix for research-driven changes, sensitive claims, external actions.
- Excluded scope: blocking read-only research summaries.
- Deliverables: research decision approval gate.
- Acceptance criteria: research can recommend, but humans approve execution.
- GO conditions: MCP/research workflows are designed.
- NO-GO conditions: automated research creates tickets or contacts customers.
- Dependencies: PVB-H3-RESEARCH-01 through PVB-H3-RESEARCH-09.
- Approval requirement: explicit human approval.
- Suggested owner/agent: risk_reviewer.
- Risk level: High.
- Notes for implementation: Tie to AGENTS.md approval gates.
