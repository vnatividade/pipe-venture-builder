# Integrating a chosen direction into an existing app

Status: candidate pattern (consolidated 2026-09-14, pending founder review). Provenance: LR-0002 (Flask single-service + PWA), LR-0005 (React + Tailwind/shadcn SPA).

## Use when

Concierge phase 2: the founder picked a static direction and it must become the real landing/segment pages inside an app that already works, without breaking any existing flow.

## Rules

1. **Expand by reusing the direction's own devices.** New sections reuse the chosen direction's rules, type pairings, accent and motion device instead of inventing new ones; the whole page must read as one system.
2. **Scope the direction's CSS under one root class** (e.g. `.rc …`) with zero global selectors. It then coexists with the app's Tailwind/shadcn without interference in either direction.
3. **Never replicate data-bearing components.** Forms, counters and anything wired to the backend stay the app's existing components (e.g. tRPC-bound); the direction only dresses them.
4. **Don't touch app routes; add beside them.** Landing and segment pages get new routes; app routes stay untouched.

## Single-service app + landing (server-rendered / PWA)

Serve landing and app from the same service by **possession of credential** at the root:

```py
@app.get("/")
def root():
    if _user_ok(request) or not LANDING_HTML:   # cookie, ?token= or header; fallback if file missing
        return INDEX_HTML                        # installed PWA and token links keep working
    return LANDING_HTML

@app.get("/app")                                 # fixed app route: CTA destination, token form
def app_route():
    return INDEX_HTML
```

- The app HTML stays untouched; the diff is minimal and auditable.
- If the landing is read from disk at import, the container needs the file copied (Dockerfile `COPY`) and local testing needs a server restart after edits.
- Test every route state: visitor, valid/invalid token, cookie, `/app`, health, manifest, service worker.

## Evidence

- md-audio `app.py` routes `/` and `/app`, 17 final captures incl. authenticated root (LR-0002).
- AuraSite hub + 4 segment pages under a scoped root class, PR vnatividade/aurasite#31 (LR-0005).
