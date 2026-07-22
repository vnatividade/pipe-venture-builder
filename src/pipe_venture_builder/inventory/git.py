"""Read-only Git metadata inventory using argument-based subprocess calls."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True, slots=True)
class GitInventory:
    """Bounded Git facts that are safe to normalize into a baseline."""

    present: bool
    has_history: bool
    commit_count: int
    head_commit: str | None
    committed_at: str | None


def inspect_git(repository: Path) -> GitInventory:
    """Inspect local Git state without reading remotes, diffs, or file contents."""

    inside = _run_git(repository, "rev-parse", "--is-inside-work-tree")
    if inside != "true":
        return GitInventory(False, False, 0, None, None)
    top_level = _run_git(repository, "rev-parse", "--show-toplevel")
    try:
        is_repository_root = bool(top_level) and Path(top_level).resolve(
            strict=True
        ) == repository.resolve(strict=True)
    except (OSError, FileNotFoundError):
        is_repository_root = False
    if not is_repository_root:
        return GitInventory(False, False, 0, None, None)

    head = _run_git(repository, "rev-parse", "--verify", "HEAD")
    if not head:
        return GitInventory(True, False, 0, None, None)

    count_text = _run_git(repository, "rev-list", "--count", "HEAD")
    committed_at = _normalize_git_datetime(
        _run_git(repository, "show", "-s", "--format=%cI", "HEAD")
    )
    try:
        count = int(count_text or "0")
    except ValueError:
        count = 0
    return GitInventory(True, True, max(count, 0), head, committed_at)


def _run_git(repository: Path, *arguments: str) -> str | None:
    environment = {
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
        "PATH": os.environ.get("PATH", ""),
    }
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _normalize_git_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (
        parsed.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
