# Portable Installation And First Run

PIP-709 provides the repository-local portability layer for Pipe: the canonical `ProductManifest`, plan-first `pipe bootstrap`, read-only `pipe doctor`, and toolkit resolution that does not place machine-specific paths in product artifacts.

This setup does not provision credentials, authenticate connectors, install production services, change operating mode, or configure Hermes/Atelier adapters. Those capabilities remain separate governed tickets.

## Prerequisites

- Python 3.11 or newer
- Git
- a versioned clone of `pipe-venture-builder`
- one product repository, normally created from this template or selected for brownfield adoption
- at least one supported executor binary: Hermes, Codex, or Claude Code

See the [platform matrix](platform-matrix.md) for current support and validation depth.

## Install The CLI From A Clone

macOS or Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install .
pipe version
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install .
pipe version
```

The toolkit root resolves in this order:

1. explicit `--toolkit-root`
2. machine-local `PIPE_TOOLKIT_ROOT`
3. the source checkout that contains the installed module, when available
4. the current directory and its parents

No home-directory or founder-specific fallback exists. `PIPE_TOOLKIT_ROOT` is machine-local configuration; its value is never written to `.pipe/project.json` or printed by `doctor`.

For a non-editable installation, keep the versioned toolkit clone and either pass `--toolkit-root /path/to/pipe-toolkit` or configure `PIPE_TOOLKIT_ROOT` in the local shell/session.

## Review The Bootstrap Plan

Run from the product repository root or pass that root as the first positional argument:

```bash
pipe bootstrap /path/to/product \
  --toolkit-root /path/to/pipe-toolkit \
  --product-id example-product \
  --entry-mode adopt \
  --plan \
  --json
```

`--plan` is the default; `--dry-run` is an equivalent alias. Both perform no writes. Initial bootstrap requires a `product-id` and `entry-mode` (`idea` or `adopt`). The default desired runtime is Hermes, with Codex and Claude Code as fallbacks, and Agent Atelier is the default selected capability.

Optional, non-secret bindings can be declared with:

```bash
--linear-project-id <stable-project-id>
--github-repository <owner/repository>
```

These fields do not authenticate anything. Never pass a token, credential, customer identifier, production identifier, private URL, or credential-bearing clone URL.

## Apply The Reviewed Plan

Repeat the same command with `--apply`:

```bash
pipe bootstrap /path/to/product \
  --toolkit-root /path/to/pipe-toolkit \
  --product-id example-product \
  --entry-mode adopt \
  --apply \
  --json
```

Apply creates only:

- `.pipe/`, when it does not exist
- `.pipe/project.json`, using the canonical [ProductManifest schema](../../schemas/ProductManifest.schema.json)

It never creates or changes `.pipe/mode.json`; operating-mode activation is human-only. It never overwrites an existing manifest, follows a manifest or `.pipe` symlink, stores absolute paths, or copies credentials. Repeating bootstrap with the same effective configuration returns `unchanged` and preserves identical file bytes.

If an existing manifest differs, bootstrap returns `BOOTSTRAP_CONFLICT`. Use the reviewed [migration process](migrations.md); do not delete or replace the file casually.

After apply, bootstrap automatically runs the same checks as `pipe doctor`. The manifest may be created successfully while the command returns readiness exit code `9` if a required local prerequisite is still missing.

## Run Doctor

```bash
pipe doctor /path/to/product \
  --toolkit-root /path/to/pipe-toolkit \
  --json
```

Doctor is read-only. It checks:

- platform, architecture, Python, toolkit, and version compatibility
- ProductManifest and canonical schemas
- `.pipe/mode.json` validity without changing it
- exact local Git root and intended repository write permission
- selected capabilities and repository-relative references
- Hermes, Codex, and Claude Code executable availability
- runtime capability/adapter registry entries and fallbacks
- declared Linear/GitHub bindings without inspecting credential values
- manifest path portability

Individual checks use these states:

| State | Meaning |
|---|---|
| `configured` | The local prerequisite or contract is usable. |
| `unavailable` | A file, binary, binding, or registry entry is absent. |
| `unauthorized` | The binding exists but Pipe did not inspect or receive authorization, or intended writes are not permitted. |
| `incompatible` | A schema, version, platform, or identity does not match the supported contract. |
| `blocked` | A policy or safety condition prevents use. |
| `not_applicable` | The check does not apply to the current manifest or ticket stage. |

Overall status is `ready`, `ready_with_warnings`, `blocked`, or `not_configured`. A diagnostic that executes successfully but finds required readiness gaps returns exit code `9`; `ready` and `ready_with_warnings` return `0`.

Connector authentication is deliberately reported as `unauthorized` when a binding is declared: PIP-709 does not read credentials or call external systems. PIP-710 owns read-only Linear/GitHub adapters. Hermes may be installed locally while its registry adapter remains `unavailable`; Codex or Claude Code can satisfy the fallback until PIP-713 lands.

## Continue Into Product Intake

After bootstrap and an acceptable doctor report:

```bash
pipe idea brainstorm.md --json
pipe adopt /path/to/existing-product --json
```

Both commands resolve the local toolkit without requiring a product manifest to contain its installation path. Their generated ProductBaseline remains `review_required` and does not authorize implementation or external mutation.

## Safety Boundary

Bootstrap and doctor do not:

- read, store, print, rotate, or transmit credentials
- inspect customer or production data
- authenticate or mutate Linear/GitHub
- install executors, plugins, paid services, or production integrations
- change operating mode or governance policy
- contact customers or send external communication
- deploy anything

Manifest and error rendering is schema-constrained and redacted. This is a defensive boundary, not a general secret scanner or a security/compliance certification.
