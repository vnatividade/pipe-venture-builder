"""Explicit, non-overwriting ProductBaseline output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import INPUT_UNAVAILABLE


def serialize_product_baseline(baseline: dict[str, Any]) -> str:
    return json.dumps(baseline, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_product_baseline(path: str | Path, baseline: dict[str, Any]) -> None:
    """Write to an explicit new file; never replace an existing artifact."""

    destination = Path(path)
    try:
        with destination.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(serialize_product_baseline(baseline))
    except FileExistsError as exc:
        raise PipeError(
            code="ADOPT_OUTPUT_EXISTS",
            message="The adoption output already exists; choose a new path.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc
    except (OSError, PermissionError) as exc:
        raise PipeError(
            code="ADOPT_OUTPUT_UNAVAILABLE",
            message="The adoption output could not be written.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc
