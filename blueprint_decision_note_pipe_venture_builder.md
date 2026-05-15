# Pipe Venture Builder Blueprint Decision Note

Date: 2026-05-14
Ticket: PIP-57
Status: Approved for execution

## Decision

Use the existing Pipe Venture Builder baseline as the source of truth and adopt only targeted incremental improvements from the later analyses.

The approved direction is a reusable, Linear-governed base repository for moving venture ideas from intake to validated MVP planning. The system should stay narrow in the first execution wave: repository foundation, C.O.N.T.R.O.L.E. gate, validation, MVP scope, Linear governance, and first trial readiness.

## Sources Reconciled

- `/Users/vnatividade/Downloads/previous_pipe_venture_builder_analysis.md`
- `pipe_venture_builder_incremental_analysis.md`
- `linear_execution_plan_pipe_venture_builder.md`
- `linear_ticket_creation_order.md`

## Accepted Deltas

- Keep `pipe-venture-builder` template-first and product-agnostic.
- Preserve C.O.N.T.R.O.L.E. as a mandatory strategic gate before PRD, MVP, growth, monetization, or build work.
- Add a stronger solo-founder lens: one target market, one problem, one offer, one channel, and one focused execution path before expansion.
- Add validation scorecards, customer discovery memory, ICP language capture, and GO/NO-GO gates before implementation.
- Add lightweight MVP discipline around the smallest ethical test of the riskiest business assumption.
- Add compact agent/skill contracts later, using focused operators instead of a broad master agent.
- Add KDR/DAR-style decision memory and conflict/supersession rules after the foundation layer.
- Use Linear as the execution governance plane with one ticket, one branch, and one PR.
- Track research, discovery MCPs, market intelligence, growth, and synthetic persona work as future/backlog unless explicitly promoted.

## Rejected Imports

- Do not import the full `solo-founder-superpowers-main` skill library.
- Do not import the full `product-architect-main` agent system.
- Do not create a master agent that owns the whole venture-builder flow.
- Do not bring paid acquisition, billing implementation, automated outreach, or production deployment into the MVP foundation.
- Do not treat synthetic personas, Idea Browser signals, BuilderPulse signals, or web research as substitutes for real customer evidence.
- Do not build advanced MCP integrations before the core validation and governance flow is proven.

## MVP Boundary

The MVP/foundation path includes:

- base repository skeleton;
- README and operating manual;
- AGENTS.md and approval gates;
- core venture pipeline map;
- product context template;
- C.O.N.T.R.O.L.E. template;
- founder focus template;
- validation scorecard;
- customer discovery and ICP memory;
- MVP core loop and scope gate;
- Linear governance model;
- ticket, PR, and handoff workflow;
- first product trial protocol.

The MVP/foundation path excludes:

- full agent implementation;
- full skill marketplace;
- research MCP automation;
- venture intelligence memory layer;
- market signal ingestion;
- synthetic persona generation;
- growth automation;
- billing/payment implementation;
- product-specific implementation.

## First Execution Sequence

The approved first execution sequence is:

1. PIP-57 - Consolidate blueprint delta into approved execution plan.
2. PIP-58 - Confirm project before issues.
3. PIP-53 - Create base repository skeleton.
4. PIP-59 - Write README and operating manual.
5. PIP-60 - Define AGENTS.md and approval gates.
6. PIP-61 - Map core venture pipeline.
7. PIP-62 - Define product context template.
8. PIP-54 - Add C.O.N.T.R.O.L.E. gate template.
9. PIP-55 - Add founder focus template.
10. PIP-63 - Add validation scorecard and pressure-test questions.
11. PIP-64 - Add customer discovery and ICP memory.
12. PIP-56 - Add MVP core loop and scope gate.
13. PIP-65 - Define Linear governance model.
14. PIP-66 - Add ticket, PR, and handoff system.
15. PIP-67 - Define first product trial protocol.

## P0/P1 Boundary

P0 work is required to make the repository usable and governable. P0 should remain focused on foundation, validation gates, MVP scope, and Linear execution governance.

P1 work improves repeatability after the foundation is usable. P1 should include deeper agent contracts, skill contracts, knowledge memory, architecture templates, template/fork automation, and hardening.

P2/P3 work should remain visible but should not block the foundation path.

## Open Decisions

- Whether legacy Linear milestones should be merged, archived, or left as historical context.
- Whether first-class Linear dependency links should be added after the ticket order is reviewed.
- Whether Codex automatic review should be enabled for the GitHub repository.
- Which Horizon 2 item should be promoted immediately after H1 foundation stabilizes.

## Ready For Execution

The blueprint is ready for execution under the following constraints:

- Execute one Linear ticket per branch and PR.
- Keep PR scope aligned to the linked Linear ticket.
- Require review before merge.
- Correct P0/P1 review findings before merge.
- Create Linear follow-up tickets for relevant out-of-scope findings.
- Do not execute external, billing, customer, production, legal, financial, compliance, or sensitive actions without explicit approval.
