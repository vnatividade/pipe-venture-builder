# Test-Oriented Delivery Rule

This rule defines what evidence is required before a Pipe ticket can be considered delivered.

It complements `schemas/DeliveryEvidence.schema.json`, `execution/ticket-pr-handoff-system.md`, and the future `/pipe:check` delivery gate. It does not install test tooling, configure CI, add Playwright, implement `/pipe:check`, or change approval gates.

## Core Rule

No relevant implementation is complete without evidence.

Evidence can be automated, manual, documentary, or review-based depending on the delivery surface, but it must be explicit. If a validation type is not applicable or unavailable, the PR and Linear handoff must say why.

Do not write "not tested" as a shortcut when a stronger check is available.

## Evidence Sources

Use the strongest relevant evidence available for the ticket:

- BDD scenario or acceptance example
- unit test
- integration test
- contract or schema check
- lint or static validation
- typecheck
- build
- migration or rollback check
- E2E or browser check
- path/link sanity check
- manual review against the ticket type matrix
- PR review finding classification
- DeliveryEvidence-style handoff

`schemas/DeliveryEvidence.schema.json` is the canonical structured evidence package for completed delivery records. PRs and Linear handoffs may use prose, but they should preserve the same evidence intent: expected behavior, acceptance criteria, tests, E2E, artifacts, risks, manual validation, and recommendation.

## Applicability By Delivery Type

Use this table with `execution/ticket-type-field-matrix.md`.

| Delivery type | BDD / acceptance examples | TDD / automated tests | E2E / browser evidence | Minimum evidence when automation is not relevant |
|---|---|---|---|---|
| `architecture` | Required when the decision changes downstream behavior. | Not normally required. | Not applicable unless architecture affects a UI or runtime flow. | Path/link sanity, consistency check against related architecture/execution docs, explicit downstream consumer notes. |
| `documentation` | Required when docs define a process or expected reader behavior. | Not normally required. | Not applicable unless docs publish a user-facing flow. | Path/link sanity, scope check against Linear ticket, no unsupported claims. |
| `prompt` | Required for expected agent behavior and non-behavior. | Conditional when prompt fixtures or evals exist. | Not normally required. | Trigger/non-trigger examples, stop-condition review, approval-gate consistency check. |
| `skill` | Required for trigger and non-trigger cases. | Conditional when skill execution can be tested locally. | Not normally required. | Skill contract review, input/output example, stop-condition review. |
| `workflow` | Required for state transitions and stop conditions. | Conditional when workflow has scripts or schemas. | Not normally required. | Manual walkthrough against Linear/GitHub/repository state transitions. |
| `governance` | Required for allowed and forbidden behavior. | Not normally required. | Not applicable unless governance controls a runtime flow. | Consistency check against `AGENTS.md`, approval gates, and affected protocols. |
| `code` | Required for user, agent, or system behavior changed. | Required when tests can reasonably cover the changed logic. | Required for user-facing flows; conditional for backend-only work. | If tests are unavailable, document why and provide the strongest local/manual check. |
| `infrastructure` | Required for operational behavior and rollback. | Required when config or scripts can be validated. | Conditional when infrastructure affects a user flow. | Config validation, dry-run or plan output when available, rollback/mitigation evidence. |
| `automation` | Required for trigger, success, skip, and failure behavior. | Required when automation logic is implemented. | Conditional when automation touches UI/browser flows. | Dry-run, disabled-mode, or manual execution evidence; audit and stop-condition review. |
| `observability` | Required for the decision each signal enables. | Conditional when instrumentation can be tested. | Conditional when signal depends on a user flow. | Signal presence check, sample log/metric/event shape, actionability review. |
| `product` | Required for user outcome and acceptance. | Conditional when implementation is included. | Required when user-facing experience changes. | Validation artifact review, KPI/evidence boundary check, no invented customer proof. |
| `research` | Required for research question and acceptance. | Not normally required. | Not applicable unless research output is delivered through a UI. | Source quality, citation, contradiction, confidence, and unsupported-claim review. |
| `validation` | Required for hypothesis, test method, and GO/NO-GO criteria. | Conditional when validation tooling is implemented. | Conditional when validating an interactive flow. | Evidence plan, source/customer-data boundary review, manual validation summary. |
| `orchestration-prep` | Required for future orchestrator assumptions and stop conditions. | Not normally required until runtime tooling exists. | Not applicable unless evaluating an orchestrator UI. | Readiness checklist, dependency review, no implementation or dispatch evidence. |

