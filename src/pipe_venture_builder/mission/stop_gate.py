"""Mission contract → Stop hook (PIP-913).

Today ``verify.verify_criteria`` runs *after* the worker returns: a failing
``check`` costs a whole supervisor cycle (dispatch, wait, review, redispatch)
to tell the worker something a shell command already knew. Claude Code's
native ``Stop`` hook (exit code 2 blocks the turn from ending and feeds the
worker its stderr) already does the "keep going" part; this module is the
compiler from a mission's ``check`` criteria to that hook's settings file.

This is acceleration only, never a verdict:

- Only ``check`` criteria compile to the hook. ``rubric`` is the reviewer's
  judgment and ``artifact`` is ``verify_criteria``'s deterministic check
  after the run — neither belongs in a pre-stop gate the worker itself
  triggers, and neither's text is embedded here.
- ``verify.verify_criteria`` still runs after the worker returns and is
  still the only source of criterion evidence. A hook that "passed" (let
  the worker stop) is not evidence of anything: the worker could have
  stopped because every check genuinely passed, or because
  ``MAX_REINFORCEMENTS`` was reached with a check still failing, or
  because the hook itself failed to run. ``verify_criteria`` cannot tell
  those apart from the outside, and does not try to — it just reruns the
  same commands and records what actually happened.
- The generated ``.claude/settings.json`` carries *only* ``hooks.Stop``.
  No ``permissions``, ``mcpServers``, ``env`` or ``apiKeyHelper`` — the
  worker's isolation (``--setting-sources project``, the allow/deny lists
  in ``worker.py``) is not widened by this file; it only adds a Stop hook
  to what ``--setting-sources project`` already loads from the worktree.

The hook script is fully self-contained (inlined into the settings file,
not a separate script the worktree could lose track of) for two reasons:
so a reviewer can read the exact commands a Stop hook will run straight
out of ``.claude/settings.json``, and so there is nothing extra for the
worker's own file edits to disturb. It never imports this package — the
hook's own execution environment is not guaranteed to have it on
``PYTHONPATH`` (the same caveat ``check`` commands already have inside a
mission worktree, see ``docs/mission/README.md``) — and it never catches
exceptions on purpose. Claude Code only blocks a Stop on exit code 2;
every other exit code (a Python interpreter that isn't on PATH, an
unhandled exception, a check whose ``cwd`` doesn't exist) is already a
non-blocking failure as far as the harness is concerned. The one
deliberate path to ``exit(2)`` is: at least one check still fails, the
reinforcement count is below ``MAX_REINFORCEMENTS``, and the incremented
count was written successfully. Anything else — including the hook
failing to run at all — lets the worker's turn end.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from string import Template
from typing import Any, Mapping

# How many times the hook may force the worker to keep going (exit 2)
# before it lets the turn end regardless of outcome. A check that is
# genuinely stuck (flaky, or not fixable within this turn) must not hang
# the worker forever — ``verify_criteria`` after the run is still the gate
# that actually decides the cycle, exactly as before this hook existed.
class StopGateWouldClobberError(RuntimeError):
    """Levantada quando gerar o gate apagaria um settings que nao e nosso."""


MAX_REINFORCEMENTS = 3

# Per-check timeout inside the hook: short, because this runs inside the
# worker's own turn (not the supervisor's post-run window, which allows
# ``verify.DEFAULT_CHECK_TIMEOUT_SECONDS`` == 600s). A check that is this
# slow is better left to that post-run verification anyway.
HOOK_CHECK_TIMEOUT_SECONDS = 120.0

STOP_GATE_DIR_NAME = ".claude"
SETTINGS_FILENAME = "settings.json"
STATE_FILENAME = "stop-gate-reinforcements"

_HEREDOC_DELIMITER = "PIPE_STOP_GATE_HOOK_EOF"

_HOOK_SCRIPT_TEMPLATE = Template(
    '''\
import subprocess, sys

CHECKS = $checks
STATE = $state
MAX_REINFORCEMENTS = $max_reinforcements
TIMEOUT = $timeout

failed = []
for check_id, command, cwd in CHECKS:
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=TIMEOUT,
        )
        ok = result.returncode == 0
    except subprocess.TimeoutExpired:
        # Estourar o relogio do acelerador NAO e reprovar. A verificacao que
        # decide o ciclo da 600s; aqui sao 120s, porque isto roda dentro do
        # turno do worker. Um check que leva entre os dois passa la e seria
        # reportado aqui como falhando — o worker gastaria reforcos consertando
        # o que nao esta quebrado. "Nao sei" deixa encerrar.
        ok = True
    except Exception:
        # Qualquer outra falha do proprio acelerador tambem deixa passar: quem
        # reprova e `verify_criteria`, depois.
        ok = True
    if not ok:
        failed.append(check_id)

if not failed:
    sys.exit(0)

count = 0
try:
    count = int(open(STATE, encoding="utf-8").read().strip())
except Exception:
    count = 0

if count >= MAX_REINFORCEMENTS:
    sys.exit(0)

with open(STATE, "w", encoding="utf-8") as handle:
    handle.write(str(count + 1))

sys.stderr.write(
    "Criterios check ainda falhando: " + ", ".join(failed)
    + ". Corrija antes de encerrar o turno (reforco "
    + str(count + 1) + "/" + str(MAX_REINFORCEMENTS) + ")."
)
sys.exit(2)
'''
)


def settings_path(root: str | Path) -> Path:
    return Path(root) / STOP_GATE_DIR_NAME / SETTINGS_FILENAME


def state_path(root: str | Path) -> Path:
    return Path(root) / STOP_GATE_DIR_NAME / STATE_FILENAME


def _check_criteria(mission: Mapping[str, Any]) -> list[tuple[str, str, str]]:
    """``(id, command, cwd)`` for every ``check`` criterion, in mission order.

    ``rubric`` and ``artifact`` criteria never reach the hook: rubric is the
    reviewer's judgment, artifact is ``verify_criteria``'s job after the run.
    """

    checks: list[tuple[str, str, str]] = []
    for criterion in mission["successCriteria"]:
        if criterion["kind"] == "check":
            checks.append((criterion["id"], criterion["command"], criterion.get("cwd", ".")))
    return checks


def _hook_script(root: Path, checks: list[tuple[str, str, str]]) -> str:
    resolved = [(check_id, command, str(root / cwd)) for check_id, command, cwd in checks]
    return _HOOK_SCRIPT_TEMPLATE.substitute(
        checks=repr(resolved),
        state=repr(str(state_path(root))),
        max_reinforcements=repr(MAX_REINFORCEMENTS),
        timeout=repr(HOOK_CHECK_TIMEOUT_SECONDS),
    )


def _hook_command(script: str, python_bin: str) -> str:
    """A shell command run by Claude Code's Stop hook: feed ``script`` to
    ``python_bin`` over stdin via a quoted heredoc (no shell expansion of
    anything inside it) so the hook has no separate script file to lose."""

    return f"{python_bin} - <<'{_HEREDOC_DELIMITER}'\n{script}\n{_HEREDOC_DELIMITER}\n"


def _looks_like_our_gate(parsed: Any) -> bool:
    """Reconhece um settings escrito por este gate, pela FORMA.

    Não dá para carimbar uma chave própria no arquivo: o contrato diz que o
    settings gerado não carrega nada além de ``hooks``. Então a identidade é
    estrutural — só ``hooks``, só ``Stop``, e o comando com o delimitador do
    heredoc deste módulo. Regenerar o nosso é permitido (os critérios mudam
    entre missões e entre ciclos); qualquer outra coisa é do projeto e fica.
    """

    if not isinstance(parsed, dict) or set(parsed) != {"hooks"}:
        return False
    hooks = parsed["hooks"]
    if not isinstance(hooks, dict) or set(hooks) != {"Stop"}:
        return False
    try:
        command = hooks["Stop"][0]["hooks"][0]["command"]
    except (KeyError, IndexError, TypeError):
        return False
    return isinstance(command, str) and _HEREDOC_DELIMITER in command


def build_stop_gate_settings(
    mission: Mapping[str, Any], root: str | Path, *, python_bin: str | None = None
) -> Path:
    """Write ``<root>/.claude/settings.json`` with a Stop hook that reruns
    the mission's ``check`` criteria before the worker's turn can end, and
    return its path.

    ``python_bin`` defaults to the interpreter running this process
    (``sys.executable``) — the same one the supervisor and its checks
    already use. A caller may pass a different (even nonexistent) path,
    which is how ``tests/mission/test_stop_gate.py`` proves the hook fails
    open when its own interpreter is missing, without touching machine
    state.
    """

    root_path = Path(root)
    gate_dir = root_path / STOP_GATE_DIR_NAME
    gate_dir.mkdir(parents=True, exist_ok=True)

    state_file = state_path(root_path)
    try:
        if state_file.exists():
            state_file.unlink()
    except OSError:
        # Estado sujo de worktree (o caminho virou diretorio, permissao). Tudo
        # no caminho do hook falha ABERTO; o compilador nao pode ser a unica
        # peca que falha fechado e derruba quem chamou.
        pass

    checks = _check_criteria(mission)
    script = _hook_script(root_path, checks)
    command = _hook_command(script, python_bin or sys.executable)

    settings = {
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {"type": "command", "command": command},
                    ]
                }
            ]
        }
    }
    path = settings_path(root_path)
    if path.exists():
        # Um `.claude/settings.json` versionado pelo projeto pode carregar
        # `permissions.deny` ou um `PreToolUse` — restricoes do worker.
        # Sobrescrever aqui ALARGARIA o worker, que e exatamente o que este
        # modulo promete nunca fazer. Preservar e recusar o gate e a direcao
        # segura: sem acelerador o ciclo funciona como antes; sem a deny-list,
        # nao.
        existing = path.read_text(encoding="utf-8")
        try:
            parsed = json.loads(existing)
        except json.JSONDecodeError:
            parsed = None
        if not _looks_like_our_gate(parsed):
            raise StopGateWouldClobberError(
                f"{path} ja existe e nao foi escrito por este gate; "
                "preservado para nao remover restricoes do worker"
            )
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
