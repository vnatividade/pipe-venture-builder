from __future__ import annotations

import json
from typing import Any
from unittest import TestCase, mock

from pipe_venture_builder.adapters.deepseek_harness import (
    BLOCKER_CODES,
    COMPATIBILITY_MATRIX,
    MAX_FRAME_BYTES,
    DeepSeekHarnessNormalizer,
    DeepSeekHarnessRuntimeEvent,
    FakeNdjsonTransport,
    TransportSignal,
    drive_session,
)
from pipe_venture_builder.control_plane import ControlPlaneStateError, LocalControlPlaneStore
from pipe_venture_builder.control_plane.model import fingerprint
from tests.deepseek_harness.fixtures import (
    RAW_ARGUMENTS,
    RAW_RESULT,
    chunked,
    event_frame,
    line,
    message,
    reasoning,
    review_turn,
    tool_call,
    tool_result,
)
from tests.deepseek_harness.helpers import (
    READ_TOOL,
    SECRET_SENTINEL,
    SESSION_ONE,
    SESSION_TWO,
    SESSION_THREE,
    TEXT_SENTINEL,
    assert_block_marker,
    assert_blocked,
    assert_metadata_only,
    forbid_host_access,
)
from tests.deepseek_harness.test_handoff import complete, propose
from tests.deepseek_harness.test_recovery import RecoveryTestCase, recovery_harness
from tests.helpers import REPOSITORY_ROOT


DOCUMENT = REPOSITORY_ROOT / "docs" / "deepseek-harness" / "contract-spike.md"
OPENING = "nenhum runtime/provider real foi executado; compatibilidade não foi provada"
REFUSED_AT = "2026-09-10T12:30:00Z"


def normalize_all(frames: list[dict[str, Any]]) -> list[DeepSeekHarnessRuntimeEvent]:
    normalizer = DeepSeekHarnessNormalizer(SESSION_ONE)
    events = []
    for frame in frames:
        event = normalizer.normalize(line(frame).rstrip(b"\n"))
        if event is not None:
            events.append(event)
    return events


def refuse(test: TestCase, code: str, frames: list[Any]) -> None:
    """Feed frames (dicts or raw bytes); the last one must be refused with ``code``."""

    normalizer = DeepSeekHarnessNormalizer(SESSION_ONE)
    raws = [item if isinstance(item, bytes) else line(item).rstrip(b"\n") for item in frames]
    for raw in raws[:-1]:
        normalizer.normalize(raw)
    assert_blocked(test, code, normalizer.normalize, raws[-1])
    # Fail closed: the normalizer never resynchronizes after a refusal.
    assert_blocked(test, "stream_blocked", normalizer.normalize, line(message()).rstrip(b"\n"))


