# Persona Ranking Rubric

Use this rubric when comparing how strongly one idea fits different target personas before prioritizing validation, PRD, MVP, growth, or build work.

The same idea can be promising for one persona and weak for another. Ranking must stay evidence-bound: real interviews, observed behavior, status quo workarounds, commitments, and sourced market signals outrank synthetic personas and internal opinion.

## Boundary

This rubric does not authorize:

- treating fictional or synthetic personas as customer proof
- raising validation scores without evidence type and confidence
- contacting customers, leads, or prospects
- scraping or sourcing lead lists
- automatic prioritization changes
- creating PRD, build, launch, monetization, or outreach tickets from persona fit alone
- storing identifiable customer data without approval

Human review is required before using this rubric to change prioritization.

## Required Inputs

Before ranking personas, link:

- origin Linear ticket
- idea or venture name
- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `validation/icp-profile.md`
- `validation/respondent-targeting-and-interview-planner.md`, when respondent profiles are still hypotheses
- `validation/customer-interview-template.md`, when real interviews exist
- `validation/raw-interview-evidence-intake-and-synthesis.md`, when raw conversations have been processed
- `validation/validation-scorecard.md`, when validation scores may change

If the persona is fictional, synthetic, or internally assumed, label it clearly and cap evidence confidence until real source artifacts exist.

## Evidence Strength

Use the strongest applicable evidence type for each score.

| Evidence type | Strength | Use as |
|---|---|---|
| Real customer interview with anonymized source artifact | Strong | Primary evidence |
| Observed behavior, current workaround, spend, pilot request, or commitment | Strong | Primary evidence |
| Exact customer language from approved notes | Strong | Persona language and pain evidence |
| Sourced public research or market signal | Medium | Context or hypothesis support |
| Founder/operator experience with clear source note | Medium | Assumption with context |
| Synthetic persona, AI critique, or internal brainstorm | Weak | Hypothesis only |
| Unsupported persona narrative | Invalid | Do not score as evidence |

Synthetic or AI-generated personas may help generate questions, objections, and blind spots. They must not count as interviews, willingness to pay, market proof, or validation evidence.

## Scoring Scale

Score each category from 0 to 3.

- 0: no evidence or contradicted by evidence
- 1: weak hypothesis or internal/synthetic signal
- 2: plausible external signal or limited customer evidence
- 3: strong evidence from real customer behavior, interviews, workarounds, commitments, or repeated patterns

Every score must include evidence type, confidence, and source link.

## Persona Ranking Categories

| Category | Question | Score | Evidence type | Confidence | Source |
|---|---|---:|---|---|---|
| Persona fit | Is this persona clearly inside the first ICP and not an adjacent/general audience? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Pain intensity | Does this persona feel the pain as urgent, costly, frequent, risky, or emotionally salient? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Status quo clarity | Can this persona describe current workarounds, substitutes, manual steps, or spend? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Workflow ownership | Does this persona own or directly operate the workflow where the pain appears? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Buying influence | Can this persona influence budget, approval, adoption, or championing? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Willingness to engage | Is there evidence this persona will spend time, share context, join a pilot, or introduce others? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Willingness to pay | Is there evidence of budget, existing spend, paid substitute, paid pilot interest, or economic buyer path? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Channel access | Can the founder reach this persona through a credible manual channel? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Customer language | Do we have exact or high-fidelity language from this persona about the pain? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |
| Objection clarity | Are adoption, trust, privacy, workflow, procurement, or timing objections known? |  | Strong / Medium / Weak / Invalid | Low / Medium / High |  |

## Ranking Matrix

Use this matrix to compare personas for one idea.

```md
# Persona Ranking Review

## Metadata

- Idea or venture:
- Origin ticket:
- Reviewer:
- Date:
- Human review required before prioritization change: yes

## Source Artifacts

- Founder focus:
- C.O.N.T.R.O.L.E.:
- ICP profile:
- Respondent targeting plan:
- Interview evidence:
- Raw evidence synthesis:
- Validation scorecard:

## Persona Scores

| Persona | Persona source label | Total score | Lowest category | Strongest evidence | Weakest evidence | Confidence | Priority proposal |
|---|---|---:|---|---|---|---|---|
|  | Interview-backed / research-backed / founder-assumed / synthetic / unsupported |  |  |  |  | Low / Medium / High | P1 / P2 / P3 / Do not pursue |

## Category Detail

| Persona | Category | Score | Evidence type | Source | Confidence | Notes |
|---|---|---:|---|---|---|---|
|  | Persona fit / pain / status quo / workflow / buying / engage / pay / channel / language / objection |  | Strong / Medium / Weak / Invalid |  | Low / Medium / High |  |

## Ranking Interpretation

- Best persona to validate next:
- Persona to exclude or deprioritize:
- Strongest evidence:
- Weakest evidence:
- Contradictions:
- Customer discovery still needed:
- Scorecard impact:
- C.O.N.T.R.O.L.E. impact:
- Priority change proposal:
- Human approval status:
```

## Interpretation Rules

Use the total score only after checking the evidence mix.

| Result | Use when | Allowed next action |
|---|---|---|
| Prioritize for discovery | High pain/workflow evidence and reachable manual channel, but validation still incomplete. | Update respondent targeting plan or interview questions. |
| Keep as secondary persona | Some fit, but weak buying influence, channel access, or evidence. | Park or test after primary persona. |
| Needs research | Interesting persona, but evidence is sourced research or weak signal only. | Create research question or source review. |
| Exclude for now | Persona is too broad, fictional, inaccessible, low-pain, or outside ICP. | Document exclusion criteria. |
| Blocked | Persona has no source label or would require unsafe customer data/outreach. | Stop until source or approval exists. |

Do not let a high synthetic score outrank a lower but interview-backed persona. Real evidence wins.

## Follow-Up Ticket Criteria

Create or recommend a follow-up ticket only when the ranking produces a concrete next action:

- update ICP profile with evidence-backed inclusion or exclusion criteria
- create manual respondent targeting for a named persona
- design interview questions for a specific objection or commitment gap
- research a specific persona/channel/source claim
- update the validation scorecard after evidence review
- document a durable decision if a persona is accepted or excluded with strong rationale

Do not create follow-ups for unsupported persona ideas, generic market curiosity, or synthetic-only enthusiasm.

## Done Criteria

This rubric is complete when:

- each persona score requires evidence type, confidence, and source
- real interviews and observed behavior outrank synthetic or internal assumptions
- persona fit, pain, willingness to pay, language, channels, and objections are represented
- fictional personas without source labels are blocked
- prioritization changes require human review
- follow-up criteria are concrete and validation-oriented

## Relationship To Existing Artifacts

- Use `validation/icp-profile.md` to store the current ICP hypothesis and exclusion criteria.
- Use `validation/respondent-targeting-and-interview-planner.md` to plan which respondent profiles the founder should seek manually.
- Use `validation/customer-interview-template.md` and `validation/raw-interview-evidence-intake-and-synthesis.md` when real discovery evidence exists.
- Use `validation/validation-scorecard.md` before changing validation confidence.
- Use `growth/builderpulse-idea-ranking-contrast-workflow.md` when BuilderPulse signals affect persona ranking as external advisory signals.
