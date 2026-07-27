# Speakable Markdown Profile — Draft v0

The output contract of md-audio's paste intake: what the client-side transform emits, and therefore what the Mac Studio worker receives.

Status: **draft, blocked on MD-INTAKE-01 (PIP-719).** This profile describes what the transform should produce, but the Mac worker's own normalization is unknown (it lives on the founder's machine, outside any reachable repository). Every rule below marked ⚠️ risks duplicating work the worker already does. PIP-719 resolves those before MD-INTAKE-03 (PIP-721) implements them.

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
| Lists | Each item becomes its own sentence. Nesting flattened to two levels ⚠️ |
| Emphasis / strong | Markers stripped, words kept |
| Link | Anchor text only, URL dropped. A bare URL becomes `[link omitido]` |
| Image | `Imagem: <alt>`; without alt, `[imagem omitida]` |
| Inline code | Read literally, backticks stripped |
| Code block | `[código omitido]`. Blocks of three lines or fewer may be read literally — decided by fixtures, not by a model |
| Table | Linearized row by row (`coluna: valor, …`) when it has three columns or fewer; otherwise `[tabela omitida]` |
| Footnote | Moved to the end of its section as a normal sentence |
| Raw HTML | Stripped at capture ⚠️ |
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

## Open Questions For MD-INTAKE-01 (PIP-719)

Answer these against the Mac Studio worker before implementing the transform. This section is the deliverable of PIP-719 — replace each question with its answer:

- What does the worker already strip or normalize? Every ⚠️ rule above may be redundant or actively harmful.
- Exactly which pause phrasings does it accept — only `pausa de N segundos` / `N minuto(s)`, or more? Is there an upper bound?
- How does it split sentences for Kokoro? If it is punctuation-driven, the transform must guarantee terminal punctuation on every emitted line.
- How does it treat a line that is only a heading — spoken, skipped, or paused around?
- Does it handle non-pt-BR text, and what happens on mixed-language input?
