# Hardening Audit

This audit reviews the current template for bloat, duplication, premature scope, approval-gate drift, and future-work separation.

It is a report only. It does not delete approved files, rewrite core governance, or promote later-stage automation into the MVP path.

## Scope

- Duplicate checks across product, validation, architecture, execution, knowledge, setup, agents, skills, and planning files.
- Stage-order review for strategy, validation, MVP, architecture, Linear, execution, learning, growth, monetization, and future intelligence work.
- Approval-gate review for PRs, Linear mutations, production, billing, ads, outreach, secrets, customer data, and sensitive claims.
- Future backlog separation for MCP, BuilderPulse, Idea Browser, synthetic persona, growth, billing, and venture intelligence work.

## Inventory Snapshot

| Area | Snapshot | Recommendation |
|---|---|---|
| Core repository docs | `README.md`, `AGENTS.md`, `setup/operating-manual.md`, `execution/core-pipeline-map.md` define the operating spine. | Keep. |
| Product and validation templates | Founder focus, C.O.N.T.R.O.L.E., ICP, validation scorecard, customer interviews, PRD, and MVP scope are stage-specific. | Keep. |
| Architecture templates | Architecture review, ADR, RFC, engineering standards, and decision guide are lightweight and versionable. | Keep. |
| Execution governance | Linear governance, approval gates, risk reviewer, ticket orchestration, handoff, and readiness validator overlap by design but serve different execution moments. | Keep, monitor for drift. |
| Knowledge layer | KDR/DAR, conflict protocol, curator workflow, customer language memory, and README are distinct surfaces. | Keep. |
| Agent and skill contracts | Core agent and skill contracts are long but centralized and additive. | Adapt later only if agents become hard to route. |
| Linear planning exports | Horizon files, execution plan, creation summary, and ticket order are historical planning artifacts. | Keep as source history unless a future archive ticket approves moving them. |
| Growth, monetization, research placeholders | Placeholder READMEs keep later-stage areas visible without implementation. | Keep. |

## Duplicate Checks

| Topic | Files checked | Finding | Recommendation |
|---|---|---|---|
| Approval gates | `AGENTS.md`, `execution/approval-gates.md`, `setup/operating-manual.md`, `execution/linear-governance-model.md` | Repeated intentionally across operator-facing docs. No material contradiction found. | Keep canonical policy in `execution/approval-gates.md`; update references when policy changes. |
| PR and ticket workflow | `execution/ticket-pr-handoff-system.md`, `execution/linear-governance-model.md`, `setup/operating-manual.md` | Some repetition, but each doc serves a different altitude: policy, detailed workflow, quick operator path. | Keep. |
| Risk severity | `execution/approval-gates.md`, `execution/risk-reviewer-matrix-lite.md`, PR handoff docs | Severity language is consistent enough: P0/P1 block, P2 selective, P3 non-blocking. | Keep; avoid adding new severity definitions elsewhere. |
| Knowledge decisions | `knowledge/kdr-dar-template.md`, `knowledge/decision-conflict-protocol.md`, `architecture/adr/adr-template.md` | Strategic and technical decision records are separated. | Keep. |
| Agent contracts | `.codex/agents/core-agent-contracts.md`, `.agents/skills/core-skill-contracts.md` | Long files may feel heavy, but they avoid many scattered agent fragments. | Adapt later only if routing becomes confusing. |

## Stage-Order Review

| Stage | Current gate | Finding | Recommendation |
|---|---|---|---|
| Idea and founder focus | `product/product-context.md`, `product/founder-focus.md` | Focus precedes validation and build. | Keep. |
| Strategic evaluation | `product/controle-evaluation.md` | Required before PRD, tickets, growth, monetization, or build work. | Keep. |
| Validation | `validation/validation-scorecard.md`, `validation/icp-profile.md` | Blocks PRD/build when evidence is weak or synthetic-only. | Keep. |
| MVP scope | `product/mvp-scope.md` | Defines core loop, riskiest assumption, cuts, and ticket boundary. | Keep. |
| PRD and architecture | `product/prd.md`, `architecture/architecture-review.md` | PRD and architecture depend on validation and MVP scope. | Keep. |
| Execution | `execution/linear-governance-model.md`, `execution/ticket-pr-handoff-system.md` | Requires one ticket, branch, PR, review, and merge handoff. | Keep. |
| Learning | `knowledge/knowledge-curator-workflow.md`, `knowledge/kdr-dar-template.md` | Captures decisions and learning after cycles. | Keep. |
| Growth and monetization | `growth/README.md`, `monetization/README.md` | Present as later-stage placeholders; no implementation. | Keep as deferred surfaces. |

