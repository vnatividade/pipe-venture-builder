# ProductManifest Compatibility And Migration

The initial ProductManifest schema and runtime compatibility version are `0.1.0`.

PIP-709 deliberately uses exact version compatibility: `.pipe/project.json` `pipeVersion` must match the installed Pipe package version, and `schemaVersion` must satisfy the canonical schema constant. A mismatch is `incompatible` in `pipe doctor`.

Bootstrap never upgrades or overwrites an existing manifest. This prevents an installation on one computer from silently changing the repository contract for every other operator.

## Reviewed Migration Procedure

1. Run `pipe doctor --json` with the current toolkit/package.
2. Record the incompatible fields and affected runtimes/capabilities without copying credentials or local paths.
3. Read the target release's schema and migration notes.
4. Create or use the scoped Linear migration ticket when repository files must change.
5. Prepare a branch and edit only `.pipe/project.json` plus explicitly owned dependent artifacts.
6. Validate the proposed manifest against `schemas/ProductManifest.schema.json`.
7. Run `pipe doctor --json` with the target package and toolkit.
8. Review and merge through the repository's declared operating mode.
9. Keep rollback as a normal revert of the reviewed migration commit.

Do not delete the existing manifest to make bootstrap recreate it. Do not store an installation directory in the manifest. Do not migrate `.pipe/mode.json` automatically; operating-mode changes remain human-only.

Breaking schema changes require a future dedicated compatibility ticket, migration notes, affected-consumer inventory, and review under the canonical schema policy.
