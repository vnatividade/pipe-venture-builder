# Linear Ticket Creation Order

This file defines the recommended order for creating tickets and dependencies in Linear. It was written as a pre-execution planning artifact and assumes no Linear items are created until the user explicitly approves Linear mutation.

Current execution note: Linear creation was later authorized and completed. Use this file as the ordering/dependency map, not as the current status record.

## 1. Pre-Flight

1. Search for existing `pipe-venture-builder` Linear projects.
2. Confirm the target project or create the project only with explicit approval.
3. Create labels.
4. Create milestones.
5. Create H1 P0 tickets.
6. Create H1 P1 and H2 P1 tickets.
7. Create H3/H4/H5 backlog tickets only after the immediate MVP path is visible.

## 2. Label Creation Order

1. Horizon labels.
2. Priority labels.
3. Work type labels.
4. Owner/agent labels.
5. Risk labels.
6. Approval labels.
7. Source area labels.

## 3. Milestone Creation Order

1. Blueprint Consolidation.
2. Base Repository Foundation.
3. Core Agent System.
4. Validation & Discovery Pipeline.
5. Product Architecture Pipeline.
6. Linear Governance Workflow.
7. Knowledge Base & Memory Layer.
8. First Product Trial Run.
9. Agent/Skill Specialization.
10. Automated Discovery MCP.
11. Market Signal Intelligence.
12. Idea Ranking & Idea Browser Validation.
13. Synthetic Persona Validation.
14. Distribution & Growth System.
15. Template/Fork Automation.
16. Hardening, Documentation & Operating Manual.

## 4. H1 Creation Order

| Order | Ticket | Depends on |
|---:|---|---|
| 1 | PVB-H1-PLAN-01-consolidate-blueprint-delta | none |
| 2 | PVB-H1-LINEAR-01-confirm-project-before-issues | PVB-H1-PLAN-01 |
| 3 | PVB-H1-FOUND-02-create-base-repo-skeleton | PVB-H1-PLAN-01 |
| 4 | PVB-H1-FOUND-03-write-readme-and-operating-manual | PVB-H1-FOUND-02 |
| 5 | PVB-H1-FOUND-04-define-agents-md-and-approval-gates | PVB-H1-FOUND-03 |
| 6 | PVB-H1-FOUND-05-map-core-pipeline | PVB-H1-FOUND-04 |
| 7 | PVB-H1-FOUND-06-define-product-context-template | PVB-H1-FOUND-05 |
| 8 | PVB-H1-VALID-07-add-controle-gate-template | PVB-H1-FOUND-05 |
| 9 | PVB-H1-VALID-08-add-founder-focus-template | PVB-H1-VALID-07 |
| 10 | PVB-H1-VALID-09-add-validation-scorecard | PVB-H1-VALID-07, PVB-H1-VALID-08 |
| 11 | PVB-H1-VALID-10-add-customer-discovery-and-icp-memory | PVB-H1-VALID-09 |
| 12 | PVB-H1-MVP-11-add-mvp-core-loop-and-scope-gate | PVB-H1-VALID-09, PVB-H1-VALID-10 |
| 13 | PVB-H1-LINEAR-12-define-linear-governance-model | PVB-H1-FOUND-05, PVB-H1-MVP-11 |
| 14 | PVB-H1-EXEC-13-add-ticket-pr-handoff-system | PVB-H1-LINEAR-12 |
| 15 | PVB-H1-TRIAL-14-define-first-product-trial-protocol | PVB-H1-VALID-10, PVB-H1-MVP-11, PVB-H1-EXEC-13 |

## 5. H2 Creation Order

