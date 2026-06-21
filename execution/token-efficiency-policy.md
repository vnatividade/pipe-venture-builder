# Token Efficiency Policy

This policy defines how Pipe Venture Builder agents should manage context, summaries, retrieval, and long-running session cost without weakening governance.

Use it with `AGENTS.md`, `execution/context-routing-protocol.md`, `architecture/context-pack-builder-spec.md`, `execution/ticket-pr-handoff-system.md`, and the assigned Linear ticket.

This policy does not implement token accounting, model routing, provider cost optimization, Datadog instrumentation, telemetry pipelines, retrieval automation, or runtime dashboards.

## Operating Principle

Agents should load the smallest context that is sufficient to execute safely.

Smallest sufficient context means:

- enough source material to satisfy the assigned ticket
- enough repository policy to preserve approval gates and safety rules
- enough artifact context to edit without breaking local patterns
- enough validation context to prove the work
- enough handoff context for a future agent to resume without chat memory

It does not mean omitting safety-critical governance, approval requirements, customer-data boundaries, validation evidence, or review state.

## Safety Floor

Never reduce context below the safety floor.

The safety floor includes:

- `AGENTS.md`
- the assigned Linear ticket
- approval gates relevant to the action
- expected write set and files being edited
- nearest repository protocol for the ticket type
- validation expectations for the ticket type
- review and merge rules when a PR is involved
- privacy, security, customer-data, billing, external-communication, or sensitive-claim boundaries when applicable

If token pressure would require dropping any safety-floor item, stop and record a blocker instead of proceeding.

## Stage Budget Principles

Use these principles as operating budgets. They are qualitative until real token accounting exists.

| Stage | Default context shape | Token discipline |
|---|---|---|
| Discovery | Validation artifacts, research question, target persona or respondent plan, evidence boundary. | Prefer interview goals, assumptions, and source excerpts over broad product history. Do not invent evidence from summaries. |
| Planning | Linear ticket, strategic gate, PRD/MVP or architecture source, risk notes, expected write set. | Build a compact plan from canonical artifacts; record omitted background that may affect later tickets. |
| Development | Ticket, expected write set, affected files, local tests, relevant protocol, ADRs when design changes. | Read full files before editing them; use targeted search for adjacent patterns. Avoid broad repository scans unless scope requires them. |
| Review | PR diff, ticket acceptance criteria, validation output, risk and security boundaries, review comments. | Review the changed surface and risk paths first; only expand context when a finding needs source confirmation. |
| Handoff | Branch, PR, commit, changed files, validation, review result, follow-ups, context choices, known omissions. | Compress execution history into source-linked facts that let the next agent resume. |

## Context Selection Rules

Use targeted search before broad reading when the goal is to find candidate files or repeated terms.

Read a full artifact when:

- editing that artifact
- the artifact is the policy authority for the ticket
- the file is short enough that partial reading risks missing local structure
- a safety, approval, privacy, security, billing, customer-data, or sensitive-claim boundary may be affected
- a review finding or validation failure depends on full context
- a future handoff would otherwise be ambiguous

Use targeted snippets when:

- locating references across many files
- checking whether a term or policy already exists
- comparing naming and link conventions
- gathering examples for a narrow documentation change
- confirming that excluded scope was not introduced

Do not use chat memory as the only source for decisions that future agents need. Promote durable decisions into repository artifacts, ADRs, or Linear handoffs when the assigned ticket allows it.

## Context Pack Rules

Context Packs should follow `architecture/context-pack-builder-spec.md` and add an explicit context-efficiency note.

A useful pack states:

- why each source was included
- which source class it belongs to
- which files were read fully
- which searches or snippets were used
- what was omitted and why
- whether omitted context could affect safety, acceptance, validation, review, or future sequencing

The pack should link to source files instead of copying long sections. Derived summaries must remain derived; they must not become new rules unless promoted through the appropriate repository decision process.

## Summarization Rules

Summarize when:

- a session crosses multiple execution phases
- handoff or resume will happen later
- several large artifacts were consulted
- a PR review, Linear handoff, or context pack needs a compact source-linked record
- repeated context would otherwise be reloaded by another agent

A useful summary includes:

- ticket ID and objective
- source files or URLs used
- decisions made and their source
- validations run or unavailable
- branch, PR, commit, and review state when applicable
- blockers, follow-ups, and residual risks
- context deliberately omitted

Do not summarize away:

- approvals or missing approvals
- P0/P1 findings
- validation failures
- customer-data or privacy boundaries
- secrets or credential handling boundaries
- production, billing, paid acquisition, or external-communication gates
- unsupported claims about customers, evidence, metrics, integrations, revenue, or market validation

## Operational Control Loop

Use this loop during agent execution:

1. Define context need: ticket type, expected write set, safety floor, and validation target.
2. Gather minimally: use the context routing protocol and targeted search before broad reads.
3. Execute narrowly: edit only included scope and read full files before modifying them.
4. Check context drift: if new files, gates, or risks appear, decide whether to continue, stop, or create a follow-up.
5. Compress: summarize source-linked decisions, validations, and omissions before PR or handoff.
6. Hand off: record context strategy and omissions in PR and Linear when repository changes occur.
7. Learn: create a follow-up only when a repeated context failure or cost pattern is actionable.

## Handoff Fields

For PRs, final Linear handoffs, or cross-agent resumes, record these fields when the work involved meaningful repository context:

```md
## Context and token efficiency
- Context strategy:
- Safety-floor sources:
- Full artifacts read:
- Targeted searches or snippets used:
- Summaries or compression created:
- Known omitted context:
- Omission risk:
- Token/cost/session signal:
- Follow-up needed:
```

`Token/cost/session signal` is a qualitative field until instrumentation exists. Use values such as `low`, `medium`, `high`, or `not measured`, plus a short reason when it affects future sequencing.

These fields may later map to Datadog, a runtime cockpit, or another observability capability. Recording them manually does not authorize telemetry implementation or external data transfer.

## Validation Checklist

Before opening a PR or completing a handoff, check:

- Did the agent read the assigned Linear ticket and relevant safety-floor artifacts?
- Did the agent avoid broad repository dumps?
- Were full files read before edits?
- Were targeted searches used for discovery across large areas?
- Were context omissions named when they could affect a future agent?
- Did summaries preserve approvals, validations, review state, blockers, and risks?
- Did the handoff include enough source-linked context to resume without chat memory?
- Did the work avoid implementing token accounting, model routing, external instrumentation, or provider cost optimization unless a separate approved ticket allows it?

## Stop Conditions

Stop and record a blocker when:

- token pressure would drop a safety-floor artifact
- missing source context affects approval, security, privacy, customer data, billing, production, external communication, or sensitive claims
- the ticket requires full evidence but only a summary is available
- a context omission could change acceptance criteria or review outcome
- cost or session length makes the agent unable to preserve reviewable evidence

## Out Of Scope

- exact token counting
- automated context window management
- embeddings or retrieval implementation
- model/provider routing
- pricing or provider optimization
- Datadog instrumentation
- runtime dashboards
- production telemetry
- changes that reduce governance or approval coverage
