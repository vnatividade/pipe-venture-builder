from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator
from unittest import TestCase, mock

from pipe_venture_builder.adapters.deepseek_harness import (
    DeepSeekHarnessCheckpointStore,
    DeepSeekHarnessContractError,
    DeepSeekHarnessRuntimeAdapter,
    SessionRegistry,
)
from pipe_venture_builder.control_plane import ControlPlaneStateError, LocalControlPlaneStore
from pipe_venture_builder.control_plane.model import canonical_json
from tests.deepseek_harness.helpers import (
    OTHER_MODEL_ID,
    READ_TOOL,
    SECRET_SENTINEL,
    SESSION_THREE,
    SESSION_TWO,
    TEXT_SENTINEL,
    assert_block_marker,
    assert_blocked,
    assert_metadata_only,
    event_metadata,
    fixture_base,
)
from tests.deepseek_harness.test_adapter import Harness


PAYLOAD_FINGERPRINT = "sha256:" + "4" * 64


class RecoveryHarness(Harness):
    """The C2 harness with a checkpoint store and a simulated process restart."""

    def __init__(self, base: Path, plan: dict[str, Any] | None = None) -> None:
        super().__init__(base, plan)
        self.checkpoint_dir = base / "checkpoints"
        self.checkpoints = DeepSeekHarnessCheckpointStore(self.checkpoint_dir)
        self.adapter = DeepSeekHarnessRuntimeAdapter(
            self.store, self.sessions, checkpoints=self.checkpoints
        )

    @property
    def checkpoint_path(self) -> Path:
        return self.checkpoint_dir / f"{self.run_id}.json"

    def checkpoint(self) -> dict[str, Any] | None:
        return self.checkpoints.load(self.run_id)

    def restart(self) -> None:
        """Drop every in-memory object; only the SQLite audit and checkpoint survive."""

        lineage = self.sessions.lineage(self.run_id)
        self.store.close()
        self.store = LocalControlPlaneStore(self.db_path)
        self.sessions = SessionRegistry()
        for binding in lineage:
            self.sessions.bind(binding)
        self.checkpoints = DeepSeekHarnessCheckpointStore(self.checkpoint_dir)
        self.adapter = DeepSeekHarnessRuntimeAdapter(
            self.store, self.sessions, checkpoints=self.checkpoints
        )

    def runtime_keys(self) -> list[str]:
        return [
            item["references"]["idempotencyKey"]
            for item in self.audit()
            if (item["references"]["idempotencyKey"] or "").startswith("DHE-")
        ]

    def dispatch_keys(self) -> list[str]:
        return [
            item["references"]["idempotencyKey"]
            for item in self.audit()
            if (item["references"]["idempotencyKey"] or "").startswith("DHD-")
        ]


@contextmanager
def recovery_harness(plan: dict[str, Any] | None = None) -> Iterator[RecoveryHarness]:
    with fixture_base() as base:
        instance = RecoveryHarness(base, plan)
        try:
            yield instance
        finally:
            instance.close()


@contextmanager
def failing_checkpoint_save(*, on_call: int) -> Iterator[None]:
    """Fail exactly the ``on_call``-th checkpoint save; slots forbid instance patching."""

    real = DeepSeekHarnessCheckpointStore.save
    calls: list[Any] = []

    def flaky(store: Any, document: Any) -> dict[str, Any]:
        calls.append(document)
        if len(calls) == on_call:
            raise DeepSeekHarnessContractError("checkpoint_write_failed")
        return real(store, document)

    with mock.patch.object(DeepSeekHarnessCheckpointStore, "save", autospec=True, side_effect=flaky):
        yield


