# `/pipe:check` Command Specification

This specification defines `/pipe:check` as a manually executable delivery quality gate.

It does not implement a command runner, CI automation, GitHub Action, MCP tool, or runtime integration.

Use it with:

- `execution/test-oriented-delivery-rule.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/ticket-type-field-matrix.md`
- `schemas/DeliveryEvidence.schema.json`
- `schemas/LearningRecord.schema.json`
- `execution/approval-gates.md`

## Purpose

`/pipe:check` verifies whether a PR or delivery handoff has enough evidence for its delivery type before review completion or merge.

It should prevent:

- evidence-free delivery
- documentation tickets being overburdened with irrelevant code tests
- code/runtime/integration tickets being closed with only prose
- missing DeliveryEvidence when delivery risk or complexity requires it
- missing LearningRecord candidates when reusable learning was discovered
- hidden validation gaps in PR or Linear handoff

## Non-Goals

`/pipe:check` does not:

- run tests
- install dependencies
- configure CI
- call external services
- approve PRs
- merge PRs
- create Linear tickets
- replace human review
- override approval gates
- prove product, customer, legal, financial, compliance, privacy, or security claims

## When To Run

Run `/pipe:check` manually:

- before requesting review when a PR is opened
- after review fixes
- before merge
- before marking a documentary or investigative ticket Done
- when validation evidence changed
- when a PR touches code, runtime, workflow, governance, validation, automation, observability, product, or research artifacts

For tiny prose-only updates, `/pipe:check` can be a short manual checklist. It should still record why heavier validation is not applicable.

## Inputs

Required inputs:

```json
{
  "linearTicketId": "PIP-156",
  "linearTicketUrl": "https://linear.app/...",
  "deliveryType": "documentation",
  "branch": "codex/pip-156-pipe-check-command-spec",
  "pullRequestUrl": "https://github.com/...",
  "changedFiles": [],
  "includedScope": [],
  "excludedScope": [],
  "acceptanceCriteria": [],
  "validationPerformed": [],
  "reviewStatus": {
    "reviewRequested": true,
    "reviewSource": "copilot|codex|manual-fallback|human",
    "p0": 0,
    "p1": 0,
    "p2": 0,
    "p3": 0
  },
  "deliveryEvidencePresent": false,
  "learningRecordPresent": false,
  "learningRecordNotApplicableReason": "No reusable learning discovered.",
  "residualRisks": []
}
```

Optional inputs:

```json
{
  "deliveryEvidencePathOrUrl": "schemas/DeliveryEvidence.schema.json",
  "learningRecordPathOrUrl": "schemas/LearningRecord.schema.json",
  "e2eEvidencePathOrUrl": null,
  "artifactPathsOrUrls": [],
  "blockedReason": null,
  "followUpLinks": [],
  "manualCheckNotes": []
}
```

## Output JSON

`/pipe:check` should produce this result shape:

```json
{
  "schemaVersion": "0.1.0",
  "command": "/pipe:check",
  "checkedAt": "2026-05-26",
  "linearTicketId": "PIP-156",
  "pullRequestUrl": "https://github.com/...",
  "deliveryType": "documentation",
  "status": "pass",
  "recommendation": "ready_for_review",
  "summary": "Evidence is complete for a documentation/governance delivery.",
  "findings": [],
  "evidence": {
    "deliveryEvidence": "not_required",
    "bdd": "present",
    "tests": "not_applicable",
    "e2e": "not_applicable",
    "artifacts": "present",
    "risk": "present",
    "learningRecord": "not_applicable"
  },
  "missingEvidence": [],
  "requiredFollowUps": [],
  "residualRisk": []
}
```

Allowed `status` values:

```txt
pass
pass_with_warnings
fail
blocked
not_applicable
```

Allowed `recommendation` values:

```txt
ready_for_review
ready_to_merge
needs_fixes
needs_human_decision
needs_follow_up
blocked
not_applicable
```

## Finding Shape

Every finding should use this shape:

```json
{
  "id": "PCHECK-001",
  "severity": "P1",
  "category": "missing_tests",
  "message": "Code behavior changed but no test or substitute validation is recorded.",
  "blocking": true,
  "evidenceRequired": "unit or integration test, or documented reason with substitute validation",
  "source": "execution/test-oriented-delivery-rule.md",
  "suggestedFix": "Add or run relevant tests, or document why unavailable and provide substitute validation."
}
```

Allowed severity values:

```txt
P0
P1
P2
P3
```

Allowed categories:

```txt
scope
acceptance_criteria
bdd
missing_tests
missing_e2e
missing_artifacts
missing_delivery_evidence
missing_learning_record
risk
approval
review
unsupported_claims
stale_handoff
follow_up
residual_risk
```

## Severity Logic

Use the same P0/P1/P2/P3 semantics as PR review.

P0 examples:

- validation evidence would require secrets, customer data, production data, or external action without approval
- PR changes billing, legal, compliance, privacy, security-sensitive, production, or customer-facing claims without approval
- delivery claims customer proof, revenue, willingness to pay, clinical/legal/financial conclusion, or production impact without source evidence

P1 examples:

