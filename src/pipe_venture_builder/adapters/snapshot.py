"""Canonical ExternalSnapshot construction and failure mapping."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Mapping

from .contracts import (
    DEFAULT_MAX_PAGES,
    DEFAULT_RECORD_LIMIT,
    AdapterReadError,
    ReadOnlyInventorySource,
    SNAPSHOT_SCHEMA_VERSION,
    SourceContractFailure,
    UnsafeSourcePayload,
    validate_read_bounds,
)
from .safety import UnsafeValueError, payload_is_safe, safe_identifier, safe_url

Normalizer = Callable[
    [Mapping[str, Any], tuple[Mapping[str, Any], ...], str], list[dict[str, Any]]
]
_GIT_SHA = re.compile(r"^[A-Fa-f0-9]{7,64}$")


def capture_snapshot(
    source: ReadOnlyInventorySource,
    container_id: str,
    normalizer: Normalizer,
    *,
    captured_at: str | None = None,
    limit: int = DEFAULT_RECORD_LIMIT,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> dict[str, Any]:
    """Read, normalize, and seal one bounded snapshot with fixed diagnostics."""

    validate_read_bounds(limit, max_pages)
    safe_container_id = safe_identifier(container_id)
    observed_at = captured_at or _now()
    _require_datetime(observed_at)

    try:
        payload = source.read(
            safe_container_id,
            limit=limit,
            max_pages=max_pages,
        )
        if not payload_is_safe(payload.container) or not payload_is_safe(payload.items):
            raise UnsafeSourcePayload()
        records = normalizer(payload.container, payload.items, observed_at)
        if not payload_is_safe(records):
            raise UnsafeSourcePayload()
        container_url = safe_url(payload.container.get("url"))
    except AdapterReadError as exc:
        return _failure_snapshot(
            source_system=source.source_system,
            container_type=source.container_type,
            container_id=safe_container_id,
            captured_at=observed_at,
            limit=limit,
            error=exc,
        )
    except UnsafeValueError:
        return _failure_snapshot(
            source_system=source.source_system,
            container_type=source.container_type,
            container_id=safe_container_id,
            captured_at=observed_at,
            limit=limit,
            error=UnsafeSourcePayload(),
        )
    except (KeyError, TypeError, ValueError):
        return _failure_snapshot(
            source_system=source.source_system,
            container_type=source.container_type,
            container_id=safe_container_id,
            captured_at=observed_at,
            limit=limit,
            error=SourceContractFailure(),
        )

    records = sorted(records, key=lambda item: (item["entityType"], item["sourceId"]))
    returned_count = len(payload.items)
    diagnostics: list[dict[str, Any]] = []
    if payload.truncated:
        status = "partial"
        diagnostics.append(
            _diagnostic(
                "inventory_truncated",
                "pagination",
                "warning",
                "The bounded inventory stopped before all source records were read.",
                True,
            )
        )
    elif returned_count == 0:
        status = "empty"
        diagnostics.append(
            _diagnostic(
                "source_empty",
                "availability",
                "info",
                "The authorized read completed and returned no child records.",
                False,
            )
        )
    else:
        status = "complete"

    return _snapshot(
        source_system=source.source_system,
        container_type=source.container_type,
        container_id=safe_container_id,
        container_url=container_url,
        captured_at=observed_at,
        status=status,
        records=records,
        limit=limit,
        returned_count=returned_count,
        pages_read=payload.pages_read,
        truncated=payload.truncated,
        diagnostics=diagnostics,
    )


def make_record(
    *,
    source_system: str,
    source_id: Any,
    source_key: Any,
    entity_type: str,
    observed_at: str,
    title: Any = None,
    state: Any = None,
    url: Any = None,
    source_created_at: Any = None,
    source_updated_at: Any = None,
    source_closed_at: Any = None,
    relationships: Iterable[dict[str, str]] = (),
    attributes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a schema-shaped record while preserving only the allowlisted fields."""

    from .safety import safe_text

    normalized_source_id = safe_identifier(source_id)
    normalized_relationships = sorted(
        (
            {
                "type": safe_identifier(relationship["type"]),
                "targetSourceId": safe_identifier(relationship["targetSourceId"]),
            }
            for relationship in relationships
        ),
        key=lambda item: (item["type"], item["targetSourceId"]),
    )
    base_attributes: dict[str, Any] = {
        "number": None,
        "priority": None,
        "labels": [],
        "draft": None,
        "merged": None,
        "reviewDecision": None,
        "baseBranch": None,
        "headBranch": None,
        "headSha": None,
        "mergeCommitSha": None,
        "defaultBranch": None,
        "tag": None,
        "prerelease": None,
        "checkSummary": None,
    }
    if attributes:
        unknown = set(attributes).difference(base_attributes)
        if unknown:
            raise ValueError("unsupported normalized attribute")
        base_attributes.update(attributes)
    labels = base_attributes["labels"]
    if not isinstance(labels, list):
        raise ValueError("labels must be a list")
    base_attributes["labels"] = sorted(
        {label for item in labels if (label := safe_text(item, limit=100))}
    )
    for key in (
        "reviewDecision",
        "baseBranch",
        "headBranch",
        "defaultBranch",
        "tag",
    ):
        base_attributes[key] = safe_text(base_attributes[key], limit=256)
    for key in ("headSha", "mergeCommitSha"):
        if base_attributes[key] is not None:
            candidate = str(base_attributes[key])
            if not _GIT_SHA.fullmatch(candidate):
                raise ValueError("invalid Git commit identifier")
            base_attributes[key] = candidate

    return {
        "recordId": _stable_id(
            "ER", source_system, f"{entity_type}:{normalized_source_id}"
        ),
        "sourceId": normalized_source_id,
        "sourceKey": safe_identifier(source_key),
        "entityType": entity_type,
        "title": safe_text(title),
        "state": safe_text(state, limit=100),
        "url": safe_url(url),
        "sourceCreatedAt": _optional_datetime(source_created_at),
        "sourceUpdatedAt": _optional_datetime(source_updated_at),
        "sourceClosedAt": _optional_datetime(source_closed_at),
        "observedAt": observed_at,
        "relationships": normalized_relationships,
        "attributes": base_attributes,
    }


