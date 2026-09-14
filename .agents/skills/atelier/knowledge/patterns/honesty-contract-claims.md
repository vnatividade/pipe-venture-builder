# Honesty contract: every claim traced to code

Status: candidate pattern (consolidated 2026-09-14, pending founder review; LR-0005 proposes it as a standard section of `references/design-brief.md`). Provenance: LR-0003, LR-0005.

## Use when

Writing or rewriting product copy for a landing, segment page, FAQ or onboarding — especially when inheriting copy from an earlier direction or mockup.

## Procedure

1. **Map the real journey before writing copy.** Delegate a read-only sweep (Explore agent) that returns a table:

   | Claim | Source (file:line) | Verdict |
   |---|---|---|
   | "<claim as written>" | `path/to/file.ts:42` | can say / cannot say / say with limit |

2. Drop or rewrite every claim the code does not sustain. Typical casualties: "always in sync" with no scheduled re-sync; delivery times that contradict the real pipeline; guarantees whose justifying process no longer exists.
3. Turn limitations into direct answers instead of hiding them (FAQ: "Does it update by itself? Not yet.").
4. The table becomes a section of the venture's `design-brief.md` and a criterion of the audit gate (brief fidelity).
5. **Mockups never simulate evidence.** Counters, metrics and testimonials that are not real become labeled placeholders ("your services", "your testimonials") — no fictional personas.
6. Regulated segments keep their constraints in copy (e.g. health professionals: council-compliant tone, no promise of results); retail segments speak their own channel. Segment copy is re-verified against the same table.

## Evidence

- Design brief with the claim→source table, PR vnatividade/aurasite#31 (LR-0005, PIP-668).
- Labeled placeholders instead of invented metrics in phase 1 directions (LR-0003).