- code/runtime behavior changed with no tests and no credible substitute validation
- required E2E evidence is missing for a user-facing critical flow
- acceptance criteria are not mapped
- relevant validation failed
- review has unresolved P0 or P1 findings
- implementation scope does not match the Linear ticket

P2 examples:

- DeliveryEvidence is missing for a medium-risk non-code delivery where prose evidence exists but structured evidence would improve traceability
- LearningRecord candidate is missing when reusable learning probably exists
- monitoring or rollback evidence is weak but not blocking for the delivery type
- follow-up candidate is relevant but not yet filed

P3 examples:

- wording could be clearer
- non-blocking artifact link could be more convenient
- evidence summary could be more concise

## Pass / Fail Conditions

Return `pass` when:

- acceptance criteria are mapped
- included scope is delivered
- excluded scope is preserved
- evidence matches the delivery type
- required validations passed
- review is complete or ready to request, depending on run phase
- no unresolved P0/P1 exists
- risk and residual gaps are recorded
- LearningRecord is present or explicitly not applicable

Return `pass_with_warnings` when:

- no P0/P1 exists
- evidence is sufficient for the delivery type
- one or more P2/P3 findings remain and are documented
- required follow-ups exist or are clearly named

Return `fail` when:

- required evidence is missing
- relevant validation failed
- acceptance criteria are not checked
- P0/P1 remains unresolved
- delivery type requires tests/E2E and neither evidence nor substitute is present

Return `blocked` when:

- required approval is missing
- required source artifacts are missing
- branch ownership or write set is unclear
- GitHub review or branch protection state prevents the next step
- safe evidence collection would require gated data or external action

Return `not_applicable` only when:

- the ticket has no delivery artifact to check
- the reason is recorded in Linear or PR
- a human or assigned ticket explicitly agrees the gate is unnecessary

## Type-Aware Evidence Matrix

Use `execution/test-oriented-delivery-rule.md` as the source of truth.

Quick mapping:

| Delivery type | `/pipe:check` should require |
|---|---|
| `documentation` | changed files, path/link sanity, acceptance mapping, no unsupported claims, tests/E2E not-applicable reason |
| `governance` | allowed/forbidden behavior, approval-gate consistency, affected protocol links, tests/E2E not-applicable reason |
| `architecture` | decision/constraint, downstream consumers, related-doc consistency, path/link sanity |
| `prompt` | trigger/non-trigger examples, expected behavior, stop conditions, prompt scope boundary |
| `skill` | trigger/non-trigger examples, input/output expectations, stop conditions, consumer list |
| `workflow` | state transition walkthrough, owner handoff, stop conditions, Linear/GitHub/repository interaction |
| `code` | behavior expectation, tests when available, lint/typecheck/build when available, E2E if user-facing, risk/rollback if relevant |
| `infrastructure` | config validation, dry-run/plan when available, rollback/mitigation, secret/data approval check |
| `automation` | trigger, success/skip/failure behavior, dry-run or disabled-mode evidence, audit/observability |
| `observability` | signal shape, decision enabled, sample/log/event/metric evidence, owner and threshold |
| `product` | user outcome, KPI/evidence boundary, validation artifact, E2E if user-facing implementation changed |
| `research` | source quality, citations, contradictions, confidence, unsupported-claim boundary |
| `validation` | hypothesis, method, GO/NO-GO, evidence boundary, customer-data/outreach approval check |
| `orchestration-prep` | readiness checklist, dependency review, no implementation or autonomous dispatch |

## DeliveryEvidence Rule

`DeliveryEvidence` is required when:

- the ticket implements or changes code behavior
- runtime, automation, infrastructure, observability, or user-facing product behavior changes
- the delivery is medium/high risk and future agents need structured evidence
- the ticket explicitly asks for DeliveryEvidence
- review identifies traceability gaps that prose cannot safely cover

`DeliveryEvidence` is usually optional when:

- the ticket is documentation-only
- the change is a narrow architecture/governance clarification
- the PR and Linear handoff already preserve the DeliveryEvidence intent in prose

If optional, `/pipe:check` should still confirm why it is optional.

## LearningRecord Rule

`LearningRecord` is required or a candidate must be proposed when:

- execution reveals reusable learning for future agents
- a capability succeeds, fails, or needs routing changes in a reusable way
- a validation method becomes reusable
- a repeated blocker or workflow failure appears
- future agents would otherwise need conversational memory to understand the lesson

`LearningRecord` is not required when:

- delivery is routine
- no reusable learning was discovered
- the result is a one-off implementation detail
- the note belongs in PR/Linear handoff only

`/pipe:check` should flag missing LearningRecord as:

- P1 only when durable learning is required by the ticket or critical for safe continuation
- P2 when reusable learning appears likely but not blocking
- no finding when the handoff states a clear not-applicable reason

## Manual Execution Checklist

Use this sequence until a runner exists:

