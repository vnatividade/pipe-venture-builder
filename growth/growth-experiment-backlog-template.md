# Growth Experiment Backlog Template

Use this template to capture, prioritize, and sequence validated growth experiments without turning growth ideas into automatic execution.

Use it with `growth/distribution-strategy-framework.md`, `growth/channel-experiment-template.md`, `validation/validation-scorecard.md`, `product/mvp-scope.md`, `knowledge/knowledge-curator-workflow.md`, `execution/linear-governance-model.md`, and `execution/approval-gates.md`.

## Boundary

This backlog is a planning and sequencing artifact. It does not authorize publishing, outreach, paid ads, paid acquisition, scraping, automated messaging, growth automation, billing, customer data handling, or external communications.

Every external action requires human approval before execution. Items stay in `Idea` or `Blocked` until approvals, evidence, and scope are explicit.

Unvalidated growth work must not be treated as P0. Growth ideas may be urgent to inspect, but execution priority depends on evidence, approval state, and fit with the current product stage.

## Backlog States

| State | Meaning | Entry rule | Exit rule |
|---|---|---|---|
| Idea | A growth hypothesis, channel option, message, loop, audience, or experiment candidate. | Captured with source, owner, and why it might matter. | Move to `Approved Experiment`, `Blocked`, or `Killed` after evidence and gate review. |
| Approved Experiment | A scoped experiment that is approved to prepare or run within the allowed boundary. | Has channel strategy, measurable hypothesis, approval status, risk review, and GO/NO-GO threshold. | Move to `Running` when execution starts, or back to `Idea` / `Blocked` if scope changes. |
| Running | An approved experiment currently being executed manually or within approved constraints. | Human approval exists for any external action, and the experiment has an owner and timebox. | Move to `Learned`, `Killed`, or `Blocked` based on result and risk. |
| Learned | A completed experiment with result, threshold comparison, learning card, and repository or Linear update. | Result has been interpreted as GO, NO-GO, INCONCLUSIVE, or BLOCKED. | Inform next backlog item, distribution strategy, validation scorecard, or MVP scope after review. |
| Killed | An idea or experiment that should not continue in the current stage. | Evidence, risk, scope, cost, or approval review makes continuation inappropriate. | Reopen only with new evidence, changed product stage, or explicit human approval. |
| Blocked | An item cannot proceed because a gate, dependency, claim review, data review, or approval is unresolved. | Missing required approval, artifact, evidence, owner, metric, threshold, or risk mitigation. | Move only after blocker is resolved and recorded. |

The minimum required separation is `Idea`, `Approved Experiment`, `Running`, `Learned`, and `Killed`. Use `Blocked` when the reason for non-movement should remain visible.

## Required Backlog Columns

| Column | Required value |
|---|---|
| Backlog ID | Stable identifier or Linear issue link. |
| Title | Short objective name. |
| State | Idea / Approved Experiment / Running / Learned / Killed / Blocked. |
| Origin | Source ticket, PR, strategy artifact, research artifact, validation artifact, or manual observation. |
| Target persona | Specific ICP or persona. |
| Channel | One selected channel or channel candidate. |
| Hypothesis | What should happen and why. |
| Primary metric | One measurable learning or conversion metric. |
| GO threshold | Evidence needed to continue. |
| NO-GO threshold | Evidence or risk that stops the experiment. |
| Evidence links | Links to validation, research, channel strategy, prior learning, or customer-safe artifacts. |
| Approval label | approval:required / approval:granted / approval:blocker / approval:not-needed. |
| Risk label | risk:low / risk:medium / risk:high. |
| Priority label | priority:P1 / priority:P2 / priority:P3. Do not use P0 for unvalidated growth. |
| Stage gate | Draft / Evidence Review / Approval Review / Ready / Running / Learning Review / Closed. |
| Owner | Person or agent responsible for the next action. |
| Timebox | Maximum duration once running. |
| Cost | Free / approved cost cap / blocked by paid spend. |
| External action involved | yes/no. |
| Paid spend involved | yes/no. |
| Automation involved | yes/no. |
| Sensitive claim involved | yes/no. |
| Customer/private data involved | yes/no. |
| Next action | One concrete next step or blocker resolution. |
| Learning link | Link to learning card after completion. |

## Priority Rules

Use priority to decide sequencing, not to override gates.

| Priority | Use when | Default action |
|---|---|---|
| P1 | The experiment is approved, tied to a current validation or MVP learning need, low-risk, and likely to unblock the next product decision. | Execute next after current ticket finishes. |
| P2 | The experiment is relevant and evidence-linked, but not required for the next product decision or has minor unresolved uncertainty. | Keep visible; schedule after P1 work. |
| P3 | The idea is plausible but early, weakly evidenced, future-stage, or dependent on a later channel/product decision. | Preserve as context; do not execute now. |
| Blocked | Required approval, artifact, owner, metric, evidence, or risk review is missing. | Resolve blocker or kill. |

