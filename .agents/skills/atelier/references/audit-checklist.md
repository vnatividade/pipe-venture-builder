# Audit Checklist (the exit gate)

No Atelier deliverable ships without this pass. It is also the standalone **audit** workflow for existing screens. Findings use the repository severity model: P0/P1 block, P2 fix-if-trivial, P3 note.

## 1. Interface & accessibility — Vercel Web Interface Guidelines

Run the checklist from `~/.claude/atelier-deps/web-interface-guidelines` (`command.md` / `AGENTS.md`, 100+ rules). Non-negotiables (P0/P1 when violated):

- full keyboard path: every interactive element focusable, visible focus state, logical order, no traps
- never disable zoom; no `user-scalable=no`
- don't block paste; inputs use correct `type`/`autocomplete`/`inputmode`
- buttons show loading state and disable during submit (no double-fire)
- heading hierarchy sane (one h1, no skips); ARIA labels where text is absent; icons have accessible names
- contrast ≥ WCAG AA for text and essential UI; state never encoded by color alone
- touch targets ≥ 44px; `prefers-reduced-motion` honored by every animation

When auditing a live preview, annotate findings **visually on the page** (outline offending elements + floating labels via injected JS) — a marked screenshot lands harder than a list.

## 2. Slop & noise — the "quieter" pass

Concept from Impeccable (46 deterministic detectors — run its audit/quieter when available). Manual sweep: gradient count, heavy-weight headings everywhere, utility emoji, accent-bar cards, shadow inflation, centered-everything, more than 2 type families, decoration that encodes nothing (cross-check `design-philosophy.md` slop list). Removing noise is a fix, not a style preference.

## 3. Brief fidelity

Compare against the project's `design-brief.md`: primary action unmistakably dominant? direction's type/color/motion contract honored? every `anti:` entry absent? states trio present (`states-loading.md`)? copy in the product voice?

## 4. Evidence

Attach to the handoff: screenshots (desktop + mobile widths, light + dark if themed), console clean, findings table with severities, what was fixed vs. deferred. Then write the LearningRecord.
