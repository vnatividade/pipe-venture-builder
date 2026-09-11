"""Mission Loop B, slice 5: the deterministic supervisor.

Named after the failure list of the design (§5, F1–F9) plus the anti-loop
guards, delivery by PR, and the no-raw-output rule. Only the fake ``claude``
and ``gh`` in ``tests/mission/fakes/`` are executed.
"""

from __future__ import annotations

import os
import sqlite3
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import TestCase

from pipe_venture_builder.control_plane.model import ControlPlaneStateError
from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.delivery import branch_name, worktree_path
from pipe_venture_builder.mission.status import build_status
from pipe_venture_builder.mission.store import MissionStore
from pipe_venture_builder.mission.supervisor import (
    SupervisorRefusal,
    reconcile,
    run_once,
    supervise,
)
from tests.mission.loop_helpers import (
    GOOD_FILES,
    WORKER_SENTINEL,
    FakeBinaries,
    git,
    good_worker_output,
    loop_mission,
    make_repo,
    satisfied_verdict,
)

REVIEWER_SENTINEL = "SENTINEL-reviewer-instructions-that-stay-out-of-sqlite"


def needs_revision_verdict(instructions: str = "Cite o comando no guia.") -> dict[str, Any]:
    return satisfied_verdict(
        verdict="needs_revision",
        criteria=[{"id": "C3", "met": False, "evidence": "falta referencia"}],
        reasons=["rubric pendente"],
        revisionInstructions=instructions,
    )


def flags(argv: list[str]) -> dict[str, str]:
    """``--flag value`` pairs from the fake's logged argv (``-p <brief>`` first)."""

    return dict(zip(argv[2::2], argv[3::2]))


def good_worker(**extra: Any) -> dict[str, Any]:
    call = {"write_files": dict(GOOD_FILES), "worker_output": good_worker_output()}
    call.update(extra)
    return call


class Harness:
    """A repo, a file store with an active mission, a mission home, fakes."""

    def __init__(self, root: Path, *, with_origin: bool = False, **overrides: Any) -> None:
        self.root = root
        self.repo = make_repo(root, with_origin=with_origin)
        self.home = root / "home"
        self.store_path = root / "mission.sqlite3"
        self.store = MissionStore(self.store_path)
        self.mission = build_mission(loop_mission(self.repo, **overrides))
        self.mission_id = self.store.create(self.mission)
        self.store.activate(self.mission_id)
        self.fakes = FakeBinaries(root)

    def kwargs(self, **extra: Any) -> dict[str, Any]:
        options = dict(
            store=self.store,
            claude_bin=self.fakes.claude_bin,
            gh_bin=self.fakes.gh_bin,
            home=self.home,
            poll_seconds=0.05,
            checks_poll_seconds=0.01,
            checks_max_polls=20,
        )
        options.update(extra)
        return options

    def run_once(self, **extra: Any):
        return run_once(self.mission_id, **self.kwargs(**extra))

    def supervise(self, **extra: Any):
        return supervise(self.mission_id, **self.kwargs(**extra))

    def events(self) -> list[str]:
        return [event["eventType"] for event in self.store.list_events(self.mission_id)]

    def payloads(self, event_type: str) -> list[dict[str, Any]]:
        return [
            event["payload"] for event in self.store.list_events(self.mission_id)
            if event["eventType"] == event_type
        ]

    def calls(self, role: str) -> list[dict[str, Any]]:
        return [call for call in self.fakes.claude_calls() if call["role"] == role]

    def status(self) -> str:
        return self.store.get(self.mission_id)["status"]

    def close(self) -> None:
        self.store.close()


class SupervisorTestCase(TestCase):
    def setUp(self) -> None:
        self._directory = TemporaryDirectory()
        self.root = Path(self._directory.name)

    def tearDown(self) -> None:
        for harness in getattr(self, "_harnesses", []):
            harness.close()
        self._directory.cleanup()

    def harness(self, **kwargs: Any) -> Harness:
        harness = Harness(self.root, **kwargs)
        self._harnesses = getattr(self, "_harnesses", []) + [harness]
        harness.fakes.__enter__()
        self.addCleanup(harness.fakes.__exit__)
        return harness