## BDD Rule

Use BDD-style acceptance examples when the ticket changes expected behavior, workflow, governance, product validation, or agent routing.

BDD examples should state:

- given context
- when action happens
- then expected outcome
- and forbidden outcome, when risk matters

Example:

```txt
Given a documentation-only governance ticket
When the agent prepares final delivery evidence
Then automated code tests may be marked not applicable with a reason
And path, link, scope, and approval-gate checks must still be recorded
```

BDD does not require a test framework unless the ticket explicitly implements executable behavior.

## TDD Rule

Use TDD or test-first discipline when a ticket changes code, automation logic, infrastructure scripts, runtime behavior, data transformation, validation tooling, or command behavior.

At minimum, the PR should state:

- expected behavior before implementation
- test or check added or updated
- command run
- result
- reason a test could not be added, if applicable

If no local test framework exists, use the smallest meaningful validation available and create a follow-up only when the gap is material.

## E2E Rule

Use E2E or browser evidence when the delivery changes a user-facing or agent-facing interactive flow.

E2E is usually required for:

- frontend behavior
- onboarding or form flows
- checkout, billing, or payment flows
- login or permission flows
- workflow screens used by agents or humans
- any change where visual layout or interaction correctness matters

E2E is usually not required for:

- prose-only documentation
- architecture notes
- schema-only changes
- governance docs
- research synthesis
- backend-only changes without a user-visible path

When E2E is not run for a user-facing change, the PR must explain why and record the substitute evidence.

PIP-158 will define the dedicated Playwright and agent-browser applicability matrix. Until then, use this rule as the minimum boundary.

## Documentation And Governance Tickets

Documentation and governance tickets can be delivered without automated tests when they do not change executable behavior.

They still require evidence:

- target files changed
- links and paths checked
- acceptance criteria mapped
- related policies checked for conflicts
- unsupported claims avoided
- approval gates preserved
- no unrelated scope added

For these tickets, `git diff --check`, path existence checks, `rg` checks, and manual consistency review are valid evidence when recorded clearly.

## Code, Runtime, Integration, And Automation Tickets

Code, runtime, integration, and automation tickets need stronger evidence.

Expected evidence:

- tests for changed behavior when available
- lint/typecheck/build when available
- contract/schema checks when structured data changes
- integration or dry-run checks when external systems are involved
- E2E/browser checks when user-facing behavior changes
- rollback or mitigation notes for risky changes
- observability notes when runtime behavior changes

If any expected evidence cannot be produced, document the reason and whether the gap is blocking.

## DeliveryEvidence Relationship

DeliveryEvidence should answer:

- What changed?
- What behavior was expected?
- Which acceptance criteria were checked?
- Which tests or checks ran?
- Was E2E required?
- Which artifacts support the delivery?
- What risks remain?
- What manual validation happened?
- Is the recommendation ready, ready with warnings, blocked, or not applicable?

PR descriptions and Linear handoffs do not need to embed a full JSON object unless a ticket asks for it, but they must preserve these answers.

## `/pipe:check` Relationship

`/pipe:check` is the future delivery quality gate that should inspect whether evidence is complete enough for the ticket type.

Until `/pipe:check` exists:

- reviewers and agents must apply this rule manually
- PRs must record validation evidence directly
- Linear handoffs must state unavailable validation explicitly
- P0/P1 review findings still block merge

PIP-156 will specify `/pipe:check` inputs, output JSON, severity logic, and pass/fail conditions.

## Stop Conditions

Stop and record a blocker when:

- a relevant implementation has no evidence and no credible reason
- a critical path lacks tests or substitute validation
- E2E is required for a user-facing change but cannot be run
- validation fails and the failure is relevant
- evidence would require secrets, customer data, production data, or external action without approval
- the ticket asks to mark Done before review, validation, or handoff is complete

## Done Criteria

A ticket satisfies this rule when:

- evidence type matches the delivery type
- unavailable validation is explained
- acceptance criteria are checked
- risks and residual gaps are recorded
- DeliveryEvidence intent is reflected in PR and Linear handoff
- review findings are classified
- P0 and P1 findings are resolved
- follow-ups exist for material evidence gaps outside scope
