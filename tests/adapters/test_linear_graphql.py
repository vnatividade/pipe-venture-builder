"""PIP-833: transporte GraphQL para a leitura viva do Linear.

Nenhum destes testes toca a rede: o transporte é injetado. O que eles guardam é o
comportamento que a documentação da Linear torna não óbvio e que custa caro errar:

- cota estourada volta **HTTP 400 com `RATELIMITED`**, não 429. Classificar por status
  code transforma "recusado por cota" em "falhou", e o operador caça o bug errado.
- as relações vêm como `relations.nodes[].type`, não no formato `{blocks, blockedBy}`
  que o normalizador consome. A tradução é do transporte, não do normalizador.
"""

from __future__ import annotations

import json
from typing import Any, Mapping
from unittest import TestCase

from pipe_venture_builder.adapters.contracts import (
    SourceContractFailure,
    SourceRateLimited,
    SourceUnauthorized,
    SourceUnavailable,
)
from pipe_venture_builder.adapters.linear import LinearConnectorSource, LinearInventoryAdapter
from pipe_venture_builder.adapters.linear_graphql import (
    ISSUES_LIST,
    PROJECT_READ,
    LinearGraphQLInvoker,
)

CAPTURED_AT = "2026-08-05T12:00:00Z"

PROJECT_PAYLOAD = {
    "id": "11111111-1111-1111-1111-111111111111",
    "slugId": "abc123",
    "name": "Protocolo",
    "url": "https://linear.app/x/project/protocolo-abc123",
    "createdAt": CAPTURED_AT,
    "updatedAt": CAPTURED_AT,
    "status": {"name": "In Progress", "type": "started"},
}

ISSUE_PAYLOAD = {
    "id": "22222222-2222-2222-2222-222222222222",
    "identifier": "PIP-831",
    "title": "Tipar artefatos",
    "url": "https://linear.app/x/issue/PIP-831",
    "createdAt": CAPTURED_AT,
    "updatedAt": CAPTURED_AT,
    "completedAt": None,
    "canceledAt": None,
    "priority": 1,
    "state": {"name": "Done", "type": "completed"},
    "parent": {"id": "33333333-3333-3333-3333-333333333333"},
    "labels": {"nodes": [{"name": "priority:P0"}]},
    "relations": {"nodes": [{"type": "blocks", "relatedIssue": {"id": "44444444-4444-4444-4444-444444444444"}}]},
    "inverseRelations": {"nodes": [{"type": "blocks", "issue": {"id": "55555555-5555-5555-5555-555555555555"}}]},
}

QUOTA_HEADERS = {
    "x-ratelimit-requests-limit": "2500",
    "x-ratelimit-requests-remaining": "2499",
    "x-ratelimit-complexity-limit": "3000000",
    "x-ratelimit-complexity-remaining": "2999999",
    "x-complexity": "17",
}


def transport_returning(status: int, body: Any, headers: Mapping[str, str] | None = None):
    calls: list[dict[str, Any]] = []

    def transport(url: str, payload: bytes, headers_sent: Mapping[str, str]):
        calls.append({"url": url, "payload": json.loads(payload), "headers": dict(headers_sent)})
        raw = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        return status, raw, dict(QUOTA_HEADERS if headers is None else headers)

    transport.calls = calls  # type: ignore[attr-defined]
    return transport


def invoker_for(status: int, body: Any, headers: Mapping[str, str] | None = None):
    transport = transport_returning(status, body, headers)
    return LinearGraphQLInvoker(token_provider=lambda: "chave-de-teste", transport=transport), transport