class HappyPathTests(SupervisorTestCase):
    def test_one_cycle_verifies_reviews_and_completes_with_cost_of_worker_plus_reviewer(self) -> None:
        h = self.harness()
        h.fakes.scenario(
            worker=[good_worker(result={"total_cost_usd": 1.25})],
            reviewer=[{"structured_output": satisfied_verdict(), "result": {"total_cost_usd": 0.5}}],
        )
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("completed", "completed"))
        self.assertEqual(h.status(), "completed")
        self.assertEqual(
            h.events()[2:],
            ["run.dispatched", "run.collected", "verify.passed", "run.dispatched", "run.collected",
             "review.satisfied", "mission.completed"],
        )
        self.assertAlmostEqual(h.store.total_cost_usd(h.mission_id), 1.75)
        runs = h.store.list_runs(h.mission_id)
        self.assertEqual(sorted(run["executor"] for run in runs), ["reviewer:sonnet", "worker:sonnet"])
        self.assertTrue(all(item["satisfied"] for item in h.store.criteria_status(h.mission_id)))
        collected = h.payloads("run.collected")[0]
        self.assertEqual(collected["model"], "sonnet")
        self.assertEqual(collected["permissionDenials"], 0)
        worker_argv = h.calls("worker")[0]["argv"]
        self.assertEqual(flags(worker_argv)["--max-budget-usd"], "13.50",
                         "worker budget = mission budget minus the reviewer reserve")
        self.assertEqual(Path(h.calls("worker")[0]["cwd"]).resolve(),
                         worktree_path(h.mission_id, h.home).resolve())
        self.assertEqual(h.run_once().reason, "not_active", "a completed mission dispatches nothing")
        self.assertEqual(len(h.calls("worker")), 1)


class FailureF1WorkerWithoutJsonTests(SupervisorTestCase):
    def test_f1_worker_without_json_fails_each_cycle_then_blocks_with_decision(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[{"mode": "garbage"}, {"mode": "silent", "exit_code": 1},
                                 {"worker_output": {"summary": "no done flag"}}])
        step = h.supervise()
        self.assertEqual((step.status, step.reason), ("blocked", "run_failed"))
        runs = h.store.list_runs(h.mission_id)
        self.assertEqual([(run["cycle"], run["status"]) for run in runs],
                         [(1, "failed"), (2, "failed"), (3, "failed")])
        reasons = [payload["reason"] for payload in h.payloads("run.failed")]
        self.assertEqual(reasons, ["no_json", "no_json", "worker_output_invalid"])
        self.assertEqual(h.calls("reviewer"), [], "a failed worker never reaches the reviewer")
        self.assertEqual(h.payloads("mission.blocked")[-1]["reasonCode"], "run_failed")
        [decision] = h.store.pending_decisions(h.mission_id)
        self.assertEqual(decision["kind"], "escalation")
        self.assertEqual(decision["safeDefault"], "stop")
        second_brief = h.calls("worker")[1]["argv"][1]
        self.assertIn("Revisão anterior pediu (ciclo 1)", second_brief)
        self.assertIn("JSON", second_brief)