def _failure_snapshot(
    *,
    source_system: str,
    container_type: str,
    container_id: str,
    captured_at: str,
    limit: int,
    error: AdapterReadError,
) -> dict[str, Any]:
    return _snapshot(
        source_system=source_system,
        container_type=container_type,
        container_id=container_id,
        container_url=None,
        captured_at=captured_at,
        status=error.status,
        records=[],
        limit=limit,
        returned_count=0,
        pages_read=0,
        truncated=False,
        diagnostics=[
            _diagnostic(
                error.code,
                error.category,
                "error",
                error.summary,
                error.retryable,
            )
        ],
    )


def _snapshot(
    *,
    source_system: str,
    container_type: str,
    container_id: str,
    container_url: str | None,
    captured_at: str,
    status: str,
    records: list[dict[str, Any]],
    limit: int,
    returned_count: int,
    pages_read: int,
    truncated: bool,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    identity = json.dumps(
        {
            "sourceSystem": source_system,
            "containerId": container_id,
            "capturedAt": captured_at,
            "status": status,
            "records": records,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "schemaVersion": SNAPSHOT_SCHEMA_VERSION,
        "snapshotId": _stable_id("ES", source_system, identity),
        "sourceSystem": source_system,
        "sourceContainer": {
            "type": container_type,
            "id": container_id,
            "url": container_url,
        },
        "capturedAt": captured_at,
        "status": status,
        "records": records,
        "pagination": {
            "limit": limit,
            "returnedCount": returned_count,
            "pagesRead": pages_read,
            "truncated": truncated,
        },
        "constraints": {
            "readOnly": True,
            "mutationSurfaceExposed": False,
            "credentialsPersisted": False,
            "rawPayloadPersisted": False,
        },
        "diagnostics": diagnostics,
    }


def _diagnostic(
    code: str,
    category: str,
    severity: str,
    summary: str,
    retryable: bool,
) -> dict[str, Any]:
    return {
        "code": code,
        "category": category,
        "severity": severity,
        "summary": summary,
        "retryable": retryable,
    }


def _stable_id(prefix: str, source_system: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{source_system}-{digest}"


def _now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _optional_datetime(value: Any) -> str | None:
    if value in (None, ""):
        return None
    candidate = str(value)
    _require_datetime(candidate)
    return candidate


def _require_datetime(value: str) -> None:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        raise ValueError("date-time must include a timezone")
