"""PIP-911 onda 2: o turno único do executor local.

``run_local_worker`` reduz UMA chamada a um endpoint OpenAI-compatível ao
mesmo formato de saída que ``worker.extract_worker_output`` já produz de um
worker Claude Code — e mantém separado, no resultado, se o envelope
``tool_calls`` chegou e se uma chamada foi recuperada de outra forma
(``local_adapter.ToolCallEnvelope``). Nenhum teste aqui chama um modelo de
verdade: ``transport`` é sempre uma função Python que este arquivo escreve.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.local_worker import SUBMIT_TOOL_NAME, run_local_worker

from tests.mission.helpers import CREATED_AT, mission_input


def _mission_with_write_set(write_set: list[str]) -> dict[str, Any]:
    draft = mission_input()
    draft["workspace"]["writeSet"] = write_set
    return build_mission(draft, created_at=CREATED_AT)


def _tool_calls_transport(name: str, arguments: dict[str, Any]):
    def transport(url: str, payload: bytes, headers: dict) -> bytes:
        body = json.loads(payload.decode("utf-8"))
        assert body["model"], "o transporte deveria receber o modelo pedido"
        response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": name, "arguments": json.dumps(arguments)},
                    }],
                }
            }]
        }
        return json.dumps(response).encode("utf-8")

    return transport


def _native_xml_transport(arguments: dict[str, Any]):
    params = "".join(
        f"<parameter={key}>{json.dumps(value) if not isinstance(value, str) else value}</parameter>\n"
        for key, value in arguments.items()
    )
    content = f"<function={SUBMIT_TOOL_NAME}>\n{params}</function>"

    def transport(url: str, payload: bytes, headers: dict) -> bytes:
        response = {"choices": [{"message": {"role": "assistant", "content": content}}]}
        return json.dumps(response).encode("utf-8")

    return transport


class RunLocalWorkerHappyPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.worktree = Path(self.tmp.name)
        self.mission = _mission_with_write_set(["docs/a.md"])

    def test_a_tool_calls_response_writes_the_file_and_reports_the_envelope(self) -> None:
        arguments = {
            "done": True,
            "summary": "onda mecanica concluida",
            "filesChanged": [{"path": "docs/a.md", "content": "# onda a\n"}],
            "criteriaSelfAssessment": [{"id": "C1", "met": True}],
            "blockers": [],
        }
        result = run_local_worker(
            self.mission, worktree=self.worktree, base_url="http://fake",
            model="qwen-local", transport=_tool_calls_transport(SUBMIT_TOOL_NAME, arguments),
        )
        self.assertEqual(result.status, "collected")
        self.assertTrue(result.envelope_present)
        self.assertTrue(result.content_recovered)
        self.assertEqual(result.tool_call_source, "tool_calls")
        self.assertEqual((self.worktree / "docs/a.md").read_text(encoding="utf-8"), "# onda a\n")
        self.assertEqual(result.output["filesChanged"], ["docs/a.md"])
        self.assertTrue(result.output["done"])

    def test_a_native_xml_response_still_recovers_the_call_but_not_the_envelope(self) -> None:
        arguments = {
            "done": "true",
            "summary": "via xml nativo",
            "filesChanged": [],
            "criteriaSelfAssessment": [],
            "blockers": [],
        }
        result = run_local_worker(
            self.mission, worktree=self.worktree, base_url="http://fake",
            model="qwen-local", transport=_native_xml_transport(arguments),
        )
        self.assertEqual(result.status, "collected")
        self.assertFalse(result.envelope_present)
        self.assertTrue(result.content_recovered)
        self.assertEqual(result.tool_call_source, "native_xml")
        self.assertTrue(result.output["done"])


class RunLocalWorkerFailureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.worktree = Path(self.tmp.name)
        self.mission = _mission_with_write_set(["docs/a.md"])

    def test_no_tool_call_recovered_fails_without_touching_the_worktree(self) -> None:
        def transport(url: str, payload: bytes, headers: dict) -> bytes:
            return json.dumps({"choices": [{"message": {"role": "assistant", "content": "sem chamada nenhuma"}}]}).encode("utf-8")

        result = run_local_worker(
            self.mission, worktree=self.worktree, base_url="http://fake", model="m", transport=transport,
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.reason, "local_no_tool_call")
        self.assertFalse(result.envelope_present)
        self.assertFalse(result.content_recovered)
        self.assertEqual(list(self.worktree.iterdir()), [])

    def test_the_wrong_tool_name_fails_as_unexpected(self) -> None:
        result = run_local_worker(
            self.mission, worktree=self.worktree, base_url="http://fake", model="m",
            transport=_tool_calls_transport("outra_ferramenta", {"x": 1}),
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.reason, "local_unexpected_tool")
        # A chamada FOI recuperada — só não era a esperada; C3 exige que
        # isso continue distinto de "nenhuma chamada".
        self.assertTrue(result.content_recovered)

    def test_a_file_path_outside_the_write_set_is_refused(self) -> None:
        arguments = {
            "done": True, "summary": "tentando escapar",
            "filesChanged": [{"path": "../fora/arquivo.md", "content": "x"}],
            "criteriaSelfAssessment": [], "blockers": [],
        }
        result = run_local_worker(
            self.mission, worktree=self.worktree, base_url="http://fake", model="m",
            transport=_tool_calls_transport(SUBMIT_TOOL_NAME, arguments),
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.reason, "local_arguments_invalid")
        self.assertFalse((self.worktree.parent / "fora" / "arquivo.md").exists())

    def test_a_path_inside_the_worktree_but_outside_the_write_set_is_refused(self) -> None:
        arguments = {
            "done": True, "summary": "escrevendo fora do write set declarado",
            "filesChanged": [{"path": "docs/outro.md", "content": "x"}],
            "criteriaSelfAssessment": [], "blockers": [],
        }
        result = run_local_worker(
            self.mission, worktree=self.worktree, base_url="http://fake", model="m",
            transport=_tool_calls_transport(SUBMIT_TOOL_NAME, arguments),
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.reason, "local_arguments_invalid")
        self.assertFalse((self.worktree / "docs/outro.md").exists())

    def test_the_endpoint_being_unreachable_fails_closed(self) -> None:
        def broken_transport(url: str, payload: bytes, headers: dict) -> bytes:
            raise ConnectionRefusedError("nobody home")

        result = run_local_worker(
            self.mission, worktree=self.worktree, base_url="http://fake", model="m",
            transport=broken_transport,
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.reason, "local_endpoint_unavailable")
        self.assertFalse(result.envelope_present)
        self.assertFalse(result.content_recovered)

    def test_an_unconfigured_endpoint_fails_closed_without_a_real_call(self) -> None:
        result = run_local_worker(
            self.mission, worktree=self.worktree, base_url="", model="m",
            transport=lambda *a, **k: (_ for _ in ()).throw(AssertionError("never called")),
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.reason, "local_endpoint_unavailable")


if __name__ == "__main__":
    unittest.main()
