# md-audio — Venture Product Artifacts

This folder holds Pipe-governed product artifacts for the house venture **md-audio**, a product that plays markdown documents as audiobooks.

The md-audio implementation lives in its own repository (referenced as `md-audio-proxy` in `.agents/skills/atelier/scripts/consolidate.md`). That repository is not inspectable from this one, so every statement here about the current implementation is labeled as fact, inference, or assumption per `execution/dual-entry-product-intake-workflow.md`.

## Source Boundary

Inspectable sources inside this repository:

- `.agents/skills/atelier/stack-adapters/react-next.md` — names md-audio as a house venture on the React/Next.js App Router stack.
- `.agents/skills/atelier/scripts/consolidate.md` — names the `md-audio-proxy` repository in the Atelier working set.
- `capabilities/entries/capability.internal.atelier.json` — records md-audio as the first Atelier design pilot (founder decision of 2026-07-16).
- Founder request of 2026-07-27 (this planning session) describing the desired intake feature.

Not inspectable from here:

- The md-audio codebase, its current markdown input format, its player/TTS behavior, and its library model.

## Fact vs Assumption Ledger

| Statement | Class | Source |
|---|---|---|
| md-audio is a house venture on the React/Next.js App Router stack. | fact | Atelier stack adapter |
| md-audio's code lives in a separate repository (`md-audio-proxy`). | fact | Atelier consolidate script |
| md-audio consumes markdown documents and plays them as audiobooks. | inference | venture name + founder request framing |
| md-audio has a defined markdown structure its player expects (chapters, headings). | assumption | must be confirmed against the md-audio repository |
| md-audio has a library/collection concept where converted documents land. | assumption | must be confirmed against the md-audio repository |

Assumptions above are Definition-of-Ready blockers for implementation tickets: they must be confirmed (or corrected) against the md-audio repository before code is written.

## Artifacts

- `feature-universal-text-intake.md` — feature plan: paste raw text or raw markdown, understand it, transform it into audiobook-ready markdown.
- `audiobook-markdown-profile-draft.md` — draft v0 of the output contract the intake pipeline must produce.
