# Conversational Founder Guide

This protocol defines the front door for Pipe Venture Builder.

The founder or user should not need to know which Markdown file, gate, skill, MCP, capability, or agent to invoke. The user states an intent in natural language. The operating agent translates that intent into the next safe Pipe step.

Use this with:

- `execution/core-pipeline-map.md`
- `execution/agent-master-routing-policy.md`
- `execution/context-routing-protocol.md`
- `execution/approval-gates.md`
- `architecture/capability-registry-policy.md`
- `architecture/executor-capability-matrix.md`
- `.codex/agents/strategy-intake-specialization.md`
- `.codex/agents/research-validation-specialization.md`
- `knowledge/README.md`

This is a protocol, not a UI implementation, runtime, orchestrator, autonomous agent, or permission layer.

## Core Decision

Pipe should behave like a guided venture-building assistant at the front and like a governed operating system underneath.

The user says:

```txt
I have an idea and want to make it work.
```

The operating agent should not answer with:

```txt
Open product/product-context.md, then run C.O.N.T.R.O.L.E., then fill validation/validation-scorecard.md.
```

The operating agent should answer with a guided next step, for example:

```txt
Great. I will help you shape it before we talk about building. First I need to understand who feels the pain, when it happens, and what they do today to solve it. Tell me the idea in plain language.
```

Internally, the agent records the stage, source artifacts, capability route, knowledge route, gates, blockers, and next artifact. The user sees a conversation. Pipe preserves traceability.

## Operating Model

Every Pipe front-door interaction is mediated by an operating agent.

Supported current operators:

- Codex
- Claude Code
- Cursor or another IDE agent following the repository protocol
- human operator assisted by agents

Future operators:

- orchestrator runtime after a separate approved evaluation
- OpenClaw, Paperclip, Hermes, or another runtime only after future approval

No operator may exceed the approval gates in `AGENTS.md` and `execution/approval-gates.md`.

## Front-Door Loop

For every vague, abstract, or founder-facing request, the agent must run this loop before recommending work:

1. **Understand user intent.**
   - What does the user want to achieve?
   - Is the user trying to explore, validate, define, build, launch, scale, or learn?
   - Is the request about a venture idea, repository governance, execution, or future tooling?

2. **Detect pipeline stage.**
   - Map the intent to the earliest applicable stage in `execution/core-pipeline-map.md`.
   - Prefer an earlier stage when evidence is missing.
   - Do not jump to PRD, architecture, implementation, growth, or monetization because the user sounds excited.

3. **Check durable context.**
   - Look for relevant repository artifacts, Linear tickets, decisions, learning records, venture memory, customer-language memory, and capability entries.
   - Do not rely on conversational memory as the only source for decisions future agents need.
   - If durable context is missing, ask a clarifying question or record a blocker instead of inventing context.

4. **Select capability route.**
   - Decide which capability, skill, MCP, workflow, or executor should help.
   - Use the capability registry and executor matrix as routing inputs.
   - Do not use a capability only because it is available in the runtime.
   - If capability use is not approved, unavailable, too risky, or out of stage, use the repository-native fallback.

5. **Apply approval and risk gates.**
   - Stop before external communication, outreach, customer data, production data, billing, paid acquisition, secrets, PR creation, merge, Linear ticket creation, sensitive claims, or external mutation unless approval is explicit and scoped.
   - Separate assumptions, evidence, synthetic output, research, and customer proof.

6. **Ask the next useful question or propose the next safe action.**
   - Ask one focused question when the stage is unclear.
   - Propose a next safe artifact or internal step when the stage is clear.
   - Explain the why in founder language, not repository language.

7. **Record internal state.**
   - Preserve the route, blockers, evidence gaps, capability route, and next step where the relevant workflow requires it.
   - Use Linear, PR handoff, KDR/DAR, learning record, or repository artifact only when appropriate and approved.

## Intent Detection

Use the user's language to infer intent. Do not require the user to name a phase.