1. Read the Linear ticket.
2. Identify delivery type and risk.
3. Read PR description and changed files.
4. Check acceptance criteria against delivered scope.
5. Check excluded scope was preserved.
6. Apply the type-aware evidence matrix.
7. Confirm BDD/acceptance examples when behavior or workflow changed.
8. Confirm tests, lint, build, schema checks, or substitute evidence.
9. Confirm E2E/browser evidence if user-facing or agent-facing interaction changed.
10. Confirm artifacts and links exist.
11. Confirm risks and residual gaps are recorded.
12. Confirm review state and unresolved findings.
13. Confirm DeliveryEvidence is present or not required.
14. Confirm LearningRecord is present or not applicable.
15. Return pass/fail/blocker JSON.

## Dry Run 1: Recent Documentation PR

Scenario:

```txt
PIP-157 added `execution/test-oriented-delivery-rule.md` and linked it from execution docs.
```

Manual input summary:

- deliveryType: `governance`
- changedFiles:
  - `execution/test-oriented-delivery-rule.md`
  - `execution/README.md`
  - `execution/ticket-pr-handoff-system.md`
- tests: not applicable because no executable behavior changed
- e2e: not applicable because no user-facing flow changed
- artifacts: present
- DeliveryEvidence: optional because prose PR and Linear handoff preserve evidence intent
- LearningRecord: not applicable because no reusable runtime learning was discovered beyond the rule itself

Expected `/pipe:check` result:

```json
{
  "schemaVersion": "0.1.0",
  "command": "/pipe:check",
  "linearTicketId": "PIP-157",
  "deliveryType": "governance",
  "status": "pass",
  "recommendation": "ready_to_merge",
  "summary": "Governance delivery has appropriate documentary evidence and no code/E2E requirement.",
  "findings": [],
  "evidence": {
    "deliveryEvidence": "not_required",
    "bdd": "present",
    "tests": "not_applicable",
    "e2e": "not_applicable",
    "artifacts": "present",
    "risk": "present",
    "learningRecord": "not_applicable"
  },
  "missingEvidence": [],
  "requiredFollowUps": [],
  "residualRisk": [
    "CI, Playwright, and executable /pipe:check remain future tickets."
  ]
}
```

Why it passes:

- documentation/governance evidence is enough
- tests and E2E have explicit not-applicable reasons
- DeliveryEvidence intent is preserved in PR/Linear handoff
- follow-ups already exist for `/pipe:check` and E2E matrix

## Dry Run 2: Hypothetical Code PR

Scenario:

```txt
A code PR changes onboarding form validation and error display.
```

Manual input summary:

- deliveryType: `code`
- changedFiles:
  - `app/onboarding/Form.tsx`
  - `app/onboarding/validation.ts`
- BDD: present for valid and invalid submission
- tests: unit tests for validation logic passed
- build/typecheck: passed
- E2E: missing
- artifacts: PR summary present
- DeliveryEvidence: required because user-facing behavior changed
- LearningRecord: not applicable unless a reusable validation pattern or failure is found

Expected `/pipe:check` result:

```json
{
  "schemaVersion": "0.1.0",
  "command": "/pipe:check",
  "linearTicketId": "PIP-XXX",
  "deliveryType": "code",
  "status": "fail",
  "recommendation": "needs_fixes",
  "summary": "Code delivery has unit evidence but is missing required E2E/browser evidence for a user-facing onboarding flow.",
  "findings": [
    {
      "id": "PCHECK-001",
      "severity": "P1",
      "category": "missing_e2e",
      "message": "User-facing onboarding behavior changed without E2E or browser evidence.",
      "blocking": true,
      "evidenceRequired": "Playwright, browser interaction check, or documented blocker with approved substitute evidence.",
      "source": "execution/test-oriented-delivery-rule.md",
      "suggestedFix": "Run or add targeted onboarding E2E/browser validation before merge."
    },
    {
      "id": "PCHECK-002",
      "severity": "P1",
      "category": "missing_delivery_evidence",
      "message": "DeliveryEvidence is required for this user-facing code behavior change.",
      "blocking": true,
      "evidenceRequired": "DeliveryEvidence-style structured handoff covering expected behavior, tests, E2E, artifacts, risks, and recommendation.",
      "source": "schemas/DeliveryEvidence.schema.json",
      "suggestedFix": "Add DeliveryEvidence or an equivalent structured PR/Linear evidence block."
    }
  ],
  "evidence": {
    "deliveryEvidence": "missing",
    "bdd": "present",
    "tests": "present",
    "e2e": "missing",
    "artifacts": "present",
    "risk": "present",
    "learningRecord": "not_applicable"
  },
  "missingEvidence": [
    "E2E/browser evidence",
    "DeliveryEvidence"
  ],
  "requiredFollowUps": [],
  "residualRisk": []
}
```

Why it fails:

- user-facing behavior changed
- E2E/browser evidence is required by the test-oriented delivery rule
- DeliveryEvidence is required for structured traceability
- missing evidence is P1 because it blocks safe merge

## Done Criteria

This specification is working when:

- agents can manually decide pass/fail from PR and Linear artifacts
- documentation and governance tickets are not forced into irrelevant code tests
- code/runtime/integration tickets cannot pass with prose-only validation
- missing DeliveryEvidence is flagged when structured evidence is required
- missing LearningRecord is flagged only when durable learning is required or likely
- future automation can implement the JSON result shape without inventing semantics