class RecoveryTestCase(TestCase):
    def assert_refused_unchanged(
        self, h: RecoveryHarness, code: str, function: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        audit = h.audit()
        status = h.store.get_run(h.run_id)["status"]
        checkpoint = h.checkpoint_path.read_bytes() if h.checkpoint_path.exists() else None
        assert_blocked(self, code, function, *args, forbidden=(str(h.base),), **kwargs)
        self.assertEqual(h.audit(), audit)
        self.assertEqual(h.store.get_run(h.run_id)["status"], status)
        after = h.checkpoint_path.read_bytes() if h.checkpoint_path.exists() else None
        self.assertEqual(after, checkpoint)


class CheckpointedDispatchTests(RecoveryTestCase):
    """ADR-004 D5: the adapter keeps its own checkpoint, consistent with the Pipe audit."""

    def test_dispatch_and_events_are_checkpointed_metadata_only(self) -> None:
        with recovery_harness() as h:
            result = h.begin()
            checkpoint = h.checkpoint()
            self.assertEqual(checkpoint["state"], "running")
            self.assertEqual(checkpoint["dispatchId"], result["dispatchId"])
            self.assertEqual(checkpoint["sessionLineage"], [h.binding.session_id])
            self.assertEqual(checkpoint["attempt"], 1)
            self.assertEqual(checkpoint["expectedSequence"], 1)
            self.assertEqual(checkpoint["processedEvents"], [])
            self.assertIsNone(checkpoint["pendingEvent"])
            self.assertEqual(checkpoint["bindingFingerprint"], h.binding.binding_fingerprint)
            self.assertEqual(checkpoint["contextFingerprint"], h.context.context_fingerprint)
            self.assertEqual(
                checkpoint["planFingerprint"], h.store.get_run(h.run_id)["plan_fingerprint"]
            )
            self.assertEqual(checkpoint["workflow"], "review")

            h.record(1, kind="turn.started")
            h.record(2, kind="tool.started", toolName=READ_TOOL)
            h.record(
                3, kind="tool.succeeded", toolName=READ_TOOL, payloadFingerprint=PAYLOAD_FINGERPRINT
            )
            checkpoint = h.checkpoint()
            self.assertEqual(checkpoint["expectedSequence"], 4)
            self.assertIsNone(checkpoint["pendingEvent"])
            self.assertEqual(
                [item["eventId"] for item in checkpoint["processedEvents"]], h.runtime_keys()
            )
            self.assertEqual(
                [item["kind"] for item in checkpoint["processedEvents"]],
                ["turn.started", "tool.started", "tool.succeeded"],
            )
            assert_metadata_only(self, checkpoint)
            raw = h.checkpoint_path.read_text(encoding="utf-8")
            for forbidden in (READ_TOOL, PAYLOAD_FINGERPRINT, str(h.base)):
                self.assertNotIn(forbidden, raw)

    def test_event_intent_is_checkpointed_before_the_audit_write(self) -> None:
        with recovery_harness() as h:
            h.begin()
            seen: list[Any] = []
            real = h.store.record_run_event

            def observing(*args: Any, **kwargs: Any) -> Any:
                pending = h.checkpoint()["pendingEvent"]
                seen.append((kwargs["idempotency_key"], pending and pending["eventId"]))
                return real(*args, **kwargs)

            with mock.patch.object(h.store, "record_run_event", side_effect=observing):
                result = h.record(1)
            self.assertEqual(seen, [(result["eventId"], result["eventId"])])
            self.assertIsNone(h.checkpoint()["pendingEvent"])


class ForwardOnlyRecoveryTests(RecoveryTestCase):
    """Recovery never rewinds, never infers an event and never resumes mid-turn."""

    def test_restart_resumes_a_quiescent_attempt_forward_only(self) -> None:
        with recovery_harness() as h:
            first = h.begin()
            h.record(1, kind="turn.started")
            h.record(2, kind="turn.ended")
            h.restart()
            dispatches = h.dispatch_keys()
            resumed = h.begin()
            self.assertIs(resumed["recovered"], True)
            self.assertIs(resumed["duplicate"], True)
            self.assertEqual(resumed["dispatchId"], first["dispatchId"])
            self.assertEqual(resumed["expectedSequence"], 3)
            self.assertEqual(h.dispatch_keys(), dispatches)
            before = h.audit()
            self.assertIs(h.record(2, kind="turn.ended")["duplicate"], True)
            self.assertEqual(h.audit(), before)
            accepted = h.record(3, kind="session.idle")
            self.assertIs(accepted["duplicate"], False)
            self.assertEqual(h.checkpoint()["expectedSequence"], 4)
            self.assertTrue(h.store.verify_audit_chain(h.run_id))

    def test_conflict_is_detected_from_checkpoint_records_after_restart(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.started")
            h.record(2, kind="turn.ended")
            h.restart()
            h.begin()
            audit = h.audit()
            assert_blocked(
                self, "event_conflict", h.record, 2, kind="session.idle", forbidden=(str(h.base),)
            )
            assert_block_marker(self, audit, h.audit())
            # The block is persisted, so a restart cannot clear it.
            self.assertEqual(h.checkpoint()["state"], "blocked")
            self.assertEqual(h.checkpoint()["blockerCode"], "event_conflict")
            h.restart()
            self.assert_refused_unchanged(h, "stream_blocked", h.begin)

    def test_protocol_block_survives_restart_and_requires_a_new_attempt(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="session.idle")
            assert_blocked(self, "sequence_gap", h.record, 3)
            checkpoint = h.checkpoint()
            self.assertEqual(checkpoint["state"], "blocked")
            self.assertEqual(checkpoint["blockerCode"], "sequence_gap")
            h.restart()
            self.assert_refused_unchanged(h, "stream_blocked", h.begin)
            self.assert_refused_unchanged(
                h, "dispatch_missing", h.adapter.record_event,
                binding=h.binding, context=h.context, event=h.event(2),
            )
            successor = h.sessions.bind(h.binding_for(session_id=SESSION_TWO, attempt=2))
            resumed = h.begin(binding=successor)
            self.assertEqual(resumed["attempt"], 2)
            self.assertEqual(resumed["expectedSequence"], 1)
            self.assertIs(resumed["recovered"], False)
            self.assertEqual(
                h.checkpoint()["sessionLineage"], [h.binding.session_id, SESSION_TWO]
            )
            self.assertIs(
                h.record(1, binding=successor, sessionId=SESSION_TWO)["duplicate"], False
            )

    def test_mid_turn_restart_blocks_the_attempt_as_outcome_unknown(self) -> None:
        for name, kinds in (
            ("dispatched, nothing observed", ()),
            ("turn open", ("turn.started",)),
            ("tool in flight", ("turn.started", "tool.started")),
        ):
            with self.subTest(case=name), recovery_harness() as h:
                h.begin()
                for sequence, kind in enumerate(kinds, start=1):
                    extra = {"toolName": READ_TOOL} if kind.startswith("tool.") else {}
                    h.record(sequence, kind=kind, **extra)
                audit = h.audit()
                h.restart()
                assert_blocked(self, "outcome_unknown", h.begin, forbidden=(str(h.base),))
                self.assertEqual(h.audit(), audit)
                checkpoint = h.checkpoint()
                self.assertEqual(checkpoint["state"], "outcome_unknown")
                self.assertEqual(checkpoint["blockerCode"], "outcome_unknown")
                self.assert_refused_unchanged(h, "outcome_unknown", h.begin)
                self.assertNotEqual(h.store.get_run(h.run_id)["status"], "completed")

                successor = h.sessions.bind(h.binding_for(session_id=SESSION_TWO, attempt=2))
                self.assertEqual(h.begin(binding=successor)["attempt"], 2)
                self.assert_refused_unchanged(h, "binding_superseded", h.begin)


class FailureConsistencyTests(RecoveryTestCase):
    """A failed audit or checkpoint write is reconciled from the audit, never guessed."""

    def test_audit_write_failure_drops_the_intent_and_accepts_the_retransmission(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="session.idle")
            failure = ControlPlaneStateError("synthetic audit failure")
            with mock.patch.object(h.store, "record_run_event", side_effect=failure):
                assert_blocked(
                    self, "audit_write_failed", h.record, 2, kind="turn.started",
                    forbidden=(str(h.base),),
                )
            pending = h.checkpoint()["pendingEvent"]
            self.assertEqual(pending["sequence"], 2)
            assert_blocked(self, "stream_blocked", h.record, 2, kind="turn.started")
            self.assertEqual(len(h.runtime_keys()), 1)

            h.restart()
            resumed = h.begin()
            self.assertEqual(resumed["expectedSequence"], 2)
            self.assertIsNone(h.checkpoint()["pendingEvent"])
            accepted = h.record(2, kind="turn.started")
            self.assertIs(accepted["duplicate"], False)
            self.assertEqual(h.runtime_keys().count(accepted["eventId"]), 1)
            self.assertEqual(h.runtime_keys()[-1], pending["eventId"])

    def test_checkpoint_commit_failure_rolls_forward_without_a_duplicate_audit(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.started")
            with failing_checkpoint_save(on_call=2):
                assert_blocked(
                    self, "checkpoint_write_failed", h.record, 2, kind="turn.ended",
                    forbidden=(str(h.base),),
                )
            self.assertEqual(h.checkpoint()["pendingEvent"]["sequence"], 2)
            self.assertEqual(len(h.runtime_keys()), 2)

            h.restart()
            resumed = h.begin()
            self.assertEqual(resumed["expectedSequence"], 3)
            checkpoint = h.checkpoint()
            self.assertIsNone(checkpoint["pendingEvent"])
            self.assertEqual(
                [item["eventId"] for item in checkpoint["processedEvents"]], h.runtime_keys()
            )
            before = h.audit()
            self.assertIs(h.record(2, kind="turn.ended")["duplicate"], True)
            self.assertEqual(h.audit(), before)

    def test_dispatch_intent_is_reconciled_after_a_failed_begin(self) -> None:
        with recovery_harness() as h:
            failure = ControlPlaneStateError("synthetic audit failure")
            with mock.patch.object(h.store, "record_run_event", side_effect=failure):
                assert_blocked(self, "audit_write_failed", h.begin, forbidden=(str(h.base),))
            self.assertEqual(h.checkpoint()["state"], "dispatch_pending")
            self.assertEqual(h.dispatch_keys(), [])
            h.restart()
            resumed = h.begin()
            self.assertEqual(h.dispatch_keys(), [resumed["dispatchId"]])
            self.assertEqual(h.checkpoint()["state"], "running")
            self.assertEqual(resumed["expectedSequence"], 1)
            self.assertIs(h.record(1)["duplicate"], False)

        with recovery_harness() as h:
            with failing_checkpoint_save(on_call=2):
                assert_blocked(self, "checkpoint_write_failed", h.begin)
            h.restart()
            resumed = h.begin()
            self.assertEqual(h.dispatch_keys(), [resumed["dispatchId"]])
            self.assertEqual(h.checkpoint()["state"], "running")


class CheckpointIntegrityTests(RecoveryTestCase):
    """A stale, foreign, tampered or missing checkpoint never drives recovery."""

    def test_checkpoint_behind_the_audit_is_refused(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.ended")
            stale = h.checkpoint_path.read_bytes()
            h.record(2, kind="session.idle")
            h.checkpoint_path.write_bytes(stale)
            os.chmod(h.checkpoint_path, 0o600)
            h.restart()
            self.assert_refused_unchanged(h, "checkpoint_stale", h.begin)

    def test_checkpoint_claiming_unaudited_events_is_refused(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.ended")
            forged = h.checkpoint()
            forged["processedEvents"] = forged["processedEvents"] + [
                {
                    "eventId": "DHE-00000000beef",
                    "sequence": 2,
                    "fingerprint": "sha256:" + "8" * 64,
                    "kind": "session.idle",
                }
            ]
            forged["expectedSequence"] = 3
            h.checkpoints.save(forged)
            h.restart()
            self.assert_refused_unchanged(h, "checkpoint_audit_mismatch", h.begin)

    def test_tampered_checkpoint_blocks_dispatch(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.ended")
            document = json.loads(h.checkpoint_path.read_text(encoding="utf-8"))
            document["expectedSequence"] = 1
            document["processedEvents"] = []
            h.checkpoint_path.write_text(canonical_json(document) + "\n", encoding="utf-8")
            h.restart()
            self.assert_refused_unchanged(h, "checkpoint_tampered", h.begin)

    def test_checkpoint_of_another_binding_is_refused(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.ended")
            h.restart()
            h.sessions = SessionRegistry()
            other = h.sessions.bind(h.binding_for(profile_id="pipe-readonly-other"))
            h.adapter = DeepSeekHarnessRuntimeAdapter(
                h.store, h.sessions, checkpoints=h.checkpoints
            )
            # The Pipe audit already owns attempt 1, so it refuses the foreign binding
            # before the checkpoint is even read.
            self.assert_refused_unchanged(h, "binding_immutable", h.begin, binding=other)

    def test_checkpoint_of_another_binding_is_refused_before_any_dispatch_is_audited(self) -> None:
        with recovery_harness() as h:
            failure = ControlPlaneStateError("synthetic audit failure")
            with mock.patch.object(h.store, "record_run_event", side_effect=failure):
                assert_blocked(self, "audit_write_failed", h.begin)
            self.assertEqual(h.dispatch_keys(), [])
            h.restart()
            h.sessions = SessionRegistry()
            other = h.sessions.bind(h.binding_for(profile_id="pipe-readonly-other"))
            h.adapter = DeepSeekHarnessRuntimeAdapter(
                h.store, h.sessions, checkpoints=h.checkpoints
            )
            self.assert_refused_unchanged(h, "checkpoint_binding_mismatch", h.begin, binding=other)

    def test_missing_checkpoint_with_audited_dispatch_requires_recovery(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.checkpoint_path.unlink()
            h.restart()
            self.assert_refused_unchanged(h, "recovery_required", h.begin)

    def test_no_raw_sentinel_reaches_checkpoint_or_disk(self) -> None:
        with recovery_harness() as h:
            h.begin()
            for metadata in (
                event_metadata(1, prompt=TEXT_SENTINEL),
                event_metadata(1, externalEventId=SECRET_SENTINEL),
            ):
                with self.assertRaises(ValueError):
                    h.adapter.record_event(
                        binding=h.binding, context=h.context,
                        event=type(h.event(1)).from_metadata(metadata),
                    )
            h.record(1, kind="tool.started", toolName=READ_TOOL)
            h.record(2, kind="tool.succeeded", toolName=READ_TOOL)
            h.store.close()
            h.store = LocalControlPlaneStore(h.db_path)
            for path in sorted(h.base.rglob("*")):
                if path.is_file():
                    content = path.read_bytes()
                    with self.subTest(file=path.name):
                        self.assertNotIn(TEXT_SENTINEL.encode(), content)
                        self.assertNotIn(SECRET_SENTINEL.encode(), content)
            self.assertEqual(
                sorted(item.name for item in h.checkpoint_dir.iterdir()),
                [h.checkpoint_path.name],
            )


class AuditAuthorityTests(RecoveryTestCase):
    """The Pipe audit, not the registry or checkpoint, owns attempts and blocks."""

    def rebuild(self, h: RecoveryHarness, bindings: list[Any], *, checkpoints: bool) -> None:
        h.sessions = SessionRegistry()
        for binding in bindings:
            h.sessions.bind(binding)
        h.adapter = DeepSeekHarnessRuntimeAdapter(
            h.store, h.sessions, checkpoints=h.checkpoints if checkpoints else None
        )

    def test_rebuilt_registry_cannot_rebind_or_go_back_to_an_audited_attempt(self) -> None:
        for checkpoints in (False, True):
            with self.subTest(checkpoint_store=checkpoints), recovery_harness() as h:
                if not checkpoints:
                    h.adapter = DeepSeekHarnessRuntimeAdapter(h.store, h.sessions)
                h.begin()
                h.record(1, kind="turn.started")
                h.record(2, kind="turn.ended")
                successor = h.sessions.bind(h.binding_for(session_id=SESSION_TWO, attempt=2))
                h.begin(binding=successor)
                h.restart()
                rebound = h.binding_for(session_id=SESSION_THREE, model_id=OTHER_MODEL_ID)
                self.rebuild(h, [rebound], checkpoints=checkpoints)
                self.assert_refused_unchanged(h, "binding_superseded", h.begin, binding=rebound)
                other_second = h.binding_for(session_id=SESSION_THREE, attempt=2)
                self.rebuild(h, [h.binding, other_second], checkpoints=checkpoints)
                self.assert_refused_unchanged(h, "binding_immutable", h.begin, binding=other_second)
                self.assertEqual(len(h.dispatch_keys()), 2)

    def test_mid_turn_attempt_cannot_be_replaced_after_its_checkpoint_is_lost(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.started")
            h.checkpoint_path.unlink()
            h.restart()
            rebound = h.binding_for(session_id=SESSION_THREE, model_id=OTHER_MODEL_ID)
            self.rebuild(h, [rebound], checkpoints=True)
            self.assert_refused_unchanged(h, "binding_immutable", h.begin, binding=rebound)
            self.rebuild(h, [h.binding], checkpoints=True)
            self.assert_refused_unchanged(h, "recovery_required", h.begin)

    def test_gap_block_survives_a_failed_checkpoint_write_and_a_restart(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="session.started")
            before = h.audit()
            with failing_checkpoint_save(on_call=1):
                assert_blocked(self, "checkpoint_write_failed", h.record, 3, kind="turn.started")
            assert_block_marker(self, before, h.audit())
            self.assertEqual(h.checkpoint()["state"], "running")
            h.restart()
            self.assert_refused_unchanged(h, "stream_blocked", h.begin)

    def test_a_re_signed_running_checkpoint_cannot_clear_a_block(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="session.started")
            assert_blocked(self, "sequence_gap", h.record, 3, kind="turn.started")
            h.checkpoints.save({**h.checkpoint(), "state": "running", "blockerCode": None})
            h.restart()
            self.assert_refused_unchanged(h, "stream_blocked", h.begin)

    def test_block_marker_audit_failure_is_raised_not_swallowed(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="session.started")
            failure = ControlPlaneStateError("synthetic audit failure")
            with mock.patch.object(h.store, "record_run_event", side_effect=failure):
                assert_blocked(self, "audit_write_failed", h.record, 3, kind="turn.started")
            # The checkpoint still carries the block as a second line of defence.
            self.assertEqual(h.checkpoint()["state"], "blocked")
            assert_blocked(self, "stream_blocked", h.record, 2, kind="turn.started")

    def test_marker_blocks_every_adapter_that_holds_the_attempt(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.started")
            h.record(2, kind="turn.ended")
            first = h.adapter
            others = []
            for _ in range(2):
                h.adapter = DeepSeekHarnessRuntimeAdapter(
                    h.store, h.sessions, checkpoints=h.checkpoints
                )
                self.assertIs(h.begin()["recovered"], True)
                others.append(h.adapter)
            h.adapter = first
            assert_blocked(self, "sequence_gap", h.record, 4, kind="session.idle")
            # The other adapters never saw the gap; only the audit marker stops them.
            h.adapter = others[0]
            assert_blocked(
                self,
                "stream_blocked",
                h.adapter.propose,
                binding=h.binding,
                context=h.context,
                result_ref="review:PIP-899:notes",
                result_fingerprint="sha256:" + "9" * 64,
                occurred_at="2026-09-10T12:31:00Z",
            )
            h.adapter = others[1]
            assert_blocked(self, "stream_blocked", h.record, 3, kind="session.idle")
            self.assertEqual(h.checkpoint()["state"], "blocked")
            self.assertNotIn("run.completed", [item["eventType"] for item in h.audit()])

    def test_any_storage_failure_on_the_marker_still_blocks_the_checkpoint(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="session.started")
            failure = sqlite3.OperationalError("database is locked")
            with mock.patch.object(h.store, "record_run_event", side_effect=failure):
                assert_blocked(self, "audit_write_failed", h.record, 3, kind="turn.started")
            self.assertEqual(h.checkpoint()["state"], "blocked")
            self.assertEqual(h.checkpoint()["blockerCode"], "sequence_gap")
            h.restart()
            self.assert_refused_unchanged(h, "stream_blocked", h.begin)