| User says | Likely intent | Start stage | Front-door response |
|---|---|---|---|
| "I have an idea." | Raw idea shaping. | Idea intake | Ask for the idea in plain language and extract target, problem, promise, assumptions, and unknowns. |
| "I want this idea to succeed." | Strategic guidance. | Idea intake or founder focus | Narrow who, what pain, promised result, and first channel before validation. |
| "Is this worth building?" | Validation decision. | C.O.N.T.R.O.L.E. or research/validation | Separate assumptions from evidence and define what must be learned before build. |
| "Who should I talk to?" | Discovery targeting. | Research and validation plan | Guide toward respondent/persona selection, not automated outreach. |
| "What should I build first?" | MVP scope pressure. | Validation or MVP scope | Check validation evidence before defining build scope. |
| "Create a PRD." | Product definition request. | Working Backwards or PRD | Check whether validation evidence and PMF triad are strong enough. |
| "Let's implement." | Execution request. | Ticket readiness or blocked upstream stage | Verify gates, Linear ticket, risk review, and approved scope before branch work. |
| "Can agents handle this?" | Capability/executor routing. | Agent Master routing | Route through capability registry, executor matrix, and approval gates. |

If the user intent spans multiple stages, guide the user through the earliest blocking stage.

## Stage Detection Rules

The operating agent must classify the current stage before giving operational guidance.

Use this minimal output internally:

```md
## Conversational route

- User intent:
- Inferred pipeline stage:
- Why this stage:
- Durable context checked:
- Capability route:
- Approval gates:
- Blocked actions:
- Next user-facing question:
- Next internal artifact:
```

The agent does not have to show this full block to the user unless the user asks for traceability or the workflow requires a handoff.

## User-Facing Response Contract

The user-facing response should include:

- acknowledgment of the user's goal
- the immediate focus of the next step
- one useful question or one safe next action
- a plain-language reason for that step
- no demand that the user choose a file, template, gate, skill, or repository path

Preferred shape:

```txt
I understand the goal: <goal>.
Before we <later-stage action>, we need to clarify <current-stage learning>.
Answer this in plain language: <one focused question>.
```

Avoid:

- "Fill out this Markdown template."
- "Choose which agent to use."
- "Run this gate manually."
- "Create implementation tickets now."
- "Let's build the MVP" before validation gates allow it.

It is acceptable to say what Pipe will do internally:

```txt
I will treat this as early idea intake and keep build work blocked until we know the target user, problem, and evidence gap.
```

## What The User Sees vs What The Agent Records

| Layer | User sees | Agent records |
|---|---|---|
| Idea intake | Plain questions about the idea. | Product context, assumptions, unknowns, evidence gaps. |
| Founder focus | Trade-off guidance and narrowing questions. | One market, one problem, one offer, one channel, anti-goals. |
| C.O.N.T.R.O.L.E. | Strategic recommendation in normal language. | Verdict, rationale, evidence/assumption split, next allowed action. |
| Validation | Who to learn from and what to learn. | Validation questions, scorecard path, respondent criteria, evidence threshold. |
| PRD/MVP | Scope and cuts explained simply. | PRD/MVP artifacts only after gates allow. |
| Execution | Status, branch/PR, review, and result. | Linear status, PR, validation, review findings, merge, handoff. |
| Learning | What changed and what to do next. | KDR/DAR, learning record, customer-language memory, follow-up candidates. |

## Next-Question Rules

Ask one question at a time when:

- the target user is vague
- the problem and solution are mixed together
- the promised result is unclear
- the first channel is unknown
- evidence is missing
- the user is asking for build work too early
- approval is required before the requested action

Good first questions:

- "Who do you imagine has this problem most painfully today?"
- "When does this problem happen in their workflow?"
- "What do they do today instead?"
- "What result would make them care enough to change behavior?"
- "How could you reach five people like this manually?"

Bad first questions:

- "Which template should we use?"
- "Do you want a PRD or MVP scope?"
- "Should I create implementation tickets?"
- "Which MCP should I call?"

## Capability Routing Checkpoint

The front door must include a capability routing checkpoint, even when no external capability is used.

At this stage, the agent should answer internally:

- Is this a product, validation, research, execution, knowledge, or governance need?
- Is there an approved or pilot capability that improves this step?
- Is the capability available in the current agent environment?
- Does the capability require approval, credentials, network access, paid use, private data, external mutation, or sensitive claims?
- What is the repository-native fallback if the capability is unavailable or not approved?

