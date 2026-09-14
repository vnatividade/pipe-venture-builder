"""Delivery: the mission worktree, supervisor commits, one PR per branch, checks.

Everything is idempotent by construction: ``ensure_worktree`` reuses what
exists and otherwise adopts (never creates — PIP-915) the worktree a worker
run's own ``--worktree`` already produced, ``open_pr`` asks ``gh pr list
--head`` before creating, and ``checks_status`` only reads. Merge is never
automatic.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import stop_gate as _stop_gate
from .status import default_mission_home


class WorktreeNotReady(RuntimeError):
    """No native worktree exists yet for this mission (PIP-915): a worker run
    with ``--worktree`` has to create one before ``ensure_worktree`` can adopt
    it. Never raised once the mission's worktree has been adopted once."""


class WorktreeBaseMissing(RuntimeError):
    """The mission's ``baseRef`` resolves to no commit (PIP-918). Someone has to fix the repository;
    guessing another base would hand the worker the wrong history."""


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
# A lista cobre todo o mecanismo de configuração do CPython descrito em
# `python3 --help`/`man 1 python3` (variáveis PYTHON* que mudam sys.path,
# comportamento de venv ou modo seguro) mais VIRTUAL_ENV/__PYVENV_LAUNCHER__,
# que apontam para o virtualenv do supervisor.
_INTERPRETER_ENV = (
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "PYTHONNOUSERSITE",
    "PYTHONPLATLIBDIR",
    "PYTHONSAFEPATH",
    "VIRTUAL_ENV",
    "__PYVENV_LAUNCHER__",
)

# Variáveis que um hook de worktree vinculado (``git worktree add``) exporta
# para apontar para o ADMINISTRATIVO daquele worktree — ``GIT_DIR`` absoluto
# incluído. Um filho git do supervisor que herdasse isso operaria no
# repositório errado; foi assim que a demo de 11/09 corrompeu o repositório
# real (``core.bare=true``, branch movida). Mantida como documentação do
# incidente e usada pelos testes: o filtro abaixo é por PREFIXO, não por lista.
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
# Variáveis que fazem o git (ou o gh) EXECUTAR um programa ou abrir um editor,
# e que não começam com ``GIT_``. Um filho não interativo não precisa de
# nenhuma delas (PIP-905, revisão adversarial: ``GIT_EXTERNAL_DIFF`` herdado
# falsificou o diff mandado ao revisor).
_PROGRAM_ENV = ("EDITOR", "VISUAL", "PAGER", "SSH_ASKPASS")
# Forçado em todo filho: nenhum deles tem terminal para responder um prompt.
_FORCED_ENV = {"GIT_TERMINAL_PROMPT": "0"}


def child_env() -> dict[str, str]:
    """Environment for every child of the supervisor (git, gh, checks, worker,
    reviewer, responder): the caller's, minus **every** variable whose name
    starts with ``GIT_``, minus the interpreter leaks (``_INTERPRETER_ENV``)
    and the program/editor ones (``_PROGRAM_ENV``), plus
    ``GIT_TERMINAL_PROMPT=0``.

    A prefix, not a list: three adversarial reviews of name lists showed the
    same failure each time. The list missed ``GIT_CONFIG_GLOBAL``,
    ``GIT_CONFIG_SYSTEM``, ``GIT_EXTERNAL_DIFF``, ``GIT_SSH_COMMAND`` and
    ``GIT_PROTOCOL_FROM_USER`` — measured: a ``core.fsmonitor`` injected
    through ``GIT_CONFIG_GLOBAL`` ran a program during a mission, and an
    inherited ``GIT_EXTERNAL_DIFF`` falsified the diff sent to the reviewer,
    both invisible to ``git_config_snapshot`` (which only reads ``--local``).
    The supervisor never needs an inherited ``GIT_*``: it passes what it needs
    explicitly (``-c user.name``, ``-c core.hooksPath``, ``--git-dir`` via
    ``cwd``). ``gh`` authenticates through ``GH_*``/``GITHUB_*``, which are
    kept, and ``SSH_AUTH_SOCK`` (no ``GIT_`` prefix) still reaches a push
    over ssh."""

    excluded = frozenset(_INTERPRETER_ENV) | frozenset(_PROGRAM_ENV)
    kept = {
        key: value for key, value in os.environ.items()
        if key not in excluded and not key.startswith("GIT_")
    }
    kept.update(_FORCED_ENV)
    return kept


