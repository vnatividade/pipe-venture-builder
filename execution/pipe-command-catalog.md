# Pipe Command Catalog

## Purpose

This catalog defines the spec-only `/pipe:*` command map for Pipe Venture Builder.

The commands are not executable slash commands, CLI commands, MCP tools, automations, or agent-dispatch instructions. They are stable operating contracts that future agents can use to understand the expected stage, inputs, outputs, routing, stop conditions, and next step.

Use this catalog with:

- `execution/core-pipeline-map.md`
- `execution/agent-master-routing-policy.md`
- `execution/context-routing-protocol.md`
- `execution/tactical-execution-plan.md`
- `execution/pipe-check-command-spec.md`
- `execution/approval-gates.md`
- `schemas/planning-schema-outlines.md`
- `schemas/DeliveryEvidence.schema.json`
- `schemas/LearningRecord.schema.json`

## Global Rules

Every `/pipe:*` command must:

- start from an assigned Linear ticket or a human-approved planning request
- preserve the repository as the source of truth for strategy, validation, architecture, and learning
- preserve Linear as the source of truth for execution state
- separate evidence, assumptions, unknowns, and decisions
- stop before gated actions without explicit approval
- avoid implementation before upstream gates are satisfied
- avoid creating unsupported customer, revenue, integration, metric, or validation claims
- record the expected next artifact or blocker

Every command in this catalog is spec-only until a later ticket explicitly authorizes implementation.

## Stage Map

| Command | Pipeline stage | Primary output | Next command |
|---|---|---|---|
| `/pipe:idea` | Idea intake | Focused idea brief or intake artifact | `/pipe:discover` |
| `/pipe:discover` | Founder focus and early framing | Founder focus, assumptions, unknowns, discovery questions | `/pipe:validate` |
| `/pipe:validate` | C.O.N.T.R.O.L.E., research, validation plan | Validation plan, scorecard, GO/NO-GO gate | `/pipe:prd` |
| `/pipe:prd` | Working Backwards and PRD | PRD and product requirements | `/pipe:plan` |
| `/pipe:plan` | MVP scope, risk review, architecture, ticket planning | MVP scope, risk review, architecture notes, Tactical Execution Plan, Linear-ready execution plan | `/pipe:build` |
| `/pipe:build` | Ticket execution | Branch, scoped changes, validation evidence | `/pipe:check` |
| `/pipe:check` | Delivery quality gate | Pass/fail/blocker quality result | `/pipe:review` |
| `/pipe:review` | PR review and findings handling | Review findings classified P0-P3 and fixes | `/pipe:ship` |
| `/pipe:ship` | Merge and release handoff | Merged PR, Linear delivery update, residual risk | `/pipe:learn` |
| `/pipe:learn` | Feedback and learning | LearningRecord candidate, KDR/DAR update, or no-learning note | Next iteration or stop |

## Command Contracts

### `/pipe:idea`

**Purpose:**
Convert a raw idea into a narrow, traceable idea intake artifact.

**Current artifacts:**
- `product/product-context.md`
- `product/founder-focus.md`
- `schemas/planning-schema-outlines.md`
- `execution/core-pipeline-map.md`

**Inputs:**
- Raw idea, founder note, market observation, or opportunity signal.
- Known target user, problem, promise, assumptions, and unknowns if available.

**Expected output:**
- One focused idea hypothesis.
- Initial target market and segment.
- One-sentence promise.
- Assumptions and unknowns.
- Evidence links or explicit evidence gap.
- Next gate recommendation.

**Required schema or outline:**
- `IdeaBrief` outline in `schemas/planning-schema-outlines.md`.

**Capability routing:**
- Human founder for source intent.
- Product strategist or Codex for repository-grounded artifact drafting.
- Do not use research tools unless the task explicitly includes source-backed research.

**GO conditions:**
- Idea can be stated as one problem, one target, one initial promise, and clear unknowns.
- No unsupported evidence claims are introduced.

