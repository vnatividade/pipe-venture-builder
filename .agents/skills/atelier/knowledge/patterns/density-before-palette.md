# Density before palette ("Console" for execution apps)

Status: candidate pattern (consolidated 2026-09-14, pending founder review; LR-0006 proposes an "execution apps" section for `references/design-philosophy.md`). Provenance: LR-0006 (high confidence + high importance), LR-0007 (founder feedback on a squeezed row).

## Use when

- A screen "looks generic" or "feels cramped" and the instinct is to change colors.
- The product is an **execution app**: operated in a hurry, one-handed, bad light, between tasks (workouts, kitchen, field work, shop floor).
- A data row carries name + chips + values + a bar and gets squeezed at intermediate widths.

## Diagnose density first

Measure: how many pixels does the user scroll before reaching the control they came to touch? If there is preamble, fix structure before color:

- Demote demo media from content to reference (a ~120px strip that expands on tap).
- Collapse generic instructions into native `<details>`; keep today's specific note visible.
- Collapse finished items into a one-line ledger row with what was done.
- Placeholder media (1×1): detect `naturalWidth <= 2` on load and collapse the block instead of reserving height.

## "Console" direction for execution apps

- Numbers are the content: `font-variant-numeric: tabular-nums`, expanded width (`font-stretch` on a variable family with a `wdth` axis).
- Near-black ground with a slight hue bias; **one** high-visibility signal spent only on confirmation / progress / primary CTA.
- Zero shadow, gradient or glass; restrained radii.
- Primary inputs ≥ 56px tall, confirm target ~64×56px, column legend once, select-all on focus so a value is corrected by typing over it.
- Self-host the font and precache it in the service worker (see the glyph caveat in `remote-direction-delivery-artifacts.md`).

## Rows that squeeze: two-line stack, not a tighter grid

When a row holds name + variable-width chips + values + a progress bar, a fixed-column grid (`name | bar | values`) squeezes at every intermediate width. Use a two-line stack:

```html
<div class="irow">
  <div class="irow-head">  <!-- display:flex; flex-wrap:wrap; align-items:center; gap -->
    <span class="dot"></span><span class="name">…</span><span class="chip">…</span>
    <span class="spacer" style="flex:1"></span><span class="amount">R$ x de R$ y</span>
  </div>
  <div class="irow-bar">   <!-- full-width bar + % beside it -->
    <div class="bar"><i style="width:62%"></i></div><span class="pct">62%</span>
  </div>
</div>
```

Corollary: if the source prototype already defines the section's layout, implement **the prototype's layout** — fitting new content into a legacy grid was the origin of the defect.

## Evidence

- ShapeOS session screen before/after, 375/768/1280 with seeded data; lint/typecheck/16 tests/build green (LR-0006).
- Cofre PR vnatividade/cofre#8 — head row height 24px, badge on one line, verified by DOM geometry (LR-0007).
