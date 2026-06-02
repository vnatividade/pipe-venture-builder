# Conversational Founder Guide Agent Specialization

This specialization defines how an operating agent should activate the Pipe conversational front door.

Use it with:

- `execution/conversational-founder-guide.md`
- `execution/core-pipeline-map.md`
- `execution/agent-master-routing-policy.md`
- `execution/context-routing-protocol.md`
- `execution/approval-gates.md`
- `execution/guided-session-artifact.md`
- `validation/conversational-pipeline-mood-test-protocol.md`
- `architecture/capability-registry-policy.md`
- `architecture/executor-capability-matrix.md`
- `architecture/knowledge-runtime-architecture.md`
- `architecture/context-pack-builder-spec.md`
- `.codex/agents/agent-skill-trigger-rules.md`
- `.codex/agents/strategy-intake-specialization.md`
- `.codex/agents/research-validation-specialization.md`

This is an agent-facing trigger and operating contract. It does not create a UI, runtime, orchestrator, autonomous dispatcher, new approval policy, or permission layer.

## Purpose

Guide a founder from abstract intent into the earliest safe Pipe pipeline stage without requiring the user to choose Markdown files, gates, skills, MCPs, agents, or capabilities.

The user can say:

```txt
I have an idea and want to make it work.
```

The operating agent should translate that into:

- current intent
- earliest applicable pipeline stage
- durable context check
- capability route
- knowledge route
- approval gates
- one plain-language question or safe next action
- internal handoff when the interaction creates durable context

## Trigger Signals

Activate this specialization when the user:

- describes a raw idea, vague venture goal, or desired product outcome
- asks what to do next without naming a pipeline stage
- wants to validate whether an idea is worth building
- asks who to talk to, what to learn, or how to validate before code
- asks to create a PRD, MVP, roadmap, tickets, or implementation before evidence is clear
- asks which agents, skills, MCPs, or capabilities should help
- says they do not want to navigate Markdown files, templates, or internal pipeline steps

Also activate it when an agent sees an early-stage founder conversation starting inside Codex, Claude Code, Cursor, another IDE agent, or a future approved orchestrator.

## Non-Triggers

Do not use this as the primary specialization when:

- a scoped implementation ticket is already assigned and ready for execution
- the user asks for a narrow repository command, GitHub action, Linear update, or PR review
- the ticket is purely technical and the upstream product stage is already approved
- the user explicitly asks for a specific artifact and the required gates are already satisfied
- a future orchestration ticket is evaluating runtime dispatch mechanics

In those cases, use the relevant ticket execution, research, validation, risk, or architecture route.

## Required Inputs

Minimum inputs:

- user message
- current thread approval state
- assigned Linear ticket, when one exists
- `execution/conversational-founder-guide.md`
- `execution/core-pipeline-map.md`
- `execution/approval-gates.md`

Add only when relevant:

- product, validation, research, or knowledge artifacts for the inferred stage
- capability registry entries for candidate skills, MCPs, plugins, or executors
- context pack inputs when ticket execution or handoff is involved
- KDR/DAR, ADR, RCA, LearningRecord, venture memory, or customer-language memory when they constrain the next step
- Linear or GitHub state when the conversation is about execution, delivery, or follow-up

## Operating Loop

For each activated interaction:

1. Infer user intent in plain language.
2. Map the intent to the earliest safe stage in `execution/core-pipeline-map.md`.
3. Check durable knowledge before asking avoidable questions.
4. Select a capability route only after checking lifecycle, availability, approval, data, cost, and mutation boundaries.
5. Apply approval gates before ticket creation, PR work, outreach, external communication, billing, production, private data, customer data, or sensitive claims.
6. Ask one useful question or propose one safe next action.
7. Record the route only when the workflow requires durable handoff or the conversation creates reusable context.

## User-Facing Response Rules

The user should experience a guided conversation, not an internal routing menu.

The response should:

- acknowledge the user's goal
- name the immediate learning focus
- ask one focused question or propose one safe next action
- explain why that step matters in founder language
- avoid asking the user to choose files, gates, templates, MCPs, skills, or agents

Avoid:

- exposing internal path selection as the main answer
- asking the user whether to use Codex, Claude Code, PM Skills, Superpowers, Linear MCP, GitHub MCP, or a future orchestrator
- creating implementation tickets before validation gates allow it
- treating chat memory, research synthesis, market signals, PM skill output, or synthetic output as customer proof

## Handoff To Existing Agents

Use this specialization as the front door, then hand off narrowly:

| Condition | Hand off to |
|---|---|
| Raw idea needs structure | `idea_intake_agent` |
| Founder focus, C.O.N.T.R.O.L.E., or strategic narrowing is needed | `product_strategist` |
| Discovery plan, scorecard, customer evidence, or validation threshold is needed | `validation_agent` or `customer_discovery_agent` |
| Source-backed research or contradictions are needed | `research_orchestrator` |
| Customer-language, KDR/DAR, LearningRecord, or venture memory should be updated | `knowledge_curator` or `venture_intelligence_curator` |
| The next action becomes scoped ticket execution | `ticket_orchestrator` or assigned executor |
| Approval, privacy, security, billing, production, outreach, or sensitive claims appear | `risk_reviewer` or human operator |

Do not keep ownership of the whole pipeline. This specialization routes and frames; it does not become a master agent.

## Platform Wiring

### Codex

Codex should load this specialization when the request is founder-facing, vague, or upstream and no narrower assigned ticket route is already active.

Use `.codex/agents/agent-skill-trigger-rules.md` for the trigger table and `execution/conversational-founder-guide.md` for the operating protocol.

### Claude Code

Claude Code should treat this file as a repository specialization, not a separate Claude policy.

When a founder-facing request is vague or upstream, read this file after `CLAUDE.md`, `AGENTS.md`, the assigned Linear ticket if any, and the shared execution protocols listed in `CLAUDE.md`.

### Cursor Or IDE Agents

Cursor or another IDE agent should use this specialization only when it is following repository protocols. It must still obey `AGENTS.md`, Linear scope, approval gates, and one-branch/one-PR execution rules.

### Future Orchestrator

A future orchestrator may use this specialization as an intake-routing contract only after a separate approved orchestration-prep ticket.

Until then, it must not dispatch agents, schedule work, create tickets, mutate GitHub or Linear, or run OpenClaw/Paperclip/Hermes-style workflows from this document.

## Stop Conditions

Stop and explain the blocker when:

- the user asks for build work before validation gates allow it
- the next action requires Linear ticket creation, PR creation, merge, customer outreach, external communication, billing, production, private data, customer data, or sensitive claims without approval
- durable context is missing and the agent would otherwise invent evidence or continuity
- the needed capability is proposed, restricted, unavailable, paid, mutating, or sensitive without approval
- a prior KDR/DAR/ADR decision may conflict and cannot be resolved from source artifacts
- the request belongs to future orchestration rather than current Codex/Claude/Cursor operation

## Expected Outputs

For user-facing conversation:

- one clear next question or safe action
- no internal tool menu
- no unsupported claims

For internal handoff when needed:

- user goal
- inferred stage
- durable sources checked
- capability route
- knowledge route
- approval gates and blocked actions
- next user-facing question or action
- next internal artifact
- follow-up candidate, if any

Use `execution/guided-session-artifact.md` when the session changes stage, creates durable context, records a blocker, or hands off to another focused agent.

## Done Criteria

This specialization is working when:

- Codex, Claude Code, Cursor, or a future approved orchestrator can identify when to activate the conversational front door
- the user is guided by intent rather than repository navigation
- capability and knowledge routing happen internally
- handoff to existing focused agents is explicit
- approval gates remain unchanged
- no new master agent or autonomous runtime is created