**NO-GO conditions:**
- Idea is too broad to frame.
- Request implies external communication, customer outreach, billing, or production without approval.
- The command would create implementation tickets.

**Next stage:**
- `/pipe:discover`

### `/pipe:discover`

**Purpose:**
Narrow the idea into founder focus and discovery questions before validation.

**Current artifacts:**
- `product/founder-focus.md`
- `validation/icp-profile.md`
- `validation/customer-interview-template.md`
- `validation/customer-data-retention-policy.md`
- `execution/core-pipeline-map.md`

**Inputs:**
- Idea intake output.
- Founder constraints and anti-goals.
- Early ICP hypothesis.

**Expected output:**
- One market.
- One problem.
- One offer.
- One channel.
- Anti-goals and expansion constraints.
- Discovery questions and evidence gaps.
- Customer-data boundary.

**Required schema or outline:**
- `IdeaBrief` outline.
- Early `ValidationPlan` outline when discovery questions become testable.

**Capability routing:**
- Product strategist for narrowing.
- Validation lead for discovery question quality.
- Linear only for approved tracking, not for inventing evidence.

**GO conditions:**
- Focus is narrow enough for C.O.N.T.R.O.L.E. evaluation.
- Assumptions and evidence are separated.

**NO-GO conditions:**
- Multiple unrelated personas, markets, offers, or channels remain active.
- Customer outreach is required but not approved.
- Sensitive data handling is unclear.

**Next stage:**
- `/pipe:validate`

### `/pipe:validate`

**Purpose:**
Apply C.O.N.T.R.O.L.E., research planning, and market-validation gates before PRD or build work.

**Current artifacts:**
- `product/controle-evaluation.md`
- `validation/venture-validation-framework.md`
- `validation/validation-scorecard.md`
- `validation/market-validation-before-code-gate.md`
- `research/README.md`
- `research/consensus-validation-design.md`

**Inputs:**
- Founder focus.
- ICP hypothesis.
- Assumptions and unknowns.
- Existing research or validation evidence.

**Expected output:**
- C.O.N.T.R.O.L.E. verdict: Attack, Refine, Pivot, Kill, or not evaluated.
- Validation questions.
- Evidence needed.
- Research/source plan.
- Validation scorecard.
- GO, CONDITIONAL GO, REFINE, NO-GO, or NOT APPLICABLE gate.

**Required schema or outline:**
- `ValidationPlan` outline in `schemas/planning-schema-outlines.md`.

**Capability routing:**
- Validation lead or research synthesis capability when source-backed research is explicitly approved.
- Consensus or external research only when required by ticket and citation expectations.
- Human approval before outreach or external communications.

**GO conditions:**
- Evidence needs and blocked downstream actions are explicit.
- Gate decision is traceable and separates assumptions from evidence.

**NO-GO conditions:**
- Build, monetization, growth, billing, or outreach is requested before validation gate allows it.
- Market proof, willingness to pay, customer claims, or integrations are invented.

**Next stage:**
- `/pipe:prd` when gate allows.
- Otherwise refine, pivot, kill, or create validation follow-up.

### `/pipe:prd`

**Purpose:**
Translate validated problem framing into product requirements without broadening the MVP.

**Current artifacts:**
- `product/prd.md`
- `product/mvp-scope.md`
- `validation/validation-scorecard.md`
- `validation/market-validation-before-code-gate.md`
- `validation/icp-profile.md`

**Inputs:**
- Validation gate result.
- Evidence-backed ICP and problem framing.
- Working Backwards or launch narrative, if available.

**Expected output:**
- PRD with goals, non-goals, user stories, requirements, edge cases, constraints, risks, and acceptance criteria.
- Clear evidence links.
- Explicit unsupported assumptions.

**Required schema or outline:**
- `PRD` outline in `schemas/planning-schema-outlines.md`.

**Capability routing:**
- Product strategist for requirements.
- Risk reviewer when claims, data, billing, compliance, privacy, security, or external actions appear.

