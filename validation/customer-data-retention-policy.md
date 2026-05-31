# Customer Data Retention Policy

This policy defines how this repository handles customer discovery data before real interviews, quotes, recordings, or sensitive customer context are stored.

It is an operating policy for founder and agent workflows. It is not a legal compliance claim and does not assert GDPR, HIPAA, SOC 2, or other regulatory compliance.

## Purpose

Customer discovery should create useful validation evidence without turning the repository into a store of private customer data.

Use this policy when capturing:

- customer interview notes
- exact customer quotes
- ICP evidence
- customer-language snippets
- objections, workflows, and sensitive business context
- recordings or transcripts
- follow-up notes from discovery calls

## Data Categories

| Category | Examples | Repository Treatment |
|---|---|---|
| Public template data | Blank templates, synthetic examples clearly marked as examples, generic process guidance | May live in the repository. |
| Anonymized validation evidence | Segment-level notes, anonymized quotes, non-identifying workflow patterns | May live in the repository when it is useful and minimally necessary. |
| Identifiable customer data | Names, emails, company identifiers, direct quotes tied to a person, recordings, transcripts | Do not store in the repository without explicit approval and a retention reason. |
| Sensitive customer context | Credentials, payment details, health data, legal data, confidential business records, private customer files | Do not store in the repository. Stop and request approval before handling. |

## Storage Rules

- Store public templates and reusable guidance in the repository.
- Store only anonymized, minimum-useful validation evidence in repository artifacts.
- Use participant labels instead of names, such as `P01`, `ICP-A-02`, or `Ops lead, anonymized`.
- Keep identifiable interview notes, recordings, transcripts, and raw customer materials outside the repository unless explicit approval says otherwise.
- Record the storage location in the interview artifact when private notes exist outside the repository.
- Do not store secrets, credentials, payment details, health data, legal data, private files, or confidential customer records in the repository.

## Anonymization Rules

Before adding discovery evidence to repository artifacts:

- remove names, emails, phone numbers, addresses, and account identifiers
- remove company names unless explicit approval permits naming the company
- replace exact titles or roles that identify a person with broader role labels
- generalize confidential workflows when exact details would reveal the customer
- separate exact quotes from synthesis
- mark confidence and source artifacts without exposing private identity

If anonymization would remove the evidence value, keep the raw detail private and summarize the validated pattern in the repository.

## Retention Rules

Use the shortest retention that still supports validation.

| Data Type | Default Retention | Deletion Trigger |
|---|---|---|
| Blank templates and policies | Keep while useful | Delete or revise when obsolete. |
| Anonymized repository evidence | Keep while it supports active validation, decisions, or learning | Delete or archive when the product direction changes or evidence is no longer needed. |
| Private interview notes | Keep only while needed for the active validation cycle | Delete after synthesis, decision, or follow-up completion unless approval extends retention. |
| Recordings and transcripts | Do not retain by default | Delete after synthesis unless explicit approval defines a retention reason and review date. |
| Sensitive customer context | Do not retain | Delete immediately if captured accidentally and document the incident or blocker. |

Every retained private artifact should have:

- owner
- storage location
- approval source
- retention reason
- review or deletion date
- deletion owner

## Deletion Expectations

Delete customer discovery data when:

- the participant requests deletion
- the validation cycle ends and raw notes are no longer needed
- the evidence has been synthesized into anonymized repository artifacts
- the data was captured without required approval
- the data is sensitive and should not have been stored
- the project is paused, killed, or materially changes direction

When deleting private artifacts, update the related Linear ticket or repository artifact with a non-sensitive note such as: `Raw notes deleted after anonymized synthesis`.

## Approval Requirements

Explicit approval is required before:

- recording a customer conversation
- storing recordings or transcripts
- storing identifiable quotes
- retaining raw interview notes beyond the active validation cycle
- storing private customer files, samples, screenshots, or workflows
- sharing identifiable customer context outside the repository
- using direct customer quotes externally
- handling sensitive personal, financial, legal, health, security, or confidential business data

Approval should name:

- what data may be captured
- where it may be stored
- who owns it
- how long it may be retained
- when it must be reviewed or deleted
- whether it may be quoted, shared, or synthesized

If approval is missing, do not capture or retain the data. Use anonymized summary notes instead.

## Repository Artifact Rules

### Customer Interview Template

`validation/customer-interview-template.md` may store interview metadata, anonymized notes, exact language, synthesis, and scorecard inputs.

Use it with this policy:

- participant labels should be anonymized
- storage location should identify where private raw notes live, if any
- exact quotes should be anonymized before entering the repository
- confidential details should stay out of the repository
- recordings require explicit approval and a retention reason

### ICP Profile

`validation/icp-profile.md` should store segment-level evidence and assumptions.

Use it with this policy:

- prefer role, segment, and workflow patterns over individual details
- link to source artifacts without exposing private identifiers
- keep confidence levels clear
- do not paste private customer context into ICP fields

### Customer Language Memory

`knowledge/customer-language-memory.md` should preserve reusable language and learning loops.

Use it with this policy:

- store anonymized quotes only
- avoid source labels that identify a person or company without approval
- keep sensitive or confidential details out of the quote bank
- treat synthetic persona output as hypothesis material, never customer evidence

### Raw Interview Evidence Intake And Synthesis

`validation/raw-interview-evidence-intake-and-synthesis.md` should be used when raw notes, call summaries, transcript summaries, objection logs, or interview batches need to become repository-safe evidence.

Use it with this policy:

- process raw material only after the source approval and retention boundary are clear
- keep raw private notes, recordings, transcripts, and identifiable quotes outside the repository unless explicit approval permits retention
- convert only anonymized, minimum-useful evidence into repository artifacts
- record what was deleted, retained privately, or still needs retention review
- do not let private raw material become hidden memory inside prompts, chats, embeddings, or undocumented files

## Handoff Requirements

When a ticket handles real customer discovery data, the Linear or PR handoff should state:

- whether private customer data was captured
- whether approval was required and where approval is recorded
- where private notes are stored, if any
- what was anonymized into the repository
- what was deleted
- what retention review date remains open
- residual privacy risks

Do not include private customer details in the handoff itself.

## Accidental Capture

If sensitive or unapproved customer data is captured:

1. Stop using the data.
2. Do not copy it into additional tools or repository files.
3. Delete it if safe and authorized to do so.
4. Document a non-sensitive blocker in Linear.
5. Ask for human guidance before proceeding.

## Review Cadence

Review retained private discovery data at the end of each validation cycle and before any PR that promotes validation evidence into strategy, ICP, customer-language memory, or MVP scope.

If the repository changes its privacy, legal, compliance, or customer data posture, update this policy through a dedicated approved ticket.
