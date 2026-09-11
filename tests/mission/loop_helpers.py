"""Fixtures for the Mission Loop B tests: fake binaries, scenario files, git repos."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from tests.mission.helpers import mission_input

FAKES = Path(__file__).resolve().parent / "fakes"
FAKE_CLAUDE = FAKES / "fake_claude.py"
FAKE_GH = FAKES / "fake_gh.py"
WORKER_SENTINEL = "SENTINEL-worker-summary-text-that-must-never-be-persisted"


def cli_options(tokens: list[str]) -> dict[str, list[str]]:
    """``--option value...`` groups: a boolean option maps to ``[]``, a
    variadic one (``--disallowedTools a b``) to every value until the next
    ``--option``. ``tokens`` start at the first option (after ``-p <prompt>``)."""

    options: dict[str, list[str]] = {}
    current: str | None = None
    for token in tokens:
        if token.startswith("--"):
            current = token
            if current in options:
                raise AssertionError(f"option repeated: {current}")
            options[current] = []
        elif current is None:
            raise AssertionError(f"value before any option: {token[:40]}")
        else:
            options[current].append(token)
    return options


def single_values(tokens: list[str]) -> dict[str, str]:
    """``cli_options`` reduced to the one-value options."""

    return {key: values[0] for key, values in cli_options(tokens).items() if len(values) == 1}


# The deny-list the worker and the reviewer must carry (review A2/A3). Written
# out here, not imported, so removing an entry from the code fails a test.
EXPECTED_DISALLOWED_TOOLS = [
    "Bash(gh *)", "Bash(railway *)", "Bash(git push*)", "Bash(git config*)",
    "Bash(git remote*)", "Bash(git -c *)", "Bash(git -C *)", "Bash(git checkout*)",
    "Bash(git switch*)", "Bash(git reset*)", "Bash(git worktree*)", "Bash(git commit*)",
    "Bash(git add*)", "Bash(git rebase*)", "Bash(git merge*)", "Bash(curl *)",
    "Bash(wget *)", "WebFetch", "WebSearch",
]

# The responder additionally denies `Read` of the machine's and the
# project's own secrets by path (PIP-906 v2 review, achado 5): its
# `instructions` reach the next worker's brief without going through review.
EXPECTED_RESPONDER_DISALLOWED_TOOLS = EXPECTED_DISALLOWED_TOOLS + [
    "Read(~/.ssh/**)", "Read(~/.claude/**)", "Read(**/.env)", "Read(**/.env.*)",
]


def read_pid(path: Path, *, timeout: float = 10.0) -> int:
    """Wait for a pid file written by a fake and return the pid."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            return int(path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            time.sleep(0.02)
    raise AssertionError(f"no pid written to {path.name}")


def process_gone(pid: int, *, timeout: float = 5.0) -> bool:
    """True once ``pid`` no longer exists (reaped), waiting up to ``timeout``."""

    deadline = time.monotonic() + timeout
    while True:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            pass
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)


def kill_quietly(pid: int | None) -> None:
    if not pid:
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid", *args],
        cwd=cwd, capture_output=True, text=True, check=True,
    )
    return completed.stdout


def make_repo(root: Path, *, with_origin: bool = False) -> Path:
    """A small repository with README.md and docs/, on branch ``main``."""

    repo = root / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "README.md").write_text("# Demo\n\nidea and adopt remain follow-up\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("guide\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "initial")
    if with_origin:
        origin = root / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
        git(repo, "remote", "add", "origin", str(origin))
        git(repo, "push", "-q", "-u", "origin", "main")
    return repo


def loop_mission(repo: Path, **overrides: Any) -> dict[str, Any]:
    """The test mission: a check, an artifact, and a rubric over ``repo``."""

    document = mission_input()
    document["successCriteria"] = [
        {
            "id": "C1",
            "text": "README nao diz que idea/adopt sao follow-up",
            "kind": "check",
            "command": "! grep -q 'remain follow-up' README.md",
        },
        {
            "id": "C2",
            "text": "guia cita o CLI",
            "kind": "artifact",
            "path": "docs/guide.md",
            "mustMatch": "pipe (idea|adopt)",
        },
        {
            "id": "C3",
            "text": "texto novo afirma so o que o codigo mostra",
            "kind": "rubric",
            "question": "O texto novo afirma apenas o que o codigo mostra?",
        },
    ]
    document["workspace"] = {
        "repo": str(repo),
        "baseRef": "main",
        "writeSet": ["README.md", "docs/guide.md"],
    }
    document["delivery"] = {"kind": "none", "requireChecks": False}
    document["linearTicketIds"] = ["PIP-902"]
    document.update(overrides)
    return document