**GO conditions:**
- PRD ties requirements to validation evidence or explicit assumptions.
- Non-goals prevent platform sprawl.

**NO-GO conditions:**
- PRD treats assumptions as evidence.
- PRD expands MVP beyond validation.
- Sensitive or regulated claims are added without approval and source artifacts.

**Next stage:**
- `/pipe:plan`

### `/pipe:plan`

**Purpose:**
Convert PRD and MVP scope into risk-reviewed architecture and Linear-ready execution.

**Current artifacts:**
- `product/mvp-scope.md`
- `execution/core-pipeline-map.md`
- `execution/tactical-execution-plan.md`
- `execution/linear-ticket-template-v2.md`
- `execution/agent-readiness-validator.md`
- `execution/risk-reviewer-matrix-lite.md`
- `architecture/technical-decision-guide.md`
- `architecture/engineering-standards.md`

**Inputs:**
- PRD.
- MVP scope.
- Risk review inputs.
- Architecture constraints.

**Expected output:**
- MVP scope review.
- Risk review and mitigations.
- Minimum viable architecture direction.
- Tactical Execution Plan with ticket/story breakdown, ADR path, validation plan, observability needs, docs, and DeliveryEvidence expectations.
- Linear-ready ticket breakdown.
- Dependencies and blocked items.

**Required schema or outline:**
- `ExecutionPlan` outline in `schemas/planning-schema-outlines.md`.
- Linear ticket template fields from `execution/linear-ticket-template-v2.md`.

**Capability routing:**
- Agent Master routing policy for stage and owner.
- Architecture agent for technical shape.
- Risk reviewer for approval gates and sensitive areas.
- Linear governance only after ticket/project approval.

**GO conditions:**
- P0/P1 risks are mitigated, accepted, or converted into blockers.
- Tactical Execution Plan is complete or explicitly marked not applicable for the work.
- Linear project and ticket creation approval is clear.
- Tickets are small and sequenced.

**NO-GO conditions:**
- Implementation tickets are created before validation and MVP scope gates.
- Ticket set is broad, vague, or hides dependencies.
- Tactical Execution Plan is required but missing before development work.
- Project/ticket creation approval is missing.

**Next stage:**
- `/pipe:build`

### `/pipe:build`

**Purpose:**
Execute one approved Linear ticket in one branch and one PR.

**Current artifacts:**
- `AGENTS.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/tactical-execution-plan.md`
- `execution/multi-agent-operating-protocol.md`
- `execution/context-routing-protocol.md`
- `execution/worktree-isolation-protocol.md`
- `architecture/executor-capability-matrix.md`

**Inputs:**
- One approved Linear ticket.
- Tactical Execution Plan link, lightweight plan, or not-applicable reason.
- Expected write set.
- Acceptance criteria.
- Validation plan.
- Dependencies and approval state.

**Expected output:**
- Ticket-specific branch.
- Scoped repository changes.
- Validation commands and results.
- PR body with Linear reference, scope, exclusions, validation, risks, and handoff notes.

**Required schema or outline:**
- `DeliveryEvidence` when required by delivery risk or type.
- `LearningRecord` candidate when reusable learning appears.

**Capability routing:**
- Codex or Claude Code for repository-grounded execution.
- Serialize shared high-risk files.
- Use capability registry only when the ticket allows the capability category.

**GO conditions:**
- Ticket is ready.
- Tactical Execution Plan is present or not applicable.
- Scope and expected write set are clear.
- Approval exists for gated PR operations in the current cycle or ticket.

**NO-GO conditions:**
- Ticket is blocked or ambiguous.
- Work requires secrets, production data, customer data, external communication, billing, deployment, or sensitive claims without approval.
- Work crosses multiple tickets.

**Next stage:**
- `/pipe:check`

### `/pipe:check`

**Purpose:**
Run the manual delivery quality gate before review completion and merge.

