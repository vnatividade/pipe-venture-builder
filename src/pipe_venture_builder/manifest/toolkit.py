"""Product and toolkit root resolution without founder-specific fallbacks."""

from __future__ import annotations

import os
from pathlib import Path

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import PROJECT_ROOT_NOT_FOUND

from .constants import MANIFEST_SCHEMA_RELATIVE_PATH

TOOLKIT_ROOT_ENV = "PIPE_TOOLKIT_ROOT"


def resolve_toolkit_root(
    explicit: str | Path | None = None,
    *,
    start: str | Path | None = None,
) -> Path:
    """Resolve a versioned toolkit from explicit, local, or machine-local hints."""

    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit).expanduser())
    else:
        environment_root = os.environ.get(TOOLKIT_ROOT_ENV)
        if environment_root:
            candidates.append(Path(environment_root).expanduser())
        candidates.append(Path(__file__).resolve().parents[3])
        origin = Path.cwd() if start is None else Path(start).expanduser()
        candidates.extend((origin, *origin.parents))

    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
        except (FileNotFoundError, OSError):
            continue
        if resolved.is_file():
            resolved = resolved.parent
        for possible in (resolved, *resolved.parents):
            if _is_toolkit_root(possible):
                return possible
        if explicit is not None:
            break

    raise PipeError(
        code="TOOLKIT_ROOT_NOT_FOUND",
        message=(
            "No compatible Pipe toolkit found. Run from a Pipe clone, pass "
            "--toolkit-root, or configure PIPE_TOOLKIT_ROOT."
        ),
        exit_code=PROJECT_ROOT_NOT_FOUND,
    )


def resolve_product_root(target: str | Path = ".") -> Path:
    candidate = Path(target).expanduser()
    if candidate.is_symlink():
        raise PipeError(
            code="PRODUCT_ROOT_BLOCKED",
            message="The product root cannot be a symlink.",
            exit_code=PROJECT_ROOT_NOT_FOUND,
        )
    try:
        resolved = candidate.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise PipeError(
            code="PRODUCT_ROOT_NOT_FOUND",
            message="The requested product root is unavailable.",
            exit_code=PROJECT_ROOT_NOT_FOUND,
        ) from exc
    if not resolved.is_dir():
        raise PipeError(
            code="PRODUCT_ROOT_NOT_FOUND",
            message="The requested product root must be a directory.",
            exit_code=PROJECT_ROOT_NOT_FOUND,
        )
    return resolved


def _is_toolkit_root(candidate: Path) -> bool:
    return (
        candidate.is_dir()
        and (candidate / MANIFEST_SCHEMA_RELATIVE_PATH).is_file()
        and (candidate / "pyproject.toml").is_file()
    )