class FakeTransportTests(TestCase):
    """In-process NDJSON transport: no process, socket, clock or file."""

    def test_success_reassembles_partial_frames_across_chunks(self) -> None:
        frames = review_turn()
        transport = FakeNdjsonTransport(chunked(frames, size=5) + [TransportSignal.EOF])
        read = [transport.read_frame() for _ in frames]
        self.assertEqual(read, [line(frame).rstrip(b"\n") for frame in frames])
        assert_blocked(self, "transport_eof", transport.read_frame)
        assert_blocked(self, "transport_eof", transport.read_frame)

    def test_several_frames_in_one_chunk_are_split(self) -> None:
        frames = review_turn()[:3]
        transport = FakeNdjsonTransport([b"".join(line(frame) for frame in frames)])
        self.assertEqual(len([transport.read_frame() for _ in frames]), 3)
        assert_blocked(self, "transport_eof", transport.read_frame)

    def test_timeout_is_scripted_and_poisons_the_transport(self) -> None:
        transport = FakeNdjsonTransport([line(review_turn()[0])[:9], TransportSignal.TIMEOUT, b"x\n"])
        assert_blocked(self, "transport_timeout", transport.read_frame)
        assert_blocked(self, "transport_timeout", transport.read_frame)

    def test_oversized_frame_is_refused_before_completion(self) -> None:
        for chunks in (
            [b"a" * (MAX_FRAME_BYTES + 1)],
            [b"a" * MAX_FRAME_BYTES, b"b" * 8 + b"\n"],
            [b"a" * (MAX_FRAME_BYTES + 1) + b"\n"],
        ):
            with self.subTest(size=sum(len(chunk) for chunk in chunks)):
                transport = FakeNdjsonTransport(chunks)
                assert_blocked(self, "frame_too_large", transport.read_frame)

    def test_script_must_hold_only_bytes_or_signals(self) -> None:
        for script in ([TEXT_SENTINEL], [1], None, "abc", [b"ok\n", object()]):
            with self.subTest(script=type(script).__name__):
                assert_blocked(self, "contract_violation", FakeNdjsonTransport, script)

    def test_requests_keep_only_allowlisted_method_and_identifier(self) -> None:
        transport = FakeNdjsonTransport([])
        self.assertEqual(transport.send("initialize"), 1)
        self.assertEqual(transport.send("session/prompt"), 2)
        self.assertEqual(transport.sent, ((1, "initialize"), (2, "session/prompt")))
        for method in ("session/delete", "fs/write", TEXT_SENTINEL, None):
            with self.subTest(method=repr(method)[:16]):
                assert_blocked(self, "contract_violation", transport.send, method)

    def test_transport_and_normalizer_never_touch_the_host(self) -> None:
        frames = review_turn()
        with forbid_host_access(filesystem=True) as log:
            transport = FakeNdjsonTransport(chunked(frames) + [TransportSignal.EOF])
            normalizer = DeepSeekHarnessNormalizer(SESSION_ONE)
            for _ in frames:
                normalizer.normalize(transport.read_frame())
        self.assertEqual(log, [])


