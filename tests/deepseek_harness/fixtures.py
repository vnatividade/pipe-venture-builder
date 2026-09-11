"""Synthetic JSON-RPC/NDJSON frames authored for the tests.

These frames follow a small notification shape written for this spike. They
are not captured from any DeepSeek Harness process, provider or model, and
they prove nothing about runtime compatibility. Raw content fields carry the
test sentinels so every test can prove the content never leaves the
normalizer.
"""

from __future__ import annotations

import json
from typing import Any

from tests.deepseek_harness.helpers import (
    READ_TOOL,
    SECRET_SENTINEL,
    SESSION_ONE,
    TEXT_SENTINEL,
    event_at,
)


RAW_ARGUMENTS = {"path": "README.md", "note": TEXT_SENTINEL}
RAW_RESULT = {"content": f"{TEXT_SENTINEL} {SECRET_SENTINEL}"}


def line(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":")).encode("utf-8") + b"\n"


def event_frame(
    sequence: int,
    update: dict[str, Any],
    *,
    session_id: str = SESSION_ONE,
    event_id: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "method": "session/update",
        "params": {
            "sessionId": session_id,
            "seq": sequence,
            "eventId": event_id or f"dsh-evt-{sequence:04d}",
            "timestamp": timestamp or event_at(sequence),
            "update": update,
        },
    }


def content_frame(update: dict[str, Any], *, session_id: str = SESSION_ONE) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "method": "session/update",
        "params": {"sessionId": session_id, "update": update},
    }


def reasoning(text: str = f"{TEXT_SENTINEL} reasoning {SECRET_SENTINEL}") -> dict[str, Any]:
    return content_frame({"type": "reasoning_delta", "text": text})


def message(text: str = f"{TEXT_SENTINEL} answer") -> dict[str, Any]:
    return content_frame({"type": "message_delta", "text": text})


def tool_call(sequence: int, *, name: str = READ_TOOL, arguments: Any = None, call_id: str = "call-1") -> dict[str, Any]:
    return event_frame(
        sequence,
        {
            "type": "tool_call",
            "toolCallId": call_id,
            "name": name,
            "arguments": dict(RAW_ARGUMENTS) if arguments is None else arguments,
        },
    )


def tool_result(sequence: int, *, call_id: str = "call-1", content: Any = None) -> dict[str, Any]:
    return event_frame(
        sequence,
        {
            "type": "tool_result",
            "toolCallId": call_id,
            "content": dict(RAW_RESULT) if content is None else content,
        },
    )


def review_turn() -> list[dict[str, Any]]:
    """A complete, well-formed synthetic review turn ending idle."""

    return [
        event_frame(1, {"type": "session_started"}),
        event_frame(2, {"type": "turn_started"}),
        reasoning(),
        tool_call(3),
        tool_result(4),
        message(),
        event_frame(5, {"type": "turn_end"}),
        event_frame(6, {"type": "status", "status": "idle"}),
    ]


def chunked(frames: list[dict[str, Any]], size: int = 7) -> list[bytes]:
    """Split the NDJSON stream at arbitrary byte boundaries (partial frames)."""

    stream = b"".join(line(frame) for frame in frames)
    return [stream[index : index + size] for index in range(0, len(stream), size)]
