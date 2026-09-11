"""PIP-906: the clean-context blocker responder — read-only, isolated,
answers by JSON schema. Mirrors ``test_reviewer.py``'s shape."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.responder import (
    RESPONDER_ALLOWED_TOOLS,
    RESPONDER_OUTPUT_INVALID,
    RESPONDER_RUN_FAILED,
    RESPONSE_SCHEMA,
    build_responder_prompt,
    parse_response,
    responder_command,
    run_responder,
)
from tests.mission.helpers import CREATED_AT
from tests.mission.loop_helpers import (
    EXPECTED_DISALLOWED_TOOLS,
    FakeBinaries,
    cli_options,
    loop_mission,
    make_repo,
    single_values,
)


class PromptAndCommandTests(TestCase):
    def test_prompt_has_intent_criteria_reserved_and_blockers(self) -> None:
        with TemporaryDirectory() as directory:
            mission = build_mission(loop_mission(make_repo(Path(directory))), created_at=CREATED_AT)
        prompt = build_responder_prompt(mission, ["o worktree nao tem .venv"])
        self.assertIn(f"## Missão {mission['missionId']}", prompt)
        self.assertIn(mission["intent"], prompt)
        self.assertIn("- C1 (check): README nao diz que idea/adopt sao follow-up", prompt)
        self.assertIn("## Reservado ao fundador", prompt)
        self.assertIn("Merge do PR", prompt)
        self.assertIn("## Bloqueios reportados pelo worker\n- o worktree nao tem .venv", prompt)
        self.assertIn("`instruct`", prompt)
        self.assertIn("`escalate`", prompt)
        self.assertIn("credencial", prompt)

    def test_command_is_read_only_without_edit_write_or_bash(self) -> None:
        # C4: if the responder were ever given Edit, Write, or any Bash
        # entry, this is the test that must fail.
        command = responder_command("PROMPT", claude_bin="/bin/fake", budget_left=2.0)
        self.assertEqual(command[:3], ["/bin/fake", "-p", "PROMPT"])
        pairs = single_values(command[3:])
        self.assertEqual(pairs["--output-format"], "json")
        self.assertEqual(json.loads(pairs["--json-schema"]), RESPONSE_SCHEMA)
        self.assertEqual(pairs["--permission-mode"], "plan")
        self.assertEqual(pairs["--allowedTools"], RESPONDER_ALLOWED_TOOLS)
        self.assertEqual(RESPONDER_ALLOWED_TOOLS, "Read,Grep,Glob")
        for tool in ("Edit", "Write", "Bash"):
            self.assertNotIn(tool, pairs["--allowedTools"])
        self.assertNotIn("--bare", command)
        options = cli_options(command[3:])
        self.assertEqual(options["--setting-sources"], ["project"])
        self.assertEqual(options["--strict-mcp-config"], [])
        self.assertEqual(options["--disallowedTools"], EXPECTED_DISALLOWED_TOOLS)

    def test_schema_has_no_meta_schema_uri_and_the_expected_actions(self) -> None:
        command = responder_command("p", claude_bin="claude", budget_left=1.5)
        schema = json.loads(command[command.index("--json-schema") + 1])
        self.assertNotIn("$schema", schema)
        self.assertEqual(schema["required"], ["action", "instructions", "reason"])
        self.assertEqual(schema["properties"]["action"]["enum"], ["instruct", "escalate"])


class ParseResponseTests(TestCase):
    def test_parse_response_prefers_structured_output_then_result_text(self) -> None:
        response = {"action": "instruct", "instructions": "faça X", "reason": "r"}
        parsed = parse_response(response, None)
        self.assertEqual(parsed, {"action": "instruct", "instructions": "faça X"})
        from_text = parse_response(None, "Aqui está:\n" + json.dumps(response))
        self.assertEqual(from_text["action"], "instruct")
        self.assertIsNone(parse_response(None, "no json"))
        self.assertIsNone(parse_response({"action": "maybe", "instructions": "x"}, None))
        self.assertIsNone(parse_response({"action": "instruct"}, None), "instructions missing")
        self.assertIsNone(parse_response({"action": "instruct", "instructions": 1}, None))


class RunResponderTests(TestCase):
    def test_run_responder_returns_action_and_instructions(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fakes.scenario(responder=[{
                "structured_output": {"action": "instruct", "instructions": "use a venv do checkout", "reason": "r"},
                "result": {"total_cost_usd": 0.1},
            }])
            response = run_responder(
                mission, ["bloqueio"], claude_bin=fakes.claude_bin, cwd=repo,
                budget_left=3.0, poll_seconds=0.05,
            )
            self.assertTrue(response.valid)
            self.assertEqual(response.action, "instruct")
            self.assertEqual(response.instructions, "use a venv do checkout")
            self.assertAlmostEqual(response.claude.cost_usd, 0.1)
            call = fakes.claude_calls()[0]
            self.assertEqual(call["role"], "responder")
            self.assertTrue(call["stdinIsDevNull"])

    def test_invalid_json_or_failed_run_becomes_invalid_with_fixed_reason(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fakes.scenario(responder=[
                {"mode": "garbage"},
                {"result": {"subtype": "error_max_budget_usd", "is_error": True}},
                {"structured_output": {"action": "escalate", "instructions": "", "reason": "fora do escopo"}},
            ])
            common = dict(claude_bin=fakes.claude_bin, cwd=repo, budget_left=3.0, poll_seconds=0.05)
            garbage = run_responder(mission, ["x"], **common)
            self.assertEqual((garbage.valid, garbage.reason), (False, RESPONDER_RUN_FAILED))
            over_budget = run_responder(mission, ["x"], **common)
            self.assertEqual((over_budget.valid, over_budget.reason), (False, RESPONDER_RUN_FAILED))
            escalate = run_responder(mission, ["x"], **common)
            self.assertTrue(escalate.valid)
            self.assertEqual(escalate.action, "escalate")

    def test_no_structured_output_at_all_is_output_invalid(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fakes.scenario(responder=[{"result": {"result": "no JSON here"}}])
            response = run_responder(
                mission, ["x"], claude_bin=fakes.claude_bin, cwd=repo, budget_left=3.0, poll_seconds=0.05
            )
            self.assertEqual((response.valid, response.reason), (False, RESPONDER_OUTPUT_INVALID))
