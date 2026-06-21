# Planning Schema Outlines

This document defines lightweight planning schema outlines for the earliest Pipe Venture Builder planning artifacts.

It is intentionally not a full JSON Schema implementation. PIP-151 authorizes minimum outlines, source mappings, and deferred fields only. Full machine-readable contracts for `IdeaBrief`, `ValidationPlan`, `PRD`, or `ExecutionPlan` require a later approved Linear ticket.

Use this with:

- `architecture/canonical-schema-policy.md`
- `product/product-context.md`
- `product/founder-focus.md`
- `product/controle-evaluation.md`
- `validation/venture-validation-framework.md`
- `validation/validation-scorecard.md`
- `validation/market-validation-before-code-gate.md`
- `product/prd.md`
- `product/mvp-scope.md`
- `execution/core-pipeline-map.md`

## Scope

These outlines define the minimum fields future agents should preserve when translating Markdown planning artifacts into structured outputs.

They do not replace existing repository templates. The Markdown artifacts remain the operational source of truth until dedicated schema implementation tickets create and validate full schemas.

## Common Rules

All planning records should preserve these common fields:

| Field | Required | Source Mapping | Notes |
|---|---|---|---|
| `schemaVersion` | Yes | `architecture/canonical-schema-policy.md` | Use `0.1.0` for first structured records. |
| `artifactPath` | Yes | Repository path | Path to the source Markdown artifact. |
| `linearId` | No | Assigned Linear ticket | Required only when the record is produced from a ticket. |
| `owner` | Yes | Source artifact metadata | Human or agent accountable for the artifact. |
| `createdAt` | Yes | Source artifact metadata | ISO date. |
| `sourceArtifacts` | Yes | Links in source artifact | Must be source artifacts, not chat memory. |
| `evidenceBoundary` | Yes | Product/validation templates | Separate evidence, assumptions, and unknowns. |
| `sensitiveDataPolicy` | Yes | Product/validation privacy sections | Must state whether sensitive/customer data is involved. |
| `approvalStatus` | Yes | Gate/approval sections | Required before downstream build, external action, billing, or outreach. |

The artifact type is implied by the future schema title/file name, such as `IdeaBrief.schema.json`, rather than by an additional required `schemaName` property.

Do not encode invented customers, metrics, revenue, integrations, willingness to pay, market proof, or validation results.

## IdeaBrief Outline

### Purpose

Capture one focused idea hypothesis before deeper validation or PRD work.

### Primary Source Artifacts

- `product/product-context.md`
- `product/founder-focus.md`
- `product/controle-evaluation.md`

### Required Fields

| Field | Source Mapping | Notes |
|---|---|---|
| `ideaName` | `product/product-context.md` Metadata | Product or idea name. |
| `currentStage` | `product/product-context.md` Stage | Must match one of the repository stages. |
| `oneSentencePromise` | `product/product-context.md` Idea Summary | Promise, not proof. |
| `targetMarket` | `product/founder-focus.md` One Market | One initial market only. |
| `specificSegment` | `product/founder-focus.md` One Market | Must not be broad or multi-audience. |
| `primaryProblem` | `product/founder-focus.md` One Problem | One problem only. |
| `proposedOffer` | `product/founder-focus.md` One Offer | Concrete first promise, not a platform. |
| `primaryChannelHypothesis` | `product/founder-focus.md` One Channel | One channel hypothesis only. |
| `antiGoals` | `product/founder-focus.md` Anti-Goals | Binding exclusions. |
| `assumptions` | `product/product-context.md` Assumptions | Each assumption needs validation needed and confidence. |
| `evidenceLinks` | `product/product-context.md` Evidence Links | May be empty only if clearly marked as assumptions-only. |
| `controleVerdict` | `product/controle-evaluation.md` Verdict | `Attack`, `Refine`, `Pivot`, `Kill`, or `not_evaluated`. |
| `nextGate` | `product/product-context.md` GO / NO-GO | Next required repository artifact or blocker. |

### Markdown-Only For Now

- Narrative founder context
- Free-form market notes
- Long-form rationale
- Private/local founder notes

### Deferred Fields

- Scored market sizing
- Competitive landscape model
- Pricing model
- Automated channel scoring
- Customer evidence normalization

## ValidationPlan Outline

### Purpose

Define what must be learned before PRD, MVP scope, architecture, implementation, growth, or monetization work.

### Primary Source Artifacts

- `validation/venture-validation-framework.md`
- `validation/validation-scorecard.md`
- `validation/market-validation-before-code-gate.md`
- `validation/icp-profile.md`
- `product/controle-evaluation.md`

### Required Fields

