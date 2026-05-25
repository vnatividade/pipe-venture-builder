# Executor Capability Matrix

This matrix defines which executor should handle which kind of Pipe Venture Builder work.

Use it with `AGENTS.md`, `CLAUDE.md`, `execution/multi-agent-operating-protocol.md`, `execution/context-routing-protocol.md`, `execution/parallel-execution-governance.md`, `execution/worktree-isolation-protocol.md`, `architecture/agentic-multi-agent-codex-claude-plan.md`, and `architecture/orchestration-readiness-analysis.md`.

It is a routing aid, not an authorization layer. It does not weaken approval gates, authorize autonomous dispatch, select OpenClaw/Paperclip, create Linear tickets, open PRs, merge PRs, deploy, handle secrets, or contact customers.

## Core Decision

Executor choice should be based on ticket type, write set, risk, required tooling, context size, validation path, and approval ceiling.

Default rule:

- Codex is the default executor for repository-grounded implementation, documentation, architecture, GitHub, and Linear execution when the user has assigned the ticket in this environment.
- Claude Code is a peer executor for scoped code/documentation tasks when it can follow the shared protocols through `CLAUDE.md`.
- Human operator owns approvals, sensitive decisions, product judgment, external actions, and tie-breaking.
- Future OpenClaw/Paperclip is only a placeholder for later orchestration analysis.

## Approval Ceiling

No executor can exceed the approval gates in `AGENTS.md` and `execution/approval-gates.md`.

Human approval remains required before:

- creating Linear projects or tickets
- opening or merging PRs
- deploying production
- enabling billing, pricing collection, paid ads, or paid acquisition
- handling secrets, credentials, tokens, private keys, customer data, or production data
- contacting customers automatically
- sending external communications
- changing legal, financial, compliance, privacy, security, or sensitive claims
- making claims about customers, evidence, metrics, integrations, or market validation without source artifacts

Temporary thread-level approvals may authorize a specific executor to perform gated repository operations in the current cycle, but those approvals must be recorded in the PR or Linear handoff when used.

## Executor Matrix

| Executor | Entrypoint | Branch prefix | Best fit | Strengths | Limits | Approval ceiling | Restricted areas |
|---|---|---|---|---|---|---|---|
| Codex | Current Codex workspace, `AGENTS.md`, assigned Linear ticket | `codex/` | Repository edits, Git/GitHub/Linear execution, architecture docs, governance docs, validation docs, code tasks with local tests | Strong repository navigation, scoped patching, PR lifecycle, Linear handoff, review response, validation discipline | Must preserve user/other-agent local changes; needs explicit approval or recorded cycle approval for gated actions; should not use chat memory as durable source | May execute approved ticket scope and approved gated repo actions; cannot deploy, handle secrets/customer data, contact users, or change sensitive claims without explicit approval | Approval gates, production, secrets, customer data, billing, external communications, legal/compliance/security-sensitive claims |
| Claude Code | `CLAUDE.md`, shared execution protocols, assigned Linear ticket | `claude/` | Scoped code/documentation tasks, alternate implementation pass, pilot tickets, local reasoning on focused files | Useful peer executor, can increase throughput, can operate from the same common protocols | Must not create a second policy system; should not duplicate `AGENTS.md`; requires clear expected write set and handoff; should not run broad changes without serialized ownership | Same as Codex; must stop when approval is missing or ticket scope is ambiguous | Same as Codex, plus shared governance files unless explicitly assigned and serialized |
| Human operator | Linear, GitHub, local environment, current thread | `feature/`, `fix/`, `chore/`, or direct admin action when appropriate | Product decisions, approvals, prioritization, conflict resolution, sensitive judgment, external action ownership | Can approve gated actions, decide trade-offs, validate intent, resolve ambiguity | Manual bottleneck; decisions must be recorded for future agents | Highest authority below system/developer instructions and repository policy; still should preserve repository traceability | Should avoid untracked operational decisions that future agents need |
| Future OpenClaw/Paperclip placeholder | Future runtime evaluation ticket only | TBD | Future orchestration, dispatch, persistent runtime, cockpit, scheduled agent loops | Potential persistent coordination layer after Codex/Claude baseline matures | Not selected, not installed, not authorized, not part of MVP, not a current executor | No current approval ceiling; cannot act until a future approved orchestration-prep ticket defines it | All execution, dispatch, secrets, production, customer data, external actions, and merge automation until explicitly approved |

## Ticket-Type Fit

| Ticket type | Recommended primary executor | Acceptable secondary executor | Human role | Notes |
|---|---|---|---|---|
| `architecture` | Codex | Claude Code | Approve trade-offs when scope or risk expands | Serialize when changing ADRs, shared protocols, or high-risk architecture. |
| `documentation` | Codex or Claude Code | Either peer | Approve sensitive claims | Safe to parallelize only with disjoint files. |
| `prompt` | Codex | Claude Code | Approve autonomy or approval-gate implications | Do not duplicate or weaken `AGENTS.md`. |
| `skill` | Codex | Claude Code | Approve new capability boundaries | Requires clear trigger, stop conditions, and consumers. |
| `workflow` | Codex | Claude Code | Approve governance changes | Shared workflow files should be serialized. |
| `governance` | Codex | Claude Code as reviewer/drafter | Approve policy changes | Default `parallelizable:no` when approval gates or shared protocols change. |
| `code` | Codex or Claude Code | Either peer | Approve production/data/secrets risk | Choose based on local testability, write set, and implementation context. |
| `infrastructure` | Codex | Claude Code as secondary reviewer | Required for deploy/secrets/env changes | High caution; no production deployment without explicit approval. |
| `automation` | Codex | Claude Code as secondary reviewer | Required for state-mutating automation | External actions, scheduling, and autonomous mutation require approval. |
| `observability` | Codex | Claude Code | Approve production data access | Metrics must not invent customer or usage claims. |
| `product` | Human operator + Codex | Claude Code as drafter | Own product judgment and evidence quality | Agents may structure artifacts; humans own strategic decisions. |
| `validation` | Human operator + Codex | Claude Code as drafter | Own customer interaction approval | No customer outreach or data handling without approval. |
| `research` | Codex | Claude Code | Approve conclusions used for strategy | Cite sources when claims rely on external facts. |
| `orchestration-prep` | Codex | Human operator | Approve scope and timing | Future OpenClaw/Paperclip evaluation only after baseline maturity. |

