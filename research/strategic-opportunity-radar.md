# Strategic Opportunity Radar

This design defines a decision-support radar for surfacing high-potential venture opportunities from signals, rankings, personas, geographies, evidence, and C.O.N.T.R.O.L.E.

The radar recommends review. It does not approve execution, create products, create tickets, change roadmap priority, or start outreach.

## Purpose

The strategic opportunity radar helps future agents and the founder see:

- which ideas deserve human review now
- which ideas are watchlist candidates
- which opportunities are blocked by missing evidence or risk
- which signals changed since the last review
- which personas or geographies create sharper opportunity windows
- which KDR/DAR decisions constrain action

It turns accumulated evidence into strategic optionality without letting noisy signals or agent enthusiasm create execution churn.

## Boundary

This radar does not authorize:

- automatic product creation
- automatic Linear ticket generation
- automatic ranking changes
- PRD, MVP, build, launch, pricing, billing, outreach, or paid acquisition decisions
- customer contact or external communication
- live scraping, monitoring, connector sync, scheduled agents, or external tools
- treating market signals, synthetic personas, or AI summaries as validation evidence
- bypassing C.O.N.T.R.O.L.E., validation scorecard, risk review, or human approval

Human review is required before any opportunity changes prioritization, validation plan, PRD/MVP scope, backlog, growth, monetization, or implementation sequencing.

## Required Inputs

Use the radar only when inputs have source traceability and confidence labels.

| Input | Source artifact | Required fields |
|---|---|---|
| Idea memory | `knowledge/venture-intelligence-memory-layer.md` | Idea ID, status, source artifacts, C.O.N.T.R.O.L.E. verdict. |
| Market signals | `research/market-signal-ingestion-template.md` | Signal ID, source, date, persona, geography, confidence, limitation. |
| Ranking score | `research/idea-ranking-engine-design.md` | Score, band, confidence, evidence links, risk if wrong. |
| Persona ranking | `validation/persona-ranking-rubric.md` | Persona fit, evidence type, confidence, source. |
| Geography ranking | `validation/geography-ranking-rubric.md` | Geography fit, source date, confidence, review flags. |
| Validation evidence | `validation/validation-scorecard.md` | Score, evidence strength, contradictions, missing proof. |
| Decisions | `knowledge/kdr-dar-template.md` | Status, rationale, constraints, revisit trigger. |

If source traceability or confidence is missing, the opportunity must be marked `Blocked - missing traceability` or `Watchlist - needs evidence repair`.

## Radar Bands

| Band | Meaning | Allowed next action |
|---|---|---|
| Review now | Evidence or signal change may justify human review. | Human review of source artifacts and next validation action. |
| Validate next | Opportunity is promising but needs customer/research evidence. | Create or run approved validation planning only after review. |
| Watchlist | Interesting but weak, stale, or early. | Revisit on trigger; do not execute now. |
| Blocked | Missing traceability, unresolved P0/P1 risk, sensitive claim, Kill/Pivot current framing, or privacy blocker. | Resolve blocker before any review for execution. |
| Reject or archive | No longer relevant, contradicted, superseded, or outside founder focus. | Record rationale and revisit only on explicit trigger. |

No band approves build work.

## Radar Scoring Inputs

This is not a new ranking engine. It is a display layer over existing evidence and ranking.

| Dimension | Source | Radar use |
|---|---|---|
| C.O.N.T.R.O.L.E. verdict | Product evaluation | Blocks Kill/Pivot current framing; flags Attack/Refine for review. |
| Evidence strength | Evidence scoring and scorecard | Determines confidence and whether review can act. |
| Signal momentum | Market signal ingestion | Identifies changed market, channel, geography, or substitute context. |
| Persona sharpness | Persona rubric | Shows whether a first respondent/user/buyer is specific. |
| Geography fit | Geography rubric | Shows local feasibility, regulation, payment, channel, and founder fit. |
| Ranking band | Idea ranking engine | Shows relative prioritization candidate, validation candidate, watchlist, or blocked. |
| Decision constraints | KDR/DAR | Prevents repeating rejected or superseded assumptions. |
| Risk if wrong | Risk matrix or ranking notes | Blocks high-risk opportunities from accidental execution. |

## Radar Entry Template

