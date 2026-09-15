"""PIP-911 onda 2: rebaixamento automático do executor local para o forte.

Uma onda mecânica pode declarar ``execution.executor: "local"`` (onda 1).
Esta onda faz o dispatch honrar essa declaração de verdade — rodando o
turno local (``local_worker.run_local_worker``) em vez do worker Claude Code
— e prova, com uma mutação comportamental (o transporte falso do endpoint
local levanta ``AssertionError`` se for chamado uma terceira vez), que duas
falhas de verificação SEGUIDAS com ``executor: local`` derrubam a onda para
o modelo forte e emitem ``executor.fallback`` — nunca o contrário.

Nenhum teste aqui chama um modelo de verdade: o endpoint local é sempre uma
função Python que este arquivo escreve; o "Claude" é o fake de sempre
(``tests/mission/fakes/fake_claude.py``).
"""

from __future__ import annotations

import json
from typing import Any

from tests.mission.test_program import ProgramTestCase, satisfied, stage, stage_draft, writes

# O critério exige o conteúdo EXATO que ``writes("a")`` (o fake do Claude, em
# test_program.py) escreve — só existir o arquivo não bastaria para provar
# que a onda 3 (no modelo forte) é quem realmente satisfaz o critério, e não
# um resíduo qualquer deixado pelas duas ondas locais que erraram antes.
_STAGE_A_CHECK = [{
    "id": "C1", "text": "docs/a.md diz exatamente '# onda a'", "kind": "check",
    "command": "grep -qx '# onda a' docs/a.md", "cwd": ".",
}]


def _local_stage(**extra: Any) -> dict[str, Any]:
    return stage(
        "a", missionDraft=stage_draft("a", successCriteria=_STAGE_A_CHECK),
        execution={"executor": "local"}, **extra,
    )


def _tool_call_response(call_index: int, arguments: dict[str, Any]) -> bytes:
    response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": f"call-{call_index}",
                    "type": "function",
                    "function": {
                        "name": "submit_mission_result",
                        "arguments": json.dumps(arguments),
                    },
                }],
            },
        }],
    }
    return json.dumps(response).encode("utf-8")


def _local_transport_failing_twice_then_forbidden():
    """The local endpoint's fake: a well-formed ``tool_calls`` envelope both
    times (this is a CONTENT failure, not an envelope one — the two axes
    PIP-911 keeps separate) that never satisfies the stage's check criterion.
    The wrong content differs between the two calls so the diff itself
    differs cycle to cycle — an identical diff would trip the supervisor's
    own no-progress circuit breaker instead of exercising this rule. A third
    call is a defect in the fallback itself, not a scenario this test should
    silently tolerate."""

    calls: dict[str, int] = {"count": 0}

    def transport(url: str, payload: bytes, headers: dict) -> bytes:
        calls["count"] += 1
        if calls["count"] > 2:
            raise AssertionError(
                "o executor local foi chamado uma terceira vez: "
                "o rebaixamento para o modelo forte não aconteceu"
            )
        arguments: dict[str, Any] = {
            "done": True,
            "summary": "tarefa mecanica, resultado errado",
            "filesChanged": [{"path": "docs/a.md", "content": f"conteudo errado {calls['count']}\n"}],
            "criteriaSelfAssessment": [{"id": "C1", "met": False}],
            "blockers": [],
        }
        return _tool_call_response(calls["count"], arguments)

    return transport, calls


def _worker_runs(store: Any, mission_id: str) -> list[dict[str, Any]]:
    return [
        run for run in store.list_runs(mission_id)
        if run["executor"].split(":", 1)[0] == "worker"
    ]


