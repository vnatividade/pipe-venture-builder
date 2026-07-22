from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.adapters.hermes import (
    HermesCheckpointStore,
    HermesRuntimeAdapter,
    HermesRuntimeEvent,
)
from pipe_venture_builder.control_plane import LocalControlPlaneStore
from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
)
from tests.control_plane.helpers import approval_for, create_plan
from tests.hermes.helpers import (
    BEGIN_AT,
    EVENT_AT,
    LATER_AT,
    SESSION_ONE,
    SESSION_TWO,
    context_for,
    product_root,
)


class HermesRuntimeAdapterTests(TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root = product_root(self.base)
        self.plan = create_plan()
        self.control_path = self.base / "control-plane.sqlite3"
        self.checkpoint_path = self.base / "hermes"
        self.control = LocalControlPlaneStore(self.control_path)
        self.checkpoints = HermesCheckpointStore(self.checkpoint_path)
        self.adapter = HermesRuntimeAdapter(self.control, self.checkpoints)

    def tearDown(self) -> None:
        self.control.close()
        self.temporary.cleanup()

    def begin(self) -> dict[str, object]:
        return self.adapter.begin(
            plan=self.plan,
            context=context_for(self.root, self.plan),
            session_id=SESSION_ONE,
            external_event_id="begin-1",
            occurred_at=BEGIN_AT,
        )

    def event(
        self,
        kind: str,
        *,
        external_event_id: str,
        at: str = EVENT_AT,
        action_id: str | None = None,
        approval_id: str | None = None,
        tool_name: str | None = None,
        session_id: str = SESSION_ONE,
    ) -> HermesRuntimeEvent:
        return HermesRuntimeEvent.build(
            external_event_id=external_event_id,
            kind=kind,
            session_id=session_id,
            occurred_at=at,
            action_id=action_id,
            approval_id=approval_id,
            tool_name=tool_name,
        )

    def test_begin_binds_canonical_artifacts_and_audit(self) -> None:
        result = self.begin()

        self.assertEqual(result["state"], "running")
        self.assertEqual(result["artifactRefs"], ["README.md", "product/prd.md"])
        self.assertEqual(self.control.get_run(result["runId"])["status"], "running")
        self.assertTrue(self.control.verify_audit_chain(result["runId"]))
        events = self.control.list_events(result["runId"])
        self.assertEqual(events[-1]["eventType"], "run.resumed")
        self.assertRegex(events[-1]["references"]["idempotencyKey"], r"^HE-")

    def test_begin_retry_with_same_event_is_idempotent(self) -> None:
        first = self.begin()
        before = len(self.control.list_events(first["runId"]))
        repeated = self.begin()

        self.assertTrue(repeated["duplicate"])
        self.assertEqual(repeated["attempt"], 1)
        self.assertEqual(len(self.control.list_events(first["runId"])), before)

    def test_tool_events_map_without_raw_payload(self) -> None:
        run_id = self.begin()["runId"]
        started = self.adapter.record_event(
            run_id,
            self.event(
                "tool.started", external_event_id="tool-1", tool_name="read_file"
            ),
        )
        succeeded = self.adapter.record_event(
            run_id,
            self.event(
                "tool.succeeded",
                external_event_id="tool-2",
                tool_name="read_file",
                at=LATER_AT,
            ),
        )

        self.assertEqual(started["state"], "running")
        self.assertEqual(succeeded["state"], "running")
        encoded = json.dumps(self.control.list_events(run_id))
        self.assertNotIn("read_file", encoded)
        self.assertNotIn("payload", encoded)
        journal = self.checkpoints.load(run_id)["processedEvents"]
        self.assertEqual(journal[-1]["toolName"], "read_file")
        self.assertEqual(journal[-1]["kind"], "tool.succeeded")

    def test_runtime_failure_is_durable_and_resumable(self) -> None:
        run_id = self.begin()["runId"]
        blocked = self.adapter.record_event(
            run_id,
            self.event("runtime.unavailable", external_event_id="runtime-1"),
        )
        self.assertEqual(blocked["state"], "runtime_blocked")
        self.assertEqual(blocked["blockerCode"], "adapter_failed")
        self.assertIsNone(blocked["pendingActionId"])
        self.assertEqual(self.control.get_run(run_id)["status"], "interrupted")

        resumed = self.adapter.resume(
            run_id=run_id,
            session_id=SESSION_TWO,
            external_event_id="resume-1",
            occurred_at=LATER_AT,
        )
        self.assertEqual(resumed["state"], "running")
        self.assertEqual(resumed["attempt"], 2)
        checkpoint = self.checkpoints.load(run_id)
        self.assertEqual(checkpoint["sessionLineage"], [SESSION_ONE, SESSION_TWO])

    def test_timeout_is_a_durable_runtime_blocker(self) -> None:
        run_id = self.begin()["runId"]
        blocked = self.adapter.record_event(
            run_id,
            self.event("runtime.timeout", external_event_id="runtime-timeout-1"),
        )
        self.assertEqual(blocked["state"], "runtime_blocked")
        self.assertEqual(blocked["blockerCode"], "adapter_failed")

    def test_approval_denial_is_terminal_for_resume(self) -> None:
        run_id = self.begin()["runId"]
        action_id = self.plan["actions"][0]["actionId"]
        self.adapter.record_event(
            run_id,
            self.event(
                "approval.requested",
                external_event_id="approval-request-deny",
                action_id=action_id,
            ),
        )
        denied = self.adapter.record_event(
            run_id,
            self.event(
                "approval.denied",
                external_event_id="approval-denied-1",
                at=LATER_AT,
                action_id=action_id,
            ),
        )
        self.assertEqual(denied["state"], "approval_denied")
        self.assertEqual(denied["blockerCode"], "approval_not_granted")
        with self.assertRaises(ControlPlaneStateError):
            self.adapter.resume(
                run_id=run_id,
                session_id=SESSION_TWO,
                external_event_id="resume-after-denial",
                occurred_at="2026-07-21T13:03:00Z",
            )

    def test_hermes_approval_cannot_bypass_pipe_approval(self) -> None:
        run_id = self.begin()["runId"]
        action_id = self.plan["actions"][0]["actionId"]
        approval = approval_for(self.plan)
        granted = self.event(
            "approval.granted",
            external_event_id="approval-granted-1",
            action_id=action_id,
            approval_id=approval["approvalId"],
        )

        with self.assertRaises(ControlPlaneContractError):
            self.adapter.record_event(run_id, granted)
        with self.assertRaises(ControlPlaneStateError):
            self.adapter.grant_approval(
                run_id=run_id, event=granted, approval=approval, plan=self.plan
            )
        self.assertEqual(self.adapter.status(run_id)["state"], "running")

    def test_pipe_approval_handoff_requires_exact_action_and_records_it(self) -> None:
        run_id = self.begin()["runId"]
        action_id = self.plan["actions"][0]["actionId"]
        waiting = self.adapter.record_event(
            run_id,
            self.event(
                "approval.requested",
                external_event_id="approval-request-1",
                action_id=action_id,
            ),
        )
        self.assertEqual(waiting["pendingActionId"], action_id)
        approval = approval_for(self.plan)
        granted = self.adapter.grant_approval(
            run_id=run_id,
            event=self.event(
                "approval.granted",
                external_event_id="approval-granted-1",
                at=LATER_AT,
                action_id=action_id,
                approval_id=approval["approvalId"],
            ),
            approval=approval,
            plan=self.plan,
        )

        self.assertEqual(granted["state"], "approval_granted")
        self.assertIsNone(granted["pendingActionId"])
        event_types = [item["eventType"] for item in self.control.list_events(run_id)]
        self.assertIn("approval.recorded", event_types)
        self.assertTrue(self.control.verify_audit_chain(run_id))

    def test_wrong_action_approval_fails_closed(self) -> None:
        run_id = self.begin()["runId"]
        action_id = self.plan["actions"][0]["actionId"]
        self.adapter.record_event(
            run_id,
            self.event(
                "approval.requested",
                external_event_id="approval-request-1",
                action_id=action_id,
            ),
        )
        approval = approval_for(self.plan)
        wrong_event = self.event(
            "approval.granted",
            external_event_id="approval-granted-wrong",
            at=LATER_AT,
            action_id="RA-000000000000",
            approval_id=approval["approvalId"],
        )
        with self.assertRaises(ControlPlaneContractError):
            self.adapter.grant_approval(
                run_id=run_id,
                event=wrong_event,
                approval=approval,
                plan=self.plan,
            )
        self.assertEqual(self.adapter.status(run_id)["state"], "waiting_for_approval")

    def test_denied_revoked_and_expired_records_cannot_grant(self) -> None:
        run_id = self.begin()["runId"]
        action_id = self.plan["actions"][0]["actionId"]
        self.adapter.record_event(
            run_id,
            self.event(
                "approval.requested",
                external_event_id="approval-request-negative",
                action_id=action_id,
            ),
        )
        records = (
            approval_for(self.plan, decision="denied"),
            approval_for(self.plan, decision="revoked"),
            approval_for(
                self.plan,
                expires_at="2026-07-21T13:01:30Z",
            ),
        )
        for index, approval in enumerate(records, start=1):
            with self.subTest(decision=approval["decision"]), self.assertRaises(
                ControlPlaneContractError
            ):
                self.adapter.grant_approval(
                    run_id=run_id,
                    event=self.event(
                        "approval.granted",
                        external_event_id=f"approval-negative-{index}",
                        at=LATER_AT,
                        action_id=action_id,
                        approval_id=approval["approvalId"],
                    ),
                    approval=approval,
                    plan=self.plan,
                )
        self.assertEqual(self.adapter.status(run_id)["state"], "waiting_for_approval")
        self.assertNotIn(
            "approval.recorded",
            [event["eventType"] for event in self.control.list_events(run_id)],
        )

    def test_duplicate_event_is_idempotent_even_after_later_event(self) -> None:
        run_id = self.begin()["runId"]
        first = self.event(
            "tool.started", external_event_id="tool-1", tool_name="read_file"
        )
        self.adapter.record_event(run_id, first)
        self.adapter.record_event(
            run_id,
            self.event(
                "tool.succeeded",
                external_event_id="tool-2",
                at=LATER_AT,
                tool_name="read_file",
            ),
        )
        before = len(self.control.list_events(run_id))
        duplicate = self.adapter.record_event(run_id, first)

        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(len(self.control.list_events(run_id)), before)

    def test_event_recorded_before_checkpoint_recovers_without_duplicate(self) -> None:
        run_id = self.begin()["runId"]
        event = self.event(
            "tool.started", external_event_id="tool-1", tool_name="read_file"
        )
        result = self.adapter.record_event(run_id, event)
        checkpoint = self.checkpoints.load(run_id)
        checkpoint["processedEvents"] = checkpoint["processedEvents"][:-1]
        checkpoint["updatedAt"] = EVENT_AT
        self.checkpoints.save(checkpoint)
        before = len(self.control.list_events(run_id))

        recovered = self.adapter.record_event(run_id, event)

        self.assertTrue(recovered["duplicate"])
        self.assertEqual(result["state"], recovered["state"])
        self.assertEqual(len(self.control.list_events(run_id)), before)

    def test_out_of_order_event_is_rejected(self) -> None:
        run_id = self.begin()["runId"]
        self.adapter.record_event(
            run_id,
            self.event("tool.succeeded", external_event_id="tool-2", at=LATER_AT),
        )
        with self.assertRaises(ControlPlaneStateError):
            self.adapter.record_event(
                run_id,
                self.event("tool.started", external_event_id="tool-1", at=EVENT_AT),
            )

    def test_tampered_pipe_audit_blocks_further_runtime_events(self) -> None:
        run_id = self.begin()["runId"]
        self.control.close()
        connection = sqlite3.connect(self.control_path)
        event_json = json.loads(
            connection.execute(
                "SELECT event_json FROM events WHERE run_id = ? AND sequence = 1",
                (run_id,),
            ).fetchone()[0]
        )
        event_json["status"] = "failed"
        connection.execute(
            "UPDATE events SET event_json = ? WHERE run_id = ? AND sequence = 1",
            (json.dumps(event_json), run_id),
        )
        connection.commit()
        connection.close()
        self.control = LocalControlPlaneStore(self.control_path)
        self.adapter = HermesRuntimeAdapter(self.control, self.checkpoints)

        with self.assertRaises(ControlPlaneStateError):
            self.adapter.record_event(
                run_id,
                self.event("tool.started", external_event_id="tool-1"),
            )

    def test_completed_run_is_terminal_for_resume(self) -> None:
        run_id = self.begin()["runId"]
        completion_event = self.event("run.completed", external_event_id="complete-1")
        completed = self.adapter.record_event(
            run_id,
            completion_event,
        )
        self.assertEqual(completed["state"], "completed")
        self.assertTrue(self.adapter.record_event(run_id, completion_event)["duplicate"])
        with self.assertRaises(ControlPlaneStateError):
            self.adapter.record_event(
                run_id,
                self.event(
                    "tool.started",
                    external_event_id="tool-after-complete",
                    at=LATER_AT,
                ),
            )
        with self.assertRaises(ControlPlaneStateError):
            self.adapter.resume(
                run_id=run_id,
                session_id=SESSION_TWO,
                external_event_id="resume-after-complete",
                occurred_at=LATER_AT,
            )
