from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.apply.cli import main
from tests.control_plane.helpers import (
    DECIDED_AT,
    EXECUTED_AT,
    EXPIRES_AT,
    create_plan,
    fixture_for,
    write_json,
)


class SupervisedApplyCliTests(TestCase):
    def test_approve_execute_and_audit_fixture_flow(self) -> None:
        plan = create_plan()
        action_id = plan["actions"][0]["actionId"]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = root / "control-plane.sqlite3"
            plan_path = write_json(root / "plan.json", plan)
            fixture_path = write_json(root / "fixture.json", fixture_for(plan))
            approval_path = root / "approval.json"

            approve_code, approve_output, approve_error = self._run(
                [
                    "approve",
                    "--store",
                    str(store),
                    "--plan",
                    str(plan_path),
                    "--action",
                    action_id,
                    "--actor",
                    "founder",
                    "--source-ref",
                    "linear:PIP-712",
                    "--expires-at",
                    EXPIRES_AT,
                    "--at",
                    DECIDED_AT,
                    "--output",
                    str(approval_path),
                ]
            )
            self.assertEqual(approve_code, 0, approve_error)
            approve_result = json.loads(approve_output)
            self.assertEqual(approve_result["status"], "recorded")

            execute_code, execute_output, execute_error = self._run(
                [
                    "execute",
                    "--store",
                    str(store),
                    "--plan",
                    str(plan_path),
                    "--approval",
                    str(approval_path),
                    "--fixture",
                    str(fixture_path),
                    "--action",
                    action_id,
                    "--source-fingerprint",
                    plan["baseline"]["fingerprint"],
                    "--at",
                    EXECUTED_AT,
                ]
            )
            self.assertEqual(execute_code, 0, execute_error)
            execute_result = json.loads(execute_output)
            self.assertEqual(execute_result["status"], "verified")

            audit_code, audit_output, audit_error = self._run(
                [
                    "audit",
                    "--store",
                    str(store),
                    "--run-id",
                    approve_result["runId"],
                ]
            )
            self.assertEqual(audit_code, 0, audit_error)
            audit_result = json.loads(audit_output)
            self.assertTrue(audit_result["auditChainValid"])
            self.assertEqual(audit_result["status"], "completed")

    def test_approval_output_is_never_overwritten(self) -> None:
        plan = create_plan()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path = write_json(root / "plan.json", plan)
            approval_path = root / "approval.json"
            approval_path.write_text("preserve-me", encoding="utf-8")

            code, _output, error = self._run(
                [
                    "approve",
                    "--store",
                    str(root / "state.sqlite3"),
                    "--plan",
                    str(plan_path),
                    "--action",
                    plan["actions"][0]["actionId"],
                    "--actor",
                    "founder",
                    "--source-ref",
                    "linear:PIP-712",
                    "--expires-at",
                    EXPIRES_AT,
                    "--at",
                    DECIDED_AT,
                    "--output",
                    str(approval_path),
                ]
            )

            self.assertEqual(code, 8)
            self.assertEqual(approval_path.read_text(encoding="utf-8"), "preserve-me")
            self.assertIn("APPROVAL_OUTPUT_EXISTS", error)

    def test_invalid_json_error_never_echoes_source_content(self) -> None:
        sentinel = "sk-never-echo-this-value-1234567890"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path = root / "plan.json"
            plan_path.write_text("{" + sentinel, encoding="utf-8")

            code, output, error = self._run(
                [
                    "approve",
                    "--store",
                    str(root / "state.sqlite3"),
                    "--plan",
                    str(plan_path),
                    "--action",
                    "RA-111111111111",
                    "--actor",
                    "founder",
                    "--source-ref",
                    "linear:PIP-712",
                    "--expires-at",
                    EXPIRES_AT,
                    "--at",
                    DECIDED_AT,
                    "--output",
                    str(root / "approval.json"),
                ]
            )

            self.assertEqual(code, 9)
            self.assertEqual(output, "")
            self.assertNotIn(sentinel, error)
            self.assertIn("PLAN_INVALID_JSON", error)

    def test_execute_exit_codes_cover_blocked_failed_and_interrupted(self) -> None:
        cases = (
            ("denied", "success", 8, "blocked"),
            ("approved", "fail", 9, "failed"),
            ("approved", "interrupt_once", 10, "interrupted"),
        )
        for decision, behavior, expected_code, expected_status in cases:
            with self.subTest(decision=decision, behavior=behavior):
                plan = create_plan()
                action_id = plan["actions"][0]["actionId"]
                with TemporaryDirectory() as directory:
                    root = Path(directory)
                    store = root / "state.sqlite3"
                    plan_path = write_json(root / "plan.json", plan)
                    fixture_path = write_json(
                        root / "fixture.json",
                        fixture_for(plan, apply_behavior=behavior),
                    )
                    approval_path = root / "approval.json"
                    approve_code, _output, error = self._run(
                        [
                            "approve",
                            "--store",
                            str(store),
                            "--plan",
                            str(plan_path),
                            "--action",
                            action_id,
                            "--actor",
                            "founder",
                            "--source-ref",
                            "linear:PIP-712",
                            "--expires-at",
                            EXPIRES_AT,
                            "--at",
                            DECIDED_AT,
                            "--decision",
                            decision,
                            "--output",
                            str(approval_path),
                        ]
                    )
                    self.assertEqual(approve_code, 0, error)
                    code, output, error = self._run(
                        [
                            "execute",
                            "--store",
                            str(store),
                            "--plan",
                            str(plan_path),
                            "--approval",
                            str(approval_path),
                            "--fixture",
                            str(fixture_path),
                            "--action",
                            action_id,
                            "--source-fingerprint",
                            plan["baseline"]["fingerprint"],
                            "--at",
                            EXECUTED_AT,
                        ]
                    )
                    self.assertEqual(code, expected_code, error)
                    self.assertEqual(json.loads(output)["status"], expected_status)

    @staticmethod
    def _run(arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()