class TransportTests(TestCase):
    def test_project_read_sends_the_versioned_query_and_the_bare_api_key(self) -> None:
        invoker, transport = invoker_for(200, {"data": {"project": PROJECT_PAYLOAD}})
        result = invoker(PROJECT_READ, {"query": PROJECT_PAYLOAD["id"]})

        self.assertEqual(result["project"]["name"], "Protocolo")
        sent = transport.calls[0]
        self.assertIn("query", sent["payload"])
        self.assertEqual(sent["payload"]["variables"]["id"], PROJECT_PAYLOAD["id"])
        # API key pessoal vai SEM o prefixo Bearer; só OAuth usa Bearer.
        self.assertEqual(sent["headers"]["Authorization"], "chave-de-teste")

    def test_unknown_operation_is_refused_before_any_request(self) -> None:
        invoker, transport = invoker_for(200, {"data": {}})
        with self.assertRaises(SourceContractFailure):
            invoker("issues.delete", {})
        self.assertEqual(transport.calls, [], "nenhuma requisição deveria ter saído")

    def test_relations_are_translated_into_the_shape_the_normalizer_consumes(self) -> None:
        invoker, _ = invoker_for(
            200,
            {"data": {"project": {"issues": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [ISSUE_PAYLOAD]}}}},
        )
        page = invoker(ISSUES_LIST, {"project": PROJECT_PAYLOAD["id"], "limit": 50})

        issue = page["issues"][0]
        self.assertEqual([r["id"] for r in issue["relations"]["blocks"]], ["44444444-4444-4444-4444-444444444444"])
        self.assertEqual([r["id"] for r in issue["relations"]["blockedBy"]], ["55555555-5555-5555-5555-555555555555"])

    def test_rate_limit_comes_as_http_400_with_a_body_code_not_429(self) -> None:
        invoker, _ = invoker_for(
            400,
            {"errors": [{"message": "rate limited", "extensions": {"code": "RATELIMITED"}}]},
        )
        with self.assertRaises(SourceRateLimited):
            invoker(PROJECT_READ, {"query": "x"})

    def test_other_http_400_is_a_contract_failure_not_a_rate_limit(self) -> None:
        invoker, _ = invoker_for(400, {"errors": [{"message": "bad field"}]})
        with self.assertRaises(SourceContractFailure):
            invoker(PROJECT_READ, {"query": "x"})

    def test_401_and_403_are_unauthorized(self) -> None:
        for status in (401, 403):
            invoker, _ = invoker_for(status, {"errors": [{"message": "nope"}]})
            with self.subTest(status=status), self.assertRaises(SourceUnauthorized):
                invoker(PROJECT_READ, {"query": "x"})

    def test_5xx_is_unavailable_and_retryable(self) -> None:
        invoker, _ = invoker_for(503, b"upstream down")
        with self.assertRaises(SourceUnavailable) as caught:
            invoker(PROJECT_READ, {"query": "x"})
        self.assertTrue(caught.exception.retryable)

    def test_non_json_body_fails_closed_instead_of_leaking_it(self) -> None:
        invoker, _ = invoker_for(200, b"<html>proxy error</html>")
        with self.assertRaises(SourceContractFailure) as caught:
            invoker(PROJECT_READ, {"query": "x"})
        self.assertNotIn("html", str(caught.exception).lower())

    def test_quota_headers_are_recorded_for_measurement(self) -> None:
        """A doc da Linear se contradiz (2.500 vs 5.000 req/h). Só dá para dimensionar medindo."""
        invoker, _ = invoker_for(200, {"data": {"project": PROJECT_PAYLOAD}})
        invoker(PROJECT_READ, {"query": PROJECT_PAYLOAD["id"]})

        quota = invoker.last_quota
        self.assertEqual(quota["requestsLimit"], 2500)
        self.assertEqual(quota["complexityLimit"], 3000000)
        self.assertEqual(quota["complexity"], 17)

    def test_missing_quota_headers_do_not_break_the_read(self) -> None:
        invoker, _ = invoker_for(200, {"data": {"project": PROJECT_PAYLOAD}}, headers={})
        invoker(PROJECT_READ, {"query": PROJECT_PAYLOAD["id"]})
        self.assertEqual(invoker.last_quota, {})

    def test_the_token_never_appears_in_a_raised_error(self) -> None:
        invoker, _ = invoker_for(401, {"errors": [{"message": "unauthorized"}]})
        with self.assertRaises(SourceUnauthorized) as caught:
            invoker(PROJECT_READ, {"query": "x"})
        self.assertNotIn("chave-de-teste", str(caught.exception))


class EndToEndThroughTheExistingAdapterTests(TestCase):
    """O transporte novo entra pela mesma porta que o conector do host: a paginação,
    a classificação de erro e a normalização testadas continuam valendo."""

    def test_graphql_transport_produces_a_valid_snapshot(self) -> None:
        responses = [
            {"data": {"project": PROJECT_PAYLOAD}},
            {"data": {"project": {"issues": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [ISSUE_PAYLOAD]}}}},
        ]

        def transport(url: str, payload: bytes, headers: Mapping[str, str]):
            return 200, json.dumps(responses.pop(0)).encode("utf-8"), dict(QUOTA_HEADERS)

        invoker = LinearGraphQLInvoker(token_provider=lambda: "k", transport=transport)
        snapshot = LinearInventoryAdapter(LinearConnectorSource(invoker)).capture(
            PROJECT_PAYLOAD["id"], captured_at=CAPTURED_AT
        )

        self.assertEqual(snapshot["sourceSystem"], "linear")
        self.assertFalse(snapshot["constraints"]["rawPayloadPersisted"])
        issue = next(r for r in snapshot["records"] if r["entityType"] == "issue")
        self.assertEqual(issue["sourceKey"], "PIP-831")
        self.assertEqual(issue["attributes"]["labels"], ["priority:P0"])
        self.assertIn("blocks", {rel["type"] for rel in issue["relationships"]})
        self.assertIn("blocked_by", {rel["type"] for rel in issue["relationships"]})


