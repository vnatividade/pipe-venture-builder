# Synthetic Vs Real Interview Comparison Template

Use this template to compare synthetic persona outputs against real customer interview evidence after discovery conversations exist.

This artifact is the guardrail that prevents synthetic critique from becoming false market proof.

## Boundary

This template does not authorize:

- replacing interviews with synthetic personas or simulations
- filling comparison rows without real interview evidence
- inventing quotes, customers, metrics, willingness to pay, demand, adoption, or product-market-fit signals
- upgrading validation score from synthetic output alone
- changing ranking, PRD, MVP scope, pricing, launch, outreach, or build priority without real evidence and human review
- storing sensitive, identifiable, private, regulated, confidential, or customer raw data without approval

If no real customer evidence is available, stop. Record the comparison as `Blocked - no real interview evidence`.

## Required Inputs

Before comparison, link:

- origin Linear ticket
- synthetic persona generation review
- synthetic persona simulation output
- synthetic objection/risk extraction
- real interview evidence synthesis
- `validation/synthetic-persona-generation-workflow.md`
- `validation/synthetic-persona-simulation-prompt.md`
- `validation/synthetic-objection-risk-extraction-workflow.md`
- `validation/raw-interview-evidence-intake-and-synthesis.md`
- `validation/validation-scorecard.md`
- `validation/customer-data-retention-policy.md`

Use anonymized synthesis by default. Do not paste raw interview notes, personal data, or exact quotes unless the customer data retention policy and approval record allow it.

## Comparison Flow

### 1. Evidence Eligibility Gate

Confirm real evidence exists and can be used.

| Check | Pass/Fail | Notes |
|---|---|---|
| Real interview synthesis exists |  |  |
| Interview evidence is anonymized or approved |  |  |
| Customer data retention policy was followed |  |  |
| Synthetic persona and simulation are linked |  |  |
| Objection/risk extraction is linked |  |  |
| No raw sensitive or identifiable data is pasted |  |  |
| Comparison will not be used as proof beyond source evidence |  |  |

If the gate fails, do not compare. Create or recommend a follow-up for missing interview synthesis, privacy review, or evidence repair.

### 2. Agreement And Contradiction Mapping

Compare each major synthetic prediction or objection against interview evidence.

| Synthetic claim, objection, or risk | Source basis | Real interview evidence | Match type | Evidence strength | Confidence update | Action |
|---|---|---|---|---|---|---|
|  | persona / simulation / extraction artifact | interview synthesis / quote reference / observed behavior / none | Agrees / Contradicts / Partially agrees / Blind spot / Not tested | None / Weak / Medium / Strong | Increase / Decrease / No change / Unknown | keep testing / revise hypothesis / downgrade confidence / ignore / run follow-up |

Definitions:

- `Agrees`: real evidence supports the synthetic claim.
- `Contradicts`: real evidence points in the opposite direction.
- `Partially agrees`: evidence supports only part of the claim or only a subset of respondents.
- `Blind spot`: interviews reveal a material issue the synthetic output missed.
- `Not tested`: interviews did not cover the claim.

Rules:

- Synthetic agreement can increase confidence only when real evidence is medium or strong.
- Synthetic contradiction should reduce confidence or trigger hypothesis repair.
- Synthetic misses should be logged as blind spots and used to improve future prompts.
- `Not tested` cannot raise confidence.
- Do not let synthetic output outweigh interview evidence.

### 3. Synthetic Miss Register

Track what the synthetic workflow failed to catch.

| Miss | Miss type | Real evidence source | Why the synthetic output missed it | Impact | Improvement needed |
|---|---|---|---|---|---|
|  | Missing objection / wrong objection / wrong channel / wrong buyer / wrong urgency / wrong workflow / privacy blind spot / other |  | source gap / prompt gap / persona gap / assumption bias / unknown | Low / Medium / High | persona source repair / simulation prompt update / interview guide update / risk review |

High-impact synthetic misses should become follow-up candidates only when they are concrete and evidence-backed.

### 4. Evidence Score Update

Update validation confidence based on real evidence, not synthetic output.

| Validation area | Prior state | Interview evidence | Synthetic comparison result | Score update | Rationale |
|---|---|---|---|---|---|
| Problem urgency | Unknown / Weak / Medium / Strong |  | agreement / contradiction / blind spot / not tested | increase / decrease / no change |  |
| Status quo and alternatives | Unknown / Weak / Medium / Strong |  |  |  |  |
| Persona fit | Unknown / Weak / Medium / Strong |  |  |  |  |
| Buying or willingness to engage | Unknown / Weak / Medium / Strong |  |  |  |  |
| Channel reachability | Unknown / Weak / Medium / Strong |  |  |  |  |
| Trust, privacy, or risk | Unknown / Weak / Medium / Strong |  |  |  |  |
| MVP scope | Unknown / Weak / Medium / Strong |  |  |  |  |

Score update rules:

- Increase only with real interview evidence.
- Decrease when interviews contradict synthetic assumptions.
- Keep unchanged when the comparison is synthetic-only or not tested.
- Flag any score update that would affect PRD, MVP, ranking, monetization, outreach, or build priority for human review.

