# Raw Interview Evidence Intake And Synthesis

Use this workflow after approved discovery conversations, interviews, manual validation calls, or field notes when the founder needs Pipe to convert raw evidence into useful validation and product learning.

This workflow does not implement uploads, transcription, automatic ingestion, recording storage, customer data storage, or integration with external systems.

## Purpose

Pipe should learn from discovery without turning the repository into a private customer data store.

This workflow helps agents and the founder:

- distinguish raw notes, anonymized evidence, exact quotes, synthesis, assumptions, and decisions
- decide what can safely enter the repository
- convert interviews into validation scorecard updates
- update ICP, customer language, PMF evidence, contradiction synthesis, and learning artifacts
- record confidence changes and next evidence needed
- avoid hidden memory that future agents cannot audit

## When To Use

Use this workflow after:

- an approved customer interview
- an approved manual validation conversation
- an approved user observation or concierge test
- a private raw note batch that needs anonymized synthesis
- an approved call summary or transcript summary

Use this workflow before:

- updating `validation/validation-scorecard.md`
- updating `validation/icp-profile.md`
- updating `knowledge/customer-language-memory.md`
- updating `validation/pmf-evidence-metrics.md`
- creating or updating a LearningRecord
- changing MVP scope, PRD, growth, monetization, or build readiness

Do not use this workflow to:

- upload recordings or transcripts
- transcribe calls
- ingest files automatically
- store raw identifiable notes in the repository
- process credentials, private files, payment data, regulated data, or sensitive customer context
- claim representative market proof from a small or biased source batch

## Required Gates

Before processing evidence, check:

- `execution/approval-gates.md`
- `validation/customer-data-retention-policy.md`
- `validation/pre-user-security-privacy-readiness-gate.md`
- the origin Linear ticket
- the source interview or validation artifact

If approval is missing for raw notes, identifiable quotes, recordings, transcripts, customer files, or sensitive context, do not copy that material into the repository. Ask for a sanitized summary or keep the raw material outside the repository until a retention decision exists.

## Evidence Intake Categories

| Category | Examples | Repository treatment |
|---|---|---|
| Raw private notes | Unedited notes, call notes with names, private workflow detail, chat logs | Keep outside repository unless explicit approval defines storage and retention. |
| Recording or transcript | Audio, video, automated transcript, verbatim call record | Do not retain by default. Approval, storage owner, retention reason, and deletion date required. |
| Anonymized notes | Segment-level notes with identifiers removed | May enter repository when useful and minimally necessary. |
| Exact quote | Verbatim customer language | Only if anonymized or explicitly approved; keep separate from synthesis. |
| Observation | Behavior seen during workflow, demo, or manual test | May enter repository if anonymized and source is clear. |
| Objection log | Risks, objections, blockers, trust concerns | May enter repository when anonymized and not confidential. |
| Commitment signal | Time, intro, pilot interest, data sample, budget discussion | May enter repository when source and approval boundaries are clear. |
| Assumption | Founder or agent interpretation not yet proven | May enter repository only as an assumption, never as evidence. |
| Decision | GO, REFINE, NO-GO, scope change, next test | Store with source artifacts and rationale. |

## Forbidden Or Restricted Inputs

Do not store these in the repository:

- credentials, secrets, tokens, private keys, API keys, or production data
- payment details, financial account data, health data, legal records, regulated data, or identity documents
- private customer files, screenshots, exports, or confidential workflows without explicit approval
- names, emails, phone numbers, addresses, social handles, or company identifiers without explicit approval
- unapproved recordings, transcripts, or identifiable direct quotes
- raw notes retained beyond the active validation cycle without approval

If any of these appear in the source material, stop and follow the accidental capture procedure in `validation/customer-data-retention-policy.md`.

## Anonymization Steps

Before repository storage:

1. Replace real names with participant labels such as `P01`, `ICP-A-02`, or `Ops lead, anonymized`.
2. Remove emails, phone numbers, addresses, social handles, account identifiers, and file names.
3. Remove or generalize company names unless approval permits naming the company.
4. Generalize private workflows when exact details would reveal the source.
5. Separate exact quotes from interpretation.
6. Mark each item as quote, behavior, spend, workaround, objection, commitment, assumption, or synthesis.
7. Link to source artifacts without exposing private identifiers.
8. Record confidence and evidence limits.
9. Define what raw material was deleted, retained privately, or still needs retention review.

If anonymization removes the useful signal, keep the raw detail private and store only the validated pattern in the repository.

## Synthesis Procedure

Follow these steps for each interview or evidence batch.

### 1. Intake Boundary

- Origin ticket:
- Source artifact:
- Evidence owner:
- Raw material exists: yes/no
- Raw material storage location, if approved:
- Approval record:
- Retention/deletion date:
- Sensitive or restricted data present: yes/no

### 2. Evidence Extraction

Extract only what is useful for validation.

| Evidence item | Type | Segment | Source label | Confidence | Repository safe? | Notes |
|---|---|---|---|---|---|---|
|  | Quote / behavior / spend / workaround / objection / commitment / assumption |  |  | Low / Medium / High | Yes / No / Needs approval |  |

### 3. Exact Language

Exact language is powerful but risky. Store only anonymized or approved quotes.

| Quote | Topic | Emotional signal | Evidence type | Source label | Repository safe? |
|---|---|---|---|---|---|
|  |  |  | Pain / status quo / objection / willingness to pay / trigger |  | Yes / No / Needs approval |

### 4. Contradiction Synthesis

Do not force a positive conclusion.

