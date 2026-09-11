from __future__ import annotations

import json
import sqlite3
from typing import Any
from unittest import mock

from pipe_venture_builder.adapters.deepseek_harness import (
    DeepSeekHarnessRuntimeAdapter,
    DeepSeekHarnessRuntimeEvent,
)
from pipe_venture_builder.apply.service import SupervisedApplyService
from pipe_venture_builder.control_plane.model import fingerprint
from pipe_venture_builder.reconcile import plan_reconciliation
from tests.control_plane.helpers import approval_for, assert_schema_valid, create_plan, update_plan
from tests.deepseek_harness.helpers import (
    READ_TOOL,
    SECRET_SENTINEL,
    TEXT_SENTINEL,
    assert_blocked,
    assert_metadata_only,
    event_metadata,
    fixture_base,
)
from tests.deepseek_harness.test_adapter import Harness
from tests.deepseek_harness.test_recovery import (
    PAYLOAD_FINGERPRINT,
    RecoveryTestCase,
    recovery_harness,
)
from tests.reconcile.helpers import baseline_with_intent, linear_record, snapshot


DECIDED_AT = "2026-09-10T12:10:00Z"
EXPIRES_AT = "2026-09-10T18:00:00Z"
HANDOFF_AT = "2026-09-10T12:30:00Z"
PROPOSED_AT = "2026-09-10T12:31:00Z"
COMPLETED_AT = "2026-09-10T12:32:00Z"
RESULT_REF = "review:PIP-899:notes"
RESULT_FINGERPRINT = "sha256:" + "9" * 64
PROPOSAL_CONSTRAINTS = {
    "applyAuthorized": False,
    "externalMutationAllowed": False,
    "runtimeApprovalIsAuthority": False,
    "rawPayloadPersisted": False,
}
FORBIDDEN_PROPOSAL_KEYS = ("apply", "applier", "applyhandle", "callback", "handle", "execute", "hook")


def all_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [key for item in value.items() for key in (item[0], *all_keys(item[1]))]
    if isinstance(value, list):
        return [key for item in value for key in all_keys(item)]
    return []


def investigate_plan() -> dict[str, Any]:
    baseline = baseline_with_intent(
        action_type="investigate",
        target_ref=None,
        match_strategy="manual",
        confidence="high",
        title="Investigate governed ticket",
    )
    return plan_reconciliation(baseline, [snapshot([])])


def link_plan() -> dict[str, Any]:
    """A proposed ``link``: one stable external id resolves the unlinked artifact."""

    baseline = baseline_with_intent(
        action_type="link",
        target_ref=None,
        match_strategy="stable_external_id",
        confidence="high",
        title="Link governed ticket",
    )
    baseline["artifacts"][0]["sourceRef"] = "issue-713"
    record = linear_record("issue-713", "PIP-713", title="Link governed ticket")
    return plan_reconciliation(baseline, [snapshot([record])])


