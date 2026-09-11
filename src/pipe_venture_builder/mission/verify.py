"""Deterministic verification: write set, ``check`` and ``artifact`` criteria.

Runs before any reviewer. Everything here reduces to booleans, return codes,
sizes and fingerprints; command output is measured, never kept, so nothing
from a check can reach the store.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from pipe_venture_builder.control_plane.model import fingerprint


DEFAULT_CHECK_TIMEOUT_SECONDS = 600.0
GIT_TIMEOUT_SECONDS = 120.0


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    returncode: int | None
    output_bytes: int
    timed_out: bool


@dataclass(frozen=True)
class ArtifactResult:
    exists: bool
    satisfied: bool
    fingerprint: str | None


@dataclass(frozen=True)
class CriterionResult:
    id: str
    kind: str
    satisfied: bool
    evidence_ref: str
    evidence_fingerprint: str | None
    returncode: int | None = None


# -- write set -----------------------------------------------------------------


def changed_files(worktree: str | Path, base_ref: str) -> list[str]:
    """Paths touched since ``base_ref``: committed, staged, unstaged, untracked."""

    files: set[str] = set()
    committed = _git(worktree, "diff", "--name-only", f"{base_ref}...HEAD")
    files.update(line.strip() for line in committed.splitlines() if line.strip())
    for line in _git(worktree, "status", "--porcelain", "--untracked-files=all").splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            old, new = path.split(" -> ", 1)
            files.add(_unquote(old))
            files.add(_unquote(new))
        else:
            files.add(_unquote(path))
    return sorted(files)


def outside_write_set(files: Iterable[str], write_set: Iterable[str]) -> list[str]:
    allowed = [entry.rstrip("/") for entry in write_set]
    offending = []
    for file in files:
        normalized = str(PurePosixPath(file))
        if not any(
            normalized == entry or normalized.startswith(entry + "/") for entry in allowed
        ):
            offending.append(file)
    return sorted(offending)


def within_write_set(files: Iterable[str], write_set: Iterable[str]) -> bool:
    return not outside_write_set(files, write_set)


# -- criteria ------------------------------------------------------------------


def run_check(
    command: str, cwd: str | Path, *, timeout: float = DEFAULT_CHECK_TIMEOUT_SECONDS
) -> CheckResult:
    """Run a ``check`` command through the shell in ``cwd``; keep rc and size only."""

    with open(os.devnull, "rb") as devnull:
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                stdin=devnull,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            size = len(exc.stdout or b"") if isinstance(exc.stdout, (bytes, bytearray)) else 0
            return CheckResult(passed=False, returncode=None, output_bytes=size, timed_out=True)
    return CheckResult(
        passed=completed.returncode == 0,
        returncode=completed.returncode,
        output_bytes=len(completed.stdout or b""),
        timed_out=False,
    )


def check_artifact(path: str | Path, must_match: str | None) -> ArtifactResult:
    target = Path(path)
    if not target.is_file():
        return ArtifactResult(exists=False, satisfied=False, fingerprint=None)
    content = target.read_bytes()
    digest = fingerprint(content.decode("utf-8", errors="replace"))
    if must_match is None:
        return ArtifactResult(exists=True, satisfied=True, fingerprint=digest)
    matched = re.search(must_match, content.decode("utf-8", errors="replace")) is not None
    return ArtifactResult(exists=True, satisfied=matched, fingerprint=digest)


def verify_criteria(
    mission: Mapping[str, Any],
    worktree: str | Path,
    *,
    check_timeout: float = DEFAULT_CHECK_TIMEOUT_SECONDS,
) -> list[CriterionResult]:
    """Evaluate every ``check`` and ``artifact`` criterion; rubrics are the reviewer's."""

    root = Path(worktree)
    results: list[CriterionResult] = []
    for criterion in mission["successCriteria"]:
        kind = criterion["kind"]
        if kind == "check":
            cwd = root / criterion.get("cwd", ".")
            outcome = run_check(criterion["command"], cwd, timeout=check_timeout)
            code = "timeout" if outcome.timed_out else f"rc{outcome.returncode}"
            results.append(
                CriterionResult(
                    id=criterion["id"],
                    kind=kind,
                    satisfied=outcome.passed,
                    evidence_ref=f"check:{criterion['id']}:{code}",
                    evidence_fingerprint=None,
                    returncode=outcome.returncode,
                )
            )
        elif kind == "artifact":
            outcome_artifact = check_artifact(root / criterion["path"], criterion.get("mustMatch"))
            results.append(
                CriterionResult(
                    id=criterion["id"],
                    kind=kind,
                    satisfied=outcome_artifact.satisfied,
                    evidence_ref=f"artifact:{criterion['id']}",
                    evidence_fingerprint=outcome_artifact.fingerprint,
                )
            )
    return results


# -- diff ----------------------------------------------------------------------


def diff_text(worktree: str | Path, base_ref: str) -> str:
    """One diff from the merge base with ``base_ref`` to the working tree, plus
    untracked files. Committing the same content does not change it, so the
    circuit breaker never mistakes a commit for progress."""

    merge_base = _git(worktree, "merge-base", base_ref, "HEAD").strip()
    parts = [_git(worktree, "diff", merge_base)]
    untracked = _git(worktree, "ls-files", "--others", "--exclude-standard")
    for line in untracked.splitlines():
        path = line.strip()
        if path:
            parts.append(_git(worktree, "diff", "--no-index", "--", os.devnull, path, ok_codes=(0, 1)))
    return "".join(part for part in parts if part)


def diff_fingerprint(worktree: str | Path, base_ref: str) -> str:
    return fingerprint(diff_text(worktree, base_ref))


# -- internals -----------------------------------------------------------------


def _git(worktree: str | Path, *args: str, ok_codes: tuple[int, ...] = (0,)) -> str:
    completed = subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=str(worktree),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=GIT_TIMEOUT_SECONDS,
        check=False,
    )
    if completed.returncode not in ok_codes:
        raise RuntimeError(f"git {args[0]} failed with exit code {completed.returncode}")
    return completed.stdout


def _unquote(path: str) -> str:
    path = path.strip()
    if len(path) >= 2 and path[0] == '"' and path[-1] == '"':
        return path[1:-1].encode("utf-8").decode("unicode_escape")
    return path
