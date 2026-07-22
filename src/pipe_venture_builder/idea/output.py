"""Explicit, non-overwriting idea-baseline output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import INPUT_UNAVAILABLE


def write_idea_baseline(path: str | Path, baseline: dict[str, Any]) -> None:
    destination = Path(path)
    try:
        with destination.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(baseline, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
    except FileExistsError as exc:
        raise PipeError(
            code="IDEA_OUTPUT_EXISTS",
            message="The idea output already exists; choose a new path.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc
    except (OSError, PermissionError) as exc:
        raise PipeError(
            code="IDEA_OUTPUT_UNAVAILABLE",
            message="The idea output could not be written.",
            exit_code=INPUT_UNAVAILABLE,
        ) from exc
