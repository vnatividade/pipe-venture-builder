# Remote delivery of directions as font-embedded artifacts

Status: candidate pattern (consolidated 2026-09-14, pending founder review; LR-0004 targets `references/design-brief.md` and requires human review for that promotion). Provenance: LR-0004, LR-0005, LR-0006 (subset caveat).

## Use when

The concierge taste checkpoint (phase 1 directions) or a phase 2 preview must be seen by a founder who may be remote (claude.ai/code, phone). HTML does not render in GitHub blob view and local paths are useless off-machine — if the founder cannot see the directions, the whole concierge flow stalls.

## Deliverable shape

Two formats, always both:

1. **Canonical files in the venture repo** (`design/atelier/direction-*.html`) — what phase 2 builds from.
2. **One published Artifact per direction** — the one-click viewing vehicle. Links go to the founder.

## Embedding fonts (artifact CSP blocks fonts.googleapis)

1. Extract the `css2` URL from the `<link>`.
2. Fetch it with a browser User-Agent (guarantees woff2 responses).
3. Keep only the `latin` `@font-face` blocks (covers pt-BR; ~100–300 KB per family).
4. Replace the `<link>` with a `<style>` whose `src` are `data:font/woff2;base64,...` URIs.
5. Validate zero external references.

## Exporting from a rendered SPA

1. Serialize the rendered DOM (in Vite dev the injected `<style>` tags already contain compiled CSS).
2. Strip `<script>`; force scroll reveals into their visible state.
3. Embed latin fonts as above.
4. **Always prepend `<meta charset="utf-8">`** — without it the UTF-8 file renders mojibake.
5. Prove self-sufficiency offline:

```js
await page.route(/^https?:\/\//, route => route.abort());
await page.goto('file://' + exportedPath);   // must render identically
```

## Caveat — subset fonts drop UI glyphs

A latin subset has no ✓ (U+2713), ● (U+25CF), ■ (U+25A0), ← (U+2190). If the UI uses text glyphs as icons, replace them with inline SVG (`aria-hidden="true"`, label on the button's `aria-label`) — which also lets the icon scale to a 56–64px target.

## Evidence

- 3 direction artifacts, 5/9/7 faces embedded, zero external refs (LR-0004, PIP-661, 2026-07-18).
- 2 SPA-exported artifacts validated offline with `route.abort` (LR-0005, PR vnatividade/aurasite#31).
- Glyph-as-icon breakage after self-hosting a latin subset (LR-0006).

Follow-ups named by the records (not in this batch — they are skill scripts, outside the knowledge lane): `scripts/embed-fonts.py`, `scripts/export-artifact.mjs`.