class FailureF2PauseDuringWorkerTests(SupervisorTestCase):
    def test_f2_pause_during_worker_sigterms_within_5s_and_dispatches_nothing_new(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[{"sleep": 30, "on_sigterm": "exit"}, good_worker()],
                         reviewer=[{"structured_output": satisfied_verdict()}])
        paused_at: dict[str, float] = {}

        def pause_from_cli() -> None:
            paused_at["t"] = time.monotonic()
            with MissionStore(h.store_path) as founder:
                founder.pause(h.mission_id)

        threading.Timer(0.4, pause_from_cli).start()
        step = h.supervise(poll_seconds=0.1)
        ended = time.monotonic()
        self.assertEqual((step.status, step.reason), ("paused", "interrupted"))
        self.assertLess(ended - paused_at["t"], 5.0, "SIGTERM within 5 s of the pause")
        [run] = h.store.list_runs(h.mission_id)
        self.assertEqual(run["status"], "interrupted")
        self.assertIn("run.interrupted", h.events())
        self.assertEqual(h.events()[-1], "run.interrupted")
        self.assertEqual(len(h.calls("worker")), 1)
        self.assertEqual(h.calls("reviewer"), [])

        self.assertEqual(h.run_once().reason, "not_active")
        self.assertEqual(len(h.calls("worker")), 1, "nothing new is dispatched while paused")

        h.store.resume(h.mission_id)
        step = h.run_once()
        self.assertEqual(step.status, "completed")
        attempts = [(run["cycle"], run["attempt"]) for run in h.store.list_runs(h.mission_id)
                    if run["executor"].startswith("worker")]
        self.assertEqual(attempts, [(1, 1), (1, 2)], "resume re-attempts the same cycle")

    def test_f2_control_without_pause_the_cycle_continues(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[good_worker(sleep=0.6)], reviewer=[{"structured_output": satisfied_verdict()}])
        step = h.supervise(poll_seconds=0.1)
        self.assertEqual(step.status, "completed")
        self.assertNotIn("run.interrupted", h.events())
        self.assertEqual(len(h.calls("reviewer")), 1)


class FailureF3OutsideWriteSetTests(SupervisorTestCase):
    def test_f3_diff_outside_write_set_needs_revision_without_calling_reviewer(self) -> None:
        h = self.harness()
        files = dict(GOOD_FILES, **{"docs/extra.md": "out of scope\n"})
        h.fakes.scenario(worker=[{"write_files": files, "worker_output": good_worker_output()}])
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("active", "outside_write_set"))
        self.assertEqual(h.calls("reviewer"), [])
        self.assertEqual(h.events()[-2:], ["verify.failed", "review.needs_revision"])
        verify = h.payloads("verify.failed")[-1]
        self.assertEqual(verify["outsideWriteSet"], 1)
        self.assertRegex(verify["diffFingerprint"], r"^sha256:")
        revision = (h.home / h.mission_id / "revisions" / "cycle-1.md").read_text(encoding="utf-8")
        self.assertIn("docs/extra.md", revision)

    def test_f3_a_committed_rename_of_a_restricted_file_is_outside_the_write_set(self) -> None:
        # A1 (review S1): the rename used to show only its destination, which
        # here is inside the write set.
        h = self.harness(workspace={"repo": str(self.root / "repo"), "baseRef": "main",
                                    "writeSet": ["README.md", "docs/"]})
        (h.repo / "AGENTS.md").write_text("rules\n" * 20, encoding="utf-8")
        git(h.repo, "add", "AGENTS.md")
        git(h.repo, "commit", "-q", "-m", "agents")
        h.fakes.scenario(
            worker=[good_worker(git_mv=["AGENTS.md", "docs/agents-moved.md"], git_commit="move")],
            reviewer=[{"structured_output": satisfied_verdict()}],
        )
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("active", "outside_write_set"))
        self.assertEqual(h.calls("reviewer"), [])
        revision = (h.home / h.mission_id / "revisions" / "cycle-1.md").read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", revision)


class FailureF4OutOfMissionTests(SupervisorTestCase):
    def test_f4_reviewer_out_of_mission_pauses_with_decision_safe_default_pause(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[good_worker()],
                         reviewer=[{"structured_output": satisfied_verdict(verdict="out_of_mission")}])
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("paused", "out_of_mission"))
        self.assertIn("review.out_of_mission", h.events())
        [decision] = h.store.pending_decisions(h.mission_id)
        self.assertEqual(decision["kind"], "out_of_mission")
        self.assertEqual(decision["safeDefault"], "pause")
        self.assertIn("pause", decision["options"])
        self.assertEqual(h.run_once().reason, "not_active")
        self.assertEqual(len(h.calls("worker")), 1)


