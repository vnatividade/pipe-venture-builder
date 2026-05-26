# Knowledge MCP Spec

## Purpose

This document specifies a future Knowledge MCP contract for Pipe Venture Builder.

The MCP should expose governed knowledge operations to Codex, Claude Code, and future orchestrators without letting agents couple directly to database tables, vector indexes, local files, or hidden memory.

This is a specification only. It does not implement an MCP server, database access, embeddings, retrieval service, automation, or tool registration.

## Core Boundary

The Knowledge MCP is an interface boundary, not the memory itself.

It must preserve these rules:

- Repository Markdown remains canonical memory.
- Linear and GitHub remain operational execution state.
- pgvector or any retrieval backend remains recall infrastructure only.
- Every response must include source paths or URLs.
- Every write must create a candidate, draft, or operational record unless a human-approved ticket and PR promote it.
- Direct database access by agents is explicitly disallowed.

## Non-Goals

This spec does not:

- implement MCP tools
- define transport, hosting, deployment, auth provider, or runtime packaging
- create direct database queries for agents
- create write access to repository files, Linear, GitHub, or vector stores
- create an embeddings provider integration
- allow autonomous promotion to canonical rules
- weaken approval gates in `AGENTS.md` or `execution/approval-gates.md`

## Candidate Tools

| Tool | Type | Purpose | Mutates canonical memory? | Requires human approval before execution? |
|---|---|---|---:|---:|
| `search` | Read | Retrieve source-linked knowledge candidates. | No | No, unless source scope includes sensitive/private data. |
| `get_context_pack` | Read | Build a bounded Context Pack for a ticket. | No | No, unless sensitive/private data is requested. |
| `write_learning` | Write candidate | Propose a LearningRecord candidate. | No | Yes if sensitive data, customer evidence, or policy-impacting claims are involved. |
| `write_decision` | Write candidate | Draft a KDR/DAR or decision candidate. | No | Yes when decision changes strategy, architecture, policy, approval gates, or sensitive claims. |
| `write_capability` | Write candidate | Propose or update a capability registry candidate. | No | Yes when it would authorize external tools, paid use, credentials, mutation, or sensitive data. |
| `write_run` | Write operational | Record execution/run evidence for a ticket. | No | Yes if it mutates Linear/GitHub or includes sensitive/private data. |
| `promote_to_canonical` | Promotion request | Prepare a promotion request for a canonical artifact. | Not directly | Always. |

No tool may silently mutate canonical repository artifacts.

## Shared Input Envelope

Every tool request should include:

```yaml
requestId: ""
actor:
  agent: "codex|claude-code|human|future-orchestrator|other"
  role: "executor|reviewer|architect|knowledge-curator|operator|orchestrator"
linear:
  ticketId: ""
  ticketUrl: ""
  approvalState: ""
scope:
  purpose: ""
  includedScope: []
  excludedScope: []
  sourceAllowlist: []
  sourceDenylist: []
  sensitiveDataExpected: false
  customerDataExpected: false
  productionDataExpected: false
constraints:
  maxResults: 10
  maxContextWords: 1500
  requireSourceLinks: true
  allowCandidateRecords: true
  allowCanonicalMutation: false
```

Requests without a Linear ticket ID should be treated as read-only exploration unless a human explicitly approves otherwise.

## Shared Output Envelope

Every response should include:

```yaml
requestId: ""
status: "ok|partial|blocked|denied|failed"
summary: ""
results: []
sourceManifest:
  - pathOrUrl: ""
    sourceType: ""
    canonicality: "canonical|operational|candidate|derived|synthetic"
    promotionLevel: "L0|L1|L2|L3|L4|not_applicable"
    sensitivity: "public_repo|internal|sensitive_excluded|synthetic|unknown"
approval:
  required: false
  status: "not_required|missing|pending|approved|rejected"
  reason: ""
risks:
  - severity: "P0|P1|P2|P3"
    description: ""
    mitigation: ""
omitted:
  - source: ""
    reason: ""
audit:
  toolName: ""
  actor: ""
  ticketId: ""
  createdAt: "YYYY-MM-DDTHH:MM:SSZ"
```

The response must make blocked and denied states explicit.

## Tool Contracts

### `search`

Purpose:

- Find relevant source-linked knowledge candidates across repository docs, schemas, Linear handoffs, GitHub PR summaries, capability entries, and future recall indexes.

Inputs:

