# Scroll motion pitfalls

Status: candidate pattern (consolidated 2026-09-14, pending founder review). Provenance: LR-0001, LR-0003.

## Use when

Building scroll-driven or pinned motion, per-character headline entrances, or decorative text-aligned devices (ruled lines) in vanilla or framework front ends.

## 1. Keyframe fill-mode freezes scroll-driven inline styles

An entrance animation with `animation-fill-mode: both` keeps overriding the inline `transform`/`opacity` that scroll JS writes later — the element looks frozen. Clear the animation when it ends:

```js
el.addEventListener('animationend', () => { el.style.animation = 'none'; }, { once: true });
```

## 2. Scroll-driven, reversible, with a static fallback

Drive the effect as a function of scroll progress (not a one-shot trigger), so scrolling back reverses it:

```js
const p = Math.min(1, Math.max(0, (innerHeight - rect.top) / (innerHeight + rect.height)));
ring.style.strokeDashoffset = String(length * (1 - p));
```

`prefers-reduced-motion: reduce` → render the final state statically (complete ring, assembled demo). Verify both paths (see `visual-verification-harness.md`).

## 3. Ruled lines aligned to text: use `lh`, on the heading itself

A full-bleed decorative layer behind text blocks always ends up crossing something (read as strikethrough on text and CTAs). Put the rule in the heading's own background, stepping by line height:

```css
h1 {
  background: repeating-linear-gradient(
    to bottom, transparent 0 calc(1lh - 1px), var(--rule) calc(1lh - 1px) 1lh);
}
```

## 4. Measuring text for fit-to-width

`scrollWidth` of a block element returns the container width. Measure the inline spans with `getBoundingClientRect()`.

## Evidence

- md-audio `design/atelier/direction-a.html` — animationend fix + span measurement (LR-0001).
- AuraSite `design/atelier/direction-a.html` (lh rule fix), `direction-b.html` (scroll-driven ring), `direction-c.html` (scroll-assembled demo) (LR-0003).
