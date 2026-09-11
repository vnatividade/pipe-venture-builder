"""Delivery: the mission worktree, supervisor commits, one PR per branch, checks.

Everything is idempotent by construction: ``ensure_worktree`` reuses what
exists, ``open_pr`` asks ``gh pr list --head`` before creating, and
``checks_status`` only reads. Merge is never automatic.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

from .status import default_mission_home


WORKTREE_DIRNAME = "worktree"
SUPERVISOR_GIT_IDENTITY = ("pipe-mission-supervisor", "pipe-mission-supervisor@localhost")
MAX_SLUG_CHARS = 40
GIT_TIMEOUT_SECONDS = 300.0
GH_TIMEOUT_SECONDS = 120.0
CHECK_BUCKETS_FAILED = frozenset({"fail", "cancel"})
CHECK_BUCKETS_PENDING = frozenset({"pending"})



# Variáveis do interpretador do próprio supervisor (ex.: PYTHONPATH=src quando
# roda do código-fonte) não podem vazar para git/gh e seus hooks: o pre-push
# do repositório tentou `python3 -m pytest` por causa disso na demo de 11/09.
_INTERPRETER_ENV = ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONUSERBASE")

# Variáveis que um hook de worktree vinculado (``git worktree add``) exporta
# para apontar para o ADMINISTRATIVO daquele worktree — ``GIT_DIR`` absoluto
# incluído. Um filho git do supervisor que herdasse isso operaria no
# repositório errado; foi assim que a demo de 11/09 corrompeu o repositório
# real (``core.bare=true``, branch movida). Nenhum filho git/gh do supervisor
# e nenhum check de critério (``verify.run_check``) pode herdá-las.
GIT_CONTEXT_ENV = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_COMMON_DIR",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_PREFIX",
    "GIT_QUARANTINE_PATH",
    "GIT_NAMESPACE",
)


def child_env() -> dict[str, str]:
    """Environment for git/gh children: the caller's, minus interpreter leaks
    and minus the linked-worktree ``GIT_*`` variables (see ``GIT_CONTEXT_ENV``)."""

    excluded = frozenset(_INTERPRETER_ENV) | frozenset(GIT_CONTEXT_ENV)
    return {key: value for key, value in os.environ.items() if key not in excluded}


@lru_cache(maxsize=1)
def _no_hooks_dir() -> str:
    """A fresh, empty directory outside any worktree, used as ``core.hooksPath``
    for every commit/push the supervisor runs.

    ``core.hooksPath`` defaults to (or is often configured as) a path inside
    the repository, resolved relative to whatever tree git is invoked from.
    A git command the supervisor runs with ``cwd=<mission worktree>`` would
    then execute hook scripts sitting in that worktree — code the worker may
    have written — with the supervisor's credentials. Verification of the
    diff and CI are the real gate; a local hook never runs during delivery.
    """

    return tempfile.mkdtemp(prefix="pipe-mission-no-hooks-")


def _no_hooks_args() -> list[str]:
    return ["-c", f"core.hooksPath={_no_hooks_dir()}"]


@dataclass(frozen=True)
class PullRequest:
    url: str
    number: int | None
    created: bool


# -- naming --------------------------------------------------------------------


def slugify(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    slug = slug[:MAX_SLUG_CHARS].rstrip("-")
    return slug or "mission"


def branch_name(mission: Mapping[str, Any]) -> str:
    return f"claude/{mission['missionId']}-{slugify(mission['title'])}"


def mission_home(mission_id: str, home: str | Path | None = None) -> Path:
    root = Path(home) if home is not None else default_mission_home()
    return root / mission_id


def worktree_path(mission_id: str, home: str | Path | None = None) -> Path:
    return mission_home(mission_id, home) / WORKTREE_DIRNAME


def base_branch(mission: Mapping[str, Any]) -> str:
    """``origin/main`` → ``main`` for ``gh pr create --base``."""

    base_ref = mission["workspace"]["baseRef"]
    return base_ref.split("/", 1)[1] if base_ref.startswith("origin/") else base_ref


# -- worktree ------------------------------------------------------------------


def ensure_worktree(mission: Mapping[str, Any], *, home: str | Path | None = None) -> Path:
    """``git worktree add <home>/<id>/worktree -b claude/<id>-<slug> <baseRef>``, once."""

    repo = mission["workspace"]["repo"]
    path = worktree_path(mission["missionId"], home)
    branch = branch_name(mission)
    if path.is_dir() and _is_mission_worktree(path, repo, branch):
        return path
    _git(repo, "worktree", "prune")
    if path.exists():
        if any(path.iterdir()):
            raise RuntimeError(
                "mission worktree path exists and is not this mission's worktree "
                "(other repository, other branch, or not a worktree)"
            )
        path.rmdir()
    path.parent.mkdir(parents=True, exist_ok=True)
    if _branch_exists(repo, branch):
        _git(repo, "worktree", "add", str(path), branch)
    else:
        # ``--no-track``: a remote ``baseRef`` (``origin/main``) would otherwise
        # set ``branch.<branch>.remote``/``.merge`` in the repository's *shared*
        # config — another mission creating its own worktree during this
        # mission's worker run would then change what ``git_config_snapshot``
        # sees and trip ``git_config_tampered`` on a run that tampered nothing.
        _git(repo, "worktree", "add", "--no-track", str(path), "-b", branch, mission["workspace"]["baseRef"])
    return path


def git_config_snapshot(repo: str | Path, worktree: str | Path) -> dict[str, str | None]:
    """Hashes of the repository-level git config seen from the main checkout
    and from the worktree (``--local``, and ``--worktree`` when git accepts it).

    A worktree shares the main checkout's config, so a ``git config`` run by
    the worker changes what every later git command of the supervisor does
    (``core.hooksPath``, ``core.fsmonitor``, ``remote.origin.url``...). The
    supervisor compares a snapshot before and after each worker run. Only
    hashes are kept: the config may hold credentials in URLs.
    """

    snapshot: dict[str, str | None] = {}
    for label, cwd in (("repo", repo), ("worktree", worktree)):
        for scope in ("--local", "--worktree"):
            completed = subprocess.run(
                ["git", "config", scope, "--list", "--null"],
                cwd=str(cwd), capture_output=True, timeout=GIT_TIMEOUT_SECONDS, check=False, env=child_env(),
            )
            key = f"{label}:{scope.lstrip('-')}"
            if completed.returncode != 0:
                # ``--worktree`` fails without ``extensions.worktreeConfig`` when
                # there are several worktrees; the error itself is the state.
                snapshot[key] = None if scope == "--worktree" else f"error:{completed.returncode}"
                continue
            snapshot[key] = hashlib.sha256(completed.stdout).hexdigest()
    return snapshot


def commit_if_needed(worktree: str | Path, message: str) -> bool:
    """Stage and commit whatever the worker left uncommitted (write set already verified).

    When the repository has no git identity configured, the commit carries a
    fixed supervisor identity instead of failing.
    """

    if not _git(worktree, "status", "--porcelain").strip():
        return False
    _git(worktree, "add", "-A")
    _git(worktree, *_identity_args(worktree), *_no_hooks_args(), "commit", "-q", "-m", message)
    return True


def _identity_args(worktree: str | Path) -> list[str]:
    probe = subprocess.run(
        ["git", "config", "user.email"],
        cwd=str(worktree), capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, check=False, env=child_env(),
    )
    if probe.returncode == 0 and probe.stdout.strip():
        return []
    name, email = SUPERVISOR_GIT_IDENTITY
    return ["-c", f"user.name={name}", "-c", f"user.email={email}"]


def push_branch(worktree: str | Path, branch: str) -> None:
    """Publish HEAD — the commit that was verified — as ``branch``; never the
    local branch ref by name, which may not be where HEAD is."""

    _git(worktree, *_no_hooks_args(), "push", "-q", "origin", f"HEAD:refs/heads/{branch}")


def current_branch(worktree: str | Path) -> str | None:
    """The branch HEAD is on, or ``None`` when HEAD is detached."""

    completed = subprocess.run(
        ["git", "symbolic-ref", "-q", "HEAD"],
        cwd=str(worktree), capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, check=False, env=child_env(),
    )
    ref = completed.stdout.strip()
    if completed.returncode != 0 or not ref.startswith("refs/heads/"):
        return None
    return ref[len("refs/heads/"):]


# -- pull request --------------------------------------------------------------


def existing_pr(gh_bin: str, branch: str, *, cwd: str | Path) -> PullRequest | None:
    output = _gh(gh_bin, ["pr", "list", "--head", branch, "--state", "open", "--json", "number,url"], cwd=cwd)
    try:
        listed = json.loads(output or "[]")
    except ValueError as exc:
        raise RuntimeError("gh pr list returned invalid JSON") from exc
    for item in listed:
        if isinstance(item, Mapping) and isinstance(item.get("url"), str):
            number = item.get("number")
            return PullRequest(url=item["url"], number=number if isinstance(number, int) else None, created=False)
    return None


def open_pr(
    worktree: str | Path,
    gh_bin: str,
    title: str,
    body: str,
    *,
    branch: str,
    base: str,
) -> PullRequest:
    """Open the PR for ``branch`` unless one is already open (checked first)."""

    found = existing_pr(gh_bin, branch, cwd=worktree)
    if found is not None:
        return found
    push_branch(worktree, branch)
    handle = tempfile.NamedTemporaryFile("w", suffix=".md", prefix="pipe-mission-pr-", delete=False, encoding="utf-8")
    try:
        handle.write(body)
        handle.close()
        output = _gh(
            gh_bin,
            ["pr", "create", "--title", title, "--body-file", handle.name, "--head", branch, "--base", base],
            cwd=worktree,
        )
    finally:
        try:
            os.unlink(handle.name)
        except OSError:
            pass
    url = _last_url(output)
    if url is None:
        raise RuntimeError("gh pr create did not return a pull request URL")
    return PullRequest(url=url, number=_pr_number(url), created=True)


def checks_status(gh_bin: str, branch: str, *, cwd: str | Path) -> str:
    """``pending`` | ``passed`` | ``failed`` | ``none`` from ``gh pr checks --json``."""

    output = _gh(
        gh_bin,
        ["pr", "checks", branch, "--json", "bucket,name,state"],
        cwd=cwd,
        ok_codes=(0, 1, 8),
    )
    try:
        checks = json.loads(output or "[]")
    except ValueError as exc:
        raise RuntimeError("gh pr checks returned invalid JSON") from exc
    buckets = [item.get("bucket") for item in checks if isinstance(item, Mapping)]
    if not buckets:
        return "none"
    if any(bucket in CHECK_BUCKETS_FAILED for bucket in buckets):
        return "failed"
    if any(bucket in CHECK_BUCKETS_PENDING for bucket in buckets):
        return "pending"
    return "passed"


# -- PR text -------------------------------------------------------------------


def pr_title(mission: Mapping[str, Any]) -> str:
    return f"{mission['missionId']}: {mission['title']}"


def pr_body(
    mission: Mapping[str, Any],
    *,
    criteria: Sequence[Mapping[str, Any]],
    cost_usd: float,
    cycles: int,
) -> str:
    """The PR body in the shape of ``.github/pull_request_template.md``.

    It carries ids, criteria states, counts and cost — never the founder's
    intent text, the brief, or the worker's prose.
    """

    tickets = list(mission.get("linearTicketIds") or [])
    if "PIP-902" not in tickets:
        tickets.append("PIP-902")
    criteria_lines = "\n".join(
        f"- {item['id']} ({item['kind']}): {'satisfied' if item['satisfied'] else 'pending'}"
        for item in criteria
    ) or "- (no criteria recorded)"
    write_set = "\n".join(f"- `{entry}`" for entry in mission["workspace"]["writeSet"])
    non_goals = "\n".join(f"- {item}" for item in mission["nonGoals"]) or "- None declared."
    checks = "\n".join(
        f"- Command/check: `{item['command']}`"
        for item in mission["successCriteria"]
        if item["kind"] == "check"
    ) or "- Command/check: none declared as `check`; see artifacts and rubric."
    return f"""## Linear Ticket

