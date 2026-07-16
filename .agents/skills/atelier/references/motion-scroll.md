# Motion & Scroll-Driven Animation

House law: **animation is a function of scroll position, not of time.** Scrolling back reverses it exactly. This one constraint produces motion that feels engineered instead of decorated. Respect `prefers-reduced-motion` in every recipe (reduce to opacity-only or none).

## The pin pattern (foundation)

```
.hero-pin { height: 250vh; }            /* scroll room; a tuning knob */
.hero     { position: sticky; top: 0; height: 100vh; }
```

A rAF-throttled scroll listener computes progress 0→1 from the pin wrapper's position; every animated property is a pure function of that progress. Beware: `overflow-x: hidden` on `html/body` implicitly forces `overflow-y: auto` and breaks `position: sticky` — don't set it on the page root.

## Recipes (validated)

**Char-split headline fall.** Split the headline into `<span class="char">` via JS. Per char, staggered left→right across progress: `translateY` (fall) + `scale` (squish: compress vertically, widen slightly) + `opacity` (fade). Full-width display headline that scales with the section (fit text to container width).

**Scroll-scrubbed video.** Muted, `playsinline`, no controls. Each frame: `target = progress * video.duration; current += (target - current) * 0.15` (lerp kills seek jitter); set `video.currentTime = current`. Same property/lerp for every scrubbed video on the page so they feel like one system. 1080p for web, duration matched to the source reference.

**Viewport reveals.** `IntersectionObserver` adds `.in-view`; lines/cards animate from blurred + slightly scaled-down + offset to sharp/full, with staggered delays so each element enters in sequence.

**Rising panel.** Full-screen panel rises from the bottom over the previous section, driven by scroll progress, rounded top edge; behind it, a scroll-scrubbed video background. Give the new section `position: relative; z-index: 1` so it paints above fixed/sticky media.

**Text drum / manifesto.** Scroll-driven stack of statement lines: active line sharp and bright, neighbors with depth blur + opacity falloff; keywords emphasized (weight/color). Reads as a drum rotating through convictions.

## Tuning

Expose independent knobs — gap-before (`min-height` of the intro), speed-during (`RISE_PHASE_END`-style progress span), stagger step — so feel is tuned without re-architecting. Typical fixes observed: rise span 0.04→0.12 of progress (~3× slower reveal), intro gap 55vh→35vh.

## Performance rules

Animate only `transform` and `opacity` (compositor-friendly); never top/left/width. One rAF loop per page, not per element. Kill listeners on unmount. Test on a mid-range phone before calling motion done — "no lagging on any device" is part of the spec, not a hope.
