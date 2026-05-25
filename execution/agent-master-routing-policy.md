# Agent Master Routing Policy

This policy defines Agent Master as a non-executable routing and governance protocol for the Pipe Venture Builder.

Use it with `AGENTS.md`, `execution/core-pipeline-map.md`, `execution/linear-ticket-template-v2.md`, `execution/agent-readiness-validator.md`, `execution/approval-gates.md`, `execution/context-routing-protocol.md`, `execution/parallel-execution-governance.md`, `execution/worktree-isolation-protocol.md`, and `architecture/executor-capability-matrix.md`.

Agent Master is not an autonomous executor, not a background runtime, not a super-agent, and not a replacement for Linear, GitHub, PR review, human approval, or repository policy.

## Core Decision

Agent Master is a decision protocol that answers:

- what stage the work is in
- whether the work can proceed
- what artifact or ticket should exist next
- which executor or capability is appropriate
- which approval or blocker must be resolved first
- what should be recorded for future agents

Agent Master must not:

- implement code
- edit files directly
- create Linear tickets without approval
- open or merge PRs without approval
- install OpenClaw, Paperclip, MCPs, or runtime tooling
- dispatch agents autonomously
- contact customers
- handle secrets, credentials, production data, or customer data
- create unsupported customer, revenue, validation, metric, compliance, or integration claims

## Source Of Truth

| Area | Source of truth | Agent Master responsibility |
|---|---|---|
| Stage and venture flow | `execution/core-pipeline-map.md` | Identify current stage and next valid transition. |
| Execution state | Linear | Read status, priority, blockers, dependencies, approval, owner, and handoff. |
| Ticket readiness | `execution/agent-readiness-validator.md` | Classify as `READY`, `READY WITH APPROVAL`, `NOT READY`, or `BLOCKED`. |
| Ticket shape | `execution/linear-ticket-template-v2.md` | Check whether required routing fields exist. |
| Approval gates | `execution/approval-gates.md` and `AGENTS.md` | Stop before gated actions unless approval is explicit and scoped. |
| Executor routing | `architecture/executor-capability-matrix.md` | Recommend Codex, Claude Code, human operator, or future placeholder. |
| Context routing | `execution/context-routing-protocol.md` | Recommend smallest read-first context by ticket type. |
| Parallel safety | `execution/parallel-execution-governance.md` and `execution/worktree-isolation-protocol.md` | Decide whether work should be serialized, partial, or parallelizable. |

Agent Master may recommend an action. It must not treat recommendation as permission.

## Stage Transitions

Agent Master follows the venture pipeline from idea to learning.

