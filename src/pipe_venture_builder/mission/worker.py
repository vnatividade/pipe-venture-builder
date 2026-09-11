"""Headless Claude Code worker: brief compilation, fixed flags, tolerant parsing.

One worker per cycle, fresh context (never ``--resume``), never ``--bare`` (it
would bypass the subscription login), stdin always ``/dev/null`` (otherwise the
CLI waits for stdin and warns). The environment is inherited from the
supervisor process on purpose: ``claude`` authenticates from the local login
and this machine's shell profile; the supervisor never adds a secret to it.

Nothing here writes to the store. Callers persist only ids, hashes, counts and
statuses from the returned result; the brief and the worker's text stay in
memory.
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    fingerprint,
    safe_identifier,
)


DEFAULT_MODEL = "sonnet"
MIN_RUN_BUDGET_USD = 1.5
DEFAULT_WORKER_TIMEOUT_SECONDS = 3600.0
DEFAULT_POLL_SECONDS = 5.0
DEFAULT_GRACE_SECONDS = 10.0
DENIED_COMMAND_PREVIEW_CHARS = 160
# The worker edits files and reads git; it never commits (the supervisor
# verifies and commits), so no ``Bash(git *)``: ``git config`` in a worktree
# writes the main checkout's config and ``git commit`` runs hooks.
BASE_ALLOWED_TOOLS = (
    "Read",
    "Edit",
    "Write",
    "Grep",
    "Glob",
    "Bash(git status*)",
    "Bash(git diff*)",
    "Bash(git log*)",
    "Bash(git show*)",
    "Bash(ls *)",
)
# Deny wins over allow, including allow rules that could still come from the
# project's settings. Passed as separate ``--disallowedTools`` arguments.
DISALLOWED_TOOLS = (
    "Bash(gh *)",
    "Bash(railway *)",
    "Bash(git push*)",
    "Bash(git config*)",
    "Bash(git remote*)",
    "Bash(git -c *)",
    "Bash(git -C *)",
    "Bash(git checkout*)",
    "Bash(git switch*)",
    "Bash(git reset*)",
    "Bash(git worktree*)",
    "Bash(git commit*)",
    "Bash(git add*)",
    "Bash(git rebase*)",
    "Bash(git merge*)",
    "Bash(curl *)",
    "Bash(wget *)",
    "WebFetch",
    "WebSearch",
)

WORKER_FIXED_RULES = (
    "Você executa UMA missão do Pipe dentro de um worktree isolado. "
    "Só altere arquivos do write set do brief; qualquer outro diff reprova o ciclo. "
    "Não use rede (nem gh, railway, curl); não leia .env, cofre, chaves ou credenciais; "
    "não altere configuração (inclusive git config), hooks ou permissões. "
    "Não faça commit, push, PR nem merge: o supervisor verifica e commita. "
    "Não invente evidência: se um critério não ficou verdadeiro, diga done=false e liste blockers. "
    "Termine respondendo SOMENTE com o JSON pedido no brief."
)

_WORKER_OUTPUT_DEFAULTS: dict[str, Any] = {
    "summary": "",
    "filesChanged": [],
    "criteriaSelfAssessment": [],
    "blockers": [],
}
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


@dataclass
class ClaudeResult:
    """What a ``claude -p`` invocation produced, reduced to what the store may keep."""

    status: str  # collected | failed | interrupted
    reason: str | None
    session_id: str | None
    cost_usd: float
    num_turns: int
    subtype: str | None
    permission_denials: int
    denied_tools: list[str]
    result_text: str | None
    structured_output: Any
    result_fingerprint: str | None
    returncode: int | None
    stdout_bytes: int
    model: str
    # In memory only (never persisted): "Tool" or "Bash(<command preview>)".
    denied_calls: list[str] = field(default_factory=list)


@dataclass
class WorkerResult(ClaudeResult):
    output: dict[str, Any] | None = None


@dataclass
class _Capture:
    chunks: list[str] = field(default_factory=list)

    def text(self) -> str:
        return "".join(self.chunks)


class ClaudeProcess:
    """A ``claude`` subprocess with cooperative stop and forced kill.

    ``terminate()`` may be called from any thread (a signal handler, a poller);
    ``wait`` reports ``interrupted`` when the process ended because of it.
    """

    def __init__(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path,
        env: Mapping[str, str] | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.command = list(command)
        self.cwd = str(cwd)
        self.env = dict(env) if env is not None else None
        self.model = model
        self._process: subprocess.Popen[str] | None = None
        self._stdout = _Capture()
        self._stderr = _Capture()
        self._readers: list[threading.Thread] = []
        self._stop_requested = threading.Event()
        self._lock = threading.Lock()

    @property
    def pid(self) -> int | None:
        return self._process.pid if self._process else None

    def start(self) -> None:
        with open(os.devnull, "rb") as devnull:
            self._process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                env=self.env,
                stdin=devnull,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                start_new_session=True,
            )
        for stream, capture in ((self._process.stdout, self._stdout), (self._process.stderr, self._stderr)):
            reader = threading.Thread(target=self._drain, args=(stream, capture), daemon=True)
            reader.start()
            self._readers.append(reader)

    @staticmethod
    def _drain(stream: Any, capture: _Capture) -> None:
        try:
            for chunk in iter(lambda: stream.read(65536), ""):
                capture.chunks.append(chunk)
        finally:
            stream.close()

    def terminate(self, *, grace_seconds: float = DEFAULT_GRACE_SECONDS) -> None:
        """SIGTERM the whole process group; SIGKILL after ``grace_seconds``.

        Once the leader (``claude``) is gone, the rest of its group always gets
        SIGKILL: a descendant that ignores SIGTERM does not outlive the stop.
        A descendant that left the group (``setsid``) is out of reach.
        """

        self._stop_requested.set()
        process = self._process
        if process is None:
            return
        with self._lock:
            if process.poll() is None:
                self._signal(process, signal.SIGTERM)
                try:
                    process.wait(timeout=grace_seconds)
                except subprocess.TimeoutExpired:
                    self._signal(process, signal.SIGKILL)
                    try:
                        process.wait(timeout=grace_seconds)
                    except subprocess.TimeoutExpired:
                        pass
            self._kill_group(process)

    @staticmethod
    def _kill_group(process: subprocess.Popen[str]) -> None:
        """SIGKILL what is left of the process group (the leader's pid is its id)."""

        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    @staticmethod
    def _signal(process: subprocess.Popen[str], signum: int) -> None:
        try:
            os.killpg(process.pid, signum)
        except (ProcessLookupError, PermissionError):
            try:
                process.send_signal(signum)
            except ProcessLookupError:
                pass

    def wait(
        self,
        *,
        timeout: float = DEFAULT_WORKER_TIMEOUT_SECONDS,
        poll_seconds: float = DEFAULT_POLL_SECONDS,
        should_stop: Callable[[], bool] | None = None,
        grace_seconds: float = DEFAULT_GRACE_SECONDS,
    ) -> ClaudeResult:
        process = self._process
        if process is None:
            raise RuntimeError("process was not started")
        deadline = time.monotonic() + timeout
        timed_out = False
        while True:
            try:
                process.wait(timeout=poll_seconds)
                break
            except subprocess.TimeoutExpired:
                pass
            if self._stop_requested.is_set():
                self.terminate(grace_seconds=grace_seconds)
                break
            if should_stop is not None and should_stop():
                self.terminate(grace_seconds=grace_seconds)
                break
            if time.monotonic() >= deadline:
                timed_out = True
                self._stop_requested.clear()
                self._kill_now(process, grace_seconds)
                break
        # The run is over however it ended: nothing it started keeps writing.
        self._kill_group(process)
        for reader in self._readers:
            reader.join(timeout=grace_seconds)
        stdout = self._stdout.text()
        interrupted = self._stop_requested.is_set() and not timed_out
        return build_result(
            stdout,
            returncode=process.returncode,
            interrupted=interrupted,
            timed_out=timed_out,
            model=self.model,
        )

    def _kill_now(self, process: subprocess.Popen[str], grace_seconds: float) -> None:
        with self._lock:
            self._signal(process, signal.SIGKILL)
            try:
                process.wait(timeout=grace_seconds)
            except subprocess.TimeoutExpired:
                pass


def build_result(
    stdout: str,
    *,
    returncode: int | None,
    interrupted: bool,
    timed_out: bool,
    model: str,
) -> ClaudeResult:
    payload = parse_result_json(stdout)
    session_id = _identifier_or_none(payload.get("session_id")) if payload else None
    cost = _number(payload.get("total_cost_usd")) if payload else 0.0
    turns = _count(payload.get("num_turns")) if payload else 0
    subtype = _identifier_or_none(payload.get("subtype")) if payload else None
    denials = payload.get("permission_denials") if payload else None
    denied_tools: list[str] = []
    denied_calls: list[str] = []
    if isinstance(denials, list):
        for item in denials:
            if isinstance(item, Mapping):
                tool = item.get("tool_name")
                if isinstance(tool, str):
                    denied_tools.append(tool)
                    denied_calls.append(_denied_call(tool, item.get("tool_input")))
    result_text = payload.get("result") if payload else None
    if not isinstance(result_text, str):
        result_text = None

    if interrupted:
        status, reason = "interrupted", "stop_requested"
    elif timed_out:
        status, reason = "failed", "timeout"
    elif payload is None:
        status, reason = "failed", "no_json"
    elif payload.get("is_error") or (subtype is not None and subtype != "success"):
        status, reason = "failed", subtype or "is_error"
    else:
        status, reason = "collected", None

    return ClaudeResult(
        status=status,
        reason=reason,
        session_id=session_id,
        cost_usd=cost,
        num_turns=turns,
        subtype=subtype,
        permission_denials=len(denials) if isinstance(denials, list) else 0,
        denied_tools=denied_tools,
        result_text=result_text,
        structured_output=payload.get("structured_output") if payload else None,
        result_fingerprint=fingerprint(result_text) if result_text else None,
        returncode=returncode,
        stdout_bytes=len(stdout.encode("utf-8", errors="replace")),
        model=model,
        denied_calls=denied_calls,
    )


def _denied_call(tool: str, tool_input: Any) -> str:
    """``Bash(<command>)`` for a denied shell call, else the tool name."""

    if tool == "Bash" and isinstance(tool_input, Mapping):
        command = tool_input.get("command")
        if isinstance(command, str) and command.strip():
            preview = " ".join(command.split())[:DENIED_COMMAND_PREVIEW_CHARS]
            return f"Bash({preview})"
    return tool


def run_claude(
    command: Sequence[str],
    *,
    cwd: str | Path,
    model: str = DEFAULT_MODEL,
    timeout: float = DEFAULT_WORKER_TIMEOUT_SECONDS,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    should_stop: Callable[[], bool] | None = None,
    grace_seconds: float = DEFAULT_GRACE_SECONDS,
    env: Mapping[str, str] | None = None,
    on_start: Callable[[ClaudeProcess], None] | None = None,
) -> ClaudeResult:
    process = ClaudeProcess(command, cwd=cwd, env=env, model=model)
    process.start()
    if on_start is not None:
        on_start(process)
    return process.wait(
        timeout=timeout,
        poll_seconds=poll_seconds,
        should_stop=should_stop,
        grace_seconds=grace_seconds,
    )


# -- brief and command ---------------------------------------------------------


def compile_brief(
    mission: Mapping[str, Any],
    cycle: int,
    revision_instructions: str | None,
) -> str:
    """Render the worker brief from the mission (template: worker-brief.template.md)."""

    lines = [
        "# Brief do worker (compilado pelo supervisor; nunca contém segredos)",
        "",
        "Você é o executor de UMA missão do Pipe. Trabalhe só neste diretório (worktree "
        "isolado). Leia `AGENTS.md` e `CLAUDE.md` do repositório antes de editar.",
        "",
        f"## Missão {mission['missionId']} v{mission['version']} — {mission['title']}",
        f"Intenção do fundador: {mission['intent']}",
        f"Problema: {mission['problem']}",
        f"Para quem: {mission['who']}",
        "",
        "## Critérios de sucesso (todos precisam ficar verdadeiros)",
    ]
    for criterion in mission["successCriteria"]:
        line = f"- {criterion['id']} ({criterion['kind']}): {criterion['text']}"
        if criterion["kind"] == "check":
            line += f" — verificação: `{criterion['command']}`"
            if criterion.get("cwd") and criterion["cwd"] != ".":
                line += f" (em `{criterion['cwd']}`)"
        elif criterion["kind"] == "artifact":
            line += f" — artefato: `{criterion['path']}`"
            if criterion.get("mustMatch"):
                line += f" deve casar `{criterion['mustMatch']}`"
        else:
            line += f" — pergunta do revisor: {criterion['question']}"
        lines.append(line)
    lines += ["", "## Não-objetivos (não faça)"]
    lines += [f"- {item}" for item in mission["nonGoals"]] or ["- (nenhum declarado)"]
    lines += [
        "",
        "## Write set (só estes arquivos podem mudar; qualquer outro diff reprova o ciclo)",
    ]
    lines += [f"- {item}" for item in mission["workspace"]["writeSet"]]
    lines += [
        "",
        "## Regras",
        "- Não use rede (nem `gh`, `railway`, `curl`); não leia `.env`, cofre ou "
        "credenciais; não altere config (inclusive `git config`), hooks ou permissões.",
        "- Edite os arquivos e deixe as mudanças no worktree: não faça commit nem push; o "
        "supervisor verifica e commita. Não abra PR (o supervisor abre). Não faça merge.",
        f"- Ferramentas permitidas: {allowed_tools(mission)}. Qualquer outra chamada é negada "
        "(inclusive comandos encadeados com `;`, `&&` ou `|`); o supervisor roda as "
        "verificações dos critérios depois de você.",
        '- Ao terminar, responda SOMENTE com JSON: {"done": true|false, "summary": "...", '
        '"filesChanged": [...], "criteriaSelfAssessment": [{"id": "...", "met": true|false, '
        '"note": "..."}], "blockers": ["..."]}.',
    ]
    if revision_instructions:
        lines += [
            "",
            f"## Revisão anterior pediu (ciclo {max(cycle - 1, 1)})",
            revision_instructions.strip(),
        ]
    return "\n".join(lines) + "\n"


def allowed_tools(mission: Mapping[str, Any]) -> str:
    tools = list(BASE_ALLOWED_TOOLS)
    for criterion in mission["successCriteria"]:
        if criterion["kind"] == "check":
            entry = f"Bash({criterion['command']})"
            if entry not in tools:
                tools.append(entry)
    return ",".join(tools)


def isolation_args() -> list[str]:
    """Flags that keep a headless ``claude`` away from this machine's user
    settings (allow rules such as ``gh pr merge *`` or ``railway up *``, hooks)
    and MCP servers, plus the deny-list. Measured with the real CLI 2.1.267:
    with them ``gh``/``railway``/``git push`` are denied and auth still works.
    ``--disallowedTools`` is variadic, so an option must follow its values."""

    return [
        "--setting-sources",
        "project",
        "--strict-mcp-config",
        "--disallowedTools",
        *DISALLOWED_TOOLS,
    ]


def worker_command(
    mission: Mapping[str, Any],
    brief: str,
    *,
    claude_bin: str,
    budget_left: float,
    model: str = DEFAULT_MODEL,
) -> list[str]:
    return [
        claude_bin,
        "-p",
        brief,
        "--output-format",
        "json",
        "--max-turns",
        str(mission["constraints"]["maxTurnsPerRun"]),
        "--max-budget-usd",
        f"{budget_left:.2f}",
        "--permission-mode",
        "acceptEdits",
        "--permission-prompts",
        "none",
        "--allowedTools",
        allowed_tools(mission),
        *isolation_args(),
        "--append-system-prompt",
        WORKER_FIXED_RULES,
        "--model",
        model,
    ]


def run_worker(
    mission: Mapping[str, Any],
    run_id: str,
    cwd: str | Path,
    claude_bin: str,
    budget_left: float,
    *,
    cycle: int = 1,
    revision_instructions: str | None = None,
    model: str = DEFAULT_MODEL,
    timeout: float = DEFAULT_WORKER_TIMEOUT_SECONDS,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    should_stop: Callable[[], bool] | None = None,
    grace_seconds: float = DEFAULT_GRACE_SECONDS,
    env: Mapping[str, str] | None = None,
    on_start: Callable[[ClaudeProcess], None] | None = None,
) -> WorkerResult:
    """Run one worker for ``run_id`` in ``cwd`` and reduce its output."""

    del run_id  # identity lives in the store; the worker never sees it
    brief = compile_brief(mission, cycle, revision_instructions)
    command = worker_command(
        mission, brief, claude_bin=claude_bin, budget_left=budget_left, model=model
    )
    result = run_claude(
        command,
        cwd=cwd,
        model=model,
        timeout=timeout,
        poll_seconds=poll_seconds,
        should_stop=should_stop,
        grace_seconds=grace_seconds,
        env=env,
        on_start=on_start,
    )
    output = extract_worker_output(result.result_text) if result.status == "collected" else None
    return WorkerResult(**result.__dict__, output=output)


# -- parsing -------------------------------------------------------------------


def parse_result_json(stdout: str | None) -> dict[str, Any] | None:
    """The final ``type: result`` object, tolerating noise lines around it."""

    if not stdout:
        return None
    candidates = [stdout.strip()]
    candidates += [line.strip() for line in reversed(stdout.splitlines()) if line.strip()]
    for candidate in candidates:
        if not candidate.startswith("{"):
            continue
        try:
            parsed = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(parsed, dict) and parsed.get("type") == "result":
            return parsed
    return None


def extract_worker_output(text: str | None) -> dict[str, Any] | None:
    """The worker's JSON (``done`` + fields), tolerating prose or fences around it."""

    if not text:
        return None
    for candidate in _json_candidates(text):
        if isinstance(candidate, dict) and isinstance(candidate.get("done"), bool):
            output = {"done": candidate["done"]}
            for key, default in _WORKER_OUTPUT_DEFAULTS.items():
                value = candidate.get(key, default)
                if isinstance(default, list):
                    output[key] = value if isinstance(value, list) else list(default)
                else:
                    output[key] = value if isinstance(value, str) else default
            return output
    return None


def _json_candidates(text: str) -> list[Any]:
    found: list[Any] = []
    sources = [text.strip()] + [match.strip() for match in _FENCE.findall(text)]
    decoder = json.JSONDecoder()
    for source in sources:
        try:
            found.append(json.loads(source))
            continue
        except ValueError:
            pass
        start = 0
        while True:
            index = source.find("{", start)
            if index < 0:
                break
            try:
                parsed, end = decoder.raw_decode(source, index)
            except ValueError:
                start = index + 1
                continue
            found.append(parsed)
            start = end
    return found


def _identifier_or_none(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return safe_identifier(value)
    except ControlPlaneContractError:
        return None


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    number = float(value)
    if number != number or number < 0 or number == float("inf"):
        return 0.0
    return number


def _count(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value
