# Stack Adapter — React Native (mínimo, legado NaAtiva)

Maintenance adapter for the existing NaAtiva app (Uber copilot, Android). New mobile ventures use `flutter.md`. This chapter grows via LearningRecords from NaAtiva work — thin by design.

## Rules in force

- **Accessibility first**: every informational view exposes text to the a11y tree — the Radar de Viagens card bug (custom-drawn content invisible to TalkBack) is the founding lesson. `accessibilityLabel`/`accessibilityRole` on any custom-rendered element; verify with TalkBack.
- **Copy**: NaAtiva voice rules apply (no emoji; "combustível"; never "no bolso" — "a corrida sai por"; objective messages; don't repeat the pill's data).
- **Motion**: Reanimated for scroll-driven work (worklets on UI thread); same scroll-position-not-time law; respect `AccessibilityInfo.isReduceMotionEnabled`.
- **States**: boneyard has React Native bones (`boneyard-js/native`) for skeletons mirroring real layout.
- **Theming**: tokens in one module; no inline hex in components.

## Verify

Real device or emulator; drive the flow; TalkBack pass on changed screens; Datadog (`service=app.naativa`) clean of new errors.