| Field | Notes |
|---|---|
| Evidence supporting current thesis |  |
| Evidence contradicting current thesis |  |
| Ambiguous or mixed signals |  |
| Evidence that weakens ICP specificity |  |
| Evidence that weakens pain intensity |  |
| Evidence that weakens willingness to engage/pay |  |
| New risk, objection, or trust concern |  |
| Internal assumption still unproven |  |
| Confidence change | Increased / unchanged / decreased |
| Recommended decision impact | GO / CONDITIONAL GO / REFINE / NO-GO / BLOCKED |

### 5. Downstream Mapping

Map each synthesized learning to the artifact that should consume it.

| Learning | Target artifact | Update type | Required approval | Notes |
|---|---|---|---|---|
| ICP segment changed | `validation/icp-profile.md` | Segment / exclusion / trigger / confidence | Maybe |  |
| Score changed | `validation/validation-scorecard.md` | Evidence, score, contradiction review | Maybe |  |
| Customer language captured | `knowledge/customer-language-memory.md` | Quote bank / objection / status quo | Yes if identifiable |  |
| PMF signal observed | `validation/pmf-evidence-metrics.md` | Activation / commitment / false-positive warning | Maybe |  |
| MVP scope changed | `product/mvp-scope.md` | Scope, non-goal, threshold, risk | Human review required |  |
| Reusable lesson found | `knowledge/learning-record-policy.md` | LearningRecord candidate | Human review if promoting |  |
| Follow-up needed | Linear | New ticket or update | Depends on action |  |

### 6. Decision And Handoff

- What changed:
- What did not change:
- What got weaker:
- What got stronger:
- What remains only an assumption:
- Next evidence needed:
- Allowed next action:
- Blocked actions:
- Follow-up tickets:
- Raw notes deleted: yes/no/not applicable
- Private retention still open: yes/no/not applicable
- Residual privacy risk:

## Batch Synthesis Template

Copy this template when processing several interviews or notes together.

```md
# Discovery Evidence Synthesis

## Metadata

- Venture or idea:
- Origin ticket:
- Evidence batch:
- Date:
- Synthesizer:
- Source artifacts:
- Raw data handled in repository: yes/no
- Customer data approval record:
- Retention/deletion expectation:

## Source Coverage

| Source label | Segment | Evidence type | Approval status | Repository-safe summary |
|---|---|---|---|---|
|  |  | Interview / note / call summary / observation / objection log | Approved / Not approved / Needs review |  |

## Evidence Extracted

| Evidence | Type | Segment | Confidence | Target artifact | Notes |
|---|---|---|---|---|---|
|  | Quote / behavior / spend / workaround / objection / commitment / assumption |  | Low / Medium / High |  |  |

## Exact Language

| Quote | Anonymized source | Topic | Signal | Repository-safe? |
|---|---|---|---|---|
|  |  |  | Pain / status quo / objection / willingness to pay / trigger | Yes / No / Needs approval |

## Synthesis

- Confirmed evidence:
- Assumptions challenged:
- New assumptions:
- Status quo pattern:
- Trigger event:
- Willingness to engage/pay:
- Objections:
- Trust/privacy concern:
- Follow-up needed:

## Contradiction Review

- Evidence supporting the thesis:
- Evidence contradicting the thesis:
- Ambiguous or mixed signals:
- Confidence change: Increased / unchanged / decreased
- Decision impact: GO / CONDITIONAL GO / REFINE / NO-GO / BLOCKED

## Artifact Updates Required

- ICP profile:
- Validation scorecard:
- Customer language memory:
- PMF evidence metrics:
- MVP scope:
- LearningRecord candidate:
- Linear follow-up:

## Data Handling Handoff

- Raw notes deleted:
- Raw notes retained privately:
- Retention owner:
- Review/deletion date:
- Identifiable quotes retained:
- Recordings/transcripts retained:
- Residual privacy risk:
```

## GO / NO-GO Rules

| Decision | Use when | Allowed next action |
|---|---|---|
| GO | Evidence is anonymized, source coverage is clear, retention is handled, and downstream updates are scoped. | Update repository artifacts and Linear handoff. |
| CONDITIONAL GO | One low-risk retention or source-coverage item needs clarification. | Resolve the item before promoting evidence into strategy or scorecard. |
| BLOCKED | Approval, sensitive data, recordings, identifiable quotes, or retention are unresolved. | Stop and document a non-sensitive blocker in Linear. |
| NO-GO | Evidence cannot be safely anonymized or would create misleading validation claims. | Do not store or promote it; revise collection approach. |

## Quality Bar

A good synthesis:

- keeps raw data out of the repository unless explicitly approved
- separates exact quotes from interpretation
- marks assumptions as assumptions
- names confidence and source coverage
- includes contradictory evidence
- updates only the artifacts justified by the evidence
- records what was deleted, retained privately, or still needs review
- avoids claims about customers, PMF, revenue, integrations, or willingness to pay without source artifacts

## Relationship To Existing Artifacts

- Use `validation/customer-interview-template.md` for per-interview capture.
- Use `validation/respondent-targeting-and-interview-planner.md` before interviews to define who to seek and what to ask.
- Use `validation/customer-data-retention-policy.md` for approval, retention, anonymization, deletion, and accidental capture.
- Use `validation/validation-scorecard.md` for evidence scoring and contradiction review.
- Use `knowledge/customer-language-memory.md` for anonymized customer language and reusable patterns.
- Use `knowledge/learning-record-policy.md` when the synthesis produces reusable operating or validation learning.