| Field | Source Mapping | Notes |
|---|---|---|
| `linkedIdeaBrief` | IdeaBrief output or source artifacts | Link to the idea context this validates. |
| `controleVerdict` | `product/controle-evaluation.md` Verdict | Must be `Attack` or `Refine` with human approval before validation moves forward. |
| `mayaAdoptionRisk` | `validation/venture-validation-framework.md` MAYA Adoption Lens | Heuristic, not evidence by itself. |
| `innovationFlavor` | `validation/venture-validation-framework.md` 8 Innovation Flavors | Primary flavor and risk. |
| `pmfTriad` | `validation/venture-validation-framework.md` PMF Triad | What to sell, to whom, and how to reach. |
| `icpHypothesis` | `validation/icp-profile.md` Segment Definition | ICP remains a hypothesis until sourced. |
| `validationQuestions` | `validation/venture-validation-framework.md` Validation Prompt Set | Questions to answer before scoring. |
| `evidenceNeeded` | `validation/validation-scorecard.md` Evidence Rules and Scorecard | Map each category to needed evidence. |
| `evidenceSourcesAllowed` | `validation/market-validation-before-code-gate.md` Evidence Quality Rules | Distinguish behavior, quotes, research, and assumptions. |
| `blockedActions` | `validation/market-validation-before-code-gate.md` Gate Decision | Build/growth/monetization actions blocked until gate allows them. |
| `gateDecision` | `validation/market-validation-before-code-gate.md` Gate Decision | `GO`, `CONDITIONAL GO`, `REFINE`, `NO-GO`, or `NOT APPLICABLE`. |
| `approvalRecord` | `validation/market-validation-before-code-gate.md` Human Approval Rules | Required for GO/CONDITIONAL GO downstream action. |

### Markdown-Only For Now

- Interview scripts
- Discovery notes
- Free-form research synthesis
- Customer-language excerpts
- Exact quotes and sensitive context governed by retention policy

### Deferred Fields

- Automated survey design
- Experiment analytics schema
- Interview transcript schema
- Statistical confidence model
- Automated customer-data retention workflow

## PRD Outline

### Purpose

Translate validated learning into product decisions without inventing evidence, metrics, integrations, or roadmap commitments.

### Primary Source Artifacts

- `product/prd.md`
- `product/mvp-scope.md`
- `validation/validation-scorecard.md`
- `validation/market-validation-before-code-gate.md`
- `validation/icp-profile.md`
- `architecture/proprietary-data-moat-strategy.md`
- `architecture/api-dependency-risk-assessment.md`

### Required Fields

| Field | Source Mapping | Notes |
|---|---|---|
| `productName` | `product/prd.md` Required Inputs | Product or idea name. |
| `requiredInputs` | `product/prd.md` Required Inputs | Links to focus, C.O.N.T.R.O.L.E., validation, ICP, MVP, and risk artifacts. |
| `validationDecision` | `product/prd.md` Required Inputs | Must be GO or approved CONDITIONAL GO. |
| `problemEvidence` | `product/prd.md` Problem Evidence | Evidence table and remaining assumptions. |
| `pmfTriad` | `product/prd.md` PMF Triad | Specific and sourced. |
| `icpBoundary` | `product/prd.md` ICP And User Boundary | Includes excluded users/segments. |
| `mvpCoreLoop` | `product/prd.md` MVP Core Loop | Copied from `product/mvp-scope.md`. |
| `goals` | `product/prd.md` Goals | Must connect to evidence and MVP loop. |
| `nonGoals` | `product/prd.md` Non-Goals | Binding exclusions. |
| `metricsAndThresholds` | `product/prd.md` Metrics And Evidence Thresholds | No invented baselines. |
| `userStories` | `product/prd.md` User Stories | Tied to core loop. |
| `functionalRequirements` | `product/prd.md` Functional Requirements | Must link to story or evidence. |
| `nonFunctionalRequirements` | `product/prd.md` Non-Functional Requirements | Must include risk or constraint. |
| `statesAndEdgeCases` | `product/prd.md` States And Edge Cases | Minimum states for architecture planning. |
| `risks` | `product/prd.md` Risks | P0/P1 must be handled or blocking. |
| `acceptanceCriteria` | `product/prd.md` Acceptance Criteria | PRD readiness checklist. |

### Markdown-Only For Now

- Working Backwards narrative
- Long-form product rationale
- Launch narrative
- FAQ-style product thinking
- Free-form risk discussion

### Deferred Fields

- Full event taxonomy
- Detailed analytics plan
- UI state machine
- API contract
- Pricing and billing model
- Growth automation plan

## ExecutionPlan Outline

### Purpose

Translate approved product/architecture scope into a sequenced execution plan without replacing Linear as the execution source of truth.

### Primary Source Artifacts

- `execution/core-pipeline-map.md`
- `execution/tactical-execution-plan.md`
- `execution/linear-governance-model.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/ticket-type-field-matrix.md`
- `execution/parallel-execution-governance.md`
- `execution/agent-readiness-validator.md`
- `product/mvp-scope.md`
- `product/prd.md`

