# Stack Adapter — React / Next.js

The web-app stack of the house ventures (Lumia, Cofre, md-audio). App Router assumed.

## Foundations

- **Fonts**: `next/font/google` (self-hosted, zero layout shift) — display + body per `typography.md`; expose as CSS variables consumed by Tailwind config.
- **Tokens**: design tokens as CSS custom properties (`globals.css` `:root` + `.dark`), Tailwind mapped to tokens (`colors: { ground: 'var(--ground)' }`) — never hardcode hex in components; dark mode via the `.dark` class (matches boneyard's convention).
- **Components**: server components by default; `"use client"` only where interaction lives. Keep the client bundle for motion small.
- **Images/video**: `next/image` with real `sizes`; hero/bg video as muted `<video playsinline>` in a client component (scrub logic from `motion-scroll.md` in a `useRafScroll` hook — one listener per page via context).

## Motion

CSS-first (transitions, `@keyframes`, view transitions) for simple reveals; the scroll-scrub/pin recipes port directly (refs + one rAF). Reach for framer-motion only when orchestration genuinely needs it (layout animations, exit transitions) — it's a dependency choice, record it in the brief. Every variant respects `prefers-reduced-motion` (`useReducedMotion` or media query).

## States

- `loading.tsx` per route + component-level `<Skeleton>` from **boneyard** (`boneyard-js/react`, bones built from the real UI).
- `error.tsx` per route with user-language message + retry; empty states as first-class components with the primary action.
- Mutations: optimistic UI via `useOptimistic`/router refresh patterns; button-level pending via `useFormStatus`.

## House integration

If the venture adopts **Astryx** (React + StyleX design system), it becomes the component floor: use its components/tokens/themes and let Atelier direct composition and brand-level theming instead of building primitives. Decide per venture in the brief; don't mix two design systems.

## Verify

Dev server via preview tooling; drive real routes; check RSC/`use client` boundaries didn't break interactivity; Lighthouse-level sanity (LCP image priority, no CLS from fonts/media); then the audit pass.
