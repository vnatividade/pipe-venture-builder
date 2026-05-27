# Distribution And Embedded Workflow Prompts

Use this companion prompt set with `validation/venture-validation-framework.md` when an idea needs sharper validation around distribution, workflow insertion, payments, social context, or ecosystem dependency.

This document is inspired by China distribution and superapp patterns, but it is not a China market-entry plan. Do not copy WeChat, Alipay, Douyin, Taobao, or any other platform pattern literally into a Brazil or target-market context without evidence that the same user behavior, trust layer, payment habit, channel access, and regulatory environment exist.

## Purpose

The Pipe should validate where an idea enters real behavior before it becomes a PRD or build request.

This prompt set helps answer:

- where the user first discovers the offer
- which existing workflow or habit the offer enters
- what moment of use creates urgency
- whether payment, trust, or social proof is part of adoption
- whether distribution is plausible without broad paid acquisition or autonomous outreach
- how channel, workflow, timing, and trust affect the Adoption Path
- which assumptions must flow into the PRD and ValidationPlan

These questions are heuristics. They do not count as customer evidence by themselves.

## When To Use

Use this prompt set when:

- the PMF triad has a weak or vague `how to reach them`
- the idea depends on a channel, community, marketplace, platform, partner, or embedded workflow
- the solution might be easier to adopt inside an existing tool, habit, transaction, or operations flow
- the team is preparing validation questions before the scorecard
- a PRD needs a clearer first-channel or moment-of-use boundary

Do not use this prompt set to:

- authorize customer outreach, paid acquisition, billing, external communication, or integrations
- create a China expansion strategy
- justify copying a superapp pattern without local evidence
- convert distribution speculation into market validation
- broaden the MVP into a platform or multi-channel launch

## Relationship To Existing Artifacts

| Artifact | Role | This prompt set adds |
|---|---|---|
| `product/founder-focus.md` | Narrows market, problem, offer, and channel | More precise first-channel and moment-of-use questions |
| `validation/venture-validation-framework.md` | Adds MAYA, 8 Innovation Flavors, and PMF triad | Distribution and embedded-workflow pressure tests |
| `validation/validation-scorecard.md` | Scores evidence quality | Evidence categories for channel reachability, workflow insertion, and willingness to engage |
| `validation/market-validation-before-code-gate.md` | Blocks PRD/build without market evidence | Clearer assumptions to resolve before GO or CONDITIONAL GO |
| `product/prd.md` | Translates validated learning into product decisions | Source fields for channel, workflow, payment, ecosystem, and trust requirements |

## Core Principle

China-style AI and commerce patterns often win by entering daily workflows instead of asking users to adopt isolated products.

For Pipe, the lesson is not "build a superapp." The lesson is to validate whether the first wedge can attach to a real behavior, channel, transaction, or operations moment that already exists in the target market.

## Prompt Set

### 1. Channel Entry

- Where would the first user realistically discover this offer without broad paid acquisition?
- Which channel is already trusted by this ICP?
- Is the channel controlled by the founder, a community, a partner, a platform, or an incumbent?
- What behavior would prove the channel is plausible before code is written?
- What would make this channel inaccessible, expensive, or too slow for a solo-founder MVP?

### 2. Embedded Workflow

- What workflow, tool, inbox, spreadsheet, group chat, form, transaction, or operations ritual already contains the problem?
- What step immediately before the pain creates the best insertion point?
- What step immediately after the pain captures the value of the solution?
- Does the idea require the user to switch contexts, or can it enter a current context?
- Which part of the workflow must remain manual, inspectable, or human-approved at first?

### 3. Moment Of Use

- What event makes the user need this now instead of someday?
- Is the moment recurring, seasonal, urgent, compliance-driven, revenue-linked, or emotionally salient?
- How close is the solution to the moment where pain, payment, or decision authority appears?
- What signal would show repeated moment-of-use demand?
- What would make the timing too rare or too weak for MVP learning?

### 4. Payment Or Value Transfer

- Is payment part of the user journey, or is willingness to pay validated separately?
- Does the user already spend money, budget, time, credits, labor, or reputation in this workflow?
- Who controls payment, budget, approval, or procurement?
- Could payment friction block adoption even if the product works?
- Is billing excluded for now because willingness to pay can be tested manually?

Do not activate billing, pricing collection, payment flows, or paid acquisition unless a separate approved ticket explicitly authorizes it.

### 5. Social, Trust, And Distribution Loops

- Does adoption depend on social proof, referrals, groups, communities, marketplaces, or shared workflow participants?
- Who can introduce the buyer or user without automated outreach?
- What trust signal must exist before the user shares time, data, money, or workflow access?
- Could the product create a useful referral or collaboration loop later?
- What would be unsafe, spammy, or premature to automate?

### 6. Ecosystem And Platform Dependency

- Which existing ecosystem could accelerate distribution or workflow access?
- Which ecosystem could create lock-in, policy risk, rate-limit risk, or substitution risk?
- Can the first test be done manually before integration?
- Is the platform dependency core value, workflow support, infrastructure, or optional enhancement?
- What fallback exists if the platform blocks, prices, changes, or copies the path?

Use `architecture/api-dependency-risk-assessment.md` before treating platform or integration dependency as a PRD or implementation input.

### 7. Local Context Adaptation

- What is the Brazil or target-market equivalent of the behavior observed in China-style distribution?
- Are the relevant trust, payment, messaging, marketplace, regulatory, and buying behaviors actually present locally?
- Which local channel has enough density for a first wedge?
- What local constraint makes a copied superapp pattern misleading?
- What evidence would prove the local adaptation is real?

### 8. Adoption Path