```md
# Opportunity Radar Entry - <ID>

## Metadata

- Radar entry ID:
- Idea ID:
- Origin ticket:
- Owner:
- Review date:
- Radar band: Review now / Validate next / Watchlist / Blocked / Reject or archive
- Human review required before execution: yes

## Opportunity Summary

- Opportunity:
- Problem:
- Persona:
- Geography:
- Current thesis:
- What changed:

## Source Traceability

| Source | Type | Date or access date | Confidence | Limitation |
|---|---|---|---|---|
|  | idea / signal / ranking / persona / geography / validation / KDR-DAR / research |  | Low / Medium / High |  |

## Evidence And Score Snapshot

| Area | Current state | Confidence | Source | Risk if wrong |
|---|---|---|---|---|
| C.O.N.T.R.O.L.E. | Attack / Refine / Pivot / Kill / Unknown | Low / Medium / High |  |  |
| Evidence strength | Weak / Medium / Strong / Unknown | Low / Medium / High |  |  |
| Ranking band | Priority candidate / Validation candidate / Watchlist / Blocked | Low / Medium / High |  |  |
| Persona fit | Weak / Medium / Strong / Unknown | Low / Medium / High |  |  |
| Geography fit | Weak / Medium / Strong / Unknown | Low / Medium / High |  |  |
| Signal momentum | Weak / Medium / Strong / Unknown | Low / Medium / High |  |  |
| Decision constraints | None / Active / Superseded / Conflict | Low / Medium / High |  |  |

## Radar Rationale

- Why this is on the radar:
- Why it is not execution-ready:
- Strongest supporting evidence:
- Strongest contradiction:
- Biggest missing evidence:
- Risk if pursued too early:

## Recommended Review Action

Choose one:

- Review source artifacts
- Run validation planning
- Repair evidence traceability
- Run risk review
- Update ranking after human review
- Archive or reject
- Keep on watchlist

## Decision Handoff

- Decision owner:
- Human review status:
- Allowed next artifact:
- Not allowed without approval:
- Revisit trigger:
```

## Radar Review Workflow

### 1. Build Candidate List

Include only opportunities with at least one traceable source artifact.

Candidate sources:

- ranking batch changed
- market signal routed to ranking or research synthesis
- persona/geography confidence changed
- validation score changed
- KDR/DAR revisit trigger activated
- synthetic-vs-real comparison found a material miss or contradiction

### 2. Apply Hard Blocks

Mark as `Blocked` when:

- source traceability is missing
- confidence labels are missing
- C.O.N.T.R.O.L.E. is Kill or current framing is Pivot
- unresolved P0/P1 risk exists
- privacy/security/legal/compliance blocker exists
- using the opportunity would require customer outreach, paid acquisition, billing, production deployment, or sensitive claims without approval
- the opportunity is based only on synthetic output

### 3. Assign Radar Band

Assign a band using existing evidence, not agent preference.

Rules:

- `Review now` requires traceable evidence, no hard block, and a concrete reason for human review.
- `Validate next` requires a specific validation question and enough source basis to justify discovery planning.
- `Watchlist` is for weak or early signals with explicit revisit trigger.
- `Blocked` requires blocker and unblock condition.
- `Reject or archive` requires rationale and source or decision basis.

### 4. Prepare Human Review Handoff

The radar handoff must state:

- why the opportunity surfaced
- what changed
- what evidence supports it
- what contradicts it
- what is missing
- what action is allowed next
- what action is forbidden without approval

### 5. Record Outcome

After human review, record outcome in the relevant artifact:

- `knowledge/venture-intelligence-memory-layer.md` record
- `research/idea-ranking-engine-design.md` ranking batch
- `validation/validation-scorecard.md`
- KDR/DAR when a decision changes
- Linear ticket only when explicitly approved

## Review Cadence

Use a lightweight cadence:

| Cadence | Use when | Output |
|---|---|---|
| Per signal | A meaningful signal changes a current assumption. | Radar entry or source-log-only decision. |
| Per ranking batch | Multiple ideas are compared. | Radar snapshot with bands. |
| Per validation batch | Interviews or evidence change confidence. | Radar update and scorecard handoff. |
| Monthly or phase gate | No urgent changes, but accumulated context may be stale. | Watchlist cleanup and revisit trigger review. |

Do not run a scheduled radar job until a separate approved automation ticket defines permissions, data sources, review queue, and stop controls.

## Output Snapshot Template

```md
# Strategic Opportunity Radar Snapshot

## Metadata

- Origin ticket:
- Owner:
- Review date:
- Source artifacts:
- Human review required before execution: yes

## Radar Entries

| Entry | Idea | Band | What changed | Evidence confidence | Biggest risk | Recommended review action |
|---|---|---|---|---|---|---|
|  |  | Review now / Validate next / Watchlist / Blocked / Reject or archive |  | Low / Medium / High |  |  |

## Blocked Entries

| Entry | Blocker | Unblock condition | Owner |
|---|---|---|---|
|  |  |  |  |

## Review Decisions

| Entry | Human decision | Next artifact | Follow-up ticket approved? |
|---|---|---|---|
|  |  |  | yes/no |

## Notes

- No automatic product creation:
- No automatic ticket generation:
- No build/outreach approval:
- Revisit trigger:
```

## Done Criteria

This radar design is complete when:

- inputs require source traceability and confidence labels
- bands recommend review, validation, watchlist, block, or archive
- each opportunity links to evidence
- hard blocks prevent execution from weak or unsafe inputs
- review cadence is explicit
- decision handoff states allowed and forbidden next actions
- automatic product creation and ticket generation remain out of scope
