"""Mission Loop B: small additive store/status changes the supervisor needs."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.control_plane.model import ControlPlaneStateError
from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.status import build_status
from pipe_venture_builder.mission.store import MissionStore
from tests.mission.helpers import CREATED_AT, LATER, mission_input


def active_mission(store: MissionStore) -> str:
    mission_id = store.create(build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT)
    store.activate(mission_id, at=LATER)
    return mission_id


class BlockedCanBeCancelledTests(TestCase):
    def test_blocked_mission_can_be_cancelled(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            store.block(mission_id, reason_code="review_blocked", at=LATER)
            store.cancel(mission_id, at=LATER)
            self.assertEqual(store.get(mission_id)["status"], "cancelled")
            self.assertEqual(store.list_events(mission_id)[-1]["eventType"], "mission.cancelled")
            with self.assertRaises(ControlPlaneStateError):
                store.activate(mission_id, at=LATER)


class ReviewerRunIdentityTests(TestCase):
    def test_reviewer_run_shares_cycle_and_attempt_without_colliding(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            worker = store.open_run(mission_id, cycle=1, attempt=1, executor="worker", at=LATER)
            reviewer = store.open_run(
                mission_id, cycle=1, attempt=1, executor="reviewer", role="reviewer", at=LATER
            )
            self.assertNotEqual(worker, reviewer)
            self.assertRegex(reviewer, r"^MRUN-[a-f0-9]{12}$")
            # The default role keeps the historical identity: same inputs, same id.
            with self.assertRaises(ControlPlaneStateError):
                store.open_run(mission_id, cycle=1, attempt=1, executor="worker", role="worker", at=LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.open_run(mission_id, cycle=1, attempt=1, executor="x", role="reviewer", at=LATER)
            store.collect_run(
                reviewer, session_id="rev-1", cost_usd=0.4, num_turns=3, result_ref=None,
                result_fingerprint=None, status="collected", at=LATER,
            )
            store.collect_run(
                worker, session_id="wrk-1", cost_usd=1.0, num_turns=9, result_ref=None,
                result_fingerprint=None, status="collected", at=LATER,
            )
            self.assertAlmostEqual(store.total_cost_usd(mission_id), 1.4)
            self.assertEqual(store.get_run(reviewer)["executor"], "reviewer")


class SupervisorLivenessInStatusTests(TestCase):
    def test_status_reads_supervisor_pid_from_mission_home(self) -> None:
        with TemporaryDirectory() as directory, MissionStore(":memory:") as store:
            home = Path(directory)
            mission_id = active_mission(store)
            self.assertEqual(build_status(store, mission_id, home=home)["supervisor"], {"alive": None})

            pid_file = home / mission_id / "supervisor.pid"
            pid_file.parent.mkdir(parents=True)
            pid_file.write_text(f"{os.getpid()}\n", encoding="utf-8")
            status = build_status(store, mission_id, home=home)
            self.assertEqual(status["supervisor"], {"alive": True, "pid": os.getpid()})

            pid_file.write_text("999999\n", encoding="utf-8")
            status = build_status(store, mission_id, home=home)
            self.assertEqual(status["supervisor"], {"alive": False, "pid": 999999})

            pid_file.write_text("not-a-pid\n", encoding="utf-8")
            self.assertEqual(build_status(store, mission_id, home=home)["supervisor"], {"alive": None})


class RunPayloadExtraTests(TestCase):
    def test_collect_run_extra_adds_short_fields_but_never_overrides_fixed_ones(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="worker:sonnet", at=LATER)
            store.collect_run(
                run_id, session_id="s-1", cost_usd=0.7, num_turns=2, result_ref=None,
                result_fingerprint=None, status="failed", at=LATER,
                extra={"reason": "error_max_turns", "permissionDenials": 1, "costUsd": 999},
            )
            payload = store.list_events(mission_id)[-1]["payload"]
            self.assertEqual(payload["reason"], "error_max_turns")
            self.assertEqual(payload["permissionDenials"], 1)
            self.assertEqual(payload["costUsd"], 0.7, "the fixed field wins over extra")

    def test_collect_run_extra_refuses_free_text(self) -> None:
        from pipe_venture_builder.control_plane.model import ControlPlaneContractError

        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="worker:sonnet", at=LATER)
            with self.assertRaises(ControlPlaneContractError):
                store.collect_run(
                    run_id, session_id=None, cost_usd=0, num_turns=0, result_ref=None,
                    result_fingerprint=None, status="failed", at=LATER,
                    extra={"reason": "the worker said something long and free"},
                )
            self.assertEqual(store.get_run(run_id)["status"], "running", "nothing persisted")
