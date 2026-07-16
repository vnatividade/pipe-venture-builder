# Concierge Mode — Interview & Design Brief

The user should never need to know which prompt or pipeline fits each phase. That knowledge lives here. Concierge mode turns "preciso atuar na interface" into a verified interface through at most two human touchpoints: **choosing a direction** and **receiving the verified result**.

## Rule zero — bypass

If the request already carries concrete direction (exact layout, values, references), skip the interview and execute. Vague → guide; specific → build. Never interrogate an expert.

## The interview (≤5 questions, defaults offered)

Infer everything possible from the repo, brand assets, and memory first; only **confirm** inferences, never re-ask them. Then ask at most:

1. **Product & screen** — what is this? (landing / dashboard / app screen / editorial) → default: inferred from repo.
2. **Audience & context** — who, on what device, in what mood?
3. **The one action** — the single thing a visitor must do or notice. (One. Forcing this choice is half the design.)
4. **Brand mood** — 2–3 adjectives, an existing brand, or reference links/screenshots. Offer options to react to, not a blank field.
5. **Constraints** — stack (see `stack-adapters/`), deadline, existing design system (e.g., Astryx), things that must not change.

Ask in one message, with proposed defaults per question so a lazy "ok" still yields a complete brief.

## Directions — react, don't articulate

From the brief, produce **2–3 genuinely different rendered directions** (real preview HTML/screens, not descriptions): e.g., stark-typographic vs. atmospheric-media vs. editorial-structured. Each direction states its display font, ground, accent, and motion posture in one line. The user points at one (or mixes: "A com a fonte do B"). This is the taste checkpoint — the only mid-process human stop.

## The Design Brief artifact

Persist as `design-brief.md` in the target project (venture repo), versioned:

```yaml
project: <venture / screen>
date: <iso>
product_type: landing | dashboard | app-screen | editorial
audience: <who + device + context>
primary_action: <the one thing>
direction: <chosen direction name + one-line rationale>
type: { display: <font>, body: <font> }
color: { ground: <hex>, accent: <hex>, semantic: default }
motion: none | subtle | scroll-driven (see motion-scroll.md)
stack: vanilla | react-next | flutter | react-native
constraints: [...]
anti: [<explicit things to avoid for this brand>]
```

The brief feeds every downstream workflow, is the yardstick for the final audit, and becomes evidence in the LearningRecord.

## After the choice

Run the technical workflows invisibly (build → animate → audit), verifying each iteration visually. Surface progress briefly; expose internals only if asked. Deliver: verified result + one-paragraph rationale + the brief. Log the LearningRecord.
