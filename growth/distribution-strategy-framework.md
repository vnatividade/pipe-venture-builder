# Distribution Strategy Framework

Use this framework to choose one primary distribution channel for one validated product before expanding into additional channels.

Use it with `product/founder-focus.md`, `validation/icp-profile.md`, `validation/validation-scorecard.md`, `product/mvp-scope.md`, `research/market-research-workflow.md`, `research/research-decision-approval-gates.md`, and `execution/approval-gates.md`.

## Boundary

This framework is a planning artifact. It does not authorize customer outreach, paid ads, growth automation, external communications, multi-channel campaigns, scraping, billing, or production deployment.

Distribution work may begin only after the target persona is clear and validation evidence shows a real problem, credible MVP value, and an approved next external action.

Paid growth, automated outreach, public campaigns, and external messaging require explicit human approval.

## Gate Conditions

Use this framework only when:

- MVP scope exists
- ICP profile exists
- validation scorecard has GO or approved CONDITIONAL GO
- target persona is specific
- one primary problem and offer are defined
- one primary channel is being evaluated
- evidence of demand or engagement exists
- human approval exists before any external execution

Do not proceed when:

- there is no evidence of demand
- target persona is unclear
- the idea still has Pivot or Kill risk in C.O.N.T.R.O.L.E.
- MVP scope is missing or broad
- the strategy depends on multiple channels at once
- paid ads or automated outreach are required before validation
- trust, privacy, compliance, or claims risk is unresolved

## One-Channel Rule

Choose exactly one primary channel for the next distribution cycle.

Allowed supporting work:

- research the channel
- prepare manually reviewed message hypotheses
- identify trust path and proof needs
- define the first conversion metric
- define a narrow manual test after approval

Not allowed by default:

- launching multiple channels
- paid campaigns
- automated outbound
- public announcements
- broad content calendars
- influencer or partner outreach
- scraping prospect lists
- publishing unsupported claims

Expansion requires evidence that the first channel is working and a new approval decision.

## Channel Hypothesis Fields

Every channel hypothesis must include:

- target persona
- current validation evidence
- channel name
- channel type
- why this channel reaches the persona
- trust path
- proof needed
- first manual action
- first conversion metric
- expected learning
- approval state
- risks and exclusions

## Channel Types

| Channel type | Examples | Default stance |
|---|---|---|
| Founder network | Warm intros, known operators, advisors, prior collaborators. | Preferred when relevant and approval exists. |
| Manual customer discovery | Approved direct interviews, referrals, manually selected prospects. | Allowed only with outreach approval. |
| Community | Forums, Slack/Discord groups, professional groups, events. | Requires community rules review and external-communication approval. |
| Search intent | Problem-aware searches, workaround queries, comparison searches. | Useful for research and content hypotheses; SEO execution needs separate approval. |
| Content | Founder posts, guides, teardown, newsletter, case study. | Requires claim review before publishing externally. |
| Partnerships | Advisors, consultants, agencies, vendors, associations. | Requires human approval before outreach. |
| Product-led loop | Invite, share, referral, collaboration loop in MVP. | Requires validated MVP scope and risk review before implementation. |
| Paid acquisition | Search/social ads, sponsorships, paid communities. | Blocked by default; explicit paid growth approval required. |

## Reachability Assessment

Assess whether the channel can reach the target persona without forcing premature scale.

| Factor | Question | Rating | Evidence |
|---|---|---|---|
| Persona concentration | Does the target persona gather or search in this channel? | Low / Medium / High |  |
| Founder access | Can the founder reach the persona manually and credibly? | Low / Medium / High |  |
| Permission fit | Is participation allowed without spam or rule violations? | Low / Medium / High |  |
| Timing fit | Does the channel surface the problem near the trigger moment? | Low / Medium / High |  |
| Trust path | Can trust be built before asking for action? | Low / Medium / High |  |
| Learning speed | Can the channel generate useful evidence quickly? | Low / Medium / High |  |
| Risk | Could this channel create claim, privacy, compliance, or brand risk? | Low / Medium / High |  |

If reachability is Low and paid acquisition is the only path, mark the channel as blocked until explicit paid growth approval.

