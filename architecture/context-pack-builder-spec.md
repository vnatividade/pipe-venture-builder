# Context Pack Builder Spec

## Purpose

This spec defines the Context Pack contract for Pipe Venture Builder agents.

A Context Pack is the smallest useful, source-linked bundle of context needed for Codex, Claude Code, or a future orchestrator to execute a Linear ticket without relying on conversational memory or broad repository scans.

This spec does not implement retrieval, embeddings, pgvector, automation, or MCP tools.

## Core Decision

The Context Pack Builder must package context from canonical and operational sources into a bounded, explainable artifact.

It must:

- include the ticket goal and acceptance criteria
- include relevant decisions, known failures, similar ideas, recommended capabilities, constraints, and canonical rules
- preserve source links for every included item
- distinguish canonical rules from candidate learnings or operational handoffs
- enforce size and relevance limits
- be usable by Codex, Claude Code, and a future orchestrator

It must not:

- treat retrieval results as canonical without source artifacts
- include broad repository dumps
- include secrets, credentials, private customer data, or production data
- infer customer evidence, metrics, integrations, or approvals from chat history
- promote learnings into rules automatically

## Source Inputs

The builder may use these source classes.

| Source class | Examples | Required handling |
|---|---|---|
| Assigned Linear ticket | Ticket ID, title, URL, status, labels, dependencies, acceptance criteria | Always include the task goal, scope, excluded scope, dependencies, and approval state. |
| Canonical repository docs | `AGENTS.md`, `execution/*.md`, `architecture/*.md`, `knowledge/*.md`, `validation/*.md`, `product/*.md` | Include only sections relevant to the ticket type and expected write set. |
| Capability Registry | `capabilities/entries/*.json`, `capabilities/routing-examples.md`, `architecture/capability-registry-policy.md` | Include recommended capabilities and forbidden capabilities with source paths. |
| Knowledge records | KDRs, DARs, RCAs, LearningRecord candidates, customer-language memory, decision conflict notes | Include promotion level, sensitivity status, and supersession/conflict notes. |
| GitHub delivery evidence | PR URLs, review summaries, merge commits, validation results | Include only when prior delivery evidence informs the current ticket. |
| Linear handoffs | Final ticket comments, blockers, follow-up links | Include only when the handoff changes execution or dependency understanding. |

Retrieval systems such as pgvector may help find candidates later, but the context pack must still point back to canonical sources.

## Contract Shape

The Context Pack should be representable as Markdown, JSON, or YAML. The minimum shape is:

```yaml
contextPackVersion: "0.1.0"
generatedAt: "YYYY-MM-DD"
ticket:
  id: "PIP-000"
  title: ""
  url: ""
  status: ""
  priority: ""
  labels: []
  objective: ""
  includedScope: []
  excludedScope: []
  acceptanceCriteria: []
  dependencies: []
  approvalState: ""
goal:
  summary: ""
  expectedArtifacts: []
  expectedWriteSet: []
canonicalRules:
  - title: ""
    source: ""
    reasonIncluded: ""
    priority: "must|should|reference"
relevantDecisions:
  - id: ""
    source: ""
    status: ""
    summary: ""
    implicationForTicket: ""
knownFailures:
  - id: ""
    source: ""
    summary: ""
    preventionRule: ""
similarIdeasOrPatterns:
  - title: ""
    source: ""
    relevance: ""
recommendedCapabilities:
  - capabilityId: ""
    source: ""
    useWhen: ""
    doNotUseWhen: ""
    approvalNotes: ""
constraints:
  included: []
  excluded: []
  approvalGates: []
  sensitiveDataBoundaries: []
validationPlan:
  requiredChecks: []
  manualChecks: []
  evidenceExpected: []
handoffRequirements:
  linearUpdateRequired: true
  prRequired: true
  reviewRequired: true
  mergeRules: []
freshness:
  staleAfter: ""
  staleWhen: []
sourceManifest:
  - pathOrUrl: ""
    sourceType: ""
    canonicality: "canonical|operational|candidate|derived"
    lastKnownStatus: ""
omittedContext:
  - source: ""
    reason: ""
risks:
  - risk: ""
    mitigation: ""
builderNotes: ""
```

## Required Sections

Every Context Pack must include:

- `ticket`
- `goal`
- `canonicalRules`
- `constraints`
- `validationPlan`
- `sourceManifest`
- `omittedContext`

These sections prevent the pack from becoming a vague summary with no execution guardrails.

## Conditional Sections

Include these only when relevant:

