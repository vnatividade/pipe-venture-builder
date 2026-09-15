"""PIP-911 onda 2: o adaptador local lê a tool call em DUAS formas.

Medido em 12/09 (relatório 15): o modelo local acertava 15/15 turnos numa
tarefa estreita, mas o template do Ollama não traduziu a chamada para
``tool_calls`` em 5 de 15 — o runtime errava, não o modelo. Estes testes
travam exatamente essa distinção: ``tool_calls`` (o envelope OpenAI) sempre
vence quando presente; o XML nativo do Qwen só é lido quando ele não está.

Nenhum teste aqui chama um modelo de verdade — ``transport`` é sempre uma
função Python (ou, na classe HTTP abaixo, um servidor loopback que este
teste inicia e derruba), nunca uma rede de verdade.
"""

from __future__ import annotations

import http.server
import json
import threading
import unittest
from typing import Any

from pipe_venture_builder.mission.local_adapter import (
    LocalEndpointError,
    SOURCE_NATIVE_XML,
    SOURCE_NONE,
    SOURCE_TOOL_CALLS,
    ToolCall,
    chat_completion,
    extract_tool_calls,
    parse_native_function_calls,
    parse_openai_tool_calls,
    request_tool_call,
)


def _tool_calls_message(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call-1",
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(arguments)},
            }
        ],
    }


class ParseOpenAIToolCallsTests(unittest.TestCase):
    def test_a_well_formed_envelope_is_parsed(self) -> None:
        message = _tool_calls_message("submit_mission_result", {"done": True})
        calls = parse_openai_tool_calls(message)
        self.assertEqual(calls, (ToolCall(name="submit_mission_result", arguments={"done": True}),))

    def test_absent_tool_calls_is_empty(self) -> None:
        self.assertEqual(parse_openai_tool_calls({"role": "assistant", "content": "oi"}), ())

    def test_empty_list_is_empty(self) -> None:
        self.assertEqual(parse_openai_tool_calls({"tool_calls": []}), ())

    def test_arguments_as_a_mapping_instead_of_a_json_string_is_accepted(self) -> None:
        message = {
            "tool_calls": [
                {"type": "function", "function": {"name": "f", "arguments": {"a": 1}}}
            ]
        }
        self.assertEqual(parse_openai_tool_calls(message), (ToolCall(name="f", arguments={"a": 1}),))

    def test_unparseable_arguments_drops_the_call_instead_of_raising(self) -> None:
        message = {
            "tool_calls": [
                {"type": "function", "function": {"name": "f", "arguments": "{not json"}}
            ]
        }
        self.assertEqual(parse_openai_tool_calls(message), ())


class ParseNativeFunctionCallsTests(unittest.TestCase):
    def test_qwen_style_xml_is_parsed(self) -> None:
        content = (
            "<function=submit_mission_result>\n"
            "<parameter=done>true</parameter>\n"
            "<parameter=summary>tarefa feita</parameter>\n"
            "</function>"
        )
        calls = parse_native_function_calls(content)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].name, "submit_mission_result")
        self.assertEqual(calls[0].arguments, {"done": True, "summary": "tarefa feita"})

    def test_a_value_that_is_not_json_stays_text(self) -> None:
        content = "<function=f>\n<parameter=path>docs/a.md</parameter>\n</function>"
        calls = parse_native_function_calls(content)
        self.assertEqual(calls[0].arguments, {"path": "docs/a.md"})

    def test_no_function_block_is_empty(self) -> None:
        self.assertEqual(parse_native_function_calls("apenas texto, sem chamada"), ())

    def test_non_string_content_is_empty(self) -> None:
        self.assertEqual(parse_native_function_calls(None), ())


class ExtractToolCallsPrecedenceTests(unittest.TestCase):
    """C2/C3 do PIP-911 onda 2: as duas formas, e qual vence quando as duas
    aparecem — ``tool_calls`` é o contrato que o runtime promete, então
    nunca perde para o texto."""

    def test_tool_calls_present_reports_envelope_and_content(self) -> None:
        message = _tool_calls_message("submit_mission_result", {"done": True})
        envelope = extract_tool_calls(message)
        self.assertTrue(envelope.envelope_present)
        self.assertTrue(envelope.content_recovered)
        self.assertEqual(envelope.source, SOURCE_TOOL_CALLS)
        self.assertEqual(envelope.calls[0].name, "submit_mission_result")

    def test_native_xml_alone_recovers_content_without_the_envelope(self) -> None:
        """O caso medido em 12/09: o modelo chamou a função certa, mas o
        template não a traduziu para ``tool_calls`` — o runtime falhou, não
        o modelo. ``envelope_present`` e ``content_recovered`` têm que
        discordar aqui, nunca serem tratados como o mesmo sinal."""

        message = {
            "role": "assistant",
            "content": "<function=submit_mission_result>\n<parameter=done>true</parameter>\n</function>",
        }
        envelope = extract_tool_calls(message)
        self.assertFalse(envelope.envelope_present)
        self.assertTrue(envelope.content_recovered)
        self.assertEqual(envelope.source, SOURCE_NATIVE_XML)

    def test_tool_calls_wins_when_both_forms_are_present(self) -> None:
        message = _tool_calls_message("submit_mission_result", {"done": True})
        message["content"] = "<function=outra_coisa>\n<parameter=x>1</parameter>\n</function>"
        envelope = extract_tool_calls(message)
        self.assertTrue(envelope.envelope_present)
        self.assertEqual(envelope.source, SOURCE_TOOL_CALLS)
        self.assertEqual(envelope.calls[0].name, "submit_mission_result")

    def test_neither_form_present_recovers_nothing(self) -> None:
        envelope = extract_tool_calls({"role": "assistant", "content": "só prosa, sem chamada"})
        self.assertFalse(envelope.envelope_present)
        self.assertFalse(envelope.content_recovered)
        self.assertEqual(envelope.source, SOURCE_NONE)
        self.assertEqual(envelope.calls, ())


