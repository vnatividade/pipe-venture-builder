# Validation

Validation artifacts live here.

This area should prove whether the idea is worth building before the team invests serious implementation effort.

Planned artifacts:

- [`conversational-pipeline-mood-test-protocol.md`](conversational-pipeline-mood-test-protocol.md)
- [`customer-interview-template.md`](customer-interview-template.md)
- [customer data retention policy](customer-data-retention-policy.md)
- [`geography-ranking-rubric.md`](geography-ranking-rubric.md)
- [`branding-prototype-readiness-gate.md`](branding-prototype-readiness-gate.md)
- [`icp-profile.md`](icp-profile.md)
- [`market-validation-before-code-gate.md`](market-validation-before-code-gate.md)
- [`persona-ranking-rubric.md`](persona-ranking-rubric.md)
- [`pmf-evidence-metrics.md`](pmf-evidence-metrics.md)
- [`pre-user-security-privacy-readiness-gate.md`](pre-user-security-privacy-readiness-gate.md)
- [`raw-interview-evidence-intake-and-synthesis.md`](raw-interview-evidence-intake-and-synthesis.md)
- [`respondent-targeting-and-interview-planner.md`](respondent-targeting-and-interview-planner.md)
- [`synthetic-persona-generation-workflow.md`](synthetic-persona-generation-workflow.md)
- [`synthetic-objection-risk-extraction-workflow.md`](synthetic-objection-risk-extraction-workflow.md)
- [`synthetic-persona-simulation-prompt.md`](synthetic-persona-simulation-prompt.md)
- [`synthetic-vs-real-interview-comparison-template.md`](synthetic-vs-real-interview-comparison-template.md)
- [`synthetic-persona-schema.md`](synthetic-persona-schema.md)
- [`venture-validation-framework.md`](venture-validation-framework.md)
- [`distribution-and-embedded-workflow-prompts.md`](distribution-and-embedded-workflow-prompts.md)
- experiment test card
- learning card
- GO / NO-GO decision record
- MVP readiness review
- [`validation-scorecard.md`](validation-scorecard.md)
- [test runs](test-runs/)
- [planos de descoberta](discovery-plans/)

Validation should prioritize behavior, urgency, willingness to engage, repeated use, and willingness to pay over opinions alone.

Use the [Conversational Pipeline Mood Test Protocol](conversational-pipeline-mood-test-protocol.md) to validate whether an operating agent can guide a founder from abstract intent through the Pipe pipeline without requiring the founder to choose repository files, internal gates, skills, MCPs, capabilities, or agent roles. The protocol tests user experience, stage routing, capability routing, knowledge routing, approval gates, pass/fail criteria, and guided session handoff.

The first controlled run is captured in [`test-runs/conversational-pipeline-mood-test-2026-06-02.md`](test-runs/conversational-pipeline-mood-test-2026-06-02.md). It is a protocol validation artifact, not customer validation or product evidence.

The first live founder-led run is captured in [`test-runs/conversational-pipeline-live-mood-test-2026-06-02-tcc-quimica.md`](test-runs/conversational-pipeline-live-mood-test-2026-06-02-tcc-quimica.md). It records a real founder idea around Chemistry TCC bibliographic-review support, but it is still a guided pipeline mood test. It is not customer validation, not pricing proof, not scientific validation, and not approval to create product implementation scope.

O primeiro plano manual de descoberta para esse recorte de TCC esta registrado em [`discovery-plans/tcc-bibliographic-review-manual-discovery-plan.md`](discovery-plans/tcc-bibliographic-review-manual-discovery-plan.md). Ele prepara cinco entrevistas conduzidas pelo fundador com estudantes antes de PRD ou construcao, usando PM Skills para estruturar entrevistas enquanto preserva os pontos de decisao de validacao da Pipe.

Validation should also capture contradiction. After meaningful discovery batches, agents must record evidence that supports the thesis, evidence that contradicts it, ambiguous signals, confidence changes, and the real-world evidence needed to resolve the contradiction. Synthetic or AI-generated critique may help find blind spots, but it does not count as validation evidence.

The [PMF Evidence Metrics](pmf-evidence-metrics.md) guide should be used before treating MVP traction as product-market fit, launch readiness, scale readiness, or billing readiness.

The [Pre-User Security And Privacy Readiness Gate](pre-user-security-privacy-readiness-gate.md) must be used before real users, prospects, customers, partners, or external participants touch a prototype, manual test, form, workflow, dataset, prompt output, product trial, or validation artifact.

