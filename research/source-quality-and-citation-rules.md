# Source Quality And Citation Rules

These rules define how research sources are ranked, cited, dated, challenged, and carried into synthesis without turning source summaries into proof.

Use them with `research/research-orchestrator-workflow.md`, `research/market-research-workflow.md`, `research/scientific-validation-workflow.md`, `research/perplexity-research-design.md`, and `execution/approval-gates.md`.

## Boundary

These rules improve traceability and source review. They do not guarantee truth, replace customer discovery, replace expert review, or authorize sensitive claims.

Research outputs may inform hypotheses and next validation steps. They must not be treated as customer proof, market validation, professional advice, or approval to build unless the relevant workflow and human review gates are satisfied.

## Required Fields For Every Source

Every source used in a research output must include:

- source ID
- source title
- source URL or repository artifact path
- source owner or publisher, when available
- source type
- publication date, updated date, or access date
- date checked
- freshness: Current / Dated / Stale / Unknown
- directness: Direct customer behavior / Direct source evidence / Indirect market signal / Expert or scientific source / Internal assumption
- source tier
- confidence: Low / Medium / High
- risk if wrong: Low / Medium / High
- limitation
- review status: Candidate / Reviewed / Rejected / Blocked

If one of these fields is missing, mark it explicitly as `Unknown` or `Not available`. Do not silently omit it.

## Source Types

| Source type | Typical use | Cannot prove by itself |
|---|---|---|
| Approved customer discovery | Customer language, pain, workflow behavior, objections, commitments within source coverage. | Broad market demand, revenue, or behavior outside the sampled segment. |
| Repository artifact | Internal strategy, PRD, validation notes, decisions, and prior synthesis. | External truth or customer evidence unless backed by sources. |
| Primary public source | Vendor page, pricing page, official documentation, public filing, standards body, direct announcement. | Customer demand, adoption, or willingness to pay without direct evidence. |
| Secondary public source | Analyst report, article, newsletter, comparison page, curated list. | Primary evidence or unbiased market truth. |
| Forum or community signal | Language, complaints, workaround hints, objections, and possible channel context. | Representativeness, buyer authority, or willingness to pay. |
| Scientific or expert source | Claim support, mechanism context, technical evidence, or professional caveats. | Product demand or regulated conclusions without review. |
| AI-generated summary | Discovery aid pointing to possible sources. | Source evidence. The underlying source must be inspected. |
| Internal assumption | Hypothesis, founder belief, or agent inference. | Evidence. It must remain separate from findings. |

## Source Tiers

Use the strongest appropriate tier and record why it applies.

| Tier | Source class | Use | Limit |
|---|---|---|---|
| Tier 1 | Approved customer behavior for the exact ICP, official standards or guidance, systematic reviews, primary studies with clear methods, authoritative primary documents. | Strongest evidence input for the matching claim or question. | Still limited by scope, consent, applicability, and review gates. |
| Tier 2 | Reputable institutional reports, expert consensus, official technical documentation, direct competitor/vendor evidence, high-quality benchmarks. | Useful for market, technical, or expert context. | May be indirect, biased, incomplete, or not specific to the ICP. |
| Tier 3 | Single articles, case studies, vendor blogs, public demos, community threads, social posts with inspectable context, non-systematic summaries. | Discovery and hypothesis generation. | Weak basis for decision-critical claims. Needs corroboration. |
| Tier 4 | AI summaries, unsourced claims, stale pages, inaccessible pages, screenshots without provenance, internal opinion. | Lead generation for better sources or assumptions register. | Not acceptable as evidence for decisions or claims. |

Tier 4 sources may not support a finding unless the output clearly labels them as weak context or assumptions.

## Freshness Labels

| Freshness | Use when | Citation requirement | Decision limit |
|---|---|---|---|
| Current | Date is visible or access date is recorded and the source is recent enough for the question. | Publication/update date or access date. | Can support hypothesis context after review. |
| Dated | Source may still be useful but falls outside the preferred freshness window. | Date plus reason it remains useful. | Background context only for current-state claims. |
| Stale | Source is old for the market, regulation, pricing, tool, competitor, or scientific claim. | Date plus stale-source warning. | Do not use for current-state claims. |
| Unknown | Date is absent, unclear, or unavailable. | Access date and unknown-date note. | Weak context only; avoid decision-impacting use. |

When freshness matters, define the window before research begins. Pricing, competitor positioning, regulation, tool availability, market news, and channel behavior usually require tighter windows than evergreen concepts.

## Confidence Labels

