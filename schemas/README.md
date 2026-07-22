# Schemas

Canonical machine-readable schemas live here.

Use `architecture/canonical-schema-policy.md` before adding or changing schema files.

This directory is intentionally minimal for now. It does not provide runtime validation, CI enforcement, code generation, migrations, or a complete registry.

Initial schema convention:

```txt
schemas/<SchemaName>.schema.json
```

Current schemas:

- [DeliveryEvidence](DeliveryEvidence.schema.json)
- [LearningRecord](LearningRecord.schema.json)
- [OperatingMode](OperatingMode.schema.json) — contract for `.pipe/mode.json` (PIP-659; see `execution/operating-modes.md`)
- [ProductManifest](ProductManifest.schema.json) — portable, non-sensitive repository binding at `.pipe/project.json` (PIP-709)
- [ProductBaseline](ProductBaseline.schema.json) — common current-state contract for `idea` and `adopt` intake (PIP-700)
- [SyntheticPersona](SyntheticPersona.schema.json)

Schema outlines:

- [Planning schema outlines](planning-schema-outlines.md)

Do not add schemas without an approved Linear ticket.
