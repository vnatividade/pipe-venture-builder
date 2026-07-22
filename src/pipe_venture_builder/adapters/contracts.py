"""Read-only contracts shared by external inventory adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


SNAPSHOT_SCHEMA_VERSION = "0.1.0"
DEFAULT_RECORD_LIMIT = 200
MAX_RECORD_LIMIT = 1000
DEFAULT_MAX_PAGES = 10
MAX_PAGES = 100


@dataclass(frozen=True, slots=True)
class SourcePayload:
    """Bounded source response before normalization.

    The payload deliberately excludes response headers, credentials, request
    metadata, issue bodies, comments, and raw connector envelopes.
    """

    container: Mapping[str, Any]
    items: tuple[Mapping[str, Any], ...]
    pages_read: int = 1
    truncated: bool = False


class ReadOnlyInventorySource(Protocol):
    """The complete external-source interface; it exposes no write operation."""

    source_system: str
    container_type: str

    def read(
        self,
        container_id: str,
        *,
        limit: int,
        max_pages: int,
    ) -> SourcePayload:
        """Read a bounded inventory without changing source state."""


class AdapterReadError(Exception):
    """A classified failure with a fixed, non-source-derived diagnostic."""

    status = "failed"
    code = "source_read_failed"
    category = "contract"
    summary = "The external source could not be normalized safely."
    retryable = False

    def __init__(self) -> None:
        super().__init__(self.summary)


class SourceUnavailable(AdapterReadError):
    status = "unavailable"
    code = "source_unavailable"
    category = "availability"
    summary = "The configured read-only source is unavailable."
    retryable = True


class SourceUnauthorized(AdapterReadError):
    status = "unauthorized"
    code = "source_unauthorized"
    category = "access"
    summary = "The read-only source is present but not authorized."
    retryable = False


class SourceRateLimited(AdapterReadError):
    status = "rate_limited"
    code = "source_rate_limited"
    category = "rate_limit"
    summary = "The external source declined the bounded read because of rate limits."
    retryable = True


class SourceContractFailure(AdapterReadError):
    status = "failed"
    code = "source_contract_failed"
    category = "contract"
    summary = "The read-only source returned an incompatible response shape."
    retryable = False


class UnsafeSourcePayload(AdapterReadError):
    status = "blocked"
    code = "unsafe_source_payload"
    category = "safety"
    summary = "The source response was blocked by credential or payload safety rules."
    retryable = False


def validate_read_bounds(limit: int, max_pages: int) -> None:
    if not 1 <= limit <= MAX_RECORD_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_RECORD_LIMIT}")
    if not 1 <= max_pages <= MAX_PAGES:
        raise ValueError(f"max_pages must be between 1 and {MAX_PAGES}")
