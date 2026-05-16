# Research Orchestrator Workflow

This workflow defines how market, scientific, customer, and web research combine into one decision-ready synthesis without replacing customer discovery.

Use it with `.codex/agents/research-validation-specialization.md`, `validation/validation-scorecard.md`, `validation/customer-data-retention-policy.md`, `knowledge/knowledge-curator-workflow.md`, and `execution/approval-gates.md`.

## Boundary

This is a design-only workflow. It does not authorize live MCP calls, paid tools, credentialed sources, scraping, customer outreach, external publication, or regulated claims.

Research may strengthen or weaken hypotheses. It does not count as real customer proof unless it is based on approved customer discovery evidence and repository-safe source artifacts.

## When To Use

Use this workflow when:

- a product or validation decision needs multiple evidence types
- market, scientific, customer, and web sources need one synthesis
- existing sources conflict or have unclear confidence
- a research question should feed validation, PRD, MVP scope, risk review, or knowledge curation

Do not use this workflow to:

- bypass customer discovery
- justify build tickets when validation gates are not met
- make external claims from weak or indirect research
- access private, paid, credentialed, or confidential tools without approval

## Inputs

Required:

- Origin ticket or source artifact:
- Decision question:
- Product phase:
- Target market or ICP:
- Assumption being tested:
- Intended decision owner:
- Approval state for external tools:

Optional:

- Existing customer discovery artifacts:
- Existing market sources:
- Existing scientific or expert sources:
- Existing web/source logs:
- Known contradictions:
- Required freshness window:
- Sensitive claim or regulated-risk flag:

## Evidence Lanes

The research orchestrator separates evidence into lanes before synthesis.

| Lane | Owner | Allowed source types | Cannot prove by itself |
|---|---|---|---|
| Customer discovery | `customer_discovery_agent` | Approved/anonymized interviews, observed behavior, commitments, repository-safe customer language | Broad market demand, revenue, or willingness to pay beyond the source coverage |
| Market intelligence | `market_intelligence_agent` | Competitor pages, public market sources, forums, news, analyst summaries, approved signal logs | Customer proof, willingness to pay, or adoption for the specific ICP |
| Scientific validation | `scientific_validation_agent` | Peer-reviewed work, official guidance, expert sources, approved scientific databases | Legal, medical, financial, compliance, or safety conclusions |
| Web and source review | `research_orchestrator` | Public sources, source logs, repository artifacts, cited secondary research | Truth, validation, or external claim safety without review |

If a source does not fit a lane, mark it as `unclassified` and do not use it for decision confidence until reviewed.

## Workflow

### 1. Frame The Research Question

Write one decision question.

Good:

- "What evidence supports or weakens the assumption that this ICP already uses manual workarounds?"
- "Which substitutes and channels indicate reachable demand for this first wedge?"

Avoid:

- "Prove this is a good idea."
- "Find sources that support the thesis."

Record:

- Decision question:
- Decision this research will inform:
- What would change the decision:
- What evidence would be insufficient:

### 2. Build The Source Plan

For each evidence lane, define:

- source type
- search or retrieval approach
- freshness expectation
- confidence contribution
- approval needed before use
- owner agent

Use this table:

| Lane | Source type | Freshness expectation | Approval needed | Owner | Notes |
|---|---|---|---|---|---|
| Customer discovery |  |  |  | customer_discovery_agent |  |
| Market intelligence |  |  |  | market_intelligence_agent |  |
| Scientific validation |  |  |  | scientific_validation_agent |  |
| Web/source review |  |  |  | research_orchestrator |  |

Stop before any source that needs paid access, credentials, confidential material, customer contact, or external tool approval.

### 3. Capture Sources

Each source entry must include:

- source title
- source URL or repository artifact path
- source type
- publication or access date
- freshness label: Current / Dated / Stale / Unknown
- lane
- directness: Direct customer behavior / Direct source evidence / Indirect market signal / Expert or scientific source / Internal assumption
- relevant excerpt or summary
- limitation

Use concise summaries instead of copying long source text.

### 4. Score Confidence

Use Low, Medium, or High confidence.

| Confidence | Use when |
|---|---|
| Low | Evidence is indirect, stale, one-off, internally generated, or mostly assumption. |
| Medium | Multiple relevant sources point in the same direction but customer behavior is incomplete or source fit is imperfect. |
| High | Sources are recent, direct, consistent, and tied to observed behavior or strong source authority for the specific claim. |

Customer behavior remains stronger than market or web signals for validation decisions.

Scientific or expert confidence applies only to the evaluated claim, not to product demand.

### 5. Synthesize Findings

The synthesis must include:

- answer to the decision question
- strongest supporting evidence
- strongest contradicting evidence
- source conflicts
- confidence by lane
- assumptions still open
- what the evidence does not prove
- decision implication
- next validation action

Do not average contradictions away. Name them and explain which decision they affect.

### 6. Human Review Gate

Require human review before:

- using external research tools or paid/credentialed sources
- publishing research externally
- updating sensitive legal, financial, compliance, privacy, security, scientific, health, or customer-evidence claims
- using research to justify PRD, MVP scope, build, growth, monetization, or public positioning decisions
- storing identifiable customer data or direct identifiable quotes

If review is missing, mark the synthesis as blocked for decision use.

### 7. Handoff

Route the outcome based on the decision impact:

| Outcome | Handoff |
|---|---|
| Customer evidence needed | validation_agent or customer_discovery_agent |
| Scientific or regulated claim unresolved | scientific_validation_agent and risk_reviewer |
| Market signal affects ranking or ICP | market_intelligence_agent and product_strategist |
| Evidence changes validation confidence | validation_agent |
| Durable learning or decision changed | knowledge_curator |
| Architecture or build readiness affected | mvp_scope_reviewer or software_architect only after gates are satisfied |

## Synthesis Template

```md
# Research Synthesis - <decision question>

## Metadata

- Origin ticket:
- Research owner:
- Date:
- Product phase:
- Decision owner:
- Approval state:

## Decision Question

- Question:
- Decision this informs:
- What would change the decision:
- Insufficient evidence:

## Source Plan

| Lane | Source type | Freshness expectation | Approval needed | Owner | Notes |
|---|---|---|---|---|---|
| Customer discovery |  |  |  | customer_discovery_agent |  |
| Market intelligence |  |  |  | market_intelligence_agent |  |
| Scientific validation |  |  |  | scientific_validation_agent |  |
| Web/source review |  |  |  | research_orchestrator |  |

## Source Log

| Source | Type | Date | Freshness | Lane | Directness | Confidence | Limitation |
|---|---|---|---|---|---|---|---|
|  |  |  | Current / Dated / Stale / Unknown |  |  | Low / Medium / High |  |

## Findings

- Supporting evidence:
- Contradicting evidence:
- Source conflicts:
- Confidence by lane:
- Assumptions still open:
- What this does not prove:

## Decision Implication

- Recommended interpretation:
- Validation impact:
- PRD / MVP / risk impact:
- Human review required: yes/no
- Blocker:

## Handoff

- Next owner:
- Next repository artifact:
- Linear follow-up needed:
- Knowledge update needed:
```

## Done Criteria

The research orchestrator workflow is complete when:

- the decision question is explicit
- all source lanes are either populated or marked intentionally absent
- every source has date, freshness, directness, lane, confidence, and limitation
- contradictions and uncertainty are visible
- research output is not treated as customer proof
- human review gates are stated
- the handoff names the next owner and artifact
