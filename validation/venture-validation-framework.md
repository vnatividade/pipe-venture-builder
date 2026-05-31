# Venture Validation Framework

Use this framework during validation planning and before the validation scorecard.

This framework adds three upstream lenses to the Pipe validation flow:

- MAYA adoption risk
- 8 Innovation Flavors
- PMF triad

These lenses help shape better validation questions. They do not replace `product/controle-evaluation.md`, `validation/validation-scorecard.md`, or `validation/market-validation-before-code-gate.md`.

## When To Use

Use this framework when:

- an idea has passed founder focus or needs focus refinement
- the team is preparing customer discovery or market research
- the first ICP, offer, or channel is still fuzzy
- a PRD or build request needs clearer upstream validation
- the validation scorecard needs stronger questions before scoring

Do not use this framework to:

- create a rigid idea score
- bypass C.O.N.T.R.O.L.E.
- treat internal assumptions as customer evidence
- justify build work without validation
- expand the MVP into a broad platform

## Relationship To Existing Gates

| Artifact | Role | This framework adds |
|---|---|---|
| `product/founder-focus.md` | Narrows market, problem, offer, and channel | PMF triad language and adoption friction questions |
| `product/controle-evaluation.md` | Tests strategic coherence | More concrete validation prompts for timing, wedge, and defensibility |
| `validation/validation-scorecard.md` | Scores evidence quality | Heuristic inputs before evidence scoring |
| `validation/market-validation-before-code-gate.md` | Blocks downstream build without market evidence | PMF triad specificity before PRD/build |

C.O.N.T.R.O.L.E. remains the strategic filter. This framework only improves the questions asked before evidence is scored.

## MAYA Adoption Lens

MAYA means **Most Advanced Yet Acceptable**.

Use it to test whether a proposed product, workflow, or AI capability is advanced enough to matter but familiar enough to adopt.

### Questions

| Question | Why it matters | Evidence to seek |
|---|---|---|
| What part of the idea is familiar to the user? | Adoption is easier when the interface or workflow maps to existing behavior. | Current workaround, tool, habit, workflow, or language |
| What part is meaningfully better? | The product needs a reason to switch. | Time saved, cost reduced, risk reduced, quality improved, new capability |
| What part may feel too advanced, risky, or hard to trust? | AI features can fail when the user cannot inspect or control them. | Objections, compliance concerns, manual override needs, trust requirements |
| What should be hidden behind a familiar interface first? | Users often buy the result before they care about the technical mechanism. | Preferred workflow, existing UI pattern, manual process |
| What capability can be introduced later after trust exists? | Progressive adoption reduces premature complexity. | Expansion condition, learning threshold, repeated use |

### Output

- Familiar workflow:
- New capability:
- Adoption risk:
- Trust or control requirement:
- Capability deferred until trust exists:

## 8 Innovation Flavors Lens

Use the 8 Innovation Flavors to generate discovery questions, not to prove the idea is good.

| Flavor | Discovery question | Warning |
|---|---|---|
| Digitalize manual processes | What is still done manually, slowly, or with repeated human coordination? | Manual pain alone does not prove willingness to pay. |
| Reduce steps or intermediaries | Which steps, approvals, handoffs, or vendors create friction? | Removing a step can also remove trust or compliance. |
| Use underutilized assets | What capacity, data, inventory, expertise, or access is idle? | Asset availability does not prove demand. |
| Put a new skin on an existing product | What old solution could be repackaged for a neglected user or channel? | Branding alone is weak without distribution or trust. |
| Become the backbone | What infrastructure or workflow layer do many actors depend on? | Infrastructure is often too broad for MVP. |
| Offer as a service | What internal capability could become repeatable service delivery? | Service scope can sprawl without a narrow wedge. |
| Aggregate dispersed information | What data or knowledge is fragmented across sources? | Aggregation needs source quality and update discipline. |
| Create a marketplace | Which supply and demand sides are hard to match today? | Marketplace is usually not a first MVP unless one side is already reachable. |

### Output

- Primary flavor:
- Secondary flavor, if any:
- Manual process or friction observed:
- First narrow wedge:
- Flavor-specific risk:

## PMF Triad

Before PRD or build work, define the PMF triad in plain language.

| Element | Required clarity | Bad answer | Better answer |
|---|---|---|---|
| What to sell | One concrete offer, promise, or job | AI platform for real estate | Automated first-pass rental inspection report |
| To whom | One initial ICP with exclusions | Brokers and property companies | Independent rental brokers handling 20+ listings/month |
| How to reach them | One first channel or access path | Online marketing | Manual outreach through local broker associations |

The PMF triad does not claim product-market fit exists. It defines the market hypothesis that validation must test.

### Output

- What to sell:
- To whom:
- How to reach them:
- Evidence currently supporting the triad:
- Evidence still missing:

## Validation Prompt Set

Use these prompts to prepare customer discovery, research, or validation scorecard work.

### Adoption

- What does the user already understand about this workflow?
- What new behavior are we asking them to trust?
- What must remain manual or inspectable in the first version?
- What would make this feel too advanced or risky?

### Innovation Pattern

- Which of the 8 flavors best explains the opportunity?
- What observable friction supports that flavor?
- What would make this flavor misleading in this market?
- What is the smallest test of this flavor?

### PMF Triad

- What exactly are we selling first?
- Who is the first user or buyer, and who is explicitly excluded?
- How will we reach them without relying on broad paid acquisition or autonomous outreach?
- What behavior would prove the channel is plausible?

### Build Readiness

- What evidence would justify PRD?
- What evidence would justify implementation?
- What evidence would force REFINE or NO-GO?
- What must remain out of scope even if the idea is promising?

### Contradiction Seeking

- What evidence would make the current problem framing weaker?
- Which user behavior would prove the pain is occasional, mild, or already solved well enough?
- Which ICP assumption would break if we weighted the negative signals first?
- What would make the channel hypothesis inaccessible, expensive, slow, or low-trust?
- What would make willingness to pay unlikely even if users like the idea?
- Which part of the idea is being protected by founder preference instead of evidence?
- What synthetic or AI-generated critique is useful only as a hypothesis, and what real-world evidence would be needed to confirm it?

## Handoff To Scorecard

Before using `validation/validation-scorecard.md`, summarize:

- MAYA adoption risk:
- Primary innovation flavor:
- PMF triad:
- Strongest evidence:
- Strongest contradictory evidence:
- Ambiguous or mixed signals:
- Weakest assumption:
- Next evidence needed:

Do not score a category higher because an idea sounds strategically elegant. Score only the evidence quality.

## Synthetic Application Checks

Use these lightweight checks to confirm the framework produces actionable validation questions.

### Example A - Rental inspection assistant

- MAYA: familiar output is an inspection report; risky new behavior is trusting AI-generated observations.
- Primary flavor: digitalize manual processes.
- PMF triad: sell automated first-pass rental inspection reports to independent rental brokers through local broker associations.
- Actionable validation question: will brokers share a sample inspection workflow and review a manually produced AI-assisted report before any software is built?
- Build implication: do not build image analysis until brokers confirm the report format, trust requirements, and current workaround pain.

### Example B - AI legal intake assistant

- MAYA: familiar workflow is intake triage; risky new behavior is relying on AI around legal context.
- Primary flavor: reduce steps or intermediaries.
- PMF triad: sell structured intake summaries to small law firms through founder-led outreach to practice-area communities.
- Actionable validation question: will a lawyer spend time reviewing anonymized sample intakes and identify what must remain human-reviewed?
- Build implication: do not create an autonomous legal agent; validate risk, review boundaries, and willingness to pay for structured summaries first.