### Required Fields

| Field | Source Mapping | Notes |
|---|---|---|
| `linkedPrd` | `product/prd.md` Handoff | PRD source or blocker. |
| `linkedMvpScope` | `product/mvp-scope.md` Handoff | MVP source or blocker. |
| `pipelinePhase` | `execution/core-pipeline-map.md` Phase Map | Current phase and allowed next step. |
| `gateStatus` | `execution/core-pipeline-map.md` Gates That Block Implementation | Must identify blockers before build tickets. |
| `tacticalExecutionPlan` | `execution/tactical-execution-plan.md` | Required, lightweight, or not applicable with reason before development work. |
| `linearProject` | `execution/core-pipeline-map.md` Linear project confirmation | Confirmed project or blocker. |
| `ticketSequence` | `execution/linear-governance-model.md` and ticket templates | Ordered tickets with dependencies. |
| `ticketStoryBreakdown` | `execution/tactical-execution-plan.md` Ticket And Story Breakdown | Ordered slices with owner, write set, dependencies, acceptance checks, and evidence required. |
| `adrDecisionPath` | `execution/tactical-execution-plan.md` ADR And Decision Path | ADR/RFC required, not required, or blocker. |
| `parallelizationPlan` | `execution/parallel-execution-governance.md` | Explicit yes/no/partial by ticket or domain. |
| `ownerAgent` | `execution/ticket-type-field-matrix.md` Suggested Owner/Agent | Codex, Claude Code, human, or future orchestrator. |
| `branchAndPrRules` | `execution/ticket-pr-handoff-system.md` | One branch and one PR per ticket. |
| `validationPlan` | `execution/tactical-execution-plan.md`, `execution/agent-readiness-validator.md`, and ticket template | Checks to run before merge. |
| `deliveryEvidencePlan` | `execution/tactical-execution-plan.md` and `schemas/DeliveryEvidence.schema.json` | DeliveryEvidence required, optional, or not applicable with reason. |
| `documentationPlan` | `execution/tactical-execution-plan.md` Documentation And Knowledge Updates | Docs, ADR/KDR/DAR/LearningRecord, and handoff updates. |
| `reviewAndMergePolicy` | `execution/ticket-pr-handoff-system.md` | Review required; P0/P1 fixed before merge. |
| `handoffRequirements` | `execution/ticket-pr-handoff-system.md` | Linear delivery update fields. |
| `followUpCriteria` | `execution/linear-governance-model.md` | When to create follow-up tickets. |

### Markdown-Only For Now

- Long-form execution rationale
- Agent conversational handoffs
- Human planning notes
- Manual prioritization discussion

### Deferred Fields

- Automated orchestrator dispatch plan
- Machine-generated dependency graph
- Worktree allocation model
- CI status aggregation
- Runtime execution telemetry
- Automated Linear state transitions

## Current Artifact Mapping Check

| Outline | Existing Artifacts Mapped | Mapping Status | Notes |
|---|---|---|---|
| IdeaBrief | `product/product-context.md`, `product/founder-focus.md`, `product/controle-evaluation.md` | Mapped | No standalone `IdeaBrief.schema.json` yet. |
| ValidationPlan | `validation/venture-validation-framework.md`, `validation/validation-scorecard.md`, `validation/market-validation-before-code-gate.md`, `validation/icp-profile.md` | Mapped | Interview/test-card details remain Markdown-only. |
| PRD | `product/prd.md`, `product/mvp-scope.md`, validation and architecture risk artifacts | Mapped | PRD remains the canonical operating template. |
| ExecutionPlan | `execution/core-pipeline-map.md`, `execution/tactical-execution-plan.md`, `execution/linear-governance-model.md`, `execution/ticket-pr-handoff-system.md`, `execution/parallel-execution-governance.md` | Mapped | Linear remains execution state source of truth. |

## What Stays Markdown-Only For Now

- Exact customer interview notes and quotes
- Customer-language memory entries
- Working Backwards narrative
- Long-form PRD rationale
- Risk-review discussion
- Architecture tradeoff essays
- Human approvals and nuanced exceptions
- Exploratory research synthesis
- Conversation-derived handoff notes

These surfaces need judgment, source review, and privacy controls before they become strict machine-readable contracts.

## Future Schema Implementation Criteria

Create full JSON Schemas only when at least one of these is true:

- two or more agents need to emit or consume the artifact in a stable format
- a command, skill, MCP, or runtime system needs structured validation
- a Linear ticket requires schema-valid output as acceptance criteria
- orchestration needs dependency or gate information in machine-readable form
- repeated drift appears between Markdown templates and generated outputs

Until then, these outlines are the minimum contract.