### 5. Interview Follow-Up Mapping

Turn gaps and contradictions into the next discovery batch.

| Follow-up question or test | Trigger | Target respondent profile | Evidence needed | Priority | Owner |
|---|---|---|---|---|---|
|  | contradiction / blind spot / not tested / weak evidence / privacy concern |  |  | P1 / P2 / P3 |  |

Use `validation/respondent-targeting-and-interview-planner.md` before contacting or selecting real people. This comparison does not authorize outreach.

### 6. Decision

Choose one outcome.

| Decision | Use when | Allowed next action |
|---|---|---|
| Evidence-supported update | Interview evidence is medium/strong and traceable. | Update validation scorecard and related artifact with source links. |
| Confidence downgrade | Interviews contradict synthetic assumptions or reveal false positives. | Lower confidence, revise hypothesis, or adjust interview guide. |
| More discovery needed | Evidence is weak, mixed, or not tested. | Plan next interview batch. |
| Synthetic method repair needed | Synthetic misses are material or repeated. | Create a follow-up to improve persona generation, simulation, or extraction workflow. |
| Blocked - no real interview evidence | No interview evidence exists or cannot be used. | Do not compare; run or synthesize real discovery first. |
| Privacy review needed | Evidence includes sensitive or identifiable data without approval. | Stop until privacy review is recorded. |

## Output Template

```md
# Synthetic Vs Real Interview Comparison

## Metadata

- Origin ticket:
- Reviewer:
- Date:
- Synthetic persona:
- Simulation artifact:
- Objection/risk extraction:
- Interview evidence synthesis:
- Customer data retention check:
- Human review required before prioritization: yes

## Evidence Eligibility Gate

| Check | Pass/Fail | Notes |
|---|---|---|
| Real interview synthesis exists |  |  |
| Evidence is anonymized or approved |  |  |
| Retention policy followed |  |  |
| Synthetic artifacts linked |  |  |
| No raw sensitive or identifiable data pasted |  |  |

## Agreement And Contradiction Mapping

| Synthetic claim, objection, or risk | Source basis | Real interview evidence | Match type | Evidence strength | Confidence update | Action |
|---|---|---|---|---|---|---|
|  |  |  | Agrees / Contradicts / Partially agrees / Blind spot / Not tested | None / Weak / Medium / Strong | Increase / Decrease / No change / Unknown |  |

## Synthetic Miss Register

| Miss | Miss type | Real evidence source | Why the synthetic output missed it | Impact | Improvement needed |
|---|---|---|---|---|---|
|  |  |  |  | Low / Medium / High |  |

## Evidence Score Update

| Validation area | Prior state | Interview evidence | Synthetic comparison result | Score update | Rationale |
|---|---|---|---|---|---|
| Problem urgency |  |  |  |  |  |
| Status quo and alternatives |  |  |  |  |  |
| Persona fit |  |  |  |  |  |
| Buying or willingness to engage |  |  |  |  |  |
| Channel reachability |  |  |  |  |  |
| Trust, privacy, or risk |  |  |  |  |  |
| MVP scope |  |  |  |  |  |

## Interview Follow-Up Mapping

| Follow-up question or test | Trigger | Target respondent profile | Evidence needed | Priority | Owner |
|---|---|---|---|---|---|
|  | contradiction / blind spot / not tested / weak evidence / privacy concern |  |  | P1 / P2 / P3 |  |

## Decision

- Evidence-supported update / Confidence downgrade / More discovery needed / Synthetic method repair needed / Blocked - no real interview evidence / Privacy review needed
- Rationale:
- Scorecard update needed:
- Follow-up needed:
- Human review status:
```

## Follow-Up Ticket Criteria

Create or recommend a follow-up only when comparison identifies a concrete evidence-backed action:

- run a specific next discovery batch
- repair missing interview synthesis
- run privacy review for a named evidence source
- improve a synthetic persona prompt because of a repeated miss
- update a validation scorecard based on real evidence
- revise an interview guide for a named contradiction or blind spot

Do not create follow-ups from synthetic-only agreement, unsupported enthusiasm, or untested claims.

## Done Criteria

This template is complete when:

- real interview evidence is required before comparison
- agreement, contradiction, blind spots, and untested claims are separated
- confidence updates are tied to real evidence strength
- synthetic misses are explicitly captured
- evidence score updates cannot come from synthetic output alone
- interview follow-ups are concrete and traceable
- privacy and retention boundaries are explicit

## Relationship To Existing Artifacts

- Use `validation/raw-interview-evidence-intake-and-synthesis.md` as the real evidence source.
- Use `validation/synthetic-objection-risk-extraction-workflow.md` as the synthetic objection source.
- Use `validation/validation-scorecard.md` only after real evidence strength is clear.
- Use `validation/respondent-targeting-and-interview-planner.md` for the next discovery batch.
- Use `validation/customer-data-retention-policy.md` before storing or referencing customer-derived material.
