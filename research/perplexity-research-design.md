# Perplexity Market And Web Research Design

This design note describes how a future Perplexity-style workflow could support current market and web research while preserving source traceability, freshness checks, confidence labels, and human review gates.

Use it with `research/market-research-workflow.md`, `research/research-orchestrator-workflow.md`, `.codex/agents/research-validation-specialization.md`, and `execution/approval-gates.md`.

## Boundary

This is a planning artifact only. It does not implement a Perplexity connector, call external tools, configure credentials, run live web automation, scrape sources, or authorize current-source claims without review.

Perplexity-style outputs may help find public sources and summarize external signals. They are not customer proof, market validation, willingness-to-pay evidence, or authority for public claims.

## Intended Use

Use a Perplexity-style workflow only when:

- a market question depends on current public web sources
- substitutes, competitors, channels, pricing pages, or public buyer language may have changed recently
- a research synthesis needs source links, access dates, and freshness labels
- the `market_intelligence_agent` needs a structured source trail before updating hypotheses
- current-source gaps need to be routed into customer discovery, risk review, or product strategy

Do not use it to:

- replace customer interviews, observed behavior, or approved validation artifacts
- prove demand, urgency, willingness to pay, revenue, adoption, or customer commitments
- publish market claims externally without review
- use paid, private, credentialed, confidential, or customer data sources without approval
- accept AI-generated answers without inspecting the underlying sources
- make legal, financial, compliance, privacy, security, scientific, or regulated claims

## Approval And Access Rules

Approval is required before:

- configuring or using a Perplexity connector or API
- using paid, private, credentialed, or confidential source access
- storing credentials, tokens, or account configuration
- scraping websites or bypassing access controls
- contacting customers, communities, competitors, analysts, or third parties
- publishing Perplexity-generated synthesis externally
- using research output to change PRD commitments, MVP scope, pricing, growth, sensitive claims, or implementation tickets

If approval is missing, keep the work as a local workflow design or source-plan draft and record the blocker in Linear.

## Query Design

Start with one decision-bound research question.

Required query fields:

- query ID
- origin Linear ticket
- decision question
- market or ICP
- geography
- source freshness window
- included source types
- excluded source types
- intended downstream artifact
- approval state

Good queries:

- "For solo US bookkeeping firms, what current public signals show which onboarding workflows are handled manually or with spreadsheets?"
- "Which direct and indirect substitutes currently target independent physical therapy clinics for intake form automation?"
- "What recent public buyer-language signals describe the pain around vendor security questionnaires for seed-stage B2B SaaS teams?"

Avoid:

- "Prove this market is growing."
- "Find sources that show customers will pay."
- "Tell me the TAM and why we should build."
- "Use current web sources to validate demand."

## Prompt Patterns

Use prompts that force source review, freshness, and limits.

### Market Signal Prompt

```md
Research the following market question using public web sources only.

Question:
<decision-bound market question>

Scope:
- ICP:
- Geography:
- Time/freshness window:
- Included source types:
- Excluded source types:

Return:
- 5-10 candidate sources with URLs
- publication or access date for each source
- source type
- freshness label: Current / Dated / Stale / Unknown
- directness: Direct source evidence / Indirect market signal / Internal assumption
- short summary of the signal
- limitation for each source
- confidence label: Low / Medium / High

Do not claim validation, demand, willingness to pay, revenue, adoption, or customer proof.
```

### Substitute Discovery Prompt

```md
Identify current direct, indirect, DIY, and do-nothing substitutes for this ICP and problem.

ICP:
Problem:
Geography:
Freshness window:

For each substitute, return:
- substitute type
- source URL
- source date or access date
- ICP match
- pain addressed
- switching friction signal
- pricing or effort signal only if explicitly sourced
- confidence
- what this does not prove

Do not infer customer demand from substitute existence alone.
```

### Freshness Check Prompt

```md
Review these candidate sources for freshness and source quality.

Sources:
<source list>

For each source, classify:
- date found
- publication date, updated date, or access date
- freshness: Current / Dated / Stale / Unknown
- source owner
- primary or secondary source
- possible bias
- broken, inaccessible, or uninspectable source status
- safe use in repository synthesis: yes/no
- reason
```

### Synthesis Prompt

```md
Synthesize the reviewed sources into market hypotheses.

Use only sources with inspectable URLs and dates.

Return:
- strongest supporting signals
- strongest contradicting signals
- source conflicts
- confidence by signal
- customer discovery questions created by the sources
- what the research does not prove
- human review required: yes/no
- recommended next repository artifact

Do not create GO / NO-GO decisions, public claims, implementation approval, or validation proof.
```

## Source Entry Requirements

Every source considered for synthesis must include:

- source title
- source URL
- source owner or publisher, when available
- publication date, updated date, or access date
- date the source was checked
- source type
- lane: market intelligence / web-source review / scientific validation / customer discovery / internal artifact
- freshness: Current / Dated / Stale / Unknown
- directness: Direct source evidence / Indirect market signal / Expert or scientific source / Internal assumption
- relevant market question
- signal summary
- confidence: Low / Medium / High
- limitation
- review status: Candidate / Reviewed / Rejected / Blocked

