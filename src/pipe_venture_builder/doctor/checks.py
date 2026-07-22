"""Redacted local checks for ProductManifest and Pipe runtime readiness."""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, Callable

from jsonschema.exceptions import SchemaError

from pipe_venture_builder import __version__
from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.manifest.constants import (
    MANIFEST_RELATIVE_PATH,
    MANIFEST_SCHEMA_RELATIVE_PATH,
)
from pipe_venture_builder.manifest.loader import load_product_manifest
from pipe_venture_builder.manifest.validation import validate_document
from pipe_venture_builder.validation import load_json_document

CHECK_STATES = {
    "configured",
    "unavailable",
    "unauthorized",
    "incompatible",
    "blocked",
    "not_applicable",
}
SUPPORTED_PLATFORMS = {
    "darwin": {"arm64", "x86_64"},
    "linux": {"aarch64", "arm64", "x86_64"},
    "win32": {"amd64", "arm64", "x86_64"},
}
RUNTIME_BINARIES = {
    "hermes": "hermes",
    "codex": "codex",
    "claude-code": "claude",
}
RUNTIME_CAPABILITIES = {
    "hermes": "capability.external.hermes",
    "codex": "capability.external.codex",
    "claude-code": "capability.external.claude-code",
}
CAPABILITY_ID = re.compile(r"^capability\.[a-z0-9][a-z0-9-]*(?:\.[a-z0-9][a-z0-9-]*)*$")


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    check_id: str
    category: str
    status: str
    required: bool
    summary: str
    remediation: str | None = None

    def __post_init__(self) -> None:
        if self.status not in CHECK_STATES:
            raise ValueError("unsupported doctor check state")

    def as_dict(self) -> dict[str, Any]:
        return {
            "checkId": self.check_id,
            "category": self.category,
            "status": self.status,
            "required": self.required,
            "summary": self.summary,
            "remediation": self.remediation,
        }


@dataclass(frozen=True, slots=True)
class DoctorReport:
    status: str
    checks: tuple[DoctorCheck, ...]

    @property
    def is_ready(self) -> bool:
        return self.status in {"ready", "ready_with_warnings"}

    def as_dict(self) -> dict[str, Any]:
        counts = {state: 0 for state in sorted(CHECK_STATES)}
        for check in self.checks:
            counts[check.status] += 1
        return {
            "status": self.status,
            "counts": counts,
            "checks": [check.as_dict() for check in self.checks],
        }

    def human_summary(self) -> str:
        lines = [f"Pipe doctor: {self.status}."]
        lines.extend(
            f"- [{check.status}] {check.check_id}: {check.summary}"
            for check in self.checks
        )
        return "\n".join(lines)


Which = Callable[[str], str | None]
Access = Callable[[Path, int], bool]
GitInspector = Callable[[Path], str]


