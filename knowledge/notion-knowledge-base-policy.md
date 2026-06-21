# Notion Knowledge Base Policy

This policy defines the Pipe stance for Notion as a knowledge-base-adjacent capability.

Decision: Notion is a governed collaboration, search, and publishing surface. It is not Pipe's canonical knowledge base.

Canonical knowledge remains in repository Markdown, schemas, Linear, GitHub, and future approved Knowledge Runtime records as defined by `architecture/knowledge-runtime-architecture.md`.

Use this policy with `capabilities/entries/capability.external.notion-mcp.json`, `architecture/capability-registry-policy.md`, `knowledge/knowledge-curator-workflow.md`, `validation/customer-data-retention-policy.md`, and `validation/raw-interview-evidence-intake-and-synthesis.md`.

## Current Stance

Pipe may use Notion when an approved ticket or explicit user request calls for:

- searching existing workspace documentation
- publishing or mirroring an approved repository artifact
- creating a stakeholder-readable version of reviewed documentation
- registering a Notion link in Linear, a PR handoff, or a repository index
- preparing meeting or collaboration materials from already-approved source content

Pipe must not use Notion as:

- the source of truth for repository policy, approval gates, validation gates, PRD, MVP scope, ADRs, KDRs, DARs, schemas, or execution rules
- the only place where a decision, evidence claim, approval, blocker, or merge state exists
- a raw customer interview store
- an automatic memory sink for agent conversations
- a replacement for Linear ticket state, GitHub review state, or repository documentation

## Source Of Truth Boundary

| Surface | Role | Canonical? | Notes |
|---|---|---:|---|
| Repository Markdown | Durable product, validation, architecture, execution, and knowledge memory | Yes | Future agents should rely on reviewed repository artifacts. |
| Repository schemas | Machine-readable contracts | Yes | Schemas define structure, not persistence. |
| Linear | Ticket state, priority, blockers, ownership, and execution handoff | Yes for execution | Notion links may be recorded in Linear, but do not replace Linear status. |
| GitHub | Branch, PR, review, checks, merge, and delivery discussion | Yes for delivery | Notion cannot satisfy branch protection or review requirements. |
| Notion | Collaboration, search, stakeholder reading, and approved mirrors | No | Notion pages must point back to canonical source artifacts when used. |
| Future Knowledge Runtime | Recall, context packs, and governed retrieval | No unless explicitly promoted | Retrieval results must point back to canonical sources. |
| Agent conversation memory | Current-session working context | No | Promote durable decisions into the approved source of truth. |

## What May Live In Notion

Notion may contain:

- approved mirrors of merged repository docs
- stakeholder-friendly summaries of reviewed artifacts
- meeting notes or pre-reads that link back to source artifacts
- project overview pages that link to Linear projects and repository docs
- non-sensitive research or planning notes when the ticket approves workspace documentation
- status summaries that clearly name their source date and canonical source

Every Notion mirror or summary should state:

- source artifact path or URL
- source date or merge reference when available
- whether the page is a mirror, draft, collaboration note, or approved summary
- who requested or approved the Notion action
- what content is intentionally omitted

## What Must Stay Out Of Notion By Default

Do not put these in Notion without a dedicated approval and retention decision:

- raw interview notes
- recordings or transcripts
- identifiable customer quotes
- customer names, emails, phone numbers, company identifiers, or private workflow details
- screenshots, files, exports, or customer-provided materials
- secrets, credentials, tokens, private keys, production data, billing data, or payment data
- legal, financial, compliance, privacy, security, pricing, or customer-facing claims that are not already approved
- draft repository policies that could be mistaken for accepted rules

If raw discovery material must be processed, use `validation/raw-interview-evidence-intake-and-synthesis.md` and `validation/customer-data-retention-policy.md` before any Notion action.

## Agent Routing

Agents may use `capability.external.notion-mcp` only when:

- the assigned ticket or current user request explicitly asks for Notion search, publishing, update, or registration
- the content is approved for the requested workspace action
- the capability lifecycle, approval triggers, and data boundaries allow the use
- the action will not make Notion the canonical source of truth
- the handoff can record source artifact, Notion URL, action, approval status, and residual risk

Use read-only Notion search when the user asks whether relevant workspace documentation exists. Treat search results as discoverable references, not canonical truth, until confirmed against repository, Linear, or GitHub sources.

Do not use Notion when:

- the repository or Linear already answers the task and no workspace action was requested
- the content is draft-only, unreviewed, sensitive, private, or customer-identifiable
- the action would publish unsupported evidence, market validation, legal/compliance/privacy/security claims, or customer-facing claims
- the ticket lacks approval for external workspace mutation
- the result would bypass PR review, Linear governance, or repository source-of-truth rules

## Required Handoff When Notion Is Used

Record this in the PR, Linear handoff, or relevant artifact:

```md
## Notion usage
- Action: searched / created / updated / mirrored / registered / not used
- Capability: `capability.external.notion-mcp`
- Source artifact:
- Notion page or search result:
- Approval source:
- Data boundary:
- Canonical source remains:
- Omitted or blocked content:
- Residual risk:
```

If Notion was considered but not used, state the reason when the choice affects future agents.

## Relationship To Future Knowledge Runtime

Future retrieval may index or reference approved Notion pages only as non-canonical workspace references.

Future Context Packs should prefer canonical repository, Linear, and GitHub sources. A Notion result may be included when it:

- links back to a canonical source
- contains meeting or collaboration context explicitly approved for the ticket
- clarifies where an approved stakeholder-facing document lives
- does not include private customer data, secrets, production data, or unsupported claims

No future Knowledge Runtime, MCP, or retrieval index may promote Notion content into a canonical rule without a ticket, PR, review, and human approval.

## Verification Notes

PIP-373 verified that the repository already registers Notion as `capability.external.notion-mcp` for approved documentation search, publishing, update, and registration.

That registration is a capability boundary, not a decision to make Notion the canonical knowledge base.
