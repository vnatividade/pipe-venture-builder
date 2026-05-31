# Respondent Targeting And Interview Planner

Use this planner before manual customer discovery when the founder needs help identifying which respondent profiles to seek and which questions to ask.

This artifact supports targeting and question design only. It does not authorize outreach, external communication, lead sourcing, scraping, automated messaging, AI calls, or storage of identifiable customer data.

## Purpose

The Pipe should improve discovery quality before the first conversation happens.

This planner helps agents and the founder:

- turn an idea into respondent hypotheses
- define who is worth interviewing first
- name who should be excluded
- suggest manual places the founder may look
- prepare questions tied to validation risk
- preserve privacy, approval gates, and evidence quality

## When To Use

Use this planner after:

- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `validation/venture-validation-framework.md`, when upstream lenses are useful
- `validation/validation-scorecard.md`, when validation categories are already known

Use it before:

- `validation/customer-interview-template.md`
- customer discovery involving real people
- manual validation tests with external participants
- PMF, PRD, build, growth, or monetization decisions

Do not use it to:

- generate real lead lists
- scrape platforms, directories, communities, or social networks
- contact, message, call, invite, or schedule with anyone
- run Manus AI, ElevenLabs, or any outbound automation
- treat synthetic personas as customer evidence
- store identifiable prospect or customer data in the repository

## Approval And Privacy Boundary

Before any real external person is contacted, apply:

- `execution/approval-gates.md`
- `validation/pre-user-security-privacy-readiness-gate.md`
- `validation/customer-data-retention-policy.md`

Record the gate decision in the relevant Linear ticket or validation artifact.

If the work is only this blank planning artifact, use:

```md
Gate decision: NOT APPLICABLE
Reason: internal-only respondent targeting and question planning; no external contact, customer data, outreach, automation, or user exposure.
```

If the next action involves real people, outreach, private notes, recordings, transcripts, direct quotes, customer data, or sensitive context, stop until the required approval is recorded.

## Required Inputs

| Input | Source | Why it matters |
|---|---|---|
| Idea or venture name | Founder focus | Keeps discovery tied to one wedge. |
| C.O.N.T.R.O.L.E. verdict | C.O.N.T.R.O.L.E. evaluation | Prevents interviewing around a strategically weak idea without approval. |
| PMF triad | Venture validation framework | Clarifies what to sell, to whom, and how to reach them. |
| MAYA adoption risk | Venture validation framework | Shapes trust, familiarity, and control questions. |
| Primary innovation flavor | Venture validation framework | Shapes friction and current-workflow questions. |
| Scorecard weak spots | Validation scorecard | Focuses questions on missing evidence. |
| Privacy constraints | Customer data retention policy | Avoids collecting or storing the wrong data. |

## Respondent Hypothesis Template

Create one table per likely segment. Keep profiles at the role, workflow, and context level. Do not list real names, emails, phone numbers, social handles, or company identifiers unless a separate approval explicitly allows it.

| Field | Notes |
|---|---|
| Persona hypothesis |  |
| Role or job-to-be-done |  |
| Buyer / user / approver / influencer |  |
| Segment context |  |
| Trigger event |  |
| Current workaround |  |
| Pain intensity hypothesis | Low / Medium / High |
| Reachability hypothesis | Low / Medium / High |
| Willingness-to-engage hypothesis | Low / Medium / High |
| Willingness-to-pay hypothesis | Low / Medium / High |
| Trust, privacy, or control concern |  |
| Why this respondent now |  |
| Exclusion criteria |  |
| Evidence expected from this profile |  |

## Respondent Priority Matrix

Use this matrix to decide which respondent profiles the founder should manually seek first.

| Profile | Pain proximity | Workflow ownership | Budget influence | Access feasibility | Evidence value | Privacy risk | Bad-fit risk | Priority |
|---|---|---|---|---|---|---|---|---|
|  | Low / Medium / High | Low / Medium / High | Low / Medium / High | Low / Medium / High | Low / Medium / High | Low / Medium / High | Low / Medium / High | P1 / P2 / P3 |

Prefer profiles that have high pain proximity, direct workflow ownership, high evidence value, and low privacy risk. Do not over-prioritize budget influence if the respondent cannot describe the actual workflow.

## Manual Source Ideas

These are places the founder may manually inspect or use for warm paths after approval. They are not leads and do not authorize contact.

| Source path | Use when | Guardrail |
|---|---|---|
| Warm founder network | A trusted introduction is plausible. | Ask for approval before contact or introduction request. |
| Existing customers, partners, or advisors | The founder has a legitimate relationship. | Do not imply endorsement or validation without evidence. |
| Professional associations or local groups | The ICP has a known trade or community surface. | Do not scrape member lists or send bulk outreach. |
| Public communities and forums | The problem is discussed publicly. | Use for learning and question design; do not harvest personal data. |
| LinkedIn or public profile search | Role and trigger-event language need refinement. | Do not store profile data or automate search/contact. |
| Events, meetups, webinars, or newsletters | The ICP gathers around a topic. | Treat as channel hypothesis until validated. |
| Founder-led content replies | People opt into discussion around the problem. | Keep consent, transparency, and retention rules explicit. |

