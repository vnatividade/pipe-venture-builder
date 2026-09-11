from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.status import build_status, render_status_text
from pipe_venture_builder.mission.store import MissionStore
from tests.mission.helpers import CREATED_AT, EVEN_LATER, LATER, mission_input

FP = "sha256:" + "d" * 64


class MissionStatusTests(TestCase):
    def test_status_is_rebuilt_from_a_fresh_connection(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mission.sqlite3"
            with MissionStore(path) as store:
                mission_id = store.create(
                    build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT
                )
                store.activate(mission_id, at=LATER)
                run_id = store.open_run(
                    mission_id, cycle=1, attempt=1, executor="claude-code", at=LATER
                )
                store.collect_run(
                    run_id, session_id="sess-1", cost_usd=0.5, num_turns=7,
                    result_ref="result:sess-1", result_fingerprint=FP,
                    status="collected", at=LATER,
                )
                second = store.open_run(
                    mission_id, cycle=2, attempt=1, executor="claude-code", at=EVEN_LATER
                )
                store.record_evidence(
                    mission_id, criterion_id="C1", run_id=run_id, satisfied=True,
                    evidence_ref="evidence:C1", evidence_fingerprint=FP, at=LATER,
                )
                decision_id = store.open_decision(
                    mission_id, kind="approval",
                    context={"runId": second, "cycle": 2},
                    options=["approve", "reject"], safe_default="reject",
                    blocked_scope="delivery", deadline=None, at=EVEN_LATER,
                )
                expected = build_status(store, mission_id)

            with MissionStore(path) as reopened:
                status = build_status(reopened, mission_id)

        self.assertEqual(status, expected)
        self.assertEqual(status["missionId"], mission_id)
        self.assertEqual(status["title"], "Docs param de contradizer o codigo")
        self.assertEqual(status["status"], "active")
        self.assertEqual(status["version"], 1)
        self.assertEqual(status["cycle"], 2)
        self.assertEqual(status["attempt"], 1)
        self.assertEqual(
            status["criteria"],
            [
                {"id": "C1", "kind": "check", "satisfied": True},
                {"id": "C2", "kind": "artifact", "satisfied": False},
                {"id": "C3", "kind": "rubric", "satisfied": False},
            ],
        )
        self.assertEqual(status["pendingDecisions"][0]["decisionId"], decision_id)
        self.assertEqual(status["pendingDecisions"][0]["safeDefault"], "reject")
        self.assertAlmostEqual(status["costUsd"], 0.5)
        self.assertEqual(status["runs"], {"collected": 1, "running": 1})
        self.assertEqual(status["lastEvent"]["eventType"], "decision.opened")
        self.assertEqual(status["lastEvent"]["sequence"], 6)
        self.assertTrue(status["auditChainValid"])
        self.assertEqual(status["supervisor"], {"alive": None})
        self.assertEqual(status["sessionIds"], ["sess-1"])
        self.assertNotIn("intent", status)

    def test_status_reports_tampered_chain(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = store.create(
                build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT
            )
            store._connection.execute(
                "UPDATE mission_events SET event_json = replace(event_json, 'created', 'cancelled')"
            )
            store._connection.commit()
            status = build_status(store, mission_id)
            self.assertFalse(status["auditChainValid"])
            text = render_status_text(status)
            self.assertIn("cadeia de auditoria", text)

    def test_text_rendering_answers_the_three_questions(self) -> None:
        with MissionStore(":memory:") as store:
            mission_id = store.create(
                build_mission(mission_input(), created_at=CREATED_AT), at=CREATED_AT
            )
            text = render_status_text(build_status(store, mission_id))
            self.assertIn("Onde estamos", text)
            self.assertIn("Por quê", text)
            self.assertIn("O que depende de você", text)
            self.assertIn("nada", text)
            self.assertIn("0/3", text)

            store.activate(mission_id, at=LATER)
            store.open_decision(
                mission_id, kind="budget", context={"costUsd": 16.0},
                options=["raise_budget", "cancel"], safe_default="cancel",
                blocked_scope="mission", deadline=None, at=LATER,
            )
            store.block(mission_id, reason_code="budget_reached", at=LATER)
            text = render_status_text(build_status(store, mission_id))
            self.assertIn("blocked", text)
            self.assertIn("1 decisão pendente", text)
            self.assertIn("budget", text)
            self.assertIn("raise_budget", text)
            self.assertIn("padrão seguro: cancel", text)
            self.assertNotIn("As docs do Pipe descrevem", text)