class NormalizerTests(TestCase):
    """Raw content lives only inside normalization; only metadata comes out."""

    def test_review_turn_becomes_allowlisted_payload_free_events(self) -> None:
        events = normalize_all(review_turn())
        self.assertEqual(
            [event.kind for event in events],
            ["session.started", "turn.started", "tool.started", "tool.succeeded", "turn.ended", "session.idle"],
        )
        self.assertEqual([event.sequence for event in events], [1, 2, 3, 4, 5, 6])
        tool_started, tool_succeeded = events[2], events[3]
        self.assertEqual(tool_started.tool_name, READ_TOOL)
        self.assertEqual(tool_started.payload_fingerprint, fingerprint(RAW_ARGUMENTS))
        self.assertEqual(tool_succeeded.tool_name, READ_TOOL)
        self.assertEqual(tool_succeeded.payload_fingerprint, fingerprint(RAW_RESULT))
        encoded = json.dumps([event.document() for event in events])
        for sentinel in (TEXT_SENTINEL, SECRET_SENTINEL, "README.md"):
            self.assertNotIn(sentinel, encoded)
        for event in events:
            assert_metadata_only(self, event.document())

    def test_content_frames_produce_no_event(self) -> None:
        normalizer = DeepSeekHarnessNormalizer(SESSION_ONE)
        normalizer.normalize(line(event_frame(1, {"type": "turn_started"})).rstrip(b"\n"))
        for frame in (reasoning(), message(), message()):
            self.assertIsNone(normalizer.normalize(line(frame).rstrip(b"\n")))

    def test_unknown_tool_is_refused(self) -> None:
        refuse(self, "tool_not_allowlisted", [event_frame(1, {"type": "turn_started"}), tool_call(2, name="shell")])

    def test_turn_protocol_violations_are_refused(self) -> None:
        started = event_frame(1, {"type": "turn_started"})
        for name, frames in (
            ("turn started twice", [started, event_frame(2, {"type": "turn_started"})]),
            ("turn end without turn", [event_frame(1, {"type": "turn_end"})]),
            ("turn end with open tool call", [started, tool_call(2), event_frame(3, {"type": "turn_end"})]),
            ("idle inside a turn", [started, event_frame(2, {"type": "status", "status": "idle"})]),
            ("message outside a turn", [message()]),
            ("tool call outside a turn", [tool_call(1)]),
        ):
            with self.subTest(case=name):
                refuse(self, "turn_state_invalid", frames)

    def test_frames_of_another_session_are_refused(self) -> None:
        refuse(self, "session_mismatch", [event_frame(1, {"type": "turn_started"}, session_id=SESSION_TWO)])

    def test_event_metadata_is_validated_by_the_event_model(self) -> None:
        for name, frame in (
            ("secret-shaped event id", event_frame(1, {"type": "turn_started"}, event_id=SECRET_SENTINEL)),
            ("timestamp without zone", event_frame(1, {"type": "turn_started"}, timestamp="2026-09-10T12:00:00")),
            ("sequence zero", event_frame(0, {"type": "turn_started"})),
        ):
            with self.subTest(case=name):
                refuse(self, "event_field_invalid", [frame])

    def test_responses_must_answer_an_outstanding_request(self) -> None:
        normalizer = DeepSeekHarnessNormalizer(SESSION_ONE)
        normalizer.expect_response(1)
        ok = {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "synthetic"}}
        self.assertIsNone(normalizer.normalize(line(ok).rstrip(b"\n")))
        refuse(self, "frame_invalid", [ok])
        errored = DeepSeekHarnessNormalizer(SESSION_ONE)
        errored.expect_response(2)
        failure = {"jsonrpc": "2.0", "id": 2, "error": {"code": -1, "message": TEXT_SENTINEL}}
        assert_blocked(self, "runtime_error", errored.normalize, line(failure).rstrip(b"\n"))

    def test_normalizer_requires_a_valid_session(self) -> None:
        for value in (None, "", SECRET_SENTINEL, "has space"):
            with self.subTest(value=repr(value)[:12]):
                assert_blocked(self, "binding_field_invalid", DeepSeekHarnessNormalizer, value)


class RefusalHygieneTests(TestCase):
    """D13: a decode refusal keeps no reference to the raw frame, even in __context__."""

    def test_decode_refusals_carry_no_context_or_cause(self) -> None:
        frames = (
            ("invalid json", ('{"text": "' + TEXT_SENTINEL + '"').encode("utf-8")),
            ("invalid utf-8", TEXT_SENTINEL.encode("utf-8") + b"\xff"),
            ("non-finite", ('{"text": "' + TEXT_SENTINEL + '", "x": NaN}').encode("utf-8")),
        )
        for name, frame in frames:
            with self.subTest(frame=name):
                with self.assertRaises(ValueError) as caught:
                    DeepSeekHarnessNormalizer(SESSION_ONE).normalize(frame)
                self.assertEqual(caught.exception.code, "frame_invalid")
                self.assertIsNone(caught.exception.__context__)
                self.assertIsNone(caught.exception.__cause__)


