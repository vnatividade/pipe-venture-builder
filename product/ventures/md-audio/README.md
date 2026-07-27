# md-audio — Venture Product Artifacts

Pipe-governed product artifacts for the house venture **md-audio** (app name "Meus Áudios"): a personal tool that turns Markdown documents into pt-BR mp3 audio.

Implementation repository: [`vnatividade/md-audio-proxy`](https://github.com/vnatividade/md-audio-proxy) (public). It declares `exploration` mode in its own `.pipe/mode.json` (activated 2026-07-16, PIP-661), so the autonomous execution loop applies there too — production deploy stays founder-gated.

Linear project: [md-audio](https://linear.app/pipe-venture-builder/project/md-audio-951677fb7620).

## Source Boundary

Read directly from the md-audio-proxy repository at `main` (clone of 2026-07-27):

- `app.py` (843 lines) — the entire Railway app: Flask façade, job queue, PWA, and the app UI as an inline HTML string
- `requirements.txt`, `Dockerfile`, `.pipe/mode.json`
- `design/atelier/design-brief.md` — Atelier design brief, closed by founder decisions of 2026-07-16
- `landing.html` — public landing (direction B "Lampião")

Also read: Linear PIP-661 (Atelier pilot on md-audio) and its comments.

**Not inspectable from a cloud session, but now read:** the Mac Studio worker that performs the Kokoro TTS lives in `~/Developer/md-audio-site` (`main` @ `2c2d09f`) — reachable on the founder's machine, from no remote repository. PIP-719 read it locally and recorded its full Markdown handling in `audiobook-markdown-profile-draft.md`, which closed the keystone gap of the intake feature.

## Product Truth

Architecture, from `app.py` docstring and routes:

```txt
browser  --POST /synthesize-->      creates job (pending), returns job_id
Mac worker --GET  /jobs/next -->    claims a pending job (becomes processing)
Mac worker --POST /jobs/<id>/result --> delivers mp3 (becomes done)
browser  --GET  /result/<id>  -->   downloads the mp3 when ready
```

- **The Railway app performs no TTS and never parses Markdown.** `/synthesize` reads the uploaded bytes, decodes UTF-8, and stores the string in an in-memory job dict; the worker fetches it verbatim via `/jobs/next`. All Markdown handling happens on the Mac Studio worker.
- Stack: Flask 3.0.3 + gunicorn only (`requirements.txt` is two lines). One worker, eight threads, in-memory queue under a lock. Docker → Railway. **No build step, no framework, no database, no AI dependency.**
- Auth: a single shared `APP_TOKEN` via `X-App-Token` header, form field, `?token=`, or the `md_auth` cookie. Personal tool, one token — not multi-user accounts.
- Input today: **file upload only** — `<input type="file" accept=".md,.markdown,text/markdown,text/plain">`, max 2 MB (`MAX_MD_BYTES`).
- Voices: `pm_santa`, `pm_alex` (male), `pf_dora` (female); speech speed 0.8×–1.3×; voice preview before generating.
- Playback: 1×/1.25×/1.5×/2×, ±15s skip, resume from last position (localStorage per item).
- History: **IndexedDB on the device**, storing the mp3 blobs (pin, rename, search, delete). There is no server-side library — jobs expire from memory after `JOB_TTL` (30 min).
- **A pause command already exists**: writing `pausa de 5 segundos` or `pausa de 1 minuto` in the text inserts silence. It is surfaced as a tip in the UI and interpreted by the Mac worker.
- Routes: `/` serves the app to tokened visitors and `landing.html` to everyone else; `/app` always serves the app.
- Design tokens (Lampião theme): ground `#14110E` dark / `#F5EFE4` light, accent `#E8A33D` / `#B4741A`, display serif Iowan Old Style in the app, Fraunces + Instrument Sans on the landing.
- No analytics, telemetry, or event tracking of any kind — only `/health` (worker online, pending count).

## Corrections To Earlier Assumptions

An earlier draft of this plan (2026-07-27, before repository access) assumed md-audio was a Next.js App Router product with server actions and a server-side library, and put a Claude API structuring call in the critical path. All of that was wrong:

| Earlier assumption | Actual |
|---|---|
| React / Next.js App Router | Flask serving a single inline HTML string; vanilla JS, no build step |
| Server-side library model | IndexedDB on the device; server memory is a 30-minute queue |
| Player keys on H1/H2 chapter structure | No — the worker strips the `#` and speaks the heading inline. It contributes zero structural audio behavior; every pause must come from the transform (PIP-719) |
| LLM structuring pass as MVP core | No AI dependency exists; adding one needs an API key, which is an absolute approval gate |
| File upload out of scope, paste is the input | File upload is the *only* input today; paste is the new thing |

The Next.js assumption came from `.agents/skills/atelier/stack-adapters/react-next.md`, which lists md-audio among React ventures. That listing is inaccurate for this repository; the Atelier design brief itself records `stack: vanilla`. Filed for correction as **PIP-724**.

## Artifacts

- `feature-universal-text-intake.md` — feature plan: paste raw text or raw markdown, transform it into speakable markdown, generate audio.
- `audiobook-markdown-profile-draft.md` — the speakable-markdown contract the transform emits.
