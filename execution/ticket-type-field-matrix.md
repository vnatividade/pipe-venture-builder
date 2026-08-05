# Ticket Type Field Matrix

This matrix defines which Linear ticket fields are required, conditional, or not needed by delivery type.

Use it with `execution/linear-ticket-template-v2.md`. The template defines the full field set; this matrix decides which fields matter for each type so tickets stay complete without becoming bureaucratic.

## Legend

| Mark | Meaning |
|---|---|
| R | Required for this ticket type. |
| C | Conditional; include when the scope, risk, implementation surface, or approval state makes it relevant. |
| N | Not normally needed; omit or mark not applicable only when clarity requires it. |

## Approved Ticket Types

- architecture
- documentation
- prompt
- skill
- workflow
- governance
- code
- infrastructure
- automation
- observability
- product
- orchestration-prep

Do not add a new type during execution unless a ticket explicitly asks for the taxonomy to change.

## Baseline Fields

These fields are required for every executable ticket, regardless of type:

- Objective
- Why This Matters or Rationale
- Source Rationale
- C.O.N.T.R.O.L.E. Dimensions Supported
- Type
- Included Scope
- Excluded Scope
- Deliverables
- Acceptance Criteria
- GO Conditions
- NO-GO Conditions
- Dependencies
- Prerequisites
- Approval Requirement
- Suggested Owner/Agent
- Executor Tool
- Risk Level
- Effort
- Complexity
- Parallelizable
- Parallelization Notes
- Expected Write Set
- Restricted Files
- Definition of Ready
- Definition of Done
- Validation Plan
- Monitoring Requirements
- Success Metrics
- Rollback or Mitigation
- Notes for Implementation
- Follow-up Ticket Criteria
- Agent Execution Notes

Keep baseline fields concise. A required field may say "Not applicable" only when the reason is clear and useful to future agents.

## Field Matrix By Type

<!-- BEGIN GENERATED: field-matrix -->
<!-- Gerado de contracts/ticket-field-matrix.json por `pipe ticket matrix --emit-markdown`.
     Não edite à mão: edite o JSON e regenere. O check de deriva reprova divergência. -->
| Field | architecture | documentation | prompt | skill | workflow | governance | code | infrastructure | automation | observability | product | orchestration-prep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Technical Dependencies | C | N | C | C | C | C | R | R | R | R | C | C |
| Operational Dependencies | C | C | C | C | R | R | C | R | R | R | R | R |
| Human Decision Required | C | C | C | C | C | C | C | C | C | C | C | C |
| Observability Requirements | C | N | N | C | C | C | R | R | R | R | C | C |
| KPI Impact | N | N | N | N | N | C | C | C | C | C | R | C |
| Post-release Follow-up | C | N | C | C | C | C | C | R | R | R | R | C |
| Rollback Signal | C | N | N | C | C | C | R | R | R | R | C | C |
| Agent Consumers | R | C | R | R | R | R | C | C | C | C | C | R |
| Affected Protocol or Artifact | R | R | R | R | R | R | C | C | C | R | C | R |
| Product KPI Baseline | N | N | N | N | N | N | C | C | C | C | R | N |
| Runtime Healthcheck | N | N | N | C | C | C | R | R | R | R | C | N |
| Security or Data Sensitivity Notes | C | C | C | C | C | C | R | R | R | R | R | C |
<!-- END GENERATED: field-matrix -->

## Type-Specific Requirements

### architecture

Required emphasis:

- state the decision, constraint, or architectural surface affected
- name downstream agent consumers
- define how future tickets should use the decision
- include traceability to source rationale

Success Metrics should measure reduced ambiguity, clearer ownership, fewer conflicting implementation paths, and better readiness for dependent tickets.

Monitoring Requirements should track whether future tickets cite the architecture artifact and whether repeated clarification is still needed.

### documentation

Required emphasis:

- identify the ambiguity, missing knowledge, or outdated instruction being fixed
- preserve existing source-of-truth hierarchy
- define the intended reader or agent consumer
- keep validation manual and path-based unless docs tooling exists

Success Metrics should measure findability, lower handoff friction, fewer repeated context questions, and clearer execution references.

Monitoring Requirements should track future agent use and whether docs become stale after related workflow changes.

### prompt

Required emphasis:

- name the prompt surface and consuming agent
- define expected behavior change
- include examples or constraints when ambiguity risk is material
- declare what should not change in adjacent prompts

Success Metrics should measure reduced prompt duplication, better adherence, fewer off-scope agent actions, and clearer handoff.

Monitoring Requirements should track agent output drift, repeated instruction misses, and whether the prompt needs an eval or fixture later.

### skill

Required emphasis:

- name trigger conditions and non-trigger conditions
- define consuming agents and expected workflow
- include validation for the skill contract
- state whether runtime/tool behavior is affected

Success Metrics should measure correct skill activation, fewer manual clarifications, lower duplicated instructions, and clear boundaries with other skills.

Monitoring Requirements should track false positives, false negatives, and handoff quality after the skill is used.

### workflow

Required emphasis:

- define state transitions, owner handoff, and stop conditions
- name affected protocols
- state how Linear, GitHub, and repository artifacts interact
- define review and validation expectations

