# Market Research Workflow

This workflow defines how to evaluate market size, substitutes, channels, competition, reachability, and market maturity without relying on generic TAM slides.

Use it with `research/research-orchestrator-workflow.md`, `.codex/agents/research-validation-specialization.md`, `validation/icp-profile.md`, `validation/validation-scorecard.md`, and `product/founder-focus.md`.

## Boundary

This is a design-only workflow for market intelligence. It does not authorize paid research tools, credentialed data sources, scraping, customer outreach, external publication, or claims of market validation.

Market research can identify reachable hypotheses and risks. It does not prove customer demand, willingness to pay, or founder-market fit without customer discovery evidence.

## When To Use

Use this workflow when:

- an ICP or founder-focus decision needs market context
- substitutes, buyer leverage, channels, competition, or market maturity are unclear
- a market looks large but reachability is unproven
- country or city variation may change feasibility
- market signals need to feed validation, ranking, PRD, or MVP scope

Do not use this workflow to:

- justify build tickets from market size alone
- replace customer interviews or observed behavior
- invent market share, revenue, willingness to pay, or adoption metrics
- use paid, private, credentialed, or confidential sources without approval

## Inputs

Required:

- Origin ticket or source artifact:
- ICP or target segment:
- Problem hypothesis:
- Offer or wedge:
- Geography:
- Primary channel hypothesis:
- Current substitute hypothesis:
- Approval state for paid or external tools:

Optional:

- Competitor list:
- Existing market notes:
- Customer discovery artifacts:
- Forum/community sources:
- Country/city constraints:
- Buyer role and budget owner:
- Regulatory, procurement, or trust constraints:

## Workflow

### 1. Define The Market Question

Write one specific market question.

Good:

- "Can this ICP be reached through founder-led channels without paid acquisition?"
- "What substitutes does this segment already use when the workflow breaks?"
- "Is competition dense because demand is validated or because the market is noisy?"

Avoid:

- "How big is this market?"
- "Find a huge TAM."
- "Prove this category is growing."

Record:

- Market question:
- Decision this research informs:
- ICP and geography:
- What would make the market unattractive:
- What would require customer discovery:

### 2. Map Substitutes

Start with substitutes before market size.

| Substitute type | Definition | Evidence to look for | Interpretation limit |
|---|---|---|---|
| Direct substitute | A product or service explicitly solving the same problem for the same ICP. | Competitor pages, reviews, pricing, case studies, user complaints. | Shows category awareness, not automatic demand for this wedge. |
| Indirect substitute | A different product, service, or workflow solving part of the job. | Adjacent tools, agencies, consultants, internal systems. | Shows problem-adjacent spend or behavior, not exact solution fit. |
| DIY substitute | Manual process, spreadsheet, scripts, templates, internal workaround. | Forum posts, templates, job descriptions, tutorial content, interview notes. | Often strong pain signal, but still needs customer confirmation. |
| Do-nothing substitute | The buyer tolerates the pain, delays action, or accepts status quo risk. | Low urgency, weak penalties, unclear ownership, no budget trigger. | Can invalidate urgency even when the market looks large. |

For each substitute, capture:

- name or pattern
- source
- ICP match
- buyer or user
- pain addressed
- switching friction
- pricing or effort signal, if sourced
- confidence
- what this does not prove

### 3. Assess Buyer Leverage

Buyer leverage determines whether the founder can reach and persuade the first segment.

| Factor | Questions | Evidence |
|---|---|---|
| Buyer clarity | Who owns the problem and budget? Is the user different from the buyer? | Role descriptions, procurement notes, customer discovery, public buying pages. |
| Trigger event | When does the buyer actively look for a solution? | Compliance deadline, growth pain, operational failure, seasonal cycle, new tool adoption. |
| Budget path | Is there existing spend, time cost, or budget category? | Pricing pages, job postings, agency spend, tool stack, interview notes. |
| Switching cost | What makes switching hard? | Integrations, training, trust, migration, compliance, team habit. |
| Decision speed | Can a solo founder reach a decision-maker quickly? | Channel access, community presence, founder network, sales cycle signals. |

