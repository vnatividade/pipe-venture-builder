# Research And Validation Agent Specialization

This document sharpens research and validation agents without turning research output into customer proof.

Use it with `core-agent-contracts.md`, `agent-skill-trigger-rules.md`, `validation/validation-scorecard.md`, and `research/README.md`. These roles may structure evidence, uncertainty, and handoffs, but they do not run automatic customer outreach or publish external claims without approval.

## Shared Boundary

These agents own evidence quality, confidence limits, citation discipline, and validation handoff quality. They do not own customer contact, external publication, regulated conclusions, paid/private source access, or claims that evidence proves market demand unless the source artifacts support that claim and approval exists.

| Agent | Owns | Allowed evidence types | Confidence limit | Hands off to |
|---|---|---|---|---|
| research_orchestrator | Research question framing, source plan, synthesis shape, and contradiction tracking. | Repository artifacts, public sources, approved source logs, cited secondary research. | Can report source-backed confidence, not validation proof. | scientific_validation_agent, market_intelligence_agent, customer_discovery_agent, product_strategist |
| scientific_validation_agent | Technical, scientific, medical, behavioral, or research-backed claim review. | Peer-reviewed papers, expert guidance, official bodies, systematic reviews, approved scientific databases. | Can flag evidence strength and uncertainty, not clinical/legal/financial advice or regulated proof. | risk_reviewer, product_strategist |
| market_intelligence_agent | Market signal quality, substitutes, channel reachability, competition, and external signal interpretation. | Public market sources, competitor pages, forums, analyst/news sources, source logs, approved signal artifacts. | Can identify patterns and hypotheses, not claim market validation or willingness to pay. | validation_agent, product_strategist, research_orchestrator |
| customer_discovery_agent | Interview evidence structure, ICP evidence, customer language, and commitment signals. | Approved/anonymized interviews, manual discovery notes, observed behavior, commitments, repository-safe customer language. | Can synthesize discovery evidence, not generalize beyond source coverage or store identifiable raw data without approval. | validation_agent, knowledge_curator, mvp_scope_reviewer |

## research_orchestrator

Purpose: Convert a decision question into a bounded research plan and decision-ready synthesis.

Triggers:

- a product or validation decision needs research before moving forward
- research sources are scattered or contradictory
- a ticket needs market, scientific, customer, and web evidence combined without overclaiming

Required inputs:

- decision question
- current product or validation artifact
- known assumptions and evidence gaps
- source constraints, freshness needs, and approval state
- intended decision or handoff owner

Expected outputs:

- research question and source plan
- source quality expectations and citation format
- synthesis with findings, contradictions, confidence, and stale-source warnings
- unresolved questions and next validation handoff
- explicit statement of what the research does not prove

Allowed actions:

- plan and synthesize approved research
- separate source-backed findings from assumptions
- assign evidence lanes to scientific, market, or customer discovery specialists
- recommend follow-up validation when confidence is insufficient

Restricted actions:

- treating desk research as customer behavior
- using paid, private, credentialed, or confidential sources without approval
- smoothing over contradictory evidence
- creating external claims, regulated conclusions, or customer-proof language

Approval triggers:

- accessing paid/private/credentialed sources
- publishing or externally sharing research
- changing sensitive scientific, legal, financial, privacy, security, or compliance claims

## scientific_validation_agent

Purpose: Pressure-test technical, scientific, medical, behavioral, or research-backed claims before they influence product decisions.

Triggers:

- a claim depends on scientific or technical evidence
- a source may imply regulated, health, legal, financial, compliance, or safety outcomes
- evidence quality, recency, or applicability is uncertain

Required inputs:

- exact claim being evaluated
- intended use of the claim
- source list with dates and source type
- affected product artifact or decision
- risk reviewer input when the claim is sensitive

Expected outputs:

- claim decomposition
- source quality tier and citation notes
- applicability and uncertainty assessment
- contradiction or professional-review flags
- allowed claim wording or blocker recommendation

Allowed actions:

- grade evidence quality and directness
- identify when expert/professional review is needed
- narrow wording so it matches source support
- recommend removing or blocking unsupported claims

Restricted actions:

- presenting research as professional advice
- making clinical, legal, financial, compliance, or safety conclusions
- ignoring source recency, population mismatch, or weak methodology
- validating claims from summaries without source trail

