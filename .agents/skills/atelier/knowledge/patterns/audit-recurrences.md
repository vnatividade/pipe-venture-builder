# Audit recurrences (check before the gate)

Status: candidate pattern (consolidated 2026-09-14, pending founder review). Provenance: LR-0002, LR-0005, LR-0006, LR-0008, LR-0009.

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

Details and snippets: `visual-verification-harness.md`, `intermediate-states-and-error-copy.md`, `worktree-isolation-and-e2e-baseline.md`, `remote-direction-delivery-artifacts.md`.
