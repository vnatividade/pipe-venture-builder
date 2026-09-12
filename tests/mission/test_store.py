from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
)
from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.events import EVENT_TYPES, verify_mission_event
from pipe_venture_builder.mission.store import DATABASE_SCHEMA_VERSION, MissionStore
from tests.mission.helpers import CREATED_AT, EVEN_LATER, LATER, mission_input


def new_store() -> MissionStore:
    return MissionStore(":memory:")


def created(store: MissionStore) -> str:
    return store.create(build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT)


class MissionStoreLifecycleTests(TestCase):
    def test_create_persists_document_and_first_event(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            document = store.get(mission_id)
            self.assertEqual(document["status"], "draft")
            events = store.list_events(mission_id)
            self.assertEqual([event["eventType"] for event in events], ["mission.created"])
            self.assertEqual(events[0]["payload"]["fingerprint"], document["fingerprint"])
            self.assertTrue(store.verify_chain(mission_id))

    def test_create_is_idempotent_for_identical_content_only(self) -> None:
        mission = build_mission(mission_input(), created_at=CREATED_AT)
        with new_store() as store:
            first = store.create(mission, at=CREATED_AT)
            self.assertEqual(store.create(mission, at=LATER), first)
            self.assertEqual(len(store.list_events(first)), 1)
            altered = build_mission(
                {**mission_input(), "missionId": mission["missionId"], "title": "outro"},
                created_at=CREATED_AT,
            )
            with self.assertRaises(ControlPlaneStateError):
                store.create(altered, at=LATER)

    def test_create_rejects_non_draft_and_unsafe_documents(self) -> None:
        mission = build_mission(mission_input(), created_at=CREATED_AT)
        with new_store() as store:
            with self.assertRaises(ControlPlaneContractError):
                store.create(dict(mission, status="active"), at=CREATED_AT)
            with self.assertRaises(ControlPlaneContractError):
                store.create(dict(mission, title="x"), at=CREATED_AT)
            self.assertEqual(store.list_missions(), [])

    def test_allowed_transitions_emit_events_and_update_status(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")
            store.pause(mission_id, at=LATER)
            self.assertEqual(store.get(mission_id)["status"], "paused")
            store.resume(mission_id, at=LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")
            store.block(mission_id, reason_code="review_blocked", at=LATER)
            self.assertEqual(store.get(mission_id)["status"], "blocked")
            store.resume(mission_id, at=LATER)
            store.cancel(mission_id, at=EVEN_LATER)
            document = store.get(mission_id)
            self.assertEqual(document["status"], "cancelled")
            self.assertEqual(document["updatedAt"], EVEN_LATER)
            self.assertEqual(
                [event["eventType"] for event in store.list_events(mission_id)],
                [
                    "mission.created",
                    "mission.activated",
                    "mission.paused",
                    "mission.resumed",
                    "mission.blocked",
                    "mission.resumed",
                    "mission.cancelled",
                ],
            )
            self.assertTrue(store.verify_chain(mission_id))

    def test_blocked_mission_can_be_cancelled(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            store.open_decision(
                mission_id,
                kind="out_of_mission",
                context={"runId": "MRUN-000000000001", "cycle": 1},
                options=["pause", "continue", "cancel"],
                safe_default="pause",
                blocked_scope="mission",
                deadline=None,
                at=LATER,
            )
            store.block(mission_id, reason_code="out_of_mission", at=LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.pause(mission_id, at=EVEN_LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.resume(mission_id, at=EVEN_LATER)
            store.cancel(mission_id, at=EVEN_LATER)
            document = store.get(mission_id)
            self.assertEqual(document["status"], "cancelled")
            self.assertEqual(document["updatedAt"], EVEN_LATER)
            self.assertEqual(
                [event["eventType"] for event in store.list_events(mission_id)][-2:],
                ["mission.blocked", "mission.cancelled"],
            )
            self.assertTrue(store.verify_chain(mission_id))

    def test_budget_block_emits_budget_reached_before_blocked(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            store.block(mission_id, reason_code="budget_reached", at=LATER)
            self.assertEqual(
                [event["eventType"] for event in store.list_events(mission_id)][-2:],
                ["budget.reached", "mission.blocked"],
            )
            with self.assertRaises(ControlPlaneContractError):
                store.block(mission_id, reason_code="because I said so", at=LATER)

    def test_invalid_transition_is_refused_and_nothing_is_persisted(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            before_events = store.list_events(mission_id)
            for action in ("pause", "resume", "cancel", "complete"):
                with self.subTest(action):
                    with self.assertRaises(ControlPlaneStateError):
                        getattr(store, action)(mission_id, at=LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.block(mission_id, reason_code="review_blocked", at=LATER)
            self.assertEqual(store.get(mission_id)["status"], "draft")
            self.assertEqual(store.list_events(mission_id), before_events)

            store.activate(mission_id, at=LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.activate(mission_id, at=LATER)
            store.cancel(mission_id, at=LATER)
            count = len(store.list_events(mission_id))
            for action in ("activate", "pause", "resume", "cancel", "complete"):
                with self.subTest(f"terminal {action}"):
                    with self.assertRaises(ControlPlaneStateError):
                        getattr(store, action)(mission_id, at=EVEN_LATER)
            self.assertEqual(len(store.list_events(mission_id)), count)
            self.assertEqual(store.get(mission_id)["status"], "cancelled")

    def test_unknown_is_reachable_only_through_reconciliation(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            with self.assertRaises(ControlPlaneStateError):
                store.mark_unknown(mission_id, at=LATER)
            store.activate(mission_id, at=LATER)
            store.mark_unknown(mission_id, at=LATER)
            self.assertEqual(store.get(mission_id)["status"], "unknown")
            self.assertEqual(store.list_events(mission_id)[-1]["eventType"], "mission.unknown")
            with self.assertRaises(ControlPlaneStateError):
                store.activate(mission_id, at=EVEN_LATER)

    def test_unknown_mission_id_raises_state_error(self) -> None:
        with new_store() as store:
            with self.assertRaises(ControlPlaneStateError):
                store.get("MSN-aaaaaaaaaaaa")
            with self.assertRaises(ControlPlaneStateError):
                store.activate("MSN-aaaaaaaaaaaa", at=LATER)
            with self.assertRaises(ControlPlaneContractError):
                store.get("not an id")


class LegacyV010DocumentCompatibilityTests(TestCase):
    """PIP-903 review finding #1: ``validate_mission`` started requiring the
    ``delegation`` key, so every already-stored v0.1.0 mission (which never
    had it) failed every transition (``_apply_status`` revalidates). These
    exercise the real ``MissionStore`` the way the review's repro did."""

    def test_v0_1_0_document_without_delegation_resumes_and_cancels(self) -> None:
        with new_store() as store:
            mission = build_mission(mission_input(), created_at=CREATED_AT)
            self.assertNotIn("delegation", mission, "v0.1.0 documents never carry the key")
            mission_id = store.create(mission, at=CREATED_AT)
            store.activate(mission_id, at=LATER)
            self.assertNotIn("delegation", store.get(mission_id))
            store.pause(mission_id, at=LATER)
            store.resume(mission_id, at=LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")
            store.block(mission_id, reason_code="review_blocked", at=LATER)
            store.resume(mission_id, at=LATER)
            self.assertNotIn("delegation", store.get(mission_id))
            store.cancel(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "cancelled")

    def test_v0_1_0_missionId_is_stable_across_recreating_the_same_draft(self) -> None:
        # A mutation that put ``delegation`` back into the fingerprint (via an
        # unconditional ``setdefault``) would change this id: the same JSON
        # would stop resolving to the mission already on disk.
        with new_store() as first_store:
            first_id = first_store.create(
                build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT
            )
        with new_store() as second_store:
            second_id = second_store.create(
                build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT
            )
        self.assertEqual(first_id, second_id)


class MissionEventChainTests(TestCase):
    def test_event_allowlist_is_fixed(self) -> None:
        self.assertEqual(
            EVENT_TYPES,
            frozenset(
                {
                    "mission.created",
                    "mission.activated",
                    "mission.paused",
                    "mission.resumed",
                    "mission.cancelled",
                    "mission.blocked",
                    "mission.completed",
                    "mission.unknown",
                    "run.dispatched",
                    "run.collected",
                    "run.interrupted",
                    "run.failed",
                    "run.unknown",
                    "verify.passed",
                    "verify.failed",
                    "review.satisfied",
                    "review.needs_revision",
                    "review.out_of_mission",
                    "review.blocked",
                    "decision.opened",
                    "decision.resolved",
                    "decision.delegated",
                    "delivery.pr_opened",
                    "delivery.checks_passed",
                    "delivery.checks_failed",
                    "budget.reached",
                }
            ),
        )

    def test_event_payload_refuses_free_text_and_secrets(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            for payload in (
                {"note": "this is free text with spaces"},
                {"token": "abc"},
                {"ref": "sk-never-persist-this-value-1234567890"},
                {"nested": {"too": "deep"}},
            ):
                with self.subTest(str(sorted(payload))):
                    with self.assertRaises(ControlPlaneContractError):
                        store.record_verification(run_id, passed=True, at=LATER, extra=payload)
            with self.assertRaises(ControlPlaneContractError):
                store.record_verification(run_id, passed=True, at=LATER, extra={"kind": "x"}, event_type="not.allowed")

    def test_tampered_chain_is_detected(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mission.sqlite3"
            with MissionStore(path) as store:
                mission_id = created(store)
                store.activate(mission_id, at=LATER)
                store.pause(mission_id, at=LATER)
                self.assertTrue(store.verify_chain(mission_id))
            connection = sqlite3.connect(path)
            event = json.loads(
                connection.execute(
                    "SELECT event_json FROM mission_events WHERE mission_id = ? AND sequence = 2",
                    (mission_id,),
                ).fetchone()[0]
            )
            event["eventType"] = "mission.cancelled"
            connection.execute(
                "UPDATE mission_events SET event_json = ? WHERE mission_id = ? AND sequence = 2",
                (json.dumps(event), mission_id),
            )
            connection.commit()
            connection.close()
            with MissionStore(path) as store:
                self.assertFalse(store.verify_chain(mission_id))

    def test_deleted_event_breaks_chain(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mission.sqlite3"
            with MissionStore(path) as store:
                mission_id = created(store)
                store.activate(mission_id, at=LATER)
                store.pause(mission_id, at=LATER)
            connection = sqlite3.connect(path)
            connection.execute(
                "DELETE FROM mission_events WHERE mission_id = ? AND sequence = 2", (mission_id,)
            )
            connection.commit()
            connection.close()
            with MissionStore(path) as store:
                self.assertFalse(store.verify_chain(mission_id))

    def test_verify_mission_event_checks_previous_hash_link(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            first, second = store.list_events(mission_id)
            self.assertTrue(verify_mission_event(first, None))
            self.assertTrue(verify_mission_event(second, first["eventHash"]))
            self.assertFalse(verify_mission_event(second, None))
            self.assertRegex(second["eventId"], r"^MEV-[a-f0-9]{12}$")


class MissionStoreDurabilityTests(TestCase):
    def test_state_survives_reopen_and_files_are_private(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "mission.sqlite3"
            with MissionStore(path) as store:
                mission_id = created(store)
                store.activate(mission_id, at=LATER)
                for suffix in ("", "-wal", "-shm"):
                    sidecar = Path(f"{path}{suffix}")
                    if sidecar.exists():
                        self.assertEqual(os.stat(sidecar).st_mode & 0o777, 0o600)
            with MissionStore(path) as reopened:
                self.assertEqual(reopened.get(mission_id)["status"], "active")
                self.assertEqual(len(reopened.list_events(mission_id)), 2)
                self.assertTrue(reopened.verify_chain(mission_id))
                self.assertEqual(reopened.schema_version, DATABASE_SCHEMA_VERSION)

    def test_symlink_database_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.sqlite3"
            target.touch()
            link = root / "mission.sqlite3"
            link.symlink_to(target)
            with self.assertRaises(ControlPlaneStateError):
                MissionStore(link)

    def test_default_path_lives_under_pipe_mission(self) -> None:
        self.assertTrue(str(MissionStore.default_path()).endswith("/.pipe/mission/mission.sqlite3"))


class MissionRunTests(TestCase):
    def test_runs_require_active_mission_and_accumulate_cost(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            with self.assertRaises(ControlPlaneStateError):
                store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            store.activate(mission_id, at=LATER)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self.assertRegex(run_id, r"^MRUN-[a-f0-9]{12}$")
            with self.assertRaises(ControlPlaneStateError):
                store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self.assertEqual(store.get_run(run_id)["status"], "running")
            store.collect_run(
                run_id,
                session_id="sess-0001",
                cost_usd=0.75,
                num_turns=12,
                result_ref="result:sess-0001",
                result_fingerprint="sha256:" + "a" * 64,
                status="collected",
                at=EVEN_LATER,
            )
            with self.assertRaises(ControlPlaneStateError):
                store.collect_run(
                    run_id, session_id=None, cost_usd=0, num_turns=0,
                    result_ref=None, result_fingerprint=None, status="failed", at=EVEN_LATER,
                )
            second = store.open_run(mission_id, cycle=1, attempt=2, executor="claude-code", at=EVEN_LATER)
            store.collect_run(
                second, session_id=None, cost_usd=0.25, num_turns=0,
                result_ref=None, result_fingerprint=None, status="failed", at=EVEN_LATER,
            )
            self.assertAlmostEqual(store.total_cost_usd(mission_id), 1.0)
            self.assertEqual(
                [event["eventType"] for event in store.list_events(mission_id)][-4:],
                ["run.dispatched", "run.collected", "run.dispatched", "run.failed"],
            )
            self.assertEqual(store.run_counts(mission_id), {"collected": 1, "failed": 1})

    def test_open_run_refused_when_mission_paused(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            store.pause(mission_id, at=LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self.assertNotIn(
                "run.dispatched",
                [event["eventType"] for event in store.list_events(mission_id)],
            )
            store.resume(mission_id, at=LATER)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self.assertEqual(store.get_run(run_id)["status"], "running")
            store.block(mission_id, reason_code="review_blocked", at=EVEN_LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.open_run(mission_id, cycle=1, attempt=2, executor="claude-code", at=EVEN_LATER)

    def test_collect_run_validates_inputs(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            bad = {
                "status": {"status": "done"},
                "cost": {"cost_usd": -1},
                "cost type": {"cost_usd": "1"},
                "turns": {"num_turns": -1},
                "session": {"session_id": "has spaces"},
                "fingerprint": {"result_fingerprint": "sha1:abc"},
            }
            for label, override in bad.items():
                with self.subTest(label):
                    kwargs = dict(
                        session_id="s1", cost_usd=0.1, num_turns=1, result_ref="r1",
                        result_fingerprint="sha256:" + "b" * 64, status="collected", at=LATER,
                    )
                    kwargs.update(override)
                    with self.assertRaises(ControlPlaneContractError):
                        store.collect_run(run_id, **kwargs)
            self.assertEqual(store.get_run(run_id)["status"], "running")
            with self.assertRaises(ControlPlaneContractError):
                store.open_run(mission_id, cycle=0, attempt=1, executor="claude-code", at=LATER)

    def test_verification_and_review_verdicts_are_recorded(self) -> None:
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            store.record_verification(run_id, passed=False, at=LATER)
            store.record_verdict(run_id, verdict="needs_revision", at=LATER)
            self.assertEqual(store.get_run(run_id)["verdict"], "needs_revision")
            with self.assertRaises(ControlPlaneContractError):
                store.record_verdict(run_id, verdict="meh", at=LATER)
            self.assertEqual(
                [event["eventType"] for event in store.list_events(mission_id)][-2:],
                ["verify.failed", "review.needs_revision"],
            )

    def test_criteria_status_up_to_cycle_only_counts_evidence_from_earlier_runs(self) -> None:
        # The delegation "requireProgress" check compares a cycle's evidence
        # snapshot against the previous one; ``criteria_status`` is the only
        # place that knows how to join evidence back to the run's cycle.
        with new_store() as store:
            mission_id = created(store)
            store.activate(mission_id, at=LATER)
            first = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            store.record_evidence(
                mission_id, criterion_id="C1", run_id=first, satisfied=True,
                evidence_ref="evidence:C1", evidence_fingerprint=None, at=LATER,
            )
            second = store.open_run(mission_id, cycle=2, attempt=1, executor="claude-code", at=EVEN_LATER)
            store.record_evidence(
                mission_id, criterion_id="C2", run_id=second, satisfied=True,
                evidence_ref="evidence:C2", evidence_fingerprint=None, at=EVEN_LATER,
            )

            def satisfied_ids(up_to_cycle: int | None) -> set[str]:
                return {
                    item["id"]
                    for item in store.criteria_status(mission_id, up_to_cycle=up_to_cycle)
                    if item["satisfied"]
                }

            self.assertEqual(satisfied_ids(0), set())
            self.assertEqual(satisfied_ids(1), {"C1"})
            self.assertEqual(satisfied_ids(2), {"C1", "C2"})
            self.assertEqual(satisfied_ids(None), {"C1", "C2"}, "unset means every run, like before")
