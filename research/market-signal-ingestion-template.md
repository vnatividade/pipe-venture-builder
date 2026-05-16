# Market Signal Ingestion Template

Use this template to turn external market signals into structured opportunity evidence without letting noise drive execution.

Use it with `research/source-quality-and-citation-rules.md`, `research/market-research-workflow.md`, `research/research-synthesis-template.md`, `research/idea-ranking-engine-design.md`, `.codex/agents/research-validation-specialization.md`, and `execution/approval-gates.md`.

## Boundary

This template does not implement live scraping, monitoring, automatic ticket creation, BuilderPulse, connector use, paid research tools, customer outreach, or roadmap automation.

Signals are discovery inputs. They do not prove demand, willingness to pay, customer urgency, market validation, or implementation priority.

Human review is required before a signal changes roadmap, ranking, PRD/MVP scope, backlog priority, growth, monetization, public claims, or implementation tickets.

## Signal Types

| Signal type | Examples | Main use | Cannot prove |
|---|---|---|---|
| Substitute signal | New competitor, pricing page, feature launch, agency offer, template, manual workaround. | Substitute map, competition density, buyer alternatives. | Customer demand for this wedge. |
| Buyer-language signal | Forum complaint, review, search query pattern, public objection, procurement language. | Customer discovery questions and messaging hypotheses. | Representativeness or willingness to pay. |
| Channel signal | Community activity, search intent, newsletter/topic traction, partnership surface. | Channel reachability and distribution context. | Repeatable acquisition. |
| Geography signal | Country/city regulation, local substitute, payment behavior, language pattern. | Geography feasibility and ranking context. | Expansion approval. |
| Market maturity signal | Category creation, vendor density, consolidation, saturation, workflow normalization. | Market maturity and timing interpretation. | Product opportunity by itself. |
| Regulatory or trust signal | Compliance requirement, procurement barrier, privacy concern, safety expectation. | Risk review and trust burden assessment. | Legal/compliance conclusion. |
| Synthetic signal | AI-generated market idea, generated persona, generated objection, summary of possible sources. | Hypothesis generation only. | Evidence until underlying sources are inspected. |

## Required Signal Fields

Every ingested signal must include:

- signal ID
- origin Linear ticket or source artifact
- signal type
- signal source URL or repository path
- source owner or publisher
- source type
- publication, update, or access date
- date checked
- geography
- persona or ICP
- problem or workflow
- market maturity label
- channel fit
- source confidence: Low / Medium / High
- risk if wrong: Low / Medium / High
- limitation
- routing decision: Ranking / Research synthesis / Source log only / Rejected / Blocked

If the source, date, geography, or persona is unknown, mark it as `Unknown` and reduce confidence.

## Market Maturity Labels

Use the same maturity language as `research/market-research-workflow.md`.

| Label | Signal interpretation |
|---|---|
| Emerging | Fragmented language, new workflows, unclear budgets, early category formation. |
| Growing | More tools, content, communities, budget language, or workflow standardization. |
| Mature | Clear categories, review sites, incumbents, procurement expectations, and switching costs. |
| Declining or saturated | Price compression, vendor fatigue, weak differentiation, or reduced urgency. |
| Unknown | Signal lacks enough context to classify maturity. |

## Channel Fit Labels

| Label | Meaning |
|---|---|
| Strong | Signal points to an identifiable, founder-accessible, non-paid first channel. |
| Moderate | Channel exists but access rules, trust, or conversion path are uncertain. |
| Weak | Signal is noisy, paid-only, broad, or hard to reach manually. |
| Blocked | Channel use would require approval, outreach, paid acquisition, scraping, or sensitive claims. |
| Unknown | Channel implication is not clear from the signal. |

## Ingestion Workflow

### 1. Capture The Signal

Record only the smallest useful signal. Do not ingest broad link dumps.

Required capture:

- what happened or was observed
- where it came from
- when it was published, updated, or accessed
- which ICP, geography, workflow, channel, or market maturity question it may affect
- what the signal does not prove

### 2. Review Source Quality

Apply `research/source-quality-and-citation-rules.md`.

Reject or block a signal when:

- the source is uninspectable
- the source has no usable source trail
- the signal is only an AI summary without checked underlying sources
- the signal requires paid/private/credentialed/confidential access without approval
- using the signal would create sensitive or unsupported claims