| Stage | Required input | GO condition | NO-GO condition | Next routed action |
|---|---|---|---|---|
| 1. Idea intake | Raw idea, founder note, or opportunity signal | Target user, problem, promise, assumptions, and unknowns can be stated without invented evidence | Idea is too vague, implies sensitive claims, or requires external action before framing | Route to founder focus or request intake clarification. |
| 2. Founder focus | Idea intake artifact | One market, one problem, one offer, one channel, and anti-goals are explicit | Multiple unrelated markets/offers/channels remain active | Route to C.O.N.T.R.O.L.E. evaluation or keep narrowing. |
| 3. C.O.N.T.R.O.L.E. evaluation | Founder focus and assumptions | Verdict is Attack or Refine with rationale and validation implication | Verdict is Pivot/Kill or rationale is missing | Route to research/validation plan, pivot, or stop. |
| 4. Research and validation plan | C.O.N.T.R.O.L.E. verdict and unknowns | Questions, evidence needs, discovery plan, and validation scorecard path exist | Customer outreach or external research would happen without approval or source discipline | Route to research/validation tickets or approval request. |
| 5. Working Backwards | Validated problem framing | Promise, FAQ, constraints, and non-goals are traceable to evidence or assumptions | Claims are unsupported or too broad | Route to PRD or return to validation. |
| 6. PRD | Working Backwards and validation context | Requirements, user journeys, scope, constraints, assumptions, and evidence links are explicit | PRD implies build before validation or broadens MVP | Route to MVP scope review or revise PRD. |
| 7. MVP scope review | PRD, anti-goals, validation evidence | Core loop, riskiest assumption, cut list, and GO/NO-GO threshold are explicit | MVP is a platform, broad roadmap, or lacks evidence threshold | Route to risk review or narrow scope. |
| 8. Risk review | MVP scope and sensitive areas | P0/P1 risks are mitigated, accepted by human, or converted into blockers | Secrets, production, customer data, billing, legal/compliance, or external action risk is unresolved | Route to architecture or block. |
| 9. Architecture | MVP scope and risk review | Minimum viable technical shape and constraints are defined | Architecture overbuilds, chooses future runtime prematurely, or lacks risk boundaries | Route to Linear project confirmation or architecture follow-up. |
| 10. Linear project confirmation | Approved product scope and execution plan | Project exists or human approves creation | Project/ticket creation approval is missing | Route to ticket creation only after approval. |
| 11. Ticket creation | Approved scope, architecture, project | Ticket can be created with template v2 fields and dependencies | Ticket would be broad, vague, unapproved, or future-only | Draft ticket for approval or stop. |
| 12. Ticket readiness | Existing Linear ticket | Validator result is `READY` or approved `READY WITH APPROVAL` | Result is `NOT READY` or `BLOCKED` | Route to assigned executor, fix ticket, request approval, or block. |
| 13. Ticket execution | Ready approved ticket | One owner, one branch, one PR, validation, review, and handoff are clear | Write set conflicts, approval missing, or P0/P1 risk unresolved | Route to Codex/Claude/human or serialize. |
| 14. Feedback and learning | PR, validation, trial, or review result | Learning is traceable and recorded in the right artifact or Linear handoff | Learning contains unsupported claims or requires customer/production data without approval | Route to knowledge update, follow-up, pivot, or stop. |

## Routing Outputs

Every Agent Master routing decision should produce:

- current stage
- recommended next stage
- readiness result
- recommended executor or owner
- required source artifact
- expected ticket type
- expected write set, when branch work is involved
- approval required before next action
- GO/NO-GO rationale
- blocker or follow-up recommendation

Minimal format:

```md
## Agent Master routing decision

Current stage:
Recommended next stage:
Readiness:
Recommended executor:
Recommended ticket type:
Required artifact:
Expected write set:
Approval required before:
GO rationale:
NO-GO / blocker:
Follow-up recommendation:
```

## Executor And Capability Selection

Agent Master chooses an executor by reading the ticket type, risk, write set, approval requirement, validation plan, and stage.

Use this order:

1. If the next action is approval, sensitive judgment, customer contact, pricing, legal/compliance/security claims, production, billing, paid acquisition, or external communication, route to the human operator.
2. If the next action is repository-grounded execution with GitHub/Linear lifecycle, route to Codex by default unless the ticket names Claude Code or another executor.
3. If the next action is a scoped code/documentation task with clear write set and no high-risk shared file, Claude Code is acceptable.
4. If the next action touches shared high-risk files, serialize and assign one owner.
5. If the next action needs a future runtime, orchestrator, OpenClaw, Paperclip, MCP, scheduled agent, or production-like automation, do not execute. Route to future evaluation or block.

Agent Master may recommend capabilities such as research synthesis, validation planning, risk review, ticket orchestration, or knowledge curation, but the capability must be supported by an approved ticket and existing repository protocol.

## Stop Conditions

Stop when:

- approval is required and missing
- ticket readiness is `NOT READY` or `BLOCKED`
- the work would create Linear projects or tickets without approval
- the work would open or merge a PR without approval
- the work would deploy, schedule, or run production-like automation
- the work would handle secrets, credentials, production data, customer data, or private operational data
- the work would contact customers or send external communications
- the work would change legal, financial, compliance, privacy, security, or sensitive claims
- the work would invent evidence, metrics, customers, revenue, integrations, or validation
- the proposed executor would edit a shared high-risk file without serialized ownership
- the proposed action belongs to future orchestration rather than the current approved ticket

When stopped, Agent Master should record:

- blocker type
- source of blocker
- required approval or artifact
- recommended owner
- unblock condition
- whether a follow-up ticket should be drafted for approval

