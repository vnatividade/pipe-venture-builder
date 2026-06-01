# Synthetic Persona Generation Workflow

Use this workflow to create synthetic personas from explicit evidence and assumptions for pre-development critique.

Synthetic personas are hypothesis pressure-testing artifacts. They are not real customers, validation evidence, market proof, willingness-to-pay evidence, or prioritization authority.

Canonical output schema:

- `schemas/SyntheticPersona.schema.json`

## Boundary

This workflow does not authorize:

- automatic persona creation from sensitive data
- use of identifiable customer, prospect, employee, partner, or private business data without approval
- treating synthetic personas as customer evidence
- replacing interviews, observed behavior, source research, or validation scorecards
- creating PRD, build, monetization, launch, pricing, billing, outreach, or paid acquisition tickets
- changing priority without human review

If sensitive, private, regulated, confidential, or identifiable data is needed, stop until human approval and privacy review are recorded.

## Required Inputs

Before generation, link:

- origin Linear ticket
- `schemas/SyntheticPersona.schema.json`
- `validation/synthetic-persona-schema.md`
- `validation/icp-profile.md`
- `validation/persona-ranking-rubric.md`
- `validation/customer-data-retention-policy.md`
- `validation/respondent-targeting-and-interview-planner.md`, when the persona should become discovery questions
- source artifacts and assumptions

Do not generate a synthetic persona from no source context.

## Generation Flow

### 1. Source And Privacy Gate

Classify every input before generation.

| Input | Source type | Contains sensitive or identifiable data? | Approved for use? | Allowed use |
|---|---|---|---|---|
|  | ICP / interview synthesis / research / Idea Browser / BuilderPulse / founder assumption / other | yes/no/unknown | yes/no/N/A | evidence-backed trait / assumption / excluded |

Rules:

- Prefer anonymized synthesis over raw notes.
- Prefer repository artifacts over chat memory.
- Do not use private raw customer notes unless retention and use are approved.
- Do not use secrets, credentials, personal contact data, payment details, health data, legal data, or confidential business data.
- If approval is unclear, exclude the source and record the gap.

### 2. Evidence And Assumption Separation

Separate traits before writing the persona.

| Trait or claim | Classification | Source artifact | Confidence | Real-world validation needed |
|---|---|---|---|---|
|  | Evidence-backed / research-informed / founder-assumed / synthetic inference / source gap |  | Low / Medium / High |  |

Evidence-backed traits must link to a source artifact. Speculative traits must be labeled as assumptions or synthetic inference.

### 3. Source Gap Review

Do not hide missing evidence inside polished persona prose.

| Gap | Why it matters | Risk if ignored | Validation needed |
|---|---|---|---|
|  |  |  |  |

If the persona depends mostly on gaps, mark it as `Blocked-insufficient`.

### 4. Generation Prompt

Use this prompt only after steps 1-3 are complete.

```txt
Create a synthetic persona for hypothesis pressure-testing only.

Use only the source traits and assumptions listed below.
Separate evidence-backed traits from speculative traits.
Do not invent customer evidence, quotes, willingness to pay, market proof, commitments, budget, integrations, or validation.
Do not include personal identifiers or sensitive data.
Every claim must include source basis and confidence.
Every pain, buying, adoption, objection, or risk hypothesis must include a real-world validation test.
Output must conform to schemas/SyntheticPersona.schema.json.

Synthetic-not-proof banner:
Synthetic persona for hypothesis pressure-testing only. Not customer evidence.

Source traits:
<paste evidence-backed traits>

Assumptions:
<paste assumptions>

Source gaps:
<paste source gaps>
```

### 5. Schema Completion Check

Before using the output, verify:

| Requirement | Pass/Fail | Notes |
|---|---|---|
| Includes synthetic-not-proof banner |  |  |
| Records source basis and source artifacts |  |  |
| Separates evidence-backed traits from assumptions |  |  |
| Records confidence for major claims |  |  |
| Names real-world validation needed |  |  |
| Avoids sensitive or identifiable data |  |  |
| Includes forbidden uses |  |  |
| Requires human review before prioritization |  |  |
| Does not imply customer evidence |  |  |

### 6. Review Decision

Choose one.

| Decision | Use when | Allowed next action |
|---|---|---|
| Ready as hypothesis | Source basis is sufficient, sensitive data is absent, and confidence is bounded. | Use for critique, questions, and risk extraction. |
| Needs source repair | Missing source links, mixed assumptions, or unclear confidence. | Fix source table before use. |
| Needs privacy review | Sensitive/private/identifiable data may be involved. | Stop until approval and privacy review. |
| Blocked-insufficient | No source context or mostly unsupported traits. | Do not use persona. |

## Output Template

```md
# Synthetic Persona Generation Review

## Metadata

- Origin ticket:
- Reviewer:
- Date:
- Schema:
- Human review required before prioritization: yes
- Privacy review required: yes/no

## Source And Privacy Gate

| Input | Source type | Sensitive/identifiable? | Approved? | Allowed use |
|---|---|---|---|---|
|  | ICP / synthesis / research / signal / assumption | yes/no/unknown | yes/no/N/A | evidence-backed trait / assumption / excluded |

## Evidence-Backed Traits

| Trait | Source artifact | Confidence | Notes |
|---|---|---|---|
|  |  | Low / Medium / High |  |

## Speculative Traits

| Trait | Assumption basis | Confidence | Real-world validation needed |
|---|---|---|---|
|  |  | Low / Medium / High |  |

## Source Gaps

| Gap | Risk | Validation needed |
|---|---|---|
|  |  |  |

## Generation Prompt Used

- Prompt version:
- Model/tool used:
- Inputs included:
- Inputs excluded:

## Review

- Decision: Ready as hypothesis / Needs source repair / Needs privacy review / Blocked-insufficient
- Rationale:
- Forbidden uses confirmed:
- Human review status:
- Next real-world validation:
```

## Follow-Up Ticket Criteria

Create or recommend a follow-up only when generation identifies a concrete next action:

- repair missing source artifacts
- run privacy review for a specific data source
- turn a synthetic objection into interview questions
- update respondent targeting for a named profile
- compare synthetic persona output against real interviews
- reject or supersede a persona that is mostly unsupported

Do not create follow-ups for generic synthetic personas, unsupported persona enthusiasm, or broad market curiosity.

## Done Criteria

This workflow is complete when:

- source and privacy gate precedes generation
- evidence-backed and speculative traits are separated
- source gaps are visible
- generation prompt forbids invented evidence
- schema completion checks exist
- review decisions include privacy and insufficiency blockers
- synthetic personas remain hypothesis-only artifacts

## Relationship To Existing Artifacts

- Use `schemas/SyntheticPersona.schema.json` as the canonical output contract.
- Use `validation/synthetic-persona-schema.md` for field semantics and forbidden uses.
- Use `validation/persona-ranking-rubric.md` to prevent synthetic personas from outranking real evidence.
- Use `validation/respondent-targeting-and-interview-planner.md` to convert synthetic blind spots into discovery questions.
- Use `validation/customer-data-retention-policy.md` before using any real customer-derived material.
