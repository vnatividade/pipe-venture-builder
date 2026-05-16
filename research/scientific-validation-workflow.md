# Scientific Validation Workflow

This workflow defines how to evaluate technical, scientific, medical, behavioral, or research-backed claims before they influence product decisions, public wording, or validation thresholds.

Use it with `.codex/agents/research-validation-specialization.md`, `research/research-orchestrator-workflow.md`, `execution/risk-reviewer-matrix-lite.md`, `execution/approval-gates.md`, and `product/prd.md`.

## Boundary

This workflow is a triage and evidence-quality process. It is not medical, legal, financial, compliance, privacy, security, scientific, or professional advice. It does not claim regulatory compliance or verified scientific truth.

No public claim, regulated claim, clinical/legal/financial conclusion, customer-facing promise, or product requirement should rely on this workflow without the required human or expert review.

## When To Use

Use this workflow when:

- a product assumption depends on scientific, technical, medical, behavioral, or research-backed evidence
- a PRD, MVP scope, landing copy, or sales material includes a claim that sounds evidence-backed
- a source summary may be too weak, stale, indirect, or overgeneralized
- the claim could affect safety, money, compliance, privacy, security, health, legal exposure, or customer trust
- expert review may be needed before the claim is used externally

Do not use this workflow to:

- give professional advice
- approve public claims by itself
- treat research summaries as verified advice
- make clinical, legal, financial, compliance, safety, or security conclusions
- bypass risk review or human review

## Inputs

Required:

- Origin ticket or artifact:
- Exact claim:
- Intended use:
- Audience:
- Product phase:
- Source list:
- Sensitive domain flag:
- Approval state:

Optional:

- Existing research synthesis:
- Related PRD or MVP text:
- Regulatory, safety, privacy, or compliance concern:
- Known contradictions:
- Professional reviewer or domain expert:

## Step 1. Extract Claims

Break broad wording into testable claims.

| Claim type | Example pattern | Review need |
|---|---|---|
| Mechanism claim | "X causes Y" or "This method improves Z." | Scientific evidence and applicability review. |
| Outcome claim | "Users reduce cost, risk, time, errors, symptoms, or losses." | Evidence strength, measurement basis, and scope. |
| Comparative claim | "Better, safer, faster, more accurate, or more compliant than alternatives." | Direct comparison evidence and claim wording review. |
| Regulated claim | Health, medical, legal, financial, compliance, safety, privacy, or security wording. | Expert/human review and risk reviewer escalation. |
| Implementation claim | "The system can detect, predict, validate, secure, or automate." | Technical evidence, limitations, and failure modes. |

For each claim, record:

- exact text
- implied promise
- intended audience
- decision it influences
- sensitive domain: yes/no
- source support status

## Step 2. Classify Source Tiers

Use the strongest available source tier, but record limitations.

| Tier | Source type | Typical use | Limit |
|---|---|---|---|
| Tier 1 | Systematic reviews, meta-analyses, standards bodies, official guidance, primary peer-reviewed studies with clear methods. | Strongest basis for scientific or technical evidence assessment. | Still may not apply to the product, population, geography, or workflow. |
| Tier 2 | Expert consensus, reputable technical docs, credible institutional reports, high-quality benchmark studies. | Useful for technical assumptions and professional context. | May be indirect or not independently replicated. |
| Tier 3 | Single studies, preprints, vendor docs, blog posts with methods, public benchmarks, case studies. | Hypothesis support or implementation context. | Requires caution; may be biased, narrow, stale, or unreviewed. |
| Tier 4 | News, summaries, forums, social posts, AI summaries, unsourced claims, internal opinion. | Discovery input only. | Not enough for sensitive claims or product promises. |

AI-generated summaries are never source evidence by themselves. They may only point to sources that must be checked directly.

## Step 3. Assess Evidence Quality

Evaluate each claim-source pair.

| Dimension | Question | Rating |
|---|---|---|
| Source quality | Is the source credible, dated, and methodologically clear? | Low / Medium / High |
| Directness | Does the source evaluate this exact claim, population, setting, and outcome? | Low / Medium / High |
| Recency | Is the source current enough for the claim domain? | Current / Dated / Stale / Unknown |
| Replication | Is there more than one independent source? | None / Partial / Strong |
| Applicability | Does the evidence apply to the intended product, ICP, geography, and workflow? | Low / Medium / High |
| Contradiction | Are there credible conflicting sources or unresolved caveats? | None / Some / Material |
| Risk if wrong | Would an incorrect claim affect safety, money, legal/privacy/security posture, or customer trust? | Low / Medium / High |