## Approval Gates

Agent Master must apply `execution/approval-gates.md` before routing to execution.

Approval must be explicit and scoped. Acceptable approval sources are the same sources defined in `execution/approval-gates.md`:

- current user thread
- assigned Linear ticket

Do not treat silence, prior memory, or inferred intent as approval.

If approval exists only in conversation and future agents need it, record it in Linear or the PR handoff as supporting traceability. The durable record explains the approval; it does not create a new approval source by itself.

## GO / NO-GO Decision Rules

Use `GO` only when:

- the current stage has required inputs
- the next stage is allowed by `execution/core-pipeline-map.md`
- approval state is clear
- evidence and assumptions are separated
- ticket readiness supports the next action
- executor ownership and write set are clear
- no unresolved P0/P1 risk blocks progress

Use `CONDITIONAL GO` when:

- the work can proceed only after a named approval, dependency, or blocker is resolved
- the condition is explicit enough for Linear tracking

Use `NO-GO` when:

- the next action would skip validation, approval, risk review, or required artifacts
- the work is broad platform/orchestration/runtime expansion before baseline readiness
- the work relies on unsupported evidence or sensitive claims
- the execution owner, write set, or approval requirement is ambiguous

## Manual Validation Against Existing Flows

### Flow A - Product Flow

Example: idea to PRD or MVP scope.

Routing result:

- Current stage: product or validation.
- Required artifacts: founder focus, C.O.N.T.R.O.L.E., validation scorecard, Working Backwards, PRD/MVP scope depending on stage.
- Recommended owner: human operator plus Codex or validation/product agent for artifact drafting.
- GO: only when evidence/assumptions are separated and the next stage does not create build tickets prematurely.
- NO-GO: if customer claims, willingness-to-pay, integrations, or market proof are invented.

### Flow B - Documentation / Governance Flow

Example: a worktree isolation protocol update or an executor capability matrix update.

Routing result:

- Current stage: execution governance.
- Required artifacts: assigned Linear ticket, relevant execution/architecture docs, approval state, expected write set.
- Recommended executor: Codex or Claude Code, with serialized ownership for shared high-risk files.
- GO: when the ticket is narrow, document-only, and validation can be manual plus `diff --check` and targeted search.
- NO-GO: if the change alters approval gates, branch protection, or runtime dispatch outside scope.

### Flow C - Implementation-Ready Flow

Example: future code or automation ticket after validation and architecture.

Routing result:

- Current stage: ticket readiness or ticket execution.
- Required artifacts: approved Linear ticket, DoR/DoD, validation plan, expected write set, risk review, market-validation gate when product-facing.
- Recommended executor: Codex or Claude Code based on `architecture/executor-capability-matrix.md`.
- GO: when dependencies, approval, tests/checks, and ownership are clear.
- NO-GO: if implementation starts before validation, handles secrets/customer/production data without approval, or lacks review path.

## Future Orchestrator Boundary

Future Hermes, OpenClaw, Paperclip, or another orchestrator may consume this policy only after the Codex + Claude Code baseline is stable and an approved orchestration-prep ticket authorizes evaluation.

Until then:

- Agent Master is a protocol, not software.
- Routing decisions are made by humans or assigned agents.
- Runtime dispatch is out of scope.
- OpenClaw/Paperclip remain future placeholders.

## Monitoring Signals

Track these signals in Linear handoffs and future operations metrics:

- routing decision made without durable record
- ticket moved to execution while `NOT READY` or `BLOCKED`
- executor changed because write set or risk changed
- approval needed but missing at branch, PR, merge, or external-action step
- follow-up drafted because stage transition was unclear
- future-runtime work attempted before orchestration-prep approval
- sensitive claim or evidence gap caught before execution

## Done Criteria

This policy is working when:

- Agent Master is treated as a routing/governance protocol, not an executor
- stage transitions from idea to learning have GO/NO-GO conditions
- routing decisions link back to Linear template, readiness validator, and approval gates
- executor choice uses the capability matrix instead of vague preference
- future runtime/orchestrator work remains deferred
- blockers and approvals are recorded where future agents can find them
