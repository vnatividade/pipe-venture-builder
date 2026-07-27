# Speakable Markdown Profile — Draft v0

The output contract of md-audio's paste intake: what the client-side transform emits, and therefore what the Mac Studio worker receives.

Status: **draft, unblocked.** MD-INTAKE-01 (PIP-719) read the Mac Studio worker's actual code (`app.py` + `worker_poll.py` in `~/Developer/md-audio-site`, the repo backing the running `com.natiivis.mdaudio-poller` LaunchAgent) and answered every open question below. MD-INTAKE-03 (PIP-721) can now implement against this profile.

## Design Principle

The output is not a document to be read — it is a **script to be spoken**. Anything that cannot be pronounced usefully is either linearized into words or replaced by an explicit, visible marker. The user's words themselves are never changed.

## Structure

Unlike a written document, the spoken version carries structure through *time*, using the pause command the product already supports:

| Source structure | Emitted as |
|---|---|
| Document title | First spoken line, then `pausa de 2 segundos` |
| Chapter break (H1/H2) | The heading text, then `pausa de 2 segundos` |
| Section break (H3+) | The heading text, then `pausa de 1 segundo` |
| Paragraph break | Nothing added — normal sentence punctuation carries it |
| Horizontal rule (`---`) | `pausa de 3 segundos` |

Pause durations are a starting point to be tuned by listening, not a fixed contract. Heading levels deeper than H3 are flattened to H3.

Titles: inferred from the first heading, or failing that the first sentence if it is short enough to read as a title. The inferred title prefills the existing "Título (opcional)" field so the user can correct it before generating — inference proposes, the user decides.

## Speakable Handling

| Construct | Rule |
|---|---|
| Blockquote | Spoken as-is; an attribution line right after (`— Author`) is kept as its own sentence |
| Lists | Each item becomes its own sentence. Nesting flattened to two levels — **not redundant**: the worker strips `-`/`*`/`+`/`N.` markers unconditionally at any indentation depth and preserves no nesting signal at all, so "flatten to two levels" is entirely the transform's job and must happen before markdown is emitted |
| Emphasis / strong | Markers stripped, words kept |
| Link | Anchor text only, URL dropped. A bare URL becomes `[link omitido]` — **the transform must generate this marker itself**; the worker has no bare-URL detection and will pass a stray URL straight to Kokoro to be read literally |
| Image | `Imagem: <alt>`; without alt, `[imagem omitida]` — the worker's own image handling silently collapses `![](url)` to an empty string (no marker), so an unmarked empty-alt image is silent content loss unless the transform's marker is in place first |
| Inline code | Read literally, backticks stripped |
| Code block | `[código omitido]`. Blocks of three lines or fewer may be read literally — decided by fixtures, not by a model. **The worker deletes every fenced code block unconditionally and silently** (replaces ```…``` with a single space, no marker, regardless of length) — the transform must emit any `[código omitido]` marker itself as literal spoken text, never rely on the worker to produce or preserve it |
| Table | Linearized row by row (`coluna: valor, …`) when it has three columns or fewer; otherwise `[tabela omitida]`. **The worker does not linearize this way** — it drops separator rows and turns every remaining `\|` into `, `, so raw table rows pass through as comma-joined fragments, not `coluna: valor` pairs. The transform must fully linearize or mark tables before they reach the worker |
| Footnote | Moved to the end of its section as a normal sentence — the worker has no footnote handling at all; unmoved footnote markers/definitions pass through as literal text |
| Raw HTML | Stripped at capture — **not redundant, and mandatory**: the worker has no HTML handling whatsoever, so any tag the transform doesn't strip is passed to Kokoro and read aloud literally |
| Existing `pausa de N segundos` in the user's input | Preserved untouched — the user may already be using the command deliberately |

Every `[… omitido]` marker must be visible in the preview. A marker the user cannot see before generating is silent content loss.

## Plain-Text Mode

With no markdown syntax to read, structure comes from the text's own shape:

- Blank-line-separated blocks are paragraphs
- A short line (under ~60 characters) with no terminal punctuation, followed by a blank line, is treated as a heading
- Runs of lines starting with `-`, `*`, or `1.` are treated as a list even without valid markdown
- Nothing else is inferred — when in doubt, it stays a paragraph

## Validity Rules

- UTF-8, no raw HTML, no zero-width or control characters beyond newline
- Non-empty after transform (an input that reduces to only omission markers is an error the preview must state plainly)
- Within `MAX_MD_BYTES` (2 MB) after transform, checked client-side before submit
- No heading emitted without content following it

## Worker Findings (PIP-719)

Source: `markdown_to_text()`, `parse_segments()`, and `synth_to_mp3()` in `app.py` (`~/Developer/md-audio-site`, `main` @ `2c2d09f`), reused by `worker_poll.py` — the code behind the running `com.natiivis.mdaudio-poller` LaunchAgent. This is the entire Markdown-handling surface of the Mac Studio worker; there is no other normalization step anywhere in the pipeline.

**What the worker already strips or normalizes** (in order, all via regex over the raw string):