Link: {", ".join(tickets)}

## Context

Opened by the Pipe Mission Loop supervisor for mission `{mission['missionId']}` (v{mission['version']}, "{mission['title']}"), implemented under PIP-902. The worker ran headless in an isolated worktree; the diff was verified against the declared write set and criteria before this PR was opened. Merge is reserved to a human.

## Included Scope

{write_set}

## Excluded Scope

{non_goals}

## Development Execution Loop

- Status: lightweight (Mission Loop cycle)
- Current slice: mission `{mission['missionId']}`, {cycles} cycle(s)
- ADR/RFC decision: not applicable
- Validation and repair expectation: criteria below must stay satisfied; CI checks must pass before the mission completes
- Documentation updates: inside the write set only
- Follow-up trigger: any criterion not satisfied after review

## Validation Performed

{checks}
- Write set check: `git diff --name-only --no-renames <baseRef>...HEAD` + `git status --porcelain --no-renames` inside the declared write set

Criteria at PR time:
{criteria_lines}

## Review Status

- Review requested: automated reviewer (clean-context `claude -p`, read-only) per cycle; repository review still required before merge
- Review source: Mission Loop reviewer + repository review path
- Fallback approval source, if used: not applicable
- P0 findings: 0 known
- P1 findings: 0 known
- P2 findings: not assessed here
- P3 findings: not assessed here
- Fixed in this PR: see criteria
- Not fixed: see pending criteria, if any