| Section | Include when |
|---|---|
| `relevantDecisions` | A KDR, DAR, ADR, or architecture decision changes how the ticket should be executed. |
| `knownFailures` | An RCA, failed gate, repeated review finding, or incident affects the ticket. |
| `similarIdeasOrPatterns` | Product, validation, research, or reusable execution patterns reduce ambiguity. |
| `recommendedCapabilities` | The ticket may use skills, MCPs, plugins, external tools, agents, or workflows. |
| `handoffRequirements` | The ticket changes repository artifacts, opens a PR, updates Linear, or creates follow-ups. |
| `freshness` | External research, volatile capability behavior, product claims, or changing governance is involved. |
| `risks` | Any risk could affect approval gates, validation, quality, security, privacy, customer evidence, or future orchestration. |

## Relevance Rules

The builder should include context only when it passes at least one rule:

1. It is required by `AGENTS.md`, the Linear ticket, or the relevant execution protocol.
2. It constrains the expected write set.
3. It changes acceptance, validation, review, or merge behavior.
4. It prevents a known failure from recurring.
5. It selects or forbids a capability.
6. It provides a canonical decision that future agents must obey.
7. It supplies source-backed product, validation, or research evidence needed for the ticket.

If a source is merely interesting, omit it and record the omission reason.

## Size Limits

Default limits:

| Item | Limit |
|---|---:|
| Total pack summary | 1,500 words |
| Canonical rules | 7 items |
| Relevant decisions | 5 items |
| Known failures | 5 items |
| Similar ideas or patterns | 5 items |
| Recommended capabilities | 5 items |
| Source manifest | 20 items |
| Direct quoted text per source | Avoid by default; summarize and link |

Exceptions require a stated reason in `builderNotes`.

The pack should link to source files rather than copying long sections.

## Priority Order For Inclusion

When the pack is too large, keep context in this order:

1. Assigned Linear ticket.
2. Approval gates and repository authority rules.
3. Expected write set and nearest canonical architecture/governance docs.
4. Acceptance criteria and validation plan.
5. Blocking dependencies.
6. Known failures that directly affect the ticket.
7. Relevant decisions.
8. Recommended capabilities and routing rules.
9. Similar patterns.
10. Optional background.

Drop optional background first.

## Capability Recommendations

Recommended capabilities must come from the Capability Registry or an explicitly approved ticket.

Each recommendation must state:

- capability ID or name
- source path
- why it is relevant
- when to use it
- when not to use it
- approval notes
- fallback if unavailable

Do not recommend a capability only because it exists in the current runtime.

## Canonicality Rules

Context items must be tagged as:

- `canonical`: reviewed repository artifact, schema, accepted KDR/DAR/ADR, or approved policy
- `operational`: Linear ticket, PR, review, merge, validation, or handoff state
- `candidate`: LearningRecord candidate, proposed follow-up, unresolved decision, or unpromoted pattern
- `derived`: summary generated from canonical or operational sources

Derived summaries must link to their sources and must not become new rules by themselves.

## Sensitive Data Rules

The Context Pack must exclude:

- secrets, credentials, tokens, private keys
- customer data not approved for this ticket
- production data
- private evidence
- legal, financial, compliance, privacy, or security-sensitive claims not already approved as source material
- unsupported customer, revenue, willingness-to-pay, integration, or metric claims

If sensitive context appears necessary, the builder must stop and return a blocker rather than include it.

## Output Consumers

### Codex

Codex should use the pack to:

- identify the ticket scope
- select the smallest read set
- avoid unrelated local changes
- choose validation commands
- prepare PR and Linear handoff evidence

### Claude Code

Claude Code should use the same pack to:

- follow the same repository authority and approval boundaries
- avoid relying on Claude-specific memory
- preserve branch and PR governance
- produce equivalent handoff quality

### Future Orchestrator

A future orchestrator should use the pack to:

- assign the ticket to the right executor
- detect blocked dependencies
- avoid file ownership conflicts
- select capabilities
- verify that validation and handoff expectations are explicit
- avoid dispatching when approval or sensitive-data boundaries are unclear

## Manual Build Procedure

Until automation exists:

1. Read the assigned Linear ticket.
2. Identify ticket type, expected artifact, expected write set, risk, dependencies, and approval state.
3. Read `AGENTS.md`.
4. Read `execution/context-routing-protocol.md`.
5. Read the nearest architecture/governance/source docs required by ticket type.
6. Add only source-linked rules, decisions, failures, capabilities, and constraints that affect execution.
7. Record omitted context and why it was left out.
8. Define validation checks.
9. Confirm the pack stays within size limits.

## Manual Context Pack Example

Sample ticket: PIP-160 - Specify Context Pack Builder contract.

