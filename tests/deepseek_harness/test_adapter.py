from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator
from unittest import TestCase

from pipe_venture_builder.adapters.deepseek_harness import (
    DeepSeekHarnessRuntimeAdapter,
    DeepSeekHarnessRuntimeEvent,
    SessionRegistry,
)
from pipe_venture_builder.control_plane import LocalControlPlaneStore
from tests.control_plane.helpers import assert_schema_valid, create_plan, update_plan
from tests.deepseek_harness.helpers import (
    BEGIN_AT,
    OTHER_CONSUMER_ID,
    OTHER_ROUTE_ID,
    READ_TOOL,
    REGISTERED_AT,
    RUN_ID,
    SECRET_SENTINEL,
    SESSION_THREE,
    SESSION_TWO,
    TEXT_SENTINEL,
    assert_block_marker,
    assert_blocked,
    assert_metadata_only,
    build_binding,
    build_context,
    event_metadata,
    fixture_base,
    forbid_host_access,
    make_fixture_root,
)


PAYLOAD_FINGERPRINT = "sha256:" + "4" * 64


class Harness:
    """A registered Pipe plan/run, a C1 context and a bound attempt-1 session."""

    def __init__(self, base: Path, plan: dict[str, Any] | None = None) -> None:
        self.base = base
        self.context = build_context(make_fixture_root(base))
        self.db_path = base / "control-plane.sqlite3"
        self.store = LocalControlPlaneStore(self.db_path)
        self.plan = plan if plan is not None else create_plan()
        self.run_id = self.store.register_plan(self.plan, at=REGISTERED_AT)
        self.sessions = SessionRegistry()
        self.binding = self.sessions.bind(self.binding_for())
        self.adapter = DeepSeekHarnessRuntimeAdapter(self.store, self.sessions)

    def binding_for(self, **overrides: Any):
        fields: dict[str, Any] = {
            "pipe_run_id": self.run_id,
            "workspace_fingerprint": self.context.workspace_fingerprint,
            "context_fingerprint": self.context.context_fingerprint,
        }
        fields.update(overrides)
        return build_binding(**fields)

    def begin(self, **overrides: Any) -> dict[str, Any]:
        request: dict[str, Any] = {
            "plan": self.plan,
            "context": self.context,
            "binding": self.binding,
            "occurred_at": BEGIN_AT,
        }
        request.update(overrides)
        return self.adapter.begin(**request)

    def event(self, sequence: int, **overrides: Any) -> DeepSeekHarnessRuntimeEvent:
        return DeepSeekHarnessRuntimeEvent.from_metadata(
            event_metadata(sequence, **overrides)
        )

    def record(self, sequence: int, *, binding: Any = None, context: Any = None, **overrides: Any):
        return self.adapter.record_event(
            binding=binding or self.binding,
            context=context or self.context,
            event=self.event(sequence, **overrides),
        )

    def audit(self) -> list[dict[str, Any]]:
        return self.store.list_events(self.run_id)

    def close(self) -> None:
        self.store.close()


@contextmanager
def harness() -> Iterator[Harness]:
    with fixture_base() as base:
        instance = Harness(base)
        try:
            yield instance
        finally:
            instance.close()