Mark buyer leverage:

- High: clear owner, urgent trigger, accessible channel, low switching friction.
- Medium: reachable but requires education, trust-building, or multiple stakeholders.
- Low: unclear owner, long procurement, high trust burden, or weak urgency.

### 4. Evaluate Channel Access

Assess whether the first channel is reachable without paid acquisition by default.

| Channel | Reachability signal | Risks | Confidence |
|---|---|---|---|
| Founder network | Existing relationships or warm paths to ICP. | Biased sample, limited scale. | Low / Medium / High |
| Communities | ICP gathers in identifiable public/private groups. | Access rules, promotion bans, noisy feedback. | Low / Medium / High |
| Search intent | ICP searches for problem, workaround, or substitute terms. | SEO delay, ambiguous intent. | Low / Medium / High |
| Content or social | ICP engages with practical problem content. | Vanity engagement, weak conversion. | Low / Medium / High |
| Partnerships | Existing vendors or advisors already reach ICP. | Dependency, slow BD, trust transfer. | Low / Medium / High |
| Direct manual outreach | ICP can be identified and contacted after approval. | Requires explicit outreach approval and careful claims. | Low / Medium / High |

If the only plausible channel is paid acquisition, mark the market as channel-risky unless the ticket explicitly approves paid tests.

### 5. Analyze Competitive Density

Competition is not automatically good or bad.

Assess:

- number of direct substitutes
- number of indirect substitutes
- competitor focus by ICP
- pricing visibility
- evidence of customer complaints or churn
- positioning gaps
- switching friction
- trust and compliance burden
- founder-accessible wedge

Classify density:

| Density | Meaning | Possible implication |
|---|---|---|
| Sparse | Few visible substitutes. | Could be overlooked opportunity or weak demand. Needs customer discovery. |
| Moderate | Some substitutes and visible workarounds. | Often best for wedge testing if channels are reachable. |
| Dense | Many products, agencies, or incumbents. | Demand may exist, but differentiation and channel access are harder. |
| Noisy | Many generic tools with unclear ICP fit. | Risk of category confusion; need sharper wedge and customer language. |

### 6. Assess Market Maturity

Market maturity helps decide whether to educate, differentiate, or avoid.

| Maturity | Signals | Risk |
|---|---|---|
| Emerging | New language, fragmented workarounds, few clear budgets. | Education burden and unclear buyer. |
| Growing | Increasing tools, communities, workflows, and budget awareness. | Fast learning but rising competition. |
| Mature | Clear categories, budgets, review sites, incumbents. | Harder differentiation and switching. |
| Declining or saturated | Price compression, weak growth signals, vendor fatigue. | Low willingness to switch or pay. |

Do not treat maturity as validation. It only frames the next research or discovery step.

### 7. Add Country And City Variation Hooks

Record geography-specific factors for later ranking.

| Geography factor | Country/city note | Why it matters | Confidence |
|---|---|---|---|
| Regulation or compliance |  | Can change risk, urgency, and adoption. | Low / Medium / High |
| Payment behavior |  | Affects monetization and procurement path. | Low / Medium / High |
| Local substitutes |  | Global competitors may not reflect local behavior. | Low / Medium / High |
| Channel concentration |  | Some ICPs gather in local associations or communities. | Low / Medium / High |
| Language and messaging |  | Customer language may differ by region. | Low / Medium / High |
| Market maturity |  | Emerging in one city may be mature elsewhere. | Low / Medium / High |
| Founder access |  | Warm access can change first-test feasibility. | Low / Medium / High |

Use these hooks as future ranking inputs, not as automatic expansion scope.

### 8. Synthesize Market Attractiveness

Summarize the market using evidence, not generic size.