## Executor Selection Rules

Choose Codex when:

- the task requires GitHub/Linear execution in this workspace
- local files need precise scoped edits
- the ticket includes PR creation, review handling, merge, and Linear handoff
- validation commands are available locally
- the work touches repository governance and must preserve current patterns

Choose Claude Code when:

- the ticket is scoped and has a clear expected write set
- the work can be isolated in a `claude/` branch or worktree
- the task benefits from a second implementation pass
- the ticket is a Claude Code pilot or compatibility check
- the shared protocols are enough to avoid custom instructions

Choose the human operator when:

- the next action is an approval
- the decision changes product strategy, scope, risk, pricing, legal/compliance, customer contact, or sensitive claims
- two agents disagree on ownership or interpretation
- evidence quality or market judgment is the main question
- an external communication or production action is involved

Do not choose future OpenClaw/Paperclip for current execution. It remains a future evaluation candidate only.

## Restricted Areas By Executor

### Codex

Codex must stop or request/record approval before gated actions. It must not:

- broaden a ticket beyond included scope
- edit unrelated dirty files
- erase user or other-agent work
- create unsupported evidence or metrics
- handle secrets or customer data without approval
- deploy, enable billing, run paid acquisition, or contact customers

### Claude Code

Claude Code has the same restrictions as Codex and must also:

- treat `CLAUDE.md` as an adapter, not a separate policy system
- use `execution/multi-agent-operating-protocol.md` as the shared workflow
- avoid changes to shared high-risk files unless explicitly assigned and serialized
- record handoff so Codex or a human can continue without chat memory

### Human Operator

The human operator should record durable decisions when future agents need them.

Do not leave critical decisions only in chat when they affect:

- approval gates
- product scope
- evidence interpretation
- customer or market claims
- orchestration readiness
- branch protection or merge policy

### Future OpenClaw/Paperclip Placeholder

Future runtime work must stay behind the future orchestration-prep ticket.

It may not:

- dispatch agents
- create worktrees
- mutate Linear or GitHub
- merge PRs
- run scheduled jobs
- access secrets, customer data, production, or external systems
- become an MVP dependency

## Five-Ticket Classification Dry Run

| Recent ticket | Actual executor | Recommended executor | Match? | Rationale |
|---|---|---|---|---|
| PIP-166 - MAYA/PMF validation framework | Codex | Codex | Yes | Validation/governance documentation with repo edits, PR, review, and Linear handoff. |
| PIP-167 - Proprietary Data Moat strategy | Codex | Codex | Yes | Architecture/knowledge-base work requiring careful sensitive-data boundaries and PR review. |
| PIP-168 - API dependency risk assessment | Codex | Codex | Yes | Architecture and PRD template alignment with review corrections across existing docs. |
| PIP-169 - Global AI benchmark cadence | Codex | Codex | Yes | Research artifact with external-source discipline and repository indexing. |
| PIP-170 - AI moat case pattern library | Codex | Codex | Yes | Research-to-validation artifact with public case boundaries and Linear/GitHub lifecycle. |

Observed result: Codex was appropriate for these recent tickets because the work combined repository edits, GitHub PR operations, review handling, validation, and Linear updates in one controlled workspace.

Potential future comparison: a narrow documentation-only ticket with a disjoint write set can be routed to Claude Code once worktree isolation and handoff expectations are active.

## Future Orchestrator Inputs

A future orchestrator should read this matrix before assigning work.

This matrix addresses the executor-registry gap identified in `architecture/orchestration-readiness-analysis.md`. It is still declarative only; it does not implement dispatch, event consumption, conflict locking, or automated readiness validation.

Minimum routing inputs:

- Linear ticket type
- priority and risk
- approval requirement
- expected write set
- restricted files
- dependency list
- parallelization class
- required validations
- required handoff destination
- executor availability

Minimum routing outputs:

- selected executor
- branch prefix
- worktree requirement
- blocked files or domains
- merge-order note
- review requirement
- escalation path

## Monitoring Signals

Track these signals in PRs and Linear handoffs:

- executor selected vs executor recommended
- tickets reassigned because write set changed
- merge conflicts by executor pair
- stale worktrees by executor
- P0/P1 findings caused by executor mismatch
- PRs touching restricted files without explicit ownership
- handoffs missing executor, write set, or approval status

These signals should feed future updates to `execution/agentic-operations-metrics.md` and future orchestration readiness analysis.

## Done Criteria

This matrix is working when:

- humans can choose Codex, Claude Code, human operator, or future-placeholder routing without relying on chat memory
- each executor has clear branch prefix, strengths, limits, restricted areas, and approval ceiling
- future orchestrator work has enough fields to route tickets later
- OpenClaw/Paperclip remains visible but not prematurely selected
- recent ticket classification matches actual execution or exposes a clear routing improvement
