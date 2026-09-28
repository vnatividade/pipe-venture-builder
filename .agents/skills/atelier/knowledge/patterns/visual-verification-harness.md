# Visual verification harness

Status: candidate pattern (consolidated 2026-09-14, extended 2026-09-28, pending founder review before it graduates to `references/`; LR-0011 proposes traps 8–10 as mandatory steps in `references/audit-checklist.md`). Provenance: LR-0001, LR-0003, LR-0005, LR-0006, LR-0007, LR-0008, LR-0011, LR-0012.

## Use when

Any Atelier deliverable needs visual proof before it is declared done — directions, landings, app screens, audits of a local preview. Eight independent executions converged on the same harness and the same traps.

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
6. **Contrast is measured on the real element** (canvas + WCAG formula against the actual composed background), never inherited from docs — in LR-0008 `text-destructive` on `bg-destructive/5` measured 4.36:1 (fails AA) while the repo's primary with white measured 5.13:1, the opposite of what inherited docs suggested for both.
7. **Seed real data** through the project's sanctioned test helpers when judging app screens; empty states hide density problems.
8. **Measure before you capture, not only when something looks wrong.** In LR-0011 `getComputedStyle` revealed the headings rendering in an inherited serif, from a global `h1, h2` rule in `@layer base` — the new identity's rule needed `:is(h1, h2, h3, h4)` to win. A screenshot taken before that check would have shipped the wrong typeface as evidence.
9. **The pane's stale frame is the rule, not the exception** (second occurrence: LR-0005, LR-0011). A sheet that looks invisible and an expansion that looks empty were old frames while the DOM was already correct. Confirm with `getBoundingClientRect` / `opacity` and re-capture; never "fix" a defect seen only in the pane.
10. **Validate the console in a fresh tab.** HMR leaves stale hook errors ("deps changed size") in the tab's console buffer; a long-lived tab reports failures you did not cause and hides the ones you did.

## Harness outside the repo (locked write set, logged-in state)

When the write set forbids adding a preview route, and the state you must see is behind auth, copy the project to `/tmp`, export the subcomponents *there*, and mount a showcase of every state. LR-0012 verified seven states this way — including a real `401` observed as an interface state — with no preview route in the repo and no credentials in the harness.

The same "stay outside the repo" rule applies to references captured from a physical device: `adb -s <serial> screencap` output lives in the session scratchpad only (LR-0011). Never in the repo, never in the record.

## Evidence

- md-audio `design/atelier/screenshots/` (LR-0001: hash identical before fix, divergent after).
- AuraSite `design/atelier/screenshots/` 17 captures incl. scroll-mid and reduced-motion (LR-0003); PR vnatividade/aurasite#31, 21 captures across 5 pages × 2 viewports (LR-0005).
- Cofre PR vnatividade/cofre#8 — DOM geometry proved the fix when the pane glitched (LR-0007).
- AuraSite harness `ui.css` single-root fix (LR-0008, PIP-797).
- Finance OS `/plano`: 390px and 1280px, dark and light, mask, clean console in a new tab; 4 defects caught before delivery, two of them only visible through the DOM (LR-0011).
- trilha: seven states in WebKit at iPhone 13 viewport from a `/tmp` copy, Playwright-driven interaction, token contrast computed at 17.3 / 7.4 / 5.1 : 1 (LR-0012).
