# A missing value is shown as missing, never invented

Status: candidate pattern (consolidated 2026-09-28, pending founder review). Provenance: LR-0010, LR-0011 (same venture, two passes; the rule held through a full redesign).

## Use when

A screen must display a number the system cannot currently compute — a business rule the founder has explicitly not decided yet, a formula named in a spec but never written, a base whose meaning is still open.

## The rule

When a rule is *documented as undecided*, the correct implementation is **not** to pick the most obvious reading and compute something. It is to take the same path the codebase already takes for "no information": return `null`, and say why on screen.

In LR-0010 the percentage base could be "salary received" (a decision the project's own doc reserved for the founder). The engine returns `null` for that base instead of quietly substituting "salary forecast" — which is precisely the bug the same pass fixed: the editor always saved `base='salario-previsto'`, silently discarding a saved `salario-recebido` and computing against the wrong number with no warning.

```ts
// not: base === 'salario-recebido' ? renda * pct : ...   ← inventing the formula
// and not: 0                                             ← reads as "nothing to allocate"
valorEmReais: base === 'salario-recebido' ? null : renda * pct
```

`null` is not `0`. Zero is a legitimate amount and will be read as one.

## But the layout must not degrade

LR-0011 redesigned the same screen and found the honest version had its own failure mode: a right-hand column of em dashes destroys the hierarchy the screen exists to show.

1. **The number on the right is never empty.** When the amount in currency does not exist, promote the percentage to principal number. The row keeps its shape.
2. **Explain the absence once, at the top** — not on every line. One sentence above the list ("the % base is not defined yet"), then silence.
3. **The explanation is copy, not an error.** No red, no warning icon: nothing is broken, a decision is pending.

## Companion bug: the field that exists in the type but is never read

The base bug in LR-0010 was found by grepping for where the field is **consumed**, not where it is declared or displayed. `VersaoRegras.base` was read for display, and never used in the calculation nor preserved on save — documented but dead. Worth a sweep on any field added "for later": every declaration should have a reader, and a writer that round-trips it.

## Evidence

- `src/finance/engine.ts` — explicit base, no invented formula; 18/18 domain assertions including "absent base becomes null, not 0" and "base 'received' uses no invented formula" (LR-0010).
- Live browser reproduction: before, the editor showed "salário previsto R$ 20.000" while the active rule said "salário recebido"; after, the selector is pre-selected with the saved value, with an explicit note that the formula is undefined and "sem base" instead of a fabricated number (LR-0010).
- The redesigned `/plano`: percentage promoted to the right-hand column, absence explained once at the top of the list (LR-0011).

Related: `honesty-contract-claims.md` (the same honesty applied to copy: every claim traced to code), `intermediate-states-and-error-copy.md` (a frequent negative state is information, not an error).
