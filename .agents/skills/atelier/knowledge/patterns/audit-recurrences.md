# Audit recurrences (check before the gate)

Status: candidate pattern (consolidated 2026-09-14, extended 2026-09-28, pending founder review). Provenance: LR-0002, LR-0005, LR-0006, LR-0008, LR-0009, LR-0010, LR-0011, LR-0012.

## Use when

Right before running `references/audit-checklist.md` on a landing or app screen. These findings recurred across independent executions; checking them up front saves a gate round.

## Pre-gate sweep

| Recurrence | Typical severity | Check | Source |
|---|---|---|---|
| Nav link touch targets < 44px | P2 | measure link boxes at 375px | LR-0002 |
| Missing `<main>` landmark | P2 | one `<main>` per page | LR-0002 |
| Zoom disabled in viewport meta | P1 | no `user-scalable=no` / `maximum-scale=1` | LR-0005 |
| Text contrast below AA | P1 | measure on the real element, tinted backgrounds included | LR-0005, LR-0008 |
| Visual state and `aria-pressed` disagree | P1 | same variable drives both | LR-0009 |
| Raw transport error shown to end user | P1 | server vs transport error split | LR-0009 |
| `disabled` hides the explanation from keyboard/AT | P2 | `aria-disabled` when a reason exists | LR-0009 |
| Glyph-as-icon missing after font subset | P2 | inline SVG + `aria-label` on the control | LR-0006 |
| E2E failures blamed on the UI change | — | run baseline in a worktree first | LR-0006 |
| Global `h1, h2` rule overrides the identity font | P1 | `getComputedStyle` on a heading; identity rule needs `:is(h1..h4)` | LR-0011 |
| `position: sticky; bottom` that does not pin | P2 | the element must be the **last child** in the flow, after the list it floats over | LR-0012 |
| Defect seen only in the browser pane | — | confirm via DOM before fixing; panes show stale frames | LR-0005, LR-0011 |
| Edit draft created before store hydration | P1 | wait for the hydrated flag on a deep link, or the draft is born from sample data and save overwrites the real record | LR-0011 |
| Sheet/dialog raises the mobile keyboard on open | P2 | prevent Radix `onOpenAutoFocus`; focus only on a newly created item | LR-0011 |
| Cascade delete leaves orphans | P1 | removing a parent removes its subtree | LR-0010 |
| Pre-existing layout defect charged to this diff | — | compare against a BEFORE screenshot; report separately | LR-0010 |
| Field declared in the type but never read | P1 | grep for where it is **consumed**, not declared | LR-0010 |

Details and snippets: `visual-verification-harness.md`, `intermediate-states-and-error-copy.md`, `worktree-isolation-and-e2e-baseline.md`, `remote-direction-delivery-artifacts.md`, `direction-needs-named-provenance.md`, `missing-value-visible-not-invented.md`, `domain-logic-tests-without-a-runner.md`.