| Order | Ticket | Depends on |
|---:|---|---|
| 16 | PVB-H2-AGENT-01-define-core-agent-contracts | PVB-H1-FOUND-04, PVB-H1-FOUND-05 |
| 17 | PVB-H2-SKILL-02-define-core-skill-contracts | PVB-H2-AGENT-01 |
| 18 | PVB-H2-AGENT-03-define-trigger-rules | PVB-H2-AGENT-01, PVB-H2-SKILL-02 |
| 19 | PVB-H2-AGENT-04-define-agent-handoff-protocol | PVB-H2-AGENT-01 |
| 20 | PVB-H2-EXEC-05-add-agent-readiness-validator | PVB-H1-EXEC-13 |
| 21 | PVB-H2-RISK-06-define-risk-reviewer-and-risk-matrix | PVB-H1-FOUND-04 |
| 22 | PVB-H2-EXEC-07-define-ticket-orchestrator | PVB-H1-LINEAR-12 |
| 23 | PVB-H2-KNOW-08-define-knowledge-curator | PVB-H1-VALID-10, PVB-H1-EXEC-13 |
| 24 | PVB-H2-KNOW-09-add-kdr-dar-template | PVB-H2-KNOW-08 |
| 25 | PVB-H2-KNOW-10-add-decision-conflict-protocol | PVB-H2-KNOW-09, PVB-H2-RISK-06 |
| 26 | PVB-H2-ARCH-10-add-lean-prd-template | PVB-H1-MVP-11 |
| 27 | PVB-H2-ARCH-11-add-architecture-review-template | PVB-H2-ARCH-10 |
| 28 | PVB-H2-ARCH-12-add-adr-rfc-engineering-standards | PVB-H2-ARCH-11 |
| 29 | PVB-H2-AGENT-13-specialize-strategy-agents | PVB-H2-AGENT-01 |
| 30 | PVB-H2-AGENT-14-specialize-research-validation-agents | PVB-H1-VALID-09, PVB-H1-VALID-10 |
| 31 | PVB-H2-AGENT-15-specialize-execution-risk-agents | PVB-H1-EXEC-13, PVB-H2-RISK-06 |
| 32 | PVB-H2-TEMPLATE-16-define-template-fork-automation | PVB-H1-FOUND-05, PVB-H1-LINEAR-12 |
| 33 | PVB-H2-HARDEN-17-audit-bloat-and-duplication | H1 and key H2 templates |

## 6. H3 Creation Order

Create after H1 P0 and core H2 knowledge/risk tickets exist.

| Order | Ticket | Depends on |
|---:|---|---|
| 34 | PVB-H3-RESEARCH-01-design-research-orchestrator | PVB-H1-VALID-09, PVB-H2-KNOW-08 |
| 35 | PVB-H3-RESEARCH-02-define-market-research-workflow | PVB-H1-VALID-10 |
| 36 | PVB-H3-RESEARCH-03-define-scientific-validation-workflow | PVB-H2-RISK-06 |
| 37 | PVB-H3-RESEARCH-07-define-source-quality-and-citation-rules | PVB-H3-RESEARCH-01 |
| 38 | PVB-H3-RESEARCH-08-add-evidence-scoring-system | PVB-H3-RESEARCH-07 |
| 39 | PVB-H3-RESEARCH-09-add-research-synthesis-template | PVB-H3-RESEARCH-08 |
| 40 | PVB-H3-RANK-10-design-idea-ranking-engine | PVB-H3-RESEARCH-08 |
| 41 | PVB-H3-INTEL-11-design-market-signal-ingestion | PVB-H3-RESEARCH-07 |
| 42 | PVB-H3-MCP-04-design-notebooklm-discovery | PVB-H3-RESEARCH-01 |
| 43 | PVB-H3-MCP-05-design-consensus-validation | PVB-H3-RESEARCH-03 |
| 44 | PVB-H3-MCP-06-design-perplexity-research | PVB-H3-RESEARCH-02, PVB-H3-RESEARCH-07 |
| 45 | PVB-H3-RESEARCH-12-add-human-approval-for-research-decisions | PVB-H3 research and MCP designs |

## 7. H4 Creation Order

Create after validation, ICP, MVP, and knowledge loops are working.

