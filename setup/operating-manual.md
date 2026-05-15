# Operating Manual

This manual defines the first practical operating path for `pipe-venture-builder`. Keep it short, ticket-driven, and current as the repository gains concrete templates.

For starting a new product repository from this base template, use [template-initialization-workflow.md](template-initialization-workflow.md).

## Default Execution Loop

1. Start from a single product idea.
2. Capture the idea in `product/`.
3. Complete founder focus and strategic framing.
4. Run C.O.N.T.R.O.L.E. before serious execution.
5. Define research and validation work before implementation.
6. Write Working Backwards, PRD, MVP scope, anti-goals, and risk notes.
7. Confirm the Linear project.
8. Create or select the next approved Linear ticket.
9. Implement one ticket per branch.
10. Open one PR per ticket.
11. Review the PR before merge.
12. Update Linear and `knowledge/` with the result.

## First-Run Checklist

- `product/` contains the raw idea and initial assumptions.
- The target market is specific enough to test.
- The primary problem and desired result are explicit.
- The validation plan exists before build tickets.
- The MVP scope names what is included and excluded.
- Linear has one project for the product execution.
- Every implementation task has an approved Linear ticket.
- Every PR links back to its Linear ticket.

## Ticket Execution Rules

- Work on one Linear ticket at a time.
- Use a branch name that references the ticket, such as `codex/PIP-123-short-name`.
- Keep the PR scoped to that ticket.
- Run the available validations before review.
- Fix blocking review findings before merge.
- Create follow-up tickets for relevant work outside the current scope.
- Do not close implementation tickets without a merged PR unless the ticket is explicitly documentary or investigative.

## Approval Gates

Human approval is required before:

- creating Linear projects
- creating Linear tickets
- opening PRs
- merging PRs
- deploying to production
- enabling billing or paid ads
- handling secrets or credentials
- contacting customers automatically
- sending external communications
- changing legal, financial, compliance, privacy, or security-sensitive content

If approval is missing, stop the risky action and document the blocker in Linear.

## GO Conditions

Proceed when:

- the current task has an approved Linear ticket
- the work is inside the ticket scope
- the required prior gate exists or the ticket is specifically about creating it
- the change can be reviewed independently
- validation can be run or the validation gap can be clearly documented

## NO-GO Conditions

Do not proceed when:

- the idea lacks a defined user, problem, or outcome
- the work expands the MVP without approval
- implementation would bypass research or validation gates
- the ticket scope is ambiguous and cannot be resolved from repository context
- the action requires human approval and approval has not been granted
- the change would introduce hidden claims, fake evidence, invented metrics, or unsupported customer insight

## Handoff Notes

Each completed ticket should leave enough context for the next agent:

- Linear ticket link
- branch and PR link
- summary of delivered scope
- validations run
- review status
- merge status
- follow-up tickets created
- known residual risks

The repository should remain understandable without access to the conversation that produced the change.