- What is the first low-friction action the user can take before adopting the full product?
- What must the user trust before giving time, data, money, workflow access, or an introduction?
- Which part of the value can be delivered manually to prove the path before software exists?
- What repeated behavior shows the user is moving from curiosity to adoption?
- What friction would break the path even if the core product idea is useful?

## Output Template

Use this summary before the validation scorecard or PRD handoff.

```md
## Distribution And Embedded Workflow Summary

- Idea:
- Target market:
- ICP:

## PMF triad impact
- What to sell:
- To whom:
- How to reach them:
- How this prompt set changed the triad:

## Channel entry
- First channel hypothesis:
- Evidence supporting it:
- Evidence still missing:
- Channel risk:

## Embedded workflow
- Current workflow or habit:
- Moment before the pain:
- Moment after the solution:
- Manual or inspectable boundary:
- Switching friction:

## Moment of use
- Trigger event:
- Recurrence:
- Urgency:
- Repeated-demand signal:

## Payment or value transfer
- Existing spend, budget, time, labor, or reputation cost:
- Buyer or approver:
- Payment assumption:
- Billing status: excluded / manual test / separately approved

## Social, trust, and ecosystem context
- Trust requirement:
- Social or referral loop hypothesis:
- Platform or ecosystem dependency:
- Local adaptation evidence:

## ValidationPlan implications
- Questions to test next:
- Evidence needed before scorecard:
- Actions blocked:

## PRD implications
- Fields to carry forward:
- Requirements not allowed yet:
- Risks to include:
```

## Handoff To ValidationPlan

Carry these items into a ValidationPlan or validation scorecard only as assumptions unless evidence exists:

- first channel hypothesis
- workflow insertion point
- moment-of-use trigger
- payment or value-transfer assumption
- social or trust requirement
- ecosystem or platform dependency
- Adoption Path friction and first action
- local adaptation evidence
- blocked actions

The ValidationPlan should name the evidence needed to confirm or reject each assumption. The scorecard should stay low when distribution, workflow, or payment assumptions are still internal reasoning.

## Handoff To PRD

Carry only sourced decisions into `product/prd.md`.

The PRD should include:

- first channel or access path
- current workflow or workaround
- trigger event
- privacy, trust, or data constraints
- API or platform dependency risk, when relevant
- billing or growth automation as explicit non-goals unless separately approved
- metrics and evidence thresholds tied to actual validation, not inferred platform potential

Do not add superapp, agentic commerce, autonomous outreach, payment collection, or platform integration requirements to a PRD without specific validation evidence and human approval.

## Synthetic Application Checks

Use these checks to confirm the prompts produce practical validation questions. These are examples only; they are not customer evidence.

### B2B thesis - AI receivables follow-up assistant

- Channel entry: founder-led outreach through accounting communities or referrals from fractional CFOs, not paid ads.
- Embedded workflow: enters after an overdue invoice appears in the finance workflow and before a human sends follow-up.
- Moment of use: weekly cash collection review or month-end close pressure.
- Payment or value transfer: existing cost is staff time, delayed cash, and awkward customer communication; billing remains excluded until willingness is validated manually.
- Trust requirement: messages must be inspectable and human-approved before sending.
- Validation question: will finance operators share an anonymized overdue-invoice workflow and review manually drafted follow-up variants before software is built?
- PRD implication: if validated, carry forward human approval, audit trail, and channel evidence; do not add autonomous sending.

### Consumer thesis - Local family activity planner

- Channel entry: parent groups, school communities, local creator partnerships, or neighborhood newsletters.
- Embedded workflow: enters when parents plan weekend activities, school breaks, or rainy-day alternatives.
- Moment of use: Thursday or Friday planning, holiday planning, or unexpected schedule gaps.
- Payment or value transfer: spend may exist through event tickets or subscriptions, but payment handling is out of scope unless separately approved.
- Social loop: recommendations may spread through parent groups only if trust and relevance are high.
- Validation question: will parents repeatedly request a manually curated weekly plan and share which constraints made it useful or irrelevant?
- PRD implication: if validated, carry forward local relevance, timing cadence, and trust constraints; do not assume a marketplace or superapp destination.

### Marketplace thesis - Specialized equipment rental match

- Channel entry: niche operator associations, supplier referrals, WhatsApp groups, or existing broker relationships, depending on target market evidence.
- Embedded workflow: enters when demand exceeds owned capacity or idle equipment needs utilization.
- Moment of use: project planning, emergency replacement, seasonal spike, or quote request.
- Payment or value transfer: budget and transaction authority may be present, but payment flows and escrow are excluded until trust and liquidity are validated.
- Ecosystem dependency: platform or messaging integrations should be deferred until manual matching proves repeated demand on one side.
- Validation question: can one side provide real availability or demand examples and accept a manual match process with clear trust requirements?
- PRD implication: if validated, carry forward side-specific wedge, trust requirements, and matching workflow; do not build a two-sided marketplace upfront.

## Anti-Patterns

- Treating China superapp behavior as a universal product requirement.
- Assuming embedded distribution removes the need for customer discovery.
- Adding payments, referrals, or messaging automation before trust and willingness are validated.
- Calling a channel plausible because a platform has many users.
- Building integrations before manual channel and workflow tests.
- Turning a distribution insight into a broad platform MVP.

## Completion Check

Before moving to scorecard or PRD, confirm:

- the first channel is explicit
- the workflow insertion point is named
- the moment-of-use trigger is named
- payment or value-transfer assumptions are separated from billing implementation
- social, trust, and ecosystem dependencies are explicit
- local context is considered instead of copied from China
- the Adoption Path names a first action and adoption friction
- blocked actions are listed
- evidence gaps are clear
