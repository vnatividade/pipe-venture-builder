"""Narrow apply adapter protocol; no live implementation is provided."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class ApplyAdapterFailure(RuntimeError):
    """The fixture adapter failed without a verified result."""


class ApplyAdapterConflict(ApplyAdapterFailure):
    """The fixture target rejected the intended state transition."""


class ApplyInterrupted(ApplyAdapterFailure):
    """Execution stopped after the idempotent apply call may have started."""


@dataclass(frozen=True, slots=True)
class TargetObservation:
    exists: bool
    fingerprint: str | None


@dataclass(frozen=True, slots=True)
class ApplyResult:
    result_ref: str
    result_fingerprint: str
    already_applied: bool = False


@dataclass(frozen=True, slots=True)
class VerificationResult:
    verified: bool
    target_fingerprint: str | None


class ApplyAdapter(Protocol):
    """The complete apply boundary consumed by the supervised service."""

    adapter_name: str

    def inspect(self, action: Mapping[str, Any]) -> TargetObservation:
        """Return normalized current target identity before mutation."""

    def apply(
        self, action: Mapping[str, Any], *, idempotency_key: str
    ) -> ApplyResult:
        """Apply one named action idempotently or raise a classified failure."""

    def verify(
        self, action: Mapping[str, Any], result: ApplyResult
    ) -> VerificationResult:
        """Re-read normalized state and verify the expected result."""
