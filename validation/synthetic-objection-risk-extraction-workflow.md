# Synthetic Objection And Risk Extraction Workflow

Use this workflow after a synthetic persona simulation to turn objections into explicit risks, validation questions, and real-world tests.

Synthetic objections are not evidence. They are prompts for discovery, risk review, and better questions.

## Boundary

This workflow does not authorize:

- accepting simulated objections as true
- changing persona ranking, venture priority, validation score, PRD scope, MVP scope, pricing, launch, build, or outreach decisions without real validation and human review
- contacting customers, sourcing leads, scraping, outreach automation, or AI calls
- creating public claims, customer quotes, demand claims, willingness-to-pay claims, or product-market-fit claims
- storing sensitive, identifiable, private, regulated, confidential, or customer raw data
- creating KDR/DAR records unless a real decision changes

If the simulation output does not include source basis, confidence limits, and real-world tests, repair the simulation before extracting risks.

## Required Inputs

Before extraction, link:

- origin Linear ticket
- synthetic persona generation review
- synthetic persona simulation output
- `validation/synthetic-persona-simulation-prompt.md`
- `validation/synthetic-persona-generation-workflow.md`
- `validation/respondent-targeting-and-interview-planner.md`
- `execution/risk-reviewer-matrix-lite.md`, when a material risk needs severity classification
- `knowledge/kdr-dar-template.md`, only if a real decision changes later

## Extraction Flow

### 1. Simulation Eligibility Check

Confirm the input can be used.

| Check | Pass/Fail | Notes |
|---|---|---|
| Persona reviewed as hypothesis |  |  |
| Simulation includes synthetic-not-proof banner |  |  |
| Simulation includes objections |  |  |
| Simulation includes confidence limits |  |  |
| Simulation includes source basis |  |  |
| Simulation includes real-world tests |  |  |
| No sensitive or identifiable data is present |  |  |
| Output does not imply demand, WTP, PMF, or adoption proof |  |  |

If any critical check fails, stop and repair the upstream persona or simulation artifact.

### 2. Objection Taxonomy

Classify each objection into one primary type.

| Type | Meaning | Example validation target |
|---|---|---|
| Problem urgency | The problem may not be painful, frequent, costly, or urgent enough. | Ask about recent occurrence, consequence, workaround, and trigger. |
| Status quo strength | Existing tools, manual process, or behavior may be good enough. | Compare current workaround cost, failure, and switching threshold. |
| Trust and credibility | The claim, founder, product, or AI behavior may not be trusted. | Test trust requirement, proof needed, and red-flag claims. |
| Privacy, security, legal, or compliance | The idea may trigger sensitive data, permissions, or regulated workflow risk. | Run risk review and ask what data/control is unacceptable. |
| Buying and budget | User, buyer, approver, budget, or timing may be misread. | Identify buyer path, budget owner, approval sequence, and trigger event. |
| Channel and reachability | The persona may not be reachable through the assumed channel. | Test discovery route, permission, community fit, and warm path. |
| Adoption and workflow change | Required behavior change may be too high. | Test manual-first workflow, control requirements, and switching friction. |
| MVP scope | Proposed MVP may be too broad, too narrow, or missing the core risk. | Test smallest useful workflow and feature cut list. |
| Economic value | The benefit may not justify effort, payment, time, or risk. | Test cost of problem, current spend, and willingness to engage. |
| Evidence gap | The objection is mostly unsupported or too vague. | Repair source basis or ignore with reason. |

### 3. Extraction Table

Every synthetic objection must map to either a validation question/test or an ignored reason.

| Objection | Taxonomy type | Source basis | Confidence | Risk if true | Validation question or test | Ignore reason, if ignored | Owner | Artifact link |
|---|---|---|---|---|---|---|---|---|
|  |  | persona field / simulation section / source gap | Low / Medium / High |  |  | unsupported / duplicate / out of scope / already tested / not material |  |  |

Rules:

- Do not leave both validation and ignore reason blank.
- Use `Evidence gap` when the objection is too unsupported to become a question.
- Prefer interview questions for early discovery.
- Prefer risk review when the objection involves privacy, security, legal, compliance, billing, external communication, production, or customer data.
- Prefer MVP scope review only after real evidence supports the concern.
- Do not convert synthetic objections directly into build tickets.

### 4. Risk Classification

Classify only material risks. Use `execution/risk-reviewer-matrix-lite.md` when severity matters.

| Risk | Category | Severity | Trigger | Mitigation | Blocking? | Follow-up needed |
|---|---|---|---|---|---|---|
|  | Product / validation / privacy / security / legal / compliance / financial / operational / channel / adoption | P0 / P1 / P2 / P3 |  |  | yes/no | yes/no |