class ChatCompletionFakeTransportTests(unittest.TestCase):
    """Um transporte é só uma função Python: nenhum destes testes abre um
    socket de verdade."""

    def test_fake_transport_receives_the_right_url_and_body(self) -> None:
        seen: dict[str, Any] = {}

        def fake_transport(url: str, payload: bytes, headers: dict) -> bytes:
            seen["url"] = url
            seen["body"] = json.loads(payload.decode("utf-8"))
            seen["headers"] = headers
            return json.dumps({"choices": [{"message": {"content": "oi"}}]}).encode("utf-8")

        response = chat_completion(
            "http://127.0.0.1:9/v1", model="qwen-local",
            messages=[{"role": "user", "content": "oi"}], transport=fake_transport,
        )
        self.assertEqual(seen["url"], "http://127.0.0.1:9/v1/chat/completions")
        self.assertEqual(seen["body"]["model"], "qwen-local")
        self.assertEqual(seen["headers"]["Content-Type"], "application/json")
        self.assertEqual(response["choices"][0]["message"]["content"], "oi")

    def test_missing_base_url_fails_closed(self) -> None:
        with self.assertRaises(LocalEndpointError):
            chat_completion("", model="m", messages=[])

    def test_a_transport_failure_becomes_a_local_endpoint_error(self) -> None:
        def broken_transport(url: str, payload: bytes, headers: dict) -> bytes:
            raise ConnectionRefusedError("nobody home")

        with self.assertRaises(LocalEndpointError):
            chat_completion("http://127.0.0.1:9", model="m", messages=[], transport=broken_transport)

    def test_non_json_response_fails_closed(self) -> None:
        def garbage_transport(url: str, payload: bytes, headers: dict) -> bytes:
            return b"not json"

        with self.assertRaises(LocalEndpointError):
            chat_completion("http://127.0.0.1:9", model="m", messages=[], transport=garbage_transport)

    def test_request_tool_call_extracts_from_the_response(self) -> None:
        def fake_transport(url: str, payload: bytes, headers: dict) -> bytes:
            return json.dumps({
                "choices": [{"message": _tool_calls_message("submit_mission_result", {"done": True})}]
            }).encode("utf-8")

        envelope = request_tool_call(
            "http://127.0.0.1:9", model="m", messages=[{"role": "user", "content": "oi"}],
            tools=[{"type": "function", "function": {"name": "submit_mission_result"}}],
            transport=fake_transport,
        )
        self.assertTrue(envelope.envelope_present)
        self.assertEqual(envelope.calls[0].name, "submit_mission_result")

    def test_a_response_with_no_choices_fails_closed(self) -> None:
        def empty_transport(url: str, payload: bytes, headers: dict) -> bytes:
            return json.dumps({"choices": []}).encode("utf-8")

        with self.assertRaises(LocalEndpointError):
            request_tool_call(
                "http://127.0.0.1:9", model="m", messages=[], tools=[], transport=empty_transport
            )


class _FakeOpenAICompatibleHandler(http.server.BaseHTTPRequestHandler):
    """A tiny, real HTTP server standing in for a local OpenAI-compatible
    endpoint (vLLM/Ollama/llama.cpp) — loopback only, started and stopped by
    the test below. Proves ``default_transport`` (the real, non-injected
    code path) actually speaks the wire protocol, not just that the
    injectable ``transport`` seam type-checks."""

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler naming
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        self.server.requests.append((self.path, body))  # type: ignore[attr-defined]
        response = json.dumps({
            "choices": [{"message": _tool_calls_message("submit_mission_result", {"done": True})}]
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
        pass  # o teste não precisa do access log no stdout


class RealLoopbackEndpointTests(unittest.TestCase):
    """Um servidor HTTP de verdade, mas em loopback e iniciado pelo próprio
    teste — nunca um modelo de verdade, nunca uma rede externa."""

    def test_default_transport_round_trips_through_a_real_local_socket(self) -> None:
        server = http.server.HTTPServer(("127.0.0.1", 0), _FakeOpenAICompatibleHandler)
        server.requests = []  # type: ignore[attr-defined]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://127.0.0.1:{server.server_port}"
            envelope = request_tool_call(
                base_url, model="qwen-local", messages=[{"role": "user", "content": "oi"}],
                tools=[{"type": "function", "function": {"name": "submit_mission_result"}}],
            )
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

        self.assertTrue(envelope.envelope_present)
        self.assertEqual(envelope.calls[0].name, "submit_mission_result")
        path, body = server.requests[0]  # type: ignore[attr-defined]
        self.assertEqual(path, "/chat/completions")
        self.assertEqual(body["model"], "qwen-local")


if __name__ == "__main__":
    unittest.main()
