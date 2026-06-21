# Solution Path Decision

Use this artifact during idea intake when the founder's idea could follow different discovery and execution paths.

The selected path should be confirmed before founder focus, C.O.N.T.R.O.L.E., validation planning, PRD, MVP scope, architecture, or implementation work. It does not authorize outreach, PRD, build work, customer data handling, external communication, or Linear ticket creation by itself.

## Purpose

Pipe should ask the founder how they want to proceed before assuming every idea is a market-facing venture.

The three solution paths are:

| Path | Use when | Discovery posture | Expansion rule |
|---|---|---|---|
| Market-facing solution | The founder wants to test whether a broader market wants the solution. | Identify respondent profiles, manual source paths, discovery questions, and market validation evidence. | PRD, MVP, growth, monetization, and build work require Market Validation Before Code. |
| Own-pain solution | The founder wants to solve their own operational pain first. | Map the founder/operator workflow, constraints, current workaround, dogfooding criteria, and internal success evidence. | Treat market expansion as a later decision requiring external evidence and approval. |
| Specific-person solution | The founder wants to solve a problem for one named or specific person first. | Run deep discovery with that person, define the bespoke context, and avoid generalizing too early. | Treat market expansion as a later decision requiring repeated patterns beyond the first person. |

## Founder-Facing Question

Ask in plain language:

```txt
How do you want to proceed with this idea right now?

1. Turn it into a market-facing solution.
2. Solve my own operational pain first.
3. Build a specific solution for one person first.
```

If the user's prior message clearly selects a path, restate the inferred path and ask for confirmation before recording it.

## Decision Template

```md
# Solution Path Decision - <idea or venture>

## Metadata

- Origin ticket:
- Date:
- Owner:
- Product or idea:
- Decision status: Draft / Confirmed / Superseded

## Selected Path

- Path: Market-facing solution / Own-pain solution / Specific-person solution
- Founder confirmation:
- Why this path fits:
- Why the other paths are not first:

## Discovery Implications

- Primary discovery subject:
- Evidence needed before next stage:
- Manual source or observation path:
- Questions this path must answer:
- Privacy or sensitive context:

## Allowed Next Actions

- Allowed now:
- Blocked until evidence or approval:
- Next repository artifact:
- Next Linear action, if approved:

## Expansion Rule

- What would justify expanding beyond this path:
- Evidence required for expansion:
- Human approval required:
- Follow-up ticket trigger:
```

## Path-Specific Rules

### Market-Facing Solution

Use the existing validation path:

- define ICP and exclusions
- plan respondent targeting and interviews
- collect real evidence or source-backed market signals
- apply `validation/market-validation-before-code-gate.md` before PRD or build work

Do not treat synthetic personas, internal enthusiasm, market-size research, or generic public signals as customer demand.

### Own-Pain Solution

Start from the founder/operator workflow:

- current workflow and trigger event
- current workaround
- time, money, risk, or quality cost
- internal success criteria
- dogfooding plan
- what would make the solution useful even if it never becomes a market product

Do not claim market validation from internal dogfooding. If the solution may become a venture later, create a follow-up validation path with external evidence.

### Specific-Person Solution

Start from the specific person's context:

- role, workflow, constraints, and decision authority
- exact problem and current workaround
- success criteria for that person
- bespoke requirements that should not be generalized
- privacy and retention boundaries

Do not turn one person's request into a market claim. Generalization requires repeated patterns, respondent targeting, and a new Market Validation Before Code decision.

## GO / NO-GO Rules

| Decision | Use when | Allowed next action |
|---|---|---|
| GO | One path is confirmed, implications are clear, and no gated external action is implied. | Continue to founder focus, C.O.N.T.R.O.L.E., or the path-specific discovery step. |
| CONDITIONAL GO | The path is likely but one ambiguity remains. | Ask one clarifying question before creating downstream artifacts. |
| BLOCKED | The next action would require outreach, customer data, external communication, PRD, build, or ticket creation without approval. | Stop and record the blocker. |
| NO-GO | The path choice is incoherent, unsafe, or tries to bypass validation. | Reframe the idea or return to intake. |

## Relationship To Existing Artifacts

- Use `product/product-context.md` to store the selected path summary.
- Use `product/founder-focus.md` after the path is clear.
- Use `execution/conversational-founder-guide.md` for the user-facing front-door question.
- Use `validation/respondent-targeting-and-interview-planner.md` for market-facing discovery.
- Use `validation/market-validation-before-code-gate.md` before PRD, MVP, architecture, implementation, growth, or monetization work for market-facing or market-expansion paths.