class ExecutorFallbackTests(ProgramTestCase):
    def test_two_straight_local_verification_failures_fall_back_to_claude(self) -> None:
        h = self.program_harness([_local_stage()])
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        transport, calls = _local_transport_failing_twice_then_forbidden()

        h.run(local_base_url="http://fake-local", local_model="qwen-local-fake", local_transport=transport)

        mission_id = h.missions()["a"]
        self.assertIsNotNone(mission_id)
        self.assertEqual(h.store.get(mission_id)["status"], "completed")
        self.assertEqual(calls["count"], 2, "o endpoint local devia parar de ser chamado após o rebaixamento")

        runs = _worker_runs(h.store, mission_id)
        self.assertEqual(len(runs), 3, "esperava dois ciclos locais e um do modelo forte")
        first, second, third = runs

        self.assertEqual(first["executor_kind"], "local")
        self.assertEqual(first["verified"], "failed")
        self.assertEqual(second["executor_kind"], "local")
        self.assertEqual(second["verified"], "failed")
        self.assertEqual(third["executor_kind"], "claude")
        self.assertEqual(third["verified"], "passed")

        events = h.store.list_events(mission_id)
        fallback_events = [event for event in events if event["eventType"] == "executor.fallback"]
        self.assertEqual(len(fallback_events), 1, "o rebaixamento tem que emitir exatamente um evento")
        self.assertEqual(fallback_events[0]["payload"]["cycle"], third["cycle"])
        self.assertEqual(fallback_events[0]["payload"]["executorKind"], "claude")

        # C3: envelope (tool_calls) e conteúdo recuperado gravados SEPARADAMENTE
        # no evento do próprio run — os dois eram verdadeiros aqui (o defeito
        # simulado é de CONTEÚDO, não de envelope), e isso precisa aparecer.
        collected = {
            event["payload"]["runId"]: event["payload"]
            for event in events
            if event["eventType"] == "run.collected"
        }
        for run in (first, second):
            payload = collected[run["run_id"]]
            self.assertIs(payload["localEnvelope"], True)
            self.assertIs(payload["localRecovered"], True)
        self.assertNotIn("localEnvelope", collected[third["run_id"]])

    def test_a_local_stage_that_gets_it_right_never_falls_back(self) -> None:
        """Controle: o mesmo endpoint local, mas acertando de primeira — sem
        nenhuma falha de verificação, o rebaixamento nunca deveria disparar
        (senão o teste acima não provaria nada específico sobre DUAS
        falhas)."""

        h = self.program_harness([_local_stage()])

        def transport(url: str, payload: bytes, headers: dict) -> bytes:
            arguments = {
                "done": True,
                "summary": "onda mecanica concluida de primeira",
                "filesChanged": [{"path": "docs/a.md", "content": "# onda a\n"}],
                "criteriaSelfAssessment": [{"id": "C1", "met": True}],
                "blockers": [],
            }
            return _tool_call_response(1, arguments)

        h.fakes.scenario(reviewer=[satisfied()])
        h.run(local_base_url="http://fake-local", local_model="qwen-local-fake", local_transport=transport)

        mission_id = h.missions()["a"]
        self.assertEqual(h.store.get(mission_id)["status"], "completed")
        self.assertEqual(h.worker_calls(), 0, "nenhum worker Claude deveria ter rodado")

        runs = _worker_runs(h.store, mission_id)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["executor_kind"], "local")
        self.assertEqual(runs[0]["verified"], "passed")
        events = h.store.list_events(mission_id)
        self.assertFalse(any(event["eventType"] == "executor.fallback" for event in events))


class FallbackNeverBlocksWhatMainCompletedTests(ProgramTestCase):
    """Revisão do PR #207 (P1): uma onda `local` terminava SEMPRE bloqueada —
    endpoint não configurado ou fora do ar queimava os ciclos sem rebaixar.
    No `main` anterior a mesma onda rodava no Claude e concluía."""

    def _fallback_events(self, h: Any, mission_id: str) -> list[dict[str, Any]]:
        return [e for e in h.store.list_events(mission_id) if e["eventType"] == "executor.fallback"]

    def test_an_unconfigured_local_endpoint_falls_back_at_once_and_completes(self) -> None:
        h = self.program_harness([_local_stage()])
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        h.run()  # nenhum local_base_url / local_transport — como pelo CLI hoje
        mission_id = h.missions()["a"]
        self.assertEqual(h.store.get(mission_id)["status"], "completed")
        runs = _worker_runs(h.store, mission_id)
        self.assertEqual([r["executor_kind"] for r in runs], ["claude"], "tentou local sem endpoint")
        [evento] = self._fallback_events(h, mission_id)
        self.assertEqual(evento["payload"]["reason"], "local_not_configured")

    def test_an_endpoint_down_twice_falls_back_instead_of_blocking(self) -> None:
        calls = {"count": 0}

        def down(url: str, payload: bytes, headers: dict) -> bytes:
            calls["count"] += 1
            if calls["count"] > 2:
                raise AssertionError("chamou o endpoint local depois do rebaixamento")
            raise ConnectionRefusedError("fora do ar")

        h = self.program_harness([_local_stage()])
        h.fakes.scenario(worker=[writes("a")], reviewer=[satisfied()])
        h.run(local_base_url="http://fake-local", local_model="qwen-local-fake", local_transport=down)
        mission_id = h.missions()["a"]
        self.assertEqual(h.store.get(mission_id)["status"], "completed")
        runs = _worker_runs(h.store, mission_id)
        self.assertEqual([r["executor_kind"] for r in runs], ["local", "local", "claude"])
        [evento] = self._fallback_events(h, mission_id)
        self.assertEqual(evento["payload"]["reason"], "local_failures")

