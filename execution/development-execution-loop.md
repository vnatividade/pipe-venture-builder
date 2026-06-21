# Development Execution Loop

Use this loop after a Linear ticket is ready and any required Tactical Execution Plan is approved, linked, or explicitly marked not applicable.

This loop defines how agents move from planned development into implementation, validation, repair, documentation, review, and handoff. It does not replace `execution/tactical-execution-plan.md`, `execution/test-oriented-delivery-rule.md`, `execution/pipe-check-command-spec.md`, ADRs, PR review, branch protection, or final Linear handoff.

## Purpose

The development loop exists so agents apply the same discipline used in discovery to execution:

- plan before changing files
- break broad work into traceable stories or slices
- decide when ADRs, RFCs, tests, docs, observability, and follow-ups are required
- validate each slice before expanding scope
- repair relevant failures before asking for review
- leave evidence that another agent can resume without chat memory

## Applicability

### Required

Use this loop for tickets that include:

- code, infrastructure, automation, observability, or runtime behavior
- customer-facing product behavior, UI, onboarding, billing, permissions, or data handling
- multi-story implementation or ticket decomposition
- ADR, RFC, architecture, security, privacy, data, integration, or deployment decisions
- changes to execution workflows that future agents must follow

### Lightweight

A lightweight loop note is enough for documentation or governance tickets that define development behavior but do not implement runtime behavior.

Record:

- loop status
- planned slice
- ADR/RFC decision
- validation commands or manual checks
- docs and handoff updates
- follow-up criteria

### Not Applicable

Mark the loop as not applicable only for work such as typo fixes, link maintenance, small copy changes, or bookkeeping that does not change behavior, workflow, governance, or future execution.

## Required Inputs

Before implementation starts, the agent must have:

- one Linear ticket
- dependency and approval state
- expected write set and restricted files
- Tactical Execution Plan status
- ADR/RFC decision path or no-ADR rationale
- validation and DeliveryEvidence expectations
- context and token-efficiency strategy
- stop conditions and follow-up criteria

If any input is missing and it affects execution safety, record `NOT READY` or `BLOCKED` in Linear instead of starting branch work.

## Loop States

| State | Goal | Required action | Exit condition |
|---|---|---|---|
| Plan | Convert ticket scope into one safe slice. | Read required artifacts, confirm write set, acceptance criteria, ADR path, validation plan, and stop conditions. | Slice can be implemented without expanding scope. |
| Implement | Change only the approved slice. | Edit the smallest coherent set of files needed for the slice. | Diff matches the slice and excluded scope remains untouched. |
| Validate | Prove the slice works or is correctly documented. | Run the strongest relevant tests, checks, schema validation, path checks, or manual evidence review. | Results are recorded and relevant failures are known. |
| Repair | Fix failures before moving on. | Address relevant validation failures, review scope drift, and re-run affected checks. | No relevant blocking failure remains. |
| Document | Update durable knowledge. | Update docs, ADR/KDR/DAR/LearningRecord candidates, DeliveryEvidence, or handoff notes required by the slice. | Future agents can understand the change from repository and Linear artifacts. |
| Review | Prepare the PR for review. | Ensure PR body, validation evidence, risks, follow-ups, and context/token choices are current. | Review can classify findings without relying on chat history. |
| Handoff | Close the execution trail. | Record merge state, validation, residual risk, follow-ups, and next action in Linear. | Ticket can move to Done or an explicit blocker remains. |

Do not move from Implement to a larger slice until Validate and Repair are complete for the current slice.

## Story And Slice Breakdown

Use stories or slices when a ticket has more than one behavior, artifact, dependency, or acceptance path.

Each story or slice should state:

- outcome
- owner or agent
- expected write set
- dependency
- acceptance check
- validation evidence
- documentation update
- follow-up trigger

A story can live in the Tactical Execution Plan, Linear ticket, PR body, or a linked child ticket. Create child tickets only when the work cannot remain one reviewable PR without hiding dependencies or scope.

