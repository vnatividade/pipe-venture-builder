# md-audio Feature Plan — Universal Text Intake (Paste-to-Audiobook)

- Status: draft plan, approved for planning under `exploration` mode (`.pipe/mode.json`)
- Origin: founder request, 2026-07-27
- Venture: md-audio (implementation repository: `md-audio-proxy`, outside this repo)
- Owner: founder (Vitor Natividade); planning agent: Claude Code
- Linear: ticket creation pending — Linear MCP was not authenticated in the planning session; see Governance Notes

## Problem

md-audio turns markdown documents into audiobooks, but the content people most want to listen to rarely starts as well-formed markdown. It starts as:

- answers copied from an AI agent conversation
- personal notes and drafts
- collections of quotes and highlights
- fragments of articles or transcripts
- markdown that is technically valid but messy: no title, broken heading hierarchy, code blocks, tables, links, and other artifacts that do not speak well

Today the user must hand-convert that material into the markdown structure md-audio expects before they can listen to it. That conversion is the friction between "I have something worth hearing" and "I am listening to it."

## Solution Overview

Add an **Intake** surface to md-audio: a dedicated paste area that accepts raw content, understands it, and transforms it into audiobook-ready markdown that md-audio can play.

Two input modes share one paste area:

| Mode | Accepts | Typical sources |
|---|---|---|
| Raw text | Free-form unstructured text | AI agent answers, personal notes, quotes, transcripts |
| Raw markdown | Markdown pasted as-is, however messy | Exported notes, README fragments, AI answers already in markdown |

Mode is auto-detected from markdown syntax density (headings, lists, fences, emphasis markers) with a manual override toggle, so the user never has to know or care which parser runs.

### Pipeline

```txt
paste
  -> capture & sanitize        (size limit, strip raw HTML/scripts, normalize encoding)
  -> detect                    (input mode, language, content type)
  -> understand                (infer title, segment into chapters/sections, classify blocks)
  -> transform                 (emit audiobook-ready markdown per the profile)
  -> validate                  (profile validator; fail closed to deterministic output)
  -> preview & edit            (rendered result + estimated listening time; user can edit)
  -> save to library           (nothing is persisted before this step)
```

- **Understand** combines a deterministic pass (remark/unified parsing for markdown mode; paragraph/heading heuristics for text mode) with an LLM structuring pass (Claude API) that returns a strict, schema-validated structure.
- **Transform** emits markdown conforming to `audiobook-markdown-profile-draft.md`: frontmatter (title, language, source type), H1 title, H2 chapters, speakable handling of quotes, lists, links, code, and tables.
- **Degraded path:** if the LLM step is unavailable or its output fails validation, the deterministic pass alone produces a valid (if plainer) result. Intake never hard-fails because the model is down.

### Content-Preservation Principle

The system reorganizes and formats; it does not rewrite. The transform must not summarize, paraphrase, add, or drop the user's content beyond the profile's defined handling of non-speakable artifacts. The preview shows what was moved or marked (for example `[code omitted]`), so the user can verify nothing was lost. An optional "clean up wording" mode is explicitly a future feature, not part of this one.

## MVP Scope

- Paste area with auto-detected raw-text / raw-markdown modes and manual override
- Deterministic normalization pipeline for both modes
- LLM understanding pass with schema-validated output and content-preservation guardrails
- Audiobook markdown profile v0 and validator
- Preview with estimated listening time and inline editing before save
- Save into the md-audio library behind a feature flag

## Excluded Scope

- File upload, URL fetching, or document import (paste only)
- Any change to the TTS/player engine itself
- Rewriting, summarizing, or translating content
- Multi-document merge or batch intake
- Billing, pricing, or usage limits tied to payment (absolute gate; not touched)
- Voice cloning or per-block voice assignment beyond what the profile already encodes

## Architecture Sketch (assumptions flagged)

Assuming md-audio's Next.js App Router stack (fact) and an existing library model (assumption):

- Client: intake route with paste area, mode toggle, preview pane. No raw content leaves the page except to the transform endpoint.
- Server: one server action / route handler `transform` — stateless, idempotent, returns the candidate markdown plus a block-level provenance map for the preview diff. No persistence until an explicit `save`.
- LLM call: Claude API with a fixed output JSON schema (title, chapters[], blocks[] with type + verbatim text spans). Temperature low; verbatim spans are copied from input by offset, not re-generated, to enforce preservation.
- Validator: shared package that both the transform endpoint and the player can use to accept/reject a document against the profile.

