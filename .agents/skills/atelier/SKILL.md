---
name: atelier
description: >
  READ THIS FIRST for any request to design, build, restyle, animate, audit, or
  improve a user interface — a website, landing page, web app screen, mobile
  screen, or component. Atelier is the frontend/UX/UI capability: it routes the
  request to the right workflow, carries the house design philosophy, and knows
  when to interview the user (concierge mode) versus executing directly. Use it
  instead of improvising frontend work from model defaults.
metadata: { "tags": "read-first, frontend, ux, ui, design, router, concierge, atelier" }
---

# Atelier — start here

Atelier exists because an undirected model regresses to the statistical center of the web (purple gradient, default sans, soft card shadow — "distributional convergence"). This skill is the standing direction that prevents that, plus the process knowledge so the **user never has to know which prompt or pipeline to use**.

Two rules above all:

1. **Never ship the statistical default.** Every visual choice must be traceable to the brief, the brand, or a house heuristic — not to "what pages usually look like".
2. **Never declare done without looking.** Render, screenshot or drive the preview, check against the brief and the audit checklist, then hand off.

## Intent router

| The user says (or means)… | Route |
|---|---|
| Something vague or outcome-level: "preciso atuar na interface", "quero que fique bonito", "faz a landing" | **guide** (concierge) — `references/design-brief.md` |
| Build a new site/screen with clear direction already | **build** |
| Re-theme / rebrand existing UI, swap copy or assets | **retheme** |
| "Review/audit this screen", accessibility, "por que está feio?" | **audit** — `references/audit-checklist.md` |
| "Anima isso", scroll effects, motion, hero animado | **animate** — `references/motion-scroll.md` |
| Needs brand imagery/video assets | **assets** — `references/asset-pipeline.md` |
| New source material to absorb (article, video, repo) | **ingest** — distill into `references/`, log in `references/sources.md` |

Routing law: **vague → guide; specific → execute.** When the user states exact specs ("hero 100vh preto puro, headline preenchendo a largura"), skip the interview entirely and build. When intent is outcome-level, run guide first; it produces the Design Brief that feeds every other workflow. Never answer a vague request with an interrogation nor a specific request with questions.

## Capability map — load on demand

| Need | Read |
|---|---|
| House philosophy and anti-slop rules | `references/design-philosophy.md` |
| Concierge interview + Design Brief contract | `references/design-brief.md` |
| Scroll-driven motion, hero recipes, video scrub | `references/motion-scroll.md` |
| Type selection, pairing, responsive scale | `references/typography.md` |
| Brand image/video generation pipeline (human-in-loop) | `references/asset-pipeline.md` |
| Loading/empty/error states, skeletons | `references/states-loading.md` |
| Final QA: a11y + slop audit, severity rules | `references/audit-checklist.md` |
| Stack specifics | `stack-adapters/{vanilla,react-next,flutter,react-native}.md` |
| Validated prompts/effects from past work | `knowledge/patterns/` |

Read only what the task needs. The chapters are the house **opinion**; encyclopedic depth lives in the external dependencies below.

## External dependencies (pinned in `dependencies.lock.json`)

Installed at `~/.claude/atelier-deps/` by `install.sh`; refreshed by `scripts/update-deps.sh`. Compose with them, never re-implement them:

| Dependency | Use for | Entry point |
|---|---|---|
| `skills` (Anthropic frontend-design) | Base anti-cliché direction (also available as native plugin skill) | `skills/frontend-design/` |
| `impeccable` (Bakaus) | Iteration passes: animate, quieter (de-noise), audit, document; 46 deterministic slop rules | repo root README → commands |
| `ui-ux-pro-max-skill` | Reasoning database: 67 UI styles, 161 palettes, 57 font pairs, 99 UX guidelines | repo SKILL |
| `web-interface-guidelines` (Vercel) | 100+ interface/a11y rules for the audit workflow | `AGENTS.md`, `command.md` |
| `astryx` (Meta) | Agent-ready React design system (150+ components) when a venture opts into it | `CLAUDE.md` |
| `boneyard` | Pixel-perfect skeleton screens from real UI | `.claude/skills/boneyard/SKILL.md` |
| `hyperframes` (HeyGen) | HTML→video rendering when a deliverable is a video | `skills/hyperframes/SKILL.md` |

If a dependency is missing, run `install.sh` (idempotent); if unavailable, proceed with house chapters and record the gap in the handoff.

## Operating principles (always on)

- **One change per iteration, verify, next.** Hero → font → motion → next section. Never "build the whole site" in one shot unless one-shotting from a validated pattern.
- **Numeric specificity.** Speak in exact values: `100vh`, `padding-bottom: 40px`, 4 links, `clamp(28px, 4.5vw, 56px)`.
- **Explicit anti-slop.** State what NOT to do in every generation step ("pure black, no gradient, no nothing").
- **Screenshot as spec.** A pasted reference image of an effect is a better spec than three paragraphs; reproduce what is shown.
- **React > articulate.** To resolve taste, show 2–3 rendered directions and let the user point — never force the user to describe aesthetics in words.
- **Layout-safe copy swaps.** When re-theming, keep character counts approximately equal to preserve layout.
- **Motion is scroll-position-driven, not time-driven,** so it is reversible. Respect `prefers-reduced-motion` everywhere.
- **Web media budget:** background video 1080p (not 4K), muted, playsinline, duration matched to reference.

## Learning duty (mandatory)

After every verified task, write a LearningRecord (`schemas/LearningRecord.schema.json`) to `knowledge/learnings/`: the winning prompt or pattern, the decision that worked, evidence link (screenshot/PR). Recurring learnings get promoted to `knowledge/patterns/` (prompt + canonical code + preview) and eventually to `references/` chapters by the weekly consolidation. New raw sources go to `knowledge/inbox/` for the ingest workflow. Knowledge-content batch PRs follow the exploration lane of `execution/operating-modes.md`.

## Boundaries

Atelier inherits the repository gates: check `.pipe/mode.json` (operating mode) of the target repo before opening PRs or merging; asset generation in paid tools (Higgsfield/Seedance) is prepared by the agent and executed by the human; production deploys and the other absolute gates always require human approval.