- Fenced code blocks (```…```) → replaced with a single space. **Content is fully and silently discarded — no marker, no length exception.**
- Inline code (`` `…` ``) → backticks stripped, content kept literally.
- Images `![alt](url)` → alt text only; empty alt collapses to an empty string (no marker).
- Links `[text](url)` → anchor text only, URL dropped. Bare (non-markdown) URLs are untouched — no detection, no marker.
- Headings `#`…`######` → only the leading `#` marker is stripped at line start; the heading text stays inline as plain text with no distinguishing treatment.
- Blockquotes `>` → marker stripped, text kept inline; no attribution handling.
- List markers `-`, `*`, `+`, `N.` → stripped at line start regardless of indentation, so **no nesting depth survives**. Items are not split into separate sentences — they're left as whatever lines/punctuation the source had.
- Tables → separator rows (`|---|---|`) removed entirely; every remaining `|` (header or data) becomes `", "`. No "coluna: valor" linearization.
- Emphasis/strong/strikethrough (`**`, `__`, `*`, `_`, `~~`) → markers stripped, words kept.
- Horizontal rules (`---`, `***`, `___`) → removed entirely, no marker or pause inserted in their place.
- Whitespace → runs of spaces/tabs collapsed to one; 3+ newlines collapsed to 2.
- **Raw HTML → not handled at all.** No regex targets tags; any HTML passes through unchanged and would be read literally by Kokoro.
- **Footnotes → not handled at all.** Markers and definitions pass through unchanged as literal text.

Practical consequence for every ⚠️ rule in this document: none of them are redundant, and the code-block and table rules were previously *understating* the risk — the worker does not produce or preserve an omission marker for anything. Every `[… omitido]` marker in this profile must be emitted by the transform as literal spoken text before the content reaches the worker; there is no server-side safety net that will insert one for you, and the code-fence case is **silent total loss**, not a spoken placeholder, if the transform doesn't handle it first.

**Pause phrasings accepted** — regex `PAUSE_RE` in `app.py`:

```
\[?\s*(?:pausa|pause)(?:\s+de)?\s+(\d+(?:[.,]\d+)?)\s*(minutos?|mins?|min|m|segundos?|segs?|seg|s)\b\.?\s*\]?
```

Case-insensitive. Accepted: command word `pausa` or `pause`; optional `de`; a number (integer or decimal, `.` or `,` separator); a **pt-BR** unit word only — `minutos?`/`mins?`/`min`/`m` or `segundos?`/`segs?`/`seg`/`s` (English unit words like "seconds"/"minutes" do **not** match); optional wrapping `[...]`; optional trailing period. Examples that work: `pausa de 5 segundos`, `pausa 5s`, `[pausa de 2 min]`, `pausa de 1 minuto`, `pause 3s`, `pausa 1.5min`. Examples that do **not** work: `pause 5 seconds` (English unit), `pausa de cinco segundos` (spelled-out number), `espere 5 segundos` (wrong command word) — any non-matching text is left completely untouched and spoken literally as ordinary words; there is no error and no partial recognition.

Upper bound: `MAX_PAUSE_SECONDS` env var, default **300 seconds (5 minutes)**. Lower bound: clamped up to a floor of 0.1s, so there is no true zero-length pause. Both bounds are silent clamps (`max(0.1, min(secs, MAX_PAUSE_SECONDS))`) — an out-of-range value is not rejected, just clipped.

**Sentence splitting for Kokoro:** the worker does not split sentences at all. `parse_segments()` only breaks the text at pause-command boundaries; each resulting "speak" segment — however long, however many paragraphs it spans — is handed to `kokoro.create()` as a single call. Any further chunking happens (if at all) inside the vendored `kokoro-onnx==0.5.0` library itself, which this investigation did not read and which is opaque from this repository. Because nothing in the worker inserts sentence breaks, **the transform must guarantee terminal punctuation (`.`, `!`, `?`) on every emitted line** — a heading or list item left without it is passed to Kokoro exactly as typed, with no downstream correction.

**Heading-only lines:** spoken, never skipped, never paused around. The worker only strips the leading `#` marker; the remaining text stays on its own line and is treated exactly like any other text — normal whitespace collapsing applies, nothing else. This confirms the planned `pausa de 2 segundos`/`pausa de 1 segundo` after headings is purely additive: the worker contributes zero structural audio behavior on its own, so all of it must come from the transform.

**Non-pt-BR / mixed-language input:** no handling of any kind. `LANG` is one fixed value (env var `KOKORO_LANG`, default `"pt-br"`) passed identically to every `kokoro.create()` call regardless of segment content — there is no language detection, no per-segment switching, no voice change hook. Mixed-language input is forced through the pt-BR phonemizer/voice in full and will likely be mispronounced; there is nothing in this codebase for the transform to route through differently.

## What The Transform Must Not Do

- Must not wrap short or omitted code in triple-backtick fences and expect a marker to survive — the worker deletes fenced content unconditionally and silently. Emit `[código omitido]` (or literal short snippets) as plain spoken text, never inside a code fence.
- Must not rely on the worker to mark bare URLs, footnotes, or raw HTML — none are handled. Raw HTML in particular will be read aloud literally if the transform doesn't strip it first.
- Must not invent pause phrasings outside the exact accepted forms (pt-BR unit words, `pausa`/`pause` + optional `de` + number) — anything else is spoken as literal words instead of executed as a pause.
- Must not emit un-punctuated lines (bare headings, bare list items) and assume a natural spoken break — nothing downstream inserts one.
- Must not assume list nesting depth reaches the worker — it is stripped unconditionally before any transform-level decision could matter, so "flatten to two levels" must happen inside the transform itself.
- Must not claim or design for correct pronunciation of non-pt-BR content — voice and language are fixed pt-BR for every synthesis call, with no per-segment override.
