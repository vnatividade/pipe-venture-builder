# Idea Browser Input Mapping

Use this mapping after `growth/idea-browser-validation-workflow.md` captures an Idea Browser signal and before that signal influences idea ranking, validation planning, respondent targeting, channel hypotheses, or follow-up tickets.

Idea Browser is an input mapper, not a proof engine. Every signal must remain advisory and point to a required real-world test.

## Boundary

This mapping does not authorize:

- treating Idea Browser output as customer evidence
- raising critical validation scores from Idea Browser alone
- creating build, PRD, monetization, pricing, billing, launch, or paid acquisition tickets
- contacting customers or prospects
- scraping, automated outreach, or external communications
- changing roadmap priority without human review
- making customer-facing claims

If a signal has no source trace or confidence label, stop and mark it `NO-GO: unmapped signal`.

## Required Inputs

Before mapping a signal, link:

- origin Linear ticket
- Idea Browser source artifact or exported summary
- signal capture from `growth/idea-browser-validation-workflow.md`
- idea or venture
- current ranking artifact, if any
- `validation/validation-scorecard.md`
- `validation/persona-ranking-rubric.md`, when persona fit may change
- `validation/geography-ranking-rubric.md`, when geography fit may change
- `validation/respondent-targeting-and-interview-planner.md`, when discovery questions or respondent profiles may change

## Signal Mapping Table

Map every Idea Browser signal to one ranking or validation use. Do not let one weak signal sprawl across every artifact.

| Idea Browser signal type | Allowed ranking influence | Required real-world test | Artifact to update only after evidence |
|---|---|---|---|
| Similar idea pattern | Differentiation hypothesis, comparable workflow, possible crowdedness | Competitor/source review, customer interview on differentiation, or manual workflow comparison | Validation scorecard, PRD question, or research notes |
| Market cluster | Category naming, market map, research priority | Sourced market research or customer discovery confirming problem context | Research plan or validation plan |
| Persona hint | Candidate respondent profile or ICP question | Manual respondent targeting and customer interview evidence | ICP profile or persona ranking |
| Channel hint | Channel hypothesis or manual source idea | Approved manual channel test, qualified replies, or discovery calls | Distribution strategy or validation scorecard |
| Positioning language | Messaging hypothesis or language to test | Customer interview language, fake-door copy test after approval, or manual feedback | Customer language memory or positioning notes |
| Objection or risk hint | Risk prompt or interview question | Customer interview, expert review, or risk review artifact | Risk review, validation scorecard, or respondent planner |
| Traction proxy | Research priority or false-positive warning | Source verification, customer behavior, retention/adoption evidence, or manual validation | Research notes or validation scorecard as weak signal only |
| Contradiction signal | Confidence decrease or contradiction review | Source review, customer interview, or validation experiment targeting the contradiction | Validation scorecard or decision record |

## Mapping Template

```md
# Idea Browser Input Mapping Review

## Metadata

- Idea or venture:
- Origin ticket:
- Reviewer:
- Date:
- Idea Browser artifact:
- Human review required before priority change: yes

## Signals To Map

| Signal | Signal type | Source trace | Confidence | Ranking factor affected | Advisory influence | Required real-world test | Target artifact after evidence |
|---|---|---|---|---|---|---|---|
|  | Similar idea / market cluster / persona / channel / positioning / objection / traction proxy / contradiction |  | Low / Medium / High | Persona / geography / channel / pain / status quo / differentiation / risk / timing | Strengthen hypothesis / weaken hypothesis / create question / no impact |  |  |

## Insufficiency Rules Applied

- Source trace present:
- Confidence label present:
- Customer evidence present:
- Scorecard cap applied:
- Real-world test required:
- Human review required:

## Validation Planning Output

- Discovery question to add:
- Persona to test:
- Geography to test:
- Channel to test:
- Objection to test:
- Source/research claim to verify:
- Scorecard category affected:
- Follow-up ticket needed:

## Decision

- Decision: Advisory input / Research follow-up / Discovery follow-up / Ranking adjustment proposal / Blocked-insufficient
- Rationale:
- Blocked actions:
- Next real-world test:
```

## Influence Rules

Idea Browser may influence ranking only as follows:

- `strengthen hypothesis`: only when it supports an existing assumption and still points to a real-world test
- `weaken hypothesis`: when it contradicts unsupported assumptions or flags crowding, channel weakness, trust risk, or poor fit
- `create question`: when it is relevant but insufficient
- `no impact`: when it is weak, uncited, stale, irrelevant, vanity-based, or lacks confidence

It must not:

- auto-promote an idea
- auto-kill an idea
- satisfy critical validation scorecard categories
- replace interviews, observed behavior, manual tests, sourced research, or expert review
- create downstream execution tickets without stronger evidence and approval

## Scorecard Cap

Idea Browser influence is capped at score `1` in `validation/validation-scorecard.md` unless stronger external evidence exists.

Critical categories remain blocked from Idea Browser-only satisfaction:

- Pain intensity
- ICP specificity
- Observed evidence
- Willingness to engage
- Willingness to pay
- C.O.N.T.R.O.L.E. alignment

## Follow-Up Ticket Criteria

Create or recommend a follow-up only when the mapping identifies a concrete real-world test:

- interview a named respondent profile
- research a named market, competitor, channel, claim, or source
- run an approved manual channel or fake-door experiment
- update a validation plan with specific questions
- perform a human-reviewed ranking comparison

Do not create follow-ups for generic idea inspiration, vague trend clusters, vanity traction, unsupported AI-generated enthusiasm, or source-free signals.

## Done Criteria

This mapping is complete when:

- every Idea Browser signal has source trace and confidence label
- every advisory influence is linked to a required real-world test
- insufficiency rules are explicit
- scorecard influence is capped
- customer evidence is not implied
- human review is required before prioritization changes

## Relationship To Existing Artifacts

- Use `growth/idea-browser-validation-workflow.md` first to capture, classify, and evaluate sufficiency.
- Use `validation/persona-ranking-rubric.md` when the signal affects persona priority.
- Use `validation/geography-ranking-rubric.md` when the signal affects country, region, city, or local-market priority.
- Use `validation/respondent-targeting-and-interview-planner.md` when the signal creates a discovery target or question.
- Use `validation/validation-scorecard.md` only after evidence strength and score caps are clear.
