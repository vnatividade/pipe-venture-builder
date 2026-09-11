from __future__ import annotations

from unittest import TestCase

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
)
from pipe_venture_builder.mission.contract import build_mission, is_human_source
from pipe_venture_builder.mission.store import MissionStore
from tests.mission.helpers import CREATED_AT, EVEN_LATER, LATER, mission_input

FP = "sha256:" + "c" * 64


def active_mission(store: MissionStore) -> str:
    mission_id = store.create(build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT)
    store.activate(mission_id, at=LATER)
    return mission_id


def open_default_decision(store: MissionStore, mission_id: str, **overrides) -> str:
    kwargs = dict(
        kind="out_of_mission",
        context={"runId": "MRUN-000000000001", "cycle": 2, "verdict": "out_of_mission"},
        options=["pause", "continue", "cancel"],
        safe_default="pause",
        blocked_scope="mission",
        deadline=None,
        at=LATER,
    )
    kwargs.update(overrides)
    return store.open_decision(mission_id, **kwargs)


class DecisionTests(TestCase):
    def test_open_and_list_pending_decisions(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = open_default_decision(store, mission_id, deadline=EVEN_LATER)
            self.assertRegex(decision_id, r"^DEC-[a-f0-9]{12}$")
            pending = store.pending_decisions(mission_id)
            self.assertEqual(len(pending), 1)
            decision = pending[0]
            self.assertEqual(decision["status"], "pending")
            self.assertEqual(decision["context"]["cycle"], 2)
            self.assertEqual(decision["options"], ["pause", "continue", "cancel"])
            self.assertEqual(decision["safeDefault"], "pause")
            self.assertEqual(decision["blockedScope"], "mission")
            self.assertEqual(decision["deadline"], EVEN_LATER)
            self.assertEqual(store.list_events(mission_id)[-1]["eventType"], "decision.opened")
            self.assertEqual(
                open_default_decision(store, mission_id, deadline=EVEN_LATER, at=EVEN_LATER),
                decision_id,
                "same pending decision must not be duplicated",
            )
            self.assertEqual(len(store.pending_decisions(mission_id)), 1)

    def test_open_decision_validates_shape(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            bad = {
                "kind": {"kind": "vibes"},
                "one option": {"options": ["pause"], "safe_default": "pause"},
                "default outside options": {"safe_default": "explode"},
                "free text context": {"context": {"note": "free text here"}},
                "secret context": {"context": {"ref": "sk-never-persist-this-value-1234567890"}},
                "bad deadline": {"deadline": "tomorrow"},
                "free text scope": {"blocked_scope": "the whole thing"},
            }
            for label, override in bad.items():
                with self.subTest(label):
                    with self.assertRaises(ControlPlaneContractError):
                        open_default_decision(store, mission_id, **override)
            self.assertEqual(store.pending_decisions(mission_id), [])
            self.assertEqual(len(store.list_events(mission_id)), 2)

    def test_decision_requires_live_mission(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = store.create(
                build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT
            )
            with self.assertRaises(ControlPlaneStateError):
                open_default_decision(store, mission_id)

    def test_resolve_decision_by_human_source(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = open_default_decision(store, mission_id)
            resolved = store.resolve_decision(
                decision_id, option="continue", decided_by="human:chat:vitor", at=EVEN_LATER
            )
            self.assertEqual(resolved["status"], "resolved")
            self.assertEqual(resolved["decidedOption"], "continue")
            self.assertEqual(resolved["decidedBy"], "human:chat:vitor")
            self.assertEqual(resolved["decidedAt"], EVEN_LATER)
            self.assertEqual(store.pending_decisions(mission_id), [])
            self.assertEqual(store.list_events(mission_id)[-1]["eventType"], "decision.resolved")
            with self.assertRaises(ControlPlaneStateError):
                store.resolve_decision(
                    decision_id, option="pause", decided_by="human:chat:vitor", at=EVEN_LATER
                )

    def test_decision_from_agent_source_is_refused(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = open_default_decision(store, mission_id)
            for source in (
                "agent:claude-code:worker",
                "supervisor",
                "human:",
                "human:chat:",
                "human:slack:vitor",
                "",
                "human:chat:vitor with spaces",
            ):
                with self.subTest(source):
                    self.assertFalse(is_human_source(source))
                    with self.assertRaises(ControlPlaneContractError):
                        store.resolve_decision(
                            decision_id, option="pause", decided_by=source, at=EVEN_LATER
                        )
            with self.assertRaises(ControlPlaneContractError):
                store.resolve_decision(
                    decision_id, option="explode", decided_by="human:cli:vitor", at=EVEN_LATER
                )
            self.assertEqual(store.get_decision(decision_id)["status"], "pending")
            for source in ("human:chat:vitor", "human:linear:PIP-901", "human:cli:vitor"):
                self.assertTrue(is_human_source(source))

    def test_blocked_mission_resumes_only_after_decisions_resolve(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            decision_id = open_default_decision(store, mission_id)
            store.block(mission_id, reason_code="out_of_mission", at=LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.resume(mission_id, at=EVEN_LATER)
            store.resolve_decision(
                decision_id, option="continue", decided_by="human:cli:vitor", at=EVEN_LATER
            )
            store.resume(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")


class EvidenceAndCompletionTests(TestCase):
    def _satisfy_all(self, store: MissionStore, mission_id: str, run_id: str) -> None:
        for criterion in store.get(mission_id)["successCriteria"]:
            store.record_evidence(
                mission_id,
                criterion_id=criterion["id"],
                run_id=run_id,
                satisfied=True,
                evidence_ref=f"evidence:{criterion['id']}",
                evidence_fingerprint=FP,
                at=EVEN_LATER,
            )

    def _delivered(self, store: MissionStore, mission_id: str) -> None:
        store.record_delivery(mission_id, event_type="delivery.pr_opened", ref="pr:1", at=EVEN_LATER)
        store.record_delivery(
            mission_id, event_type="delivery.checks_passed", ref="pr:1", at=EVEN_LATER
        )

    def test_complete_without_full_evidence_is_refused(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self._delivered(store, mission_id)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.record_evidence(
                mission_id, criterion_id="C1", run_id=run_id, satisfied=True,
                evidence_ref="evidence:C1", evidence_fingerprint=FP, at=EVEN_LATER,
            )
            store.record_evidence(
                mission_id, criterion_id="C2", run_id=run_id, satisfied=True,
                evidence_ref="evidence:C2", evidence_fingerprint=FP, at=EVEN_LATER,
            )
            store.record_evidence(
                mission_id, criterion_id="C3", run_id=run_id, satisfied=False,
                evidence_ref=None, evidence_fingerprint=None, at=EVEN_LATER,
            )
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")
            self.assertNotIn(
                "mission.completed",
                [event["eventType"] for event in store.list_events(mission_id)],
            )
            status = [item["satisfied"] for item in store.criteria_status(mission_id)]
            self.assertEqual(status, [True, True, False])

    def test_latest_evidence_wins_and_complete_succeeds(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            store.record_evidence(
                mission_id, criterion_id="C1", run_id=run_id, satisfied=False,
                evidence_ref=None, evidence_fingerprint=None, at=LATER,
            )
            self._satisfy_all(store, mission_id, run_id)
            self._delivered(store, mission_id)
            store.complete(mission_id, at=EVEN_LATER)
            document = store.get(mission_id)
            self.assertEqual(document["status"], "completed")
            last = store.list_events(mission_id)[-1]
            self.assertEqual(last["eventType"], "mission.completed")
            self.assertEqual(last["payload"]["criteria"], 3)
            self.assertTrue(store.verify_chain(mission_id))

    def test_complete_requires_delivery_when_pull_request_declared(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            run_id = store.open_run(mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER)
            self._satisfy_all(store, mission_id, run_id)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.record_delivery(mission_id, event_type="delivery.pr_opened", ref="pr:1", at=EVEN_LATER)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.record_delivery(
                mission_id, event_type="delivery.checks_failed", ref="pr:1", at=EVEN_LATER
            )
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.record_delivery(
                mission_id, event_type="delivery.checks_passed", ref="pr:1", at=EVEN_LATER
            )
            store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "completed")

    def test_complete_without_delivery_requirement(self) -> None:
        draft = mission_input()
        draft["delivery"] = {"kind": "none", "requireChecks": False}
        with MissionStore(":memory:") as store:
            mission_id = store.create(build_mission(draft, created_at=CREATED_AT), at=CREATED_AT)
            store.activate(mission_id, at=LATER)
            self._satisfy_all(store, mission_id, None)
            store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "completed")

    def test_complete_refuses_pending_decisions_and_broken_chain(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            self._satisfy_all(store, mission_id, None)
            self._delivered(store, mission_id)
            decision_id = open_default_decision(store, mission_id)
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            store.resolve_decision(
                decision_id, option="continue", decided_by="human:chat:vitor", at=EVEN_LATER
            )
            store._connection.execute(
                "UPDATE mission_events SET event_hash = 'sha256:' || substr('f' || event_hash, 1, 64)"
                " WHERE mission_id = ? AND sequence = 1",
                (mission_id,),
            )
            store._connection.commit()
            self.assertFalse(store.verify_chain(mission_id))
            with self.assertRaises(ControlPlaneStateError):
                store.complete(mission_id, at=EVEN_LATER)
            self.assertEqual(store.get(mission_id)["status"], "active")

    def test_evidence_validates_criterion_run_and_shape(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = active_mission(store)
            other = store.create(
                build_mission({**mission_input(), "title": "outra"}, created_at=CREATED_AT),
                at=CREATED_AT,
            )
            store.activate(other, at=LATER)
            other_run = store.open_run(other, cycle=1, attempt=1, executor="claude-code", at=LATER)
            base = dict(
                criterion_id="C1", run_id=None, satisfied=True,
                evidence_ref="evidence:C1", evidence_fingerprint=FP, at=LATER,
            )
            with self.assertRaises(ControlPlaneContractError):
                store.record_evidence(mission_id, **{**base, "criterion_id": "C9"})
            with self.assertRaises(ControlPlaneContractError):
                store.record_evidence(mission_id, **{**base, "satisfied": "yes"})
            with self.assertRaises(ControlPlaneContractError):
                store.record_evidence(mission_id, **{**base, "evidence_ref": "has spaces"})
            with self.assertRaises(ControlPlaneContractError):
                store.record_evidence(mission_id, **{**base, "evidence_fingerprint": "nope"})
            with self.assertRaises(ControlPlaneStateError):
                store.record_evidence(mission_id, **{**base, "run_id": other_run})
            self.assertEqual(
                [item["satisfied"] for item in store.criteria_status(mission_id)],
                [False, False, False],
            )