class FailureF5ThirdNeedsRevisionTests(SupervisorTestCase):
    def test_f5_third_needs_revision_opens_decision_and_blocks(self) -> None:
        h = self.harness()
        workers = [
            good_worker(),
            {"write_files": {"README.md": "# Demo\n\npipe idea exists (v2)\n"}, "worker_output": good_worker_output()},
            {"write_files": {"README.md": "# Demo\n\npipe idea exists (v3)\n"}, "worker_output": good_worker_output()},
        ]
        h.fakes.scenario(worker=workers, reviewer=[
            {"structured_output": needs_revision_verdict(f"Primeira: {REVIEWER_SENTINEL}")},
            {"structured_output": needs_revision_verdict("Segunda revisao.")},
            {"structured_output": needs_revision_verdict("Terceira revisao.")},
        ])
        step = h.supervise()
        self.assertEqual((step.status, step.reason), ("blocked", "needs_revision_limit"))
        self.assertEqual(h.events().count("review.needs_revision"), 3)
        self.assertEqual(len(h.calls("worker")), 3)
        self.assertEqual(len(h.calls("reviewer")), 3)
        [decision] = h.store.pending_decisions(h.mission_id)
        self.assertEqual(decision["kind"], "escalation")
        self.assertEqual(set(decision["options"]), {"stop", "grant_cycle"})
        second_brief = h.calls("worker")[1]["argv"][1]
        self.assertIn(f"Primeira: {REVIEWER_SENTINEL}", second_brief, "reviewer instructions reach the next cycle")

        # A founder-granted cycle is honoured, and only one.
        h.store.resolve_decision(decision["decisionId"], option="grant_cycle", decided_by="human:cli:vitor")
        h.store.resume(h.mission_id)
        h.fakes.scenario(worker=[{"write_files": {"README.md": "# Demo\n\npipe idea exists (v4)\n"},
                                  "worker_output": good_worker_output()}],
                         reviewer=[{"structured_output": needs_revision_verdict("Quarta.")}])
        step = h.supervise()
        self.assertEqual((step.status, step.reason), ("blocked", "needs_revision_limit"))
        cycles = [run["cycle"] for run in h.store.list_runs(h.mission_id) if run["executor"].startswith("worker")]
        self.assertEqual(cycles, [1, 2, 3, 4])


class FailureF6BudgetTests(SupervisorTestCase):
    def test_f6_budget_exhausted_blocks_with_budget_reached_before_dispatch(self) -> None:
        constraints = dict(loop_mission(Path("/tmp"))["constraints"], maxBudgetUsd=4)
        h = self.harness(constraints=constraints)
        h.fakes.scenario(
            worker=[good_worker(result={"total_cost_usd": 2.0}),
                    {"write_files": {"README.md": "# Demo\n\npipe idea v2\n"}, "worker_output": good_worker_output()}],
            reviewer=[{"structured_output": needs_revision_verdict(), "result": {"total_cost_usd": 0.5}}],
        )
        step = h.supervise()
        self.assertEqual((step.status, step.reason), ("blocked", "budget_reached"))
        self.assertIn("budget.reached", h.events())
        self.assertEqual(h.events()[-3:], ["budget.reached", "mission.blocked", "decision.opened"])
        self.assertEqual(len(h.calls("worker")), 1, "no dispatch without budget for worker + reviewer")
        self.assertAlmostEqual(h.store.total_cost_usd(h.mission_id), 2.5)
        [decision] = h.store.pending_decisions(h.mission_id)
        self.assertEqual(decision["kind"], "budget")
        argv = h.calls("worker")[0]["argv"]
        self.assertEqual(flags(argv)["--max-budget-usd"], "2.50")

    def test_f6_budget_exhausted_by_the_worker_blocks_before_the_reviewer(self) -> None:
        constraints = dict(loop_mission(Path("/tmp"))["constraints"], maxBudgetUsd=4)
        h = self.harness(constraints=constraints)
        h.fakes.scenario(worker=[good_worker(result={"total_cost_usd": 3.0})])
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("blocked", "budget_reached"))
        self.assertEqual(h.calls("reviewer"), [])


