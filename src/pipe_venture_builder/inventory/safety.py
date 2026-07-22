"""Safety classification for repository metadata sources.

The adoption scanner is allowlist-first. Files with sensitive-looking names are
never opened, and allowlisted text is rejected as a whole when a secret-shaped
value is detected. Rejected names and values are deliberately not returned to
callers so they cannot leak into a ProductBaseline or an error message.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

MAX_METADATA_BYTES = 128 * 1024

_SENSITIVE_NAME = re.compile(
    r"(?:^|[._-])(secret|secrets|credential|credentials|token|tokens|password|passwords|private[-_]?key)(?:$|[._-])",
    re.IGNORECASE,
)
_SECRET_VALUE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(
        r"(?im)[\"']?\b(?:api[_-]?key|client[_-]?secret|private[_-]?key|secret|token|password|passwd)\b[\"']?"
        r"\s*[:=]\s*[\"']?[^\s\"'`]{8,}"
    ),
)
_DENIED_EXACT_NAMES = {
    ".env",
    ".netrc",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}
_DENIED_SUFFIXES = {".der", ".jks", ".key", ".p12", ".pem", ".pfx"}


@dataclass(frozen=True, slots=True)
class SafeText:
    """Result of reading one explicitly allowlisted metadata file."""

    status: str
    text: str | None = None


def is_sensitive_path(path: Path) -> bool:
    """Return whether any path segment looks like secret-bearing material."""

    for part in path.parts:
        lowered = part.lower()
        if lowered in _DENIED_EXACT_NAMES or lowered.startswith(".env."):
            return True
        if Path(lowered).suffix in _DENIED_SUFFIXES:
            return True
        if _SENSITIVE_NAME.search(lowered):
            return True
    return False


def read_allowlisted_text(path: Path) -> SafeText:
    """Read a small allowlisted UTF-8 file without returning unsafe contents."""

    if is_sensitive_path(Path(path.name)) or path.is_symlink():
        return SafeText("blocked")
    try:
        if not path.is_file():
            return SafeText("unavailable")
        if path.stat().st_size > MAX_METADATA_BYTES:
            return SafeText("bounded")
        raw = path.read_bytes()
    except (OSError, PermissionError):
        return SafeText("unavailable")

    if b"\x00" in raw:
        return SafeText("blocked")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return SafeText("blocked")
    if contains_sensitive_value(text):
        return SafeText("blocked")
    return SafeText("safe", text)


def contains_sensitive_value(text: str) -> bool:
    """Detect common secret shapes without returning the matching value."""

    return any(pattern.search(text) is not None for pattern in _SECRET_VALUE_PATTERNS)