If risk if wrong is High, require risk_reviewer and human or expert review before use.

## Step 4. Assign Claim Status

| Status | Meaning | Allowed use |
|---|---|---|
| Supported with limits | Strong enough sources support narrow wording with clear limits. | Internal decision support; external use still needs review when sensitive. |
| Plausible but unproven | Evidence points in a direction but directness, replication, or applicability is incomplete. | Hypothesis or validation question only. |
| Contradicted or uncertain | Credible conflicts, weak methods, stale sources, or poor fit. | Do not use as product promise. Record uncertainty. |
| Expert review required | Sensitive, regulated, high-impact, or outside repository competence. | Blocked for decision/public use until reviewed. |
| Unsupported | No adequate source trail. | Remove, rewrite, or treat as assumption. |

## Step 5. Rewrite Or Block Claims

For every claim, choose one:

- keep with narrower wording
- mark as internal hypothesis
- move to validation question
- escalate to risk_reviewer
- require expert/human review
- remove from customer-facing or decision-critical use

Avoid:

- absolute wording such as "proves", "guarantees", "certifies", "safe", "compliant", or "clinically validated"
- implying medical, legal, financial, compliance, privacy, or security advice
- presenting one source as universal truth
- hiding limitations in footnotes or comments

## Step 6. Professional Review Flags

Flag expert or explicit human review when any item is true:

- medical, health, mental health, clinical, legal, financial, compliance, safety, privacy, or security claim
- claim could influence customer behavior in a high-impact domain
- source evidence is Tier 3 or Tier 4 for a sensitive claim
- source population, geography, or context differs materially from the intended ICP
- claim affects pricing, liability, trust, data handling, or public positioning
- contradiction is material
- reviewer cannot determine risk from repository artifacts

Sensitive flagged claims are blocked for public use until reviewed.

## Step 7. Citation Requirements

Every accepted claim must include:

- source title
- source URL or repository artifact path
- publication date or access date
- source tier
- claim supported
- exact limitation
- confidence
- review status

Do not cite summaries without checking the underlying source. Do not quote long passages. Summarize narrowly and link the source.

## Output Template

```md
# Scientific Validation - <claim or artifact>

## Metadata

- Origin ticket:
- Owner:
- Date:
- Artifact reviewed:
- Intended use:
- Audience:
- Approval state:

## Claim Inventory

| Claim ID | Exact claim | Claim type | Sensitive domain | Intended use | Source support status |
|---|---|---|---|---|---|
| C-001 |  | Mechanism / Outcome / Comparative / Regulated / Implementation | yes/no |  | Supported / Partial / Missing |

## Evidence Review

| Claim ID | Source | Tier | Date | Directness | Applicability | Contradiction | Risk if wrong | Confidence |
|---|---|---|---|---|---|---|---|---|
| C-001 |  | Tier 1 / 2 / 3 / 4 |  | Low / Medium / High | Low / Medium / High | None / Some / Material | Low / Medium / High | Low / Medium / High |

## Claim Decision

| Claim ID | Status | Allowed wording or action | Expert/human review required | Risk reviewer needed | Notes |
|---|---|---|---|---|---|
| C-001 | Supported with limits / Plausible but unproven / Contradicted or uncertain / Expert review required / Unsupported |  | yes/no | yes/no |  |

## Required Disclaimers Or Limits

- This review is not professional advice:
- What the evidence does not prove:
- Where the claim cannot be used:
- Human or expert review blocker:

## Handoff

- Next owner:
- Artifact to update:
- Claim to remove or rewrite:
- Follow-up ticket needed:
- Knowledge update needed:
```

## Human And Expert Review Gate

Require explicit human or expert review before:

- making medical, legal, financial, compliance, privacy, security, safety, or regulated claims
- using scientific claims in public copy, sales material, investor material, PRD commitments, or customer-facing promises
- using research to justify high-impact product behavior
- accepting contradictory or weak evidence for a sensitive claim
- storing or processing sensitive customer, production, health, legal, financial, or confidential data

If review is missing, mark the claim as blocked for public or decision-critical use.

## Done Criteria

The scientific validation workflow is complete when:

- claims are extracted into explicit claim IDs
- every claim has a source tier or is marked unsupported
- uncertainty, contradiction, recency, and applicability are visible
- sensitive or regulated claims are flagged for expert/human review
- no research summary is treated as verified advice
- allowed wording is narrowed or the claim is blocked
- risk_reviewer handoff is named for high-impact claims