def gh_env() -> dict[str, str]:
    """Environment for every ``gh`` the supervisor runs: ``child_env()`` with
    ``core.hooksPath`` forced to ``/dev/null`` via the ``GIT_CONFIG_*``
    mechanism. ``gh`` shells out to ``git`` internally for several
    subcommands (``pr create`` pushes, ``pr checks`` reads refs); without
    this, that inner git would run repository hooks with the supervisor's
    credentials the same way a bare ``git`` child would (see
    ``NO_HOOKS_PATH``). ``child_env()`` already stripped any inherited
    ``GIT_CONFIG_*``, so only this forced override remains."""

    env = child_env()
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "core.hooksPath"
    env["GIT_CONFIG_VALUE_0"] = NO_HOOKS_PATH
    return env


# ``core.hooksPath`` for every git the supervisor runs against a mission
# repository/worktree (worktree prune/add, commit, push). It defaults to (or is
# configured as) a path inside the repository, resolved from whatever tree git
# runs in: a mission worktree would then execute hook scripts the worker may
# have written — with the supervisor's credentials and, in a linked worktree,
# an absolute ``GIT_DIR``. ``/dev/null`` is not a directory, so git finds no
# hook at all (pre-commit, commit-msg, post-commit, post-checkout,
# reference-transaction, pre-push...), and nobody can populate it. Diff
# verification and CI are the real gate; a local hook never runs.
NO_HOOKS_PATH = "/dev/null"


def _no_hooks_args() -> list[str]:
    return ["-c", f"core.hooksPath={NO_HOOKS_PATH}"]


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


def native_worktree_name(mission: Mapping[str, Any]) -> str:
    """The value passed to ``claude --worktree <name>``: the mission id
    itself — stable, unique, and safe both as a directory and as a branch."""

    return mission["missionId"]


def native_worktree_path(mission: Mapping[str, Any]) -> Path:
    """Where the CLI actually puts the worktree it creates — MEASURED, twice,
    against the real binary on 12 and 13/09:

        directory  <repo>/.claude/worktrees/<name>
        branch     worktree-<name>
        state      locked

    The first PIP-915 delivery looked for a *directory* named
    ``worktree-<name>``; that prefix belongs to the BRANCH. Adoption therefore
    never found anything in production, and the fake reproduced the same wrong
    premise, so 386 tests were green against a fiction.

    The mission works HERE and stays here. Moving it out was what forfeited
    containment from cycle 2 on: the CLI reuses a worktree by name/path (also
    measured — invoking it again with the same ``--worktree`` returns the same
    worktree, with the previous cycle's files, even after the branch was
    renamed). Move it and the next cycle either gets a fresh empty worktree or
    runs with no wall at all."""

    return Path(mission["workspace"]["repo"]) / ".claude" / "worktrees" / native_worktree_name(mission)


def prepare_native_worktree(mission: Mapping[str, Any]) -> Path:
    """Put the worktree where ``claude --worktree`` will look for it, on the
    mission's ``baseRef`` — before the first worker run (PIP-918).

    Left to itself the CLI creates the worktree off the checkout's current
    HEAD and ignores any base: a program wave chained from the previous wave's
    branch got ``main`` instead, every commit merged since then looked like a
    write outside the write set, and the wave blocked on ``no_progress`` with
    the worker unable to "revert" history it never wrote. Measured on 13/09
    against the real binary, in a throwaway repository with ``HEAD`` ≠ base:

        CLI alone              HEAD = main (base ignored)
        pre-created here       HEAD = base — the CLI reuses it by name/path
        write to the checkout  refused in BOTH ("This session is isolated in
                               the worktree …")

    So pre-creating costs none of the protection the native worktree really
    gives. What that protection is NOT, measured the same day: it refuses
    writes to the repository's shared checkout only — the home directory and
    sibling folders stay writable. Nothing here claims otherwise.

    Idempotent: an existing path is left to ``ensure_worktree``. When the path
    is gone but a branch survived (worktree pruned between cycles), the
    worktree is re-attached to that branch so earlier cycles' commits are not
    thrown away — the mission branch first, then the CLI's ``worktree-<name>``.
    ``--no-track`` keeps a remote base (``origin/main``) from writing tracking
    keys into the repository's shared config.
    """

    repo = mission["workspace"]["repo"]
    path = native_worktree_path(mission)
    if path.exists():
        return path
    name = native_worktree_name(mission)
    path.parent.mkdir(parents=True, exist_ok=True)
    for existing in (branch_name(mission), f"worktree-{name}"):
        if _commit_of(repo, f"refs/heads/{existing}") is not None:
            _git(repo, *_no_hooks_args(), "worktree", "add", "--lock", str(path), existing)
            return path
    base = _resolve_base(repo, mission["workspace"]["baseRef"])
    _git(repo, *_no_hooks_args(), "worktree", "add", "--lock", "--no-track",
         "-b", f"worktree-{name}", str(path), base)
    return path


