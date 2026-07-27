# md-audio Feature Plan — Colar e Ouvir (Universal Text Intake)

- Status: refined plan, ready for slicing. Written against the real md-audio-proxy code at `main` (2026-07-27)
- Origin: founder request, 2026-07-27
- Venture: md-audio · repository: [`vnatividade/md-audio-proxy`](https://github.com/vnatividade/md-audio-proxy) (`exploration` mode)
- Owner: founder (Vitor Natividade); planning agent: Claude Code
- Linear: project [md-audio](https://linear.app/pipe-venture-builder/project/md-audio-951677fb7620) · epic [PIP-718](https://linear.app/pipe-venture-builder/issue/PIP-718) · slices PIP-719 … PIP-723

## Problem

md-audio only accepts a **file**. To listen to anything today the user must first get their content into a `.md` file on the device they are holding — which is exactly the step that does not happen on a phone. The content people most want to hear arrives as something you copy, not something you save:

- answers from an AI agent conversation
- personal notes and drafts
- collections of quotes and highlights
- fragments of articles or transcripts
- markdown that is valid but unspeakable as-is: code fences, tables, link URLs, broken heading order

The file requirement is the friction between "this is worth hearing" and "I am hearing it."

## Solution

Add a **paste area** to the app card: the user pastes content, the app turns it into speakable markdown, and generates audio through the pipeline that already exists.

Two input modes share one paste area, auto-detected from markdown syntax density with a manual override:

| Mode | Accepts | Typical source |
|---|---|---|
| Texto cru | free-form unstructured text | AI answers, notes, quotes, transcripts |
| Markdown cru | markdown as-is, however messy | exported notes, README fragments, AI answers already in markdown |

### The Architectural Insight

**This feature needs no server change at all.** `doPreview()` in `app.py` already synthesizes audio from a string built in the browser:

```js
fd.append('file', new File([txt], 'previa.md', { type:'text/markdown' }));
```

A paste area does exactly the same thing with the transformed text. So `/synthesize`, the job queue, the worker protocol, and the Mac Studio worker are all untouched. The whole feature is client-side, inside the `INDEX_HTML` string — which also means:

- no new Python dependency (`requirements.txt` stays at flask + gunicorn)
- no API key, so **no secrets gate is triggered**
- no build step, honoring the repo's stated constraint
- rollback is a git revert plus `railway up`

### Pipeline (all in the browser)

```txt
paste
  -> detect        (markdown vs plain text; syntax-density heuristic + manual override)
  -> structure     (title inference, section detection, block classification)
  -> transform     (emit speakable markdown per the profile)
  -> preview       (show exactly what will be spoken + estimated duration; user can edit)
  -> generate      (File -> existing /synthesize -> existing queue -> Mac worker)
```

### Deterministic, Not Model-Driven

The transform is plain vanilla JS — no LLM. This is a deliberate reversal of the first draft of this plan, for three reasons:

1. **The gate.** An LLM needs an API key on the server. Handling secrets is an absolute approval gate in every operating mode, and it would be the only secret in a repo whose entire dependency list is two lines.
2. **The risk.** The one thing this feature must never do is change the user's words. A deterministic transform cannot hallucinate; a model can.
3. **It is not needed.** What "understanding the content" actually requires here is structural, not semantic: find the title, find the section boundaries, decide which blocks are speakable, and linearize the rest. Punctuation and paragraph shape are enough. If golden fixtures later prove a real gap, an LLM pass becomes its own ticket with its own gate.

### Using The Pause Command That Already Exists

The single best thing the current product already does for this feature: writing `pausa de 5 segundos` inserts real silence, interpreted by the Mac worker. So structure can be expressed **as audio**, not just as text — the transform emits a short pause between sections and a longer one between chapters. Section breaks stop being invisible in a linear narration.

### Content Preservation

The transform reorganizes and formats; it never rewrites, summarizes, or reorders the user's words. Non-speakable artifacts are replaced by explicit markers (`[código omitido]`) and every marker is visible in the preview, so the user can see precisely what will not be narrated. A "clean up the wording" mode is out of scope and would be a separate, clearly-labeled feature.

## MVP Scope

- Paste area in the app card, alongside the existing file input, sharing the same submit
- Mode auto-detection with manual override
- Deterministic transform to speakable markdown, including pause-command section breaks
- Title inference prefilling the existing "Título (opcional)" field
- Preview of the exact text to be spoken, with estimated duration and inline editing
- Golden fixtures and the minimal test surface to run them (the repo has none today)

## Excluded Scope

- Any change to `/synthesize`, the queue, the worker protocol, or the Mac worker
- URL fetching, file import beyond today's upload, multi-document merge
- Rewriting, summarizing, or translating content
- Any LLM or new server dependency
- Server-side persistence of pasted content (nothing is stored server-side beyond the existing 30-minute job)
- Analytics or telemetry (none exists; adding it is not justified by this feature)
- Auth changes — the shared-token model is untouched

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Transform double-processes markdown the Mac worker already handles | High | MD-INTAKE-01 maps the worker's normalization before the transform is specified |
| Pasted content is personal | Medium | Nothing new is persisted; content follows the same path as today's uploads. The known caveat stays honest: text passes through the Railway queue before reaching the Mac Studio, so "total privacy" must not be claimed |
| Silent content loss in the transform | Medium | Preview shows the exact spoken text; every omission is an explicit visible marker; fixtures assert preservation |
| `app.py` grows unwieldy (already 843 lines with the UI inline) | Low | Keep the transform as one clearly-bounded JS block; if it exceeds ~200 lines, split the UI into a served static file under its own ticket |
| 2 MB limit surprises a large paste | Low | Client-side length check with a clear message before submit |

## Success Measures

Honest constraint: **the app has no analytics**, so conversion-style metrics are not measurable, and instrumenting a single-user personal tool is not worth it. The success measures are therefore direct and qualitative:

- The founder pastes real content (an AI answer, a page of notes, a set of quotes) and the resulting audio is pleasant to listen to end to end — judged by listening, recorded in the ticket
- The spoken text contains no code fences, raw URLs, or table syntax read aloud
- Section breaks are audible as pauses
- Fixtures pass: no verbatim content lost across all representative inputs
- Not measured, deliberately: adoption, retention, conversion. Stated so nobody later mistakes their absence for failure

## Rollback

Revert the commit and `railway up`. No migrations, no schema, no server contract change. The existing file-upload path is untouched throughout, so the worst case leaves today's product exactly as it is. A feature flag would be over-engineering: the repo has no flag mechanism and the change is additive UI.

## Slice Breakdown

One ticket, branch, and PR each.

| Slice | Linear | Scope | Depends on |
|---|---|---|---|
| MD-INTAKE-01 | PIP-719 | Map the Mac Studio worker's Markdown normalization and pause-command parsing; write it down as the transform's contract | — |
| MD-INTAKE-02 | PIP-720 | Paste area UI in `INDEX_HTML`: textarea, mode toggle, size check, Lampião tokens; paste and file share one submit | — |
| MD-INTAKE-03 | PIP-721 | Deterministic transform + speakable-markdown profile, including pause-based section breaks and title inference | 01 |
| MD-INTAKE-04 | PIP-722 | Golden fixtures + minimal test surface (repo has no tests today) | 03 |
| MD-INTAKE-05 | PIP-723 | Preview of the spoken text, estimated duration, inline editing before generating | 02, 03 |

**MD-INTAKE-01 is the keystone and it is a human/local task**: the Mac Studio worker is not in any repository, so no cloud agent can inspect it. Until its normalization is written down, the transform would be guessing, and the most likely failure is doing work the worker already does — stripping syntax twice, or fighting its sentence splitting. MD-INTAKE-02 is genuinely independent and can start in parallel.

## Governance Notes

- Both repositories declare `exploration` mode, so ticket creation, PR opening, and merge run autonomously with Linear logging. Production deploy (`railway up`) remains founder-only in every mode.
- No absolute gate is touched: no secrets, no billing, no customer data, no external communication, no sensitive claims. The deliberate avoidance of an API key is what keeps it that way.
- Implementation happens in md-audio-proxy. This document is the durable handoff artifact; the repository is the source of truth for strategy, Linear for execution state.
- Follow-up outside this feature's scope, filed as **PIP-724**: `.agents/skills/atelier/stack-adapters/react-next.md` lists md-audio as a React/Next venture, which the code contradicts. That line is what misled the first draft of this plan; correcting it stops the next agent from repeating the mistake.
