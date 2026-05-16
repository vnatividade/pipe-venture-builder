# Template Initialization Workflow

Use this workflow when starting a new product from `pipe-venture-builder`.

Prefer creating a new repository from the GitHub Template Repository flow. Use a fork only when the goal is to contribute back to the base template.

This workflow is a specification and checklist. It does not create repositories, configure secrets, create Linear projects, or run external automation without explicit human approval.

## Purpose

Initialize a product workspace without contaminating the base repository with product-specific context, customer data, credentials, or private operational details.

## Required Approvals

Human approval is required before:

- creating a new repository
- creating a Linear project
- creating Linear tickets
- opening or merging setup PRs
- configuring secrets, credentials, deploy keys, integrations, or production environments
- importing customer data or private founder context
- enabling billing, paid acquisition, outreach, or production jobs

If approval is missing, prepare the checklist only and record the blocker.

## Recommended Path

1. Confirm the new product name, repository owner, visibility, and intended scope.
2. Create a new repository from the GitHub Template Repository flow after approval.
3. Clone the new product repository locally.
4. Confirm the default branch and repository remotes.
5. Replace placeholder product context only inside the new product repository.
6. Create or confirm the Linear project after approval.
7. Initialize Codex and agent guidance for the product repository.
8. Initialize knowledge surfaces with product-specific pointers, not private raw data.
9. Create first setup or validation tickets only after approval.
10. Run a first readiness check before implementation work begins.

## Product Initialization Checklist

Complete in the new product repository, not in the base template.

- Product name:
- Repository:
- Owner:
- Visibility:
- Base template source:
- Initial target market:
- Primary problem:
- Promised result:
- Current stage:
- Product-specific context stored in `product/product-context.md`: yes/no
- Sensitive founder context excluded or stored privately: yes/no
- Customer data excluded unless approved: yes/no

Do not store secrets, credentials, customer data, private founder notes, or machine-specific configuration in the repository.

## Codex Initialization

- Read `README.md`, `AGENTS.md`, and `setup/operating-manual.md`.
- Confirm branch naming and PR rules.
- Confirm approval gates in `execution/approval-gates.md`.
- Confirm one branch and one PR per Linear ticket.
- Confirm review is required before merge.
- Confirm whether Codex review is enabled; if not, use documented manual review fallback.
- Record any repository-specific agent notes in the new repository only.

Do not change base template agent rules unless a dedicated base-template ticket requires it.

## Linear Initialization

Create or confirm the Linear project only after approval.

The Linear project should record:

- product scope
- repository link
- owner
- included scope
- excluded scope
- initial milestones
- approval requirements
- validation gates required before implementation

Initial tickets should be small and should reference source artifacts. Do not create implementation tickets before founder focus, C.O.N.T.R.O.L.E., validation, PRD, MVP scope, risk, and architecture gates exist when relevant.

## Knowledge Initialization

Initialize knowledge with pointers and empty templates, not invented history.

- Link the product context artifact.
- Record known assumptions as assumptions.
- Record missing evidence explicitly.
- Start KDR/DAR only when a strategic decision is actually made.
- Keep customer language separate from synthesis.
- Use anonymized labels for any approved customer discovery notes.
- Record where private data is stored only if approved.

Do not import chat memory, synthetic persona output, or founder opinion as real evidence.

## Automation Boundary

Allowed without additional automation approval:

- drafting initialization checklists
- proposing repository setup steps
- proposing Linear project and ticket structure
- preparing PR text or handoff notes

Not allowed without explicit approval:

- creating repositories
- creating Linear projects or tickets
- configuring secrets or deploy keys
- installing production integrations
- deploying or scheduling jobs
- importing private data
- contacting customers or third parties

## Readiness Check

Before the first implementation ticket:

- repository was created from the template or approved fork path
- product context is present and sanitized
- Linear project is confirmed
- approval status is recorded
- validation gates are identified
- no secrets or private customer data were committed
- first tickets are scoped and traceable
- review and merge rules are understood

## Handoff

- Product repository:
- Linear project:
- Initialization PR:
- Approvals recorded:
- Product context status:
- Knowledge initialization status:
- Open blockers:
- Follow-up tickets:
