# NotebookLM Discovery Design Note

This design note describes how a future NotebookLM-style discovery workflow could organize source collections and synthesize discovery material while preserving citations, boundaries, and approval gates.

Use it with `research/research-orchestrator-workflow.md`, `research/scientific-validation-workflow.md`, `knowledge/knowledge-curator-workflow.md`, and `execution/approval-gates.md`.

## Boundary

This is a planning artifact only. It does not implement a NotebookLM MCP connector, configure credentials, ingest private files, call external tools, create automated decisions, or authorize source upload.

Before any implementation or connector setup, require explicit approval, security/privacy review, and confirmation that the target connector exists and is appropriate for the repository.

## Intended Use

NotebookLM-style source organization may help when:

- a discovery question depends on multiple source documents
- sources need to stay grouped by product idea, ICP, market, claim, or research question
- synthesis quality depends on preserving source citations and limitations
- future agents need a navigable source collection rather than scattered links

It must not be used to:

- replace customer discovery
- treat summaries as source evidence
- upload confidential, private, customer, regulated, or credentialed material without approval
- make public claims or product decisions without human review
- automate GO / NO-GO decisions

## Source Types

| Source type | Allowed by default | Notes |
|---|---|---|
| Repository artifacts | Yes | Product, validation, research, and knowledge docs already committed to the repo. |
| Public web sources | Yes, as links or summaries | Preserve URL, access date, source type, and limitations. |
| Public PDFs or papers | Yes, when license/access permits | Use citation metadata; do not copy long passages. |
| Customer discovery notes | No by default | Only anonymized, approved, repository-safe summaries may be used. |
| Private founder notes | No | Keep private context outside this workflow unless explicitly approved. |
| Credentials, secrets, production data, customer data | No | Stop and escalate; do not ingest. |
| Paid or credentialed sources | No by default | Requires approval and source-use constraints. |

## Collection Model

Each source collection should be scoped to one decision question.

Required collection fields:

- collection ID
- origin Linear ticket
- decision question
- product phase
- ICP or market
- source owner
- source inclusion rule
- excluded source types
- approval state
- retention or deletion note when relevant

Recommended collection shape:

```md
# Source Collection - <decision question>

- Collection ID:
- Origin ticket:
- Owner:
- Date opened:
- Decision question:
- Product phase:
- ICP / market:
- Approval state:
- Excluded sources:
- Retention note:
```

## Source Entry Requirements

Each source entry needs:

- source title
- URL or repository path
- author or organization, when available
- publication date or access date
- source type
- source lane: customer / market / scientific / web-source / internal artifact
- freshness: Current / Dated / Stale / Unknown
- directness: Direct customer behavior / Direct source evidence / Indirect market signal / Expert or scientific source / Internal assumption
- relevant question
- permitted use
- limitations

Do not include raw private or identifiable customer material in source entries.

## Synthesis Outputs

NotebookLM-style synthesis should produce bounded outputs, not decisions.

Allowed outputs:

- source map
- cited summary
- contradiction list
- open assumptions
- evidence gaps
- confidence by source lane
- questions for customer discovery
- handoff to research, validation, risk, or knowledge owner

Restricted outputs:

- GO / NO-GO verdicts
- customer proof claims
- market validation claims
- regulated or professional advice
- external copy
- implementation-ticket approval
- automated ranking without review

## Citation Expectations

Every synthesized statement should be traceable to one or more source entries.

Citation fields:

- source entry ID
- source title
- URL or repository path
- date
- source lane
- confidence
- limitation

If a synthesis cannot cite a source entry, mark it as an assumption or exclude it.

## Approval Gates

Explicit approval is required before:

- setting up a NotebookLM MCP connector
- using credentials, paid tools, or private workspaces
- uploading or syncing source files to external systems
- ingesting customer, production, confidential, regulated, or sensitive data
- publishing NotebookLM-generated synthesis externally
- using synthesis to change PRD, MVP scope, claims, pricing, growth, or implementation tickets
- automating source ingestion or decision routing

If approval is missing, keep the work as a local design note and record the blocker in Linear.

## Limitations

- Summaries are not source evidence.
- Citations can be incomplete or misleading if source entries are weak.
- Source organization improves retrieval, not truth.
- NotebookLM-style synthesis may compress nuance or miss contradictions.
- Private and sensitive data handling needs separate review before any connector setup.
- Customer discovery remains the validation path for customer proof.

## Future Implementation Checklist

Only use this checklist after approval.

- Confirm connector/tool availability.
- Complete privacy and security review.
- Define allowed source locations.
- Define forbidden source types.
- Define retention/deletion rules.
- Define citation export format.
- Define manual review before synthesis affects decisions.
- Create implementation ticket with explicit scope and rollback/disable plan.

## Handoff

| Output | Next owner |
|---|---|
| Source collection design | research_orchestrator |
| Market source synthesis | market_intelligence_agent |
| Scientific source synthesis | scientific_validation_agent |
| Customer discovery gaps | customer_discovery_agent or validation_agent |
| Sensitive source risk | risk_reviewer |
| Durable source map or learning | knowledge_curator |

## Done Criteria

This design note is complete when:

- allowed and forbidden source types are explicit
- source collection fields are defined
- synthesis outputs and restricted outputs are separated
- citation expectations preserve source traceability
- limitations prevent summaries from becoming proof
- approval gates block connector setup, credentials, private data, external publishing, and automated decisions