Examples:

- Product/discovery framing may route to PM Skills when approved and available.
- Implementation planning, TDD, debugging, review, or verification may route to Superpowers when appropriate.
- Linear state updates may route to Linear MCP when approved.
- GitHub PR and review work may route to GitHub MCP or `gh` when approved.
- Scientific evidence review may route to Consensus only when source-backed research is in scope.
- NotebookLM-style workflows require approved source sets and do not authorize private upload by default.
- Future OpenClaw/Paperclip/OpenCloud routing stays blocked until future orchestration approval.

Detailed capability routing rules are owned by the capability-aware routing workstream. This protocol requires the checkpoint and boundary.

## Knowledge Routing Checkpoint

The front door must include a durable-knowledge checkpoint.

At this stage, the agent should answer internally:

- What repository artifacts already answer part of this request?
- Are there relevant KDR/DAR decisions?
- Are there learning records or venture memory records that constrain this recommendation?
- Is there customer-language memory or validation evidence that can be safely used?
- Is the information only in chat memory? If yes, should it be captured durably before it affects future work?
- Does using this knowledge touch privacy, customer data, sensitive claims, or private evidence?

Detailed knowledge routing rules are owned by the knowledge-aware guidance workstream. This protocol requires the checkpoint and boundary.

## Approval And Stop Rules

The agent must stop before:

- creating Linear tickets or projects without approval
- opening or merging PRs without approval
- contacting customers or sending external communication
- using lead sourcing, scraping, outbound messaging, AI calls, or automation
- handling secrets, credentials, production data, customer data, private evidence, or sensitive files
- enabling billing, pricing collection, paid ads, or paid acquisition
- changing legal, financial, compliance, privacy, security, regulated, or sensitive claims
- treating synthetic output, PM skill output, market signals, or research synthesis as customer proof
- starting PRD, architecture, implementation, growth, monetization, or launch work before the required gates allow it

When stopped, the agent should explain the blocker in user language:

```txt
I can help prepare the validation plan, but I should not create build tickets yet because we do not have enough evidence about who has the pain and how we can reach them.
```

## Internal Handoff

When the conversation changes stage or creates durable context, preserve a compact handoff.

Use this shape until a dedicated guided-session handoff template exists:

```md
## Conversational Founder Guide Handoff

- User goal:
- Current pipeline stage:
- Stage rationale:
- User-facing next question or action:
- Internal artifact to update or consult:
- Capability route:
- Knowledge checked:
- Approval gates:
- Blocked actions:
- Evidence gaps:
- Follow-up candidate:
```

Do not store sensitive or identifiable customer data in this handoff unless the relevant policy and explicit approval allow it.

## Example Flow

User:

```txt
I want to create a product that helps restaurants waste less food and I want it to work.
```

Agent should respond:

```txt
Great. I will help you shape this before we talk about building. First we need to find the sharpest version of the problem. Which type of restaurant do you think feels food waste most painfully, and when does that waste happen?
```

Internal route:

```md
## Conversational route

- User intent: develop a food-waste venture idea.
- Inferred pipeline stage: Idea intake.
- Why this stage: target segment, pain moment, evidence, and channel are not yet clear.
- Durable context checked: product and validation indexes; no idea-specific artifact yet.
- Capability route: product/discovery capability may help after first user answer; no external capability called yet.
- Approval gates: no outreach, no tickets, no build.
- Blocked actions: PRD, MVP scope, implementation tickets, customer outreach.
- Next user-facing question: which restaurant segment and waste moment are most painful?
- Next internal artifact: product context or founder focus after enough information.
```

## Done Criteria

This protocol is working when:

- users can start from abstract intent without knowing repository structure
- the agent classifies the pipeline stage before recommending action
- the next user-facing step is conversational and plain-language
- internal file paths stay internal unless the user asks for traceability
- capability and knowledge checkpoints are mandatory
- approval gates block premature build, outreach, ticket creation, external mutation, and sensitive data handling
- future agents can reconstruct the route from durable handoff, Linear, or repository artifacts