| Order | Ticket | Depends on |
|---:|---|---|
| 46 | PVB-H4-GROWTH-01-define-distribution-strategy-framework | PVB-H1-VALID-10, PVB-H1-MVP-11 |
| 47 | PVB-H4-GROWTH-02-add-channel-experiment-template | PVB-H4-GROWTH-01 |
| 48 | PVB-H4-GROWTH-03-create-growth-experiment-backlog | PVB-H4-GROWTH-02 |
| 49 | PVB-H4-GROWTH-04-add-fake-door-landing-page-validation | PVB-H1-VALID-09, PVB-H1-VALID-10 |
| 50 | PVB-H4-GROWTH-05-define-content-strategy-agent | PVB-H4-GROWTH-01, PVB-H1-VALID-10 |
| 51 | PVB-H4-GROWTH-06-define-distribution-and-growth-agents | PVB-H4-GROWTH-02 |
| 52 | PVB-H4-GROWTH-07-add-founder-led-distribution-playbook | PVB-H4-GROWTH-01 |
| 53 | PVB-H4-GROWTH-08-add-launch-readiness-checklist | PVB-H1-MVP-11, PVB-H4-GROWTH-01 |
| 54 | PVB-H4-GROWTH-09-add-post-launch-learning-loop | PVB-H4-GROWTH-08, PVB-H2-KNOW-09 |
| 55 | PVB-H4-GROWTH-10-define-idea-browser-validation | PVB-H3-RANK-10 |
| 56 | PVB-H4-MONETIZATION-11-add-pricing-hypothesis-template | PVB-H1-VALID-09 |

## 8. H5 Creation Order

Create as backlog only unless explicitly promoted.

| Order | Ticket | Depends on |
|---:|---|---|
| 57 | PVB-H5-VI-01-monitor-builderpulse-publications | PVB-H3-INTEL-11 |
| 58 | PVB-H5-VI-02-contrast-builderpulse-with-ranking | PVB-H5-VI-01, PVB-H3-RANK-10 |
| 59 | PVB-H5-RANK-03-rank-ideas-by-persona | PVB-H1-VALID-10, PVB-H3-RANK-10 |
| 60 | PVB-H5-RANK-04-rank-ideas-by-country-city | PVB-H3-RESEARCH-02, PVB-H3-RANK-10 |
| 61 | PVB-H5-RANK-05-use-idea-browser-as-validation-input | PVB-H4-GROWTH-10 |
| 62 | PVB-H5-SYNTH-06-define-synthetic-persona-schema | PVB-H1-VALID-10 |
| 63 | PVB-H5-SYNTH-07-define-persona-generation-workflow | PVB-H5-SYNTH-06 |
| 64 | PVB-H5-SYNTH-08-define-persona-simulation-prompt | PVB-H5-SYNTH-07 |
| 65 | PVB-H5-SYNTH-09-extract-objections-and-risks | PVB-H5-SYNTH-08 |
| 66 | PVB-H5-SYNTH-10-compare-synthetic-output-to-real-interviews | PVB-H5-SYNTH-09, PVB-H1-VALID-10 |
| 67 | PVB-H5-VI-11-build-venture-intelligence-memory-layer | PVB-H2-KNOW-09, PVB-H3-RANK-10, PVB-H3-INTEL-11 |
| 68 | PVB-H5-VI-12-build-strategic-opportunity-radar | PVB-H5-VI-11 |
| 69 | PVB-H5-VI-13-define-synthetic-persona-agent | PVB-H5-SYNTH-06 through PVB-H5-SYNTH-10 |
| 70 | PVB-H5-VI-14-define-venture-intelligence-curator | PVB-H5-VI-11, PVB-H5-VI-12 |
| 71 | PVB-H5-MCP-15-plan-advanced-mcp-implementation-backlog | PVB-H3-MCP-04, PVB-H3-MCP-05, PVB-H3-MCP-06 |

## 9. First Linear Creation Batch

If the user authorizes actual Linear creation, create only this first batch initially:

1. Project.
2. Labels.
3. Milestones.
4. PVB-H1-PLAN-01.
5. PVB-H1-LINEAR-01.
6. PVB-H1-FOUND-02.
7. PVB-H1-FOUND-03.
8. PVB-H1-FOUND-04.
9. PVB-H1-FOUND-05.
10. PVB-H1-VALID-07.
11. PVB-H1-VALID-08.
12. PVB-H1-VALID-09.
13. PVB-H1-VALID-10.
14. PVB-H1-MVP-11.
15. PVB-H1-LINEAR-12.
16. PVB-H1-EXEC-13.

Keep H3/H4/H5 as backlog unless the user explicitly asks to create every planned issue.