No stage-order violation found in current active templates.

## Approval-Gate Review

| Gate | Finding | Recommendation |
|---|---|---|
| Linear project/ticket creation | Approval required in `AGENTS.md`, `execution/approval-gates.md`, and Linear governance. | Keep. |
| PR opening and merge | Approval required in policy, but current thread has explicit standing approval for this execution cycle. | Keep policy; document thread approval in handoffs when used. |
| Production deployment | Explicitly blocked without approval. No production workflow found. | Keep. |
| Secrets and credentials | Explicitly blocked. Setup workflow and validation docs forbid storing secrets. | Keep. |
| Customer data | Data retention and knowledge docs require minimization and approval. | Keep. |
| Billing, paid ads, outreach | Explicitly deferred and approval-gated. | Keep. |
| Sensitive claims | Repeatedly blocked without source artifacts. | Keep. |

No unapproved approval-gate weakening found.

## Future Backlog Separation

| Later-stage area | Current location | Finding | Recommendation |
|---|---|---|---|
| MCP discovery | Horizon 3 and 5 planning files | Tracked as design/backlog; no live credentials or connector use in repo. | Keep in backlog. |
| NotebookLM, Consensus, Perplexity | Horizon planning files | Planned as future workflows, not live automation. | Keep in backlog. |
| BuilderPulse monitoring | Horizon 5 planning files | Future monitoring design only. | Keep in backlog. |
| Idea Browser ranking | Horizon 3/4/5 planning files | Advisory validation input only; does not replace interviews. | Keep in backlog. |
| Synthetic personas | Horizon 5 planning files plus guardrails in validation docs | Treated as hypothesis material, not evidence. | Keep in backlog with strict evidence labels. |
| Growth and distribution | Placeholder docs and horizon files | Deferred until validation evidence exists. | Keep deferred. |
| Billing and monetization | Placeholder docs and horizon files | Pricing hypothesis separated from billing implementation. | Keep deferred and approval-gated. |

No unapproved later-stage automation is active in the repository.

## Keep / Adapt / Remove Recommendations

| Recommendation | Items | Rationale |
|---|---|---|
| Keep | Core stage templates, approval gates, Linear governance, risk review, ticket handoff, KDR/DAR, architecture review, ADR/RFC/standards, setup workflow. | These are foundational and stage-specific. |
| Keep | Horizon planning files and blueprint analysis files. | They explain ticket provenance and prevent future agents from relying on conversation memory. |
| Adapt later | Agent and skill contract files if routing becomes hard after first product trial. | They are the largest operator docs, but still centralized and useful. |
| Adapt later | Historical Linear planning exports after all linked tickets are completed. | They may be archive candidates once the execution record lives fully in Linear and merged docs. |
| Remove later only with approval | Any duplicate historical planning artifact that no longer adds traceability. | Removal is outside this ticket and requires human approval. |

## Risks And Follow-Up Candidates

| Risk | Severity | Recommendation |
|---|---|---|
| Agent/skill contracts may grow into routing bloat after specialization tickets. | P2 | Reassess during existing PIP-81/PIP-82/PIP-83 specialization work. |
| Historical planning files may become stale after all foundation and operationalization tickets are complete. | P2 | Reassess during a future archive/cleanup ticket, not now. |
| Future-intelligence backlog could tempt premature MCP or synthetic-persona execution. | P2 | Keep future tickets explicitly advisory and approval-gated. |

No new follow-up ticket is required from this audit because the identified risks are already covered by existing backlog areas or require future human approval before action.

## Final Verdict

- Overall status: Clear with monitoring.
- Broad rewrite needed: no.
- Approved removals needed now: no.
- Unapproved later-stage automation found: no.
- Stage-order violation found: no.
- Approval-gate weakening found: no.
- Next recommended action: proceed to the remaining prioritized backlog without deleting approved files.
