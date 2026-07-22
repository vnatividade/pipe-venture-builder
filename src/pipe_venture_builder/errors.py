"""Domain errors that are safe to render without source payloads."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PipeError(Exception):
    """A user-actionable CLI failure with a stable machine code."""

    code: str
    message: str
    exit_code: int
    details: list[dict[str, Any]] = field(default_factory=list)

    def __str__(self) -> str:
        return self.message
