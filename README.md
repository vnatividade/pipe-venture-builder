# pipe-venture-builder

Reusable venture builder operating-system template for taking a product idea from raw intake to validated MVP execution.

This repository is the base starting point for future product ideas. It is designed for solo founders and very small teams using Codex, Linear, GitHub, and focused agentic workflows.

## What This Template Is

`pipe-venture-builder` is not a general idea notebook or a prompt dump. It is a controlled execution pipeline for moving one product idea through founder focus, strategic validation, MVP definition, ticketed execution, review, and learning updates.

The repository should help future agents understand the current product state without relying on conversational memory.

## Operating Flow

```txt
Idea
-> idea intake
-> founder focus
-> C.O.N.T.R.O.L.E. evaluation
-> research and validation plan
-> Working Backwards
-> PRD
-> MVP scope review
-> risk review
-> architecture
-> Linear project
-> Linear tickets
-> GitHub branch and PR
-> review and merge
-> learning updates
```

Do not skip the validation gates just because implementation is possible. The point of the system is to keep execution narrow, traceable, and evidence-led.

## First-Run Path

Start here when using this template for a new product idea:

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

See [setup/operating-manual.md](setup/operating-manual.md) for the operating manual.

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

The repository skeleton and Linear project confirmation are in place. Foundation tickets continue to add the concrete README, operating manual, agent instructions, C.O.N.T.R.O.L.E. gate, founder focus templates, Working Backwards, PRD, and MVP scope templates.
