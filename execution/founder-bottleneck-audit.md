# Founder Bottleneck Audit

Use this audit to identify where founder attention is required, where agents can safely assist, and which operations may become future automation candidates only after approval and evidence.

This audit does not authorize autonomous outreach, autonomous merge, production deployment, scheduled agents, OpenClaw, orchestrator implementation, billing, paid acquisition, or changes to approval gates.

## Purpose

The Pipe should increase agentic throughput without hiding founder bottlenecks.

The founder should remain the accountable decision-maker for strategy, approval gates, sensitive claims, customer trust, and irreversible actions. Agents should absorb preparation, synthesis, routing, documentation, validation support, and execution work that can be reviewed safely.

This audit helps answer:

- Which founder decisions are blocking learning velocity?
- Which decisions must remain human?
- Which tasks can agents prepare or execute with review?
- Which repeated bottlenecks should become better templates, tickets, or future automations?
- Which automation ideas are unsafe or premature?

## Decision Taxonomy

### Founder-Only Decisions

These decisions require explicit founder/human approval. Agents may prepare evidence and options, but must not decide or execute autonomously.

| Decision area | Examples | Why founder-only |
|---|---|---|
| Strategic direction | Attack / Refine / Pivot / Kill, market choice, ICP choice, wedge choice | Changes venture focus and opportunity cost |
| Approval gates | Linear project/ticket creation, PR opening, merge, production deployment | Repository policy requires explicit approval |
| External trust | customer outreach, external communications, publishing, partnerships | Affects reputation and customer trust |
| Sensitive claims | claims about customers, metrics, validation, revenue, integrations, security, privacy, compliance | Must be source-backed and human-reviewed |
| Money movement | billing, payment collection, paid pilots, paid ads, pricing collection | Financial/legal/customer trust impact |
| Data and secrets | customer data, production data, credentials, private keys, confidential files | Privacy/security risk |
| Risk acceptance | accepting P0/P1 risk, privacy/security/legal/financial/compliance risk | High-impact or hard-to-reverse decisions |
| Scope expansion | broadening MVP, channel, platform, agent autonomy, or orchestration | Prevents sprawl and premature complexity |

### Agent-Assisted Work

Agents can perform this work when an approved ticket or human-approved planning request exists and normal review/handoff rules are followed.

| Work type | Agent can do | Required boundary |
|---|---|---|
| Evidence synthesis | summarize artifacts, identify gaps, compare supporting and contradictory evidence | no invented evidence or unsupported claims |
| Ticket preparation | draft Linear-ready ticket content, dependencies, acceptance criteria, risks | ticket creation still requires approval unless already explicitly approved |
| Repository updates | create or update scoped docs, templates, schemas, prompts, or code | one ticket, one branch, one PR, validation, review |
| Validation support | draft interview guides, scorecard questions, PMF metric plans, risk gates | no customer contact without approval |
| Review support | classify findings, suggest fixes, record residual risk | P0/P1 block merge |
| Handoff | write PR/Linear delivery update, validation summary, next action | no private data/secrets in handoff |
| Context routing | choose relevant docs, skills, tools, MCPs, or agents | must respect context boundary and source of truth |

### Future Automation Candidates

These may be candidates after repeated safe manual execution. They are not authorized by this audit.

| Candidate | Preconditions before automation | Current status |
|---|---|---|
| recurring readiness checks | repeated manual readiness failures with stable rules | future only |
| PR body and Linear handoff drafting | stable template usage and review acceptance | agent-assisted, not autonomous |
| batch metrics summary | enough merged tickets with consistent data | future only |
| context pack preparation | canonical source pointers and no hidden memory | future only |
| review routing | Codex/Claude reviewer roles and repository protections settled | future only |
| scheduled agents | safety policy, observability, stop conditions, and approval model | future only |
| OpenClaw or orchestrator dispatch | Codex + Claude Code baseline with comparable handoff metrics | future only |

## Bottleneck Signals

Track these signals during execution batches or weekly reviews.

| Signal | What it means | Response |
|---|---|---|
| tickets wait for unclear approval | approval requirement is too late or vague | clarify ticket approval field or sequencing |
| founder repeatedly restates context | repository memory or Linear handoff is insufficient | update canonical artifact or handoff template |
| PR review blocks dominate cycle time | review capacity is the bottleneck | improve review fallback, PR size, or reviewer role |
| same readiness gap repeats | ticket template or upstream artifact is missing detail | create focused governance/template follow-up |
| agents touch unexpected files | ticket scope or context routing is too loose | tighten expected write set and read context |
| follow-ups become vague | review findings are not being converted into actionable backlog | improve follow-up criteria |
| founder makes routine formatting or routing choices | agents can likely assist safely | add guidance or template, not automation first |
| external action approvals pile up | the pipeline is trying to move faster than trust gates allow | reduce external actions or batch approval decisions explicitly |

## Audit Template

```md
## Founder Bottleneck Audit

- Audit date:
- Reviewer:
- Period or ticket batch:
- Source tickets / PRs:
- Source handoffs:

## Summary
- Main bottleneck:
- Affected stage: Idea / MVP / Launch / Scale / Execution / Review / Learning
- Impact on learning velocity:
- Risk if ignored:

## Decision Classification

| Decision or task | Current owner | Classification | Evidence | Recommended change |
|---|---|---|---|---|
|  | Founder-only / Agent-assisted / Future automation candidate / Do not automate |  |  |  |

## Approval Bottlenecks
- Approval type:
- Where it appeared:
- Was it expected in the ticket? yes/no
- How to reduce delay without weakening the gate:

## Agent-Assist Opportunities
- Opportunity:
- Required source artifact:
- Required review:
- Stop condition:

## Future Automation Candidates
- Candidate:
- Required proof from manual operation:
- Required safety controls:
- Explicitly blocked until:

## Decisions
- Keep founder-only:
- Move to agent-assisted:
- Park for future automation:
- Do not automate:

## Follow-ups
- Follow-up needed:
- Reason:
- Suggested owner:
```

## Cadence

Run this audit:

- after 5 merged agentic tickets
- before adding a new agent role or capability
- before changing review or merge policy
- before evaluating scheduled agents, OpenClaw, Hermes, or any orchestrator
- whenever founder approval, review, or context synthesis becomes the dominant delay

Do not run it after every ticket unless a bottleneck is actively blocking execution.

## Rules

- Preserve `execution/approval-gates.md`.
- Treat automation as a later design question, not the default answer.
- Prefer better templates, clearer Linear tickets, and stronger handoffs before automation.
- Do not use conversational memory as the only evidence for a bottleneck.
- Do not automate external communication, outreach, billing, production deployment, data handling, or sensitive claims from this audit.
- Create specific follow-up tickets only when the bottleneck is concrete, recurring, and actionable.

## Relationship To Existing Artifacts

- Use `execution/agentic-operations-metrics.md` for throughput, review time, readiness, conflict, and handoff signals.
- Use `execution/ticket-pr-handoff-system.md` to inspect whether final handoffs are sufficient.
- Use `execution/multi-agent-operating-protocol.md` when routing work between Codex, Claude Code, and future agents.
- Use `execution/approval-gates.md` to preserve human-only approval boundaries.
- Use `knowledge/learning-record-policy.md` when a recurring bottleneck should become durable repository learning.