## Risks And Residual Concerns

- Risk: the worker's reasoning is not part of this PR; only the diff is.
- Mitigation or reason accepted: deterministic verification + independent review; human merge gate.

## Follow-Ups

No follow-ups identified by the supervisor. Record any in Linear under {", ".join(tickets)}.

## Context And Token Efficiency

- Context strategy: brief compiled from the mission; fresh context per cycle
- Full artifacts read: by the worker inside the worktree
- Targeted searches or snippets used: not tracked
- Known omitted context: worker transcript (never persisted)
- Token/cost/session signal: US$ {cost_usd:.2f} accumulated across worker and reviewer runs

## Handoff Notes

- Branch: `{branch_name(mission)}`
- Acceptance criteria result: see "Criteria at PR time"
- Knowledge or decision artifacts updated: none outside the write set
- Residual risks: merge and any file outside the write set remain reserved to a human
"""


# -- internals -----------------------------------------------------------------


def _is_mission_worktree(path: Path, repo: str | Path, branch: str) -> bool:
    """``path`` is the top of a worktree of ``repo`` checked out on ``branch``.

    ``rev-parse --is-inside-work-tree`` alone is true for any directory inside
    any repository, and for a worktree of another repository or branch.
    """

    top = _rev_parse(path, "--show-toplevel")
    if top is None or top != path.resolve():
        return False
    common = _rev_parse(path, "--git-common-dir")
    expected = _rev_parse(Path(repo), "--git-common-dir")
    if common is None or expected is None or common != expected:
        return False
    return current_branch(path) == branch


def _rev_parse(cwd: Path, option: str) -> Path | None:
    """An absolute, resolved path printed by ``git rev-parse <option>``."""

    try:
        completed = subprocess.run(
            ["git", "rev-parse", option],
            cwd=str(cwd), capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, check=False, env=child_env(),
        )
    except OSError:
        return None
    output = completed.stdout.strip()
    if completed.returncode != 0 or not output:
        return None
    printed = Path(output)
    return (printed if printed.is_absolute() else Path(cwd) / printed).resolve()


def _branch_exists(repo: str | Path, branch: str) -> bool:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=str(repo), capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, check=False, env=child_env(),
    )
    return completed.returncode == 0


def _git(cwd: str | Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=GIT_TIMEOUT_SECONDS, check=False, env=child_env(),
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed with exit code {completed.returncode}")
    return completed.stdout


def _gh(gh_bin: str, args: Sequence[str], *, cwd: str | Path, ok_codes: tuple[int, ...] = (0,)) -> str:
    with open(os.devnull, "rb") as devnull:
        completed = subprocess.run(
            [gh_bin, *args],
            cwd=str(cwd), stdin=devnull, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=GH_TIMEOUT_SECONDS, check=False, env=child_env(),
        )
    if completed.returncode not in ok_codes:
        raise RuntimeError(f"gh {' '.join(args[:2])} failed with exit code {completed.returncode}")
    return completed.stdout


def _last_url(output: str) -> str | None:
    for line in reversed(output.splitlines()):
        candidate = line.strip()
        if candidate.startswith("https://"):
            return candidate
    return None


def _pr_number(url: str) -> int | None:
    match = re.search(r"/pull/(\d+)/?$", url)
    return int(match.group(1)) if match else None