## ADR And RFC Triggers

Use `architecture/technical-decision-guide.md` before implementation.

Create or update an ADR when the work:

- changes architecture boundaries
- selects a durable data model, integration, hosting, or security posture
- accepts a meaningful technical tradeoff
- constrains future implementation tickets
- supersedes a prior architecture decision

Create an RFC before implementation when multiple plausible approaches exist, risk is unclear, or human review is needed before choosing.

Record a no-ADR rationale when the choice is routine, local to one ticket, or already covered by an existing architecture artifact.

## Validation And Self-Review

Use `execution/test-oriented-delivery-rule.md` and `execution/pipe-check-command-spec.md`.

The agent must:

- write or state BDD-style acceptance examples when behavior or workflow changes
- use TDD or test-first discipline when code, automation, infrastructure, data transformation, or runtime behavior changes
- run lint, typecheck, build, unit, integration, contract, schema, E2E, or manual checks when applicable
- explain unavailable checks and provide the strongest substitute evidence
- re-run affected checks after repair
- record validation results in the PR and Linear handoff

Do not treat a passing diff review as enough for code, runtime, infrastructure, automation, or user-facing behavior when stronger checks are available.

## Documentation And Evidence

Update documentation when the change affects:

- future agent behavior
- execution workflow
- product behavior
- architecture boundaries
- validation gates
- observability or runtime operations
- delivery evidence expectations

Use the smallest durable artifact:

- PR body and Linear handoff for routine implementation notes
- ADR for durable technical decisions
- KDR/DAR for strategic, governance, or knowledge decisions
- LearningRecord candidate for reusable learning
- DeliveryEvidence or prose-equivalent evidence for completed delivery

## Follow-Up Ticket Rules

Create a follow-up only when the new work is:

- outside the current ticket scope
- material to safety, correctness, observability, validation, or future execution
- too large or risky to include in the current PR
- dependent on a decision, approval, account, secret, customer data, production data, or external action

Do not create follow-ups for vague improvement ideas, cosmetic preferences, or work already completed in the current PR.

Every follow-up should include:

- source ticket and PR
- reason it was not completed now
- acceptance criteria
- blocker or dependency
- suggested owner or agent

## Stop Conditions

Stop and record a blocker when:

- the ticket lacks approval required for the next action
- the Tactical Execution Plan is required but missing
- ADR/RFC decision is required before implementation
- validation fails on a relevant path
- implementation requires secrets, customer data, production data, billing, deployment, paid acquisition, external communication, or sensitive claims without approval
- the next slice would exceed the ticket scope
- branch protection, review, or merge policy cannot be satisfied

## Lightweight Loop Note

Use this note in a PR body, Linear comment, or Tactical Execution Plan when a standalone loop artifact is unnecessary:

```md
## Development Execution Loop

- Loop status: full / lightweight / not applicable
- Current slice:
- ADR/RFC decision:
- Validation checks:
- Repair actions:
- Documentation updates:
- Follow-up trigger:
- Handoff notes:
```

## BDD Examples

```txt
Given a development ticket with multiple implementation stories
When the agent starts branch work
Then the agent maps each story to an acceptance check and evidence requirement
And does not implement unrelated stories in the same PR.
```

```txt
Given a code or automation change has a failing relevant validation
When the agent prepares a PR for review
Then the failure is repaired or documented as a blocker
And the PR is not presented as merge-ready.
```

```txt
Given a design decision constrains future implementation tickets
When the agent chooses an approach
Then an ADR or explicit no-ADR rationale is recorded
And future agents can find the decision without reading chat history.
```

## Done Criteria

The development loop is complete when:

- planned slices were implemented or explicitly deferred
- ADR/RFC decision path is recorded
- validation results and unavailable checks are documented
- relevant failures were repaired or converted into blockers
- docs and evidence artifacts are updated
- follow-ups are created only when material and out of scope
- PR review can evaluate the change without chat history
- Linear handoff records scope, validation, risks, follow-ups, and next action
