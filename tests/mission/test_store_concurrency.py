"""Follow-up A7 (PIP-901 review): state is read inside the write transaction.

Supervisor and CLI are two processes on the same SQLite file. A mutating
method must take the write lock (``BEGIN IMMEDIATE``) *before* it reads the
state it validates, otherwise ``open_run`` can read ``active``, a concurrent
``pause`` commits, and the run is inserted on a paused mission.
"""

from __future__ import annotations

import threading
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.control_plane.model import ControlPlaneStateError
from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.store import MissionStore
from tests.mission.helpers import CREATED_AT, LATER, mission_input


def _pause_from_another_connection(path: Path, mission_id: str, outcome: dict) -> None:
    try:
        with MissionStore(path) as other:
            other.pause(mission_id, at=LATER)
        outcome["paused"] = True
    except Exception as exc:  # pragma: no cover - reported through the dict
        outcome["error"] = repr(exc)


class WriteTransactionIsolationTests(TestCase):
    def test_open_run_and_concurrent_pause_serialize_through_the_write_lock(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mission.sqlite3"
            with MissionStore(path) as store:
                mission_id = store.create(build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT)
                store.activate(mission_id, at=LATER)

            outcome: dict = {}
            pauser = threading.Thread(target=_pause_from_another_connection, args=(path, mission_id, outcome))
            with MissionStore(path) as supervisor:
                original = supervisor._mission_row
                calls = {"n": 0}

                def racing_read(mission: str):
                    # Right after the first state read inside ``open_run``, the
                    # founder's ``pause`` races it from a second connection.
                    row = original(mission)
                    calls["n"] += 1
                    if calls["n"] == 1:
                        pauser.start()
                        pauser.join(timeout=0.5)
                    return row

                supervisor._mission_row = racing_read  # type: ignore[method-assign]
                try:
                    run_id = supervisor.open_run(mission_id, cycle=1, attempt=1, executor="worker", at=LATER)
                except ControlPlaneStateError:
                    run_id = None
                supervisor._mission_row = original  # type: ignore[method-assign]
            pauser.join(timeout=10)
            self.assertNotIn("error", outcome)
            self.assertTrue(outcome.get("paused"))

            with MissionStore(path) as store:
                events = [event["eventType"] for event in store.list_events(mission_id)]
                self.assertTrue(store.verify_chain(mission_id))
                self.assertEqual(store.get(mission_id)["status"], "paused")
            self.assertIn("mission.paused", events)
            if run_id is not None:
                self.assertLess(
                    events.index("run.dispatched"),
                    events.index("mission.paused"),
                    "a run must never be dispatched after the mission was paused",
                )
            else:
                self.assertNotIn("run.dispatched", events)

    def test_resume_rereads_pending_decisions_inside_the_transaction(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mission.sqlite3"
            with MissionStore(path) as store:
                mission_id = store.create(build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT)
                store.activate(mission_id, at=LATER)
                store.block(mission_id, reason_code="review_blocked", at=LATER)
                decision = store.open_decision(
                    mission_id, kind="escalation", context={"cycle": 1}, options=["stop", "grant_cycle"],
                    safe_default="stop", blocked_scope="cycles", deadline=None, at=LATER,
                )
                store.resolve_decision(decision, option="grant_cycle", decided_by="human:cli:vitor", at=LATER)

            outcome: dict = {}

            def open_decision_elsewhere() -> None:
                try:
                    with MissionStore(path) as other:
                        other.open_decision(
                            mission_id, kind="escalation", context={"cycle": 2}, options=["stop", "grant_cycle"],
                            safe_default="stop", blocked_scope="cycles", deadline=None, at=LATER,
                        )
                    outcome["opened"] = True
                except Exception as exc:  # pragma: no cover
                    outcome["error"] = repr(exc)

            racer = threading.Thread(target=open_decision_elsewhere)
            with MissionStore(path) as founder:
                original = founder.pending_decisions
                calls = {"n": 0}

                def racing_pending(mission: str):
                    pending = original(mission)
                    calls["n"] += 1
                    if calls["n"] == 1:
                        racer.start()
                        racer.join(timeout=0.5)
                    return pending

                founder.pending_decisions = racing_pending  # type: ignore[method-assign]
                try:
                    founder.resume(mission_id, at=LATER)
                    resumed = True
                except ControlPlaneStateError:
                    resumed = False
            racer.join(timeout=10)
            self.assertTrue(outcome.get("opened"), outcome)
            self.assertTrue(resumed)
            with MissionStore(path) as store:
                events = [event["eventType"] for event in store.list_events(mission_id)]
                self.assertTrue(store.verify_chain(mission_id))
            last_opened = len(events) - 1 - events[::-1].index("decision.opened")
            self.assertLess(
                events.index("mission.resumed"),
                last_opened,
                "resume must not commit after a decision it did not see was opened",
            )