def _resolve_base(repo: str | Path, base_ref: str) -> str:
    """The commit ``base_ref`` names, exactly as written.

    No fallback to ``origin/<base_ref>`` here on purpose: verification diffs
    against the literal ``baseRef`` too, so a worktree created from a guessed
    ref would only move the failure one step later. Resolving a locally
    deleted branch from the remote belongs to PIP-917, across every place the
    base is used."""

    commit = _commit_of(repo, base_ref)
    if commit is None:
        raise WorktreeBaseMissing(f"baseRef {base_ref!r} resolves to no commit in {repo}")
    return commit


def _commit_of(repo: str | Path, ref: str) -> str | None:
    completed = subprocess.run(
        ["git", *_no_hooks_args(), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=str(repo), capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, check=False, env=child_env(),
    )
    commit = completed.stdout.strip()
    return commit if completed.returncode == 0 and commit else None


def worktree_ready(mission: Mapping[str, Any], *, home: str | Path | None = None) -> Path | None:
    """The canonical path, if it already holds this mission's adopted
    worktree (on its own branch) — ``None`` otherwise. Never creates or
    adopts anything; a pure check the supervisor uses to decide whether a
    worker run needs ``--worktree`` (nothing adopted yet) or can run directly
    inside the existing worktree."""

    del home  # o caminho vem do repositório, não do home da missão
    repo = mission["workspace"]["repo"]
    path = native_worktree_path(mission)
    branch = branch_name(mission)
    if path.is_dir() and _is_mission_worktree(path, repo, branch):
        return path
    return None


def ensure_worktree(mission: Mapping[str, Any], *, home: str | Path | None = None) -> Path:
    """Return the mission's worktree — the one the worker's own
    ``claude --worktree`` created — putting its branch on the mission's name.

    No ``git worktree move``, and no creation here (``prepare_native_worktree``
    does that, before dispatch, on the ``baseRef``). The path is
    deterministic (``native_worktree_path``), so there is nothing to search
    for and nothing to relocate: the worktree stays exactly where the CLI put
    it, which is what lets every later cycle ask for it again by name and get
    the same contained worktree back.

    Raises ``WorktreeNotReady`` when the worker has not created it yet — the
    caller's job is ``prepare_native_worktree`` and a worker dispatched with
    ``--worktree``. The flag is what matters: a worktree the worker merely runs
    inside, without it, is no wall at all.
    """

    del home  # o caminho vem do repositório
    repo = mission["workspace"]["repo"]
    path = native_worktree_path(mission)
    branch = branch_name(mission)
    if not path.is_dir():
        raise WorktreeNotReady(
            f"no native worktree yet for {mission['missionId']}: dispatch a worker "
            "with --worktree first"
        )
    if not _is_worktree_of(path, repo):
        # Alguma coisa ocupa o caminho e não é um worktree DESTE repositório
        # (diretório solto, worktree de outro repo). Seguir daqui comitaria e
        # empurraria histórico alheio — a mesma guarda que a versão anterior
        # tinha, preservada agora que o caminho é fixo.
        raise RuntimeError(
            f"{path} exists and is not a worktree of {repo}"
        )
    atual = current_branch(path)
    if atual == f"worktree-{native_worktree_name(mission)}":
        # Renomear é seguro: medido em 13/09 que o CLI reaproveita por
        # nome/caminho e continua devolvendo o mesmo worktree depois disto.
        _git(path, *_no_hooks_args(), "branch", "-m", branch)
    elif atual != branch:
        # Um worker que trocou de branch no meio da sessão sai da linha por
        # conta própria; adotar não pode carimbar de mission branch o que ele
        # escolheu. ``_on_mission_branch`` precisa continuar vendo o desvio.
        return path
    return path


def remove_worktree(mission: Mapping[str, Any], *, home: str | Path | None = None) -> None:
    """Retire the mission's worktree and its local branch.

    Handles the same lock a native ``claude --worktree`` worktree carries:
    ``git worktree remove --force`` alone fails on a locked working tree
    ("cannot remove a locked working tree; use 'remove -f -f' to override or
    unlock it first", measured) — this unlocks first. Removing a worktree
    never deletes its branch (it would be left "solta", dangling, with no
    working tree pointing at it), so this also deletes the local branch.
    Every step is tolerant of already being gone: safe to call more than
    once, and safe when nothing was ever adopted."""

    del home  # o caminho vem do repositório
    repo = mission["workspace"]["repo"]
    branch = branch_name(mission)
    path = native_worktree_path(mission)
    _git(repo, *_no_hooks_args(), "worktree", "unlock", str(path), check=False)
    _git(repo, *_no_hooks_args(), "worktree", "remove", "--force", str(path), check=False)
    _git(repo, *_no_hooks_args(), "worktree", "prune", check=False)
    shutil.rmtree(path, ignore_errors=True)
    _git(repo, *_no_hooks_args(), "branch", "-D", branch, check=False)


def cleanup_stop_gate_residue(worktree: str | Path) -> None:
    """Remove the Stop hook accelerator's own files (PIP-916, wiring PIP-913's
    ``stop_gate`` module) from ``worktree`` right after a worker run, before
    anything computes a diff or stages a commit.

    Neither ``<worktree>/.claude/settings.json`` nor its reinforcement
    counter (``stop_gate.state_path``) is ever part of a mission's write
    set, and ``commit_if_needed`` below stages with ``git add -A`` — left in
    place, both would reach ``changed_files`` as an out-of-write-set diff and,
    on a ``pull_request`` delivery, the PR itself. Only a settings file that
    is structurally this gate's own is removed
    (``stop_gate._looks_like_our_gate``): a project's real
    ``.claude/settings.json`` — the one ``build_stop_gate_settings`` itself
    refuses to overwrite — is left untouched either way.
    """

    root = Path(worktree)
    settings_file = _stop_gate.settings_path(root)
    if settings_file.exists():
        try:
            parsed = json.loads(settings_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            parsed = None
        if _stop_gate._looks_like_our_gate(parsed):
            try:
                settings_file.unlink()
            except OSError:
                pass
    state_file = _stop_gate.state_path(root)
    try:
        if state_file.exists():
            state_file.unlink()
    except OSError:
        pass
    gate_dir = root / _stop_gate.STOP_GATE_DIR_NAME
    try:
        if gate_dir.is_dir() and not any(gate_dir.iterdir()):
            gate_dir.rmdir()
    except OSError:
        pass


def _list_worktrees(repo: str | Path) -> list[dict[str, Any]]:
    """Parsed ``git worktree list --porcelain`` blocks: each a dict with
    ``worktree`` (absolute path, as git prints it), ``branch`` (ref or
    ``None`` when detached/bare) and ``locked`` (bool)."""

    output = _git(repo, "worktree", "list", "--porcelain")
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in output.splitlines():
        if not line.strip():
            if current:
                entries.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"worktree": line[len("worktree "):], "branch": None, "locked": False}
        elif line.startswith("branch "):
            current["branch"] = line[len("branch "):]
        elif line == "locked" or line.startswith("locked "):
            current["locked"] = True
    if current:
        entries.append(current)
    return entries


def _unlock_if_locked(repo: str | Path, path: Path) -> None:
    for entry in _list_worktrees(repo):
        if Path(entry["worktree"]) == path and entry["locked"]:
            _git(repo, *_no_hooks_args(), "worktree", "unlock", str(path))
            return


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


def _is_worktree_of(path: Path, repo: str | Path) -> bool:
    """``path`` é um worktree ligado a ``repo``?"""

    try:
        toplevel = _git(path, *_no_hooks_args(), "rev-parse", "--show-toplevel").strip()
        common = _git(path, *_no_hooks_args(), "rev-parse", "--git-common-dir").strip()
    except Exception:
        return False
    if Path(toplevel).resolve() != Path(path).resolve():
        return False
    common_path = Path(common)
    if not common_path.is_absolute():
        common_path = Path(path) / common_path
    return common_path.resolve() == (Path(repo).resolve() / ".git")


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


def _git(cwd: str | Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=GIT_TIMEOUT_SECONDS, check=False, env=child_env(),
    )
    if check and completed.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed with exit code {completed.returncode}")
    return completed.stdout


def _gh(gh_bin: str, args: Sequence[str], *, cwd: str | Path, ok_codes: tuple[int, ...] = (0,)) -> str:
    with open(os.devnull, "rb") as devnull:
        completed = subprocess.run(
            [gh_bin, *args],
            cwd=str(cwd), stdin=devnull, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=GH_TIMEOUT_SECONDS, check=False, env=gh_env(),
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
