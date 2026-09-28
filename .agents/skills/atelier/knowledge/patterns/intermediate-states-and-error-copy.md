# Intermediate states and user-facing error copy

Status: candidate pattern (consolidated 2026-09-14, extended 2026-09-28, pending founder review; LR-0012 proposes section 5 for `references/states-loading.md`). Provenance: LR-0008 (execution), LR-0009 (adversarial review of the same work, PIP-797 — two lenses reproduced each defect), LR-0012.

## Use when

- A wizard, multi-step form or choice UI invents a state between "on" and "off" (draft, pending, suggested, saved-but-not-counting).
- An error is promoted from ephemeral (toast) to persistent (panel), or any RPC/tRPC error reaches an end user.
- A button is unavailable for a reason the user should be able to reach.
- A wait is long enough that the user will wonder whether the screen is stuck.

## 1. Answered ≠ resolved

Progress must distinguish **answered** from **resolved** (answered OR deliberately skipped). Using one for the other either blocks advancing past a skipped question or promises the downstream engine an input that does not exist.

## 2. An intermediate state is three things that must agree

The reducer (what a tap does), the ARIA attribute (what is announced) and the style (what is seen) all derive from **the same variable**:

```tsx
const counts = answered && !skipped;          // the single source of truth
<button
  aria-pressed={counts}
  data-state={draftKept ? 'kept' : counts ? 'on' : 'off'}
  onClick={() => dispatch(draftKept ? { type: 'restoreDraft', id } : { type: 'toggle', id })}
/>
```

A kept draft under a skip gets its own visual (neutral ring instead of accent) and an explicit "Use my answer" action — because tapping a selected option again **deselects** it and would erase the very draft the state exists to protect. Painting the gray is not the implementation.

## 3. Transport errors never reach the user raw

A persistent panel makes the message the main text on screen; `error.message` on a network drop shows "Failed to fetch", in English, between product-language sentences.

```ts
const isServerError = Boolean(error.data?.code);   // tRPC: server errors carry metadata
const text = isServerError ? error.message : t('errors.connection'); // product-language sentence
```

Never match substrings of the message. Prove it with a negative control: a **server** error whose message is literally "Failed to fetch" must still be displayed.

(Form validation errors are different — there the server message is usually the right text.)

## 4. Unavailable button with an explanation

`disabled` removes the button from tab order and takes its `aria-describedby` explanation with it. When there is a reason to reach, use `aria-disabled="true"` plus an inert submit handler.

## 5. A long wait gets a real clock, not a fake bar

With no measurable progress, a progress bar is a lie. For the 13–35s waits in LR-0012 (a local model loading its weights on the first call), what held the screen was a **counting timer** plus a sentence that changes once the typical duration is exceeded ("on the first call the model loads its weights"). Half a minute passes without the screen reading as frozen, and nothing was promised that could not be delivered.

## 6. A frequent negative outcome is information, not an error

"Left out" was the *normal* case in LR-0012 (the local model mis-spells track names), so it is drawn in a muted neutral tone with the explanation stated once at the top of the section. Red stays reserved for system failure. A normal outcome painted as an error teaches the user to distrust the screen.

## 7. A bare number in a list needs a header

`90` right-aligned across 12 rows explains nothing. A small-caps column header plus one note for the whole list ("below 60 does not get in") resolves it without repeating a legend per row.

## Evidence

- AuraSite interview wizard `client/src/components/site/InterviewForm.tsx` (LR-0008), PR vnatividade/aurasite#78 (LR-0009).
- trilha: waiting state with a real timer, "left out" section in a muted tone, score column with a header and a single note — all seven states captured in WebKit (LR-0012).
