# Capability Adapter Contract

This contract defines how Pipe Venture Builder should wrap external or heterogeneous capabilities when a future ticket authorizes adapter work.

It does not implement adapters, define executable `/pipe:*` commands, install tools, call external systems, or weaken approval gates.

Use this with:

- `capabilities/capability.schema.json`
- `architecture/capability-registry-policy.md`
- `architecture/canonical-schema-policy.md`
- `schemas/LearningRecord.schema.json`
- `execution/approval-gates.md`
- `execution/context-routing-protocol.md`
- `execution/multi-agent-operating-protocol.md`

## Purpose

External tools, MCPs, plugins, skills, services, and executors produce different output shapes.

A Pipe adapter exists to:

- inject the minimum required Pipe context into a capability request
- enforce constraints from the assigned Linear ticket and repository policy
- normalize capability output into a stable artifact
- capture validation evidence
- capture risk and unsupported-claim boundaries
- emit reusable learning when the capability result changes future execution

An adapter is a governance boundary, not just a convenience wrapper.

## What Counts As An Adapter

An adapter is a governed wrapper around a capability.

The capability registry classifies adapters with:

```txt
kind: adapter
```

Adapters may wrap:

- MCP connectors
- plugins
- local skills
- prompts
- services
- executors
- manual workflows

Adapters must not be created unless an approved Linear ticket names the capability, expected consumer, normalized output, validation plan, and approval boundary.

## Adapter Responsibilities

Every adapter must do these jobs.

### 1. Context Injection

The adapter must pass only the smallest useful context needed for the task.

Required context:

- assigned Linear ticket ID and URL
- ticket objective and acceptance criteria
- ticket type, priority, risk, labels, dependencies, and approval state
- relevant repository artifact paths
- relevant capability registry entry
- applicable approval gates
- expected output artifact path or destination
- known constraints and excluded scope

Optional context, only when needed:

- PR URL or branch name
- previous validation artifact
- source documents approved for synthesis
- related schema references
- previous LearningRecord references
- known blocker or handoff notes

Forbidden context unless explicitly approved:

- secrets, credentials, tokens, or private keys
- customer data
- production data
- private evidence
- legal, financial, compliance, privacy, or security-sensitive claims not already approved as source material
- broad repository dumps when a narrow artifact list is enough

### 2. Constraint Enforcement

The adapter must enforce constraints before calling or routing to a capability.

Minimum constraints:

- assigned ticket scope
- included and excluded scope
- lifecycle and routing rules from the capability registry
- approval gates from `AGENTS.md` and `execution/approval-gates.md`
- data boundary and sensitive-action boundary
- external mutation boundary
- paid-use boundary
- customer-evidence boundary
- source citation requirement when external claims are made

If any constraint is unclear, the adapter must stop and return a blocked output instead of improvising.

### 3. Normalized Output

The adapter must translate raw capability output into a stable Pipe artifact.

Required normalized output fields:

```txt
adapterId
adapterVersion
capabilityId
sourceCapabilityKind
linearTicketId
requestPurpose
inputContextSummary
constraintsApplied
rawOutputReference
normalizedSummary
structuredFindings
decisionsRequired
validationEvidence
risksCaptured
unsupportedClaims
learningRecordCandidate
followUpCandidates
residualRisk
adapterStatus
```

Allowed adapter status values:

```txt
ready
ready_with_warnings
blocked
failed
not_applicable
```

Do not treat raw capability output as canonical Pipe output.

### 4. Validation Evidence

The adapter must record how the output was checked.

Validation evidence should include:

- source artifacts inspected
- schemas checked, if any
- commands or manual checks executed
- citations used for external claims
- contradictions or uncertainty found
- reviewer or approval required
- reason validation was not possible, if applicable

Validation evidence does not need to prove the capability is correct. It must prove what was checked, what was not checked, and what uncertainty remains.

### 5. Risk Capture

The adapter must capture risk in a way future agents can use.

Required risk fields:

- risk category
- severity
- description
- mitigation
- owner
- whether it blocks the current ticket
- whether it requires a follow-up ticket

Use at least these categories:

```txt
approval
security
privacy
customer-data
cost
quality
reliability
vendor
scope
compliance
unsupported-claims
orchestration
```

### 6. Learning Capture

When the adapter discovers reusable learning, it must output a LearningRecord candidate instead of silently relying on conversational memory.

Use `schemas/LearningRecord.schema.json` as the canonical shape for durable learning.

Create a LearningRecord candidate when:

- a capability repeatedly succeeds or fails in a useful pattern
- a routing rule needs to change
- a capability produces an unexpected risk
- a validation method becomes reusable
- a future agent would otherwise need chat memory to understand the result

Do not create a LearningRecord candidate for one-off noise, stylistic preference, or unsupported speculation.

## Approval Requirements

Adapter work requires human approval when it:

- creates or changes an adapter contract that can mutate external systems
- calls an external tool with non-public, sensitive, customer, or production data
- uses paid capability access
- opens or merges PRs through a capability
- creates Linear projects or tickets
- contacts customers or sends external communications
- changes legal, financial, compliance, privacy, security, or sensitive claims
- treats research, model output, or synthesis as customer evidence
- schedules, dispatches, or orchestrates agents autonomously

