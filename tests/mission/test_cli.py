from __future__ import annotations

import json
import os
import subprocess
import sys
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.cli import main
from pipe_venture_builder.exit_codes import (
    INPUT_INVALID_JSON,
    INPUT_UNAVAILABLE,
    READINESS_BLOCKED,
    SUCCESS,
    USAGE_ERROR,
)
from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.store import MissionStore
from tests.helpers import REPOSITORY_ROOT
from tests.mission.helpers import CREATED_AT, LATER, mission_input, write_json

SENTINEL = "sk-never-persist-this-value-1234567890"


def run_cli(*args: str) -> tuple[int, str, str]:
    stdout, stderr = StringIO(), StringIO()
    code = main(list(args), stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


class MissionCliTests(TestCase):
    def test_create_and_status_round_trip_across_processes(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = root / "mission.sqlite3"
            source = write_json(root / "mission.json", mission_input())

            code, out, err = run_cli(
                "mission", "create", str(source), "--store", str(store), "--at", CREATED_AT, "--json"
            )
            self.assertEqual(code, SUCCESS, err)
            created = json.loads(out)
            self.assertTrue(created["ok"])
            self.assertEqual(created["command"], "mission.create")
            mission_id = created["missionId"]
            self.assertRegex(mission_id, r"^MSN-[a-f0-9]{12}$")
            self.assertEqual(created["status"], "draft")
            self.assertRegex(created["fingerprint"], r"^sha256:")

            code, out, err = run_cli(
                "mission", "create", str(source), "--store", str(store), "--at", CREATED_AT, "--json"
            )
            self.assertEqual(code, SUCCESS, err)
            self.assertEqual(json.loads(out)["missionId"], mission_id)

            code, out, err = run_cli("mission", "show", mission_id, "--store", str(store), "--json")
            self.assertEqual(code, SUCCESS, err)
            self.assertEqual(json.loads(out)["mission"]["missionId"], mission_id)

            env = dict(os.environ, PYTHONPATH=str(REPOSITORY_ROOT / "src"), PYTHONDONTWRITEBYTECODE="1")
            completed = subprocess.run(
                [
                    sys.executable, "-B", "-m", "pipe_venture_builder",
                    "mission", "status", mission_id, "--store", str(store), "--json",
                ],
                capture_output=True, text=True, env=env, check=False,
            )
            self.assertEqual(completed.returncode, SUCCESS, completed.stderr)
            status = json.loads(completed.stdout)
            self.assertEqual(status["command"], "mission.status")
            self.assertEqual(status["status"]["missionId"], mission_id)
            self.assertEqual(status["status"]["status"], "draft")
            self.assertTrue(status["status"]["auditChainValid"])
            self.assertEqual(status["status"]["supervisor"], {"alive": None})

            code, out, err = run_cli("mission", "status", mission_id, "--store", str(store))
            self.assertEqual(code, SUCCESS, err)
            self.assertIn("Onde estamos", out)

    def test_lifecycle_verbs_and_decisions_through_cli(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store_path = root / "mission.sqlite3"
            source = write_json(root / "mission.json", mission_input())
            code, out, _ = run_cli("mission", "create", str(source), "--store", str(store_path), "--json")
            mission_id = json.loads(out)["missionId"]

            for verb, expected in (
                ("activate", "active"),
                ("pause", "paused"),
                ("resume", "active"),
            ):
                code, out, err = run_cli("mission", verb, mission_id, "--store", str(store_path), "--json")
                self.assertEqual(code, SUCCESS, err)
                self.assertEqual(json.loads(out)["status"], expected)

            with MissionStore(store_path) as store:
                decision_id = store.open_decision(
                    mission_id, kind="approval", context={"cycle": 1},
                    options=["approve", "reject"], safe_default="reject",
                    blocked_scope="delivery", deadline=None, at=LATER,
                )

            code, out, err = run_cli(
                "mission", "decisions", mission_id, "--pending", "--store", str(store_path), "--json"
            )
            self.assertEqual(code, SUCCESS, err)
            listed = json.loads(out)["decisions"]
            self.assertEqual([item["decisionId"] for item in listed], [decision_id])
            self.assertEqual(listed[0]["options"], ["approve", "reject"])
            self.assertEqual(listed[0]["safeDefault"], "reject")
            self.assertEqual(listed[0]["blockedScope"], "delivery")
            self.assertIsNone(listed[0]["deadline"])
            self.assertEqual(listed[0]["context"], {"cycle": 1})

            code, out, err = run_cli(
                "mission", "decide", decision_id, "--option", "approve",
                "--by", "agent:supervisor", "--store", str(store_path), "--json",
            )
            self.assertEqual(code, READINESS_BLOCKED)
            self.assertEqual(json.loads(err)["code"], "MISSION_CONTRACT_VIOLATION")

            code, out, err = run_cli(
                "mission", "decide", decision_id, "--option", "maybe",
                "--by", "human:cli:vitor", "--store", str(store_path), "--json",
            )
            self.assertEqual(code, READINESS_BLOCKED)

            with redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as usage:
                    run_cli(
                        "mission", "decide", decision_id, "--option", "approve",
                        "--store", str(store_path),
                    )
            self.assertEqual(usage.exception.code, USAGE_ERROR)

            code, out, err = run_cli(
                "mission", "decide", decision_id, "--option", "approve",
                "--by", "human:cli:vitor", "--store", str(store_path), "--json",
            )
            self.assertEqual(code, SUCCESS, err)
            self.assertEqual(json.loads(out)["decision"]["status"], "resolved")

            code, out, err = run_cli(
                "mission", "decisions", mission_id, "--pending", "--store", str(store_path), "--json"
            )
            self.assertEqual(json.loads(out)["decisions"], [])

            code, out, err = run_cli("mission", "complete", mission_id, "--store", str(store_path), "--json")
            self.assertEqual(code, READINESS_BLOCKED)
            self.assertEqual(json.loads(err)["code"], "MISSION_STATE_CONFLICT")

            code, out, err = run_cli("mission", "cancel", mission_id, "--store", str(store_path), "--json")
            self.assertEqual(code, SUCCESS, err)
            self.assertEqual(json.loads(out)["status"], "cancelled")

            code, out, err = run_cli("mission", "activate", mission_id, "--store", str(store_path), "--json")
            self.assertEqual(code, READINESS_BLOCKED)
            self.assertEqual(json.loads(err)["code"], "MISSION_STATE_CONFLICT")

    def test_contract_errors_are_fixed_messages_without_input_echo(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store_path = root / "mission.sqlite3"
            bad = mission_input()
            bad["title"] = f"leak {SENTINEL}"
            bad["constraints"]["secretsAllowed"] = True
            source = write_json(root / "bad.json", bad)

            code, out, err = run_cli("mission", "create", str(source), "--store", str(store_path), "--json")
            self.assertEqual(code, READINESS_BLOCKED)
            self.assertEqual(out, "")
            payload = json.loads(err)
            self.assertEqual(payload["code"], "MISSION_CONTRACT_VIOLATION")
            self.assertNotIn(SENTINEL, err)
            self.assertNotIn("leak", err)
            self.assertFalse(store_path.exists() and MissionStore(store_path).list_missions())

            code, out, err = run_cli("mission", "create", str(source), "--store", str(store_path))
            self.assertEqual(code, READINESS_BLOCKED)
            self.assertNotIn(SENTINEL, err)

            missing = root / "missing.json"
            code, out, err = run_cli("mission", "create", str(missing), "--store", str(store_path), "--json")
            self.assertEqual(code, INPUT_UNAVAILABLE)

            broken = root / "broken.json"
            broken.write_text("{not json", encoding="utf-8")
            code, out, err = run_cli("mission", "create", str(broken), "--store", str(store_path), "--json")
            self.assertEqual(code, INPUT_INVALID_JSON)

            code, out, err = run_cli("mission", "show", "MSN-aaaaaaaaaaaa", "--store", str(store_path), "--json")
            self.assertEqual(code, INPUT_UNAVAILABLE)
            self.assertEqual(json.loads(err)["code"], "MISSION_NOT_FOUND")

            code, out, err = run_cli("mission", "show", "not-an-id", "--store", str(store_path), "--json")
            self.assertEqual(code, READINESS_BLOCKED)
            self.assertEqual(json.loads(err)["code"], "MISSION_CONTRACT_VIOLATION")

    def test_json_output_is_stable_and_sorted(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store_path = root / "mission.sqlite3"
            source = write_json(root / "mission.json", mission_input())
            code, out, _ = run_cli(
                "mission", "create", str(source), "--store", str(store_path), "--at", CREATED_AT, "--json"
            )
            mission_id = json.loads(out)["missionId"]
            first = run_cli("mission", "status", mission_id, "--store", str(store_path), "--json")[1]
            second = run_cli("mission", "status", mission_id, "--store", str(store_path), "--json")[1]
            self.assertEqual(first, second)
            self.assertEqual(json.loads(first), json.loads(json.dumps(json.loads(first), sort_keys=True)))
            self.assertEqual(
                json.loads(out)["missionId"],
                build_mission(mission_input(), created_at=CREATED_AT)["missionId"],
            )