class FailureF7CompleteWithoutEvidenceTests(SupervisorTestCase):
    def test_f7_reviewer_satisfied_without_rubric_evidence_does_not_complete(self) -> None:
        h = self.harness()
        verdict = satisfied_verdict(criteria=[{"id": "C1", "met": True, "evidence": "grep"}])
        h.fakes.scenario(worker=[good_worker()], reviewer=[{"structured_output": verdict}])
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("blocked", "review_blocked"))
        self.assertNotIn("mission.completed", h.events())
        self.assertIn("review.blocked", h.events())
        self.assertNotIn("review.satisfied", h.events())
        with self.assertRaises(ControlPlaneStateError):
            h.store.complete(h.mission_id)

    def test_f7_failing_check_routes_to_revision_without_reviewer_and_never_completes(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[{"write_files": {"docs/guide.md": "pipe idea\n"}, "worker_output": good_worker_output()}])
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("active", "criteria_failed"))
        self.assertEqual(h.calls("reviewer"), [])
        criteria = {item["id"]: item["satisfied"] for item in h.store.criteria_status(h.mission_id)}
        self.assertEqual(criteria, {"C1": False, "C2": True, "C3": False})
        self.assertIn("C1", (h.home / h.mission_id / "revisions" / "cycle-1.md").read_text(encoding="utf-8"))


class FailureF8OrphanRunTests(SupervisorTestCase):
    def test_f8_restart_with_orphan_running_run_marks_unknown_and_nothing_reexecutes(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[good_worker()], reviewer=[{"structured_output": satisfied_verdict()}])
        orphan = h.store.open_run(h.mission_id, cycle=1, attempt=1, executor="worker:sonnet")
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("unknown", "run_unknown"))
        self.assertEqual(h.store.get_run(orphan)["status"], "unknown")
        self.assertEqual(h.events()[-3:], ["run.unknown", "decision.opened", "mission.unknown"])
        [decision] = h.store.pending_decisions(h.mission_id)
        self.assertEqual(decision["kind"], "escalation")
        self.assertEqual(h.fakes.claude_calls(), [])
        self.assertEqual(h.run_once().reason, "not_active")
        self.assertEqual(h.supervise().reason, "not_active")
        self.assertEqual(h.fakes.claude_calls(), [], "nothing re-executes after reconciliation")

    def test_f8_reconcile_refuses_while_another_supervisor_is_alive(self) -> None:
        h = self.harness()
        orphan = h.store.open_run(h.mission_id, cycle=1, attempt=1, executor="worker:sonnet")
        pid_file = h.home / h.mission_id / "supervisor.pid"
        pid_file.parent.mkdir(parents=True)
        pid_file.write_text(f"{os.getppid()}\n", encoding="utf-8")
        with self.assertRaises(SupervisorRefusal):
            reconcile(h.mission_id, store=h.store, home=h.home)
        with self.assertRaises(SupervisorRefusal):
            h.run_once()
        self.assertEqual(h.store.get_run(orphan)["status"], "running")
        pid_file.write_text("999999\n", encoding="utf-8")
        self.assertEqual(reconcile(h.mission_id, store=h.store, home=h.home), [orphan])


class FailureF9TamperedChainTests(SupervisorTestCase):
    def test_f9_tampered_chain_supervisor_refuses_to_continue(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[good_worker()], reviewer=[{"structured_output": satisfied_verdict()}])
        before = h.events()
        with sqlite3.connect(h.store_path) as raw:
            raw.execute(
                "UPDATE mission_events SET event_json = replace(event_json, '\"version\":1', '\"version\":2')"
                " WHERE sequence = 1"
            )
        self.assertFalse(build_status(h.store, h.mission_id, home=h.home)["auditChainValid"])
        with self.assertRaises(SupervisorRefusal):
            h.run_once()
        with self.assertRaises(SupervisorRefusal):
            h.supervise()
        self.assertEqual(h.fakes.claude_calls(), [])
        self.assertEqual(h.events(), before)


