# Founder-Led Distribution Playbook

Use this playbook after `growth/distribution-strategy-framework.md` selects one primary channel for one validated product or validation cycle.

This playbook is a planning artifact. It does not authorize customer outreach, community posting, publishing, partnerships, manual sales, paid campaigns, scraping, automated messaging, external communications, billing, or production deployment.

Every external action must have explicit human approval recorded in the relevant Linear ticket, PR, or approved repository artifact before execution.

## Purpose

Founder-led distribution should create learning before scale.

This playbook helps a solo founder define practical, narrow actions for:

- warm outreach
- communities
- content
- partnerships
- manual sales
- feedback capture

The goal is not multi-channel growth. The goal is one approved, measurable learning path tied to validation, MVP scope, and the current product stage.

## Relationship To Existing Artifacts

| Artifact | Role | This playbook adds |
|---|---|---|
| `growth/distribution-strategy-framework.md` | Chooses one primary channel and trust path | Stage-aware founder-led action options |
| `growth/channel-experiment-template.md` | Designs one measurable channel experiment | Draft actions, scripts, and feedback capture inputs |
| `validation/validation-scorecard.md` | Scores evidence quality | Clear mapping from distribution response to validation evidence |
| `product/mvp-scope.md` | Defines smallest ethical test | Keeps distribution tied to one core loop and one riskiest assumption |
| `execution/approval-gates.md` | Defines gated actions | Preserves approval before external contact or publication |

## Stage Gates

| Stage | Allowed by default | Requires approval before action | Blocked by default |
|---|---|---|---|
| Idea intake | Internal channel mapping and assumption listing | Any external message, post, call, or ask | Paid campaigns, automated outreach, public claims |
| Founder focus | Identify warm paths and one possible first channel | Asking anyone outside the project for feedback | Multi-channel launch, scraping, broad prospect lists |
| Validation planning | Draft discovery asks and learning goals | Sending discovery asks or contacting communities | Sales pitch, paid acquisition, pricing collection |
| Validation running | Manually execute approved outreach or community actions | Each external action scope must be approved | Automation, spam, unsupported claims |
| PRD/MVP readiness | Use distribution learning to shape requirements and non-goals | Any new outreach, publishing, or partnership ask | Growth scale-up before MVP evidence |
| First product trial | Run approved narrow channel experiment | Trial invitations, public copy, manual sales, paid pilot | Broad launch, paid campaigns, billing without approval |
| Post-trial learning | Capture responses, objections, and next channel decision | Follow-up contact or expansion | Treating one signal as permission to scale |

## One-Channel Rule

Before using any action in this playbook, confirm:

- target persona is specific
- problem and offer are narrow
- one primary channel is selected
- excluded channels are named
- first conversion or learning metric is defined
- approval state is explicit

Do not execute warm outreach, community posting, content publishing, partnership outreach, manual sales, or follow-up contact across multiple channels at once. If the strategy needs more than one channel, return to `growth/distribution-strategy-framework.md`.

## Channel Action Menu

Use this menu to draft actions. Execution still requires approval.

| Channel | Draft actions | Good first metric | Approval needed |
|---|---|---|---|
| Warm outreach | List known operators, advisors, prior collaborators, or qualified intros; draft a learning-focused ask. | Qualified reply, intro, or willingness to review workflow. | Outreach approval before sending. |
| Communities | Identify one community, rules, moderator constraints, and trust norms; draft a non-promotional learning ask. | Approved post, qualified comment, or permission to ask members. | Community and external-communication approval. |
| Content | Draft one problem-aware note, teardown, guide, or learning artifact tied to validation evidence. | Qualified inbound response or request for manual test. | Publishing and claim review approval. |
| Partnerships | Identify one advisor, consultant, association, agency, or vendor with access to the ICP. | Qualified intro or permission to test a narrow offer. | Partnership/outreach approval. |
| Manual sales | Draft one scoped manual offer based on validated pain and MVP constraints. | Buyer conversation, budget path, or paid-pilot interest. | Sales, external communication, and pricing/billing approval if money is involved. |
| Feedback capture | Prepare response log, objection taxonomy, and learning card before action. | Completed learning update. | Customer data approval when identifiable or sensitive data is captured. |

## Warm Outreach Draft

Use only as a draft. Do not send without approval.

