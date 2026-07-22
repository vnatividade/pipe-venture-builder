# pipe-venture-builder

Reusable venture builder operating-system template for taking either a raw product idea or an already-started product into governed, evidence-aware delivery.

This repository is the base operating system for future product ideas and existing products that need governance recovery. It is designed for solo founders and very small teams using Codex, Linear, GitHub, and focused agentic workflows.

## What This Template Is

`pipe-venture-builder` is not a general idea notebook or a prompt dump. It is a controlled execution system with two entry paths: shape a new idea, or adopt an existing product without inventing the documentation and evidence it never had. Both paths converge on one governed product baseline and then use the same validation, planning, delivery, review, and learning lifecycle.

The repository should help future agents understand the current product state without relying on conversational memory.

## Operating Flow

```txt
New idea ---------> /pipe:idea ----┐
                                   ├-> ProductBaseline -> stage assessment
Existing product -> /pipe:adopt ---┘                         |
                                                             v
          discover -> validate -> prd -> plan -> build -> check
             -> review -> ship -> learn -> next iteration or stop
```

Stage assessment selects the smallest safe command; it never uses an existing implementation to waive missing validation, risk, or approval gates.

Do not skip the validation gates just because implementation is possible. The point of the system is to keep execution narrow, traceable, and evidence-led.

For stage-level GO / REFINE / NO-GO boundaries across Idea, MVP, Launch, and Scale, use [execution/core-pipeline-map.md](execution/core-pipeline-map.md). A completed document is not evidence by itself; advancement requires sourced evidence, explicit assumptions, and the required approval state.

## First-Run Path

Choose the entry that matches the product:

- New idea or brainstorm: start with `/pipe:idea`, then follow the greenfield path below.
- Existing code/product: start with the specification in [execution/dual-entry-product-intake-workflow.md](execution/dual-entry-product-intake-workflow.md) and use `/pipe:adopt` to produce a current-state baseline and reconciliation plan before changing external systems.

For a new product idea:

1. Create a new repository from this template.
2. Write the raw idea, target user, problem, promised result, and early assumptions in `product/`.
3. Complete founder focus before expanding the idea.
4. Run the idea through the C.O.N.T.R.O.L.E. gate when that template exists.
5. Define a research and validation plan before writing implementation tickets.
6. Draft Working Backwards, PRD, MVP scope, anti-goals, and risk notes.
7. Confirm or create the Linear project for the product.
8. Create small Linear tickets only for approved scope.
9. Execute one ticket per branch and one PR per ticket.
10. Update `knowledge/` with decisions and learning after each cycle.

See [setup/operating-manual.md](setup/operating-manual.md) for the operating manual and [setup/portable-bootstrap-and-runtime-boundaries.md](setup/portable-bootstrap-and-runtime-boundaries.md) for the cross-machine target architecture.

## When Not To Proceed

Do not move into implementation when:

- the target market is broad or undefined
- the problem is still a wishlist
- the C.O.N.T.R.O.L.E. gate is missing or unresolved
- the validation plan is absent
- the MVP scope is not explicit
- the work has no approved Linear ticket
- the proposed action needs human approval and approval has not been granted
- the change would create legal, financial, security, privacy, billing, or external communication risk

When blocked, document the gap and create or execute the relevant setup or validation ticket instead.

## Repository Areas

| Path | Purpose |
|---|---|
| `product/` | Idea intake, strategic framing, C.O.N.T.R.O.L.E., Working Backwards, PRD, MVP scope, anti-goals. |
| `validation/` | Customer discovery, experiments, learning cards, GO / NO-GO decisions. |
| `research/` | Market research, scientific validation, source logs, research synthesis. |
| `architecture/` | Engineering standards, system design, ADRs, technical constraints. |
| `execution/` | Linear governance, execution workflow, ticket templates, handoff, done criteria. |
| `growth/` | Growth experiment system and content/channel strategy after validation. |
| `monetization/` | Willingness-to-pay, pricing, and billing approval gates. |
| `knowledge/` | Decision log, learning log, memory map, and future knowledge-base integration. |
| `.agents/skills/` | Reusable agent skills loaded for specific workflows. |
| `.codex/agents/` | Codex agent definitions. |
| `.codex/templates/` | Reusable task, PR, and operating templates. |
| `.codex/workflows/` | Codex execution workflows. |
| `.github/` | GitHub project metadata and PR templates. |
| `setup/` | Bootstrap and setup guidance. |
| `schemas/` | Canonical machine-readable contracts shared by commands, agents, and future runtimes. |
| `examples/` | Example pipeline runs for future product ideas. |

## Operating Principles

- Validate before building.
- Keep one target market, one main problem, one offer, and one primary channel before expanding.
- Use C.O.N.T.R.O.L.E. as a required strategic gate before serious execution.
- Confirm the Linear project before creating implementation tickets.
- Execute one Linear ticket scope at a time.
- Keep one branch and one PR per ticket.
- Require review before merge.
- Preserve enough context for future agents without relying on conversational memory.

## Human Approval Gates

Human approval is required before:

- creating Linear projects or tickets
- opening or merging PRs
- production deployment
- enabling billing
- activating paid ads
- handling secrets
- contacting customers automatically
- sending external communications
- changing legal, financial, or compliance-related content

## Current Status

The declarative governance layer, command catalog, agent contracts, operating modes, capability registry, and core schemas are in place. The dual-entry architecture and `ProductBaseline` contract are specified. Executable `/pipe:*` commands, portable bootstrap/doctor, reconciliation adapters, and a persistent runtime remain follow-up implementation work.
