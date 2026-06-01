# Synthetic Persona Simulation Prompt

Use this prompt template to make a reviewed synthetic persona challenge an idea, offer, message, channel, or MVP plan before real-world discovery.

Synthetic persona simulation is a critique tool. It is not customer evidence, validation evidence, willingness-to-pay evidence, product-market fit evidence, or approval to build.

## Boundary

This prompt does not authorize:

- replacing interviews, observed behavior, market research, or validation scorecards
- making final prioritization, PRD, build, launch, pricing, billing, outreach, or paid acquisition decisions
- claiming demand, adoption, urgency, budget, or willingness to pay
- generating public claims or customer quotes
- using sensitive, identifiable, private, regulated, confidential, or customer raw data without approval
- using simulation output as proof that a persona exists in the market

If the synthetic persona was not reviewed as a hypothesis, stop and run `validation/synthetic-persona-generation-workflow.md` first.

## Required Inputs

Before simulation, link:

- origin Linear ticket
- reviewed synthetic persona record or generation review
- `schemas/SyntheticPersona.schema.json`
- `validation/synthetic-persona-schema.md`
- `validation/synthetic-persona-generation-workflow.md`
- idea, problem statement, offer, message, channel, or MVP artifact being critiqued
- explicit source gaps and assumptions from the persona
- desired simulation focus

Do not run a simulation from an unreviewed persona, missing source basis, or mostly unsupported persona.

## Simulation Focus Options

Choose one or more focus areas before running the prompt.

| Focus | Use when | Required output |
|---|---|---|
| Problem critique | Testing whether the problem is urgent enough. | Pain doubts, current workaround, switching trigger, missing evidence. |
| Offer critique | Testing whether the promise is credible and useful. | Value doubts, must-have proof, willingness-to-engage doubts, alternative options. |
| Message critique | Testing positioning, landing copy, or outbound framing. | Confusing claims, trust gaps, phrases to avoid, language to test. |
| Channel critique | Testing where and how the persona might be reached. | Channel skepticism, permission risk, trust path, discovery route. |
| MVP critique | Testing smallest useful workflow. | Feature cuts, adoption friction, success threshold, manual validation path. |
| Buying critique | Testing B2B buying or budget dynamics. | Buyer/user split, procurement friction, compliance blocker, timing risk. |

## Simulation Rules

The simulator must:

- speak from the persona's bounded context
- challenge founder assumptions directly
- separate likely objections from speculative objections
- label confidence for every critique
- cite the persona field or source basis behind each critique
- name what would need to be tested with real people
- surface contradictions and unknowns
- avoid invented quotes, budgets, commitments, integrations, metrics, or customer evidence
- avoid flattering the idea unless the source basis strongly supports it
- prefer hard questions over optimistic conclusions

The simulator must not:

- conclude that the idea is validated
- claim the persona would buy, use, respond, convert, or churn
- create a PRD or implementation task
- rank this persona above interview-backed evidence
- recommend outreach automation
- use sensitive or identifiable details
- generate exact customer language unless it is clearly marked as synthetic wording to test

## Prompt Template