If a source URL cannot be inspected directly, mark the source as `Blocked` or `Rejected` and do not use it to support a finding.

## Freshness Rules

Freshness depends on the decision and market.

| Label | Use when | Decision limit |
|---|---|---|
| Current | The source is recent enough for the market question and the date is visible or access date is recorded. | Can support current hypothesis context after review. |
| Dated | The source may still be useful but is outside the preferred freshness window. | Use for background context, not current-state claims. |
| Stale | The source is old for a fast-changing market, product category, regulation, pricing, or competitor signal. | Do not use for current-state claims. |
| Unknown | The source has no clear publication, update, or access date. | Use only as weak context, or exclude from synthesis. |

Pricing, competitor positioning, channel behavior, regulation, tool availability, and market news usually need shorter freshness windows than evergreen educational material.

## Confidence Labels

Use Low, Medium, or High confidence for each finding.

| Confidence | Use when |
|---|---|
| Low | One source, weak ICP match, stale/unknown date, indirect signal, unclear owner, or unreviewed source trail. |
| Medium | Multiple inspectable sources point in the same direction but customer behavior or ICP fit remains incomplete. |
| High | Multiple recent, inspectable, direct sources align for the specific ICP, geography, and question. |

High confidence web research still does not equal customer proof. Customer discovery remains required for demand, urgency, willingness to pay, and commitments.

## Source Review Checklist

Before using a Perplexity-style result in repository synthesis, review:

- Can the underlying URL be opened or otherwise inspected?
- Is the source owner visible?
- Is the publication, update, or access date recorded?
- Does the source directly match the ICP, geography, and problem?
- Is the signal primary evidence, secondary commentary, or an AI-generated summary?
- Are there obvious incentives, affiliate bias, vendor bias, or outdated claims?
- Is there a credible contradiction from another source?
- Would using this source affect sensitive claims, regulated content, pricing, growth, or implementation scope?
- Does this source require paid/private/credentialed access or approval?

If the source fails review, record the limitation and exclude it from decision-impacting synthesis.

## Synthesis Outputs

Allowed outputs:

- cited source list
- freshness review table
- market signal summary
- substitute map inputs
- competitor or channel hypothesis inputs
- contradictions and source-quality gaps
- confidence by signal
- questions for customer discovery
- handoff to `market_intelligence_agent`, `research_orchestrator`, `validation_agent`, or `risk_reviewer`

Restricted outputs:

- GO / NO-GO decisions
- market validation claims
- customer proof claims
- willingness-to-pay claims
- revenue, adoption, or traction claims
- public copy or external communications
- implementation-ticket approval
- pricing, billing, legal, financial, privacy, security, compliance, scientific, or regulated conclusions

## Output Template

```md
# Perplexity Research Review - <market question>

## Metadata

- Origin ticket:
- Owner:
- Date:
- Market / ICP:
- Geography:
- Product phase:
- Approval state:
- Freshness window:

## Research Question

- Question:
- Decision this informs:
- Included source types:
- Excluded source types:
- What would require customer discovery:
- What would require human or risk review:

## Query Log

| Query ID | Prompt purpose | Date run | Approval state | Notes |
|---|---|---|---|---|
|  | Market signal / Substitute discovery / Freshness check / Synthesis |  |  |  |

## Source Review

| Source | URL | Source type | Source date | Checked date | Freshness | Directness | Confidence | Review status | Limitation |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  | Current / Dated / Stale / Unknown | Direct source evidence / Indirect market signal / Expert or scientific source / Internal assumption | Low / Medium / High | Candidate / Reviewed / Rejected / Blocked |  |

## Findings

- Supporting signals:
- Contradicting signals:
- Source conflicts:
- Weak or rejected sources:
- Confidence by signal:
- What this does not prove:

## Handoff

- Next owner:
- Next repository artifact:
- Customer discovery questions:
- Risk review needed:
- Linear follow-up needed:
```

## Handoff Rules

| Finding type | Handoff |
|---|---|
| Substitute, competitor, channel, pricing, or buyer-language signal | `market_intelligence_agent` |
| Source conflict, freshness uncertainty, or mixed evidence lane | `research_orchestrator` |
| Customer behavior, urgency, pain, or willingness-to-pay gap | `validation_agent` or `customer_discovery_agent` |
| Scientific, regulated, legal, financial, privacy, security, or compliance implication | `risk_reviewer` and relevant specialist |
| Durable evidence map or research learning | `knowledge_curator` |

## Done Criteria

This design note is complete when:

- Perplexity usage is limited to source discovery, freshness review, and bounded synthesis
- source links, dates, freshness labels, confidence labels, and limitations are required
- source review is required before any finding affects repository decisions
- AI-generated answers are not accepted as source evidence
- customer discovery remains required for validation proof
- approval gates block connector use, credentials, paid/private sources, scraping, external publication, and sensitive claims
