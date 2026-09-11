"""Mission Loop B, slice 1: brief compilation and the headless worker runner."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.worker import (
    DEFAULT_MODEL,
    MIN_RUN_BUDGET_USD,
    WORKER_FIXED_RULES,
    ClaudeProcess,
    allowed_tools,
    compile_brief,
    extract_worker_output,
    parse_result_json,
    run_worker,
    worker_command,
)
from tests.mission.helpers import CREATED_AT
from tests.mission.loop_helpers import (
    WORKER_SENTINEL,
    FakeBinaries,
    good_worker_output,
    loop_mission,
    make_repo,
)


def mission_for(repo: Path) -> dict:
    return build_mission(loop_mission(repo), created_at=CREATED_AT)


class BriefAndCommandTests(TestCase):
    def test_brief_carries_mission_criteria_write_set_and_revision(self) -> None:
        with TemporaryDirectory() as directory:
            mission = mission_for(make_repo(Path(directory)))
        brief = compile_brief(mission, cycle=1, revision_instructions=None)
        self.assertIn(f"## Missão {mission['missionId']} v1 — {mission['title']}", brief)
        self.assertIn("Intenção do fundador: " + mission["intent"], brief)
        self.assertIn("- C1 (check): README nao diz que idea/adopt sao follow-up — verificação: `! grep -q 'remain follow-up' README.md`", brief)
        self.assertIn("- C2 (artifact): guia cita o CLI — artefato: `docs/guide.md`", brief)
        self.assertIn("- C3 (rubric): texto novo afirma so o que o codigo mostra", brief)
        self.assertIn("## Não-objetivos (não faça)\n- Alterar CLAUDE.md ou AGENTS.md", brief)
        self.assertIn("## Write set", brief)
        self.assertIn("- README.md\n- docs/guide.md", brief)
        self.assertIn('responda SOMENTE com JSON', brief)
        self.assertNotIn("Revisão anterior pediu", brief)

        revised = compile_brief(mission, cycle=2, revision_instructions="Reverta docs/extra.md.")
        self.assertIn("## Revisão anterior pediu (ciclo 1)\nReverta docs/extra.md.", revised)

    def test_command_has_fixed_flags_model_and_allowed_tools(self) -> None:
        with TemporaryDirectory() as directory:
            mission = mission_for(make_repo(Path(directory)))
        command = worker_command(mission, "BRIEF", claude_bin="/bin/fake-claude", budget_left=3.456)
        self.assertEqual(command[:3], ["/bin/fake-claude", "-p", "BRIEF"])
        pairs = dict(zip(command[3::2], command[4::2]))
        self.assertEqual(pairs["--output-format"], "json")
        self.assertEqual(pairs["--max-turns"], "60")
        self.assertEqual(pairs["--max-budget-usd"], "3.46")
        self.assertEqual(pairs["--permission-mode"], "acceptEdits")
        self.assertEqual(pairs["--permission-prompts"], "none")
        self.assertEqual(pairs["--model"], DEFAULT_MODEL)
        self.assertEqual(pairs["--append-system-prompt"], WORKER_FIXED_RULES)
        self.assertEqual(
            pairs["--allowedTools"],
            "Read,Edit,Write,Grep,Glob,Bash(git *),Bash(! grep -q 'remain follow-up' README.md)",
        )
        self.assertEqual(allowed_tools(mission), pairs["--allowedTools"])
        self.assertNotIn("--bare", command)
        self.assertNotIn("--resume", command)
        self.assertEqual(
            dict(zip(command[3::2], command[4::2]))["--model"], "sonnet",
        )
        custom = worker_command(mission, "B", claude_bin="c", budget_left=2, model="opus")
        self.assertEqual(dict(zip(custom[3::2], custom[4::2]))["--model"], "opus")
        self.assertGreaterEqual(MIN_RUN_BUDGET_USD, 1.5)


class ParsingTests(TestCase):
    def test_parse_result_json_tolerates_noise_and_rejects_garbage(self) -> None:
        payload = {"type": "result", "subtype": "success", "result": "x"}
        self.assertEqual(parse_result_json(json.dumps(payload)), payload)
        self.assertEqual(parse_result_json("warning\n" + json.dumps(payload) + "\n"), payload)
        self.assertIsNone(parse_result_json("nothing here"))
        self.assertIsNone(parse_result_json(""))
        self.assertIsNone(parse_result_json('{"type": "other"}'))

    def test_extract_worker_output_tolerates_text_around_and_normalises(self) -> None:
        body = json.dumps(good_worker_output())
        for text in (body, "Intro.\n" + body + "\nOutro.", "```json\n" + body + "\n```"):
            output = extract_worker_output(text)
            self.assertIsNotNone(output, text)
            self.assertTrue(output["done"])
            self.assertEqual(output["filesChanged"], ["README.md", "docs/guide.md"])
        partial = extract_worker_output('{"done": false}')
        self.assertEqual(partial, {"done": False, "summary": "", "filesChanged": [],
                                   "criteriaSelfAssessment": [], "blockers": []})
        self.assertIsNone(extract_worker_output("no json"))
        self.assertIsNone(extract_worker_output('{"other": 1}'))
        self.assertIsNone(extract_worker_output('{"done": "yes"}'))


class RunWorkerTests(TestCase):
    def test_collected_run_reports_session_cost_turns_and_output(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = mission_for(repo)
            fakes.scenario(worker=[{
                "worker_output": good_worker_output(), "wrap": "text", "noise": True,
                "result": {"total_cost_usd": 1.25, "num_turns": 11,
                           "session_id": "0c1d2e3f-0000-4000-8000-000000000001"},
            }])
            result = run_worker(
                mission, run_id="MRUN-000000000001", cwd=repo,
                claude_bin=fakes.claude_bin, budget_left=5.0, poll_seconds=0.05,
            )
            self.assertEqual(result.status, "collected")
            self.assertIsNone(result.reason)
            self.assertEqual(result.session_id, "0c1d2e3f-0000-4000-8000-000000000001")
            self.assertAlmostEqual(result.cost_usd, 1.25)
            self.assertEqual(result.num_turns, 11)
            self.assertEqual(result.subtype, "success")
            self.assertEqual(result.permission_denials, 0)
            self.assertRegex(result.result_fingerprint, r"^sha256:[a-f0-9]{64}$")
            self.assertEqual(result.output["summary"], WORKER_SENTINEL)
            self.assertEqual(result.model, DEFAULT_MODEL)

            call = fakes.claude_calls()[0]
            self.assertEqual(call["role"], "worker")
            self.assertTrue(call["stdinIsDevNull"], "stdin must be /dev/null")
            self.assertEqual(Path(call["cwd"]).resolve(), repo.resolve())
            self.assertIn("--max-budget-usd", call["argv"])

    def test_no_json_error_subtype_and_permission_denials_are_failures_or_flags(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = mission_for(repo)
            fakes.scenario(worker=[
                {"mode": "garbage", "exit_code": 0},
                {"mode": "silent", "exit_code": 1},
                {"result": {"subtype": "error_max_turns", "is_error": True, "total_cost_usd": 0.7}},
                {"worker_output": good_worker_output(),
                 "result": {"permission_denials": [{"tool_name": "Bash", "tool_input": {"command": "rm -rf x"}}]}},
            ])
            common = dict(cwd=repo, claude_bin=fakes.claude_bin, budget_left=5.0, poll_seconds=0.05)
            garbage = run_worker(mission, run_id="MRUN-000000000001", **common)
            self.assertEqual((garbage.status, garbage.reason), ("failed", "no_json"))
            self.assertIsNone(garbage.output)
            silent = run_worker(mission, run_id="MRUN-000000000002", **common)
            self.assertEqual((silent.status, silent.reason), ("failed", "no_json"))
            self.assertEqual(silent.returncode, 1)
            max_turns = run_worker(mission, run_id="MRUN-000000000003", **common)
            self.assertEqual((max_turns.status, max_turns.reason), ("failed", "error_max_turns"))
            self.assertAlmostEqual(max_turns.cost_usd, 0.7, msg="cost of a failed run still counts")
            denied = run_worker(mission, run_id="MRUN-000000000004", **common)
            self.assertEqual(denied.status, "collected")
            self.assertEqual(denied.permission_denials, 1)
            self.assertEqual(denied.denied_tools, ["Bash"])
            self.assertEqual(denied.denied_calls, ["Bash(rm -rf x)"])

    def test_timeout_kills_the_worker_and_fails_the_run(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = mission_for(repo)
            fakes.scenario(worker=[{"sleep": 30, "worker_output": good_worker_output()}])
            started = time.monotonic()
            result = run_worker(
                mission, run_id="MRUN-000000000001", cwd=repo, claude_bin=fakes.claude_bin,
                budget_left=5.0, poll_seconds=0.05, timeout=0.5, grace_seconds=0.5,
            )
            self.assertLess(time.monotonic() - started, 5)
            self.assertEqual((result.status, result.reason), ("failed", "timeout"))

    def test_should_stop_terminates_with_sigterm_and_reports_interrupted(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = mission_for(repo)
            fakes.scenario(worker=[{"sleep": 30, "on_sigterm": "exit"}])
            flag = {"stop": False}
            threading.Timer(0.3, lambda: flag.__setitem__("stop", True)).start()
            started = time.monotonic()
            result = run_worker(
                mission, run_id="MRUN-000000000001", cwd=repo, claude_bin=fakes.claude_bin,
                budget_left=5.0, poll_seconds=0.05, should_stop=lambda: flag["stop"],
            )
            self.assertLess(time.monotonic() - started, 5)
            self.assertEqual((result.status, result.reason), ("interrupted", "stop_requested"))
            self.assertEqual(result.returncode, 143, "the fake exits 143 on SIGTERM")

    def test_worker_ignoring_sigterm_is_killed_after_grace(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = mission_for(repo)
            fakes.scenario(worker=[{"sleep": 30, "on_sigterm": "ignore"}])
            result = run_worker(
                mission, run_id="MRUN-000000000001", cwd=repo, claude_bin=fakes.claude_bin,
                budget_left=5.0, poll_seconds=0.05, should_stop=lambda: True, grace_seconds=0.3,
            )
            self.assertEqual(result.status, "interrupted")
            self.assertEqual(result.returncode, -9)

    def test_external_terminate_on_process_handle(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = mission_for(repo)
            fakes.scenario(worker=[{"sleep": 30}])
            process = ClaudeProcess(
                worker_command(mission, "B", claude_bin=fakes.claude_bin, budget_left=5.0), cwd=repo
            )
            process.start()
            threading.Timer(0.2, process.terminate).start()
            result = process.wait(timeout=10, poll_seconds=0.05)
            self.assertEqual(result.status, "interrupted")
