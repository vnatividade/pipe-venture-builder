# Synthetic Persona Schema

Synthetic personas are allowed only for pre-development critique and hypothesis pressure-testing.

They are not real customers. They are not interviews. They are not market proof. They are not willingness-to-pay evidence. They cannot satisfy validation gates or raise validation scorecard categories by themselves.

Canonical schema:

- `schemas/SyntheticPersona.schema.json`

## Purpose

Use synthetic personas to:

- make assumptions explicit
- surface possible objections
- generate interview questions
- pressure-test JTBD, buying context, channel fit, and adoption risk
- identify real-world validation needed

Do not use synthetic personas to:

- replace customer discovery
- claim demand, pain intensity, willingness to pay, PMF, or customer commitment
- create build, PRD, monetization, launch, pricing, billing, or outreach tickets
- decide priority without human review
- store real personal data

## Required Source Basis

Every synthetic persona must record:

- origin Linear ticket or approved artifact
- generation date
- generator role or agent
- source context summary
- source artifacts
- assumptions
- confidence labels
- real-world validation needed

Do not create or use a synthetic persona generated from no source context.

## Synthetic-Not-Proof Banner

Every record must include this banner:

```txt
Synthetic persona for hypothesis pressure-testing only. Not customer evidence.
```

The schema also requires:

- `notCustomerEvidence: true`
- `notValidationEvidence: true`
- `requiresHumanReviewBeforePrioritization: true`

## Required Persona Fields

The schema captures:

- persona label
- persona source label
- role
- segment
- company or customer context
- broad demographic context
- broad firmographic context
- exclusion criteria
- job-to-be-done
- trigger event
- desired outcome
- current workflow
- pain hypotheses
- buying context
- adoption context
- objections and risks
- confidence
- limits
- review status

Broad demographic or firmographic fields must not contain sensitive or identifiable personal data.

## Source Labels

Use one of:

- `interview-informed-hypothesis`
- `research-informed-hypothesis`
- `founder-assumed-hypothesis`
- `ai-generated-hypothesis`
- `mixed-source-hypothesis`

None of these labels convert the persona into customer evidence.

## Evidence And Confidence Rules

Every major claim must have:

- basis type
- source reference
- confidence
- notes
- real-world test needed, when framed as a hypothesis

Allowed basis types:

- `customer_evidence`
- `research_inference`
- `founder_assumption`
- `synthetic_inference`
- `mixed`

Even when a synthetic persona references customer evidence, the synthetic persona itself is not the evidence. Link back to the original source artifact instead.

## Forbidden Uses

The schema requires `mustNotBeUsedFor` values covering:

- `customer_evidence`
- `market_proof`
- `willingness_to_pay_proof`
- `product_market_fit`
- `public_claim`
- `automatic_prioritization`
- `build_ticket_creation`
- `outreach_targeting_without_approval`

## Review Rules

Human review is required before a synthetic persona can influence prioritization.

Review status must be one of:

- `not_reviewed`
- `reviewed_as_hypothesis`
- `rejected`
- `superseded`

Review should check:

- source context exists
- assumptions are labeled
- confidence is not inflated
- no sensitive personal data is stored
- no customer evidence is implied
- real-world validation is named

## Minimal Record Skeleton

```json
{
  "schemaVersion": "0.1.0",
  "personaId": "SP-0001",
  "title": "Example synthetic persona",
  "syntheticNotProof": {
    "banner": "Synthetic persona for hypothesis pressure-testing only. Not customer evidence.",
    "notCustomerEvidence": true,
    "notValidationEvidence": true,
    "requiresHumanReviewBeforePrioritization": true
  },
  "sourceBasis": {
    "originLinearId": "PIP-114",
    "generatedAt": "2026-06-01",
    "generatedBy": "synthetic_persona_validation_agent",
    "sourceContextSummary": "Example only. Replace with linked source artifacts before use.",
    "sourceArtifacts": [
      {
        "artifactType": "icp_profile",
        "pathOrUrl": "validation/icp-profile.md",
        "summary": "ICP hypothesis source.",
        "sourceStrength": "weak"
      }
    ],
    "assumptions": [],
    "forbiddenSourceState": "Do not create or use a synthetic persona generated from no source context."
  }
}
```

The skeleton is intentionally incomplete; a usable record must satisfy the full canonical schema.

## Relationship To Existing Artifacts

- Use `validation/icp-profile.md` as the first ICP hypothesis source.
- Use `validation/persona-ranking-rubric.md` to prevent synthetic personas from outranking real evidence.
- Use `validation/respondent-targeting-and-interview-planner.md` to turn synthetic blind spots into real discovery questions.
- Use `validation/customer-interview-template.md` and `validation/raw-interview-evidence-intake-and-synthesis.md` when real interviews exist.
- Use `validation/validation-scorecard.md` only after evidence strength and score caps are clear.
