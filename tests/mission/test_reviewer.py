"""Mission Loop B, slice 2: the clean-context reviewer."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.reviewer import (
    EVIDENCE_PROMPT_CHARS,
    MAX_DIFF_CHARS,
    REVIEWER_ALLOWED_TOOLS,
    REVIEWER_OUTPUT_INVALID,
    REVIEWER_RUN_FAILED,
    VERDICT_SCHEMA,
    build_review_prompt,
    parse_verdict,
    reviewer_command,
    run_review,
)
from tests.mission.helpers import CREATED_AT
from tests.mission.loop_helpers import (
    EXPECTED_DISALLOWED_TOOLS,
    FakeBinaries,
    cli_options,
    loop_mission,
    make_repo,
    satisfied_verdict,
    single_values,
)


class PromptAndCommandTests(TestCase):
    def test_prompt_has_criteria_non_goals_diff_and_judging_instruction(self) -> None:
        with TemporaryDirectory() as directory:
            mission = build_mission(loop_mission(make_repo(Path(directory))), created_at=CREATED_AT)
        prompt = build_review_prompt(mission, "diff --git a/README.md b/README.md\n+pipe idea\n")
        self.assertIn(f"## Missão {mission['missionId']}", prompt)
        self.assertIn("- C1 (check): README nao diz que idea/adopt sao follow-up", prompt)
        self.assertIn("- C3 (rubric): texto novo afirma so o que o codigo mostra — pergunta: O texto novo afirma apenas o que o codigo mostra?", prompt)
        self.assertIn("## Não-objetivos\n- Alterar CLAUDE.md ou AGENTS.md", prompt)
        self.assertIn("## Write set\n- README.md\n- docs/guide.md", prompt)
        self.assertIn("```diff\ndiff --git a/README.md b/README.md\n+pipe idea\n```", prompt)
        self.assertIn("Julgue SOMENTE contra os critérios e os não-objetivos", prompt)
        self.assertIn("`out_of_mission`", prompt)
        self.assertIn("`blocked`", prompt)
        self.assertIn("Você não viu a transcrição do worker", prompt)

        long_diff = "x" * (MAX_DIFF_CHARS + 500)
        truncated = build_review_prompt(mission, long_diff)
        self.assertIn("[diff truncado", truncated)
        self.assertLess(len(truncated), MAX_DIFF_CHARS + 2000)

    def test_command_is_read_only_with_schema_and_model(self) -> None:
        command = reviewer_command("PROMPT", claude_bin="/bin/fake", budget_left=2.0)
        self.assertEqual(command[:3], ["/bin/fake", "-p", "PROMPT"])
        pairs = single_values(command[3:])
        self.assertEqual(pairs["--output-format"], "json")
        self.assertEqual(json.loads(pairs["--json-schema"]), VERDICT_SCHEMA)
        self.assertEqual(pairs["--max-turns"], "20")
        self.assertEqual(pairs["--max-budget-usd"], "2.00")
        self.assertEqual(pairs["--permission-mode"], "plan")
        self.assertEqual(pairs["--allowedTools"], REVIEWER_ALLOWED_TOOLS)
        self.assertEqual(REVIEWER_ALLOWED_TOOLS, "Read,Grep,Glob,Bash(git diff *),Bash(git log *)")
        self.assertEqual(pairs["--model"], "sonnet")
        self.assertNotIn("Edit", pairs["--allowedTools"])
        self.assertNotIn("--bare", command)
        options = cli_options(command[3:])
        self.assertEqual(options["--setting-sources"], ["project"], "A3: no user settings")
        self.assertEqual(options["--strict-mcp-config"], [])
        self.assertEqual(options["--disallowedTools"], EXPECTED_DISALLOWED_TOOLS)
        self.assertEqual(VERDICT_SCHEMA["properties"]["verdict"]["enum"],
                         ["satisfied", "needs_revision", "out_of_mission", "blocked"])


class VerdictParsingTests(TestCase):
    def test_schema_passed_to_cli_has_no_meta_schema_uri(self) -> None:
        # Medido com o CLI real 2.1.267 na demo de 11/09: um "$schema" draft
        # 2020-12 faz o claude recusar o --json-schema ("no schema with key or
        # ref ...") e sair em 1 s, sem sessão; o revisor virava "blocked".
        command = reviewer_command("p", claude_bin="claude", budget_left=1.5)
        schema = json.loads(command[command.index("--json-schema") + 1])
        self.assertNotIn("$schema", schema)
        self.assertNotIn("$schema", VERDICT_SCHEMA)
        self.assertEqual(schema["required"], ["verdict", "criteria", "reasons"])

    def test_schema_leaves_slack_over_the_evidence_length_the_prompt_asks_for(self) -> None:
        # Medido na missão do PIP-903 (11/09, ciclo 3): o revisor respondeu
        # "satisfied" nas 5 tentativas com evidência de 409 a 708 chars; o
        # schema (400) recusou todas e o CLI saiu com
        # error_max_structured_output_retries — veredito certo virou escalada.
        from jsonschema import Draft202012Validator

        with TemporaryDirectory() as directory:
            mission = build_mission(loop_mission(make_repo(Path(directory))), created_at=CREATED_AT)
        prompt = build_review_prompt(mission, "diff --git a/README.md b/README.md\n+pipe idea\n")
        self.assertIn(f"(máx. {EVIDENCE_PROMPT_CHARS} chars)", prompt)
        schema_limit = VERDICT_SCHEMA["properties"]["criteria"]["items"]["properties"]["evidence"]["maxLength"]
        self.assertGreaterEqual(schema_limit, 3 * EVIDENCE_PROMPT_CHARS)

        verdict = satisfied_verdict()
        verdict["criteria"][0]["evidence"] = "e" * 708
        verdict["reasons"] = ["r" * 450]
        errors = [error.message for error in Draft202012Validator(VERDICT_SCHEMA).iter_errors(verdict)]
        self.assertEqual(errors, [])

    def test_parse_verdict_prefers_structured_output_then_result_text(self) -> None:
        verdict = satisfied_verdict(revisionInstructions="none")
        parsed = parse_verdict(verdict, None)
        self.assertEqual(parsed["verdict"], "satisfied")
        self.assertEqual(parsed["criteria"], [{"id": "C1", "met": True}, {"id": "C2", "met": True}, {"id": "C3", "met": True}])
        self.assertEqual(parsed["reasons"], ["diff stays inside the write set"])
        self.assertEqual(parsed["revisionInstructions"], "none")
        from_text = parse_verdict(None, "Veredito:\n" + json.dumps(verdict))
        self.assertEqual(from_text["verdict"], "satisfied")
        self.assertIsNone(parse_verdict(None, "no json"))
        self.assertIsNone(parse_verdict({"verdict": "approved", "criteria": [], "reasons": []}, None))
        self.assertIsNone(parse_verdict({"verdict": "satisfied", "criteria": [{"id": "C1", "met": "yes"}], "reasons": []}, None))
        self.assertIsNone(parse_verdict({"verdict": "satisfied", "criteria": "C1", "reasons": []}, None))
        minimal = parse_verdict({"verdict": "blocked"}, None)
        self.assertEqual(minimal, {"verdict": "blocked", "criteria": [], "reasons": [], "revisionInstructions": None})


class RunReviewTests(TestCase):
    def test_review_returns_verdict_and_cost_from_structured_output(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fakes.scenario(reviewer=[{
                "structured_output": satisfied_verdict(),
                "result": {"total_cost_usd": 0.33, "num_turns": 4},
            }])
            review = run_review(mission, "diff", claude_bin=fakes.claude_bin, cwd=repo,
                                budget_left=3.0, poll_seconds=0.05)
            self.assertEqual(review.verdict, "satisfied")
            self.assertTrue(review.valid)
            self.assertEqual(review.criteria_met, {"C1": True, "C2": True, "C3": True})
            self.assertAlmostEqual(review.claude.cost_usd, 0.33)
            self.assertEqual(review.claude.status, "collected")
            call = fakes.claude_calls()[0]
            self.assertEqual(call["role"], "reviewer")
            self.assertTrue(call["stdinIsDevNull"])

    def test_invalid_json_or_failed_run_becomes_blocked_with_fixed_reason(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            repo = make_repo(Path(directory))
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fakes.scenario(reviewer=[
                {"result": {"result": "I think it is fine but here is no JSON"}},
                {"mode": "garbage"},
                {"result": {"subtype": "error_max_budget_usd", "is_error": True, "total_cost_usd": 0.9}},
                {"structured_output": {"verdict": "needs_revision", "criteria": [{"id": "C3", "met": False, "evidence": "claims"}],
                                       "reasons": ["overclaims"], "revisionInstructions": "Remova a frase X."}},
            ])
            common = dict(claude_bin=fakes.claude_bin, cwd=repo, budget_left=3.0, poll_seconds=0.05)
            no_json = run_review(mission, "diff", **common)
            self.assertEqual((no_json.verdict, no_json.valid, no_json.reason), ("blocked", False, REVIEWER_OUTPUT_INVALID))
            garbage = run_review(mission, "diff", **common)
            self.assertEqual((garbage.verdict, garbage.reason), ("blocked", REVIEWER_RUN_FAILED))
            self.assertEqual(garbage.claude.status, "failed")
            over_budget = run_review(mission, "diff", **common)
            self.assertEqual((over_budget.verdict, over_budget.reason), ("blocked", REVIEWER_RUN_FAILED))
            self.assertAlmostEqual(over_budget.claude.cost_usd, 0.9)
            revision = run_review(mission, "diff", **common)
            self.assertEqual(revision.verdict, "needs_revision")
            self.assertEqual(revision.revision_instructions, "Remova a frase X.")
            self.assertEqual(revision.criteria_met, {"C3": False})