### 3. Tag The Signal

Tag each signal with:

- persona or ICP
- geography
- problem or workflow
- signal type
- source type
- market maturity
- channel fit
- confidence
- risk if wrong
- affected C.O.N.T.R.O.L.E. dimension: C / O / L / other

### 4. Route The Signal

| Routing decision | Use when | Next owner |
|---|---|---|
| Ranking | Signal affects idea ranking dimensions and has source traceability. | `venture_intelligence_curator` or `market_intelligence_agent` |
| Research synthesis | Signal changes an assumption, confidence, contradiction, or next test. | `research_orchestrator` |
| Source log only | Signal is useful context but not decision-impacting. | `market_intelligence_agent` |
| Rejected | Signal is weak, duplicate, stale, unsupported, or irrelevant. | No action beyond logging reason when useful. |
| Blocked | Signal needs approval, risk review, source access, or sensitive-claim review. | `risk_reviewer` or human reviewer |

No signal may create implementation tickets automatically.

### 5. Decide Whether It Changes Anything

Before routing into ranking or synthesis, answer:

- Does this change a known assumption?
- Does this affect persona, geography, market maturity, channel fit, or ranking confidence?
- Does this introduce a contradiction?
- Does this require customer discovery?
- Would using this signal change roadmap or backlog priority?
- Is human review required before use?

If the answer is no, keep the signal in the source log only.

## Template

```md
# Market Signal - <signal ID>

## Metadata

- Signal ID:
- Origin ticket:
- Owner:
- Date captured:
- Approval state:
- Human review before roadmap/ranking use: yes/no

## Signal Capture

- Signal summary:
- Signal type:
- Source URL or repository path:
- Source owner:
- Source type:
- Publication/update/access date:
- Date checked:
- Geography:
- Persona or ICP:
- Problem or workflow:
- Affected C.O.N.T.R.O.L.E. dimension: C / O / L / other

## Signal Tags

- Market maturity: Emerging / Growing / Mature / Declining or saturated / Unknown
- Channel fit: Strong / Moderate / Weak / Blocked / Unknown
- Confidence: Low / Medium / High
- Risk if wrong: Low / Medium / High
- Source status: Candidate / Reviewed / Rejected / Blocked
- Limitation:
- What this does not prove:

## Source Quality Review

| Check | Result | Notes |
|---|---|---|
| Source inspectable | yes/no |  |
| Source date available | yes/no |  |
| Persona/geography clear | yes/no |  |
| Source type identified | yes/no |  |
| Bias or incentive noted | yes/no |  |
| Contradiction checked | yes/no |  |
| Approval needed | yes/no |  |

## Routing

- Routing decision: Ranking / Research synthesis / Source log only / Rejected / Blocked
- Ranking dimension affected:
- Research synthesis question:
- Customer discovery question:
- Risk review needed: yes/no
- Human review needed before roadmap change: yes/no
- Follow-up ticket needed: yes/no

## Decision Impact

- Assumption changed:
- Confidence changed: Increased / Decreased / Unchanged
- Roadmap or backlog change proposed: yes/no
- If yes, human approval blocker:
- Next artifact:
```

## Roadmap Safety Rules

Signals must not change roadmap, backlog priority, PRD/MVP scope, claims, growth, monetization, or implementation tickets unless:

- the signal has source traceability
- source date and geography/persona are visible or explicitly marked unknown
- confidence and risk if wrong are recorded
- the signal has been routed into ranking or research synthesis
- human review approves the resulting decision

Unsourced signals cannot change roadmap. They can only create assumptions or research questions.

## Future BuilderPulse Note

This template can later support BuilderPulse-style monitoring, but only after a separate approved implementation ticket defines:

- allowed signal sources
- connector/tool permissions
- no-scraping boundaries
- deduplication rules
- review queue
- human approval before roadmap or ticket changes
- disable/rollback plan

## Done Criteria

This template is complete when:

- signals require source, date, geography, persona, market maturity, channel fit, confidence, and risk if wrong
- signals are tagged before routing
- routing options include ranking, research synthesis, source log only, rejected, and blocked
- unsourced signals cannot change roadmap
- live scraping, automatic ticket creation, and BuilderPulse implementation remain out of scope
- human review is required before roadmap changes