## Interview Question Planner

Use the questions below to build a focused `customer-interview-template.md` for each respondent profile. Prefer behavior, examples, workarounds, trade-offs, and commitments over opinions.

### Fit And Context

- What role does this person play in the workflow?
- When does the problem appear?
- What trigger event makes the problem urgent?
- Who else is involved before a decision or workaround happens?
- Which part of the workflow is outside this respondent's view?

### Pain And Status Quo

- What is hard, slow, expensive, risky, or frustrating today?
- What do they already do to solve, avoid, delegate, or ignore the problem?
- What tools, spreadsheets, agencies, people, or manual steps are involved?
- What breaks when the workaround fails?
- How often does the problem happen and what happens if it is not solved?

### C.O.N.T.R.O.L.E.

- Which evidence would strengthen or weaken the current C.O.N.T.R.O.L.E. verdict?
- Does this problem align with the founder's strategic focus or pull the idea into distraction?
- What operational constraint would make this opportunity harder than it looks?
- What leverage, network, or edge would make this wedge more defensible?

### MAYA Adoption Risk

- What part of the proposed solution would feel familiar?
- What new behavior would require trust?
- What would need to remain manual, inspectable, or reversible at first?
- What would make the idea feel too advanced, risky, or annoying?
- Which capability should be delayed until trust exists?

### PMF Triad

- What exactly would this person expect to buy or use first?
- Is this respondent part of the first ICP, or adjacent to it?
- How would someone like this realistically discover or trust the offer?
- What would prove the proposed first channel is plausible?
- Who is explicitly excluded from the first market hypothesis?

### Willingness To Engage Or Pay

- Would they review a sample, share anonymized context, or join a pilot?
- Have they already spent time, money, or political capital on the problem?
- Who owns budget or approval?
- What would make this worth paying for?
- What commitment would be meaningful at this stage?

### Objections, Risk, And Trust

- What would stop them from trying a solution?
- What privacy, security, legal, procurement, or workflow risk matters?
- What data would they refuse to share?
- What claim would make them distrust the product?
- What human review or control would be required?

### Contradiction Seeking

- What evidence would make the pain look weaker?
- What would prove the current ICP is wrong or too broad?
- What would make willingness to pay unlikely even if the user likes the idea?
- What would make the channel inaccessible, low-trust, or too slow?
- Which founder assumption is most likely being protected by preference instead of evidence?

## Output Template

Copy this section into the relevant validation artifact or keep it as a planning note linked from the Linear ticket.

```md
## Respondent Targeting And Interview Plan

- Idea or venture:
- Origin ticket:
- Date:
- Owner:
- Gate decision:
- Approval record or blocker:
- External contact authorized: yes/no
- Customer data capture authorized: yes/no

## Source Artifacts

- Founder focus:
- C.O.N.T.R.O.L.E. evaluation:
- Venture validation framework:
- Validation scorecard:
- ICP profile:
- Data retention policy:

## PMF Triad

- What to sell:
- To whom:
- How to reach:

## Respondent Profiles To Seek

| Profile | Why this person | Evidence expected | Manual source ideas | Exclusion criteria | Priority |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Interview Question Set

### Core questions

- TBD

### Persona-specific questions

- TBD

### Contradiction questions

- TBD

### Commitment questions

- TBD

## Privacy And Data Boundary

- Notes allowed in repository:
- Notes that must stay private:
- Recording/transcript allowed: yes/no
- Direct identifiable quotes allowed: yes/no
- Retention or deletion expectation:

## Handoff

- Next approved action:
- Blocked actions:
- Next evidence needed:
- Artifact to update after interviews:
- Follow-up Linear ticket:
```

## GO / NO-GO Rules

| Decision | Use when | Allowed next action |
|---|---|---|
| GO | Profiles are specific, questions map to weak assumptions, approvals are clear, and no external action is implied by this artifact. | Prepare or run only the approved manual discovery step. |
| CONDITIONAL GO | One boundary needs clarification but can be resolved before contact. | Resolve approval, data, or scope blocker before contact. |
| BLOCKED | Outreach, automation, customer data, recordings, sensitive claims, or storage rules are unresolved. | Stop and update Linear with blocker. |
| NO-GO | The proposed discovery would be misleading, spammy, too broad, unsafe, or impossible to retain ethically. | Redesign the discovery plan. |

## Handoff To Existing Artifacts

After approved interviews or manual discovery:

- update `validation/customer-interview-template.md` per participant
- update `validation/icp-profile.md` with segment-level evidence
- update `validation/validation-scorecard.md` with evidence quality
- update `knowledge/customer-language-memory.md` only with anonymized, approved language
- update Linear with approvals, evidence captured, private storage status, deletion expectations, and follow-ups

Do not promote planning assumptions into evidence fields. Mark synthetic persona output, AI critique, and founder hypotheses as assumptions until real-world evidence exists.