def remote_workspace(repo: Path, *, write_set: tuple[str, ...] = ("README.md", "docs/guide.md")) -> dict[str, Any]:
    """A ``workspace`` override whose ``baseRef`` is a remote-tracking ref
    (``origin/main``), the case ``git worktree add -b`` would otherwise wire
    up tracking for in the repository's shared config."""

    return {"repo": str(repo), "baseRef": "origin/main", "writeSet": list(write_set)}


def good_worker_output(**overrides: Any) -> dict[str, Any]:
    output = {
        "done": True,
        "summary": WORKER_SENTINEL,
        "filesChanged": ["README.md", "docs/guide.md"],
        "criteriaSelfAssessment": [
            {"id": "C1", "met": True, "note": "grep vazio"},
            {"id": "C2", "met": True, "note": "guia atualizado"},
            {"id": "C3", "met": True, "note": "so o que o codigo mostra"},
        ],
        "blockers": [],
    }
    output.update(overrides)
    return output


GOOD_FILES = {
    "README.md": "# Demo\n\nidea and adopt exist as pipe idea / pipe adopt\n",
    "docs/guide.md": "guide: run pipe idea or pipe adopt\n",
}


def satisfied_verdict(**overrides: Any) -> dict[str, Any]:
    verdict = {
        "verdict": "satisfied",
        "criteria": [
            {"id": "C1", "met": True, "evidence": "grep returns nothing"},
            {"id": "C2", "met": True, "evidence": "guide mentions pipe idea"},
            {"id": "C3", "met": True, "evidence": "claims match cli.py"},
        ],
        "reasons": ["diff stays inside the write set"],
    }
    verdict.update(overrides)
    return verdict


class FakeBinaries:
    """Scenario + log files for ``fake_claude.py`` and ``fake_gh.py`` in a temp dir."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.dir = root / "fakes"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.scenario_path = self.dir / "scenario.json"
        self.claude_log = self.dir / "claude.log"
        self.gh_state = self.dir / "gh"
        self.gh_state.mkdir(exist_ok=True)
        self.gh_log = self.gh_state / "gh.log"
        self._previous_env: dict[str, str | None] = {}

    def scenario(
        self,
        *,
        worker: list[dict] | None = None,
        reviewer: list[dict] | None = None,
        responder: list[dict] | None = None,
    ) -> None:
        self.scenario_path.write_text(
            json.dumps({"worker": worker or [], "reviewer": reviewer or [], "responder": responder or []}),
            encoding="utf-8",
        )
        for counter in self.dir.glob("*.count"):
            counter.unlink()

    def gh_checks(self, sequence: list[list[str]]) -> None:
        """Per ``pr checks`` call, the list of check buckets to report (in order)."""

        (self.gh_state / "checks.json").write_text(json.dumps(sequence), encoding="utf-8")

    def env(self) -> dict[str, str]:
        return {
            "FAKE_CLAUDE_SCENARIO": str(self.scenario_path),
            "FAKE_CLAUDE_STATE_DIR": str(self.dir),
            "FAKE_CLAUDE_LOG": str(self.claude_log),
            "FAKE_GH_STATE_DIR": str(self.gh_state),
        }

    def __enter__(self) -> "FakeBinaries":
        for key, value in self.env().items():
            self._previous_env[key] = os.environ.get(key)
            os.environ[key] = value
        return self

    def __exit__(self, *_args: object) -> None:
        for key, previous in self._previous_env.items():
            if previous is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous

    @property
    def claude_bin(self) -> str:
        return str(FAKE_CLAUDE)

    @property
    def gh_bin(self) -> str:
        return str(FAKE_GH)

    def claude_calls(self) -> list[dict[str, Any]]:
        if not self.claude_log.exists():
            return []
        return [json.loads(line) for line in self.claude_log.read_text(encoding="utf-8").splitlines()]

    def gh_calls(self) -> list[list[str]]:
        if not self.gh_log.exists():
            return []
        return [json.loads(line) for line in self.gh_log.read_text(encoding="utf-8").splitlines()]
