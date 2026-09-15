"""Local OpenAI-compatible executor adapter (PIP-911 onda 2).

Talks to a local, OpenAI-compatible chat-completions endpoint (vLLM, Ollama,
llama.cpp...) and extracts the model's tool call from whichever shape the
runtime actually delivered it in: the OpenAI ``tool_calls`` envelope, or —
when the serving template failed to translate a real tool call into that
envelope (measured 12/09, relatório 15: 5 of 15 turns) — Qwen's own native
``<function=name><parameter=key>value</parameter></function>`` text inside
the message content. ``tool_calls`` always wins when both are present: it is
the contract the runtime itself promises, so a template that produces both
(most do not) should never have the fallback override it.

Nothing here ever calls a real model: ``transport`` is always injectable,
and it is the only thing that touches the network. Every test supplies a
fake (either a plain callable, or a real ``http.server`` loopback fake).
"""

from __future__ import annotations

import json
import urllib.request
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence


DEFAULT_TIMEOUT_SECONDS = 30.0

SOURCE_TOOL_CALLS = "tool_calls"
SOURCE_NATIVE_XML = "native_xml"
SOURCE_NONE = "none"

# ``Transport(url, payload_bytes, headers) -> response_bytes``. Production
# code leaves this unset and gets ``default_transport`` (``urllib``, stdlib
# only); every test supplies its own so no test ever opens a real socket to
# anything but a fake it started itself.
Transport = Callable[[str, bytes, Mapping[str, str]], bytes]

_FUNCTION_BLOCK = re.compile(r"<function=(?P<name>[^>\s]+)>(?P<body>.*?)</function>", re.DOTALL)
_PARAMETER = re.compile(r"<parameter=(?P<key>[^>\s]+)>(?P<value>.*?)</parameter>", re.DOTALL)


class LocalEndpointError(Exception):
    """The local endpoint could not be reached or returned something unusable."""


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolCallEnvelope:
    """What one assistant turn produced, along the two axes PIP-911 needs
    kept apart:

    - ``envelope_present``: whether the OpenAI ``tool_calls`` field itself
      showed up, non-empty — a runtime/template concern.
    - ``content_recovered``: whether a call was recovered at all, from
      *either* source — a model-content concern.

    A missing envelope with a call recovered from the native text
    (``envelope_present=False, content_recovered=True``) is the runtime's
    defect, not the model's: conflating the two is exactly what drove a
    needless downgrade in the 12/09 measurement.
    """

    envelope_present: bool
    content_recovered: bool
    source: str
    calls: tuple[ToolCall, ...] = field(default_factory=tuple)


def parse_openai_tool_calls(message: Mapping[str, Any]) -> tuple[ToolCall, ...]:
    """``message["tool_calls"]``, the standard OpenAI shape; ``()`` when
    absent, empty, or too malformed to trust — never raises: a malformed
    envelope reads the same as an absent one to every caller here."""

    if not isinstance(message, Mapping):
        return ()
    raw = message.get("tool_calls")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ()
    calls: list[ToolCall] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        function = item.get("function")
        if not isinstance(function, Mapping):
            continue
        name = function.get("name")
        if not isinstance(name, str) or not name:
            continue
        arguments = _parse_arguments(function.get("arguments"))
        if arguments is None:
            continue
        calls.append(ToolCall(name=name, arguments=arguments))
    return tuple(calls)


def parse_native_function_calls(content: Any) -> tuple[ToolCall, ...]:
    """Qwen's own text-based tool call format, used when the serving
    template failed to translate the model's call into ``tool_calls``::

        <function=NAME>
        <parameter=KEY>VALUE</parameter>
        </function>

    A parameter value that parses as JSON is coerced (so a boolean/number/
    object argument round-trips); anything else is kept as text."""

    if not isinstance(content, str) or not content:
        return ()
    calls: list[ToolCall] = []
    for match in _FUNCTION_BLOCK.finditer(content):
        name = match.group("name").strip()
        if not name:
            continue
        arguments: dict[str, Any] = {}
        for parameter in _PARAMETER.finditer(match.group("body")):
            key = parameter.group("key").strip()
            if not key:
                continue
            arguments[key] = _coerce_scalar(parameter.group("value").strip())
        calls.append(ToolCall(name=name, arguments=arguments))
    return tuple(calls)