| Dimension | Rating | Evidence | Confidence | Notes |
|---|---|---|---|---|
| Substitute clarity | Low / Medium / High |  | Low / Medium / High |  |
| Buyer leverage | Low / Medium / High |  | Low / Medium / High |  |
| Channel access | Low / Medium / High |  | Low / Medium / High |  |
| Competitive density fit | Low / Medium / High |  | Low / Medium / High |  |
| Market maturity fit | Low / Medium / High |  | Low / Medium / High |  |
| Country/city feasibility | Low / Medium / High |  | Low / Medium / High |  |

Decision guidance:

- Attractive: clear substitutes, reachable buyer/channel, manageable density, and useful maturity.
- Needs discovery: some promising signals but customer behavior, budget, or channel is unproven.
- Risky: weak substitutes, unclear buyer, inaccessible channel, or do-nothing behavior dominates.
- Avoid for now: generic market size is the strongest signal or the first wedge is not reachable.

## Output Template

```md
# Market Research - <ICP / market question>

## Metadata

- Origin ticket:
- Owner:
- Date:
- ICP:
- Geography:
- Product phase:
- Approval state:

## Market Question

- Question:
- Decision this informs:
- What would make the market unattractive:
- What requires customer discovery:

## Substitute Map

| Type | Substitute or pattern | Source | ICP match | Pain addressed | Switching friction | Confidence | Does not prove |
|---|---|---|---|---|---|---|---|
| Direct / Indirect / DIY / Do-nothing |  |  | Low / Medium / High |  | Low / Medium / High | Low / Medium / High |  |

## Buyer Leverage

| Factor | Finding | Evidence | Rating | Confidence |
|---|---|---|---|---|
| Buyer clarity |  |  | Low / Medium / High | Low / Medium / High |
| Trigger event |  |  | Low / Medium / High | Low / Medium / High |
| Budget path |  |  | Low / Medium / High | Low / Medium / High |
| Switching cost |  |  | Low / Medium / High | Low / Medium / High |
| Decision speed |  |  | Low / Medium / High | Low / Medium / High |

## Channel Access

| Channel | Reachability signal | Risk | Rating | Confidence |
|---|---|---|---|---|
|  |  |  | Low / Medium / High | Low / Medium / High |

## Competition And Maturity

- Competitive density: Sparse / Moderate / Dense / Noisy
- Maturity: Emerging / Growing / Mature / Declining or saturated
- Differentiation hypothesis:
- Founder-accessible wedge:
- Risks:

## Country And City Hooks

| Geography factor | Country/city note | Why it matters | Confidence |
|---|---|---|---|
| Regulation or compliance |  |  | Low / Medium / High |
| Payment behavior |  |  | Low / Medium / High |
| Local substitutes |  |  | Low / Medium / High |
| Channel concentration |  |  | Low / Medium / High |
| Language and messaging |  |  | Low / Medium / High |
| Market maturity |  |  | Low / Medium / High |
| Founder access |  |  | Low / Medium / High |

## Synthesis

- Market attractiveness: Attractive / Needs discovery / Risky / Avoid for now
- Strongest evidence:
- Weakest evidence:
- Contradictions:
- What generic market size would hide:
- What this does not prove:
- Next validation action:
- Handoff owner:
```

## Human Review Gate

Require human review before:

- using paid, private, credentialed, or confidential research tools
- contacting customers or communities
- publishing market claims externally
- changing sensitive legal, financial, compliance, privacy, security, scientific, or customer-evidence claims
- using market research alone to justify PRD, MVP scope, build, growth, monetization, or public positioning decisions

If review is missing, market research may be used only as hypothesis context.

## Done Criteria

The market research workflow is complete when:

- direct, indirect, DIY, and do-nothing substitutes are explicitly considered
- buyer leverage is rated with evidence and confidence
- channel access is assessed without assuming paid acquisition
- competitive density and market maturity are classified
- country/city variation hooks are captured for later ranking
- generic market size is not the strongest decision signal
- customer discovery remains the required path for validation proof