class AntiLoopGuardTests(SupervisorTestCase):
    def test_circuit_breaker_same_diff_fingerprint_twice_blocks(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[
            {"write_files": {"README.md": "# Demo\n\npipe idea\n"}, "worker_output": good_worker_output()},
            {"worker_output": good_worker_output()},
        ])
        step = h.supervise()
        self.assertEqual((step.status, step.reason), ("blocked", "no_progress"))
        self.assertEqual(len(h.calls("worker")), 2)
        self.assertEqual(h.calls("reviewer"), [])
        fingerprints = [payload["diffFingerprint"] for payload in h.payloads("verify.failed")]
        self.assertEqual(len(fingerprints), 2)
        self.assertEqual(fingerprints[0], fingerprints[1])
        self.assertEqual(h.payloads("mission.blocked")[-1]["reasonCode"], "no_progress")
        [decision] = h.store.pending_decisions(h.mission_id)
        self.assertEqual(decision["kind"], "escalation")

    def test_worker_blockers_open_clarification_with_safe_default_pause(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[{"worker_output": good_worker_output(
            done=False, blockers=["preciso saber qual versao do CLI documentar"])}])
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("paused", "worker_blockers"))
        [decision] = h.store.pending_decisions(h.mission_id)
        self.assertEqual(decision["kind"], "clarification")
        self.assertEqual(decision["safeDefault"], "pause")
        self.assertEqual(h.calls("reviewer"), [])

    def test_permission_denials_route_to_needs_revision_with_instruction(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[good_worker(result={"permission_denials": [
            {"tool_name": "WebFetch", "tool_input": {"url": "https://example.invalid"}},
            {"tool_name": "Bash", "tool_input": {"command": "npm test"}}]}),
            good_worker()], reviewer=[{"structured_output": satisfied_verdict()}])
        step = h.run_once()
        self.assertEqual((step.status, step.reason), ("active", "permission_denied"))
        self.assertEqual(h.payloads("run.collected")[0]["permissionDenials"], 2)
        self.assertEqual(h.events()[-1], "review.needs_revision")
        self.assertEqual(h.calls("reviewer"), [])
        step = h.run_once()
        brief = h.calls("worker")[1]["argv"][1]
        self.assertIn("- WebFetch", brief)
        self.assertIn("- Bash(npm test)", brief, "the denied call is named, not the whole tool")
        self.assertIn("Bash(git *)", brief, "the allowed tools are listed")
        self.assertIn("negada", brief)
        self.assertEqual(step.status, "completed")


class DeliveryTests(SupervisorTestCase):
    def pr_harness(self) -> Harness:
        return self.harness(with_origin=True, delivery={"kind": "pull_request", "requireChecks": True})

    def test_pull_request_opened_once_and_completion_waits_for_green_checks(self) -> None:
        h = self.pr_harness()
        h.fakes.scenario(
            worker=[good_worker(), {"write_files": {"README.md": "# Demo\n\npipe idea and pipe adopt\n"},
                                    "worker_output": good_worker_output()}],
            reviewer=[{"structured_output": satisfied_verdict()}],
        )
        h.fakes.gh_checks([[], ["pending"], ["fail", "pass"], ["pending"], ["pass", "pass"]])
        step = h.supervise()
        self.assertEqual((step.status, step.reason), ("completed", "completed"))
        creates = [call for call in h.fakes.gh_calls() if call[:2] == ["pr", "create"]]
        self.assertEqual(len(creates), 1, "one PR per branch, across cycles")
        self.assertEqual(h.events().count("delivery.pr_opened"), 1)
        delivery = [event for event in h.events() if event.startswith("delivery.")]
        self.assertEqual(delivery, ["delivery.pr_opened", "delivery.checks_failed", "delivery.checks_passed"])
        self.assertLess(h.events().index("delivery.checks_passed"), h.events().index("mission.completed"))
        self.assertEqual(len(h.calls("worker")), 2, "failed checks send the mission to a new cycle")
        second_brief = h.calls("worker")[1]["argv"][1]
        self.assertIn("checks", second_brief)
        branch = branch_name(h.mission)
        self.assertEqual(
            git(h.repo, "ls-remote", "--heads", "origin", branch).split()[0],
            git(worktree_path(h.mission_id, h.home), "rev-parse", "HEAD").strip(),
            "the last cycle's commit was pushed to the PR branch",
        )
        self.assertEqual(git(worktree_path(h.mission_id, h.home), "status", "--porcelain"), "")

        status = build_status(h.store, h.mission_id, home=h.home)
        self.assertEqual(status["delivery"],
                         {"pullRequest": "https://github.example/owner/repo/pull/1", "checks": "passed"})

        # Restarting after completion changes nothing.
        self.assertEqual(h.supervise().reason, "not_active")
        self.assertEqual(len([c for c in h.fakes.gh_calls() if c[:2] == ["pr", "create"]]), 1)

    def test_completion_requires_green_checks_failed_at_the_last_cycle_blocks(self) -> None:
        constraints = dict(loop_mission(Path("/tmp"))["constraints"], maxCycles=1)
        h = self.harness(with_origin=True, delivery={"kind": "pull_request", "requireChecks": True},
                         constraints=constraints)
        h.fakes.scenario(worker=[good_worker()], reviewer=[{"structured_output": satisfied_verdict()}])
        h.fakes.gh_checks([["fail"]])
        step = h.supervise()
        self.assertEqual((step.status, step.reason), ("blocked", "delivery_checks_failed"))
        self.assertNotIn("mission.completed", h.events())
        with self.assertRaises(ControlPlaneStateError):
            h.store.complete(h.mission_id)

    def test_checks_that_never_report_block_after_the_polling_cap(self) -> None:
        h = self.pr_harness()
        h.fakes.scenario(worker=[good_worker()], reviewer=[{"structured_output": satisfied_verdict()}])
        h.fakes.gh_checks([["pending"]])
        step = h.supervise(checks_max_polls=3)
        self.assertEqual((step.status, step.reason), ("blocked", "delivery_checks_timeout"))
        [decision] = h.store.pending_decisions(h.mission_id)
        self.assertIn("keep_waiting", decision["options"])
        checks = [call for call in h.fakes.gh_calls() if call[:2] == ["pr", "checks"]]
        self.assertEqual(len(checks), 3)


