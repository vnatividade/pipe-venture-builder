"""Credential-free Hermes CLI compatibility probe."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from typing import Any


_VERSION = re.compile(r"Hermes Agent v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)")


def probe_hermes(executable: str = "hermes", *, timeout: float = 5.0) -> dict[str, Any]:
    """Read only `--version` with a minimal environment and no shell."""

    resolved = shutil.which(executable)
    if resolved is None:
        return {
            "available": False,
            "compatible": False,
            "command": executable,
            "version": None,
            "reason": "runtime_unavailable",
        }
    environment = {
        key: value
        for key, value in os.environ.items()
        if key in {"PATH", "LANG", "LC_ALL", "SYSTEMROOT", "PATHEXT"}
    }
    try:
        completed = subprocess.run(
            [resolved, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError):
        return {
            "available": False,
            "compatible": False,
            "command": executable,
            "version": None,
            "reason": "runtime_probe_failed",
        }
    match = _VERSION.search(completed.stdout or completed.stderr)
    if completed.returncode != 0 or match is None:
        return {
            "available": True,
            "compatible": False,
            "command": executable,
            "version": None,
            "reason": "runtime_version_unknown",
        }
    version = match.group("version")
    compatible = _version_tuple(version) >= (0, 17, 0)
    return {
        "available": True,
        "compatible": compatible,
        "command": executable,
        "version": version,
        "reason": None if compatible else "runtime_version_unsupported",
    }


def _version_tuple(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]