| Confidence | Use when | Required explanation |
|---|---|---|
| Low | Evidence is indirect, stale, uncorroborated, weakly matched to the ICP, source ownership is unclear, or source quality is low. | Name the gap and next source needed. |
| Medium | Multiple relevant sources point in the same direction, but direct customer behavior, exact ICP fit, or source independence remains incomplete. | Name what is supported and what remains unproven. |
| High | Multiple recent, inspectable, direct, independent sources support the exact claim, ICP, geography, or workflow. | State the scope where confidence applies and review gates still needed. |

High confidence desk research is still not customer proof unless it is based on approved customer discovery or observed customer behavior.

## Risk If Wrong

Every cited finding must state the risk if the finding is wrong.

| Risk | Use when | Required action |
|---|---|---|
| Low | Error would mostly affect internal prioritization or minor wording. | Record limitation. |
| Medium | Error could mislead product scope, validation planning, positioning, channel choice, or founder time allocation. | Require human review before decision impact. |
| High | Error could affect safety, money, legal/privacy/security posture, regulated claims, customer trust, billing, external communication, or production behavior. | Block decision/public use until risk reviewer and human or expert review. |

High-risk findings cannot be used to change PRD, MVP scope, public claims, pricing, legal/compliance/security/privacy content, or implementation scope without review.

## Citation Format

Use this compact citation format in research outputs:

```md
<Source ID> - <Title> (<Source type>, <Tier>, <Date or access date>, <Freshness>, <Confidence>, Risk if wrong: <Low/Medium/High>) - <URL or repository path>
Limit: <one sentence limitation>
```

Example:

```md
S-001 - Example vendor pricing page (Primary public source, Tier 2, accessed 2026-05-16, Current, Medium, Risk if wrong: Medium) - https://example.com/pricing
Limit: Vendor pricing shows an available substitute but does not prove buyer adoption or willingness to pay for this wedge.
```

Do not cite an AI-generated answer as the source. Cite the underlying URL or repository artifact that was inspected.

## Simple Source Log Template

Use this table when a workflow needs a lightweight source log.

```md
| Source ID | Source | URL or path | Type | Tier | Date | Checked | Freshness | Directness | Confidence | Risk if wrong | Status | Limitation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S-001 |  |  |  | Tier 1 / 2 / 3 / 4 |  |  | Current / Dated / Stale / Unknown | Direct customer behavior / Direct source evidence / Indirect market signal / Expert or scientific source / Internal assumption | Low / Medium / High | Low / Medium / High | Candidate / Reviewed / Rejected / Blocked |  |
```

Keep source logs short enough to maintain. If a source does not affect the synthesis, reject it or move it out of the active log.

## Challenging Sources

Before a source supports a finding, challenge it with these questions:

- Is the source inspectable from a URL or repository path?
- Who owns or published it?
- Is the relevant date visible or is the access date recorded?
- Is the source primary evidence, secondary commentary, expert context, customer evidence, or AI-generated summary?
- Does it match the ICP, geography, product phase, and exact research question?
- What incentive, bias, sample limit, or methodology limit could distort the source?
- What credible source would contradict or weaken it?
- What would be the risk if this source is wrong?
- Does the source touch sensitive legal, financial, compliance, privacy, security, scientific, customer, or regulated claims?
- Does source use require approval because it is paid, private, credentialed, confidential, customer-related, or externally published?

If the source cannot pass basic traceability, mark it `Rejected` or `Blocked`.

## Conflict Rules

Do not average away conflicting sources.

When sources disagree, record:

- the conflicting source IDs
- what they disagree about
- which source is more direct
- which source is fresher
- which source has stronger methodology or authority
- whether the conflict changes confidence
- whether a risk reviewer or human review is required
- what additional evidence would resolve the conflict

If a material conflict affects a decision, mark the synthesis as blocked for decision use until reviewed.

## Output Requirements

Every research output must show:

- source type
- source date or access date
- freshness
- confidence
- risk if wrong
- limitation
- conflicts or contradiction status
- what the source does not prove
- human review status when decision impact exists

Research outputs that summarize sources without traceability are incomplete.

## Human Review Gate

Human review is required before:

- using source synthesis to change PRD, MVP scope, validation thresholds, pricing, growth, monetization, public positioning, or implementation tickets
- publishing research or claims externally
- using paid, private, credentialed, confidential, customer, or production data sources
- accepting high-risk findings
- making or changing legal, financial, compliance, privacy, security, scientific, customer-evidence, or regulated claims

If review is missing, the source-backed output may be used only as hypothesis context.

## Done Criteria

These rules are complete when:

- source types and tiers are defined
- every source requires type, date, freshness, confidence, risk if wrong, and limitation
- citation format preserves source traceability
- conflicts and contradictions are explicitly handled
- AI-generated summaries are excluded as source evidence
- human review gates block high-risk or decision-impacting use
- the source log stays simple enough for future agents to maintain