Success Metrics should measure fewer blocked tickets, cleaner handoffs, lower context loss, and fewer merge or ownership conflicts.

Monitoring Requirements should track blocked tickets, stale states, missing handoffs, and repeated workflow exceptions.

### governance

Required emphasis:

- name the policy or rule surface affected
- preserve approval gates unless the ticket explicitly scopes a change
- identify risk of divergence if not implemented
- define how adherence will be checked

Success Metrics should measure clearer approval state, fewer unsafe actions, stronger traceability, and fewer scope disputes.

Monitoring Requirements should track approval blockers, policy exceptions, and tickets that bypass required fields.

### code

Required emphasis:

- declare files, modules, or bounded directories likely to change
- define tests, lint, build, and targeted runtime checks
- include observability and rollback or mitigation when behavior changes
- state security or data sensitivity assumptions

Success Metrics should cover expected behavior, error rate, logs, events, traces, latency when applicable, healthcheck when applicable, and rollback signal.

Monitoring Requirements should track runtime errors, test failures, regression signals, and any post-merge verification.

### infrastructure

Required emphasis:

- declare environment, configuration, deployment, or dependency surfaces
- define rollback, mitigation, and operational owner
- include security and secret-handling constraints
- require monitoring before merge or before activation when applicable

Success Metrics should cover availability, healthcheck, error rates, resource limits, audit trail, rollback signal, and operational readiness.

Monitoring Requirements should track system health, configuration drift, failed jobs, access changes, and rollback triggers.

### automation

Required emphasis:

- state trigger, cadence, actor, inputs, outputs, and stop conditions
- define safeguards, dry-run behavior, and failure handling
- include observability for runs and audit trail
- preserve approval gates for external action, billing, customer contact, or data movement

Success Metrics should cover successful run rate, failure rate, skipped unsafe actions, audit completeness, latency when applicable, and rollback or disable signal.

Monitoring Requirements should track run status, error logs, skipped actions, and unexpected side effects.

### observability

Required emphasis:

- define logs, events, metrics, traces, dashboards, alerts, or audit trails
- state what decision each signal enables
- define owner, threshold, and follow-up behavior
- avoid adding noisy metrics without an action path

Success Metrics should cover signal coverage, alert/action usefulness, reduced diagnosis time, and traceability from signal to ticket or incident.

Monitoring Requirements should track signal presence, signal quality, alert noise, and follow-up closure.

### product

Required emphasis:

- define user outcome and value hypothesis
- include KPI Impact, primary KPI, secondary KPI, conversion event, adoption metric, and baseline when available
- state validation and post-release follow-up
- include rollback or mitigation for user-facing risk

Success Metrics should cover adoption, conversion, retention when applicable, perceived quality when applicable, and customer or user learning artifacts.

Monitoring Requirements should track KPI movement, usage evidence, feedback, support or quality signals, and follow-up decision date.

### orchestration-prep

Required emphasis:

- state that runtime orchestration is not being implemented
- depend on the Codex + Claude Code baseline unless explicitly waived
- define future orchestrator assumptions and questions
- produce an adaptation plan or readiness analysis, not an orchestrator

Success Metrics should cover dependency readability, ownership clarity, task distribution readiness, validation routing, progress recording, conflict handling, and follow-up generation.

Monitoring Requirements should track when prerequisites are complete and whether the future orchestration analysis should be reopened.

## Cross-Type Conditional Rules

Use these rules when the matrix alone is not enough:

- If a ticket changes runtime behavior, include Observability Requirements and Rollback or Mitigation.
- If a ticket touches user value, growth, validation, billing, pricing, onboarding, or customer-facing behavior, include KPI Impact.
- If a ticket touches secrets, customer data, production data, billing, legal, compliance, privacy, security, or external communication, include explicit approval and sensitivity notes.
- If a ticket changes shared governance, global templates, agent contracts, or approval-sensitive docs, mark `Parallelizable` as `No` or `Partial`.
- If expected files are broad or shared, include merge-order constraints and restricted files.
- If a human decision can block start, PR opening, merge, or Done, include Human Decision Required.
- If a field would be empty noise, omit it only when the baseline template does not require it; otherwise write a short not-applicable reason.

## Readiness Check

A ticket is READY when:

- every baseline field is present
- type-specific required fields are present
- conditional fields are included when triggered by scope or risk
- dependencies and approval state are clear
- expected write set and restricted files are declared
- validation plan is executable or unavailable checks are explicitly documented
- monitoring and success metrics match the delivery type

A ticket is NOT READY when:

- the type is missing or unsupported
- acceptance criteria are not observable
- validation is vague
- dependencies or approvals are ambiguous
- write set is too broad for one ticket
- product tickets lack KPI Impact
- code, infrastructure, automation, or observability tickets lack observability or rollback reasoning
- governance, prompt, skill, workflow, or documentation tickets do not name the affected artifact or agent consumers

## Maintenance

Revise this matrix when actual ticket execution shows that a field is creating noise, a recurring field is missing, or a new ticket type is needed.

Do not revise it as part of ordinary implementation work unless the assigned Linear ticket explicitly scopes template or matrix governance.