The validation scorecard must link back to founder focus and C.O.N.T.R.O.L.E. before PRD, build, growth, or monetization work.

The [Market Validation Before Code Gate](market-validation-before-code-gate.md) must be applied before product PRD, architecture, implementation, growth, monetization, or customer-facing build tickets. For governance-only, documentation-only, research-only, or internal operating tickets, record `Gate decision: NOT APPLICABLE` instead of blocking execution.

Use the [Branding And Prototype Readiness Gate](branding-prototype-readiness-gate.md) before customer-facing code, prototype sharing, landing pages, onboarding flows, product trials, or interface implementation when brand, prototype, or UX ambiguity could distort learning. This gate is contextual: classify it as `REQUIRED`, `OPTIONAL`, or `NOT APPLICABLE`, and never use it to bypass Market Validation Before Code.

The [Venture Validation Framework](venture-validation-framework.md) adds MAYA, the 8 Innovation Flavors, and the PMF triad as upstream validation lenses. These are heuristics for better questions, not rigid scores or replacements for C.O.N.T.R.O.L.E.

The [Distribution and Embedded Workflow Prompts](distribution-and-embedded-workflow-prompts.md) add China-inspired but locally adapted questions for channel entry, workflow insertion, moment-of-use, payment assumptions, trust loops, and ecosystem dependency before PRD or build work.

Customer discovery artifacts must distinguish exact quotes, observed evidence, assumptions, and synthesis. Fictional personas do not count as real interviews.

Customer discovery artifacts must follow the customer data retention policy before storing identifiable notes, recordings, transcripts, exact quotes, or sensitive customer context.

Use the [Respondent Targeting And Interview Planner](respondent-targeting-and-interview-planner.md) before manual customer discovery when agents need to suggest which respondent profiles the founder should seek and which questions should be asked. The planner does not authorize outreach, lead sourcing, scraping, automated messaging, AI calls, or storage of identifiable customer data.

Use the [Raw Interview Evidence Intake And Synthesis](raw-interview-evidence-intake-and-synthesis.md) workflow after approved discovery conversations, interviews, notes, or call summaries to turn raw material into anonymized evidence, contradiction synthesis, scorecard inputs, customer-language memory, PMF signals, and follow-ups. It does not authorize upload pipelines, transcription services, automatic ingestion, recordings, or storage of identifiable raw data.

Use the [Persona Ranking Rubric](persona-ranking-rubric.md) when comparing which target persona should be validated first for a given idea. Every persona score must include evidence type, confidence, and source; synthetic or fictional personas remain hypotheses and cannot outrank interview-backed evidence.

Use the [Geography Ranking Rubric](geography-ranking-rubric.md) when comparing country, region, city, or local-market fit for a given idea and persona. Every geography score must include source citation, source date or access date, evidence type, and confidence; regulatory, legal, compliance, tax, privacy, financial, healthcare, safety, or sensitive local-market claims require human or expert review.

Use the [Synthetic Persona Schema](synthetic-persona-schema.md) only for pre-development critique and hypothesis pressure-testing. Synthetic personas must record source basis and confidence, include a synthetic-not-proof banner, and must never be treated as real customers, market proof, willingness-to-pay evidence, or validation evidence.

Use the [Synthetic Persona Generation Workflow](synthetic-persona-generation-workflow.md) before creating any synthetic persona record. The workflow requires source and privacy gating, separates evidence-backed traits from speculative traits, records source gaps, and blocks generation from sensitive data unless approval and privacy review are recorded.

Use the [Synthetic Persona Simulation Prompt](synthetic-persona-simulation-prompt.md) only after a synthetic persona has been reviewed as a hypothesis. Simulation should challenge problem, offer, message, channel, buying, and MVP assumptions; it must include objections, confidence limits, source basis, and real-world tests, and must never be treated as proof of demand.

Use the [Synthetic Objection And Risk Extraction Workflow](synthetic-objection-risk-extraction-workflow.md) after a synthetic persona simulation to turn objections into validation questions, tests, ignored reasons, or risk-review inputs. Every synthetic objection must map to a real-world validation path or an explicit ignore reason; synthetic objections cannot change ranking or scope without real validation.

Use the [Synthetic Vs Real Interview Comparison Template](synthetic-vs-real-interview-comparison-template.md) only after real customer interview synthesis exists. The template compares synthetic claims, objections, risks, and misses against real evidence; confidence or score updates must come from real interview evidence, never synthetic output alone.