Do not assign P0 to growth ideas that have not been validated. P0 is reserved for critical risks, production blockers, security issues, data loss, or unsafe external impact under `execution/approval-gates.md`.

Increase priority only when:

- evidence links are specific and current
- the item maps to MVP scope or validation scorecard learning
- approval status is clear
- the experiment has one metric and thresholds
- the next action is manual, narrow, and safe

Decrease priority or block the item when:

- evidence is missing or speculative
- the item depends on paid spend, automation, scraping, or outreach without approval
- the metric is vanity engagement
- the experiment would broaden MVP scope
- claims, customer data, privacy, legal, financial, compliance, or security risk is unresolved

## Stage Gates

| Gate | Required before moving forward |
|---|---|
| Draft | Origin, persona, channel, and hypothesis exist. |
| Evidence Review | Evidence links are present, limitations are explicit, and no unsupported claims are added. |
| Approval Review | Required approvals are recorded for external action, outreach, publishing, paid spend, automation, sensitive claims, or data handling. |
| Ready | Owner, metric, thresholds, timebox, cost, and stop condition are defined. |
| Running | Experiment has started only within approved boundaries. |
| Learning Review | Result, threshold comparison, confidence, and learning card are complete. |
| Closed | Next action is captured, follow-up tickets are created if needed, and the item is marked `Learned` or `Killed`. |

If any gate fails, mark the item as `Blocked` or keep it in `Idea`. Do not move it to `Approved Experiment`.

## Approval Labels

Use approval labels to make gate status obvious:

- `approval:not-needed`: the next action is internal planning only.
- `approval:required`: the next action crosses an approval gate and approval is not recorded.
- `approval:granted`: approval is explicit in the current Linear ticket, PR, or current thread.
- `approval:blocker`: the item cannot proceed until approval is supplied or scope changes.

Approval labels do not replace the approval record. Link the source in `Evidence links` or `Origin`.

## Backlog Template

```md
# Growth Experiment Backlog

## Metadata

- Product:
- Owner:
- Date:
- Source distribution strategy:
- Source validation scorecard:
- Human approval required before external execution: yes

## Backlog

| ID | Title | State | Priority | Approval | Stage gate | Owner | Evidence links | Next action |
|---|---|---|---|---|---|---|---|---|
|  |  | Idea / Approved Experiment / Running / Learned / Killed / Blocked | P1 / P2 / P3 / Blocked | required / granted / blocker / not-needed | Draft / Evidence Review / Approval Review / Ready / Running / Learning Review / Closed |  |  |  |

## Item Detail - <ID / title>

### Scope

- Origin:
- Target persona:
- Channel:
- Hypothesis:
- Primary metric:
- GO threshold:
- NO-GO threshold:
- Timebox:
- Cost:

### Evidence

- Distribution strategy:
- Channel experiment:
- Validation scorecard:
- Research artifact:
- Prior learning:
- Evidence gap:

### Gates

| Gate | Status | Link or note |
|---|---|---|
| Evidence review | Passed / Blocked / Not needed |  |
| External action approval | Granted / Required / Blocked / Not needed |  |
| Publishing approval | Granted / Required / Blocked / Not needed |  |
| Outreach approval | Granted / Required / Blocked / Not needed |  |
| Paid spend approval | Granted / Required / Blocked / Not needed |  |
| Automation/scraping approval | Granted / Required / Blocked / Not needed |  |
| Sensitive claim review | Passed / Blocked / Not needed |  |
| Customer/private data review | Passed / Blocked / Not needed |  |

### Execution State

- State:
- Stage gate:
- Owner:
- Started:
- Ended:
- Result:
- Decision: GO / NO-GO / INCONCLUSIVE / BLOCKED / KILLED
- Learning link:
- Follow-up ticket:

### Closeout

- What was learned:
- Threshold comparison:
- Confidence: Low / Medium / High
- Impact on validation scorecard:
- Impact on distribution strategy:
- Impact on MVP scope:
- Next backlog state:
```

## Linear Usage Notes

When represented in Linear, use issues, labels, or views to mirror state, priority, approval status, and risk. Do not treat a Linear label as approval by itself.

Recommended label families:

- state: `growth:idea`, `growth:approved-experiment`, `growth:running`, `growth:learned`, `growth:killed`, `growth:blocked`
- priority: `priority:P1`, `priority:P2`, `priority:P3`
- approval: `approval:required`, `approval:granted`, `approval:blocker`, `approval:not-needed`
- risk: `risk:low`, `risk:medium`, `risk:high`

Create or change Linear labels/views only through the appropriate approved governance ticket.

## Done Criteria

This backlog model is complete when:

- backlog states separate `Idea`, `Approved Experiment`, `Running`, `Learned`, and `Killed`
- required columns include priority, evidence links, stage gates, approval labels, owner, metric, thresholds, and next action
- unvalidated growth work cannot become P0
- external actions, paid growth, automation, outreach, publishing, sensitive claims, and data handling remain gated
- completed experiments require learning updates
- Linear labels/views are described as future representation, not automatic execution
