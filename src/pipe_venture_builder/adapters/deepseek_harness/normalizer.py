"""Normalize synthetic JSON-RPC/NDJSON frames into allowlisted events (D4, D10, D13).

The frame shape is a small notification protocol authored for this spike. It
is not a capture of any DeepSeek Harness process and proves no compatibility.
Raw content (prompt, message, reasoning, tool arguments and results) exists
only inside :meth:`DeepSeekHarnessNormalizer.normalize`: tool arguments and
results leave as a fingerprint, messages and reasoning leave as nothing, and
no refusal echoes the frame. The normalizer keeps only identifiers and turn
state, and never resynchronizes after a refusal.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pipe_venture_builder.control_plane.model import ControlPlaneContractError, fingerprint

from .errors import DeepSeekHarnessContractError
from .events import DeepSeekHarnessRuntimeEvent
from .session import _require_identifier


MAX_FRAME_BYTES = 256 * 1024
# Synthetic protocol risks (hypotheses and refusals, not claims about DSH):
# scenario name -> stable blocker code. Each scenario has a named test.
COMPATIBILITY_MATRIX = (
    ("literal_tool_call", "tool_call_literal"),
    ("malformed_tool_call", "tool_call_malformed"),
    ("truncated_frame", "frame_truncated"),
    ("inconsistent_reasoning", "reasoning_inconsistent"),
    ("timeout", "transport_timeout"),
    ("eof", "transport_eof"),
    ("invalid_framing", "frame_invalid"),
    ("unknown_type", "frame_type_unknown"),
)

_NOTIFICATION = frozenset({"jsonrpc", "method", "params"})
_RESULT = frozenset({"jsonrpc", "id", "result"})
_ERROR = frozenset({"jsonrpc", "id", "error"})
_EVENT_PARAMS = frozenset({"sessionId", "seq", "eventId", "timestamp", "update"})
_CONTENT_PARAMS = frozenset({"sessionId", "update"})
_EVENT_UPDATES = {
    "session_started": frozenset({"type"}),
    "turn_started": frozenset({"type"}),
    "turn_end": frozenset({"type"}),
    "status": frozenset({"type", "status"}),
    "tool_call": frozenset({"type", "toolCallId", "name", "arguments"}),
    "tool_result": frozenset({"type", "toolCallId", "content"}),
}
_CONTENT_UPDATES = {
    "message_delta": frozenset({"type", "text"}),
    "reasoning_delta": frozenset({"type", "text"}),
}
_TOOL_UPDATES = frozenset({"tool_call", "tool_result"})
_CALL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}")
# A tool call rendered as literal text instead of a structured frame.
_LITERAL_TOOL_CALL = re.compile(r'<\s*/?\s*tool_call|<\|\s*tool|"arguments"\s*:', re.IGNORECASE)
_MAX_OPEN_TOOL_CALLS = 64


class DeepSeekHarnessNormalizer:
    """Per-session, fail-closed frame normalizer holding no raw content."""

    __slots__ = ("_session_id", "_turn_open", "_answered", "_open_tools", "_pending", "_blocked")

    def __init__(self, session_id: Any) -> None:
        _require_identifier(session_id)
        self._session_id: str = session_id
        self._turn_open = False
        self._answered = False
        self._open_tools: dict[str, str] = {}
        self._pending: set[int] = set()
        self._blocked = False

    @property
    def session_id(self) -> str:
        return self._session_id

    def expect_response(self, request_id: Any) -> None:
        if type(request_id) is not int or request_id < 1:
            raise DeepSeekHarnessContractError("contract_violation") from None
        self._pending.add(request_id)

    def normalize(self, frame: Any) -> DeepSeekHarnessRuntimeEvent | None:
        """Return an allowlisted event, ``None`` for content/responses, or refuse."""

        if self._blocked:
            raise DeepSeekHarnessContractError("stream_blocked") from None
        try:
            return self._normalize(frame)
        except DeepSeekHarnessContractError:
            self._blocked = True
            self._open_tools.clear()
            raise

    def _normalize(self, frame: Any) -> DeepSeekHarnessRuntimeEvent | None:
        message = _decode(frame)
        if message.get("jsonrpc") != "2.0":
            _refuse("frame_invalid")
        if "method" in message and "id" in message:
            # Runtime-to-client requests are outside the spike surface.
            _refuse("frame_type_unknown")
        if "method" not in message:
            return self._response(message)
        if set(message) != _NOTIFICATION:
            _refuse("frame_invalid")
        if message["method"] != "session/update":
            _refuse("frame_type_unknown")
        params = message["params"]
        if type(params) is not dict or type(params.get("update")) is not dict:
            _refuse("frame_invalid")
        update = params["update"]
        kind = update.get("type")
        if kind in _CONTENT_UPDATES:
            self._require_shape(params, _CONTENT_PARAMS, update, _CONTENT_UPDATES[kind], kind)
            self._content(kind, update["text"])
            return None
        if kind not in _EVENT_UPDATES:
            _refuse("frame_type_unknown")
        self._require_shape(params, _EVENT_PARAMS, update, _EVENT_UPDATES[kind], kind)
        return self._event(kind, params, update)

    def _require_shape(
        self,
        params: dict[str, Any],
        params_keys: frozenset[str],
        update: dict[str, Any],
        update_keys: frozenset[str],
        kind: str,
    ) -> None:
        if set(params) != params_keys:
            _refuse("frame_invalid")
        if set(update) != update_keys:
            _refuse("tool_call_malformed" if kind in _TOOL_UPDATES else "frame_invalid")
        if params["sessionId"] != self._session_id:
            _refuse("session_mismatch")

    def _content(self, kind: str, text: Any) -> None:
        if type(text) is not str:
            _refuse("frame_invalid")
        if kind == "reasoning_delta":
            if not self._turn_open or self._answered:
                _refuse("reasoning_inconsistent")
            return
        if not self._turn_open:
            _refuse("turn_state_invalid")
        if _LITERAL_TOOL_CALL.search(text):
            _refuse("tool_call_literal")
        self._answered = True

    def _event(
        self, kind: str, params: dict[str, Any], update: dict[str, Any]
    ) -> DeepSeekHarnessRuntimeEvent:
        metadata: dict[str, Any] = {
            "externalEventId": params["eventId"],
            "sessionId": params["sessionId"],
            "sequence": params["seq"],
            "occurredAt": params["timestamp"],
        }
        if kind == "session_started":
            if self._turn_open:
                _refuse("turn_state_invalid")
            metadata["kind"] = "session.started"
        elif kind == "turn_started":
            if self._turn_open:
                _refuse("turn_state_invalid")
            metadata["kind"] = "turn.started"
        elif kind == "turn_end":
            if not self._turn_open or self._open_tools:
                _refuse("turn_state_invalid")
            metadata["kind"] = "turn.ended"
        elif kind == "status":
            if update["status"] != "idle":
                _refuse("frame_type_unknown")
            if self._turn_open:
                _refuse("turn_state_invalid")
            metadata["kind"] = "session.idle"
        elif kind == "tool_call":
            call_id = self._tool_call_id(update)
            if call_id in self._open_tools or len(self._open_tools) >= _MAX_OPEN_TOOL_CALLS:
                _refuse("tool_call_malformed")
            if type(update["name"]) is not str or type(update["arguments"]) is not dict:
                _refuse("tool_call_malformed")
            metadata.update(
                kind="tool.started",
                toolName=update["name"],
                payloadFingerprint=_payload_fingerprint(update["arguments"]),
            )
        else:
            call_id = self._tool_call_id(update)
            if call_id not in self._open_tools:
                _refuse("tool_call_malformed")
            metadata.update(
                kind="tool.succeeded",
                toolName=self._open_tools[call_id],
                payloadFingerprint=_payload_fingerprint(update["content"]),
            )
        event = DeepSeekHarnessRuntimeEvent.from_metadata(metadata)
        # Turn state only changes after the event itself validated.
        if kind == "turn_started":
            self._turn_open, self._answered = True, False
        elif kind == "turn_end":
            self._turn_open = False
        elif kind == "tool_call":
            self._open_tools[update["toolCallId"]] = event.tool_name or ""
        elif kind == "tool_result":
            del self._open_tools[update["toolCallId"]]
        return event

    def _tool_call_id(self, update: dict[str, Any]) -> str:
        if not self._turn_open:
            _refuse("turn_state_invalid")
        call_id = update["toolCallId"]
        if type(call_id) is not str or _CALL_ID.fullmatch(call_id) is None:
            _refuse("tool_call_malformed")
        return call_id

    def _response(self, message: dict[str, Any]) -> None:
        keys = set(message)
        if keys not in (_RESULT, _ERROR):
            _refuse("frame_invalid")
        request_id = message["id"]
        if type(request_id) is not int or request_id not in self._pending:
            _refuse("frame_invalid")
        self._pending.discard(request_id)
        if keys == _ERROR:
            # The runtime error body is never read into a document or error.
            _refuse("runtime_error")
        if type(message["result"]) is not dict:
            _refuse("frame_invalid")
        return None


def _decode(frame: Any) -> dict[str, Any]:
    if type(frame) is not bytes:
        _refuse("frame_invalid")
    if len(frame) > MAX_FRAME_BYTES:
        _refuse("frame_too_large")
    # Refuse outside the handler: a decode error keeps the raw frame on its
    # attributes, and raising inside ``except`` would retain it as __context__.
    message = None
    try:
        message = json.loads(
            frame.decode("utf-8"),
            object_pairs_hook=_unique_keys,
            parse_constant=_no_constant,
        )
    except (UnicodeError, ValueError, RecursionError):
        message = None
    if type(message) is not dict:
        _refuse("frame_invalid")
    return message


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _no_constant(_name: str) -> Any:
    raise ValueError("non-finite constant")


def _payload_fingerprint(value: Any) -> str:
    digest = None
    try:
        digest = fingerprint(value)
    except ControlPlaneContractError:
        digest = None
    if digest is None:
        _refuse("frame_invalid")
    return digest


def _refuse(code: str) -> None:
    raise DeepSeekHarnessContractError(code) from None
