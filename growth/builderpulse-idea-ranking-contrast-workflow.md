# BuilderPulse Idea Ranking Contrast Workflow

Use this workflow when a captured BuilderPulse signal needs to be compared against an internal idea ranking, opportunity shortlist, validation plan, or prioritization hypothesis.

BuilderPulse can challenge the Pipe's assumptions. It must not become an authority that automatically promotes, kills, or reorders ideas.

## Boundary

This workflow does not authorize:

- auto-promoting ideas
- auto-demoting ideas
- changing roadmap priority without human review
- treating BuilderPulse as validation evidence by itself
- creating build, PRD, launch, monetization, or outreach work from a signal alone
- bypassing C.O.N.T.R.O.L.E., validation scorecards, customer discovery, or market validation gates
- creating KDR/DAR records unless a durable strategic decision actually changed

Every ranking change remains a proposal until a human reviews the source, relevance, confidence, and evidence gap.

## Required Inputs

Do not run this contrast workflow unless these inputs exist:

- origin Linear ticket
- captured BuilderPulse signal review from `growth/builderpulse-monitoring-workflow.md`
- stable BuilderPulse source URL
- publication date or observed date
- idea, venture, market, persona, channel, or ranking factor being compared
- current internal assumption or ranking rationale
- current validation evidence, if any

If the BuilderPulse signal lacks citation, date, or clear relevance, stop and mark the contrast as `NO-GO: insufficient source`.

## Contrast Outcomes

Each signal must produce exactly one primary outcome.

| Outcome | Meaning | Allowed effect | Blocked effect |
|---|---|---|---|
| Strengthen | The signal supports an existing assumption or ranking factor. | Increase confidence as a hypothesis; add validation question. | Auto-raise score or priority. |
| Weaken | The signal contradicts or weakens an assumption. | Lower confidence or flag contradiction. | Auto-kill the idea. |
| Create question | The signal is relevant but incomplete. | Add research, discovery, or interview question. | Treat ambiguity as proof. |
| No impact | The signal is too weak, irrelevant, stale, or uncited. | Record no change. | Create follow-up noise. |

## Contrast Matrix

Use this matrix to compare one or more BuilderPulse signals against internal ranking factors.

```md
# BuilderPulse / Idea Ranking Contrast

## Metadata

- Origin ticket:
- Reviewer:
- Review date:
- BuilderPulse source URL:
- Publication date:
- Related idea or venture:
- Current ranking artifact:
- Human review required before priority change: yes

## Current Internal Ranking Rationale

- Current rank or priority:
- Ranking factors currently used:
- Current confidence:
- Source artifacts:
- Known assumptions:

## Signal-To-Idea Mapping

| BuilderPulse signal | Signal type | Idea/ranking factor affected | Strengthen / weaken / create question / no impact | Confidence change | Contradiction note | Evidence still needed |
|---|---|---|---|---|---|---|
|  | Builder behavior / market pattern / persona hint / channel hint / product pattern / objection or risk / traction proxy / contradiction | Pain / ICP / wedge / channel / timing / competition / defensibility / founder fit / risk |  | Increase / unchanged / decrease / unknown |  |  |

## Ranking Decision Proposal

- Proposed ranking effect: no change / confidence note / ranking review needed / defer
- Rationale:
- Human review required:
- Scorecard impact:
- C.O.N.T.R.O.L.E. impact:
- Validation plan impact:
- Discovery question impact:
- KDR/DAR update needed: yes/no
- Follow-up ticket needed: yes/no

## Blocked Actions

- Auto-promote idea:
- Auto-demote idea:
- Create build ticket:
- Create outreach or launch action:
- Make customer-facing claim:
```

## Confidence Change Rules

Use BuilderPulse to change confidence only as a hypothesis unless stronger evidence exists.

| Source condition | Maximum confidence effect |
|---|---|
| Stable source URL, recent publication, clear relevance, but no customer evidence | Add advisory confidence note only. |
| Signal supports an existing assumption already backed by customer evidence | Strengthen confidence modestly; customer evidence remains primary. |
| Signal contradicts an unsupported assumption | Decrease confidence or create contradiction question. |
| Signal contradicts customer evidence | Do not override customer evidence; create contradiction review. |
| Signal is stale, vague, uncited, vanity-based, or irrelevant | No ranking impact. |

BuilderPulse can lower confidence faster than it can raise confidence. A contradiction may reveal a blind spot, but a positive signal rarely proves demand.

## KDR/DAR Update Triggers

Recommend a KDR/DAR update only when the contrast produces a durable decision future agents must understand.

KDR/DAR may be needed when:

- a previously accepted strategic assumption is materially weakened
- a ranking factor changes across multiple ideas
- a market, channel, or persona assumption is superseded
- a contradiction changes a GO / REFINE / NO-GO path
- a human accepts a priority change based on combined evidence

KDR/DAR is not needed when:

- the signal only creates a research question
- the signal is weak or advisory
- the PR/Linear handoff already captures routine status
- no durable strategic decision changed

Use `knowledge/kdr-dar-template.md` and `knowledge/decision-conflict-protocol.md` if a KDR/DAR is required.

## Follow-Up Ticket Criteria

Create or recommend a follow-up ticket only when the contrast identifies a specific next action:

- research a named contradiction or source claim
- interview a named persona segment suggested by the signal
- update a validation plan with specific questions
- run a manual channel test after approval
- review ranking for a named set of ideas using cited evidence
- draft a KDR/DAR after human acceptance of a durable decision

Do not create follow-ups for generic trend watching, curiosity, weak hype, or uncited signals.

## Done Criteria

This workflow is complete when:

- every BuilderPulse signal can be mapped to an idea or ranking factor
- each signal produces `strengthen`, `weaken`, `create question`, or `no impact`
- confidence changes are explicit and evidence-bounded
- contradiction notes are captured
- KDR/DAR triggers are defined
- priority changes require human review
- auto-promotion is explicitly blocked

## Relationship To Existing Artifacts

- Start with `growth/builderpulse-monitoring-workflow.md` to capture and classify the signal.
- Use `growth/idea-browser-validation-workflow.md` when BuilderPulse and Idea Browser both inform idea comparison.
- Use `validation/validation-scorecard.md` to keep BuilderPulse from over-inflating validation evidence.
- Use `product/controle-evaluation.md` when a signal affects strategic fit.
- Use `knowledge/kdr-dar-template.md` only when a durable decision changes.
- Use `knowledge/decision-conflict-protocol.md` if the contrast conflicts with accepted repository decisions.