def extract_tool_calls(message: Mapping[str, Any]) -> ToolCallEnvelope:
    """``tool_calls`` wins whenever it is present and non-empty; the native
    XML in ``content`` is only ever consulted when it is not."""

    if not isinstance(message, Mapping):
        return ToolCallEnvelope(envelope_present=False, content_recovered=False, source=SOURCE_NONE)
    openai_calls = parse_openai_tool_calls(message)
    if openai_calls:
        return ToolCallEnvelope(
            envelope_present=True,
            content_recovered=True,
            source=SOURCE_TOOL_CALLS,
            calls=openai_calls,
        )
    native_calls = parse_native_function_calls(message.get("content"))
    if native_calls:
        return ToolCallEnvelope(
            envelope_present=False,
            content_recovered=True,
            source=SOURCE_NATIVE_XML,
            calls=native_calls,
        )
    return ToolCallEnvelope(envelope_present=False, content_recovered=False, source=SOURCE_NONE)


def _parse_arguments(raw: Any) -> dict[str, Any] | None:
    if isinstance(raw, Mapping):
        return dict(raw)
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except ValueError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _coerce_scalar(value: str) -> Any:
    try:
        return json.loads(value)
    except ValueError:
        return value


def default_transport(url: str, payload: bytes, headers: Mapping[str, str], *, timeout: float) -> bytes:
    """The only place this module touches the network: a plain ``urllib``
    POST. Only ever called with a caller-supplied ``base_url`` — never a
    hardcoded host — so it always talks to whatever local endpoint the
    Program stage declared, never anything else."""

    request = urllib.request.Request(url, data=payload, headers=dict(headers), method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - local endpoint only
        return response.read()


def chat_completion(
    base_url: str,
    *,
    model: str,
    messages: Sequence[Mapping[str, Any]],
    tools: Sequence[Mapping[str, Any]] | None = None,
    transport: Transport | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    api_key: str | None = None,
) -> dict[str, Any]:
    """One OpenAI-compatible ``POST /chat/completions`` turn.

    ``transport`` is always injectable (``(url, body_bytes, headers) ->
    response_bytes``); left unset, a production caller gets
    ``default_transport`` (``urllib``, stdlib only)."""

    if not base_url:
        raise LocalEndpointError("local endpoint base_url is not configured")
    body: dict[str, Any] = {"model": model, "messages": list(messages)}
    if tools:
        body["tools"] = list(tools)
    payload = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    url = f"{base_url.rstrip('/')}/chat/completions"
    send: Callable[[str, bytes, Mapping[str, str]], bytes] = (
        transport if transport is not None else (lambda u, p, h: default_transport(u, p, h, timeout=timeout))
    )
    try:
        raw = send(url, payload, headers)
    except LocalEndpointError:
        raise
    except Exception as exc:  # noqa: BLE001 - any transport failure reads the same to the caller
        raise LocalEndpointError(f"local endpoint request failed: {type(exc).__name__}") from exc
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise LocalEndpointError("local endpoint returned invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise LocalEndpointError("local endpoint response must be a JSON object")
    return parsed


def request_tool_call(
    base_url: str,
    *,
    model: str,
    messages: Sequence[Mapping[str, Any]],
    tools: Sequence[Mapping[str, Any]],
    transport: Transport | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    api_key: str | None = None,
) -> ToolCallEnvelope:
    """One full turn: request the completion, then read its tool call in
    whichever of the two forms it actually arrived in."""

    response = chat_completion(
        base_url, model=model, messages=messages, tools=tools, transport=transport,
        timeout=timeout, api_key=api_key,
    )
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LocalEndpointError("local endpoint response has no choices")
    first = choices[0]
    message = first.get("message") if isinstance(first, Mapping) else None
    if not isinstance(message, Mapping):
        raise LocalEndpointError("local endpoint response has no message")
    return extract_tool_calls(message)
