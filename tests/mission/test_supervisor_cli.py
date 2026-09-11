"""Mission Loop B, slice 5: ``pipe mission supervise|run-once|reconcile`` and ``--detach``."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.cli import main
from pipe_venture_builder.exit_codes import READINESS_BLOCKED, SUCCESS
from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.store import MissionStore
from tests.helpers import REPOSITORY_ROOT
from tests.mission.loop_helpers import (
    GOOD_FILES,
    FakeBinaries,
    good_worker_output,
    loop_mission,
    make_repo,
    satisfied_verdict,
)


def run_cli(*args: str) -> tuple[int, str, str]:
    stdout, stderr = StringIO(), StringIO()
    code = main(list(args), stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


def wait_until(predicate, *, timeout: float = 15.0, interval: float = 0.05) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


def _read_pid(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


class SupervisorCliTests(TestCase):
    def setUp(self) -> None:
        self._directory = TemporaryDirectory()
        self.root = Path(self._directory.name)
        self.repo = make_repo(self.root)
        self.home = self.root / "home"
        self.store_path = self.root / "mission.sqlite3"
        with MissionStore(self.store_path) as store:
            self.mission_id = store.create(build_mission(loop_mission(self.repo)))
            store.activate(self.mission_id)
        self.fakes = FakeBinaries(self.root)
        self.fakes.__enter__()

    def tearDown(self) -> None:
        self.fakes.__exit__()
        self._directory.cleanup()

    def common(self) -> list[str]:
        return ["--store", str(self.store_path), "--home", str(self.home), "--json"]

    def fake_bins(self) -> list[str]:
        return ["--claude-bin", self.fakes.claude_bin, "--gh-bin", self.fakes.gh_bin, "--poll-seconds", "0.05"]

    def status(self) -> dict:
        code, out, err = run_cli("mission", "status", self.mission_id, *self.common())
        self.assertEqual(code, SUCCESS, err)
        return json.loads(out)["status"]

    def test_run_once_completes_a_cycle_and_records_the_models(self) -> None:
        self.fakes.scenario(
            worker=[{"write_files": dict(GOOD_FILES), "worker_output": good_worker_output()}],
            reviewer=[{"structured_output": satisfied_verdict()}],
        )
        code, out, err = run_cli(
            "mission", "run-once", self.mission_id, *self.common(), *self.fake_bins(),
            "--worker-model", "haiku", "--reviewer-model", "opus",
        )
        self.assertEqual(code, SUCCESS, err)
        payload = json.loads(out)
        self.assertEqual(payload["command"], "mission.run-once")
        self.assertEqual((payload["status"], payload["reason"]), ("completed", "completed"))
        roles = {call["role"]: call["argv"] for call in self.fakes.claude_calls()}
        self.assertEqual(roles["worker"][roles["worker"].index("--model") + 1], "haiku")
        self.assertEqual(roles["reviewer"][roles["reviewer"].index("--model") + 1], "opus")
        status = self.status()
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["supervisor"]["alive"], True, "run-once claimed the pid file (this process)")
        self.assertEqual(status["supervisor"]["pid"], os.getpid())

    def test_reconcile_marks_orphan_run_unknown_through_cli(self) -> None:
        with MissionStore(self.store_path) as store:
            orphan = store.open_run(self.mission_id, cycle=1, attempt=1, executor="worker:sonnet")
        code, out, err = run_cli("mission", "reconcile", self.mission_id, *self.common())
        self.assertEqual(code, SUCCESS, err)
        payload = json.loads(out)
        self.assertEqual(payload["reconciled"], [orphan])
        self.assertEqual(payload["status"], "unknown")
        code, out, err = run_cli("mission", "reconcile", self.mission_id, *self.common())
        self.assertEqual(json.loads(out)["reconciled"], [])

    def test_supervise_refuses_a_tampered_chain_with_a_fixed_code(self) -> None:
        import sqlite3

        with sqlite3.connect(self.store_path) as raw:
            changed = raw.execute(
                "UPDATE mission_events SET event_json = replace(event_json, '\"status\":\"active\"',"
                " '\"status\":\"paused\"') WHERE sequence = 2"
            ).rowcount
        self.assertEqual(changed, 1)
        self.assertFalse(self.status()["auditChainValid"], "the tamper really broke the chain")
        code, out, err = run_cli("mission", "supervise", self.mission_id, *self.common(), *self.fake_bins())
        self.assertEqual(code, READINESS_BLOCKED)
        self.assertEqual(json.loads(err)["code"], "MISSION_SUPERVISOR_REFUSED")
        self.assertEqual(self.fakes.claude_calls(), [])

    def test_detach_refuses_a_mission_that_is_not_active(self) -> None:
        with MissionStore(self.store_path) as store:
            store.pause(self.mission_id)
        code, out, err = run_cli(
            "mission", "supervise", self.mission_id, "--detach", *self.common(), *self.fake_bins()
        )
        self.assertEqual(code, READINESS_BLOCKED)
        self.assertEqual(json.loads(err)["code"], "MISSION_STATE_CONFLICT")
        self.assertFalse((self.home / self.mission_id / "supervisor.pid").exists())

    def test_detach_writes_pid_status_reports_alive_then_false_after_cancel(self) -> None:
        self.fakes.scenario(worker=[{"sleep": 60, "on_sigterm": "exit"}])
        env = dict(os.environ, PYTHONPATH=str(REPOSITORY_ROOT / "src"), PYTHONDONTWRITEBYTECODE="1")
        completed = subprocess.run(
            [sys.executable, "-B", "-m", "pipe_venture_builder", "mission", "supervise", self.mission_id,
             "--detach", *self.common(), *self.fake_bins()],
            capture_output=True, text=True, env=env, timeout=60, check=False,
        )
        self.assertEqual(completed.returncode, SUCCESS, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["detached"])
        pid = payload["pid"]
        pid_file = self.home / self.mission_id / "supervisor.pid"
        log_file = self.home / self.mission_id / "supervisor.log"
        try:
            self.assertEqual(Path(payload["pidFile"]).resolve(), pid_file.resolve())
            self.assertEqual(Path(payload["log"]).resolve(), log_file.resolve())
            self.assertEqual(pid_file.read_text(encoding="utf-8").strip(), str(pid))
            self.assertTrue(wait_until(lambda: self.status()["supervisor"].get("alive") is True))
            self.assertTrue(wait_until(lambda: bool(self.fakes.claude_calls())), "the worker was dispatched")

            code, out, err = run_cli(
                "mission", "cancel", self.mission_id, "--store", str(self.store_path), "--json"
            )
            self.assertEqual(code, SUCCESS, err)
            self.assertTrue(
                wait_until(lambda: self.status()["supervisor"].get("alive") is False, timeout=20),
                "the detached supervisor exits after cancel",
            )
        finally:
            for leftover in (pid, _read_pid(self.home / self.mission_id / "worker.pid")):
                if leftover:
                    try:
                        os.kill(leftover, 9)
                    except ProcessLookupError:
                        pass
        status = self.status()
        self.assertEqual(status["status"], "cancelled")
        self.assertEqual(status["supervisor"], {"alive": False, "pid": pid})
        with MissionStore(self.store_path) as store:
            events = [event["eventType"] for event in store.list_events(self.mission_id)]
            [run] = store.list_runs(self.mission_id)
        self.assertEqual(run["status"], "interrupted")
        self.assertLess(events.index("mission.cancelled"), events.index("run.interrupted"))
        log = log_file.read_text(encoding="utf-8")
        self.assertIn("supervise.start", log)
        self.assertIn("supervise.end", log)
        self.assertEqual(len(self.fakes.claude_calls()), 1, "nothing new after cancel")
