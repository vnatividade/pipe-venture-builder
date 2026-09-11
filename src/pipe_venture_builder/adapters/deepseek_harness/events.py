"""Allowlisted, payload-free runtime events and their sequence (ADR-004 D4, D10).

A runtime event is metadata only: identifiers, a sequence number, a kind from a
closed allowlist, a timestamp, an allowlisted read-only tool name and an
optional payload fingerprint. Prompts, messages, reasoning, tool arguments,
tool results, frames and environment never enter this model. Runtime events
cannot approve or complete a Pipe run. ``DHE-*`` identifiers are experimental
spike identifiers, never canonical runtime identities.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from pipe_venture_builder.adapters.safety import payload_is_safe
from pipe_venture_builder.control_plane.model import (
    FINGERPRINT_PATTERN,
    ControlPlaneContractError,
    fingerprint,
    parse_datetime,
    stable_id,
)

from .errors import DeepSeekHarnessContractError


SCHEMA_VERSION = "0.1.0"
TOOL_KINDS = frozenset({"tool.started", "tool.succeeded"})
EVENT_KINDS = frozenset(
    {"session.started", "turn.started", "turn.ended", "session.idle"} | TOOL_KINDS
)
# Read-only tools only; shell, editors and patching are outside the spike.
READ_ONLY_TOOLS = frozenset({"read_file"})
# Runtime authority over Pipe approval or run lifecycle is never accepted.
FORBIDDEN_KIND_PREFIXES = ("approval.", "run.")
MAX_SEQUENCE = 2**31 - 1

_REQUIRED_FIELDS = ("externalEventId", "sessionId", "sequence", "kind", "occurredAt")
_OPTIONAL_FIELDS = ("toolName", "payloadFingerprint")
_FIELDS = frozenset(_REQUIRED_FIELDS + _OPTIONAL_FIELDS)
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+=-]{0,127}")
_TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})"
)


@dataclass(frozen=True)
class DeepSeekHarnessRuntimeEvent:
    """One normalized runtime event; validated on every construction path."""

    external_event_id: str
    session_id: str
    sequence: int
    kind: str
    occurred_at: str
    tool_name: str | None = None
    payload_fingerprint: str | None = None
    event_id: str = field(init=False)
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        _require_kind(self.kind)
        for value in (self.external_event_id, self.session_id):
            _require_identifier(value)
        if type(self.sequence) is not int or not 1 <= self.sequence <= MAX_SEQUENCE:
            raise DeepSeekHarnessContractError("event_field_invalid") from None
        _require_timestamp(self.occurred_at)
        if self.kind in TOOL_KINDS:
            if type(self.tool_name) is not str or self.tool_name not in READ_ONLY_TOOLS:
                raise DeepSeekHarnessContractError("tool_not_allowlisted") from None
        elif self.tool_name is not None:
            raise DeepSeekHarnessContractError("event_field_invalid") from None
        if self.payload_fingerprint is not None and (
            type(self.payload_fingerprint) is not str
            or FINGERPRINT_PATTERN.fullmatch(self.payload_fingerprint) is None
        ):
            raise DeepSeekHarnessContractError("event_field_invalid") from None
        identity = {"sessionId": self.session_id, "externalEventId": self.external_event_id}
        object.__setattr__(self, "event_id", stable_id("DHE", identity))
        object.__setattr__(self, "fingerprint", fingerprint(self._core()))

    @classmethod
    def from_metadata(cls, metadata: Any) -> DeepSeekHarnessRuntimeEvent:
        """Normalize runtime metadata; any field outside the allowlist is refused."""

        if not isinstance(metadata, Mapping):
            raise DeepSeekHarnessContractError("event_field_invalid") from None
        if any(type(key) is not str or key not in _FIELDS for key in metadata):
            raise DeepSeekHarnessContractError("event_field_unknown") from None
        if any(key not in metadata for key in _REQUIRED_FIELDS):
            raise DeepSeekHarnessContractError("event_field_invalid") from None
        return cls(
            external_event_id=metadata["externalEventId"],
            session_id=metadata["sessionId"],
            sequence=metadata["sequence"],
            kind=metadata["kind"],
            occurred_at=metadata["occurredAt"],
            tool_name=metadata.get("toolName"),
            payload_fingerprint=metadata.get("payloadFingerprint"),
        )

    def document(self) -> dict[str, Any]:
        """Return a fresh metadata-only document of the event."""

        document = {"eventId": self.event_id, **self._core()}
        document["fingerprint"] = self.fingerprint
        document["constraints"] = {
            "rawPayloadPersisted": False,
            "runtimeApprovalIsAuthority": False,
            "canonicalRuntimeIdentity": False,
        }
        return document

    def _core(self) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "externalEventId": self.external_event_id,
            "sessionId": self.session_id,
            "sequence": self.sequence,
            "kind": self.kind,
            "occurredAt": self.occurred_at,
            "toolName": self.tool_name,
            "payloadFingerprint": self.payload_fingerprint,
        }


class DeepSeekHarnessEventSequence:
    """Contiguous-from-one sequence with idempotent duplicates (ADR-004 D10).

    A gap, reorder or conflict blocks the stream permanently: the missing or
    conflicting event is never inferred, and every later event is refused.
    """

    __slots__ = ("_records", "_by_event_id", "_blocked")

    def __init__(self) -> None:
        # Only identifiers, fingerprints and kinds are retained, never payload.
        self._records: list[dict[str, Any]] = []
        self._by_event_id: dict[str, int] = {}
        self._blocked: str | None = None

    @classmethod
    def restore(cls, records: Any) -> DeepSeekHarnessEventSequence:
        """Rebuild from checkpoint records; they must be contiguous from one."""

        sequence = cls()
        if type(records) not in (list, tuple):
            raise DeepSeekHarnessContractError("checkpoint_invalid") from None
        for number, record in enumerate(records, start=1):
            if (
                not isinstance(record, Mapping)
                or set(record) != {"eventId", "sequence", "fingerprint", "kind"}
                or record["sequence"] != number
                or record["eventId"] in sequence._by_event_id
            ):
                raise DeepSeekHarnessContractError("checkpoint_invalid") from None
            sequence._append(dict(record))
        return sequence

    @property
    def expected_sequence(self) -> int:
        return len(self._records) + 1

    @property
    def blocked_code(self) -> str | None:
        return self._blocked

    def records(self) -> list[dict[str, Any]]:
        """Return fresh metadata-only records of the accepted events."""

        return [dict(record) for record in self._records]

    def admit(self, event: Any) -> bool:
        """Check without advancing: True for the next event, False for a duplicate."""

        if type(event) is not DeepSeekHarnessRuntimeEvent:
            raise DeepSeekHarnessContractError("event_field_invalid") from None
        if self._blocked is not None:
            raise DeepSeekHarnessContractError("stream_blocked") from None
        if event.sequence <= len(self._records):
            seen = self._records[event.sequence - 1]
            if (seen["eventId"], seen["fingerprint"]) == (event.event_id, event.fingerprint):
                return False
            self.block("event_conflict")
        if event.event_id in self._by_event_id:
            self.block("event_conflict")
        if event.sequence != self.expected_sequence:
            self.block("sequence_gap")
        return True

    def observe(self, event: Any) -> bool:
        """Admit and record the event; return False for an identical retransmission."""

        if not self.admit(event):
            return False
        self._append(record_of(event))
        return True

    def block(self, code: str) -> None:
        """Block the stream permanently and raise ``code``."""

        self.block_quietly(code)
        raise DeepSeekHarnessContractError(code) from None

    def block_quietly(self, code: str) -> None:
        """Block the stream permanently; the first blocker code is kept."""

        if self._blocked is None:
            self._blocked = code

    def _append(self, record: dict[str, Any]) -> None:
        self._by_event_id[record["eventId"]] = record["sequence"]
        self._records.append(record)


def record_of(event: DeepSeekHarnessRuntimeEvent) -> dict[str, Any]:
    """The metadata-only record kept for dedupe: identity, sequence, hash, kind."""

    return {
        "eventId": event.event_id,
        "sequence": event.sequence,
        "fingerprint": event.fingerprint,
        "kind": event.kind,
    }


def _require_kind(kind: Any) -> None:
    if type(kind) is str and kind.startswith(FORBIDDEN_KIND_PREFIXES):
        raise DeepSeekHarnessContractError("event_kind_forbidden") from None
    if type(kind) is not str or kind not in EVENT_KINDS:
        raise DeepSeekHarnessContractError("event_kind_unknown") from None


def _require_identifier(value: Any) -> None:
    if (
        type(value) is not str
        or _IDENTIFIER.fullmatch(value) is None
        or not payload_is_safe(value)
    ):
        raise DeepSeekHarnessContractError("event_field_invalid") from None


def _require_timestamp(value: Any) -> None:
    if type(value) is not str or _TIMESTAMP.fullmatch(value) is None:
        raise DeepSeekHarnessContractError("event_field_invalid") from None
    try:
        parse_datetime(value)
    except ControlPlaneContractError:
        raise DeepSeekHarnessContractError("event_field_invalid") from None
