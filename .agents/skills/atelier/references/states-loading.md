# States: Loading, Empty, Error

A screen isn't designed until its non-happy states are. Every data-bearing view ships the trio: loading, empty, error — designed with the same care as the content state.

## Loading — skeletons over spinners

Skeletons preserve layout and feel faster; spinners communicate nothing. Use **boneyard** (`~/.claude/atelier-deps/boneyard`) to generate pixel-perfect skeletons by snapshotting the real rendered UI into positioned "bones" instead of hand-drawing gray boxes:

- CLI `boneyard-js build` snapshots per breakpoint (`boneyard.config.json`: breakpoints, wait, colors, animation).
- Multi-framework: React/Preact/Vue/Svelte/Angular/React Native; vanilla via `renderBones()`.
- Dark mode follows the `.dark` class convention (not `prefers-color-scheme`) — align the app's theming or configure accordingly.
- Container bones aren't rendered (avoid opacity stacking); shimmer defaults are sane — respect `prefers-reduced-motion` by switching to static or pulse.

Rules: skeleton mirrors the REAL layout (no generic three-line ghost); show only after ~150–300ms delay to avoid flashes; one shimmer rhythm per page.

## Empty

An empty state is onboarding: say what would appear here, why it's valuable, and give the single next action (aligned with the brief's `primary_action`). Illustration optional; never a bare "No data".

## Error

Explain what failed in user language, preserve user input, offer retry or a path out. No apologies-without-help, no raw error codes as the primary message. Distinguish user-fixable (bad input, offline) from system errors (retry + status).

## Perceived performance

Optimistic UI for mutations the server almost never rejects; button-level busy states ("Saving…" in the button, not a page spinner); stream/stagger content in (reveals from `motion-scroll.md` double as loading choreography). Never block the whole screen for a partial fetch.
