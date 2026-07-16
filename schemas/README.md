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
- [SyntheticPersona](SyntheticPersona.schema.json)

Schema outlines:

- [Planning schema outlines](planning-schema-outlines.md)

Do not add schemas without an approved Linear ticket.
