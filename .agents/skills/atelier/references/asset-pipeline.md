# Brand Asset Pipeline (image → video, human-in-the-loop)

Generates the brand character/background imagery and the animated backgrounds that scroll-driven sites scrub. Paid browser tools (Higgsfield, Seedance) are **executed by the human**; the agent prepares exact prompts, validates results, and integrates files. Never treat this pipeline as agent-executable.

## Flow

1. **Reference hunt** — find a mood image (Pinterest or the brief's references) and, when re-theming, screenshot the existing asset to preserve composition.
2. **Image composition** (Higgsfield GPT-Image class, or ChatGPT) — attach TWO images: the composition reference first, the new subject second. Canonical prompt:
   > "replace the [subject] in the first image with the second one; keep the background and the style of the first image"
   Works because it pins composition/lighting and swaps only the subject. When both images share the background style (e.g., both black), the keep-clause can be dropped.
3. **Image → video** (Seedance 2.0) — attach the original reference VIDEO + the new image. Canonical prompt:
   > "animate the @Image like the video attached, the motion should be the same"
   Settings: duration = same as the reference video (check it; minimum available if equal), aspect 16:9, **1080p for web** (4K only for video-platform deliverables — web pays the load cost).
4. **Integrate** — rename descriptively (`video-2.mp4`, no collisions), drop into the project, wire as muted scroll-scrubbed background (`motion-scroll.md`), no overlays unless the brief says so.
5. **Validate** — generated video must match the reference's motion and the new subject's identity; regenerate on drift. Log the winning prompt pair in `knowledge/patterns/`.

## Prompt bank rules

Reuse validated prompts before writing new ones (check `knowledge/patterns/`). A screenshot of a desired effect pasted to the model is a legitimate spec ("recreate exactly this") — for code effects too, not just images. Galleries of prompt-ready animated sites (motionsites.ai) are legitimate starting points for one-shots; treat any copied prompt as a draft to re-brand, never ship someone else's brand language.