```txt
You are simulating a reviewed synthetic persona for hypothesis pressure-testing only.

This is not customer evidence, validation evidence, willingness-to-pay proof, product-market fit evidence, or approval to build.

Your job is to challenge the founder's assumptions from the persona's bounded context.
Do not validate the idea by default.
Do not invent customer evidence, quotes, commitments, budget, usage metrics, integrations, procurement facts, or willingness to pay.
Every critique must include confidence, source basis, and the real-world test needed.

Synthetic persona:
<paste reviewed synthetic persona or generation review summary>

Persona source basis:
<paste evidence-backed traits, assumptions, source artifacts, source gaps, and review decision>

Artifact to critique:
<paste problem statement, offer, message, channel hypothesis, MVP scope, or buying hypothesis>

Simulation focus:
<problem critique / offer critique / message critique / channel critique / MVP critique / buying critique>

Output exactly this structure:

# Synthetic Persona Simulation

## Synthetic-Not-Proof Banner
Synthetic persona simulation for hypothesis pressure-testing only. Not customer evidence.

## Inputs Reviewed
- Origin ticket:
- Persona:
- Persona review decision:
- Artifact critiqued:
- Simulation focus:

## Core Reaction
- Likely first reaction:
- Why this reaction might happen:
- Confidence: Low / Medium / High
- Source basis:
- Real-world test needed:

## Strongest Objections
| Objection | Confidence | Source basis | Risk if true | Real-world test |
|---|---|---|---|---|

## Buying Or Adoption Friction
| Friction | Confidence | Source basis | Who or what blocks it | Real-world test |
|---|---|---|---|---|

## Message And Trust Risks
| Claim or message | What may feel unclear, unbelievable, risky, or irrelevant | Confidence | Test needed |
|---|---|---|---|

## Channel Response
| Channel | Likely reaction | Permission or trust risk | Better discovery route | Evidence needed |
|---|---|---|---|---|

## MVP Pressure Test
| MVP element | Keep / cut / test manually / unknown | Rationale | Real-world test |
|---|---|---|---|

## Contradictions And Unknowns
| Unknown or contradiction | Why it matters | What evidence would resolve it |
|---|---|---|

## Interview Questions To Ask Next
- Question 1:
- Question 2:
- Question 3:
- Question 4:
- Question 5:

## Confidence Limits
- What this simulation can help with:
- What this simulation cannot prove:
- Evidence that would upgrade confidence:
- Evidence that would downgrade confidence:

## Recommended Next Action
Choose one:
- Run targeted interviews
- Repair persona source basis
- Revise problem framing
- Revise message
- Narrow MVP hypothesis
- Investigate channel risk
- Do not use this simulation because source basis is insufficient

## Forbidden Uses Confirmed
- Not used as customer evidence: yes
- Not used as market proof: yes
- Not used as willingness-to-pay proof: yes
- Not used for automatic prioritization: yes
- Not used to create build/outreach tickets without human review: yes
```

## Review Checklist

Before using simulation output, verify:

| Requirement | Pass/Fail | Notes |
|---|---|---|
| Persona was reviewed as hypothesis before simulation |  |  |
| Synthetic-not-proof banner is included |  |  |
| Objections are explicit |  |  |
| Confidence limits are explicit |  |  |
| Every material critique names source basis |  |  |
| Every material critique names a real-world test |  |  |
| Output does not imply demand, WTP, PMF, or adoption proof |  |  |
| No sensitive or identifiable data is present |  |  |
| Recommended next action stays upstream of build unless human review approves otherwise |  |  |

## Output Storage Template

```md
# Synthetic Persona Simulation Review

## Metadata

- Origin ticket:
- Reviewer:
- Date:
- Persona source:
- Artifact critiqued:
- Simulation focus:
- Human review required before prioritization: yes

## Review Checklist

| Requirement | Pass/Fail | Notes |
|---|---|---|
| Persona reviewed as hypothesis |  |  |
| Objections included |  |  |
| Confidence limits included |  |  |
| Real-world tests included |  |  |
| No proof claims |  |  |
| No sensitive data |  |  |

## Simulation Summary

- Strongest objection:
- Highest-risk assumption:
- Biggest source gap:
- Most important real-world test:
- Recommended next action:

## Decision

- Ready for interview question design / Needs persona source repair / Needs privacy review / Do not use
- Rationale:
- Follow-up needed:
```

## Follow-Up Ticket Criteria

Create or recommend a follow-up only when simulation identifies a concrete next action:

- convert objections into interview questions for a named persona
- revise the problem or message artifact being critiqued
- repair missing persona source basis
- investigate a specific channel or buying blocker
- compare simulation output with real interview evidence after discovery
- update MVP scope only after human review and stronger evidence

Do not create follow-ups for broad curiosity, speculative enthusiasm, or simulated demand.

## Done Criteria

This prompt template is complete when:

- it critiques problem, offer, message, channel, buying friction, and MVP assumptions
- it includes adversarial questions and objections
- it requires confidence limits and source basis
- it requires real-world tests for material claims
- it blocks use as proof of demand
- it keeps simulation upstream of build, outreach, monetization, and final prioritization

## Relationship To Existing Artifacts

- Use `validation/synthetic-persona-generation-workflow.md` before simulation.
- Use `validation/synthetic-persona-schema.md` to confirm synthetic-not-proof and forbidden-use fields.
- Use `validation/respondent-targeting-and-interview-planner.md` to turn simulation blind spots into real discovery questions.
- Use `validation/persona-ranking-rubric.md` before comparing synthetic critique to real persona evidence.
- Use `validation/market-validation-before-code-gate.md` before any build or PRD decision.