class AdapterTestCase(TestCase):
    def assert_refused_without_mutation(
        self, h: Harness, code: str, function: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        before = h.audit()
        status = h.store.get_run(h.run_id)["status"]
        assert_blocked(self, code, function, *args, forbidden=(str(h.base),), **kwargs)
        self.assertEqual(h.audit(), before)
        self.assertEqual(h.store.get_run(h.run_id)["status"], status)


class AdapterBeginTests(AdapterTestCase):
    """C2: dispatch binds a registered Pipe plan/run to the C1 context and session."""

    def test_begin_binds_registered_plan_run_and_c1_session(self) -> None:
        with harness() as h:
            result = h.begin()

            self.assertEqual(result["runId"], h.run_id)
            self.assertEqual(result["planId"], h.plan["planId"])
            self.assertEqual(result["sessionId"], h.binding.session_id)
            self.assertEqual(result["attempt"], 1)
            self.assertEqual(result["workflow"], "review")
            self.assertEqual(result["linearTicketId"], h.context.linear_ticket_id)
            self.assertEqual(result["bindingFingerprint"], h.binding.binding_fingerprint)
            self.assertEqual(result["contextFingerprint"], h.context.context_fingerprint)
            self.assertRegex(result["dispatchId"], r"^DHD-[a-f0-9]{12}$")
            self.assertEqual(result["state"], "running")
            self.assertEqual(result["expectedSequence"], 1)
            self.assertIs(result["duplicate"], False)
            self.assertIs(result["constraints"]["runtimeApprovalIsAuthority"], False)
            assert_metadata_only(self, result)

            self.assertEqual(h.store.get_run(h.run_id)["status"], "running")
            events = h.audit()
            self.assertEqual(events[-1]["eventType"], "run.resumed")
            self.assertEqual(events[-1]["references"]["idempotencyKey"], result["dispatchId"])
            self.assertEqual(events[-1]["checkpoint"]["attempt"], 1)
            self.assertTrue(h.store.verify_audit_chain(h.run_id))
            for event in events:
                assert_schema_valid(self, "RunEvent.schema.json", event)
            # Read-only review/check runs under the ticket's authorization: no
            # ApprovalRecord is required, recorded or fabricated.
            self.assertNotIn("approval.recorded", [item["eventType"] for item in events])

    def test_begin_retry_with_same_binding_is_idempotent(self) -> None:
        with harness() as h:
            first = h.begin()
            before = h.audit()
            repeated = h.begin()
            self.assertIs(repeated["duplicate"], True)
            self.assertEqual(repeated["dispatchId"], first["dispatchId"])
            self.assertEqual(h.audit(), before)

    def test_begin_refuses_unregistered_run_or_mismatched_plan_before_mutation(self) -> None:
        with harness() as h:
            unregistered = h.sessions.bind(
                h.binding_for(pipe_run_id=RUN_ID, session_id=SESSION_THREE)
            )
            other_plan = update_plan()
            other_run_id = h.store.register_plan(other_plan, at=REGISTERED_AT)
            other_run_binding = h.sessions.bind(
                h.binding_for(pipe_run_id=other_run_id, session_id=SESSION_TWO)
            )
            tampered = {**h.plan, "generatedAt": "2026-07-21T12:30:00Z"}
            cases = (
                ("unregistered run", "run_unregistered", {"binding": unregistered}),
                ("other plan", "plan_mismatch", {"plan": other_plan}),
                ("tampered plan", "plan_mismatch", {"plan": tampered}),
                (
                    "binding for another registered run",
                    "plan_mismatch",
                    {"binding": other_run_binding},
                ),
                ("non-mapping plan", "plan_mismatch", {"plan": [h.plan]}),
            )
            other_before = h.store.list_events(other_run_id)
            for name, code, overrides in cases:
                with self.subTest(case=name):
                    self.assert_refused_without_mutation(h, code, h.begin, **overrides)
            self.assertEqual(h.store.list_events(other_run_id), other_before)

    def test_begin_requires_resolvable_latest_binding_and_matching_context(self) -> None:
        with harness() as h:
            divergent = build_context(make_fixture_root(h.base, "other"), workflow="check")
            unbound = h.binding_for(session_id=SESSION_TWO, attempt=2)
            forged = h.binding_for(route_id=OTHER_ROUTE_ID)
            other_consumer = h.binding_for(consumer_id=OTHER_CONSUMER_ID)
            cases = (
                ("binding not registered", "binding_unknown", {"binding": unbound}),
                ("forged binding element", "binding_unknown", {"binding": forged}),
                ("second consumer", "consumer_conflict", {"binding": other_consumer}),
                ("divergent context", "context_mismatch", {"context": divergent}),
                ("not a binding", "binding_field_invalid", {"binding": h.binding.document()}),
            )
            for name, code, overrides in cases:
                with self.subTest(case=name):
                    self.assert_refused_without_mutation(h, code, h.begin, **overrides)

            h.sessions.bind(h.binding_for(session_id=SESSION_TWO, attempt=2))
            with self.subTest(case="superseded attempt"):
                self.assert_refused_without_mutation(h, "binding_superseded", h.begin)

    def test_begin_refuses_terminal_or_blocked_run(self) -> None:
        for status in ("completed", "failed", "blocked"):
            with self.subTest(status=status), harness() as h:
                h.store.update_run_status(h.run_id, status, at=BEGIN_AT)
                self.assert_refused_without_mutation(h, "run_terminal", h.begin)

    def test_begin_refuses_invalid_dispatch_timestamp(self) -> None:
        with harness() as h:
            for value in ("yesterday", "2026-09-10T12:00:00", None, TEXT_SENTINEL):
                with self.subTest(value=repr(value)[:12]):
                    self.assert_refused_without_mutation(
                        h, "timestamp_invalid", h.begin, occurred_at=value
                    )

    def test_audited_dispatch_unknown_to_adapter_requires_recovery(self) -> None:
        # Stream state is in memory in C2; a dispatch already in the audit but
        # unknown to this adapter is never silently restarted from sequence 1.
        with harness() as h:
            h.begin()
            h.record(1)
            fresh = DeepSeekHarnessRuntimeAdapter(h.store, h.sessions)
            self.assert_refused_without_mutation(
                h, "recovery_required", fresh.begin,
                plan=h.plan, context=h.context, binding=h.binding, occurred_at=BEGIN_AT,
            )
            self.assert_refused_without_mutation(
                h, "dispatch_missing", fresh.record_event,
                binding=h.binding, context=h.context, event=h.event(2),
            )

    def test_adapter_requires_real_store_and_registry(self) -> None:
        with harness() as h:
            for store, sessions in ((None, h.sessions), (h.store, None), (object(), object())):
                with self.subTest(store=type(store).__name__, sessions=type(sessions).__name__):
                    assert_blocked(
                        self, "contract_violation", DeepSeekHarnessRuntimeAdapter, store, sessions
                    )


class AdapterEventTests(AdapterTestCase):
    """C2: allowlisted events are sequenced, deduplicated and audited payload-free."""

    def test_happy_path_records_payload_free_schema_valid_audit(self) -> None:
        with harness() as h:
            h.begin()
            steps = (
                {"kind": "session.started"},
                {"kind": "turn.started"},
                {"kind": "tool.started", "toolName": READ_TOOL},
                {
                    "kind": "tool.succeeded",
                    "toolName": READ_TOOL,
                    "payloadFingerprint": PAYLOAD_FINGERPRINT,
                },
            )
            for sequence, overrides in enumerate(steps, start=1):
                with self.subTest(sequence=sequence):
                    result = h.record(sequence, **overrides)
                    self.assertIs(result["duplicate"], False)
                    self.assertEqual(result["sequence"], sequence)
                    self.assertEqual(result["expectedSequence"], sequence + 1)
                    self.assertRegex(result["eventId"], r"^DHE-[a-f0-9]{12}$")
                    self.assertEqual(result["state"], "running")
                    assert_metadata_only(self, result)

            events = h.audit()
            runtime = [
                item
                for item in events
                if (item["references"]["idempotencyKey"] or "").startswith("DHE-")
            ]
            self.assertEqual(len(runtime), len(steps))
            self.assertTrue(h.store.verify_audit_chain(h.run_id))
            for event in events:
                assert_schema_valid(self, "RunEvent.schema.json", event)
            encoded = json.dumps(events)
            self.assertNotIn(READ_TOOL, encoded)
            self.assertNotIn("payload", encoded.replace("rawPayloadPersisted", ""))
            self.assertNotIn("run.completed", [item["eventType"] for item in events])
            self.assertNotIn("approval.recorded", [item["eventType"] for item in events])
            self.assertEqual(h.store.get_run(h.run_id)["status"], "running")

    def test_idle_and_turn_end_never_complete_the_run(self) -> None:
        with harness() as h:
            h.begin()
            h.record(1, kind="turn.started")
            for sequence, kind in ((2, "turn.ended"), (3, "session.idle")):
                with self.subTest(kind=kind):
                    result = h.record(sequence, kind=kind)
                    self.assertEqual(result["state"], "running")
            self.assertIs(h.record(3, kind="session.idle")["duplicate"], True)
            self.assertEqual(h.store.get_run(h.run_id)["status"], "running")
            self.assertNotIn("run.completed", [item["eventType"] for item in h.audit()])

    def test_runtime_authority_and_non_normalized_events_are_refused(self) -> None:
        with harness() as h:
            h.begin()
            for kind in ("approval.granted", "run.completed"):
                with self.subTest(kind=kind):
                    assert_blocked(
                        self, "event_kind_forbidden", DeepSeekHarnessRuntimeEvent.from_metadata,
                        event_metadata(1, kind=kind),
                    )
            for value in (event_metadata(1), h.event(1).document(), None):
                with self.subTest(value=type(value).__name__):
                    self.assert_refused_without_mutation(
                        h, "event_field_invalid", h.adapter.record_event,
                        binding=h.binding, context=h.context, event=value,
                    )

    def test_identical_retransmission_is_idempotent(self) -> None:
        with harness() as h:
            h.begin()
            h.record(1)
            h.record(2, kind="session.started")
            before = h.audit()
            for sequence, overrides in ((1, {}), (2, {"kind": "session.started"})):
                with self.subTest(sequence=sequence):
                    result = h.record(sequence, **overrides)
                    self.assertIs(result["duplicate"], True)
                    self.assertEqual(result["expectedSequence"], 3)
            self.assertEqual(h.audit(), before)

    def test_gap_reorder_and_conflicts_fail_closed_without_accepted_event(self) -> None:
        cases = (
            ("gap", "sequence_gap", {"sequence": 4}),
            ("reordered delivery", "sequence_gap", {"sequence": 5}),
            ("same sequence, other data", "event_conflict", {"sequence": 2, "kind": "session.started"}),
            (
                "same event id, other sequence",
                "event_conflict",
                {"sequence": 3, "externalEventId": "dsh-evt-0001"},
            ),
        )
        for name, code, request in cases:
            with self.subTest(case=name), harness() as h:
                h.begin()
                h.record(1)
                h.record(2)
                sequence = request.pop("sequence")
                before = h.audit()
                assert_blocked(self, code, h.record, sequence, forbidden=(str(h.base),), **request)
                # The block is written to the Pipe audit, the durable authority.
                assert_block_marker(self, before, h.audit())
                self.assertEqual(h.store.get_run(h.run_id)["status"], "interrupted")
                # Fail closed: the missing or conflicting event is never inferred,
                # so even the next well-formed event is refused afterwards.
                self.assert_refused_without_mutation(h, "stream_blocked", h.record, 3)

    def test_superseded_session_consumer_context_and_dispatch_fail_closed(self) -> None:
        with harness() as h:
            h.begin()
            h.record(1)
            divergent = build_context(make_fixture_root(h.base, "other"), workflow="check")
            cases = (
                ("divergent context", "context_mismatch", {"context": divergent}),
                (
                    "second consumer",
                    "consumer_conflict",
                    {"binding": h.binding_for(consumer_id=OTHER_CONSUMER_ID)},
                ),
                ("event from another session", "session_mismatch", {"sessionId": SESSION_TWO}),
                ("not a binding", "binding_field_invalid", {"binding": h.binding.document()}),
            )
            for name, code, overrides in cases:
                with self.subTest(case=name):
                    self.assert_refused_without_mutation(h, code, h.record, 2, **overrides)

            successor = h.sessions.bind(h.binding_for(session_id=SESSION_TWO, attempt=2))
            with self.subTest(case="successor not dispatched"):
                self.assert_refused_without_mutation(
                    h, "dispatch_missing", h.record, 1, binding=successor, sessionId=SESSION_TWO
                )
            with self.subTest(case="superseded attempt"):
                self.assert_refused_without_mutation(h, "binding_superseded", h.record, 2)

            resumed = h.begin(binding=successor)
            self.assertEqual(resumed["attempt"], 2)
            self.assertEqual(resumed["expectedSequence"], 1)
            accepted = h.record(1, binding=successor, sessionId=SESSION_TWO)
            self.assertIs(accepted["duplicate"], False)
            self.assertEqual(accepted["attempt"], 2)
            self.assertTrue(h.store.verify_audit_chain(h.run_id))

    def test_tampered_audit_chain_blocks_dispatch_and_events(self) -> None:
        with harness() as h:
            h.begin()
            h.record(1)
            connection = sqlite3.connect(h.db_path)
            try:
                row = connection.execute(
                    "SELECT event_json FROM events WHERE run_id = ? AND sequence = 1",
                    (h.run_id,),
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
            self.assertFalse(h.store.verify_audit_chain(h.run_id))
            count = len(h.audit())
            assert_blocked(self, "audit_chain_invalid", h.record, 2, forbidden=(str(h.base),))
            successor = h.sessions.bind(h.binding_for(session_id=SESSION_TWO, attempt=2))
            assert_blocked(
                self, "audit_chain_invalid", h.begin, binding=successor, forbidden=(str(h.base),)
            )
            self.assertEqual(len(h.audit()), count)


class AdapterBoundaryTests(AdapterTestCase):
    """ADR-004 D13: no raw sentinel reaches errors, documents, audit or disk."""

    def test_no_raw_sentinel_reaches_errors_documents_audit_or_disk(self) -> None:
        with harness() as h:
            results = [h.begin()]
            for metadata in (
                event_metadata(1, prompt=TEXT_SENTINEL),
                event_metadata(1, externalEventId=SECRET_SENTINEL),
                event_metadata(1, kind="tool.started", toolName=TEXT_SENTINEL),
                event_metadata(1, reasoning=SECRET_SENTINEL),
            ):
                with self.subTest(keys=sorted(metadata)[:2]):
                    with self.assertRaises(ValueError) as caught:
                        DeepSeekHarnessRuntimeEvent.from_metadata(metadata)
                    self.assertNotIn(TEXT_SENTINEL, str(caught.exception))
                    self.assertNotIn(SECRET_SENTINEL, str(caught.exception))
            results.append(h.record(1, kind="tool.started", toolName=READ_TOOL))
            results.append(h.record(2, kind="tool.succeeded", toolName=READ_TOOL))

            documents = json.dumps([results, h.audit(), h.event(1).document()])
            for sentinel in (TEXT_SENTINEL, SECRET_SENTINEL):
                self.assertNotIn(sentinel, documents)
            h.store.close()
            h.store = LocalControlPlaneStore(h.db_path)
            for path in sorted(h.base.rglob("*")):
                if path.is_file():
                    content = path.read_bytes()
                    with self.subTest(file=path.name):
                        self.assertNotIn(TEXT_SENTINEL.encode(), content)
                        self.assertNotIn(SECRET_SENTINEL.encode(), content)

    def test_adapter_does_not_read_host_environment_or_spawn(self) -> None:
        with harness() as h:
            with forbid_host_access(filesystem=False) as log:
                h.begin()
                h.record(1)
                h.record(2, kind="session.idle")
            self.assertEqual(log, [])