Guidance:

- P0/P1 risks must not be accepted from synthetic simulation alone.
- P0/P1 risks should block downstream build or outreach until mitigated, explicitly accepted, or converted into a scoped follow-up with human review.
- P2 risks may become follow-ups when concrete and outside current scope.
- P3 suggestions should not create noise unless they clarify future discovery.

### 5. Validation Mapping

Convert accepted extraction rows into specific real-world learning actions.

| Validation target | Best next artifact | Question or test | Evidence needed | Success signal | Failure signal |
|---|---|---|---|---|---|
|  | interview guide / respondent plan / scorecard / risk review / MVP scope review / KDR candidate |  |  |  |  |

Use:

- `validation/respondent-targeting-and-interview-planner.md` for interview questions
- `validation/customer-interview-template.md` for live discovery
- `validation/raw-interview-evidence-intake-and-synthesis.md` after real conversations
- `validation/validation-scorecard.md` only when evidence exists
- `execution/risk-reviewer-matrix-lite.md` for material risks
- `knowledge/kdr-dar-template.md` only after a real decision changes

### 6. KDR/DAR Link Rule

Synthetic objection extraction can reference a future KDR/DAR candidate, but it should not create one by itself.

Create or update a KDR/DAR only when real evidence or human decision changes:

- product strategy
- validation path
- MVP scope
- architecture
- risk posture
- growth, monetization, or governance

Record candidate decision pressure like this:

| Possible decision pressure | Current evidence | KDR/DAR action |
|---|---|---|
|  | synthetic only / interview-backed / research-backed / decision accepted | none / candidate later / update required |

## Output Template

```md
# Synthetic Objection And Risk Extraction

## Metadata

- Origin ticket:
- Reviewer:
- Date:
- Persona:
- Simulation artifact:
- Human review required before prioritization: yes

## Eligibility Check

| Check | Pass/Fail | Notes |
|---|---|---|
| Persona reviewed as hypothesis |  |  |
| Simulation includes objections |  |  |
| Simulation includes confidence limits |  |  |
| Simulation includes source basis |  |  |
| Simulation includes real-world tests |  |  |
| No proof claims |  |  |
| No sensitive data |  |  |

## Objection Extraction

| Objection | Type | Source basis | Confidence | Risk if true | Validation question or test | Ignore reason | Owner | Artifact link |
|---|---|---|---|---|---|---|---|---|
|  |  |  | Low / Medium / High |  |  |  |  |  |

## Material Risk Classification

| Risk | Category | Severity | Trigger | Mitigation | Blocking? | Follow-up needed |
|---|---|---|---|---|---|---|
|  |  | P0 / P1 / P2 / P3 |  |  | yes/no | yes/no |

## Validation Mapping

| Validation target | Best next artifact | Question or test | Evidence needed | Success signal | Failure signal |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## KDR/DAR Decision Pressure

| Possible decision pressure | Current evidence | KDR/DAR action |
|---|---|---|
|  | synthetic only / interview-backed / research-backed / decision accepted | none / candidate later / update required |

## Decision

- Ready for interview guide / Needs simulation repair / Needs risk review / Needs privacy review / Do not use
- Rationale:
- Follow-up needed:
```

## Follow-Up Ticket Criteria

Create or recommend a follow-up only when extraction identifies a concrete action:

- add specific interview questions to a named interview guide
- revise respondent targeting for a named persona or segment
- run risk review for a named material risk
- repair a missing source basis or simulation artifact
- compare extracted synthetic objections against real interview evidence
- update KDR/DAR after real evidence or human decision changes

Do not create follow-ups for generic objections, duplicate doubts, simulated demand, or unsupported speculation.

## Done Criteria

This workflow is complete when:

- every synthetic objection maps to a validation question/test or ignored reason
- objections are classified with a practical taxonomy
- material risks can be routed to the risk matrix
- KDR/DAR links are limited to real decision changes
- synthetic objections cannot change ranking without real validation
- outputs are usable for interview guides and validation planning

## Relationship To Existing Artifacts

- Use `validation/synthetic-persona-simulation-prompt.md` as the upstream simulation contract.
- Use `validation/respondent-targeting-and-interview-planner.md` to convert objections into interview plans.
- Use `validation/raw-interview-evidence-intake-and-synthesis.md` after real discovery.
- Use `execution/risk-reviewer-matrix-lite.md` for material risk severity.
- Use `knowledge/kdr-dar-template.md` only when a real decision changes.
