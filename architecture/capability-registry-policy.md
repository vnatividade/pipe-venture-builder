# Capability Registry Policy

This policy defines how Pipe Venture Builder records internal and external capabilities that agents may use, route to, wrap, or avoid.

The canonical registry entry contract is `capabilities/capability.schema.json`.

This policy does not vendor external repositories, install tools, call MCPs, create adapters, approve paid usage, or authorize external actions.

## Purpose

The Capability Registry exists so agents can answer:

- What capability is available or proposed?
- Is it internal, external, hybrid, executor, MCP, plugin, skill, prompt, workflow, adapter, model, or service?
- When should an agent use it?
- When should an agent avoid it?
- What inputs and outputs are expected?
- Which schemas or artifacts does it produce or consume?
- What tool access, credentials, network access, costs, and risks are involved?
- What approval and review gates apply?

The registry should help Pipe orchestrate capabilities without copying whole external systems into the repository.

## Registry Location

Registry contracts and future entries live under:

```txt
capabilities/
```

Initial contract:

```txt
capabilities/capability.schema.json
```

This is a domain-specific registry path approved by PIP-152. General cross-domain schemas still live under `schemas/` unless a ticket explicitly chooses a domain-specific path.

## What Counts As A Capability

Use a capability entry for reusable resources that agents may invoke, consult, route to, or wrap.

Supported kinds:

| Kind | Meaning |
|---|---|
| `capability` | Broad reusable ability that may include tools, workflows, or methods. |
| `adapter` | Governed wrapper that normalizes inputs/outputs around another capability. |
| `executor` | Agent or runtime that can execute scoped work, such as Codex or Claude Code. |
| `mcp` | MCP server or connector. |
| `plugin` | Plugin-provided capability. |
| `skill` | Triggered reusable workflow or local skill. |
| `prompt` | Reusable prompt pattern or instruction bundle. |
| `workflow` | Repository-defined process or operating protocol. |
| `model` | Model or model family, when model choice itself is a capability. |
| `service` | External product, API, or SaaS capability. |

## Required Registry Fields

Every capability entry must capture:

- identity: schema version, capability ID, name, summary
- classification: kind, origin, lifecycle
- ownership: primary owner, supporting owner, reviewer
- source: source type, source name, URL/path, license or terms, version/date
- routing: use cases, non-use cases, pipeline stages, ticket types, consumers, fallback
- inputs and outputs
- related schemas
- tool access: access type, credentials, network, external mutation, allowed and forbidden operations
- cost: cost type, expected level, driver, paid-use approval
- risks and mitigations
- governance: approval triggers, data boundary, sensitive-action boundary, logging, update policy
- review: cadence, status, notes
- examples: at least one expected use and non-use scenario

## Lifecycle States

| State | Meaning |
|---|---|
| `proposed` | Candidate capability; not approved for operational use. |
| `pilot` | Limited use in scoped tickets with review. |
| `approved` | Usable under the recorded routing and governance limits. |
| `restricted` | Usable only with explicit approval or special conditions. |
| `deprecated` | Should not be used for new work. |
| `blocked` | Must not be used. |

## Routing Rules

Agents should use registry entries as routing guidance, not as authorization.

Agents must proactively consider registered capabilities when a request, assigned ticket, or pipeline phase implies a capability. This should happen internally. The user should receive the next clear question, action, or artifact, not a menu of tools.

Before using a capability:

1. Confirm the assigned Linear ticket allows the capability category.
2. Confirm the capability lifecycle is `pilot`, `approved`, or explicitly approved for this use.
3. Confirm required credentials, network access, external state mutation, paid use, and data boundaries.
4. Confirm the capability's `useWhen` matches the task.
5. Confirm no `doNotUseWhen` rule applies.
6. If unavailable or unauthorized, follow the recorded fallback.

Do not use a capability only because it is available in the current runtime.

When multiple capabilities match, choose the smallest useful set:

1. Select the primary executor or workflow capability.
2. Add one supporting capability only when it changes the quality or safety of the output.
3. Add external research, publication, browser, repository, or workspace-mutation capabilities only when the ticket scope and approval boundary allow them.
4. Record selected, rejected, and blocked capabilities in the resulting artifact, PR, or Linear handoff when the choice affects future agents.

Default proactive routing examples:

| Need | Candidate capabilities | Boundary |
|---|---|---|
| Product discovery, interview planning, PRD inputs, value proposition, GTM, or assumption mapping | `capability.external.pm-skills` | Product reasoning only; not customer evidence. |
| Source-backed scientific, academic, technical, or market research | `capability.external.consensus` | Cite sources and limits; not customer validation proof. |
| Approved source-set synthesis | `capability.external.notebooklm` | Use only approved non-sensitive source sets. |
| Approved documentation search, publishing, update, or registration in Notion | `capability.external.notion-mcp` | Notion is not the source of truth; use `knowledge/notion-knowledge-base-policy.md`; publication is gated. |
| Ticket state, delivery handoff, blockers, PR links, or follow-ups | `capability.external.linear-mcp` | Mutate Linear only within approved scope. |
| GitHub PR lifecycle, issue/PR metadata, comments, merge-state checks, or repository references | `capability.external.github-mcp` | Mutate GitHub only within approved scope. |
| Code/workflow execution discipline, TDD, debugging, review, or verification | `capability.external.superpowers` | Guidance only; cannot broaden scope. |
| UI validation, browser-visible workflows, screenshots, or local app checks | `capability.external.browser-playwright` | Use only for approved UI/test scope. |
| Repository-grounded execution | `capability.external.codex` or `capability.external.claude-code` | Respect executor matrix, branch ownership, and approval gates. |
| Future runtime orchestration analysis | `capability.future.openclaw-paperclip` | Future evaluation only; no current dispatch or automation. |

## Approval Rules

Human approval is required before a capability is used for:

- creating Linear projects or tickets
- opening or merging PRs, unless the current thread or ticket has explicit scoped approval
- mutating external systems
- paid usage, billing, pricing, paid ads, or paid acquisition
- customer outreach or external communication
- handling secrets, credentials, customer data, production data, or private evidence
- changing legal, financial, compliance, privacy, security, or sensitive claims
- treating research, model output, or synthetic data as customer evidence

Registry entries must record these approval triggers even when the capability is otherwise approved.

## Review And Update Policy

Create or update a registry entry only through an approved Linear ticket and PR.

Review should check:

- kind and origin are accurate
- routing is narrow enough
- non-use cases are explicit
- inputs and outputs are concrete
- schemas are linked when available
- tool access does not hide credential, network, mutation, or paid-use risk
- data boundaries are explicit
- external capability use does not create unsupported claims
- fallback is realistic

When a capability changes behavior, terms, access, cost, or risk, update the registry before relying on it for new operational work.

## Relationship To Other Repository Artifacts

Use this policy with:

- `architecture/executor-capability-matrix.md`
- `execution/context-routing-protocol.md`
- `.codex/agents/agent-skill-trigger-rules.md`
- `.agents/skills/core-skill-contracts.md`
- `execution/approval-gates.md`
- `execution/multi-agent-operating-protocol.md`
- `schemas/LearningRecord.schema.json`
- `knowledge/notion-knowledge-base-policy.md`

The executor matrix chooses who should execute. The capability registry records what resources those executors may use and under what constraints.

## PIP-152 Example Boundary

PIP-152 includes example entries inside `capabilities/capability.schema.json` only to validate the schema shape:

- one internal workflow capability
- one external capability candidate

Those examples do not register operational capability entries, approve tool use, create adapters, or call external tools. Operational registration belongs to later tickets such as PIP-153.
