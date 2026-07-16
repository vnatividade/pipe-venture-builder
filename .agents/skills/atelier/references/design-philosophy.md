# Design Philosophy

The model's default output is the average of the web: safe, generic, forgettable. Anthropic calls the mechanism *distributional convergence* — without direction, generation falls to the most probable choice, not the most interesting one. Atelier's job is to be that direction, permanently loaded.

## The slop list — recognize and refuse

These read as "AI made this" on sight. Never produce them unless the brief explicitly asks:

- purple/violet gradient on white; purple-to-blue gradient hero
- Inter / Space Grotesk / system sans as the "choice" for display type
- soft drop-shadow cards with `rounded-lg` everywhere, accent bar on the card edge
- a stray emoji in the middle of a section; emoji as section markers
- every heading in heavy weight; everything centered; equal-width three-card rows for everything
- gradient text on the one keyword; glassmorphism by default
- "warm cream + serif + terracotta" editorial defaults applied regardless of subject

Restraint reads as elegance: fewer weights, fewer colors, more space. When in doubt, run the *quieter* pass (Impeccable) — remove noise before adding anything.

## Core heuristics

1. **Design is ~50% typography.** A generic hero becomes distinctive by the font choice alone. Pick a characterful display face (Google Fonts is full of free ones — Michroma-class geometry, editorial serifs, expressive slabs), pair it with one clean body face, and stop.
2. **Specificity amplifies.** A skill or brief doesn't read minds — it amplifies direction. Vague in, average out. Every generation step carries exact values and explicit negations ("pure black, no gradient, no nothing").
3. **Intentional, not decorative.** Every section answers "what must the user notice or do here?" A light-to-dark transition belongs exactly where the KPI must pop, not wherever it looks nice. If a device (numbering, dividers, animation) doesn't encode meaning, cut it.
4. **Identify the product type first** (dashboard, landing, app, editorial); infer the screen's single goal before drawing. Design changes with context — a landing sells one action; a dashboard surfaces state before detail.
5. **Contained palettes.** Neutral ground chosen (slightly hue-biased toward the accent), one accent spent in one place, semantic colors (ok/warn/critical) separate from the accent.
6. **React > articulate.** Users can't reliably describe aesthetics in words, and shouldn't have to. Resolve taste by rendering 2–3 directions and letting them point (see `design-brief.md`).
7. **The loop beats the model.** Quality comes from build → look at it → fix → look again, not from a better first shot. Verification (screenshot, preview drive, audit pass) is part of design, not QA theater afterwards.
8. **Accessibility is a floor, not a feature.** Keyboard focus visible, ARIA correct, contrast passing, zoom never disabled — see `audit-checklist.md`. Beautiful and inaccessible = failed.

## Voice

Interface copy is design material: name things by what users recognize, active voice, a control says exactly what happens. No utility emoji in product UI (house rule from Lumia/NaAtiva); emoji only where it genuinely adds lightness and the brand allows it.
