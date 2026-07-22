"""Stable identifiers for deterministic idea intake."""

from __future__ import annotations

import hashlib
import re
import unicodedata


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def slug(value: str, *, fallback: str = "idea") -> str:
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", normalized).strip("-._").lower()
    return normalized[:64] or fallback


def stable_id(prefix: str, value: str, *, label: str) -> str:
    return f"{prefix}-{slug(label)[:40]}-{digest(value)[:10]}"
