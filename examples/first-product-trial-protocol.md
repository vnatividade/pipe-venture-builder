# First Product Trial Protocol

Use this protocol to test whether the repository can move one sample product idea through the full venture-builder pipeline without relying on conversational memory.

The first trial must use a sample idea only. Do not use a real business idea externally, contact customers, deploy to production, collect billing, run paid ads, or make public claims without explicit human approval.

## Purpose

The trial proves whether the template can produce a coherent chain from idea intake to learning handoff:

```txt
sample idea
-> product context
-> founder focus
-> C.O.N.T.R.O.L.E.
-> validation scorecard
-> ICP and customer-language memory
-> MVP scope
-> Working Backwards / PRD placeholder
-> architecture review placeholder
-> Linear proposal
-> KDR output
-> follow-up issues
```

## Trial Inputs

Use a fictional or internal sample idea with no private customer data.

Required input:

- sample idea name
- target market hypothesis
- problem hypothesis
- offer hypothesis
- primary channel hypothesis
- riskiest assumption
- known exclusions
- source artifacts used

Forbidden input:

- private founder biography
- secrets, credentials, or production data
- real customer names, recordings, transcripts, or identifiable quotes
- confidential third-party documents
- claims of real demand, revenue, interviews, or market proof without source artifacts

## Required Artifacts

Complete or update these artifacts in order.

| Step | Artifact | Purpose | Pass Condition |
|---|---|---|---|
| 1 | `product/product-context.md` | Capture sample idea context, current stage, assumptions, evidence links, privacy boundaries, and handoff. | Stage is explicit and assumptions are separated from evidence. |
| 2 | `product/founder-focus.md` | Narrow the sample idea to one market, one problem, one offer, and one channel. | Focus is narrow enough to validate. |
| 3 | `product/controle-evaluation.md` | Stress-test strategic coherence and choose Attack, Refine, Pivot, or Kill. | Verdict includes rationale, assumptions, and next action. |
| 4 | `validation/validation-scorecard.md` | Define whether the idea has enough evidence to proceed. | Scorecard identifies evidence, gaps, and GO / CONDITIONAL GO / NO-GO. |
| 5 | `validation/icp-profile.md` | Define the target customer segment and source basis. | ICP distinguishes assumptions from evidence. |
| 6 | `knowledge/customer-language-memory.md` | Capture only anonymized or sample language. | Language is marked as sample, synthetic, or sourced evidence. |
| 7 | `product/mvp-scope.md` | Define the core loop, riskiest assumption, smallest ethical test, cuts, and evidence threshold. | MVP loop is smaller than a feature backlog and includes GO / NO-GO. |
| 8 | Working Backwards / PRD placeholder | Describe the promise, non-goals, requirements, and success criteria without inventing evidence. | Product narrative stays tied to validation artifacts. |
| 9 | Architecture review placeholder | Identify minimum technical shape, constraints, integrations, data, and risks. | No implementation ticket is proposed before MVP and risk gates allow it. |
| 10 | Linear proposal | Propose small execution or follow-up tickets without creating them unless approved. | Tickets are scoped, sequenced, and tied to repository artifacts. |
| 11 | KDR output | Record the decision, rationale, evidence, risks, and revisit trigger. | Future agents can understand why the next action was chosen. |

If a placeholder artifact does not exist yet, write the minimum trial output inside the trial notes and recommend a follow-up ticket rather than creating broad new templates.

## Trial Steps

1. Open a dedicated Linear ticket and branch for the trial.
2. Copy the blank templates into a sample trial area or clearly mark sample content if editing existing examples.
3. Fill each artifact using the same sample idea and source assumptions.
4. Stop at every approval gate that would require external action, customer contact, billing, paid ads, production deployment, or sensitive data handling.
5. Record each blocked action as a trial finding, not as work to bypass.
6. Produce a Linear proposal with candidate follow-up tickets, dependencies, acceptance criteria, and approval requirements.
7. Produce a KDR output summarizing whether the pipeline is ready, needs refinement, or should stop.

## Success Criteria

The first trial succeeds when:

- every required artifact has a clear output or an explicit placeholder gap
- assumptions and evidence remain separate throughout the pipeline
- the sample idea stays narrow enough for MVP scoping
- GO / CONDITIONAL GO / NO-GO decisions are explicit
- no external action happens without approval
- no sensitive or private data enters repository artifacts
- Linear follow-up candidates are specific and tied to artifact gaps or trial findings
- KDR output explains the decision and revisit trigger

## Failure Criteria

The trial fails or pauses when:

- the sample idea becomes too broad to evaluate
- the artifacts contradict each other without a documented conflict
- a stage advances without required evidence or approval
- the trial needs real customer outreach, billing, production deployment, paid ads, or external communication
- sensitive data would be required to continue
- follow-up tickets would be speculative future/evolution work rather than current foundation fixes

## KDR Output

At the end of the trial, write a decision record with:

- decision:
- status: Ready / Needs refinement / Stop
- context:
- options considered:
- evidence used:
- assumptions still unresolved:
- risks:
- selected next action:
- follow-up ticket candidates:
- revisit trigger:
- owner:
- date:

## Follow-Up Issue Creation Rules

Create or propose follow-up Linear tickets only when the trial exposes a current operational gap.

Each follow-up should include:

- context from the trial
- problem or opportunity
- why it matters
- suggested scope
- acceptance criteria
- origin ticket and PR

Do not execute follow-ups labeled or described as future evolution during the current execution cycle.

## Trial Handoff

The final trial handoff should state:

- sample idea used
- artifacts completed
- artifacts missing or placeholder-only
- GO / CONDITIONAL GO / NO-GO outcome
- approvals encountered
- blocked external actions
- KDR output location
- follow-up tickets created or proposed
- residual risks