class NoRawOutputTests(SupervisorTestCase):
    def test_no_raw_worker_or_reviewer_text_reaches_sqlite_or_the_log(self) -> None:
        h = self.harness()
        h.fakes.scenario(
            worker=[good_worker(), {"write_files": {"README.md": "# Demo\n\npipe idea v2\n"},
                                    "worker_output": good_worker_output()}],
            reviewer=[{"structured_output": needs_revision_verdict(REVIEWER_SENTINEL)},
                      {"structured_output": satisfied_verdict(reasons=[REVIEWER_SENTINEL])}],
        )
        self.assertEqual(h.supervise().status, "completed")
        h.store.close()
        blobs = b""
        for suffix in ("", "-wal", "-shm"):
            candidate = Path(f"{h.store_path}{suffix}")
            if candidate.exists():
                blobs += candidate.read_bytes()
        self.assertGreater(len(blobs), 0)
        for sentinel in (WORKER_SENTINEL, REVIEWER_SENTINEL, "Brief do worker", "grep vazio"):
            self.assertNotIn(sentinel.encode(), blobs, sentinel)
        log = (h.home / h.mission_id / "supervisor.log").read_text(encoding="utf-8")
        self.assertIn("step", log)
        self.assertNotIn(WORKER_SENTINEL, log)
        self.assertNotIn(REVIEWER_SENTINEL, log)
        h.store = MissionStore(h.store_path)


class SingleWriterTests(SupervisorTestCase):
    def test_supervise_writes_its_pid_and_refuses_a_second_live_supervisor(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[good_worker()], reviewer=[{"structured_output": satisfied_verdict()}])
        pid_file = h.home / h.mission_id / "supervisor.pid"
        pid_file.parent.mkdir(parents=True)
        pid_file.write_text(f"{os.getppid()}\n", encoding="utf-8")
        with self.assertRaises(SupervisorRefusal):
            h.supervise()
        self.assertEqual(h.fakes.claude_calls(), [])
        pid_file.unlink()
        self.assertEqual(h.supervise().status, "completed")
        self.assertEqual(pid_file.read_text(encoding="utf-8").strip(), str(os.getpid()))

    def test_active_mission_with_pending_decision_dispatches_nothing(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[good_worker()])
        h.store.open_decision(h.mission_id, kind="approval", context={"cycle": 1}, options=["yes", "no"],
                              safe_default="no", blocked_scope="mission", deadline=None)
        step = h.supervise()
        self.assertEqual((step.status, step.reason), ("active", "pending_decisions"))
        self.assertEqual(h.fakes.claude_calls(), [])


