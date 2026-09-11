"""In-process fake JSON-RPC/NDJSON transport (ADR-004 D8, D9, D10).

The transport replays an authored script of byte chunks and signals. There is
no process, socket, clock, thread or file: a timeout and an end-of-stream are
scripted signals, so every scenario is deterministic. Partial frames are
reassembled across chunks; a frame cut by end-of-stream is a truncation. Any
failure poisons the transport and drops buffered bytes, so raw content is
never retained after a refusal.
"""

from __future__ import annotations

import enum
from collections import deque
from typing import Any

from .adapter import DeepSeekHarnessRuntimeAdapter
from .errors import DeepSeekHarnessContractError
from .normalizer import MAX_FRAME_BYTES, DeepSeekHarnessNormalizer


# Client requests the fake protocol knows; only method names and ids are kept.
REQUEST_METHODS = frozenset({"initialize", "session/prompt", "shutdown"})


class TransportSignal(enum.Enum):
    TIMEOUT = "timeout"
    EOF = "eof"


class FakeNdjsonTransport:
    """Replay an authored script of NDJSON byte chunks and scripted signals."""

    __slots__ = ("_script", "_buffer", "_failure", "_sent")

    def __init__(self, script: Any) -> None:
        if type(script) not in (list, tuple) or any(
            type(item) is not bytes and type(item) is not TransportSignal for item in script
        ):
            raise DeepSeekHarnessContractError("contract_violation") from None
        self._script: deque[bytes | TransportSignal] = deque(script)
        self._buffer = bytearray()
        self._failure: str | None = None
        self._sent: list[tuple[int, str]] = []

    @property
    def sent(self) -> tuple[tuple[int, str], ...]:
        return tuple(self._sent)

    def send(self, method: Any) -> int:
        """Record a client request by method name and id; parameters are never kept."""

        if type(method) is not str or method not in REQUEST_METHODS:
            raise DeepSeekHarnessContractError("contract_violation") from None
        request_id = len(self._sent) + 1
        self._sent.append((request_id, method))
        return request_id

    def read_frame(self) -> bytes:
        """Return the next complete NDJSON line without its newline, or refuse."""

        if self._failure is not None:
            raise DeepSeekHarnessContractError(self._failure) from None
        while True:
            newline = self._buffer.find(b"\n")
            if newline >= 0:
                if newline > MAX_FRAME_BYTES:
                    self._fail("frame_too_large")
                frame = bytes(self._buffer[:newline])
                del self._buffer[: newline + 1]
                return frame
            if len(self._buffer) > MAX_FRAME_BYTES:
                self._fail("frame_too_large")
            item = self._script.popleft() if self._script else TransportSignal.EOF
            if item is TransportSignal.TIMEOUT:
                self._fail("transport_timeout")
            if item is TransportSignal.EOF:
                self._fail("frame_truncated" if self._buffer else "transport_eof")
            self._buffer.extend(item)

    def _fail(self, code: str) -> None:
        self._failure = code
        self._buffer.clear()
        self._script.clear()
        raise DeepSeekHarnessContractError(code) from None


def drive_session(
    adapter: Any,
    *,
    binding: Any,
    context: Any,
    transport: Any,
    normalizer: Any,
    clock: Any,
) -> None:
    """Pump frames into the adapter until the transport stops.

    It never returns normally. Every transport or normalizer refusal is handed
    to ``adapter.refuse`` with a time from ``clock``: a clean ``transport_eof``
    at a resting point is only reported, and any other refusal blocks the
    attempt durably, so a fresh normalizer cannot resume the stream. That end
    never completes the Pipe run; completion stays the adapter's dedicated
    method.
    """

    if (
        type(adapter) is not DeepSeekHarnessRuntimeAdapter
        or type(transport) is not FakeNdjsonTransport
        or type(normalizer) is not DeepSeekHarnessNormalizer
        or not callable(clock)
    ):
        raise DeepSeekHarnessContractError("contract_violation") from None
    if getattr(binding, "session_id", None) != normalizer.session_id:
        raise DeepSeekHarnessContractError("session_mismatch") from None
    while True:
        event = refused = None
        try:
            event = normalizer.normalize(transport.read_frame())
        except DeepSeekHarnessContractError as error:
            refused = error.code
        if refused is not None:
            adapter.refuse(binding=binding, context=context, code=refused, occurred_at=clock())
        if event is not None:
            adapter.record_event(binding=binding, context=context, event=event)