An adapter must never use a capability registry entry as authorization by itself.

## Relationship To Capability Registry

The capability registry answers:

```txt
What capability exists, when should it be used, and what boundaries apply?
```

The adapter contract answers:

```txt
How should Pipe safely inject context, call or route to that capability, normalize output, validate evidence, capture risk, and preserve learning?
```

Before an adapter can be implemented, its capability entry must exist or be proposed in `capabilities/entries/`.

Adapter registry entries should reference:

- wrapped capability ID
- adapter owner
- input and output schemas
- approval triggers
- data boundary
- fallback path
- review cadence

## Relationship To Schema Policy

If adapter output will be consumed by multiple agents, commands, workflows, or future runtime systems, create a canonical JSON Schema under `schemas/` through a dedicated approved ticket.

Do not create a schema inside an adapter implementation unless the ticket explicitly authorizes schema work.

For PIP-154, the contract remains Markdown-only because executable command contracts and adapter schemas are not yet approved.

## Example Flow: `/pipe:discover`

This is a draft flow for future command-contract work. It is not an implemented command.

Goal:

```txt
Support upstream idea discovery before code.
```

Likely capability routing:

- PM Skills for discovery structure
- Consensus for source-backed research only when approved
- NotebookLM for approved source-set synthesis only when approved
- Linear MCP for ticket handoff only when approved

Input context:

- idea statement
- founder constraints
- C.O.N.T.R.O.L.E. dimensions
- current validation artifacts
- included and excluded scope
- target output path
- approval state for external research or synthesis

Constraints:

- no customer evidence may be invented
- no outreach may be performed
- no paid capability use without approval
- no private source upload without approval
- no implementation tasks may start until validation scope is accepted

Normalized output:

- idea summary
- assumptions
- unknowns
- evidence found
- evidence gaps
- risks
- validation questions
- next recommended Linear tasks
- LearningRecord candidate if reusable discovery learning appears

Validation evidence:

- repository artifacts read
- external sources cited, if any
- unanswered questions
- confidence and contradictions

Stop conditions:

- source artifacts are missing
- requested claim is sensitive or unsupported
- customer contact is implied
- capability would require approval not present in the ticket

## Example Flow: `/pipe:build`

This is a draft flow for future command-contract work. It is not an implemented command.

Goal:

```txt
Support scoped implementation after a ticket is ready for execution.
```

Likely capability routing:

- Codex or Claude Code as executor
- Superpowers for TDD, debugging, review, and verification discipline
- GitHub MCP or gh CLI for PR lifecycle when approved
- Linear MCP for ticket state and delivery handoff when approved
- Browser/Playwright for local UI validation when applicable

Input context:

- assigned Linear ticket
- branch and write-set ownership
- acceptance criteria
- validation plan
- relevant architecture notes
- capability registry entries
- approval status for PR and merge actions

Constraints:

- one ticket per branch
- one PR per ticket
- no unrelated refactors
- no overwrite of user or other-agent work
- P0/P1 review findings must be fixed before merge
- production, secrets, customer data, billing, and external communications remain gated

Normalized output:

- changed files
- validation results
- review findings by severity
- corrections applied
- unresolved findings and why
- follow-up candidates
- merge status
- residual risk
- LearningRecord candidate when execution reveals reusable learning

Validation evidence:

- tests, lint, build, or equivalent checks
- manual review summary
- PR review comments inspected
- browser evidence when applicable

Stop conditions:

- ticket is not approved or not ready
- write set overlaps another active branch without handoff
- required validation is impossible for a critical path
- P0/P1 findings remain open
- the implementation would require out-of-scope architecture, adapter, or command changes

## Minimum Adapter Definition Of Ready

Before implementing an adapter, the ticket must define:

- wrapped capability ID
- adapter owner
- intended consumers
- trigger or command surface
- input context allowed
- forbidden context
- normalized output destination
- validation plan
- approval triggers
- data boundary
- fallback path
- expected LearningRecord behavior

If any of these are missing, the adapter ticket is not ready.

## Minimum Adapter Definition Of Done

An adapter is done only when:

- it reads from an approved capability registry entry
- it injects only allowed context
- it enforces constraints before capability use
- it normalizes raw output
- it records validation evidence
- it captures risks and unsupported claims
- it emits or suppresses LearningRecord candidates intentionally
- it preserves approval gates
- it has at least one positive and one blocked-path example
- it has validation appropriate to its risk level

## Non-Goals

This contract does not:

- implement adapters
- define executable `/pipe:*` commands
- create MCP servers
- install plugins or skills
- vendor external repositories
- add runtime orchestration
- create schemas outside approved tickets
- authorize external actions
- approve paid capability use

## Maintenance Rule

Update this contract when:

- the capability registry schema changes
- adapter schemas are introduced
- `/pipe:*` command contracts are approved
- LearningRecord capture changes
- approval gates change
- a real adapter implementation exposes a recurring gap

Do not update this contract to bless a specific external tool. Tool approval belongs in the capability registry and the assigned Linear ticket.
