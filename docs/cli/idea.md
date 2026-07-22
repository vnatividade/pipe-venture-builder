# `pipe idea`

`pipe idea` converts one approved Markdown or JSON brainstorm into a schema-valid, review-required `ProductBaseline` with `entryMode: idea`. It is the greenfield entry point defined by PIP-708 and ADR-001.

The command normalizes founder-authored material; it does not research a market, validate demand, contact anyone, create implementation work, or mutate Linear, GitHub, documentation, or code.

## Generate A Baseline

Return the baseline in the stable JSON response envelope:

```bash
pipe idea /path/to/brainstorm.md \
  --root /path/to/pipe-toolkit \
  --json
```

Write the canonical baseline object to an explicit new file:

```bash
pipe idea /path/to/brainstorm.json \
  --root /path/to/pipe-toolkit \
  --output /path/to/product-baseline.json
```

`--root` resolves the Pipe toolkit that owns `schemas/ProductBaseline.schema.json`. Until the portable bootstrap contract is implemented, run from a Pipe clone or provide that root explicitly.

One of `--json` or `--output` is required. Output files use non-overwriting creation; an existing destination produces `IDEA_OUTPUT_EXISTS` and remains unchanged.

## Accepted Source Shape

The input must describe exactly one product. Supported suffixes are `.md`, `.markdown`, and `.json`.

Markdown uses level-one to level-three headings. A representative source is:

```markdown
# Working Product Name

## Idea
One focused product hypothesis.

## Target User
The narrow initial user.

## Problem
The important problem to validate.

## Promise
The proposed user outcome.

## Mechanism
The proposed way the product may deliver the outcome.

## Channel
The first channel hypothesis.

## Solution Path
Market-facing, own-pain, or specific-person.

## Assumptions
- An explicit founder assumption.

## Unknowns
- An unanswered question.
```

JSON accepts an object with the equivalent fields. English and Portuguese aliases are supported, including `name`/`nome`, `idea`/`ideia`, `target user`/`publico alvo`, `problem`/`problema`, `promise`/`promessa`, `mechanism`/`mecanismo`, `channel`/`canal`, and `solution path`/`caminho da solucao`.

Lists under `ideas`, `products`, `ideias`, or `produtos` are accepted only when they contain exactly one object. Multiple top-level Markdown products or multi-item JSON collections stop with `IDEA_MULTIPLE_PRODUCTS`; split the brainstorm into one source per product before rerunning the command.

Unknown fields are ignored. Missing product name, target user, problem, or promise produces a blocked P1 framing gap and keeps the lifecycle at `idea_intake`. A missing solution path is represented as an explicit P2 gap.

## Evidence Boundary

Every founder-provided product statement is classified as an assumption, not as a fact or customer evidence. Text placed under `Evidence`, `Evidencias`, or `Evidence Claims` is retained only as an unverified assumption and creates a blocked verification gap.

The baseline always reports:

- `customerEvidencePresent: false`
- `demandValidationStatus: hypothesis_only`
- `strongestEvidenceLane: internal_assumption`
- no evidence statement IDs

The source file remains separately traceable through its safe filename and content-derived source ID. Raw content is not copied into error messages.

## Safety And Bounds

The parser rejects unsupported files, symlinks, binary or invalid UTF-8 input, oversized content, recognized secret-shaped values, email addresses, phone-number-shaped values, and explicit customer identity fields. Rejected sensitive values are never included in the error response.

This is a defensive intake boundary, not a complete privacy, secret-scanning, or compliance certification. Do not provide secrets, credentials, personal data, customer data, or production data.

Fields are bounded to 2,000 normalized characters and list fields to 20 items. Code-fenced Markdown is ignored.

## Determinism And Handoff

For unchanged input, normalized content, IDs, ordering, and `generatedAt` are stable. The deterministic intake timestamp is `1970-01-01T00:00:00Z`; a later governed workflow can record an approved event time without changing the source-derived identity.

A sufficiently framed idea points to founder focus through `/pipe:discover`. An incomplete idea points back to `/pipe:idea`. The generated status is always `review_required`; generation alone does not authorize validation claims, a PRD, implementation, outreach, billing, deployment, or external mutation.

## Validation

From the repository's Python 3.11 environment:

```bash
python -m unittest discover -v
python -m compileall -q src tests
python -m pip check
```

The idea suite covers Markdown and JSON ingestion, Portuguese aliases, canonical schema validation, golden deterministic output, ambiguity, multi-product blocking, evidence classification, reference integrity, sensitive-value redaction, JSON CLI output, and non-overwriting file output.
