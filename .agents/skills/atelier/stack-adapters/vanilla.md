# Stack Adapter — Vanilla (HTML/CSS/JS)

The reference stack for animated brand sites and landings (the validated video workflow runs on it). Zero build step, instant preview, maximum control.

## Structure

- **Single self-contained `index.html`** for landings/prototypes: CSS and JS inlined. Survives any preview context (sandboxed file preview, dev server, artifact) and eliminates "my edit isn't showing" split-file confusion. Extract files only when the page grows past ~1.5k lines or gains real routing.
- Semantic elements (`header/nav/main/section/footer`, one `h1`); design tokens as CSS custom properties on `:root`; dark variant via `data-theme`/`.dark` re-declaring tokens only.
- Layout with flex/grid + `gap` (never margin chains); wide content in its own `overflow-x: auto` container.

## Hero recipe (canonical starting point)

1. Section `100vh`, ground pure per brief ("pure black, no gradient, no nothing" unless brief says otherwise); minimal navbar — wordmark left, ~4 links right.
2. Display headline at the bottom (~40px padding), uppercase, **filling the section width** and scaling with it; display font from Google Fonts embed (`typography.md`).
3. Motion per `motion-scroll.md`: pin wrapper + char-split fall, or scroll-scrubbed video background; `IntersectionObserver` reveals for following sections.
4. Iterate one change at a time; screenshot-verify each.

## JS discipline

No frameworks, no libraries for what the platform does: `IntersectionObserver`, `scrollIntoView`, `requestAnimationFrame`, `<dialog>`, `details/summary`, CSS `:has()`/container queries. One rAF loop drives all scroll math. Feature-detect, don't UA-sniff. Forms work without JS where possible.

## Verify

Open via dev-server preview; drive it (scroll, click, resize 375px/768px/1280px); console clean; then the audit pass.