Raw pasted content may contain personal or sensitive material. It must not be logged, retained server-side pre-save, or used for anything beyond the transform call. This constraint is part of acceptance criteria, not an afterthought.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| LLM alters or invents content | Verbatim-span architecture, validator diff check (input tokens ⊆ output tokens above threshold), preview diff, deterministic fallback |
| Sensitive data in pastes | No pre-save persistence, no raw-content logging, LLM call scoped to transform only |
| Huge pastes | Hard size limit with clear messaging; chunked understanding pass later if evidence demands it |
| Mixed/ambiguous language | Language detected and recorded in frontmatter; no translation attempted |
| md-audio format assumptions wrong | Definition of Ready requires reconciling the profile draft against the md-audio repository before implementation |

## KPI Impact

- Primary KPI: intake conversion — % of paste sessions that end in a saved audiobook
- Secondary KPI: time from paste to first playback
- Adoption: share of new library items created via intake vs. pre-existing paths
- Retention signal: repeat intake use within 14 days
- Baseline: none yet (feature does not exist); first two weeks post-flag define the baseline

## Validation Plan

- Golden fixture suite: representative pastes (AI answer, notes, quote list, messy markdown, table/code-heavy markdown) with expected profile-valid outputs, run in CI
- Property check: content-preservation threshold on every fixture (no verbatim span lost)
- Validator unit tests against the profile spec
- Manual mood test: founder pastes three real inputs and rates the listening result
- Unavailable in planning repo: no md-audio code or CI is reachable from pipe-venture-builder; execution-time validation happens in the md-audio repository

## Rollback

Feature flag `intake_paste`. Rollback = flag off; no schema migrations required in MVP (documents saved through intake are ordinary library items). Rollback signal: intake conversion below an agreed floor or any report of content alteration.

## Slice Breakdown (one ticket, branch, and PR each)

| Slice | Scope | Depends on |
|---|---|---|
| MD-INTAKE-01 | Audiobook markdown profile v0 reconciled against the md-audio player + shared validator | — |
| MD-INTAKE-02 | Deterministic normalization pipeline (both modes) + golden fixtures | 01 |
| MD-INTAKE-03 | Intake UI: paste area, mode auto-detect/override, size limits | 01 |
| MD-INTAKE-04 | LLM understanding pass with verbatim-span schema + degraded path | 02 |
| MD-INTAKE-05 | Preview/edit, listening-time estimate, save-to-library behind flag | 02, 03, 04 |

MD-INTAKE-01 is the keystone: it converts the ledger's assumptions about md-audio's expected format into facts before anything else is built.

## Draft Epic Ticket (Linear Ticket Template V2, condensed)

```md
# [md-audio] Universal text intake: paste raw text or markdown, get an audiobook

## Objective
Let a user paste raw text or raw markdown and receive a profile-valid,
audiobook-ready markdown document in the md-audio library.

## Why This Matters
Removes the manual-conversion friction between having content and listening
to it; widens md-audio's usable input from "well-formed markdown" to
"anything textual the user can paste."

## Type
- product

## Included Scope / Excluded Scope / Deliverables / Acceptance Criteria
See feature plan sections above; acceptance criteria highlights:
- both input modes produce profile-valid output on the golden fixtures
- content-preservation check passes on every fixture
- LLM-down path still yields a valid document
- no raw paste content is persisted or logged before save
- feature is fully disabled by its flag

## GO Conditions
- MD-INTAKE-01 reconciliation confirms or corrects the profile draft

## NO-GO Conditions
- md-audio player format cannot be confirmed
- preservation check cannot be enforced

## Dependencies
- md-audio repository access; Claude API availability for the LLM pass

## Approval Requirement
- Exploration mode: ticket creation, PR opening, and merge run autonomously
  with Linear logging; production deploy and any billing/claims remain
  human-gated (absolute gates)

## Executor Tool
- Claude Code

## Risk Level
- Medium: LLM in the write path of user content, mitigated by verbatim-span
  design and deterministic fallback

## Expected Write Set
- md-audio repository: intake route, transform endpoint, profile validator
  package, fixtures; pipe-venture-builder: this folder only

## Rollback or Mitigation
- Flag off; rollback signal per feature plan
```

## Governance Notes

- Planned under `exploration` mode; absolute gates untouched (no billing, no production deploy, no customer contact, no sensitive claims — all metrics above are targets, not evidence).
- Linear MCP was not authenticated in the planning session, so the epic and slice tickets could not be created there yet. Creating them (or authorizing Linear for an agent session) is the next action; until then this document and its PR are the audit trail.
- Implementation happens in the md-audio repository, not in pipe-venture-builder. This plan is the handoff artifact for that work.