```yaml
contextPackVersion: "0.1.0"
generatedAt: "2026-05-26"
ticket:
  id: "PIP-160"
  title: "PVB-KNOW-016 - Specify Context Pack Builder contract"
  url: "https://linear.app/pipe-venture-builder/issue/PIP-160/pvb-know-016-specify-context-pack-builder-contract"
  status: "In Progress"
  priority: "P2"
  labels:
    - "type:architecture"
    - "type:knowledge-base"
    - "risk:medium"
  objective: "Specify the Context Pack contract used by agents before retrieval automation exists."
  includedScope:
    - "Define Context Pack fields."
    - "Define sources: canonical docs, Linear ticket, capability registry, and knowledge records."
    - "Define max-size and relevance rules."
  excludedScope:
    - "Retrieval implementation."
    - "Embeddings."
  acceptanceCriteria:
    - "Context Pack includes goal, relevant decisions, similar ideas, known failures, recommended capabilities, constraints, and canonical rules."
    - "Contract prevents context bloat."
    - "Output can be used by Codex, Claude Code, and future orchestrator."
  dependencies:
    - "PIP-152 Capability Registry schema"
    - "PIP-159 Knowledge Runtime architecture"
  approvalState: "Repository PR/review/merge approved for this execution cycle by project lead; no sensitive data involved."
goal:
  summary: "Create architecture/context-pack-builder-spec.md and link it from architecture/README.md."
  expectedArtifacts:
    - "architecture/context-pack-builder-spec.md"
  expectedWriteSet:
    - "architecture/context-pack-builder-spec.md"
    - "architecture/README.md"
canonicalRules:
  - title: "Markdown is canonical memory; pgvector is recall."
    source: "architecture/knowledge-runtime-architecture.md"
    reasonIncluded: "Defines the source-of-truth boundary this pack must preserve."
    priority: "must"
  - title: "Context routing should load the smallest useful context."
    source: "execution/context-routing-protocol.md"
    reasonIncluded: "Prevents context bloat and broad repository scans."
    priority: "must"
relevantDecisions:
  - id: "PIP-159"
    source: "architecture/knowledge-runtime-architecture.md"
    status: "Done"
    summary: "Context packs are a future ticket hook from the Knowledge Runtime architecture."
    implicationForTicket: "This spec should define packaging only, not retrieval infrastructure."
knownFailures:
  - id: "RCA-001"
    source: "knowledge/rca-001-pr-flow-regression-root-cause.md"
    summary: "Review objects can exist without substantive review."
    preventionRule: "Context pack handoff requirements should preserve review-quality evidence."
similarIdeasOrPatterns:
  - title: "Capability routing examples"
    source: "capabilities/routing-examples.md"
    relevance: "Shows how recommended capabilities and non-use cases should be normalized."
recommendedCapabilities:
  - capabilityId: "capability.external.codex"
    source: "capabilities/entries/capability.external.codex.json"
    useWhen: "Repository-grounded architecture documentation and PR lifecycle."
    doNotUseWhen: "Product validation or external research is the primary task."
    approvalNotes: "PR/merge approved for this cycle by project lead."
constraints:
  included:
    - "Architecture documentation only."
  excluded:
    - "No retrieval implementation."
    - "No embeddings."
  approvalGates:
    - "PR review before merge."
    - "Human approval required for canonical rule promotion."
  sensitiveDataBoundaries:
    - "No secrets, customer data, production data, or unsupported claims."
validationPlan:
  requiredChecks:
    - "git diff --check"
    - "rg acceptance terms in architecture/context-pack-builder-spec.md"
  manualChecks:
    - "Manual sample context pack included."
    - "No retrieval or embedding implementation introduced."
  evidenceExpected:
    - "PR body and Linear handoff list checks and review state."
sourceManifest:
  - pathOrUrl: "architecture/knowledge-runtime-architecture.md"
    sourceType: "architecture"
    canonicality: "canonical"
    lastKnownStatus: "merged by PIP-159"
  - pathOrUrl: "execution/context-routing-protocol.md"
    sourceType: "execution"
    canonicality: "canonical"
    lastKnownStatus: "existing"
  - pathOrUrl: "capabilities/routing-examples.md"
    sourceType: "capability"
    canonicality: "canonical"
    lastKnownStatus: "existing"
omittedContext:
  - source: "Full capabilities schema"
    reason: "Useful for future automation, but too detailed for this architecture-only spec."
risks:
  - risk: "Spec becomes too large for agents to use."
    mitigation: "Add strict size limits, inclusion rules, and omission tracking."
builderNotes: "Manual pack validates the contract shape without implementing automation."
```

## Validation Expectations

For this ticket, validation should confirm:

- the spec includes goal, relevant decisions, similar ideas, known failures, recommended capabilities, constraints, and canonical rules
- max-size and relevance rules are explicit
- output consumers include Codex, Claude Code, and a future orchestrator
- a manual context pack exists for a sample ticket
- retrieval implementation and embeddings remain out of scope

## Relationship To Future Work

Future tickets may:

- create a machine-readable `ContextPack` schema
- implement a manual `/pipe:context-pack` command
- connect retrieval candidates from pgvector
- expose `get_context_pack` through a future Knowledge MCP
- evaluate context-pack quality against agent handoff and execution metrics

Those tickets must preserve this spec's source-of-truth and anti-bloat boundaries.
