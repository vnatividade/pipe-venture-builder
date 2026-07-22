"""Construct minimal portable ProductManifest documents."""

from __future__ import annotations

from typing import Any, Iterable

from .constants import MANIFEST_SCHEMA_VERSION, SUPPORTED_RUNTIMES


def build_product_manifest(
    *,
    product_id: str,
    pipe_version: str,
    entry_mode: str,
    runtime: str,
    fallback_runtimes: Iterable[str],
    capabilities: Iterable[str],
    linear_project_id: str | None = None,
    github_repository: str | None = None,
) -> dict[str, Any]:
    """Return the canonical manifest shape without machine-specific state."""

    fallbacks = list(dict.fromkeys(fallback_runtimes))
    enabled = sorted(set(capabilities))
    if runtime not in SUPPORTED_RUNTIMES:
        raise ValueError("unsupported runtime")
    if runtime in fallbacks:
        raise ValueError("preferred runtime cannot also be a fallback")
    return {
        "schemaVersion": MANIFEST_SCHEMA_VERSION,
        "productId": product_id,
        "pipeVersion": pipe_version,
        "entryMode": entry_mode,
        "repository": {"root": "."},
        "linear": {"projectId": linear_project_id},
        "github": {"repository": github_repository},
        "capabilities": {"enabled": enabled},
        "runtime": {
            "preferred": runtime,
            "fallbacks": fallbacks,
        },
    }
