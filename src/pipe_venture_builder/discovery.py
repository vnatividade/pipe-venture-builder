"""Pipe project-root discovery without machine-specific paths."""

from pathlib import Path

from .errors import PipeError
from .exit_codes import PROJECT_ROOT_NOT_FOUND

SCHEMA_RELATIVE_PATH = Path("schemas/ProductBaseline.schema.json")


def is_pipe_root(candidate: Path) -> bool:
    """Return whether *candidate* has the minimum current Pipe markers."""

    return (
        candidate.is_dir()
        and (candidate / SCHEMA_RELATIVE_PATH).is_file()
        and ((candidate / ".pipe").is_dir() or (candidate / "AGENTS.md").is_file())
    )


def discover_project_root(start: str | Path | None = None) -> Path:
    """Find the nearest Pipe root from *start* or the current directory."""

    candidate = Path.cwd() if start is None else Path(start).expanduser()
    try:
        candidate = candidate.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise PipeError(
            code="PROJECT_ROOT_NOT_FOUND",
            message="The requested start location is unavailable.",
            exit_code=PROJECT_ROOT_NOT_FOUND,
        ) from exc

    if candidate.is_file():
        candidate = candidate.parent

    for directory in (candidate, *candidate.parents):
        if is_pipe_root(directory):
            return directory

    raise PipeError(
        code="PROJECT_ROOT_NOT_FOUND",
        message="No Pipe project root found. Run inside a Pipe repository or pass --root.",
        exit_code=PROJECT_ROOT_NOT_FOUND,
    )


def resolve_baseline_schema(root: Path, explicit_schema: str | Path | None = None) -> Path:
    """Resolve the canonical ProductBaseline schema for validation."""

    if explicit_schema is not None:
        schema_path = Path(explicit_schema).expanduser()
        if not schema_path.is_absolute():
            schema_path = root / schema_path
    else:
        schema_path = root / SCHEMA_RELATIVE_PATH

    try:
        schema_path = schema_path.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise PipeError(
            code="BASELINE_SCHEMA_UNAVAILABLE",
            message="The ProductBaseline schema is unavailable.",
            exit_code=PROJECT_ROOT_NOT_FOUND,
        ) from exc

    if not schema_path.is_file():
        raise PipeError(
            code="BASELINE_SCHEMA_UNAVAILABLE",
            message="The ProductBaseline schema is unavailable.",
            exit_code=PROJECT_ROOT_NOT_FOUND,
        )
    return schema_path