class SupervisorErrorTests(SupervisorTestCase):
    def test_a_supervisor_error_during_the_worker_terminates_it_and_fails_the_run(self) -> None:
        h = self.harness()
        h.fakes.scenario(worker=[{"sleep": 30, "on_sigterm": "exit"}])
        seen: dict[str, int] = {}
        worker_pid_file = h.home / h.mission_id / "worker.pid"
        original = h.store.get

        def flaky_get(mission_id: str):
            # Once the worker is running, the store read in the pause poll fails.
            if worker_pid_file.exists() and h.calls("worker"):
                seen["pid"] = int(worker_pid_file.read_text(encoding="utf-8"))
                raise RuntimeError("store read failed")
            return original(mission_id)

        h.store.get = flaky_get  # type: ignore[method-assign]
        started = time.monotonic()
        with self.assertRaises(RuntimeError):
            h.run_once(poll_seconds=0.05)
        h.store.get = original  # type: ignore[method-assign]
        self.assertLess(time.monotonic() - started, 10)
        [run] = h.store.list_runs(h.mission_id)
        self.assertEqual(run["status"], "failed", "no running run is left for reconciliation")
        self.assertEqual(h.payloads("run.failed")[-1]["reason"], "supervisor_error")
        self.assertFalse(worker_pid_file.exists())
        self.assertIn("pid", seen)
        with self.assertRaises(ProcessLookupError, msg="the worker process was terminated and reaped"):
            os.kill(seen["pid"], 0)


class ResumeAndSignalTests(SupervisorTestCase):
    def test_pause_during_review_resumes_with_the_review_only(self) -> None:
        h = self.harness()
        h.fakes.scenario(
            worker=[good_worker()],
            reviewer=[{"sleep": 30, "on_sigterm": "exit"}, {"structured_output": satisfied_verdict()}],
        )

        def pause_when_reviewing() -> None:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and not h.calls("reviewer"):
                time.sleep(0.02)
            with MissionStore(h.store_path) as founder:
                founder.pause(h.mission_id)

        threading.Thread(target=pause_when_reviewing).start()
        step = h.run_once(poll_seconds=0.05)
        self.assertEqual((step.status, step.reason), ("paused", "interrupted"))
        reviewer_runs = [run for run in h.store.list_runs(h.mission_id) if run["executor"].startswith("reviewer")]
        self.assertEqual([run["status"] for run in reviewer_runs], ["interrupted"])

        h.store.resume(h.mission_id)
        step = h.run_once()
        self.assertEqual(step.status, "completed")
        self.assertEqual(len(h.calls("worker")), 1, "the worker is not re-dispatched")
        self.assertEqual(len(h.calls("reviewer")), 2)
        attempts = [run["attempt"] for run in h.store.list_runs(h.mission_id) if run["executor"].startswith("reviewer")]
        self.assertEqual(sorted(attempts), [1, 2])

    def test_sigterm_to_the_supervisor_interrupts_the_worker_and_keeps_the_mission_active(self) -> None:
        import signal

        h = self.harness()
        h.fakes.scenario(worker=[{"sleep": 30, "on_sigterm": "exit"}, good_worker()],
                         reviewer=[{"structured_output": satisfied_verdict()}])
        previous = signal.getsignal(signal.SIGTERM)
        threading.Timer(0.5, os.kill, (os.getpid(), signal.SIGTERM)).start()
        started = time.monotonic()
        step = h.supervise(poll_seconds=0.05)
        self.assertLess(time.monotonic() - started, 10)
        self.assertEqual((step.status, step.reason), ("active", "interrupted"))
        self.assertEqual(signal.getsignal(signal.SIGTERM), previous, "handlers are restored")
        [run] = h.store.list_runs(h.mission_id)
        self.assertEqual(run["status"], "interrupted")
        self.assertEqual(h.run_once().status, "completed", "the mission resumes from the same cycle")
