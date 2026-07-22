"""Safe loading of repository-local ProductManifest documents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import MANIFEST_INVALID
from pipe_venture_builder.validation import load_json_document

from .constants import MANIFEST_RELATIVE_PATH, MANIFEST_SCHEMA_RELATIVE_PATH
from .validation import invalid_manifest_error, validate_product_manifest


@dataclass(frozen=True, slots=True)
class ProductManifest:
    root: Path
    path: Path
    data: dict[str, Any]


def load_product_manifest(product_root: Path, toolkit_root: Path) -> ProductManifest:
    path = product_root / MANIFEST_RELATIVE_PATH
    if path.is_symlink():
        raise PipeError(
            code="MANIFEST_BLOCKED",
            message="The ProductManifest cannot be loaded through a symlink.",
            exit_code=MANIFEST_INVALID,
        )
    instance = load_json_document(path, kind="manifest")
    schema = load_json_document(
        toolkit_root / MANIFEST_SCHEMA_RELATIVE_PATH,
        kind="manifest_schema",
    )
    findings = validate_product_manifest(instance, schema)
    if findings:
        raise invalid_manifest_error(findings)
    if not isinstance(instance, dict):  # schema validation already reports this
        raise PipeError(
            code="MANIFEST_INVALID",
            message="ProductManifest must be a JSON object.",
            exit_code=MANIFEST_INVALID,
        )
    return ProductManifest(root=product_root, path=path, data=instance)
