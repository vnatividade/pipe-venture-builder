"""Shared deterministic primitives for the local control plane."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from pipe_venture_builder.inventory.safety import contains_sensitive_value


SCHEMA_VERSION = "0.1.0"
FINGERPRINT_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")
SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+=-]{0,511}$")


class ControlPlaneContractError(ValueError):
    """A caller supplied an unsafe or incompatible control-plane document."""


class ControlPlaneStateError(RuntimeError):
    """Durable state conflicts with the requested transition."""


def fingerprint(value: Any) -> str:
    try:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ControlPlaneContractError("value is not canonical JSON") from exc
    return f"sha256:{hashlib.sha256(encoded.encode('utf-8')).hexdigest()}"


def stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}-{fingerprint(value).split(':', 1)[1][:12]}"


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ControlPlaneContractError("value is not canonical JSON") from exc


def parse_datetime(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ControlPlaneContractError("timestamp must be RFC 3339 text")
    try:
        candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ControlPlaneContractError("timestamp must be RFC 3339 text") from exc
    if parsed.tzinfo is None:
        raise ControlPlaneContractError("timestamp must include a timezone")
    return parsed


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def require_fingerprint(value: Any, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not FINGERPRINT_PATTERN.fullmatch(value):
        raise ControlPlaneContractError("invalid fingerprint")
    return value


def safe_identifier(value: Any, *, limit: int = 512) -> str:
    if not isinstance(value, str):
        raise ControlPlaneContractError("identifier must be text")
    candidate = value[:limit]
    if candidate != value or not SAFE_IDENTIFIER_PATTERN.fullmatch(candidate):
        raise ControlPlaneContractError("invalid safe identifier")
    if contains_sensitive_value(candidate):
        raise ControlPlaneContractError("secret-shaped identifier is forbidden")
    return candidate


def require_stable_id(value: Any, prefix: str) -> str:
    candidate = safe_identifier(value)
    if re.fullmatch(rf"{re.escape(prefix)}-[a-f0-9]{{12}}", candidate) is None:
        raise ControlPlaneContractError("invalid stable identifier")
    return candidate
