# Direction needs a named provenance ("functional" is not "designed")

Status: candidate pattern (consolidated 2026-09-28, pending founder review; LR-0012 targets `references/typography.md` and requires human review for that promotion). Provenance: LR-0011 (high importance), LR-0012 (high importance) — two independent ventures, same rejection.

## Use when

A screen is being designed or restyled and the request is for **direction** (not a bug fix, not an extension): a first pass, a "make this better", a "está fraco". Also use immediately after a founder rejects a delivery that works.

Both records here start at the same place: the delivery was functional, typechecked, tested, visually verified — and rejected anyway.

- LR-0011 (Finance OS `/plano`): a working editor rejected for overlapping fields and no hierarchy.
- LR-0012 (trilha): inline styles correctly refactored into CSS Modules with a system stack (`ui-serif` = New York on iOS) rejected as *"está fraco — fonte, tamanhos, disposição, hierarquia visual, de cor, tipográfica e de ação. Vai atrás, pesquisa referências"*.

The system font renders beautifully and still read as **"they didn't choose a font"**. Sober defaults with no provenance read as absence of direction, not as restraint.

## Procedure

1. **Get a concrete reference before writing any CSS.** Not adjectives — artifacts.
   - Ask the founder what they already admire, and take it literally. In LR-0011 the founder pointed at an app open on their own phone; the equivalent screens were captured off the physical device (`adb -s <serial> screencap`, navigation taps only) and read as the spec.
   - With no app to point at, research the printed/graphic repertoire of the domain. LR-0012 landed on ECM Records (dynamic emptiness, asymmetric type blocks) and Blue Note / Reid Miles (one dominant focus per piece, hierarchy by **scale**, display serif for the title, small sans for the track list, metadata as a catalogue number).
2. **Extract principles, and name them.** Write down what the reference *does* — "ring with gaps and rounded caps, total in the centre, expandable row whose children have no card of their own" — so the decision survives a review without the reference in the room.
3. **Put the provenance in the CSS**, at the top of the token block. That is where review looks. A token file whose header cites who used the family, in what, and why is defensible; the same tokens with no header are taste.
4. **Own font, from your own repo.** `next/font/local` (or an equivalent local loader) with an OFL `woff2` committed next to a README naming origin and licence: a real typeface, no new dependency in `package.json`, no third-party request, no CLS. This is what dissolved the usual "no new dependency" objection in LR-0012 (Bodoni Moda variable for display + Archivo variable, `wdth` axis, for UI/metadata).
5. **Resolve action hierarchy by mode, not by button size.** Form and result on one screen always produce competing primary actions. One state per mode (compose | waiting | result | notice) leaves exactly one primary action, and only that one gets the solid light fill; everything else is outlined.
6. **Hierarchy beats density.** One question per screen (LR-0011: *how does the income divide?*), the big number in the centre, rows as `chip + name + rule` on the left and **one** number on the right, editing in a per-item sheet instead of an inline form.

## Hard boundary — the reference lends interaction, never identity

Take patterns of interaction, motion, and hierarchy. Never the brand, the icon, the assets, or the palette.

Where the reference's colour was arbitrary, LR-0011 re-derived it from the data's own meaning — warm = ceiling, cool = floor — so the palette carries financial semantics instead of copying a choice that meant nothing here. Reference captures containing personal data stayed in the session scratchpad; nothing entered the repo or the record.

## Sequencing: logic is autonomous, interface is gated

Recorded by the founder in LR-0010 and borne out by both rejections here: **logic the agent validates alone; interface the founder validates.** A task that produces both is split — the engine change can close on its own evidence, the screen stays out of "done" until the founder sees it. Skipping step 1 does not save the round trip, it spends it: in both records the reference was gathered *after* the rejection, and gathering it first is the whole lesson.

## Evidence

- Finance OS `/plano`: segmented ring with income in the centre, areas as expandable surfaces at 3 levels, bottom sheet per item; captured at 390px and 1280px, dark and light; 68 domain cases; 4 defects caught by verification before delivery (LR-0011).
- trilha: `src/app/globals.css` with the cited references in the header, modular 1.25 scale (13/16/20/25/31/39/49), 4pt grid, 3 measured text levels + 1 accent (17.3 / 7.4 / 5.1 : 1); seven states captured in WebKit at iPhone 13 viewport (LR-0012).

Related: `density-before-palette.md` (when density, not colour, is the real defect), `visual-verification-harness.md` (proving the direction actually renders).