def approval(plan: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {"decided_at": DECIDED_AT, "expires_at": EXPIRES_AT}
    fields.update(overrides)
    return approval_for(plan, **fields)


def quiescent(h: Any) -> None:
    h.begin()
    h.record(1, kind="turn.started")
    h.record(2, kind="turn.ended")


def handoff(h: Any, **overrides: Any) -> dict[str, Any]:
    request: dict[str, Any] = {
        "binding": h.binding,
        "context": h.context,
        "plan": h.plan,
        "action_id": h.plan["actions"][0]["actionId"],
        "approval": None,
        "occurred_at": HANDOFF_AT,
    }
    request.update(overrides)
    return h.adapter.handoff(**request)


def propose(h: Any, **overrides: Any) -> dict[str, Any]:
    request: dict[str, Any] = {
        "binding": h.binding,
        "context": h.context,
        "result_ref": RESULT_REF,
        "result_fingerprint": RESULT_FINGERPRINT,
        "occurred_at": PROPOSED_AT,
    }
    request.update(overrides)
    return h.adapter.propose(**request)


def complete(h: Any, proposal: Any, **overrides: Any) -> dict[str, Any]:
    request: dict[str, Any] = {
        "binding": h.binding,
        "context": h.context,
        "proposal": proposal,
        "occurred_at": COMPLETED_AT,
    }
    request.update(overrides)
    return h.adapter.complete(**request)


class ProposalAssertions(RecoveryTestCase):
    def assert_inert_proposal(self, proposal: dict[str, Any]) -> None:
        self.assertEqual(json.loads(json.dumps(proposal)), proposal)
        unsigned = {k: v for k, v in proposal.items() if k != "proposalFingerprint"}
        self.assertEqual(proposal["proposalFingerprint"], fingerprint(unsigned))
        self.assertEqual(proposal["constraints"], PROPOSAL_CONSTRAINTS)
        assert_metadata_only(self, proposal)
        for key in all_keys(proposal):
            folded = key.lower()
            self.assertNotIn(folded, FORBIDDEN_PROPOSAL_KEYS, key)
            self.assertFalse(folded.endswith(("callback", "handle", "hook")), key)
        for sentinel in (TEXT_SENTINEL, SECRET_SENTINEL):
            self.assertNotIn(sentinel, json.dumps(proposal))


class ApprovalHandoffTests(ProposalAssertions):
    """ADR-004 D6: runtime approval is never authority; only an exact, active Pipe record."""

    def test_runtime_approval_event_is_never_authority(self) -> None:
        with recovery_harness() as h:
            quiescent(h)
            assert_blocked(
                self, "event_kind_forbidden", DeepSeekHarnessRuntimeEvent.from_metadata,
                event_metadata(3, kind="approval.granted"),
            )
            self.assert_refused_unchanged(h, "approval_missing", handoff, h)
            self.assertNotIn("approval.recorded", [item["eventType"] for item in h.audit()])

    def test_handoff_validates_the_exact_active_record_and_never_applies(self) -> None:
        for factory in (create_plan, update_plan, link_plan):
            plan = factory()
            with self.subTest(action=plan["actions"][0]["actionType"]), recovery_harness(plan) as h:
                quiescent(h)
                record = approval(plan)
                h.store.record_approval(record, at=DECIDED_AT)
                audit = h.audit()
                with mock.patch.object(
                    SupervisedApplyService, "execute_action", side_effect=AssertionError("apply")
                ) as apply:
                    proposal = handoff(h, approval=record)
                apply.assert_not_called()
                self.assert_inert_proposal(proposal)
                action = plan["actions"][0]
                self.assertEqual(proposal["kind"], "action_handoff")
                self.assertEqual(proposal["action"]["actionId"], action["actionId"])
                self.assertEqual(proposal["action"]["actionType"], action["actionType"])
                self.assertEqual(proposal["action"]["approvalId"], record["approvalId"])
                self.assertEqual(proposal["action"]["scope"], record["scope"])
                self.assertIsNone(proposal["resultRef"])
                # Validation never applies, records or checkpoints the Pipe action.
                self.assertEqual(h.audit(), audit)
                self.assertEqual(h.store.get_run(h.run_id)["status"], "running")
                self.assertIsNone(h.store.get_checkpoint(h.run_id, action["actionId"]))

    def test_handoff_refuses_non_approvable_missing_inactive_or_foreign_records(self) -> None:
        with recovery_harness(investigate_plan()) as h:
            quiescent(h)
            self.assert_refused_unchanged(h, "action_not_approvable", handoff, h)

        # Only the action type matters: flagging a non-mutating action as
        # approval-required never makes it approvable.
        flagged = investigate_plan()
        flagged["actions"][0]["approvalRequired"] = True
        with recovery_harness(flagged) as h:
            quiescent(h)
            self.assert_refused_unchanged(h, "action_not_approvable", handoff, h)

        plan = create_plan()
        with recovery_harness(plan) as h:
            quiescent(h)
            recorded = approval(plan)
            unrecorded = approval(plan, decided_at="2026-09-10T12:11:00Z")
            denied = approval(plan, decided_at="2026-09-10T12:12:00Z", decision="denied")
            expired = approval(
                plan, decided_at="2026-09-10T12:00:00Z", expires_at="2026-09-10T12:20:00Z"
            )
            for record in (recorded, denied, expired):
                h.store.record_approval(record, at=DECIDED_AT)
            tampered = {**recorded, "scope": {**recorded["scope"], "targetContainerId": "other"}}
            cases = (
                ("unknown action", "action_not_approvable", {"action_id": "RA-000000000000"}),
                ("no record", "approval_missing", {"approval": None}),
                ("not a mapping", "approval_missing", {"approval": [recorded]}),
                ("record absent from Pipe", "approval_missing", {"approval": unrecorded}),
                ("denied record", "approval_inactive", {"approval": denied}),
                ("expired record", "approval_inactive", {"approval": expired}),
                ("record of another action", "approval_invalid", {"approval": approval(update_plan())}),
                ("tampered record", "approval_invalid", {"approval": tampered}),
                ("plan of another run", "plan_mismatch", {"plan": update_plan(), "approval": recorded}),
            )
            for name, code, overrides in cases:
                with self.subTest(case=name):
                    self.assert_refused_unchanged(h, code, handoff, h, **overrides)


        with recovery_harness(plan) as h:
            quiescent(h)
            record = approval(plan)
            h.store.record_approval(record, at=DECIDED_AT)
            self.assertEqual(handoff(h, approval=record)["kind"], "action_handoff")
            revoked = approval(plan, decided_at="2026-09-10T12:20:00Z", decision="revoked")
            h.store.record_approval(revoked, at="2026-09-10T12:20:00Z")
            with self.subTest(case="superseded by a later revocation"):
                self.assert_refused_unchanged(h, "approval_inactive", handoff, h, approval=record)

    def test_handoff_requires_a_quiescent_stream(self) -> None:
        plan = create_plan()
        with recovery_harness(plan) as h:
            h.begin()
            h.record(1, kind="turn.started")
            record = approval(plan)
            h.store.record_approval(record, at=DECIDED_AT)
            self.assert_refused_unchanged(h, "stream_not_quiescent", handoff, h, approval=record)


class CompletionTests(ProposalAssertions):
    """ADR-004 D3: only a dedicated Pipe method completes, with the issued proposal."""

    def test_idle_with_an_open_turn_or_tool_call_is_not_a_resting_point(self) -> None:
        cases = (
            ("tool call in flight", ("turn.started", "tool.started", "turn.ended", "session.idle")),
            ("turn still open", ("turn.started", "session.idle")),
        )
        for name, kinds in cases:
            with self.subTest(case=name), recovery_harness() as h:
                h.begin()
                for sequence, kind in enumerate(kinds, start=1):
                    extra: dict[str, Any] = {}
                    if kind == "tool.started":
                        extra = {"toolName": READ_TOOL, "payloadFingerprint": PAYLOAD_FINGERPRINT}
                    h.record(sequence, kind=kind, **extra)
                self.assert_refused_unchanged(h, "stream_not_quiescent", propose, h)
                h.restart()
                assert_blocked(self, "outcome_unknown", h.begin)

    def test_idle_turn_end_and_status_signals_never_complete(self) -> None:
        with recovery_harness() as h:
            quiescent(h)
            h.record(3, kind="session.idle")
            assert_blocked(
                self, "event_kind_unknown", DeepSeekHarnessRuntimeEvent.from_metadata,
                event_metadata(4, kind="session.status"),
            )
            self.assertEqual(h.store.get_run(h.run_id)["status"], "running")
            self.assertNotIn("run.completed", [item["eventType"] for item in h.audit()])
            self.assertEqual(h.checkpoint()["state"], "running")

    def test_read_run_completes_only_through_the_dedicated_method(self) -> None:
        with recovery_harness() as h:
            quiescent(h)
            audit = h.audit()
            proposal = propose(h)
            self.assert_inert_proposal(proposal)
            self.assertEqual(proposal["kind"], "read_result")
            self.assertIsNone(proposal["action"])
            self.assertEqual(proposal["resultRef"], RESULT_REF)
            self.assertEqual(proposal["resultFingerprint"], RESULT_FINGERPRINT)
            self.assertEqual(proposal["eventWatermark"], 2)
            self.assertEqual(h.audit(), audit)
            self.assertEqual(h.store.get_run(h.run_id)["status"], "running")

            result = complete(h, proposal)
            self.assertEqual(result["state"], "completed")
            self.assertEqual(result["proposalFingerprint"], proposal["proposalFingerprint"])
            assert_metadata_only(self, result)
            self.assertEqual(h.store.get_run(h.run_id)["status"], "completed")
            events = h.audit()
            completed = [item for item in events if item["eventType"] == "run.completed"]
            self.assertEqual(len(completed), 1)
            self.assertEqual(completed[0]["status"], "succeeded")
            self.assertIsNone(completed[0]["references"]["approvalId"])
            self.assertEqual(
                completed[0]["references"]["idempotencyKey"],
                f"{proposal['dispatchId']}:{proposal['proposalFingerprint'].split(':', 1)[1]}",
            )
            # A read-only run never needs, records or fabricates an ApprovalRecord.
            self.assertNotIn("approval.recorded", [item["eventType"] for item in events])
            self.assertTrue(h.store.verify_audit_chain(h.run_id))
            for event in events:
                assert_schema_valid(self, "RunEvent.schema.json", event)
            checkpoint = h.checkpoint()
            self.assertEqual(checkpoint["state"], "completed")
            self.assertEqual(checkpoint["proposalFingerprint"], proposal["proposalFingerprint"])

            for name, function in (
                ("event after completion", lambda: h.record(3, kind="session.idle")),
                ("second completion", lambda: complete(h, proposal)),
                ("new dispatch", h.begin),
            ):
                with self.subTest(after=name):
                    self.assert_refused_unchanged(h, "run_terminal", function)
            h.restart()
            self.assert_refused_unchanged(h, "run_terminal", h.begin)

    def test_completion_refuses_unissued_altered_stale_or_foreign_proposals(self) -> None:
        with recovery_harness() as h:
            quiescent(h)
            # Nothing was proposed yet: refused before the argument is even inspected.
            self.assert_refused_unchanged(h, "proposal_missing", complete, h, {})
            proposal = propose(h)
            altered = {**proposal, "resultFingerprint": "sha256:" + "a" * 64}
            forged = {k: v for k, v in altered.items() if k != "proposalFingerprint"}
            forged["proposalFingerprint"] = fingerprint(forged)
            with fixture_base() as other_base:
                other = Harness(other_base)
                try:
                    other.begin()
                    other.record(1, kind="session.idle")
                    foreign = other.adapter.propose(
                        binding=other.binding, context=other.context, result_ref=RESULT_REF,
                        result_fingerprint=RESULT_FINGERPRINT, occurred_at=PROPOSED_AT,
                    )
                finally:
                    other.close()
            cases = (
                ("altered content, stale fingerprint", "proposal_invalid", altered),
                ("re-signed forgery", "proposal_mismatch", forged),
                ("raw key added", "proposal_invalid", {**proposal, "prompt": TEXT_SENTINEL}),
                ("not a mapping", "proposal_invalid", [proposal]),
                ("proposal of another run", "proposal_mismatch", foreign),
            )
            for name, code, value in cases:
                with self.subTest(case=name):
                    self.assert_refused_unchanged(h, code, complete, h, value)

            h.record(3, kind="turn.started")
            h.record(4, kind="turn.ended")
            with self.subTest(case="events arrived after the proposal"):
                self.assert_refused_unchanged(h, "proposal_mismatch", complete, h, proposal)

    def test_handoff_proposal_cannot_complete_the_run(self) -> None:
        plan = create_plan()
        with recovery_harness(plan) as h:
            quiescent(h)
            record = approval(plan)
            h.store.record_approval(record, at=DECIDED_AT)
            proposal = handoff(h, approval=record)
            propose(h)
            # The handoff is inert: it never completes the run in place of a result.
            self.assert_refused_unchanged(h, "proposal_mismatch", complete, h, proposal)

    def test_propose_and_complete_require_a_quiescent_intact_stream(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.started")
            self.assert_refused_unchanged(h, "stream_not_quiescent", propose, h)
            h.record(2, kind="turn.ended")
            proposal = propose(h)
            h.record(3, kind="turn.started")
            self.assert_refused_unchanged(h, "stream_not_quiescent", complete, h, proposal)

        with recovery_harness() as h:
            quiescent(h)
            proposal = propose(h)
            assert_blocked(self, "sequence_gap", h.record, 9)
            self.assert_refused_unchanged(h, "stream_blocked", complete, h, proposal)

        with recovery_harness() as h:
            quiescent(h)
            proposal = propose(h)
            connection = sqlite3.connect(h.db_path)
            try:
                row = connection.execute(
                    "SELECT event_json FROM events WHERE run_id = ? AND sequence = 1", (h.run_id,)
                ).fetchone()
                tampered = json.loads(row[0])
                tampered["status"] = "failed"
                connection.execute(
                    "UPDATE events SET event_json = ? WHERE run_id = ? AND sequence = 1",
                    (json.dumps(tampered), h.run_id),
                )
                connection.commit()
            finally:
                connection.close()
            self.assert_refused_unchanged(h, "audit_chain_invalid", complete, h, proposal)

    def test_result_reference_and_fingerprint_are_validated(self) -> None:
        with recovery_harness() as h:
            quiescent(h)
            for name, overrides in (
                ("absolute path", {"result_ref": str(h.base)}),
                ("spaces", {"result_ref": "has space"}),
                ("secret-shaped", {"result_ref": SECRET_SENTINEL}),
                ("empty", {"result_ref": ""}),
                ("not text", {"result_ref": None}),
                ("bad fingerprint", {"result_fingerprint": "sha256:abc"}),
                ("bad timestamp", {"occurred_at": "yesterday"}),
            ):
                with self.subTest(case=name):
                    code = "timestamp_invalid" if "occurred_at" in overrides else "result_ref_invalid"
                    self.assert_refused_unchanged(h, code, propose, h, **overrides)

    def test_completion_survives_restart_through_the_checkpointed_proposal(self) -> None:
        with recovery_harness() as h:
            quiescent(h)
            proposal = propose(h)
            h.restart()
            self.assertIs(h.begin()["recovered"], True)
            self.assertEqual(complete(h, proposal)["state"], "completed")
            self.assertEqual(h.store.get_run(h.run_id)["status"], "completed")

    def test_completion_without_a_checkpoint_store(self) -> None:
        with fixture_base() as base:
            h = Harness(base)
            try:
                quiescent(h)
                self.assertIsInstance(h.adapter, DeepSeekHarnessRuntimeAdapter)
                proposal = propose(h)
                self.assertEqual(complete(h, proposal)["state"], "completed")
                self.assertEqual(h.store.get_run(h.run_id)["status"], "completed")
            finally:
                h.close()