```yaml
query: ""
recordTypes:
  - "learning|decision|capability|idea|run|failure|pattern"
canonicality:
  - "canonical|operational|candidate|derived"
promotionLevels:
  - "L0|L1|L2|L3|L4|not_applicable"
maxResults: 10
```

Outputs:

- Shared output envelope.
- Each result must include title, summary, source path or URL, canonicality, promotion level, sensitivity, and reason included.

Schema references:

- `architecture/knowledge-runtime-architecture.md`
- `schemas/LearningRecord.schema.json`
- `capabilities/capability.schema.json`

Restrictions:

- Must not return content from forbidden or sensitive sources.
- Must not represent a candidate as a canonical rule.
- Must not expose raw database identifiers as the primary source of truth.

### `get_context_pack`

Purpose:

- Build a bounded Context Pack for a Linear ticket.

Inputs:

```yaml
ticketId: ""
ticketUrl: ""
ticketType: ""
expectedWriteSet: []
maxContextWords: 1500
includeCapabilities: true
includeKnownFailures: true
includeSimilarPatterns: true
```

Outputs:

- A Context Pack following `architecture/context-pack-builder-spec.md`.
- Shared output envelope metadata.

Schema references:

- `architecture/context-pack-builder-spec.md`
- `execution/context-routing-protocol.md`
- `architecture/knowledge-runtime-architecture.md`

Restrictions:

- Must obey Context Pack size and relevance rules.
- Must include omitted-context notes.
- Must not include secrets, customer data, production data, or unsupported claims.

### `write_learning`

Purpose:

- Propose a LearningRecord candidate when execution, validation, review, incident, or capability use produces reusable learning.

Inputs:

```yaml
learningRecordCandidate:
  schemaVersion: "0.1.0"
  title: ""
  learningType: ""
  source: {}
  scope: {}
  agent: {}
  capability: {}
  confidence: {}
  importance: {}
  tags: []
  summary: ""
  insight: ""
  evidence: []
  recommendation: {}
  promotion: {}
  sensitivity: {}
```

Outputs:

- Candidate record ID or draft artifact reference.
- Validation issues against the schema.
- Approval requirements.

Schema references:

- `schemas/LearningRecord.schema.json`
- `knowledge/learning-record-policy.md`

Restrictions:

- Must set `promotion.humanReviewRequiredForPromotion` to `true`.
- Must set `promotion.automaticPromotionAllowed` to `false`.
- Must not promote to a canonical rule.
- Must block if sensitive/customer/private data lacks approval.

### `write_decision`

Purpose:

- Draft a KDR/DAR or decision candidate for human review.

Inputs:

```yaml
decisionCandidate:
  decisionId: ""
  decisionType: ""
  status: "draft|proposed"
  context: ""
  optionsConsidered: []
  recommendedOption: ""
  evidence: []
  risks: []
  revisitTrigger: ""
  supersedes: []
  conflictsWith: []
```

Outputs:

- Draft decision reference.
- Conflict scan summary.
- Human approval requirement.

Schema references:

- `knowledge/kdr-dar-template.md`
- `knowledge/decision-conflict-protocol.md`
- `architecture/technical-decision-guide.md`

Restrictions:

- Must not mark a decision as accepted.
- Must not supersede existing decisions without human approval and PR.
- Must not change strategy, approval gates, legal/compliance/security-sensitive claims, or product claims automatically.

### `write_capability`

Purpose:

- Propose a capability entry or capability update candidate.

Inputs:

```yaml
capabilityCandidate:
  schemaVersion: ""
  capabilityId: ""
  name: ""
  kind: ""
  origin: ""
  lifecycle: "proposed|pilot|approved|restricted|deprecated|blocked"
  routing: {}
  inputs: {}
  outputs: {}
  risks: {}
  governance: {}
```

Outputs:

- Candidate capability reference.
- Schema validation issues.
- Approval and risk notes.

Schema references:

- `capabilities/capability.schema.json`
- `architecture/capability-registry-policy.md`
- `architecture/capability-adapter-contract.md`

Restrictions:

- Must not approve a capability for operational use.
- Must not authorize credentials, paid use, external mutation, customer data, or production access.
- Must not vendor external tools.

### `write_run`

Purpose:

- Record execution evidence for a ticket run, such as branch, PR, validation, review state, merge state, residual risk, and follow-ups.

Inputs:

```yaml
runRecord:
  ticketId: ""
  branch: ""
  pullRequestUrl: ""
  mergeCommit: ""
  validations: []
  review:
    requested: false
    p0: 0
    p1: 0
    p2: 0
    p3: 0
    unresolvedBlockingFindings: []
  followUps: []
  residualRisk: ""
```

