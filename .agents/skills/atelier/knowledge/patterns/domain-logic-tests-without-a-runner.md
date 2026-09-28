# Domain logic tests in a project with no test runner

Status: candidate pattern (consolidated 2026-09-28, pending founder review). Provenance: LR-0010, LR-0011, LR-0012 — three consecutive executions, two ventures, same technique.

## Use when

An Atelier task touches domain logic (money, distribution, matching, scheduling) in a prototype that has no `vitest`/`jest` installed, and installing one is out of the write set. Screenshots cannot prove arithmetic; the logic still needs evidence before the screen is judged.

## The trap

The project uses bundler-style extensionless imports (`./format`, not `./format.ts`). A plain `node script.mjs` fails with `ERR_MODULE_NOT_FOUND` **even on Node 22+ with native type stripping** — the type stripping works, the resolution does not.

The tempting fallback is to re-create a copy of the engine in a flat `.mjs` and assert against that. Do not: it is an anti-pattern already present in this repo's history (the `handoff/baseline-tests` copies, which the project's own `CLAUDE.md` warns about precisely because they are not wired to `src`). A test that passes against a copy proves nothing about the shipped code.

## The technique

Look in `node_modules/.bin` for a loader that already does bundler-style resolution — `jiti`, `tsx`, `vite-node`. One of them is almost always there transitively. In all three records `jiti` resolved on the first try, with nothing added to the project.

```bash
ls node_modules/.bin | grep -E 'jiti|tsx|vite-node'
node_modules/.bin/jiti scratchpad/test-distribuicao.mjs   # imports the real src
```

Rules:

1. **Import the real `src`.** That is the entire point.
2. **The script is ephemeral** — it lives in the session scratchpad, never in the repo, unless the project asks for a suite.
3. **Assert the refusals too**, not just the happy path: fourth level rejected, cycle detected, non-existent parent detected, sum > 100% invalid, absent base becomes `null` and not `0`, the two-argument call still works.
4. **Prove the suite can fail.** LR-0012 ran 5 deliberate mutations against a 68-case suite and confirmed each was caught. A green suite that no mutation turns red is decoration.
5. **When the project does have a script** (`npm run verificar`), run it and report its count instead of inventing a parallel harness.

## Depth extension with compatibility

A recurring shape in these records: generalising a function from N to N+1 levels (2 → 3 in LR-0010) while few call sites exist. Give the new parameter a default — old call sites keep working untouched until they are updated deliberately.

This is not only convenience: it separates **logic change** (the agent validates alone) from **interface change** (waits for founder review) even when both were born from the same task. See the sequencing note in `direction-needs-named-provenance.md`.

## Evidence

- 18/18 assertions via `jiti` against the real `src/finance/engine.ts`, with `tsc --noEmit` and `npm run build` clean before and after (LR-0010).
- 68 domain cases in `tests/dominio/plano-da-casa.mjs` via `jiti` against the real `src` (LR-0011).
- 68 tests green through `npm run verificar`, with 5 mutations confirmed caught (LR-0012).

Related: `worktree-isolation-and-e2e-baseline.md` (proving a failure pre-dates your change), `visual-verification-harness.md` (the visual half of the same evidence bar).