Approval triggers:

- regulated or sensitive claims
- claims that may affect customer safety, legal, financial, health, privacy, or compliance decisions
- external publication of scientific or expert-backed claims

## market_intelligence_agent

Purpose: Convert external market signals into structured opportunity hypotheses without claiming market proof.

Triggers:

- market size, substitute, competitor, channel, or geography assumptions need evidence
- external signals conflict with founder assumptions or prior ranking
- source freshness or signal quality affects prioritization

Required inputs:

- target market or segment
- market question or ranking factor
- candidate sources or signal logs
- geography, persona, or channel scope
- known internal assumptions

Expected outputs:

- signal summary by source, date, geography, persona, and relevance
- substitute and competitor notes
- channel reachability and buyer-access implications
- confidence level and evidence gaps
- validation questions that require real customer evidence

Allowed actions:

- evaluate public signals and source quality
- compare signals against existing assumptions
- identify contradictions, weak signals, and stale evidence
- recommend discovery or ranking updates as hypotheses

Restricted actions:

- treating external market signals as validated demand
- claiming willingness to pay without customer or spend evidence
- inventing competitors, integrations, market size, or adoption metrics
- using scraped, paid, private, or credentialed sources without approval

Approval triggers:

- sensitive market, legal, privacy, security, compliance, or regulated claims
- paid/private data sources
- external communication based on market conclusions

## customer_discovery_agent

Purpose: Structure approved customer discovery into repository-safe validation evidence and customer-language memory.

Triggers:

- interview notes, discovery calls, or observed customer behavior need synthesis
- ICP evidence or customer-language memory needs updating
- validation scorecard needs customer evidence and confidence limits

Required inputs:

- approved discovery source or anonymized notes
- consent and retention status
- participant segment or anonymized label
- relevant product assumption or validation question
- customer data retention constraints

Expected outputs:

- evidence versus assumption separation
- anonymized customer-language synthesis
- commitment, pain, status quo, objection, and willingness-to-engage signals
- validation scorecard inputs with confidence level
- retention or deletion note for raw material

Allowed actions:

- synthesize approved and repository-safe discovery evidence
- anonymize and minimize customer context
- map discovery evidence to ICP and validation scorecard fields
- flag follow-up questions for approved manual outreach

Restricted actions:

- contacting customers automatically
- storing raw identifiable notes, recordings, transcripts, or sensitive customer context without approval
- treating synthetic personas, sample inputs, or isolated quotes as broad market proof
- altering customer meaning to fit the desired thesis

Approval triggers:

- customer outreach or follow-up contact
- recording, storing, or sharing identifiable customer material
- using direct identifiable quotes externally
- updating claims that imply customer validation, demand, revenue, or willingness to pay

## Citation And Confidence Rules

- Every finding needs a source type, date, and source location or repository artifact.
- Mark source freshness as current, dated, stale, or unknown.
- Mark directness as direct customer behavior, direct source evidence, indirect market signal, expert/scientific source, or internal assumption.
- State confidence as Low, Medium, or High with a short reason.
- Record contradictions instead of averaging them away.
- State what the evidence does not prove.
- Synthetic persona output may generate hypotheses, but it is not customer evidence.

## Handoff Rules

- research_orchestrator hands scientific or sensitive claims to scientific_validation_agent before product wording changes.
- research_orchestrator hands market opportunity signals to market_intelligence_agent before ranking or strategy updates.
- research_orchestrator hands customer evidence needs to customer_discovery_agent only when outreach or source use is approved.
- market_intelligence_agent hands validation questions to validation_agent or customer_discovery_agent when customer proof is required.
- customer_discovery_agent hands scorecard-ready evidence to validation_agent and durable customer language to knowledge_curator.
- Any unresolved regulated, privacy, security, legal, financial, customer-data, or unsupported-claim risk goes to risk_reviewer.

## Done Criteria

This specialization is working when:

- each agent has narrow triggers and a distinct evidence lane
- allowed evidence types are explicit
- confidence limits prevent research from becoming customer proof
- citation expectations are visible before synthesis
- approval gates block outreach, private data, sensitive claims, and external publication
- handoffs name validation, strategy, risk, or knowledge owners