class CompatibilityMatrixTests(TestCase):
    """Synthetic protocol risks: hypotheses and refusals, never claims about DSH."""

    def test_matrix_literal_tool_call(self) -> None:
        started = event_frame(1, {"type": "turn_started"})
        for text in (
            '<tool_call>{"name": "read_file"}</tool_call>',
            '{"name": "read_file", "arguments": {"path": "x"}}',
            "<|tool_call_begin|>read_file",
        ):
            with self.subTest(text=text[:16]):
                refuse(self, "tool_call_literal", [started, message(text)])

    def test_matrix_malformed_tool_call(self) -> None:
        started = event_frame(1, {"type": "turn_started"})
        for name, frames in (
            ("arguments as broken json text", [started, tool_call(2, arguments='{"path": "README.md"')]),
            ("arguments as a list", [started, tool_call(2, arguments=["README.md"])]),
            ("missing call id", [started, event_frame(2, {"type": "tool_call", "name": READ_TOOL, "arguments": {}})]),
            ("result for unknown call", [started, tool_result(2, call_id="call-9")]),
            ("duplicate open call", [started, tool_call(2), tool_call(3)]),
        ):
            with self.subTest(case=name):
                refuse(self, "tool_call_malformed", frames)

    def test_matrix_truncated_frame(self) -> None:
        payload = line(review_turn()[0])
        transport = FakeNdjsonTransport([payload[: len(payload) // 2], TransportSignal.EOF])
        assert_blocked(self, "frame_truncated", transport.read_frame)
        transport = FakeNdjsonTransport([payload[:-1]])
        assert_blocked(self, "frame_truncated", transport.read_frame)

    def test_matrix_inconsistent_reasoning(self) -> None:
        started = event_frame(1, {"type": "turn_started"})
        for name, frames in (
            ("reasoning outside a turn", [reasoning()]),
            ("reasoning after the answer", [started, message(), reasoning()]),
        ):
            with self.subTest(case=name):
                refuse(self, "reasoning_inconsistent", frames)

    def test_matrix_timeout(self) -> None:
        transport = FakeNdjsonTransport([TransportSignal.TIMEOUT])
        assert_blocked(self, "transport_timeout", transport.read_frame)

    def test_matrix_eof(self) -> None:
        transport = FakeNdjsonTransport([line(review_turn()[0]), TransportSignal.EOF])
        transport.read_frame()
        assert_blocked(self, "transport_eof", transport.read_frame)

    def test_matrix_invalid_framing(self) -> None:
        base = review_turn()[0]
        for name, raw in (
            ("not json", b"{" + TEXT_SENTINEL.encode()),
            ("not an object", b"[1, 2]"),
            ("not utf-8", b"\xff\xfe" + SECRET_SENTINEL.encode()),
            ("wrong jsonrpc version", line({**base, "jsonrpc": "1.0"}).rstrip(b"\n")),
            ("extra top-level key", line({**base, "raw": TEXT_SENTINEL}).rstrip(b"\n")),
            (
                "duplicate key in an otherwise valid frame",
                b'{"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"dsh-session-0001",'
                b'"seq":1,"seq":2,"eventId":"dsh-evt-0001","timestamp":"2026-09-10T12:01:00Z",'
                b'"update":{"type":"session_started"}}}',
            ),
            ("extra params key", line({**base, "params": {**base["params"], "prompt": TEXT_SENTINEL}}).rstrip(b"\n")),
            ("empty line", b""),
            ("nan constant", b'{"jsonrpc":"2.0","method":"session/update","params":{"seq":NaN}}'),
        ):
            with self.subTest(case=name):
                refuse(self, "frame_invalid", [raw])

    def test_matrix_unknown_type(self) -> None:
        for name, frame in (
            ("unknown update type", event_frame(1, {"type": "subagent_spawned"})),
            ("unknown status", event_frame(1, {"type": "status", "status": "busy"})),
            ("unknown method", {"jsonrpc": "2.0", "method": "session/permission", "params": {}}),
            ("server request", {"jsonrpc": "2.0", "id": 7, "method": "fs/read", "params": {}}),
        ):
            with self.subTest(case=name):
                refuse(self, "frame_type_unknown", [frame])

    def test_every_scenario_has_a_named_test_a_stable_code_and_documentation(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertTrue(COMPATIBILITY_MATRIX)
        for scenario, code in COMPATIBILITY_MATRIX:
            with self.subTest(scenario=scenario):
                self.assertTrue(callable(getattr(self, f"test_matrix_{scenario}", None)))
                self.assertIn(code, BLOCKER_CODES)
                self.assertIn(f"`{scenario}`", document)
                self.assertIn(f"`{code}`", document)


class ContractSpikeDocumentTests(TestCase):
    def test_document_opens_with_the_non_compatibility_statement(self) -> None:
        body = [
            item.strip()
            for item in DOCUMENT.read_text(encoding="utf-8").splitlines()
            if item.strip() and not item.startswith("#")
        ]
        self.assertIn(OPENING, body[0])
        text = DOCUMENT.read_text(encoding="utf-8")
        for sentinel in (TEXT_SENTINEL, SECRET_SENTINEL):
            self.assertNotIn(sentinel, text)


class FakeSessionEndToEndTests(RecoveryTestCase):
    """Transport -> normalizer -> adapter; EOF and timeout never complete a run."""

    def drive(self, h: Any, chunks: list[Any]) -> None:
        drive_session(
            h.adapter,
            binding=h.binding,
            context=h.context,
            transport=FakeNdjsonTransport(chunks),
            normalizer=DeepSeekHarnessNormalizer(h.binding.session_id),
            clock=lambda: REFUSED_AT,
        )

    def test_fake_session_is_audited_payload_free_and_eof_never_completes(self) -> None:
        with recovery_harness() as h:
            h.begin()
            with self.assertRaises(ValueError) as caught:
                self.drive(h, chunked(review_turn()) + [TransportSignal.EOF])
            self.assertEqual(caught.exception.code, "transport_eof")
            self.assertEqual(h.store.get_run(h.run_id)["status"], "running")
            self.assertNotIn("run.completed", [item["eventType"] for item in h.audit()])
            self.assertEqual(len(h.runtime_keys()), 6)
            self.assertEqual(h.checkpoint()["expectedSequence"], 7)
            self.assertTrue(h.store.verify_audit_chain(h.run_id))

            # Completion is still only the dedicated Pipe method.
            self.assertEqual(complete(h, propose(h))["state"], "completed")
            h.store.close()
            h.store = LocalControlPlaneStore(h.db_path)
            for path in sorted(h.base.rglob("*")):
                if path.is_file():
                    content = path.read_bytes()
                    with self.subTest(file=path.name):
                        for sentinel in (TEXT_SENTINEL, SECRET_SENTINEL):
                            self.assertNotIn(sentinel.encode(), content)

    def test_eof_mid_turn_blocks_the_attempt_durably(self) -> None:
        with recovery_harness() as h:
            h.begin()
            frames = review_turn()[:4]  # tool call in flight
            before = h.audit()
            with self.assertRaises(ValueError) as caught:
                self.drive(h, chunked(frames) + [TransportSignal.EOF])
            self.assertEqual(caught.exception.code, "transport_eof")
            assert_block_marker(self, before + h.audit()[len(before):-1], h.audit())
            self.assertEqual(h.store.get_run(h.run_id)["status"], "interrupted")
            self.assertEqual(h.checkpoint()["state"], "blocked")
            h.restart()
            assert_blocked(self, "stream_blocked", h.begin)

    def test_timeout_and_refused_frames_block_without_completing(self) -> None:
        with recovery_harness() as h:
            h.begin()
            with self.assertRaises(ValueError) as caught:
                self.drive(h, chunked(review_turn()[:2]) + [TransportSignal.TIMEOUT])
            self.assertEqual(caught.exception.code, "transport_timeout")
            self.assertEqual(h.store.get_run(h.run_id)["status"], "interrupted")

        with recovery_harness() as h:
            h.begin()
            frames = [event_frame(1, {"type": "turn_started"}), message("<tool_call>read_file</tool_call>")]
            with self.assertRaises(ValueError) as caught:
                self.drive(h, [line(frame) for frame in frames] + [TransportSignal.EOF])
            self.assertEqual(caught.exception.code, "tool_call_literal")
            self.assertNotIn(TEXT_SENTINEL, str(caught.exception))
            self.assertEqual(len(h.runtime_keys()), 1)
            self.assertNotIn("run.completed", [item["eventType"] for item in h.audit()])


class RefusalPropagationTests(RecoveryTestCase):
    """Every matrix refusal blocks the attempt; no fresh normalizer or restart resumes it."""

    SCENARIOS = (
        (
            "unknown_type",
            "frame_type_unknown",
            [line(event_frame(1, {"type": "session_started"})), line(event_frame(2, {"type": "plan_update"}))],
        ),
        (
            "invalid_framing",
            "frame_invalid",
            [line(event_frame(1, {"type": "session_started"})), b"{not json\n"],
        ),
        (
            "truncated_frame",
            "frame_truncated",
            [line(event_frame(1, {"type": "session_started"})), b'{"jsonrpc":"2.0"', TransportSignal.EOF],
        ),
        (
            "literal_tool_call",
            "tool_call_literal",
            [line(event_frame(1, {"type": "turn_started"})), line(message("<tool_call>read_file</tool_call>"))],
        ),
        (
            "malformed_tool_call",
            "tool_call_malformed",
            [line(event_frame(1, {"type": "turn_started"})), line(tool_call(2, arguments="not-an-object"))],
        ),
        (
            "inconsistent_reasoning",
            "reasoning_inconsistent",
            [line(event_frame(1, {"type": "session_started"})), line(reasoning())],
        ),
        (
            "timeout",
            "transport_timeout",
            [line(event_frame(1, {"type": "session_started"})), TransportSignal.TIMEOUT],
        ),
        (
            "eof_mid_turn",
            "transport_eof",
            [line(event_frame(1, {"type": "turn_started"})), TransportSignal.EOF],
        ),
    )

    def drive(self, h: Any, chunks: list[Any]) -> None:
        drive_session(
            h.adapter,
            binding=h.binding,
            context=h.context,
            transport=FakeNdjsonTransport(chunks),
            normalizer=DeepSeekHarnessNormalizer(h.binding.session_id),
            clock=lambda: REFUSED_AT,
        )

    def test_every_refusal_blocks_durably_and_cannot_be_resumed_or_completed(self) -> None:
        for name, code, chunks in self.SCENARIOS:
            with self.subTest(scenario=name), recovery_harness() as h:
                h.begin()
                with self.assertRaises(ValueError) as caught:
                    self.drive(h, chunks)
                self.assertEqual(caught.exception.code, code)
                self.assertIsNone(caught.exception.__context__)
                self.assertNotIn(TEXT_SENTINEL, str(caught.exception))
                self.assertEqual(len(h.runtime_keys()), 1)
                markers = [
                    item for item in h.audit()
                    if (item["references"]["idempotencyKey"] or "").endswith(":blocked")
                ]
                self.assertEqual(len(markers), 1)
                self.assertEqual(h.store.get_run(h.run_id)["status"], "interrupted")
                self.assertEqual(h.checkpoint()["state"], "blocked")
                self.assertEqual(h.checkpoint()["blockerCode"], code)

                # A fresh normalizer on the same adapter cannot resume the stream.
                idle = [line(event_frame(2, {"type": "status", "status": "idle"}))]
                with self.assertRaises(ValueError) as resumed:
                    self.drive(h, idle)
                self.assertEqual(resumed.exception.code, "stream_blocked")
                assert_blocked(self, "stream_blocked", propose, h)
                # Nor can a restart, even after the checkpoint is re-signed as running.
                h.checkpoints.save({**h.checkpoint(), "state": "running", "blockerCode": None})
                h.restart()
                assert_blocked(self, "stream_blocked", h.begin)
                self.assertEqual(len(markers), 1)
                self.assertNotIn("run.completed", [item["eventType"] for item in h.audit()])

    def test_refusal_without_a_checkpoint_store_is_still_durable(self) -> None:
        from tests.deepseek_harness.test_adapter import harness

        with harness() as h:
            h.begin()
            with self.assertRaises(ValueError) as caught:
                self.drive(h, self.SCENARIOS[0][2])
            self.assertEqual(caught.exception.code, "frame_type_unknown")
            h.adapter = type(h.adapter)(h.store, h.sessions)
            assert_blocked(self, "stream_blocked", h.begin)

    def test_a_new_attempt_may_follow_a_blocked_one(self) -> None:
        with recovery_harness() as h:
            h.begin()
            with self.assertRaises(ValueError):
                self.drive(h, self.SCENARIOS[0][2])
            h.binding = h.sessions.bind(h.binding_for(session_id=SESSION_THREE, attempt=2))
            resumed = h.begin()
            self.assertEqual(resumed["attempt"], 2)
            self.assertEqual(h.store.get_run(h.run_id)["status"], "running")

    def test_clean_eof_at_rest_is_reported_without_a_block(self) -> None:
        with recovery_harness() as h:
            h.begin()
            before = h.audit()
            with self.assertRaises(ValueError) as caught:
                self.drive(h, chunked(review_turn()) + [TransportSignal.EOF])
            self.assertEqual(caught.exception.code, "transport_eof")
            self.assertFalse(
                any((item["references"]["idempotencyKey"] or "").endswith(":blocked") for item in h.audit())
            )
            self.assertEqual(h.audit()[: len(before)], before)
            self.assertEqual(h.checkpoint()["state"], "running")

    def test_refuse_requires_a_stable_code_a_timestamp_and_a_dispatch(self) -> None:
        with recovery_harness() as h:
            def refuse(**overrides: Any) -> None:
                request = {
                    "binding": h.binding,
                    "context": h.context,
                    "code": "frame_invalid",
                    "occurred_at": REFUSED_AT,
                }
                h.adapter.refuse(**{**request, **overrides})

            assert_blocked(self, "dispatch_missing", refuse)
            h.begin()
            assert_blocked(self, "contract_violation", lambda: refuse(code="not-a-code"))
            assert_blocked(self, "timestamp_invalid", lambda: refuse(occurred_at="soon"))
            self.assertEqual(h.checkpoint()["state"], "running")
            with self.assertRaises(TypeError):
                drive_session(
                    h.adapter,
                    binding=h.binding,
                    context=h.context,
                    transport=FakeNdjsonTransport([]),
                    normalizer=DeepSeekHarnessNormalizer(h.binding.session_id),
                )


class RefusalBoundaryTests(RecoveryTestCase):
    """A refusal never reopens a terminal run and never loses an unpersisted block."""

    def refuse(self, h: Any, code: str) -> None:
        h.adapter.refuse(binding=h.binding, context=h.context, code=code, occurred_at=REFUSED_AT)

    def test_refusal_after_completion_or_failure_never_rewrites_the_run(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.started")
            h.record(2, kind="turn.ended")
            complete(h, propose(h))
            self.assert_refused_unchanged(h, "run_terminal", self.refuse, h, "transport_timeout")
            self.assertEqual(h.store.get_run(h.run_id)["status"], "completed")

        with recovery_harness() as h:
            h.begin()
            h.store.update_run_status(h.run_id, "failed", at=REFUSED_AT)
            self.assert_refused_unchanged(h, "run_terminal", self.refuse, h, "frame_invalid")
            self.assertEqual(h.store.get_run(h.run_id)["status"], "failed")

    def test_refusal_persists_a_block_that_was_only_in_memory(self) -> None:
        with recovery_harness() as h:
            h.begin()
            h.record(1, kind="turn.started")
            failure = ControlPlaneStateError("synthetic audit failure")
            with mock.patch.object(h.store, "record_run_event", side_effect=failure):
                assert_blocked(self, "audit_write_failed", h.record, 2, kind="turn.ended")
            self.assertEqual(h.checkpoint()["state"], "running")
            before = h.audit()
            assert_blocked(self, "tool_call_literal", self.refuse, h, "tool_call_literal")
            assert_block_marker(self, before, h.audit())
            self.assertEqual(h.checkpoint()["state"], "blocked")
            h.restart()
            assert_blocked(self, "stream_blocked", h.begin)
