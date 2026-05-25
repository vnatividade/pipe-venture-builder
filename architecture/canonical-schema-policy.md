# Canonical Schema Policy

This policy defines where Pipe Venture Builder schemas live, how they are named, when they are required, and how they should be reviewed.

Use it with `execution/linear-ticket-template-v2.md`, `execution/ticket-type-field-matrix.md`, `execution/agent-readiness-validator.md`, `architecture/technical-decision-guide.md`, and future schema tickets.

This policy does not create runtime validation, CI checks, code generation, database migrations, or schema enforcement tooling.

## Core Decision

Canonical machine-readable schemas live under the top-level `schemas/` directory.

Human-readable templates, examples, and operating docs may live in their domain folders, but the canonical contract for structured outputs belongs in `schemas/`.

Initial convention:

```txt
schemas/
  README.md
  <SchemaName>.schema.json
```

Examples for upcoming work:

```txt
schemas/DeliveryEvidence.schema.json
schemas/LearningRecord.schema.json
schemas/IdeaBrief.schema.json
schemas/ValidationPlan.schema.json
schemas/PRD.schema.json
schemas/ExecutionPlan.schema.json
```

## What Counts As A Canonical Schema

A canonical schema is a durable contract for structured data that future agents, templates, commands, capabilities, or runtime systems may read or write.

Use JSON Schema for canonical schemas unless an approved ticket chooses another format for a specific reason.

Markdown templates are not canonical schemas. They may mirror a schema for human usability, but the `.schema.json` file is the authoritative machine-readable contract.

## When A Schema Is Required

Create or update a canonical schema when a ticket introduces:

- reusable structured output consumed by more than one agent, command, skill, or workflow
- delivery evidence intended to be checked or compared across PRs
- learning, decision, capability, run, or context-pack records
- planning artifacts that future capabilities may consume, such as IdeaBrief, ValidationPlan, PRD, or ExecutionPlan
- data contracts that affect future orchestration, retrieval, evaluation, or automation
- fields that must stay stable across Linear, GitHub, Markdown templates, and future runtime integrations

Do not create a schema for:

- one-off documentation
- prose-only strategy notes
- exploratory research summaries
- temporary local scripts
- artifacts with no stable consumer
- fields that are still being discovered and would be overfit by early formalization

If unsure, keep the artifact Markdown-only and add a follow-up candidate rather than creating a premature schema.

## Naming Rules

Schema files use PascalCase object names and the `.schema.json` suffix:

```txt
schemas/<SchemaName>.schema.json
```

Rules:

- Use singular nouns: `LearningRecord`, not `LearningRecords`.
- Use stable domain names: `DeliveryEvidence`, not `PRProof`.
- Avoid implementation-specific names: do not encode tool names such as Codex, Claude, Linear, or GitHub unless the schema is truly tool-specific.
- Avoid version numbers in filenames for the first version.
- Use `$id` inside the schema to identify the contract.
- Use `title` to match the schema name.
- Use `description` to state purpose, consumers, and non-use cases.

Recommended `$id` format:

```json
"$id": "https://pipe-venture-builder.local/schemas/<SchemaName>.schema.json"
```

This is an internal stable identifier, not a public hosting claim.

## Versioning Rules

Every canonical schema should include:

```json
"x-pipe-schema-version": "0.1.0"
```

Use semantic versioning:

- Patch: wording, descriptions, examples, or non-behavioral metadata changes.
- Minor: additive optional fields or compatible clarifications.
- Major: required field changes, removed fields, renamed fields, changed enum meaning, or incompatible structure changes.

Do not create `v1`, `v2`, or date-stamped copies unless a separate compatibility ticket proves that multiple active versions are needed.

When a breaking change is required:

- explain the reason in the PR
- list affected templates, commands, skills, and tickets
- provide migration notes or state why no migration is needed
- update related Markdown templates in the same PR only when they are owned by the same ticket scope

## Required Schema Shape

Use JSON Schema draft 2020-12 by default:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://pipe-venture-builder.local/schemas/Example.schema.json",
  "title": "Example",
  "description": "Purpose, consumers, and non-use cases.",
  "type": "object",
  "additionalProperties": false,
  "required": [],
  "properties": {},
  "x-pipe-schema-version": "0.1.0"
}
```

Default expectations:

- `additionalProperties` should be `false` unless the schema intentionally allows extension.
- Required fields should be minimal and justified.
- Enums should be small, stable, and documented.
- Descriptions should distinguish evidence from assumptions.
- Sensitive fields must state privacy, approval, or redaction expectations.
- Schema examples should avoid invented customers, revenue, metrics, integrations, or validation.

## Ownership

Default owner by schema type:

| Schema family | Primary owner | Supporting reviewer |
|---|---|---|
| Delivery evidence and validation artifacts | Execution / validation owner | Risk reviewer when evidence, customer data, or production claims appear |
| Learning, decision, memory, and context-pack records | Knowledge owner | Architecture owner |
| Capability registry records | Capability / architecture owner | Risk reviewer for external tools, costs, and data boundaries |
| Product planning artifacts | Product / validation owner | Human operator for strategic claims |
| Runtime or orchestration-prep records | Architecture owner | Human operator before automation or dispatch implications |

If ownership is unclear, do not create the schema. Record the ambiguity in the ticket or PR and create a follow-up when needed.

## Review Path

Schema PRs must include:

- linked Linear ticket
- expected consumers
- included and excluded fields
- compatibility assessment
- validation approach, even if manual
- relationship to any Markdown template
- privacy, security, customer-data, or sensitive-claim implications
- follow-ups for runtime validation tooling, if relevant

Review should check:

- naming follows this policy
- required fields are justified
- schema does not encode unsupported business evidence
- schema does not pull future runtime implementation into the current ticket
- related templates or docs are updated only when in scope
- breaking changes are clearly marked

P0/P1 review findings block merge under `execution/approval-gates.md`.

## Compatibility Expectations

Schemas should be stable enough for future agents to consume without reading chat history.

Before changing an existing schema, check:

- templates that mirror the schema
- commands or skills that reference it
- Linear ticket examples using it
- knowledge records or examples already created
- future runtime/orchestration references

If compatibility impact is unknown, mark the change as `READY WITH APPROVAL` or `BLOCKED` in the readiness validator until the owner resolves it.

## Directory Placeholder

The initial `schemas/README.md` exists so future schema tickets have a canonical home.

It must not be interpreted as:

- runtime validation tooling
- CI enforcement
- a complete schema registry
- permission to create schemas outside approved Linear tickets

## Manual Validation Against Linear Schema Tickets

Against the approved Linear schema backlog:

- PIP-149 / PVB-SCHEMA-005 can create `schemas/DeliveryEvidence.schema.json` using this naming and versioning rule.
- PIP-150 / PVB-SCHEMA-006 can create `schemas/LearningRecord.schema.json` using this ownership and compatibility path.
- PIP-151 / PVB-SCHEMA-007 can define planning schemas under `schemas/` while leaving Markdown-only artifacts where structure is not mature.
- Capability Registry work can reference this policy before adding structured capability records.

## Done Criteria

This policy is working when:

- new schema tickets use `schemas/<SchemaName>.schema.json`
- schema PRs identify owner, consumer, compatibility, and review path
- Markdown templates do not drift from canonical schemas
- agents do not create schemas without an approved ticket
- runtime validation remains out of scope until a dedicated ticket authorizes it
