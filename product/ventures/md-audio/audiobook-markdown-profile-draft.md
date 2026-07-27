# Audiobook Markdown Profile — Draft v0

Output contract for md-audio's Universal Text Intake pipeline: every document the intake produces must conform to this profile, and the md-audio player should be able to narrate any conforming document predictably.

Status: **draft**. This profile was written without access to the md-audio repository. MD-INTAKE-01 must reconcile it against the player's actual capabilities before any other slice is implemented; the reconciled version lives in the md-audio repository, and this draft is then updated or superseded with a pointer.

## Frontmatter

```yaml
---
title: "Inferred or user-confirmed title"        # required
language: "pt-BR"                                 # required, BCP 47
source_type: ai_answer | notes | quotes | article | transcript | other   # required
source_attribution: "optional free text"          # optional (e.g., "Answer from Claude, 2026-07-27")
created: 2026-07-27                               # required, intake date
intake: paste_text | paste_markdown               # required, provenance of the input mode
---
```

No other frontmatter keys in v0. Unknown keys are a validation error, so the schema can grow deliberately.

## Structure

- Exactly one `#` H1: the audiobook title (must match `title`).
- `##` H2 = chapter break. Every document has at least one chapter; the transform inserts a single "Conteúdo" chapter when the source has no natural segmentation.
- `###` H3 = section within a chapter (optional; deeper levels are flattened to H3).
- Paragraphs are the spoken unit. Blank-line separated.
- `---` horizontal rule = long pause.
- Empty chapters are a validation error.

## Speakable Handling of Markdown Constructs

| Construct | Rule |
|---|---|
| Blockquote | Spoken as quoted material; an attribution line immediately after (`— Author`) is spoken as attribution |
| Ordered/unordered list | Preserved; player narrates as enumeration. Nesting flattened to two levels |
| Emphasis/strong | Preserved in text; carries no required audio semantics in v0 |
| Link | Anchor text only; URL dropped. Bare URLs become `[link omitido]` |
| Image | Alt text spoken as `Imagem: <alt>`; images without alt become `[imagem omitida]` |
| Inline code | Read literally |
| Code block | Replaced by `[código omitido]` marker paragraph by default; blocks ≤ 3 lines may be read literally when the understanding pass marks them speakable |
| Table | Linearized row by row (`header: value, …`) when ≤ 3 columns; otherwise `[tabela omitida]` |
| Footnote | Moved to end of its chapter under a `### Notas` section |
| Raw HTML | Stripped at capture; never reaches the profile |

Every omission marker (`[… omitido]`) must correspond to an entry in the intake preview's provenance map, so the user sees exactly what will not be narrated.

## Validity Rules

- UTF-8, LF line endings, no raw HTML, no unknown frontmatter keys
- Required frontmatter present; H1 present and unique
- No heading-level jumps (H2 before any H3 within a chapter)
- Chapter length guidance: warn above ~10k characters (chunking guidance for the player), not an error
- A conforming document round-trips through the validator with zero warnings on the golden fixtures

## Open Questions for MD-INTAKE-01 Reconciliation

- What structure does the current md-audio player actually key on for chapters and pauses?
- Does the library already store metadata that overlaps with this frontmatter (and which side wins)?
- Are omission markers rendered/skipped by the player today, or do they need player support?
- Is pt-BR the only launch language, or must fixtures cover mixed-language pastes from day one?