**Current artifacts:**
- `execution/pipe-check-command-spec.md`
- `execution/test-oriented-delivery-rule.md`
- `execution/e2e-applicability-matrix.md`
- `schemas/DeliveryEvidence.schema.json`
- `schemas/LearningRecord.schema.json`

**Inputs:**
- Linear ticket.
- Branch and PR.
- Changed files.
- Acceptance criteria.
- Validation evidence.
- Review state.
- Residual risks and follow-ups.

**Expected output:**
- `/pipe:check` pass/fail/blocker result.
- Evidence summary by delivery type.
- Missing evidence and required follow-ups.
- Recommendation: ready for review, ready to merge, needs fixes, blocked, or not applicable.

**Required schema or outline:**
- `/pipe:check` output shape from `execution/pipe-check-command-spec.md`.

**Capability routing:**
- Execution agent can run manually.
- Reviewer should inspect evidence for P0/P1 gaps.

**GO conditions:**
- Acceptance criteria are mapped.
- Excluded scope is preserved.
- Validation evidence matches delivery type.

**NO-GO conditions:**
- Missing critical validation.
- Unresolved P0/P1 findings.
- Unsupported claims, approval gaps, or scope mismatch.

**Next stage:**
- `/pipe:review`

### `/pipe:review`

**Purpose:**
Review PR correctness, scope, tests/evidence, security, maintainability, and ticket alignment.

**Current artifacts:**
- `execution/ticket-pr-handoff-system.md`
- `execution/approval-gates.md`
- `execution/pipe-check-command-spec.md`

**Inputs:**
- PR URL.
- `/pipe:check` result.
- Changed files and validation evidence.
- Review comments.

**Expected output:**
- Findings classified P0, P1, P2, P3.
- Required fixes for P0/P1.
- P2 fix or follow-up decision.
- P3 non-blocking notes.
- Review summary comment.

**Required schema or outline:**
- Review severity rules from `execution/approval-gates.md`.

**Capability routing:**
- Copilot/Codex/human review when available.
- Structured fallback review when automated review does not produce substantive findings.

**GO conditions:**
- Review completed.
- P0/P1 are zero or fixed.
- Follow-ups are created for relevant out-of-scope risks.

**NO-GO conditions:**
- Review missing.
- P0/P1 unresolved.
- Required fix would exceed ticket scope and no follow-up/blocker is recorded.

**Next stage:**
- `/pipe:ship`

### `/pipe:ship`

**Purpose:**
Merge a reviewed PR and update Linear with delivery evidence, residual risk, and follow-ups.

**Current artifacts:**
- `execution/ticket-pr-handoff-system.md`
- `execution/linear-governance-model.md`
- `execution/approval-gates.md`

**Inputs:**
- PR with review complete.
- Validation results.
- Merge approval state.
- Follow-up list.
- Residual risk.

**Expected output:**
- Merged PR.
- Merge commit or merge reference.
- Linear delivery update.
- Ticket moved to Done when appropriate.
- Follow-up tickets linked when created.

**Required schema or outline:**
- Delivery update format from current Linear/PR handoff pattern.
- `DeliveryEvidence` when required.

**Capability routing:**
- Codex/GitHub/Linear lifecycle when approved.
- Human operator for gated actions not pre-approved.

**GO conditions:**
- PR scope delivered.
- PR linked to correct Linear ticket.
- Validation ran.
- Review complete.
- P0/P1 resolved.
- Follow-ups created for relevant risks.

**NO-GO conditions:**
- Merge approval missing.
- Review missing.
- Blocking validation failure.
- P0/P1 unresolved.

**Next stage:**
- `/pipe:learn`

### `/pipe:learn`

**Purpose:**
Capture reusable learning after delivery, validation, review, failure, or trial feedback.

**Current artifacts:**
- `knowledge/learning-record-policy.md`
- `schemas/LearningRecord.schema.json`
- `knowledge/kdr-dar-template.md`
- `knowledge/decision-conflict-protocol.md`
- `architecture/knowledge-runtime-architecture.md`

