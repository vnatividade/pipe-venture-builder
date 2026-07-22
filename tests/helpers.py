"""Test helpers for creating isolated Pipe roots and baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SCHEMA = REPOSITORY_ROOT / "schemas/ProductBaseline.schema.json"


def load_schema() -> dict[str, Any]:
    return json.loads(CANONICAL_SCHEMA.read_text(encoding="utf-8"))


def valid_baseline() -> dict[str, Any]:
    schema = load_schema()
    return schema["examples"][0]


def make_pipe_root(path: Path) -> Path:
    (path / ".pipe").mkdir(parents=True)
    schema_directory = path / "schemas"
    schema_directory.mkdir()
    (schema_directory / "ProductBaseline.schema.json").write_text(
        CANONICAL_SCHEMA.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return path


def write_json(path: Path, value: Any) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path
