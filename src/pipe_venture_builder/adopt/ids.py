"""Stable identifiers for deterministic adoption artifacts."""

from __future__ import annotations

import hashlib
import re
import unicodedata


def slug(value: str, *, fallback: str = "item") -> str:
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", normalized).strip("-._").lower()
    return normalized[:64] or fallback


def stable_id(prefix: str, value: str, *, label: str | None = None) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    readable = slug(label or value)
    return f"{prefix}-{readable[:40]}-{digest}"
