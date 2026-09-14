# Worktree isolation and E2E baseline

Status: candidate pattern (consolidated 2026-09-14, pending founder review; LR-0006 proposes the baseline rule for `references/audit-checklist.md`). Provenance: LR-0003, LR-0005, LR-0006.

## Use when

- The venture repo has someone else's work in progress (staged or unstaged, other branch) and Atelier must build without touching it.
- A UI refactor touches screens covered by E2E and the question "did I break it?" must be answered honestly.

## Clean tree without touching anyone's index

```sh
git worktree add ../<repo>-atelier -b atelier/<slug> main   # no stash, no reset
# build, commit and push from the worktree
```

pnpm repos with a pinned `packageManager`: install inside the worktree with `npx pnpm@<pinned-version> install` — a different global pnpm may refuse the lockfile.

## Baseline before blaming the change

```sh
git worktree add /tmp/<repo>-baseline HEAD
ln -s "$PWD/node_modules" /tmp/<repo>-baseline/node_modules   # plus workspace node_modules if any
# run the same E2E suite against the same backend in both trees
```

Compare the exact pass/fail sets. Identical sets = the refactor is neutral; the failures are environment (ambiguous seed data, a sync queue that never drains, unavailable mic, login-helper races). Without the baseline those failures get attributed to the refactor and correct work gets reverted.

## Evidence

- Founder WIP preserved via worktree during AuraSite phase 1 (LR-0003).
- pnpm pin mismatch in a worktree (LR-0005).
- ShapeOS: baseline and post-change both failed scenarios 1/3/5/6 and passed 2/4 — proof of neutrality (LR-0006).
