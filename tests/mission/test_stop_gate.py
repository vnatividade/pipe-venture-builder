"""PIP-913: the mission contract compiles to a Claude Code Stop hook.

The hook is acceleration only — it lets a worker see a failing ``check``
inside its own turn instead of waiting a full supervisor cycle — never a
verdict. These tests prove: the generated settings carry nothing beyond the
``Stop`` hook (no widened isolation), only ``check`` criteria reach it, the
reinforcement cap eventually lets the worker's turn end even with a check
still failing, a failure of the hook machinery itself (missing interpreter,
an I/O error while it runs) also lets the turn end rather than hang it, and
none of that is treated as evidence — ``verify.verify_criteria`` still runs
after and still decides the criterion on its own.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import tempfile
import unittest
from unittest import TestCase

from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.verify import verify_criteria
from pipe_venture_builder.mission import stop_gate
from pipe_venture_builder.mission.stop_gate import (
    StopGateWouldClobberError,
    build_stop_gate_settings,
)
from pipe_venture_builder.mission.stop_gate import (
    MAX_REINFORCEMENTS,
    build_stop_gate_settings,
    settings_path,
    state_path,
)
from tests.mission.helpers import CREATED_AT, mission_variant


def _mission(criteria: list[dict]) -> dict:
    return build_mission(mission_variant(successCriteria=criteria), created_at=CREATED_AT)


def _checks(*commands_and_cwd: tuple[str, str, str | None]) -> list[dict]:
    criteria = []
    for index, (command, _text, cwd) in enumerate(commands_and_cwd, start=1):
        criterion = {
            "id": f"C{index}",
            "text": f"criterio {index}",
            "kind": "check",
            "command": command,
        }
        if cwd is not None:
            criterion["cwd"] = cwd
        criteria.append(criterion)
    return criteria


def _run_hook(path: Path) -> subprocess.CompletedProcess:
    settings = json.loads(path.read_text(encoding="utf-8"))
    command = settings["hooks"]["Stop"][0]["hooks"][0]["command"]
    return subprocess.run(
        ["sh", "-c", command],
        capture_output=True,
        text=True,
        timeout=30,
    )


class SettingsShapeTests(TestCase):
    """C2 / C4: the compiled settings widen nothing about the worker."""

    def test_max_reinforcements_is_a_small_bounded_cap(self) -> None:
        self.assertIsInstance(MAX_REINFORCEMENTS, int)
        self.assertTrue(1 <= MAX_REINFORCEMENTS <= 10)

    def test_settings_carry_only_the_stop_hook(self) -> None:
        mission = _mission(
            _checks(("true", "sobe", None))
            + [
                {
                    "id": "R1",
                    "text": "julgamento",
                    "kind": "rubric",
                    "question": "ficou bom mesmo?",
                }
            ]
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            self.assertEqual(path, settings_path(root))
            self.assertTrue(path.is_file())
            data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(set(data), {"hooks"})
        self.assertEqual(set(data["hooks"]), {"Stop"})
        for forbidden in ("apiKeyHelper", "permissions", "mcpServers", "env"):
            self.assertNotIn(forbidden, data)

    def test_only_check_criteria_reach_the_hook(self) -> None:
        mission = _mission(
            _checks(("true", "sobe", None), ("false", "cai", "."))
            + [
                {
                    "id": "R1",
                    "text": "julgamento",
                    "kind": "rubric",
                    "question": "ficou bom mesmo?",
                },
                {
                    "id": "A1",
                    "text": "artefato",
                    "kind": "artifact",
                    "path": "docs/x.md",
                },
            ]
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            text = path.read_text(encoding="utf-8")
        self.assertIn("true", text)
        self.assertIn("false", text)
        self.assertNotIn("ficou bom mesmo?", text)
        self.assertNotIn("docs/x.md", text)

    def test_worker_command_keeps_project_only_setting_sources(self) -> None:
        # C4: this module never touches worker.py's isolation flags; the
        # worktree it writes into is only ever loaded through
        # ``--setting-sources project``, already the worker's only source.
        from pipe_venture_builder.mission.worker import isolation_args

        self.assertEqual(isolation_args()[:2], ["--setting-sources", "project"])


class HookBehaviorTests(TestCase):
    """C3: a reinforcement cap, and the hook's own failure fails open."""

    def test_all_checks_passing_lets_the_turn_end(self) -> None:
        mission = _mission(_checks(("true", "sobe", None), ("true", "sobe2", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            result = _run_hook(path)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(state_path(root).exists())

    def test_no_check_criteria_lets_the_turn_end(self) -> None:
        mission = _mission(
            [
                {
                    "id": "R1",
                    "text": "julgamento",
                    "kind": "rubric",
                    "question": "ficou bom?",
                }
            ]
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            result = _run_hook(path)
        self.assertEqual(result.returncode, 0)

    def test_failing_check_blocks_up_to_the_cap_then_lets_the_turn_end(self) -> None:
        mission = _mission(_checks(("false", "cai", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            for attempt in range(1, MAX_REINFORCEMENTS + 1):
                result = _run_hook(path)
                self.assertEqual(
                    result.returncode, 2, f"attempt {attempt} should still block"
                )
                self.assertIn("C1", result.stderr)
                self.assertEqual(state_path(root).read_text(encoding="utf-8").strip(), str(attempt))
            # The cap is reached: the same still-failing check no longer blocks.
            result = _run_hook(path)
            self.assertEqual(result.returncode, 0, "past the cap the turn must be able to end")

    def test_rebuilding_settings_resets_the_reinforcement_count(self) -> None:
        mission = _mission(_checks(("false", "cai", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            for _ in range(MAX_REINFORCEMENTS):
                self.assertEqual(_run_hook(path).returncode, 2)
            self.assertEqual(_run_hook(path).returncode, 0, "cap reached")
            # A new cycle (the supervisor calls this again per run) starts fresh.
            build_stop_gate_settings(mission, root)
            self.assertFalse(state_path(root).exists())
            self.assertEqual(_run_hook(path).returncode, 2, "fresh cap after rebuild")

    def test_checks_run_in_their_declared_cwd(self) -> None:
        mission = _mission(_checks(("test -f marker.txt", "existe", "sub")))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sub").mkdir()
            (root / "sub" / "marker.txt").write_text("x", encoding="utf-8")
            path = build_stop_gate_settings(mission, root)
            result = _run_hook(path)
        self.assertEqual(result.returncode, 0)

    def test_missing_interpreter_lets_the_turn_end_instead_of_hanging(self) -> None:
        # "script ausente": the hook's own runtime is not on the machine.
        # Claude Code only blocks a Stop on exit code 2 — anything else
        # (here, the shell's "command not found") is already fail-open.
        mission = _mission(_checks(("false", "cai", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(
                mission, root, python_bin="/nonexistent/path/to/python3-does-not-exist"
            )
            result = _run_hook(path)
        self.assertNotEqual(result.returncode, 2)
        self.assertFalse(state_path(root).exists())

    def test_hook_execution_error_lets_the_turn_end_instead_of_hanging(self) -> None:
        # "erro de execucao": something inside the hook itself breaks (here,
        # its state file can't be written because the path is a directory).
        # The deliberate exit(2) branch is never reached, so the unhandled
        # exception's exit code (never 2) fails open the same as above.
        mission = _mission(_checks(("false", "cai", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            state_path(root).mkdir(parents=True)
            result = _run_hook(path)
        self.assertNotEqual(result.returncode, 2)
        self.assertNotEqual(result.returncode, 0, "a real internal error, not a clean pass")


class EvidenceSeparationTests(TestCase):
    """C5: the hook never becomes the evidence; verify_criteria still is."""

    def test_hook_module_never_imports_the_store_or_verification(self) -> None:
        # Only the module's own defined/imported names — not its prose
        # docstring, which talks *about* verify_criteria without depending
        # on it — so this fails if stop_gate ever starts calling into
        # verify.py or store.py directly instead of staying a pure compiler.
        names = vars(stop_gate)
        for forbidden in ("verify_criteria", "MissionStore", "criteria_evidence", "collect_run"):
            self.assertNotIn(forbidden, names)

    def test_a_hook_pass_past_the_cap_is_not_treated_as_criterion_evidence(self) -> None:
        mission = _mission(_checks(("false", "cai", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            for _ in range(MAX_REINFORCEMENTS):
                self.assertEqual(_run_hook(path).returncode, 2)
            # Cap reached: the hook now lets the worker's turn end even
            # though the check still genuinely fails.
            self.assertEqual(_run_hook(path).returncode, 0)
            # The deterministic post-run gate is unmoved by that: it reruns
            # the same command itself and reports the real outcome.
            results = verify_criteria(mission, root)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].satisfied)

    def test_a_hook_pass_because_the_interpreter_is_missing_is_not_evidence_either(self) -> None:
        mission = _mission(_checks(("false", "cai", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(
                mission, root, python_bin="/nonexistent/path/to/python3-does-not-exist"
            )
            self.assertNotEqual(_run_hook(path).returncode, 2, "the missing interpreter must not block")
            results = verify_criteria(mission, root)
        self.assertFalse(results[0].satisfied)

    def test_a_genuine_hook_pass_still_matches_verify_criteria(self) -> None:
        mission = _mission(_checks(("true", "sobe", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            self.assertEqual(_run_hook(path).returncode, 0)
            results = verify_criteria(mission, root)
        self.assertTrue(results[0].satisfied)


class DefaultInterpreterTests(TestCase):
    def test_default_python_bin_is_this_process(self) -> None:
        mission = _mission(_checks(("true", "sobe", None)))
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = build_stop_gate_settings(mission, root)
            settings = json.loads(path.read_text(encoding="utf-8"))
        command = settings["hooks"]["Stop"][0]["hooks"][0]["command"]
        self.assertIn(sys.executable, command)


class StopGateReviewTests(unittest.TestCase):
    """PIP-913, revisão adversarial: o que a suíte entregue não exercitava.

    Três dos achados foram provados por mutação — remover a guarda deixava os
    371 testes verdes. Estes testes existem para que isso não se repita.
    """

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="stopgate-review-"))

    def _mission(self, criteria):
        return {"missionId": "MSN-000000000000", "successCriteria": criteria}

    def _check(self, cid, command, **extra):
        body = {"id": cid, "kind": "check", "text": cid, "command": command}
        body.update(extra)
        return body

    def _hook_command(self, criteria) -> str:
        path = build_stop_gate_settings(self._mission(criteria), self.root)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data["hooks"]["Stop"][0]["hooks"][0]["command"]

    # -- injeção: a única linha que segura o envelope -------------------------

    def test_the_heredoc_delimiter_is_quoted(self) -> None:
        """Sem as aspas no delimitador, `$(...)` e crase do documento da missão
        rodam no shell do HOOK — antes de o Python existir, fora do `cwd` do
        critério e fora do timeout dele. Medido: com `<<EOF` o efeito colateral
        aparece no cwd do hook; com `<<'EOF'` fica contido no do critério."""

        comando = self._hook_command([self._check("C1", "true")])
        primeira = comando.splitlines()[0]
        self.assertRegex(
            primeira, r"<<'[A-Za-z0-9_]+'",
            f"delimitador do heredoc sem aspas — substituição do shell vaza: {primeira!r}",
        )

    def test_command_substitution_never_runs_in_the_hook_shell(self) -> None:
        """O `cwd` separa os dois casos.

        O comando do critério roda com `shell=True` no `cwd` DELE — então um
        `$(...)` ali executar é comportamento normal, pré-existente em
        `verify.run_check`. O que não pode acontecer é executar no shell do
        HOOK, que roda no diretório de trabalho do worker, antes de o Python
        existir e fora do timeout do critério. Com `<<EOF` sem aspas, o efeito
        aparece no cwd do hook; com `<<'EOF'`, no cwd do critério.
        """

        sub = self.root / "sub"
        sub.mkdir(parents=True, exist_ok=True)
        comando = self._hook_command(
            [self._check("C1", '$(printf x > marcador) true', cwd="sub")]
        )
        subprocess.run(comando, shell=True, capture_output=True, text=True,
                       input="{}", cwd=self.root, timeout=120)
        self.assertFalse(
            (self.root / "marcador").exists(),
            "a substituição do documento da missão executou no shell do hook",
        )
        self.assertTrue(
            (sub / "marcador").exists(),
            "o controle falhou: o comando do critério nem chegou a rodar",
        )

    # -- timeout: "não sei" não é "falhou" -----------------------------------

    def test_a_check_slower_than_the_hook_timeout_does_not_block_the_turn(self) -> None:
        """O acelerador dá 120s; a verificação que decide o ciclo dá 600s. Um
        check entre os dois passa lá. Reprovar aqui faria o worker gastar
        reforços consertando o que não está quebrado."""

        from pipe_venture_builder.mission.stop_gate import HOOK_CHECK_TIMEOUT_SECONDS

        lento = self._hook_command([self._check("C1", "sleep 5")])
        adulterado = lento.replace("TIMEOUT = ", "TIMEOUT = 0.05  # ", 1)
        self.assertNotEqual(adulterado, lento, "não achei a constante de timeout no script")
        resultado = subprocess.run(adulterado, shell=True, capture_output=True, text=True,
                                   input="{}", cwd=self.root, timeout=120)
        self.assertEqual(
            resultado.returncode, 0,
            f"check que estourou o relógio do acelerador bloqueou o turno: {resultado.stderr[:200]}",
        )
        self.assertLess(HOOK_CHECK_TIMEOUT_SECONDS, 600)

    def test_a_check_that_really_fails_still_blocks(self) -> None:
        """Controle: o afrouxamento acima não pode ter virado 'nunca bloqueia'."""

        comando = self._hook_command([self._check("C1", "false")])
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True,
                                   input="{}", cwd=self.root, timeout=120)
        self.assertEqual(resultado.returncode, 2, "check falhando deixou de bloquear")

    def test_the_per_check_timeout_is_declared(self) -> None:
        comando = self._hook_command([self._check("C1", "true")])
        self.assertIn("timeout=TIMEOUT", comando.replace(" ", ""),
                      "sem timeout por check, um check pendurado segura o hook")

    # -- não destruir restrição do projeto -----------------------------------

    def test_an_existing_project_settings_is_never_clobbered(self) -> None:
        """Um `.claude/settings.json` do projeto pode carregar `permissions.deny`
        ou um `PreToolUse`. Sobrescrever ALARGARIA o worker — o oposto do que
        este módulo promete."""

        gate_dir = self.root / ".claude"
        gate_dir.mkdir(parents=True, exist_ok=True)
        alvo = gate_dir / "settings.json"
        original = {"permissions": {"deny": ["Bash(curl *)"]},
                    "hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "guard"}]}]}}
        alvo.write_text(json.dumps(original), encoding="utf-8")

        with self.assertRaises(StopGateWouldClobberError):
            build_stop_gate_settings(self._mission([self._check("C1", "true")]), self.root)

        self.assertEqual(json.loads(alvo.read_text(encoding="utf-8")), original,
                         "a restrição do projeto foi destruída")

    def test_regenerating_our_own_settings_is_allowed(self) -> None:
        """Controle: a guarda acima não pode impedir o próprio gate de rodar
        duas vezes no mesmo worktree."""

        criteria = [self._check("C1", "true")]
        primeiro = build_stop_gate_settings(self._mission(criteria), self.root)
        segundo = build_stop_gate_settings(self._mission(criteria), self.root)
        self.assertEqual(Path(primeiro), Path(segundo))

    # -- o compilador não pode ser a única peça que falha fechado ------------

    def test_a_dirty_state_path_does_not_bring_the_caller_down(self) -> None:
        gate_dir = self.root / ".claude"
        gate_dir.mkdir(parents=True, exist_ok=True)
        (gate_dir / "stop-gate-reinforcements").mkdir(exist_ok=True)
        caminho = build_stop_gate_settings(self._mission([self._check("C1", "true")]), self.root)
        self.assertTrue(Path(caminho).is_file())