def run_doctor(
    product_root: Path,
    toolkit_root: Path,
    *,
    which: Which = shutil.which,
    access: Access = os.access,
    git_inspector: GitInspector | None = None,
    platform_name: str | None = None,
    machine_name: str | None = None,
    python_version: tuple[int, int, int] | None = None,
) -> DoctorReport:
    """Inspect local readiness without writing files or reading credential values."""

    product_root = product_root.resolve()
    toolkit_root = toolkit_root.resolve()
    checks: list[DoctorCheck] = []
    current_platform = (platform_name or sys.platform).lower()
    current_machine = (machine_name or platform.machine()).lower()
    current_python = python_version or (
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    checks.append(_platform_check(current_platform, current_machine))
    checks.append(_python_check(current_python))
    checks.append(_toolkit_check(toolkit_root))

    schema_states = _schema_checks(toolkit_root)
    checks.extend(schema_states)
    manifest = None
    manifest_state = _manifest_check(product_root, toolkit_root)
    checks.append(manifest_state[0])
    manifest = manifest_state[1]

    if manifest is not None:
        checks.append(_manifest_version_check(manifest.data))
        checks.append(_path_portability_check(manifest.data))
    checks.append(_mode_check(product_root, toolkit_root))

    git_binary = which("git")
    checks.append(
        DoctorCheck(
            "git_binary",
            "repository",
            "configured" if git_binary else "unavailable",
            True,
            "Git executable is available."
            if git_binary
            else "Git executable is unavailable.",
            None if git_binary else "Install Git and rerun pipe doctor.",
        )
    )
    if git_binary:
        checks.append(
            _git_repository_check(
                product_root,
                git_inspector or _inspect_git_root,
            )
        )
    else:
        checks.append(
            DoctorCheck(
                "git_repository",
                "repository",
                "unavailable",
                True,
                "Repository identity cannot be checked without Git.",
                "Install Git and rerun pipe doctor.",
            )
        )
    write_target = (
        product_root / ".pipe" if (product_root / ".pipe").is_dir() else product_root
    )
    writable = access(write_target, os.W_OK)
    checks.append(
        DoctorCheck(
            "repository_write_access",
            "repository",
            "configured" if writable else "unauthorized",
            True,
            (
                "Repository permits intended local output writes."
                if writable
                else "Repository does not permit intended local output writes."
            ),
            None
            if writable
            else "Grant repository-local write access to the operator.",
        )
    )

    if manifest is not None:
        capability_checks = _capability_checks(manifest.data, toolkit_root)
        checks.extend(capability_checks)
        runtime_checks = _runtime_checks(manifest.data, toolkit_root, which)
        checks.extend(runtime_checks)
        checks.extend(_connector_checks(manifest.data))
    else:
        checks.extend(
            (
                DoctorCheck(
                    "runtime_selection",
                    "runtime",
                    "unavailable",
                    True,
                    "Runtime selection is unavailable until ProductManifest is configured.",
                    "Run pipe bootstrap --plan, then apply the reviewed plan.",
                ),
                DoctorCheck(
                    "capability_selection",
                    "capability",
                    "unavailable",
                    True,
                    "Capability selection is unavailable until ProductManifest is configured.",
                    "Run pipe bootstrap --plan, then apply the reviewed plan.",
                ),
            )
        )

    connector_bound = bool(
        manifest
        and (
            manifest.data["linear"]["projectId"]
            or manifest.data["github"]["repository"]
        )
    )
    checks.append(
        DoctorCheck(
            "connector_authentication",
            "connector",
            "unauthorized" if connector_bound else "not_applicable",
            False,
            (
                "External binding exists; credential state was intentionally not inspected."
                if connector_bound
                else "Connector authentication is not applicable without an external binding."
            ),
            (
                "Use the connector's interactive authentication and its future adapter doctor."
                if connector_bound
                else None
            ),
        )
    )
    checks.append(
        DoctorCheck(
            "baseline_freshness",
            "governance",
            "not_applicable",
            False,
            "Persistent baseline freshness is deferred to the reconciliation workflow.",
        )
    )

    ordered = tuple(sorted(checks, key=lambda check: check.check_id))
    return DoctorReport(status=_overall_status(ordered), checks=ordered)


def _platform_check(platform_name: str, machine_name: str) -> DoctorCheck:
    supported = machine_name in SUPPORTED_PLATFORMS.get(platform_name, set())
    return DoctorCheck(
        "platform",
        "runtime",
        "configured" if supported else "incompatible",
        True,
        (
            "Operating system and architecture are in the supported portability matrix."
            if supported
            else "Operating system or architecture is outside the supported portability matrix."
        ),
        None
        if supported
        else "Use a supported platform or open a scoped compatibility ticket.",
    )


def _python_check(version: tuple[int, int, int]) -> DoctorCheck:
    supported = version >= (3, 11, 0)
    return DoctorCheck(
        "python_runtime",
        "runtime",
        "configured" if supported else "incompatible",
        True,
        (
            "Python runtime satisfies the 3.11+ requirement."
            if supported
            else "Python runtime is older than the required 3.11 release."
        ),
        None
        if supported
        else "Install Python 3.11 or newer in an isolated environment.",
    )


def _toolkit_check(toolkit_root: Path) -> DoctorCheck:
    metadata_path = toolkit_root / "pyproject.toml"
    if metadata_path.is_symlink():
        return DoctorCheck(
            "toolkit",
            "runtime",
            "blocked",
            True,
            "Toolkit package metadata cannot be loaded through a symlink.",
            "Restore tracked package metadata from the versioned toolkit.",
        )
    try:
        if metadata_path.stat().st_size > 128 * 1024:
            raise ValueError("metadata is unexpectedly large")
        with metadata_path.open("rb") as handle:
            metadata = tomllib.load(handle)
        declared = metadata["project"]["version"]
    except (KeyError, OSError, PermissionError, tomllib.TOMLDecodeError, ValueError):
        return DoctorCheck(
            "toolkit",
            "runtime",
            "incompatible",
            True,
            "Toolkit package metadata is unavailable or invalid.",
            "Restore a compatible versioned toolkit clone.",
        )
    compatible = declared == __version__
    return DoctorCheck(
        "toolkit",
        "runtime",
        "configured" if compatible else "incompatible",
        True,
        (
            "Toolkit metadata version matches the installed Pipe runtime."
            if compatible
            else "Toolkit metadata version does not match the installed Pipe runtime."
        ),
        None
        if compatible
        else "Install the matching Pipe package or migrate the toolkit.",
    )


def _schema_checks(toolkit_root: Path) -> list[DoctorCheck]:
    schemas = {
        "manifest_schema": MANIFEST_SCHEMA_RELATIVE_PATH,
        "baseline_schema": Path("schemas/ProductBaseline.schema.json"),
        "operating_mode_schema": Path("schemas/OperatingMode.schema.json"),
        "capability_registry_schema": Path("capabilities/capability.schema.json"),
    }
    checks: list[DoctorCheck] = []
    for check_id, relative in schemas.items():
        path = toolkit_root / relative
        if path.is_symlink():
            checks.append(
                DoctorCheck(
                    check_id,
                    "schema",
                    "blocked",
                    True,
                    "Canonical schema cannot be loaded through a symlink.",
                    "Restore the tracked canonical schema file.",
                )
            )
            continue
        try:
            schema = load_json_document(path, kind="schema")
            validate_document({}, schema)
        except PipeError as exc:
            state = (
                "incompatible" if exc.code.endswith("INVALID_JSON") else "unavailable"
            )
        except SchemaError:
            state = "incompatible"
        else:
            state = "configured"
        checks.append(
            DoctorCheck(
                check_id,
                "schema",
                state,
                True,
                (
                    "Canonical schema is available and valid."
                    if state == "configured"
                    else "Canonical schema is unavailable or invalid."
                ),
                None
                if state == "configured"
                else "Restore a compatible versioned toolkit.",
            )
        )
    return checks


def _manifest_check(
    product_root: Path,
    toolkit_root: Path,
) -> tuple[DoctorCheck, Any | None]:
    path = product_root / MANIFEST_RELATIVE_PATH
    if not path.exists() and not path.is_symlink():
        return (
            DoctorCheck(
                "product_manifest",
                "manifest",
                "unavailable",
                True,
                "ProductManifest is not configured.",
                "Run pipe bootstrap --plan, review it, then use --apply.",
            ),
            None,
        )
    try:
        manifest = load_product_manifest(product_root, toolkit_root)
    except PipeError as exc:
        state = "blocked" if exc.code in {"MANIFEST_BLOCKED"} else "incompatible"
        return (
            DoctorCheck(
                "product_manifest",
                "manifest",
                state,
                True,
                "ProductManifest is unsafe or incompatible.",
                "Repair the manifest through a reviewed migration; bootstrap will not overwrite it.",
            ),
            None,
        )
    return (
        DoctorCheck(
            "product_manifest",
            "manifest",
            "configured",
            True,
            "ProductManifest is schema-valid and repository-local.",
        ),
        manifest,
    )


def _manifest_version_check(manifest: dict[str, Any]) -> DoctorCheck:
    compatible = manifest.get("pipeVersion") == __version__
    return DoctorCheck(
        "manifest_pipe_version",
        "manifest",
        "configured" if compatible else "incompatible",
        True,
        (
            "Manifest Pipe version matches the installed runtime."
            if compatible
            else "Manifest Pipe version does not match the installed runtime."
        ),
        None
        if compatible
        else "Follow the documented version migration before continuing.",
    )


def _path_portability_check(manifest: dict[str, Any]) -> DoctorCheck:
    portable = not any(_machine_specific(value) for value in _strings(manifest))
    return DoctorCheck(
        "manifest_path_portability",
        "manifest",
        "configured" if portable else "blocked",
        True,
        (
            "Manifest contains no machine-specific absolute path."
            if portable
            else "Manifest contains a machine-specific absolute path."
        ),
        None
        if portable
        else "Replace machine-specific values with repository-relative identifiers.",
    )


def _mode_check(product_root: Path, toolkit_root: Path) -> DoctorCheck:
    mode_path = product_root / ".pipe/mode.json"
    if mode_path.is_symlink():
        return DoctorCheck(
            "operating_mode",
            "governance",
            "blocked",
            True,
            "Operating mode cannot be loaded through a symlink.",
            "A human must restore a tracked, repository-local mode declaration.",
        )
    if not mode_path.is_file():
        return DoctorCheck(
            "operating_mode",
            "governance",
            "unavailable",
            True,
            "Operating mode is not configured; restricted remains the fail-safe default.",
            "A human must create a valid .pipe/mode.json declaration.",
        )
    try:
        mode = load_json_document(mode_path, kind="operating_mode")
        schema = load_json_document(
            toolkit_root / "schemas/OperatingMode.schema.json",
            kind="operating_mode_schema",
        )
        findings = validate_document(mode, schema)
    except (PipeError, SchemaError):
        findings = [object()]
    return DoctorCheck(
        "operating_mode",
        "governance",
        "configured" if not findings else "incompatible",
        True,
        (
            "Operating mode declaration is valid."
            if not findings
            else "Operating mode declaration is invalid; restricted is the fail-safe default."
        ),
        None if not findings else "A human must repair the mode declaration.",
    )


def _git_repository_check(root: Path, inspector: GitInspector) -> DoctorCheck:
    try:
        top_level = Path(inspector(root)).resolve(strict=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        top_level = None
    exact = top_level == root
    return DoctorCheck(
        "git_repository",
        "repository",
        "configured" if exact else "unavailable",
        True,
        (
            "Target is the exact root of a local Git repository."
            if exact
            else "Target is not the exact root of a local Git repository."
        ),
        None if exact else "Run doctor against the product repository root.",
    )


def _inspect_git_root(root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    return completed.stdout.strip()


def _capability_checks(
    manifest: dict[str, Any],
    toolkit_root: Path,
) -> list[DoctorCheck]:
    enabled = manifest["capabilities"]["enabled"]
    if not enabled:
        return [
            DoctorCheck(
                "capability_selection",
                "capability",
                "configured",
                True,
                "No optional capabilities are selected.",
            )
        ]
    return [
        _capability_entry_check(capability_id, toolkit_root, required=True)
        for capability_id in enabled
    ]


def _runtime_checks(
    manifest: dict[str, Any],
    toolkit_root: Path,
    which: Which,
) -> list[DoctorCheck]:
    preferred = manifest["runtime"]["preferred"]
    candidates = [preferred, *manifest["runtime"]["fallbacks"]]
    available: list[str] = []
    adapter_usable: list[str] = []
    checks: list[DoctorCheck] = []
    for runtime in candidates:
        present = which(RUNTIME_BINARIES[runtime]) is not None
        if present:
            available.append(runtime)
        checks.append(
            DoctorCheck(
                f"runtime_binary_{runtime}",
                "runtime",
                "configured" if present else "unavailable",
                False,
                (
                    f"{runtime} executable is available."
                    if present
                    else f"{runtime} executable is unavailable."
                ),
                None if present else f"Install {runtime} or use a configured fallback.",
            )
        )
        adapter = _capability_entry_check(
            RUNTIME_CAPABILITIES[runtime],
            toolkit_root,
            required=False,
            check_prefix="runtime_adapter",
        )
        if adapter.status in {"configured", "unauthorized"}:
            adapter_usable.append(runtime)
        checks.append(adapter)
    usable = [
        runtime
        for runtime in candidates
        if runtime in available and runtime in adapter_usable
    ]
    checks.append(
        DoctorCheck(
            "runtime_selection",
            "runtime",
            "configured" if usable else "blocked",
            True,
            (
                "At least one selected executor is installed and registered; action-specific authorization may still be required."
                if usable
                else "No selected executor has both a local binary and usable registry entry."
            ),
            None
            if usable
            else "Install or select a compatible executor with a registered adapter.",
        )
    )
    return checks


def _capability_entry_check(
    capability_id: str,
    toolkit_root: Path,
    *,
    required: bool,
    check_prefix: str = "capability",
) -> DoctorCheck:
    check_id = f"{check_prefix}_{capability_id.replace('.', '_')}"
    if not CAPABILITY_ID.fullmatch(capability_id):
        return DoctorCheck(
            check_id,
            "capability",
            "blocked",
            required,
            "Capability identifier is unsafe.",
            "Use a schema-valid capability identifier.",
        )
    entry_path = toolkit_root / "capabilities/entries" / f"{capability_id}.json"
    if entry_path.is_symlink():
        return DoctorCheck(
            check_id,
            "capability",
            "blocked",
            required,
            "Capability entry cannot be loaded through a symlink.",
            "Restore the tracked capability entry.",
        )
    if not entry_path.is_file():
        return DoctorCheck(
            check_id,
            "capability",
            "unavailable",
            required,
            "Capability entry is unavailable.",
            "Install a toolkit version that includes the selected capability entry.",
        )
    try:
        entry = load_json_document(entry_path, kind="capability")
        schema = load_json_document(
            toolkit_root / "capabilities/capability.schema.json",
            kind="capability_schema",
        )
        findings = validate_document(entry, schema)
    except (PipeError, SchemaError):
        findings = [object()]
        entry = {}
    if findings or entry.get("capabilityId") != capability_id:
        return DoctorCheck(
            check_id,
            "capability",
            "incompatible",
            required,
            "Capability entry is invalid or has mismatched identity.",
            "Restore a schema-valid capability entry with matching identity.",
        )
    lifecycle = entry.get("lifecycle")
    review_status = entry.get("review", {}).get("reviewStatus")
    status = _capability_governance_status(lifecycle, review_status)
    repository_path = entry.get("source", {}).get("repositoryPath")
    if repository_path:
        if _machine_specific(repository_path) or ".." in Path(repository_path).parts:
            status = "blocked"
        else:
            referenced = (toolkit_root / repository_path).resolve()
            try:
                referenced.relative_to(toolkit_root.resolve())
            except ValueError:
                status = "blocked"
            else:
                if not referenced.exists():
                    status = "unavailable"
    return DoctorCheck(
        check_id,
        "capability",
        status,
        required,
        (
            "Capability entry and repository-relative references are usable."
            if status == "configured"
            else "Capability entry is unavailable, unauthorized, incompatible, or blocked."
        ),
        None
        if status == "configured"
        else "Review capability lifecycle, version, and referenced paths.",
    )


def _connector_checks(manifest: dict[str, Any]) -> list[DoctorCheck]:
    bindings = {
        "linear": manifest["linear"]["projectId"],
        "github": manifest["github"]["repository"],
    }
    checks: list[DoctorCheck] = []
    for name, binding in bindings.items():
        if binding is None:
            checks.append(
                DoctorCheck(
                    f"connector_{name}",
                    "connector",
                    "not_applicable",
                    False,
                    f"{name.title()} binding is not configured.",
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    f"connector_{name}",
                    "connector",
                    "unauthorized",
                    False,
                    f"{name.title()} binding is declared; authentication was not inspected.",
                    "Use the connector's own interactive authentication and rerun its adapter doctor after PIP-710.",
                )
            )
    return checks


def _capability_governance_status(lifecycle: Any, review_status: Any) -> str:
    if lifecycle == "blocked" or review_status == "blocked":
        return "blocked"
    if lifecycle == "proposed":
        return "unavailable"
    if lifecycle == "deprecated" or review_status == "needs-update":
        return "incompatible"
    if lifecycle == "restricted" or review_status in {"restricted", "not-reviewed"}:
        return "unauthorized"
    return "configured"


def _overall_status(checks: tuple[DoctorCheck, ...]) -> str:
    manifest = next(check for check in checks if check.check_id == "product_manifest")
    mode = next(check for check in checks if check.check_id == "operating_mode")
    severe = {"unauthorized", "incompatible", "blocked"}
    if any(check.required and check.status in severe for check in checks):
        return "blocked"
    if manifest.status == "unavailable" or mode.status == "unavailable":
        return "not_configured"
    if any(check.required and check.status == "unavailable" for check in checks):
        return "blocked"
    failing = {"unavailable", *severe}
    if any(not check.required and check.status in failing for check in checks):
        return "ready_with_warnings"
    return "ready"


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(_strings(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_strings(item))
        return result
    return []


def _machine_specific(value: str) -> bool:
    if value.startswith(("~/", "~\\")):
        return True
    return Path(value).is_absolute() or PureWindowsPath(value).is_absolute()