class ComplexityBudgetTests(TestCase):
    """A cota que derruba a leitura não é a de requisições, é a de complexidade.

    Medido contra a API em 2026-08-05: a query de issues custa ~139 pontos por issue
    (25 → 3.469; 50 → 6.936) contra um teto de 10.000 por query. Com `first: 100` a
    Linear responde "Query too complex" e a leitura inteira falha. Como o limite
    padrão de registros é 200, sem este teto **todo snapshot real falharia** — e
    falharia como `source_contract_failed`, que não diz ao operador que o problema
    é tamanho de página.
    """

    def test_page_size_is_capped_regardless_of_the_record_limit(self) -> None:
        from pipe_venture_builder.adapters.linear_graphql import MAX_PAGE_SIZE

        invoker, transport = invoker_for(
            200,
            {"data": {"project": {"issues": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}},
        )
        invoker(ISSUES_LIST, {"project": "p", "limit": 200})
        self.assertEqual(transport.calls[0]["payload"]["variables"]["first"], MAX_PAGE_SIZE)

    def test_a_smaller_request_is_honoured(self) -> None:
        invoker, transport = invoker_for(
            200,
            {"data": {"project": {"issues": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}},
        )
        invoker(ISSUES_LIST, {"project": "p", "limit": 10})
        self.assertEqual(transport.calls[0]["payload"]["variables"]["first"], 10)


class AppIdentityTests(TestCase):
    """PIP-838: o transporte precisa falar as duas identidades.

    API key pessoal vai SEM prefixo; access token OAuth vai com `Bearer`. E como o
    token de app não tem refresh, um 401 precisa disparar renovação e UMA nova
    tentativa — senão a integração morre calada 30 dias depois de entrar no ar.
    """

    def test_the_bearer_scheme_is_used_when_configured(self) -> None:
        transport = transport_returning(200, {"data": {"project": PROJECT_PAYLOAD}})
        invoker = LinearGraphQLInvoker(
            token_provider=lambda: "tok-app",
            authorization_scheme="Bearer",
            transport=transport,
        )
        invoker(PROJECT_READ, {"query": "x"})
        self.assertEqual(transport.calls[0]["headers"]["Authorization"], "Bearer tok-app")

    def test_the_api_key_path_keeps_no_prefix(self) -> None:
        invoker, transport = invoker_for(200, {"data": {"project": PROJECT_PAYLOAD}})
        invoker(PROJECT_READ, {"query": "x"})
        self.assertEqual(transport.calls[0]["headers"]["Authorization"], "chave-de-teste")

    def test_a_401_renews_the_token_and_retries_once(self) -> None:
        respostas = [
            (401, {"errors": [{"message": "expired"}]}),
            (200, {"data": {"project": PROJECT_PAYLOAD}}),
        ]
        enviados: list[str] = []
        tokens = iter(["velho", "novo"])
        atual = [next(tokens)]
        renovacoes: list[int] = []

        def transport(url: str, payload: bytes, headers: Mapping[str, str]):
            enviados.append(headers["Authorization"])
            status, body = respostas.pop(0)
            return status, json.dumps(body).encode("utf-8"), dict(QUOTA_HEADERS)

        def renovar() -> None:
            renovacoes.append(1)
            atual[0] = next(tokens)

        invoker = LinearGraphQLInvoker(
            token_provider=lambda: atual[0],
            authorization_scheme="Bearer",
            transport=transport,
            on_unauthorized=renovar,
        )
        resultado = invoker(PROJECT_READ, {"query": "x"})

        self.assertEqual(resultado["project"]["name"], "Protocolo")
        self.assertEqual(enviados, ["Bearer velho", "Bearer novo"])
        self.assertEqual(len(renovacoes), 1, "renovação deve acontecer exatamente uma vez")

    def test_a_second_401_gives_up_instead_of_looping(self) -> None:
        """Credencial revogada não pode virar laço infinito de renovação."""
        tentativas: list[int] = []

        def transport(url: str, payload: bytes, headers: Mapping[str, str]):
            tentativas.append(1)
            return 401, json.dumps({"errors": [{"message": "nope"}]}).encode("utf-8"), {}

        invoker = LinearGraphQLInvoker(
            token_provider=lambda: "t",
            authorization_scheme="Bearer",
            transport=transport,
            on_unauthorized=lambda: None,
        )
        with self.assertRaises(SourceUnauthorized):
            invoker(PROJECT_READ, {"query": "x"})
        self.assertEqual(len(tentativas), 2, "uma tentativa original e exatamente uma repetição")

    def test_without_a_renewal_hook_a_401_fails_immediately(self) -> None:
        invoker, transport = invoker_for(401, {"errors": [{"message": "nope"}]})
        with self.assertRaises(SourceUnauthorized):
            invoker(PROJECT_READ, {"query": "x"})
        self.assertEqual(len(transport.calls), 1, "sem hook de renovação não há repetição")
