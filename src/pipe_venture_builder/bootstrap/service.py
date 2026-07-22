"""Plan-first and idempotent ProductManifest bootstrap."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import INPUT_UNAVAILABLE, MANIFEST_INVALID
from pipe_venture_builder.manifest.constants import (
    DEFAULT_CAPABILITIES,
    DEFAULT_FALLBACK_RUNTIMES,
    DEFAULT_RUNTIME,
    MANIFEST_RELATIVE_PATH,
    MANIFEST_SCHEMA_RELATIVE_PATH,
)
from pipe_venture_builder.manifest.loader import load_product_manifest
from pipe_venture_builder.manifest.model import build_product_manifest
from pipe_venture_builder.manifest.validation import (
    invalid_manifest_error,
    validate_product_manifest,
)
from pipe_venture_builder.validation import load_json_document


@dataclass(frozen=True, slots=True)
class BootstrapOptions:
    product_id: str | None = None
    entry_mode: str | None = None
    runtime: str | None = None
    fallback_runtimes: tuple[str, ...] | None = None
    capabilities: tuple[str, ...] | None = None
    linear_project_id: str | None = None
    github_repository: str | None = None


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    action: str
    operations: tuple[dict[str, str], ...]
    warnings: tuple[str, ...]
    manifest: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "operations": list(self.operations),
            "warnings": list(self.warnings),
        }


def plan_bootstrap(
    product_root: Path,
    toolkit_root: Path,
    *,
    pipe_version: str,
    options: BootstrapOptions,
) -> BootstrapResult:
    """Return a deterministic plan without changing the target repository."""

    pipe_directory = product_root / ".pipe"
    destination = product_root / MANIFEST_RELATIVE_PATH
    _guard_targets(pipe_directory, destination)

    existing: dict[str, Any] | None = None
    if destination.exists():
        existing = load_product_manifest(product_root, toolkit_root).data

    manifest = _resolve_manifest(existing, pipe_version=pipe_version, options=options)
    schema = load_json_document(
        toolkit_root / MANIFEST_SCHEMA_RELATIVE_PATH,
        kind="manifest_schema",
    )
    findings = validate_product_manifest(manifest, schema)
    if findings:
        raise invalid_manifest_error(findings)

    warnings = _warnings(product_root)
    if existing is not None:
        if manifest != existing:
            raise PipeError(
                code="BOOTSTRAP_CONFLICT",
                message=(
                    "A different ProductManifest already exists. Bootstrap never "
                    "overwrites repository configuration."
                ),
                exit_code=INPUT_UNAVAILABLE,
            )
        return BootstrapResult(
            action="unchanged",
            operations=(),
            warnings=warnings,
            manifest=manifest,
        )

    operations: list[dict[str, str]] = []
    if not pipe_directory.exists():
        operations.append({"operation": "create_directory", "target": ".pipe"})
    operations.append(
        {"operation": "create_file", "target": MANIFEST_RELATIVE_PATH.as_posix()}
    )
    return BootstrapResult(
        action="create",
        operations=tuple(operations),
        warnings=warnings,
        manifest=manifest,
    )


def apply_bootstrap(
    product_root: Path,
    toolkit_root: Path,
    *,
    pipe_version: str,
    options: BootstrapOptions,
) -> BootstrapResult:
    """Apply exactly the safe plan, never replacing an existing file."""

    planned = plan_bootstrap(
        product_root,
        toolkit_root,
        pipe_version=pipe_version,
        options=options,
    )
    if planned.action == "unchanged":
        return planned

    pipe_directory = product_root / ".pipe"
    destination = product_root / MANIFEST_RELATIVE_PATH
    created_directory = False
    created_file = False
    try:
        if not pipe_directory.exists():
            pipe_directory.mkdir(mode=0o755)
            created_directory = True
        if pipe_directory.is_symlink() or not pipe_directory.is_dir():
            raise PipeError(
                code="BOOTSTRAP_TARGET_BLOCKED",
                message="The .pipe target is not a safe repository-local directory.",
                exit_code=MANIFEST_INVALID,
            )
        with destination.open("x", encoding="utf-8", newline="\n") as handle:
            created_file = True
            json.dump(
                planned.manifest, handle, indent=2, sort_keys=True, ensure_ascii=False
            )
            handle.write("\n")
        loaded = load_product_manifest(product_root, toolkit_root)
        if loaded.data != planned.manifest:
            raise PipeError(
                code="BOOTSTRAP_POSTCONDITION_FAILED",
                message="The created ProductManifest did not match the validated plan.",
                exit_code=MANIFEST_INVALID,
            )
    except FileExistsError as exc:
        raise PipeError(
            code="BOOTSTRAP_CONFLICT",
            message="ProductManifest appeared during apply and was not overwritten.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc
    except PipeError:
        _remove_created_file(destination, created_file)
        _remove_empty_directory(pipe_directory, created_directory)
        raise
    except (OSError, PermissionError) as exc:
        _remove_created_file(destination, created_file)
        _remove_empty_directory(pipe_directory, created_directory)
        raise PipeError(
            code="BOOTSTRAP_APPLY_UNAVAILABLE",
            message="Bootstrap could not create the repository-local ProductManifest.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc

    return BootstrapResult(
        action="created",
        operations=planned.operations,
        warnings=planned.warnings,
        manifest=planned.manifest,
    )


def _resolve_manifest(
    existing: dict[str, Any] | None,
    *,
    pipe_version: str,
    options: BootstrapOptions,
) -> dict[str, Any]:
    if existing is None and (options.product_id is None or options.entry_mode is None):
        raise PipeError(
            code="BOOTSTRAP_CONFIGURATION_REQUIRED",
            message=(
                "Initial bootstrap requires --product-id and --entry-mode. "
                "No repository files were changed."
            ),
            exit_code=INPUT_UNAVAILABLE,
        )

    current = existing or {}
    current_runtime = current.get("runtime", {})
    current_capabilities = current.get("capabilities", {})
    current_linear = current.get("linear", {})
    current_github = current.get("github", {})
    try:
        return build_product_manifest(
            product_id=options.product_id or current.get("productId"),
            pipe_version=current.get("pipeVersion", pipe_version),
            entry_mode=options.entry_mode or current.get("entryMode"),
            runtime=options.runtime
            or current_runtime.get("preferred", DEFAULT_RUNTIME),
            fallback_runtimes=(
                options.fallback_runtimes
                if options.fallback_runtimes is not None
                else tuple(current_runtime.get("fallbacks", DEFAULT_FALLBACK_RUNTIMES))
            ),
            capabilities=(
                options.capabilities
                if options.capabilities is not None
                else tuple(current_capabilities.get("enabled", DEFAULT_CAPABILITIES))
            ),
            linear_project_id=(
                options.linear_project_id
                if options.linear_project_id is not None
                else current_linear.get("projectId")
            ),
            github_repository=(
                options.github_repository
                if options.github_repository is not None
                else current_github.get("repository")
            ),
        )
    except (TypeError, ValueError) as exc:
        raise PipeError(
            code="BOOTSTRAP_CONFIGURATION_INVALID",
            message="Bootstrap configuration is invalid and no files were changed.",
            exit_code=MANIFEST_INVALID,
        ) from exc


def _guard_targets(pipe_directory: Path, destination: Path) -> None:
    if pipe_directory.is_symlink() or (
        pipe_directory.exists() and not pipe_directory.is_dir()
    ):
        raise PipeError(
            code="BOOTSTRAP_TARGET_BLOCKED",
            message="The .pipe target is not a safe repository-local directory.",
            exit_code=MANIFEST_INVALID,
        )
    if destination.is_symlink():
        raise PipeError(
            code="BOOTSTRAP_TARGET_BLOCKED",
            message="ProductManifest cannot be created through a symlink.",
            exit_code=MANIFEST_INVALID,
        )


def _warnings(product_root: Path) -> tuple[str, ...]:
    mode_path = product_root / ".pipe/mode.json"
    if not mode_path.is_file() or mode_path.is_symlink():
        return (
            "Operating mode is not configured. A human must create a valid .pipe/mode.json before the repository can be ready.",
        )
    return ()


def _remove_empty_directory(path: Path, created: bool) -> None:
    if not created:
        return
    try:
        path.rmdir()
    except OSError:
        pass


def _remove_created_file(path: Path, created: bool) -> None:
    if not created:
        return
    try:
        path.unlink()
    except OSError:
        pass