```md
## Warm Outreach Draft

- Target person or segment:
- Relationship path:
- Why this person is relevant:
- Validation artifact linked:
- One learning question:
- One low-friction ask:
- Claim to avoid:
- Data or privacy concern:
- Approval record:

Draft message:

Hi <name>,

I am testing a narrow problem around <problem> for <specific persona>. I am not trying to sell anything yet. I am trying to understand whether this workflow is actually painful and how people handle it today.

Would you be open to <low-friction ask>?

If useful, I can share the exact questions upfront.
```

## Community Draft

Use only as a draft. Do not post without approval.

```md
## Community Draft

- Community:
- Rules reviewed:
- Moderator approval needed: yes/no
- Target persona present: yes/no/unknown
- Learning question:
- Non-promotional framing:
- Claim to avoid:
- Approval record:

Draft post:

I am researching how <specific persona> handles <specific workflow/problem>. I am not promoting a product. I am looking for examples of the current workaround, what makes it painful, and what would make a first-pass solution trustworthy enough to test.

If this is relevant to your work, what is the most frustrating part of <workflow> today?
```

## Content Draft

Use only as a draft. Do not publish without approval.

```md
## Content Draft

- Content type:
- Target persona:
- Problem:
- Evidence linked:
- Claim review needed: yes/no
- Desired learning:
- Approval record:

Draft angle:

What <specific persona> should check before trying to solve <problem> with software:

1. Current workaround
2. Trigger moment
3. Trust requirement
4. Data or privacy boundary
5. Manual test before build
```

## Partnership Draft

Use only as a draft. Do not send without approval.

```md
## Partnership Draft

- Partner type:
- Why partner has ICP access:
- Mutual value hypothesis:
- What is being asked:
- What is explicitly not being asked:
- Approval record:

Draft ask:

I am validating a narrow workflow problem for <ICP>. I think your perspective may help me avoid building the wrong thing. I am not asking for promotion or access to your customers. Could I ask you to review the problem framing and tell me whether this pain appears in your work with <segment>?
```

## Manual Sales Draft

Use only as a draft. Do not send, quote prices, request payment, invoice, or collect payment details without approval.

```md
## Manual Sales Draft

- Buyer:
- User:
- Validated pain:
- Manual offer:
- Value anchor:
- Pricing hypothesis artifact:
- Payment or billing involved: yes/no
- Approval record:

Draft offer:

Based on the workflow you described, I can manually produce <specific output/result> for <narrow scope> so we can test whether the result is useful before building software.

This is a validation offer, not a product launch. Scope, price, payment handling, and any customer data would need explicit approval before proceeding.
```

## Feedback Capture

Capture learning after any approved action.

```md
## Founder-Led Distribution Learning

- Origin ticket:
- Channel:
- Persona:
- Action approved by:
- Action performed:
- Date:
- Primary metric:
- Result:
- Qualified signal:
- Objection:
- Unexpected language:
- Trust or proof gap:
- Data/privacy issue:
- Impact on validation scorecard:
- Impact on distribution strategy:
- Impact on MVP scope:
- Follow-up needed:
- What this does not prove:
```

Do not store identifiable customer data, private customer materials, recordings, transcripts, or sensitive context in the repository unless `validation/customer-data-retention-policy.md` allows it and explicit approval exists.

## GO / NO-GO Rules

| Decision | Condition | Next action |
|---|---|---|
| GO | One approved action produced the predefined learning or conversion signal without unresolved risk. | Capture learning and decide whether to continue the same channel manually. |
| REFINE | Signal is weak, message was unclear, or target persona/channel fit is uncertain. | Update channel hypothesis, message draft, or validation question. |
| NO-GO | Channel creates spam risk, trust risk, unsupported claims, or no qualified signal after the agreed threshold. | Stop this channel and record learning. |
| BLOCKED | Approval, data, privacy, claim, paid spend, billing, or external action gate is unresolved. | Do not execute. Resolve blocker or narrow scope. |

One GO does not authorize scaling, automation, paid acquisition, public launch, billing, or multi-channel expansion.

## Done Criteria

This playbook is ready when:

- every action is tied to one stage and one primary channel
- warm outreach, communities, content, partnerships, manual sales, and feedback capture are covered
- sample scripts are clearly drafts only
- external contact and publishing remain approval-gated
- spam, automated outreach, and paid campaigns are blocked by default
- feedback capture links back to validation, distribution strategy, MVP scope, and Linear
