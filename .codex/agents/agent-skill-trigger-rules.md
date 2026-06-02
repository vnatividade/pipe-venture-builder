# Agent And Skill Trigger Rules

These rules decide which small set of agents, skills, and templates should be loaded for a task. They are a lightweight routing guide, not a scoring engine or autonomous orchestrator.

For Codex and Claude Code shared ticket-type routing, use `../../execution/context-routing-protocol.md`. This file keeps Codex-specific agent and skill trigger details compatible with that shared protocol.

Default behavior: identify the request type, map it to the current pipeline phase, load the smallest useful context set, and stop when approval or scope is missing.

## Routing Principles

- Start from the assigned Linear ticket or repository artifact.
- Load one primary agent by default.
- Add at most one supporting skill by default.
- Add a risk reviewer only when the task touches approval gates, sensitive claims, data, billing, production, outreach, security, privacy, or high-risk changes.
- Do not load all agents, all skills, or all templates for broad requests.
- Do not advance to growth, billing, external communication, production, or future/evolution workflows unless the current ticket explicitly allows it and approval exists.

## Request Type Detection

| Request Type | Signals | Primary Agent | Default Skill | Default Template |
|---|---|---|---|---|
| Conversational founder front door | vague founder goal, raw idea with unclear stage, "I have an idea", "I want this to work", "what should I do next?", user does not want to choose files or tools | Conversational Founder Guide Agent | None by default | `execution/conversational-founder-guide.md` |
| Idea intake | raw idea, new product context, sample idea | Idea Intake Agent | None unless validation is requested | `product/product-context.md` |
| Strategy focus | target market, problem, offer, channel, anti-goals | Product Strategist Agent | None | `product/founder-focus.md` |
| C.O.N.T.R.O.L.E. evaluation | strategic gate, Attack, Refine, Pivot, Kill | Product Strategist Agent | None | `product/controle-evaluation.md` |
| Validation planning | scorecard, ICP, discovery, evidence threshold | Validation Agent | Validation planning | `validation/validation-scorecard.md` |
| Research orchestration | research question, source plan, evidence lanes, contradictions | Research Orchestrator Agent | Research synthesis | `.codex/agents/research-validation-specialization.md` |
| Scientific validation | scientific claim, technical claim, evidence quality, expert source | Scientific Validation Agent | Research synthesis | `.codex/agents/research-validation-specialization.md` |
| Market intelligence | market signals, substitutes, competition, channel reachability | Market Intelligence Agent | Research synthesis | `.codex/agents/research-validation-specialization.md` |
| Venture intelligence curation | venture memory, opportunity radar, ranking hygiene, KDR/DAR linkage, evidence freshness, revisit trigger | Venture Intelligence Curator | Research synthesis / Knowledge update | `.codex/agents/venture-intelligence-curator-specialization.md` |
| Customer discovery evidence | interview notes, customer language, observed behavior, ICP evidence | Customer Discovery Agent | Validation planning | `validation/customer-interview-template.md` |
| Synthetic persona validation | synthetic persona, simulation, synthetic objections, synthetic-vs-real comparison | Synthetic Persona Validation Agent | Validation planning | `.codex/agents/synthetic-persona-validation-specialization.md` |
| PRD or requirements | PRD, requirements, stories, non-goals | Product Strategist Agent | PRD drafting | PRD placeholder or source artifact |
| MVP scope | core loop, riskiest assumption, smallest ethical test | MVP Scope Reviewer Agent | Validation planning | `product/mvp-scope.md` |
| Architecture handoff | technical shape, constraints, integrations, data, implementation readiness | Architecture Agent / software_architect | None | `.codex/agents/execution-risk-specialization.md` |
| Risk review | approval, sensitive claim, privacy, security, billing, production, P0, P1 | Risk Reviewer Agent | None | `.codex/agents/execution-risk-specialization.md` |
| Ticket decomposition | scope split, readiness, dependencies, acceptance, PR checklist | Ticket Orchestrator Agent | Execution handoff | `.codex/agents/execution-risk-specialization.md` |
| Roadmap sequencing | next ticket, dependencies, priority, future filter | Roadmap Orchestrator Agent | Linear governance | `execution/core-pipeline-map.md` |
| Ticket execution | branch, PR, validation, review, merge | Ticket Orchestrator Agent | Execution handoff | `execution/ticket-pr-handoff-system.md` |
| Linear state | status update, PR link, blocker, final handoff | Linear Steward Agent | Linear governance | `execution/linear-governance-model.md` |
| Knowledge update | KDR, learning, decision, customer language | Knowledge Curator Agent | Knowledge update | `knowledge/README.md` |
| Growth or content | distribution, channels, content, launch | Growth Strategist Agent or Content Strategy Agent | None unless approved | `growth/README.md` |
| Billing strategy | pricing hypothesis, willingness to pay, billing gate | Billing Strategy Agent | None unless approved | `monetization/README.md` |

If a request matches multiple rows, choose the earliest active pipeline phase unless the assigned ticket says otherwise.

## Phase Routing

| Pipeline Phase | Allowed Primary Agents | Allowed Skills | Stop Before |
|---|---|---|---|
| Conversational front door | Conversational Founder Guide Agent, then earliest applicable focused agent | None by default | asking the user to choose files/tools, ticket creation, build work, outreach, sensitive data |
| Idea intake | Idea Intake Agent | None | customer outreach, ticket creation, sensitive data |
| Founder focus | Product Strategist Agent | None | validation claims, implementation tickets |
| C.O.N.T.R.O.L.E. | Product Strategist Agent | None | advancing Attack/Refine without approval |
| Research and validation plan | Validation Agent, Research Orchestrator Agent, Scientific Validation Agent, Market Intelligence Agent, Venture Intelligence Curator, Customer Discovery Agent | Validation planning, Research synthesis, Knowledge update | outreach, storing identifiable data, unsupported claims |
| Working Backwards / PRD | Product Strategist Agent | PRD drafting | implementation tickets, broadening MVP |
| MVP scope review | MVP Scope Reviewer Agent, Validation Agent, Risk Reviewer Agent | Validation planning | architecture or implementation tickets without GO |
| Risk review | Risk Reviewer Agent | None | accepting unresolved P0/P1 risk |
| Architecture | Architecture Agent / software_architect, Risk Reviewer Agent, Ticket Orchestrator Agent | None | production-impacting changes, secrets, external integrations |
| Linear project and tickets | Roadmap Orchestrator Agent, Linear Steward Agent, Ticket Orchestrator Agent | Linear governance | creating projects or tickets without approval |
| Ticket execution | Ticket Orchestrator Agent, Linear Steward Agent | Execution handoff | PR open/merge without approval or review |
| First product trial | Roadmap Orchestrator Agent, Knowledge Curator Agent | Knowledge update | real external use without approval |
| Feedback and learning | Validation Agent, Knowledge Curator Agent | Knowledge update, Research synthesis | strategy changes or claims without human review |

## Context Load Limits

Use these limits unless the assigned ticket explicitly needs more.

| Task Shape | Max Agents | Max Skills | Max Templates / Artifacts |
|---|---:|---:|---:|
| Narrow documentation ticket | 1 | 0-1 | 2-4 |
| Governance or execution ticket | 1 primary + 1 supporting | 1 | 3-5 |
| Product strategy ticket | 1 | 0-1 | 3-5 |
| Validation or research ticket | 1 primary + risk reviewer if gated | 1 | 4-6 |
| Architecture ticket | 1 primary + risk reviewer if gated | 0-1 | 4-6 |
| Broad founder-facing request | Conversational Founder Guide Agent first | 0 | conversational guide, pipeline map, and relevant index files only |
| Broad repository/execution request | Roadmap Orchestrator first | 0 | pipeline map and relevant index files only |

When the task feels broad, reduce context by asking: "What phase is this in?" Then load only the contracts and templates for that phase.

## Escalation Rules

Escalate to the risk reviewer when:

- the task touches legal, financial, compliance, privacy, security, customer data, secrets, billing, production, paid acquisition, external communication, or sensitive claims
- the work could create unsupported evidence, customer, revenue, metric, integration, or market-validation claims
- the ticket is high risk or has ambiguous approval state
- review finds possible P0 or P1 issues

Escalate to the roadmap orchestrator when:

- the request is broad and could span multiple phases
- the next ticket is unclear
- backlog items include future/evolution labels
- dependencies or approval gates are unclear

Escalate to the Linear steward when:

- status, PR links, blockers, or final handoff must be recorded
- a follow-up ticket is proposed
- Linear project or ticket creation is requested

Escalate to the knowledge curator when:

- the work creates durable decision or learning context
- KDR output is required
- customer language may be recorded
- a prior decision may be superseded

Escalate to the venture intelligence curator when:

- market signals, ranking, opportunity radar, venture memory, KDR/DAR links, or revisit triggers need evidence hygiene
- a recommendation needs source traceability, confidence labels, contradiction tracking, and allowed/forbidden next actions
- a promising opportunity should be prepared for human review without approving execution, ticket creation, outreach, or build

## Broad Request Handling

For vague founder-facing requests like "I have an idea", "I want this to work", "what should I do next?", or "help me develop this idea":

1. Use the conversational founder guide first.
2. Infer the earliest safe pipeline stage.
3. Check durable knowledge and capability routing internally.
4. Ask one plain-language question or propose one safe next action.
5. Hand off to the focused agent only after the stage is clear.

For broad repository or execution requests like "build the product", "make the pipeline better", "run the whole system", or "continue autonomously":

1. Use the roadmap orchestrator first.
2. Check current Linear tickets and labels.
3. Filter out `horizon:future`, `source:future-evolution`, and clearly future/evolution work when the current cycle forbids it.
4. Select one current ticket.
5. Load only the primary agent and skill for that ticket.
6. Complete one branch and PR before selecting another ticket.
7. Stop when no current suitable ticket remains or approval is required.

## Approval Stop Rules

Stop instead of loading more context when:

- approval is missing for a gated action
- the ticket scope is ambiguous
- the requested action would bypass validation gates
- all apparent next work is future/evolution
- the task would require secrets, customer data, production data, billing, paid ads, external communication, or sensitive claims
- a specific human reviewer or external actor is required

## Examples

| User Request | Route |
|---|---|
| "Define customer interview evidence thresholds." | Validation Agent + Validation planning skill + validation scorecard. |
| "Synthesize market and scientific research for a validation decision." | Research Orchestrator Agent + Research synthesis skill + research and validation specialization. |
| "Check whether this implementation ticket is ready." | Ticket Orchestrator Agent + Execution handoff skill + execution and risk specialization. |
| "Create a PRD from this validated idea." | Product Strategist Agent + PRD drafting skill + product and validation artifacts. |
| "Update Linear after merge." | Linear Steward Agent + Linear governance skill + PR and ticket. |
| "What should we execute next?" | Roadmap Orchestrator Agent + pipeline map + Linear backlog. |
| "Add pricing collection." | Billing Strategy Agent for analysis only, then stop for approval before billing. |
| "Launch outreach." | Growth or Content Strategy Agent for draft only, then stop for approval before external communication. |

## Maintenance Rule

Do not turn this document into an exhaustive routing engine. Add new rows only when an approved current ticket creates a new recurring route.
