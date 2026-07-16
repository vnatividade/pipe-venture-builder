# Stack Adapter — Flutter (mobile multi-plataforma)

Primary mobile stack for new ventures (founder decision 2026-07-16): one codebase, consistent rendering on Android and iOS.

## Theming = the design system

Everything flows from `ThemeData` — never inline styles per widget:

- `ColorScheme.fromSeed(seedColor: brandAccent, brightness: …)` then override the tokens the brief pins (ground, surface, accent); both `light` and `dark` schemes always.
- `TextTheme` with the brief's faces via `google_fonts` (`GoogleFonts.michromaTextTheme()`-style for display slots, body face for body slots); apply `typography.md` scale logic (display large ≈ clamp equivalent via `MediaQuery` size classes).
- Material 3 on (`useMaterial3: true`); shape/elevation tokens set once in the theme (the "quieter" rule: restrained radii and shadows globally, not per-card).

## Layout & responsiveness

`LayoutBuilder`/size classes for phone-vs-tablet; content max-widths on large screens; spacing via a fixed scale (4/8/12/16/24/32) as constants — no magic numbers per screen. Touch targets ≥ 48dp (Material floor).

## Motion

- Scroll-driven: `CustomScrollView` + slivers (`SliverAppBar` pinned = the pin pattern; `SliverPersistentHeader` for rising panels); drive custom effects from a `ScrollController` position mapped to 0→1 progress — same reversibility law as web.
- Reveals: `AnimatedOpacity`/`AnimatedSlide`/`TweenAnimationBuilder` triggered by visibility (`VisibilityDetector`) with staggered delays; implicit animations first, explicit `AnimationController` only for orchestration.
- Respect `MediaQuery.of(context).disableAnimations` — reduce to opacity/none.
- Hero transitions (`Hero` widget) for entity continuity between screens.

## States

`FutureBuilder`/state-management-agnostic trio per screen: skeleton (shimmer package or hand-built bones mirroring the real layout — boneyard has native/RN bones formats to mirror), designed empty state with the primary action, error with retry. Button-level busy states.

## Accessibility & verify

`Semantics` labels on every meaningful non-text element (the NaAtiva lesson: a custom-painted card with no semantics is invisible to TalkBack); contrast via theme tokens; test with TalkBack/VoiceOver. Verify on a real device/emulator: drive the flow, screenshot both themes, check jank (`flutter run --profile`, no frames > 16ms in scroll paths); golden tests for key screens once direction stabilizes.