## Trust Path

Define how the persona can move from awareness to a safe first action.

Required fields:

- why the persona would trust the founder or product
- what proof is needed before asking for action
- what claim must be avoided or narrowed
- what sensitive topic needs review
- what first action is low-risk for the persona
- what would feel spammy, misleading, or premature

Proof examples:

- customer language from approved discovery
- observed workflow or workaround
- manual trial result
- credible before/after artifact
- domain-specific explanation
- clear limitation or anti-claim

Do not invent proof, customers, metrics, revenue, integrations, or validation.

## First Conversion Metric

Choose one first conversion metric for the channel cycle.

Good metrics:

- qualified reply from target persona
- scheduled discovery call
- permission to inspect workflow
- request for manual test
- repeated engagement from ICP
- intro to another qualified persona
- willingness to share context, data sample, or time after approval

Avoid:

- impressions
- likes
- generic traffic
- broad waitlist signups without qualification
- synthetic persona scores
- vanity engagement

The metric must map to the validation scorecard or MVP scope evidence threshold.

## Template

```md
# Distribution Strategy - <product / persona / channel>

## Metadata

- Origin ticket:
- Owner:
- Date:
- Product phase:
- Approval state:
- Human approval before external execution: yes/no

## Required Inputs

- ICP profile:
- Validation scorecard result:
- MVP scope:
- Founder focus:
- Research or market evidence:
- Customer evidence:

## One-Channel Decision

- Target persona:
- Primary problem:
- Offer or promise:
- Selected primary channel:
- Channel type:
- Channels intentionally excluded:
- Reason for one-channel focus:

## Evidence Check

| Evidence needed | Source | Confidence | Gap |
|---|---|---|---|
| Persona clarity |  | Low / Medium / High |  |
| Demand or pain evidence |  | Low / Medium / High |  |
| MVP value credibility |  | Low / Medium / High |  |
| Channel reachability |  | Low / Medium / High |  |
| Trust/proof path |  | Low / Medium / High |  |

## Channel Hypothesis

- Why this channel reaches the persona:
- Trigger moment:
- Trust path:
- Proof needed:
- First manual action:
- First conversion metric:
- Expected learning:
- What would falsify this channel:

## Reachability Assessment

| Factor | Rating | Evidence | Risk |
|---|---|---|---|
| Persona concentration | Low / Medium / High |  |  |
| Founder access | Low / Medium / High |  |  |
| Permission fit | Low / Medium / High |  |  |
| Timing fit | Low / Medium / High |  |  |
| Trust path | Low / Medium / High |  |  |
| Learning speed | Low / Medium / High |  |  |
| Risk | Low / Medium / High |  |  |

## Approval And Safety

- External execution approved: yes/no
- Paid growth involved: yes/no
- Automated outreach involved: yes/no
- Sensitive claims involved: yes/no
- Customer or private data involved: yes/no
- Approval source:
- Blocker:

## Decision

- Decision: Proceed manually / Refine channel / Blocked / Defer
- Rationale:
- Next test:
- Owner:
- Done condition:
- Follow-up ticket needed:
```

## Expansion Rule

Do not add a second channel until:

- first channel result is recorded
- first conversion metric is evaluated
- learning is captured in `knowledge/` or Linear
- validation scorecard or MVP evidence threshold is updated when relevant
- channel risk is reviewed
- human approval exists for expansion

Expansion should state what remains paused or removed. More channels should not become a substitute for sharper positioning.

## Paid Growth Gate

Paid growth is blocked by default.

Explicit approval is required before:

- running ads
- sponsoring content or communities
- paying for acquisition tools
- collecting payment or pricing intent through paid flows
- scaling spend
- optimizing campaigns
- automating audience creation

If a channel requires paid spend to learn anything useful, mark it as `Blocked` or create a separate approval follow-up.

## Done Criteria

This framework is complete when:

- one primary channel is required before expansion
- target persona, channel hypothesis, reachability, trust path, proof, and first conversion metric are explicit
- validation evidence is required before external execution
- paid growth and automated outreach are gated
- multi-channel campaigns are out of scope by default
- human approval is required before external execution
