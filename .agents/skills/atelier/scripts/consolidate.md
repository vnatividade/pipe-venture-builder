# Atelier — Weekly Consolidation Contract

Executed weekly by a scheduled Claude Code session (and on demand via "roda a consolidação do atelier"). Cadence: weekly per founder decision of 2026-07-16; revisit toward biweekly once volume stabilizes. Umbrella ticket: **PIP-665** (all output PRs run under it via the knowledge-content lane of `execution/operating-modes.md`).

## Inputs to sweep

1. Pipe module: `.agents/skills/atelier/knowledge/learnings/*.json` and `knowledge/inbox/*` (unprocessed sources).
2. Venture repos (working set — extend as ventures adopt Atelier): `~/Developer/md-audio-proxy`, `~/Developer/cofre`, `~/Developer/aurasite`, `~/Developer/palavra-da-semana` — path `design/atelier/learning-record*.json` in each.
3. Latest dependency update report: `~/.claude/atelier-deps/update-report-*.md` (most recent; note any HELD bumps).

## Steps

1. **Collect** all LearningRecords not yet consolidated (track via `knowledge/learnings/.consolidated` — a list of already-processed record ids; venture-side records are COPIED into `knowledge/learnings/` with a `source` pointer, never moved).
2. **Respect sensitivity**: records marked venture-sensitive stay summarized in generic terms in shared patterns; never copy venture-confidential specifics across ventures.
3. **Cluster** by theme (motion, typography, integration patterns, audit recurrences, prompts). A theme with 2+ independent records, or 1 record of high confidence + importance, is promotion-eligible.
4. **Promote to patterns**: for each eligible theme, write/update `knowledge/patterns/<slug>.md` — trigger ("use when…"), the canonical prompt and/or code snippet, preview screenshot or link to evidence, provenance (record ids). Patterns are the reusable galley; keep each self-contained.
5. **Update references** when a pattern graduates to house law (stable across 3+ uses or founder-endorsed): fold a distilled rule into the matching `references/*.md` chapter with provenance in `sources.md`. Contract files (SKILL routing, specialization, capability entry) are NEVER touched here.
6. **Ingest inbox**: for each item in `knowledge/inbox/`, distill per the ingest workflow (heuristics + provenance into references/sources), then remove the inbox item in the same PR.
7. **Ship**: one batch PR (branch `atelier/knowledge-<date>`) touching ONLY knowledge-content paths (knowledge/**, references distillations, sources.md). Body lists records processed, patterns created/updated, references touched, held dependency bumps. Cross-account review, autonomous merge (knowledge lane). If the PR would touch anything else, split it out and stop that part for a dedicated ticket.
8. **Log**: comment on PIP-665 (PR link + one-line summary). Update `.consolidated`.

## Empty week

If nothing new: no PR; a single PIP-665 comment "no new learnings (week of <date>); deps report: <status>". Never invent learnings to fill the cadence.
