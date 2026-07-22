"""Conflict-safe, repository-local Pipe bootstrap."""

from .service import (
    BootstrapOptions,
    BootstrapResult,
    apply_bootstrap,
    plan_bootstrap,
)

__all__ = [
    "BootstrapOptions",
    "BootstrapResult",
    "apply_bootstrap",
    "plan_bootstrap",
]
