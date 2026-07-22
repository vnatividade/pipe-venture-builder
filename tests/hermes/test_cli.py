from __future__ import annotations

import io
import json
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from pipe_venture_builder.adapters.hermes.cli import main
from tests.control_plane.helpers import approval_for, create_plan
from tests.hermes.helpers import BEGIN_AT, EVENT_AT, SESSION_ONE, product_root


class HermesCliTests(TestCase):
    def invoke(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    @mock.patch(
        "pipe_venture_builder.adapters.hermes.cli.probe_hermes",
        return_value={
            "available": True,
            "compatible": True,
            "command": "hermes",
            "version": "0.17.0",
            "reason": None,
        },
    )
    def test_probe_reports_compatible_runtime_without_configuration_access(
        self, _probe: mock.Mock
    ) -> None:
        code, stdout, stderr = self.invoke(["probe"])

        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        result = json.loads(stdout)
        self.assertTrue(result["available"])
        self.assertTrue(result["compatible"])
        self.assertEqual(result["version"], "0.17.0")

    def test_begin_uses_hermes_session_environment_and_status_resumes(self) -> None:
        with TemporaryDirectory() as directory:
            base = Path(directory)
            root = product_root(base)
            plan_path = base / "plan.json"
            plan_path.write_text(json.dumps(create_plan()), encoding="utf-8")
            state_args = [
                "--store",
                str(base / "control.sqlite3"),
                "--checkpoint-dir",
                str(base / "hermes"),
            ]
            with mock.patch.dict(os.environ, {"HERMES_SESSION_ID": SESSION_ONE}):
                code, stdout, _ = self.invoke(
                    [
                        "begin",
                        *state_args,
                        "--plan",
                        str(plan_path),
                        "--product-root",
                        str(root),
                        "--product-id",
                        "example-product",
                        "--ticket-id",
                        "PIP-713",
                        "--workflow",
                        "adopt",
                        "--artifact",
                        "README.md",
                        "--event-id",
                        "begin-cli-1",
                        "--at",
                        BEGIN_AT,
                    ]
                )
            self.assertEqual(code, 0)
            begun = json.loads(stdout)
            self.assertEqual(begun["sessionId"], SESSION_ONE)

            status_code, status_stdout, _ = self.invoke(
                ["status", *state_args, "--run-id", begun["runId"]]
            )
            self.assertEqual(status_code, 0)
            self.assertTrue(json.loads(status_stdout)["auditChainValid"])

    def test_event_requires_session_and_never_echoes_input(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            code, stdout, stderr = self.invoke(
                [
                    "event",
                    "--store",
                    ":memory:",
                    "--checkpoint-dir",
                    "/tmp/unused-hermes-cli-test",
                    "--run-id",
                    "RUN-000000000000",
                    "--kind",
                    "tool.failed",
                    "--event-id",
                    "sk-secret-value-12345678901234567890",
                    "--at",
                    EVENT_AT,
                ]
            )

        self.assertEqual(code, 8)
        self.assertEqual(stdout, "")
        self.assertEqual(json.loads(stderr)["error"]["code"], "HERMES_SESSION_ID_REQUIRED")
        self.assertNotIn("sk-secret", stderr)

    def test_invalid_json_uses_stable_controlled_exit(self) -> None:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "plan.json"
            source.write_text("not-json", encoding="utf-8")
            code, _, stderr = self.invoke(
                [
                    "begin",
                    "--store",
                    str(Path(directory) / "control.sqlite3"),
                    "--checkpoint-dir",
                    str(Path(directory) / "hermes"),
                    "--plan",
                    str(source),
                    "--product-root",
                    directory,
                    "--product-id",
                    "example-product",
                    "--ticket-id",
                    "PIP-713",
                    "--workflow",
                    "adopt",
                    "--artifact",
                    "plan.json",
                    "--event-id",
                    "begin-cli-invalid",
                    "--session-id",
                    SESSION_ONE,
                ]
            )
        self.assertEqual(code, 8)
        self.assertEqual(json.loads(stderr)["error"]["code"], "PLAN_INVALID_JSON")

    def test_approval_grant_requires_the_exact_plan_input(self) -> None:
        with TemporaryDirectory() as directory:
            plan = create_plan()
            approval = approval_for(plan)
            approval_path = Path(directory) / "approval.json"
            approval_path.write_text(json.dumps(approval), encoding="utf-8")
            code, stdout, stderr = self.invoke(
                [
                    "event",
                    "--store",
                    ":memory:",
                    "--checkpoint-dir",
                    str(Path(directory) / "hermes"),
                    "--run-id",
                    "RUN-000000000000",
                    "--kind",
                    "approval.granted",
                    "--event-id",
                    "approval-grant-cli-1",
                    "--session-id",
                    SESSION_ONE,
                    "--action-id",
                    approval["actionId"],
                    "--approval-id",
                    approval["approvalId"],
                    "--approval",
                    str(approval_path),
                    "--at",
                    EVENT_AT,
                ]
            )
        self.assertEqual(code, 8)
        self.assertEqual(stdout, "")
        self.assertEqual(
            json.loads(stderr)["error"]["code"], "PLAN_REQUIRED_FOR_APPROVAL"
        )
