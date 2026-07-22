"""Credential and raw-payload guards for connector inventories."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlsplit

from pipe_venture_builder.inventory.safety import contains_sensitive_value

MAX_SOURCE_PAYLOAD_BYTES = 2 * 1024 * 1024

_FORBIDDEN_KEYS = {
    "access_token",
    "apikey",
    "api_key",
    "authorization",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "headers",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "set_cookie",
    "token",
}
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+=-]{0,255}$")


class UnsafeValueError(ValueError):
    """An allowlisted normalized value crossed the snapshot safety boundary."""


def payload_is_safe(value: Any) -> bool:
    """Return false without returning or rendering unsafe source material."""

    try:
        encoded = json.dumps(value, ensure_ascii=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        return False
    if len(encoded) > MAX_SOURCE_PAYLOAD_BYTES:
        return False
    return _walk_is_safe(value)


def safe_identifier(value: Any) -> str:
    candidate = str(value or "")
    if not _SAFE_IDENTIFIER.fullmatch(candidate):
        raise UnsafeValueError("unsafe external identifier")
    if contains_sensitive_value(candidate):
        raise UnsafeValueError("secret-shaped external identifier")
    return candidate


def safe_text(value: Any, *, limit: int = 500) -> str | None:
    if value is None:
        return None
    candidate = " ".join(str(value).split())
    if not candidate:
        return None
    if contains_sensitive_value(candidate):
        raise UnsafeValueError("secret-shaped external text")
    return candidate[:limit]


def safe_url(value: Any) -> str | None:
    if value is None:
        return None
    candidate = str(value)
    parsed = urlsplit(candidate)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or contains_sensitive_value(candidate)
    ):
        raise UnsafeValueError("unsafe external URL")
    return candidate


def _walk_is_safe(value: Any) -> bool:
    if isinstance(value, str):
        return not contains_sensitive_value(value)
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in _FORBIDDEN_KEYS or not _walk_is_safe(item):
                return False
        return True
    if isinstance(value, (list, tuple)):
        return all(_walk_is_safe(item) for item in value)
    return value is None or isinstance(value, (bool, int, float))
