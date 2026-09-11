from __future__ import annotations

from dataclasses import replace
from typing import Any
from unittest import TestCase

from pipe_venture_builder.adapters.deepseek_harness import (
    DeepSeekHarnessEventSequence,
    DeepSeekHarnessRuntimeEvent,
)
from tests.deepseek_harness.helpers import (
    FINGERPRINT,
    READ_TOOL,
    SECRET_SENTINEL,
    SESSION_ONE,
    TEXT_SENTINEL,
    assert_blocked,
    assert_metadata_only,
    event_at,
    event_metadata,
)


PAYLOAD_FINGERPRINT = "sha256:" + "4" * 64
TOOL_KINDS = ("tool.started", "tool.succeeded")
NON_TOOL_KINDS = ("session.started", "turn.started", "turn.ended", "session.idle")


def event(sequence: int = 1, **overrides: Any) -> DeepSeekHarnessRuntimeEvent:
    return DeepSeekHarnessRuntimeEvent.from_metadata(event_metadata(sequence, **overrides))


class RuntimeEventModelTests(TestCase):
    """ADR-004 D4: allowlisted, payload-free event metadata only."""

    def test_event_is_metadata_only_with_experimental_dhe_identity(self) -> None:
        built = event(
            4, kind="tool.succeeded", toolName=READ_TOOL, payloadFingerprint=PAYLOAD_FINGERPRINT
        )
        document = built.document()

        self.assertRegex(built.event_id, r"^DHE-[a-f0-9]{12}$")
        self.assertRegex(built.fingerprint, FINGERPRINT)
        expected = {
            "eventId": built.event_id,
            "externalEventId": "dsh-evt-0004",
            "sessionId": SESSION_ONE,
            "sequence": 4,
            "kind": "tool.succeeded",
            "occurredAt": event_at(4),
            "toolName": READ_TOOL,
            "payloadFingerprint": PAYLOAD_FINGERPRINT,
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(document[key], value)
        constraints = document["constraints"]
        self.assertIs(constraints["rawPayloadPersisted"], False)
        self.assertIs(constraints["runtimeApprovalIsAuthority"], False)
        # DHE-* is an experimental spike identifier, never a canonical identity.
        self.assertIs(constraints["canonicalRuntimeIdentity"], False)
        assert_metadata_only(self, document)

    def test_identity_is_stable_and_fingerprint_covers_content(self) -> None:
        self.assertEqual(event(), event())
        self.assertEqual(event().fingerprint, event().fingerprint)
        changed = event(kind="session.started")
        self.assertEqual(changed.event_id, event().event_id)
        self.assertNotEqual(changed.fingerprint, event().fingerprint)
        self.assertNotEqual(event(sessionId="dsh-session-0002").event_id, event().event_id)

    def test_allowlisted_kinds_are_accepted(self) -> None:
        for kind in NON_TOOL_KINDS:
            with self.subTest(kind=kind):
                self.assertEqual(event(kind=kind).kind, kind)
        for kind in TOOL_KINDS:
            with self.subTest(kind=kind):
                self.assertEqual(event(kind=kind, toolName=READ_TOOL).tool_name, READ_TOOL)

    def test_unknown_kinds_are_rejected_without_echo(self) -> None:
        for kind in (
            "message.delta",
            "reasoning.delta",
            "tool.output",
            "shell.executed",
            "subagent.started",
            "session.status",
            "SESSION.IDLE",
            TEXT_SENTINEL,
            "",
            None,
            1,
        ):
            with self.subTest(kind=kind):
                assert_blocked(
                    self, "event_kind_unknown", DeepSeekHarnessRuntimeEvent.from_metadata,
                    event_metadata(kind=kind),
                )

    def test_runtime_authority_kinds_are_forbidden(self) -> None:
        # ADR-004 D3/D6: DSH can neither approve nor complete a Pipe run.
        for kind in ("approval.granted", "run.completed"):
            with self.subTest(kind=kind):
                assert_blocked(
                    self, "event_kind_forbidden", DeepSeekHarnessRuntimeEvent.from_metadata,
                    event_metadata(kind=kind),
                )

    def test_unknown_keys_are_rejected_without_echo(self) -> None:
        for extra in (
            {"prompt": TEXT_SENTINEL},
            {"message": TEXT_SENTINEL},
            {"reasoning": TEXT_SENTINEL},
            {"arguments": {"path": TEXT_SENTINEL}},
            {"toolResult": TEXT_SENTINEL},
            {"stdout": TEXT_SENTINEL},
            {"stderr": TEXT_SENTINEL},
            {"frame": TEXT_SENTINEL},
            {"env": {"TOKEN": SECRET_SENTINEL}},
            {SECRET_SENTINEL: 1},
            {1: "x"},
        ):
            with self.subTest(extra=[str(key)[:8] for key in extra]):
                assert_blocked(
                    self, "event_field_unknown", DeepSeekHarnessRuntimeEvent.from_metadata,
                    {**event_metadata(), **extra},
                )

    def test_missing_required_fields_and_non_mapping_are_rejected(self) -> None:
        for field in ("externalEventId", "sessionId", "sequence", "kind", "occurredAt"):
            with self.subTest(missing=field):
                metadata = event_metadata()
                del metadata[field]
                assert_blocked(
                    self, "event_field_invalid", DeepSeekHarnessRuntimeEvent.from_metadata, metadata
                )
        for value in (None, [], "turn.started", list(event_metadata().items())):
            with self.subTest(value=type(value).__name__):
                assert_blocked(
                    self, "event_field_invalid", DeepSeekHarnessRuntimeEvent.from_metadata, value
                )

    def test_malformed_values_are_rejected_without_echo(self) -> None:
        identifiers = ("", None, 7, "has space", "/absolute", "x" * 600, SECRET_SENTINEL)
        cases: dict[str, tuple[Any, ...]] = {
            "externalEventId": identifiers,
            "sessionId": identifiers,
            "sequence": (0, -1, True, False, "1", 1.5, None, 2**63),
            "occurredAt": ("2026-09-10", "2026-09-10T12:00:00", "yesterday", "", None, 1),
            "payloadFingerprint": (
                "sha256:abc",
                "sha256:" + "A" * 64,
                "md5:" + "1" * 32,
                "",
                1,
                SECRET_SENTINEL,
            ),
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=repr(value)[:20]):
                    assert_blocked(
                        self, "event_field_invalid", DeepSeekHarnessRuntimeEvent.from_metadata,
                        {**event_metadata(), field: value},
                    )

    def test_tool_names_are_allowlisted_and_only_on_tool_kinds(self) -> None:
        for name in ("shell", "write_file", "apply_patch", "", None, TEXT_SENTINEL, SECRET_SENTINEL):
            with self.subTest(name=name):
                assert_blocked(
                    self, "tool_not_allowlisted", DeepSeekHarnessRuntimeEvent.from_metadata,
                    event_metadata(kind="tool.started", toolName=name),
                )
        for kind in NON_TOOL_KINDS:
            with self.subTest(kind=kind):
                assert_blocked(
                    self, "event_field_invalid", DeepSeekHarnessRuntimeEvent.from_metadata,
                    event_metadata(kind=kind, toolName=READ_TOOL),
                )

    def test_event_is_immutable_and_direct_construction_is_validated(self) -> None:
        built = event()
        with self.assertRaises(AttributeError):
            built.kind = "run.completed"  # type: ignore[misc]
        for code, changes in (
            ("event_kind_forbidden", {"kind": "run.completed"}),
            ("event_kind_unknown", {"kind": "message.delta"}),
            ("event_field_invalid", {"sequence": 0}),
            ("event_field_invalid", {"session_id": SECRET_SENTINEL}),
        ):
            with self.subTest(changes=changes):
                assert_blocked(self, code, replace, built, **changes)
        document = built.document()
        document["kind"] = "run.completed"
        self.assertEqual(built.document()["kind"], "turn.started")


class EventSequenceTests(TestCase):
    """ADR-004 D4/D10: contiguous from one, idempotent duplicates, fail closed."""

    def observe_all(self, sequence: DeepSeekHarnessEventSequence, *numbers: int) -> None:
        for number in numbers:
            self.assertIs(sequence.observe(event(number)), True)

    def test_contiguous_sequence_from_one_is_accepted(self) -> None:
        sequence = DeepSeekHarnessEventSequence()
        self.assertEqual(sequence.expected_sequence, 1)
        self.observe_all(sequence, 1, 2, 3)
        self.assertEqual(sequence.expected_sequence, 4)
        self.assertIsNone(sequence.blocked_code)

    def test_identical_retransmission_is_idempotent(self) -> None:
        sequence = DeepSeekHarnessEventSequence()
        self.observe_all(sequence, 1, 2, 3)
        for number in (1, 3, 2):
            with self.subTest(retransmitted=number):
                self.assertIs(sequence.observe(event(number)), False)
        self.assertEqual(sequence.expected_sequence, 4)
        self.assertIsNone(sequence.blocked_code)

    def test_gap_and_reorder_fail_closed_and_stay_blocked(self) -> None:
        for name, accepted, offending in (
            ("first event is not one", (), 2),
            ("gap", (1, 2), 4),
            ("reordered delivery", (1,), 3),
        ):
            with self.subTest(case=name):
                sequence = DeepSeekHarnessEventSequence()
                self.observe_all(sequence, *accepted)
                assert_blocked(self, "sequence_gap", sequence.observe, event(offending))
                self.assertEqual(sequence.blocked_code, "sequence_gap")
                self.assertEqual(sequence.expected_sequence, len(accepted) + 1)
                # The missing event is never inferred: even the expected event
                # or an identical retransmission is refused afterwards.
                assert_blocked(
                    self, "stream_blocked", sequence.observe, event(len(accepted) + 1)
                )
                if accepted:
                    assert_blocked(self, "stream_blocked", sequence.observe, event(1))

    def test_conflicting_content_for_same_identity_fails_closed(self) -> None:
        for name, conflicting in (
            ("same sequence, other event id", event(2, externalEventId="dsh-evt-other")),
            ("same event id, other sequence", event(3, externalEventId="dsh-evt-0001")),
            ("same identity, other kind", event(2, kind="session.started")),
            ("same identity, other time", event(2, occurredAt=event_at(9))),
            (
                "same identity, other payload fingerprint",
                event(2, payloadFingerprint=PAYLOAD_FINGERPRINT),
            ),
        ):
            with self.subTest(case=name):
                sequence = DeepSeekHarnessEventSequence()
                self.observe_all(sequence, 1, 2)
                assert_blocked(self, "event_conflict", sequence.observe, conflicting)
                self.assertEqual(sequence.blocked_code, "event_conflict")
                assert_blocked(self, "stream_blocked", sequence.observe, event(3))

    def test_admit_is_a_dry_run_that_never_advances(self) -> None:
        # The adapter admits, persists to the audit, and only then observes, so
        # a failed audit write never leaves the stream ahead of the audit.
        sequence = DeepSeekHarnessEventSequence()
        self.assertIs(sequence.admit(event(1)), True)
        self.assertIs(sequence.admit(event(1)), True)
        self.assertEqual(sequence.expected_sequence, 1)
        self.observe_all(sequence, 1)
        self.assertIs(sequence.admit(event(1)), False)
        assert_blocked(self, "sequence_gap", sequence.admit, event(3))
        self.assertEqual(sequence.blocked_code, "sequence_gap")

    def test_observe_rejects_values_that_are_not_normalized_events(self) -> None:
        sequence = DeepSeekHarnessEventSequence()
        for value in (None, event_metadata(), event().document()):
            with self.subTest(value=type(value).__name__):
                assert_blocked(self, "event_field_invalid", sequence.observe, value)
        self.assertEqual(sequence.expected_sequence, 1)
