# E2E Applicability Matrix

This matrix defines when Playwright, agent-browser exploration, screenshots, videos, and traces are required for Pipe delivery evidence.

It complements `execution/test-oriented-delivery-rule.md` and feeds `/pipe:check` in `execution/pipe-check-command-spec.md`.

It does not install Playwright, write E2E tests, create browser automation, configure CI, contact external systems, or change approval gates.

## Core Rule

E2E or browser evidence is required when a delivery changes a user-facing or agent-facing interactive flow.

Do not require E2E for prose-only documentation, architecture notes, governance docs, schema-only work, or research synthesis unless the ticket also changes an interactive surface.

When E2E is not run for a ticket where it would normally apply, the PR and Linear handoff must include a rationale and substitute evidence.

## Evidence Types

Use these terms consistently.

| Evidence type | Meaning | Strength |
|---|---|---|
| Playwright automated E2E | Repeatable browser test that asserts critical user/agent flow behavior. | Strongest for stable web flows. |
| Agent-browser exploratory evidence | Manual or agent-driven browser interaction with notes and observed result. | Useful for exploratory or early UI validation. |
| Screenshot | Static visual proof of a state. | Good for layout/state confirmation, weak for behavior. |
| Video | Recording of a flow. | Good for demos and behavior review, not a substitute for assertions. |
| Trace | Debuggable execution artifact showing steps, requests, console, and timing. | Strong for diagnosing E2E failures or complex flows. |
| Console/network observation | Browser console, request, or response observation. | Useful supporting evidence, not usually enough alone. |

## Required, Optional, Or Not Applicable

Use these categories in PR and Linear handoff.

| Category | Meaning |
|---|---|
| Required | Must be present before merge unless blocked with documented rationale and approved substitute evidence. |
| Conditional | Required only when the ticket changes a relevant interaction, integration, or high-risk path. |
| Exploratory acceptable | Agent-browser evidence is acceptable; automated Playwright can be deferred. |
| Optional | Useful but not necessary for merge. |
| Not applicable | The delivery has no interactive surface affected. |

## Applicability Matrix

| Delivery surface | Playwright automated E2E | Agent-browser exploratory evidence | Screenshots | Videos | Traces | Notes |
|---|---|---|---|---|---|---|
| Frontend critical user flow | Required | Conditional as pre-check or fallback | Required for visual change | Conditional for complex flow | Required on failure or flaky behavior | Examples: signup, onboarding, checkout, permissions, destructive actions. |
| Frontend non-critical UI change | Conditional | Exploratory acceptable | Required when layout/state changes | Optional | Conditional on failure | Examples: copy/layout tweaks, non-blocking settings panel. |
| Frontend visual-only change | Conditional | Exploratory acceptable | Required | Optional | Optional | Screenshot should show before/after or final state. |
| Frontend accessibility-affecting change | Required when flow is critical | Conditional | Required | Optional | Conditional | Include keyboard/focus behavior when relevant. |
| Backend/API with no UI change | Not applicable | Optional only for API-driven UI smoke | Not applicable | Not applicable | Conditional for integration debugging | Use unit/integration/contract tests instead. |
| Backend/API that changes user-visible behavior | Conditional | Conditional | Conditional | Optional | Conditional | If UI path exists and changed behavior is observable, run browser validation. |
| MCP/tooling connector | Conditional | Exploratory acceptable when connector has UI or browser-visible workflow | Conditional | Optional | Conditional | Do not call external tools or mutate state without approval. |
| Agent workflow or cockpit UI | Required for interactive workflow screens | Exploratory acceptable during early design | Required for stateful UI | Conditional | Required on failure or long-running flow | Agent-facing UI counts as interactive surface. |
| CLI command with no UI | Not applicable | Not applicable | Not applicable | Optional for demos only | Conditional for logs/debugging | Use command output, exit code, fixtures, and logs instead. |
| CLI that launches browser or modifies browser-visible app | Conditional | Conditional | Conditional | Optional | Conditional | Browser evidence applies only to the affected browser-visible path. |
| Documentation-only | Not applicable | Not applicable | Optional when documenting UI state | Optional | Not applicable | Use path/link/scope checks. |
| Governance-only | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Use policy consistency checks. |
| Architecture-only | Not applicable | Not applicable | Optional for diagrams if relevant | Not applicable | Not applicable | Use decision and downstream-consumer checks. |
| Schema-only | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Use JSON/schema checks and examples. |
| Research/validation artifact | Not applicable unless delivered through UI | Optional if reviewing a research UI | Optional | Optional | Not applicable | Use source/citation/confidence checks. |
| Product page or landing page | Required for interactive conversion path | Conditional | Required | Conditional for funnel demo | Conditional on failure | E2E should cover primary CTA and responsive state when applicable. |
| Billing, payments, pricing collection | Required when implemented | Conditional only in safe sandbox | Required when UI changes | Conditional | Required on failure | Requires explicit approval; no live billing without approval. |
| Auth, permissions, privacy, security-sensitive flow | Required | Conditional as supplement, not replacement | Required when UI changes | Optional | Required on failure | Missing E2E is usually P1 for critical paths. |

## When Playwright Is Required

Playwright automated E2E is required when:

- a critical user-facing flow changes
- auth, permissions, onboarding, checkout, billing, privacy, or destructive actions change
- a frontend behavior change could regress conversion, access, data entry, or state transitions
- a prior E2E exists for the affected path
- `/pipe:check` classifies missing E2E as P1
- the ticket explicitly requires E2E

