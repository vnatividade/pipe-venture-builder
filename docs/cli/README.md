# Pipe CLI Foundation

PIP-706 introduces the first executable, read-only Pipe commands. This is the shared CLI foundation for the later `idea`, `adopt`, bootstrap, reconciliation, Hermes, and Atelier tickets; those later behaviors are not implemented here.

## Requirements

- Python 3.11 or newer
- a local clone containing `schemas/ProductBaseline.schema.json`
- no credentials, connector access, customer data, or production data

The current schema resolver expects a Pipe repository root. Portable toolkit/product manifests and `pipe doctor` belong to PIP-709.

## Install In An Isolated Environment

macOS or Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install .
pipe --help
pipe version
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install .
pipe --help
pipe version
```

If another executable named `pipe` is already installed, use `python -m pipe_venture_builder` or inspect the selected command with `command -v pipe`/`Get-Command pipe`.

## Commands

### Show version

```bash
pipe --version
pipe version
pipe version --json
```

### Discover the repository root

From anywhere inside a Pipe repository:

```bash
pipe root
pipe root --json
pipe root path/to/nested/directory
```

Discovery walks upward and requires:

- `schemas/ProductBaseline.schema.json`, and
- `.pipe/` or `AGENTS.md`.

It never falls back to a user-specific home or `Developer` directory.

Root precedence is deliberately small in this foundation: an explicit `--root`/start location wins; otherwise the command starts from the current working directory. Environment-variable and manifest configuration is deferred to PIP-709 so it cannot become an undocumented second source of truth.

### Validate ProductBaseline

```bash
pipe baseline validate path/to/product-baseline.json
pipe baseline validate path/to/product-baseline.json --json
pipe baseline validate path/to/product-baseline.json --root path/to/repository
```

Use `--schema` only to select a schema inside the discovered root or an explicitly approved absolute schema path:

```bash
pipe baseline validate baseline.json \
  --root . \
  --schema schemas/ProductBaseline.schema.json
```

The command checks:

- valid JSON for the input and schema
- the canonical schema itself against Draft 2020-12
- all ProductBaseline constraints and local references
- declared formats such as RFC 3339 date-time values

Validation errors include a JSON Pointer, the failed rule, and a sanitized explanation. They do not echo the invalid instance value. At most the first 50 findings are rendered; when more exist, the message states the total and that the list was truncated.

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success. |
| `2` | CLI usage error. |
| `3` | Pipe root or canonical schema unavailable. |
| `4` | Input file unavailable or unreadable. |
| `5` | Input or schema is not valid JSON. |
| `6` | ProductBaseline fails schema validation. |
| `7` | Canonical ProductBaseline schema is invalid. |

Scripts should use the exit code and `--json`, not parse human-readable messages.

Example success:

```json
{"command":"baseline.validate","message":"ProductBaseline is valid.","ok":true,"schemaVersion":"0.1.0"}
```

Example failure shape:

```json
{
  "code": "BASELINE_INVALID",
  "errors": [
    {
      "message": "Missing required property: product.",
      "path": "/",
      "rule": "required",
      "schemaPath": "/required"
    }
  ],
  "exitCode": 6,
  "message": "ProductBaseline validation failed with 1 error(s).",
  "ok": false
}
```

## Development Validation

From an activated Python 3.11+ environment with the package installed:

```bash
python -m unittest discover -v
python -m compileall -q src tests
python -m pip check
```

The acceptance run must additionally install the non-editable package in a fresh virtual environment and exercise `pipe --help`, `pipe version`, root discovery from a path containing spaces, and both valid and invalid ProductBaseline inputs.

## Boundaries

This CLI foundation does not:

- implement `/pipe:idea` or `/pipe:adopt`
- create or update Linear/GitHub records
- read credentials or secret stores
- persist runs or approvals
- install or configure Hermes or Atelier
- deploy anything

See [ADR-002](../../architecture/adr/adr-002-portable-cli-runtime.md), the [dual-entry workflow](../../execution/dual-entry-product-intake-workflow.md), and the canonical [ProductBaseline schema](../../schemas/ProductBaseline.schema.json).