**Inputs:**
- Merged PR or completed documentary/investigative ticket.
- Review findings.
- Validation or trial evidence.
- Follow-ups and residual risk.

**Expected output:**
- LearningRecord candidate when reusable learning exists.
- KDR/DAR update when a decision changes.
- Follow-up ticket when learning is out of current scope.
- Explicit no-learning note when delivery is routine.

**Required schema or outline:**
- `LearningRecord` schema when reusable learning is recorded.
- KDR/DAR template when decision memory changes.

**Capability routing:**
- Knowledge curator workflow.
- Risk reviewer when learning touches approval gates, sensitive data, customer claims, privacy/security, billing, legal, compliance, or production.

**GO conditions:**
- Learning is source-linked and future-useful.
- Sensitive data and customer evidence have approval and redaction rules.
- Candidate promotion target is explicit if promotion is proposed.

**NO-GO conditions:**
- Learning invents evidence or relies only on chat memory.
- Candidate is promoted to canonical rule without human approval.
- Sensitive/private data would be stored without approval.

**Next stage:**
- Next iteration, follow-up ticket, pivot/kill decision, or stop.

## Paper Walkthrough

Scenario: a founder proposes a new idea and the Pipe needs to move from intake to reusable learning without creating executable commands.

1. `/pipe:idea`
   - Reads raw idea and produces a focused idea brief mapped to `product/product-context.md` and `product/founder-focus.md`.
   - Stops if the idea implies outreach, billing, or build work.
2. `/pipe:discover`
   - Narrows one market, one problem, one offer, one channel, and discovery questions.
   - Produces assumptions and unknowns for validation.
3. `/pipe:validate`
   - Applies C.O.N.T.R.O.L.E., validation scorecard, and market-validation-before-code gate.
   - Produces GO, CONDITIONAL GO, REFINE, NO-GO, or NOT APPLICABLE.
4. `/pipe:prd`
   - Converts validated framing into PRD requirements with evidence links and non-goals.
5. `/pipe:plan`
   - Produces MVP scope, risk review, architecture direction, and Linear-ready tickets.
   - Stops before creating Linear tickets unless approval exists.
6. `/pipe:build`
   - Executes one approved ticket in one branch and one PR.
7. `/pipe:check`
   - Validates scope, evidence, tests/checks, E2E applicability, DeliveryEvidence, and LearningRecord need.
8. `/pipe:review`
   - Requests review, classifies findings, fixes P0/P1, and records fallback review if automation is non-substantive.
9. `/pipe:ship`
   - Merges only when review and validation gates pass, then updates Linear with branch, PR, merge, validations, findings, follow-ups, and residual risk.
10. `/pipe:learn`
   - Creates a LearningRecord candidate only if the run produced reusable learning.
   - Otherwise records that no durable learning changed.

Walkthrough result:

- Every stage has a source artifact.
- Build work is blocked until upstream validation and planning gates allow it.
- Linear remains execution state.
- Repository artifacts remain strategic and knowledge source of truth.
- LearningRecord appears only when reusable learning exists.

## Validation Expectations

For this catalog ticket, validation should confirm:

- all proposed commands are covered
- every command links to current repository artifacts
- every command has GO and NO-GO conditions
- every command has expected outputs
- commands are explicitly spec-only
- no CLI, MCP, executable slash command, automation, or runtime integration is introduced
- the paper walkthrough reaches LearningRecord or a no-learning note without skipping validation gates

## Future Ticket Hooks

Future tickets may:

- create a machine-readable command schema
- create command-specific Markdown templates
- implement a manual `/pipe:context-pack` or `/pipe:check` runner
- connect commands to a future Knowledge MCP
- add command usage examples for Codex and Claude Code

Those tickets must preserve this catalog's spec-only boundary unless explicitly approved to implement runtime behavior.