If Playwright is not installed or no test harness exists, record:

- why it cannot be run
- what substitute evidence was used
- whether the gap blocks merge
- whether a follow-up is required

## When Agent-Browser Evidence Is Acceptable

Agent-browser exploratory evidence is acceptable when:

- the UI is early, exploratory, or documentation-adjacent
- the ticket changes non-critical UI behavior
- Playwright is not installed and the risk is low/medium
- the goal is visual/interaction confirmation rather than regression coverage
- a human-readable observation is enough for the current ticket

Agent-browser evidence should include:

- target URL or local path
- steps taken
- observed result
- screenshots when visual state matters
- console/network notes when relevant
- limitations

Agent-browser evidence is not enough by itself when:

- the flow is critical
- auth, billing, privacy, security, permissions, or destructive actions changed
- repeated regression protection is needed
- the ticket explicitly requires automated E2E

## Screenshots, Videos, And Traces

Screenshots are required when:

- visual layout changes
- stateful UI is introduced or changed
- a PR claims a screen renders correctly
- responsive or mobile layout matters
- agent-browser is used as substitute evidence for a UI change

Videos are required only when:

- a multi-step interaction is difficult to understand from screenshots
- a reviewer needs to see transition, drag/drop, animation, or timing
- the ticket explicitly asks for video evidence

Traces are required when:

- Playwright fails or is flaky
- debugging needs step/request/console timing
- the flow spans multiple pages or async states
- auth, permissions, billing, or critical state transitions are involved
- the ticket explicitly asks for trace evidence

Do not include screenshots, videos, or traces containing secrets, credentials, customer data, production data, or private evidence.

## Exceptions

Exceptions require rationale in both PR and Linear handoff.

Valid exception reasons:

- no interactive surface changed
- Playwright is not installed and installation is out of scope
- no local app can be run safely
- browser validation would require secrets, customer data, production data, billing, or external action without approval
- the flow is backend/API-only and covered by stronger contract/integration tests
- the change is documentation/governance/schema-only
- test flakiness is unrelated and documented with a follow-up

Invalid exception reasons:

- "small change" without explaining risk
- "not tested" without substitute evidence
- "browser not needed" for user-facing behavior changes
- skipping E2E because it is inconvenient
- using screenshots alone for a critical behavioral flow

## `/pipe:check` Integration

`/pipe:check` should read this matrix after identifying delivery type and changed files.

It should classify missing browser evidence as:

- P1 when required E2E is missing for critical user-facing, auth, billing, permission, privacy, destructive, or high-risk flows
- P2 when browser evidence would materially improve confidence but the path is not critical
- P3 when evidence packaging could be clearer but adequate evidence exists
- no finding when E2E is not applicable and rationale is recorded

`/pipe:check` should include the E2E decision in output:

```json
{
  "evidence": {
    "e2e": "required|present|missing|not_applicable|blocked_with_rationale"
  },
  "missingEvidence": [
    "E2E/browser evidence"
  ]
}
```

## Ten-Ticket Classification Dry Run

| Example ticket | Surface | Required evidence | Classification |
|---|---|---|---|
| Add onboarding form validation | Frontend critical user flow | Playwright E2E, tests, screenshot or trace on failure | E2E required |
| Update homepage hero copy only | Frontend non-critical UI | Screenshot, path/link check; Playwright optional unless CTA behavior changes | Agent-browser acceptable |
| Add backend score calculation endpoint | Backend/API no UI | Unit/integration/contract tests; browser not applicable | E2E not applicable |
| Change API response consumed by dashboard | Backend/API user-visible behavior | API tests plus browser validation of affected dashboard state | E2E conditional |
| Add Linear MCP status update workflow doc | Governance/workflow doc | Policy consistency and path checks | E2E not applicable |
| Build agent cockpit task queue screen | Agent workflow UI | Playwright E2E for core queue actions; screenshots | E2E required |
| Add CLI command that prints validation report | CLI no UI | Command output, exit code, fixture checks | E2E not applicable |
| Add CLI command that opens local preview page | CLI browser-visible | Command check plus browser smoke validation | E2E conditional |
| Define schema for DeliveryEvidence | Schema-only | JSON syntax/schema checks, examples | E2E not applicable |
| Add pricing collection flow | Billing/pricing collection | Explicit approval, sandbox E2E, screenshots, trace on failure | E2E required with approval |

## PR And Linear Handoff Language

Use one of these forms:

```txt
E2E/browser evidence: Required and completed with <tool/check/artifact>.
```

```txt
E2E/browser evidence: Not applicable because this is documentation/governance/schema-only and no interactive surface changed.
```

```txt
E2E/browser evidence: Normally required, but blocked because <reason>. Substitute evidence: <evidence>. Follow-up: <ticket/link or none with rationale>.
```

```txt
E2E/browser evidence: Agent-browser exploratory check completed. Playwright automated E2E deferred because <reason>; risk is <low/medium/high>.
```

## Done Criteria

This matrix is working when:

- agents can decide whether Playwright is required before merge
- agent-browser evidence is used only where exploratory evidence is acceptable
- screenshots, videos, and traces are requested for the right reasons
- documentation and governance tickets are not overburdened with E2E
- frontend and agent-facing flows are not closed with prose-only evidence
- `/pipe:check` can classify missing E2E evidence by severity
- exceptions are visible in PR and Linear handoff
