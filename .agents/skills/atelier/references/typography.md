# Typography

Design is ~50% typography. The fastest lever from generic to distinctive is the display face.

## Selection

- **Display**: one characterful face per project — geometric/techno (Michroma-class), editorial serif, expressive slab, or brutalist grotesk — chosen to match the brief's mood adjectives, never as a habit. Google Fonts first (free, embeddable, name is enough for any stack to import). Check the license badge before committing.
- **Body**: one clean, quiet face that contrasts the display (display loud → body silent). Two families total; a third only for data/code (`tabular-nums` for aligned digits).
- **Banned as "choices"**: Inter/Space Grotesk/system-ui *as the display* — they are defaults, not decisions. Fine as body when the brief is deliberately neutral.

## Scale & setting

- Responsive display size via `clamp(min, vw-based, max)` — e.g. `clamp(28px, 4.5vw, 56px)`; hero headlines may instead **fill the container width** (fit-to-width JS or `vw` sizing) so the type scales with the section.
- Uppercase display + slight positive letter-spacing for labels/taglines; never letter-space lowercase body.
- Body measure ≈ 65ch; line-height ~1.5 body, ~1.05–1.15 display; `text-wrap: balance` on headings.
- Hierarchy by size + space first, weight second, color last. If every heading is bold, nothing is.

## Recipe (from the validated hero pattern)

Tagline (display, small, logo-sized, left-aligned) → headline (display, uppercase, clamp or fill-width) → one-sentence description (body, muted). Same display face applied to the logo/wordmark ties the page together.

## Stack notes

Import: vanilla → `<link>` embed from Google Fonts; React/Next → `next/font/google` (self-hosted, no layout shift); Flutter → `google_fonts` package. Always specify fallback stack and `font-display: swap`.
