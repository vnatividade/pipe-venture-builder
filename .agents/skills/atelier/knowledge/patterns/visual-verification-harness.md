# Visual verification harness

Status: candidate pattern (consolidated 2026-09-14, pending founder review before it graduates to `references/`). Provenance: LR-0001, LR-0003, LR-0005, LR-0006, LR-0007, LR-0008.

## Use when

Any Atelier deliverable needs visual proof before it is declared done — directions, landings, app screens, audits of a local preview. Six independent executions converged on the same harness and the same traps.

## Canonical harness

`playwright-core` driving the system Chrome, capturing viewport shots at desktop and mobile widths plus a reduced-motion pass.

```js
import { chromium } from 'playwright-core';

const browser = await chromium.launch({ channel: 'chrome' });
const ctx = await browser.newContext({
  viewport: { width: 1280, height: 800 },     // repeat at 375x812 (and 768x1024 for apps)
  reducedMotion: 'no-preference',              // explicit: macOS Reduce Motion leaks into headless
});
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'networkidle' });

// 0. Prove the theme compiled before judging anything (see trap 3)
const probe = await page.evaluate(() => {
  const el = document.querySelector('.bg-primary, [class*="bg-primary"]');
  return el && getComputedStyle(el).backgroundColor;
});
if (!probe || probe === 'rgba(0, 0, 0, 0)') throw new Error('theme utilities not generated — harness is lying');

await page.screenshot({ path: 'hero-1280.png' });

// fullPage: force scroll reveals, then wait >= transition duration
await page.evaluate(() => document.querySelectorAll('[data-reveal], .reveal')
  .forEach(el => el.classList.add('is-visible')));
await page.waitForTimeout(650);                // 500ms fade + margin
await page.screenshot({ path: 'full-1280.png', fullPage: true });

// reduced-motion path is a separate context with reducedMotion: 'reduce'
```

## Rules

1. **Shoot both motion paths.** Default motion and `reducedMotion: 'reduce'` each get captures; set `no-preference` explicitly or the host OS setting silently decides which one you validated.
2. **fullPage does not scroll.** IntersectionObserver reveals below the fold never fire, so fullPage captures look empty. Force the revealed state and wait at least the transition length (otherwise blocks come out semi-transparent). Viewport captures at scroll positions still validate the real motion; capture a scroll-mid frame for scroll-driven effects.
3. **Prove the theme resolves first.** A preview/harness that mounts components from outside the bundler root can open a second Tailwind root without the app's `@theme` — every semantic utility (`bg-primary`, `text-muted-foreground`) computes to transparent and all visual rounds on it are worthless. Fix: one root only (import the app's CSS entry and `@source` the component folder).
4. **Measure, don't eyeball.** When a pane or screenshot disagrees with expectation, read the DOM (`getBoundingClientRect`, `getComputedStyle`) before "fixing" anything: embedded browser panes can show stale compositor frames after scroll while the DOM is correct. Fall back to the harness above.
5. **Transitions contaminate measurements.** `transition-colors`/`transition-all` return intermediate (oklab) values for ~150ms; re-measure in a separate call before reporting a color defect.
6. **Contrast is measured on the real element** (canvas + WCAG formula against the actual composed background), never inherited from docs — tinted backgrounds like `destructive/5` routinely fail AA where the doc says pass.
7. **Seed real data** through the project's sanctioned test helpers when judging app screens; empty states hide density problems.

## Evidence

- md-audio `design/atelier/screenshots/` (LR-0001: hash identical before fix, divergent after).
- AuraSite `design/atelier/screenshots/` 17 captures incl. scroll-mid and reduced-motion (LR-0003); PR vnatividade/aurasite#31, 21 captures across 5 pages × 2 viewports (LR-0005).
- Cofre PR vnatividade/cofre#8 — DOM geometry proved the fix when the pane glitched (LR-0007).
- AuraSite harness `ui.css` single-root fix (LR-0008, PIP-797).