Outputs:

- Operational run summary.
- Suggested Linear/PR handoff body.
- DeliveryEvidence compatibility notes.

Schema references:

- `schemas/DeliveryEvidence.schema.json`
- `execution/ticket-pr-handoff-system.md`
- `execution/pipe-check-command-spec.md`

Restrictions:

- Must not mutate Linear or GitHub unless the tool implementation has explicit approved permission.
- Must not fabricate validations, reviews, merge state, metrics, or evidence.
- Must preserve review severity rules.

### `promote_to_canonical`

Purpose:

- Prepare a human-reviewable promotion proposal from candidate learning, decision, capability, run, failure, or pattern into a canonical artifact.

Inputs:

```yaml
promotionRequest:
  candidateId: ""
  candidateSource: ""
  targetCanonicalArtifact: ""
  promotionReason: ""
  evidence: []
  riskAssessment: []
  requiredApprovals: []
  proposedChangeSummary: ""
```

Outputs:

- Promotion proposal.
- Required approval list.
- Suggested Linear ticket title and acceptance criteria.
- NO-GO reasons if blocked.

Schema references:

- `schemas/LearningRecord.schema.json`
- `knowledge/learning-record-policy.md`
- `execution/approval-gates.md`
- `architecture/canonical-schema-policy.md`

Restrictions:

- Always requires human approval.
- Must not edit canonical artifacts directly.
- Must not bypass ticket, branch, PR, review, and merge flow.
- Must block if evidence is missing, sensitive data is unresolved, or target artifact ownership is unclear.

## Auth And Permission Model

A future implementation must distinguish:

- read-only source discovery
- candidate write
- operational handoff write
- promotion proposal
- canonical mutation

Default posture:

- read-only is allowed for public repository artifacts and assigned ticket context
- candidate writes require assigned ticket scope
- operational writes require explicit approval when they mutate Linear or GitHub
- promotion proposals require explicit ticket scope
- canonical mutation is not an MCP tool action; it happens through repository PR flow

## Logging Requirements

Every tool call should log:

- request ID
- actor and agent type
- Linear ticket ID
- tool name
- source allowlist and denylist
- result count
- canonicality distribution
- denied or omitted sources
- approval status
- risks returned
- created draft/candidate references
- timestamp

Logs must not include secrets, raw customer data, production data, private evidence, or sensitive source text.

## Approval And Write Restrictions

The MCP must block or return `denied` when a request would:

- create or mutate a Linear project or ticket without approval
- open or merge a PR without approval
- deploy or enable production execution
- read, store, rotate, use, or transmit secrets
- access, export, modify, delete, or share customer or production data
- send external communications
- change legal, financial, compliance, privacy, security, or sensitive claims
- create unsupported customer, metric, revenue, integration, or validation evidence
- promote candidate memory into a canonical rule without human approval

These restrictions mirror `AGENTS.md` and `execution/approval-gates.md`.

## Direct Database Access Rule

Agents must not connect directly to a knowledge database, pgvector store, or embedding index.

Allowed:

- MCP-mediated read results with source links
- MCP-mediated candidate write proposals
- repository PRs that update canonical artifacts
- local-only spikes explicitly approved by a ticket

Forbidden:

- raw SQL queries by agents against a shared knowledge DB
- using database rows as canonical decisions
- writing embeddings that have no source artifact
- promoting retrieved content without human review
- indexing sensitive data without approval and redaction policy

## Validation Expectations

For this specification ticket, validate:

- candidate tools include `search`, `write_learning`, `write_decision`, `write_capability`, `write_run`, `get_context_pack`, and `promote_to_canonical`
- canonical promotion is protected behind human review
- tool inputs/outputs reference existing schemas or canonical specs
- direct DB access by agents is explicitly disallowed
- auth, logging, approval, and write restrictions align with `AGENTS.md` and `execution/approval-gates.md`
- no MCP implementation, database access, or executable integration is introduced

## Future Ticket Hooks

Future tickets may:

- create a machine-readable Knowledge MCP tool schema
- implement a local mock MCP server with synthetic fixtures
- add automated schema validation for tool payloads
- connect `get_context_pack` to a retrieval backend
- define repository-safe logging and audit storage
- add a security/privacy review for candidate writes

Those tickets must not weaken the canonical-memory, approval, and direct-DB-access boundaries defined here.
