"""PIP-838 (decisão D1): identidade de app via client_credentials.

Nenhum teste toca a rede — transporte e relógio são injetados.

O que estes testes guardam é o que a doc torna não óbvio e que quebra em produção
semanas depois de funcionar:

- o token de app dura 30 dias e **não tem refresh**. A renovação é reagir ao 401.
  Sem isso, a integração morre calada um mês depois de entrar no ar.
- pedir scopes diferentes REVOGA todos os tokens de app existentes. O conjunto de
  scopes é decidido uma vez e não pode variar por chamada.
"""

from __future__ import annotations

import json
from typing import Any, Mapping
from unittest import TestCase

from pipe_venture_builder.adapters.contracts import (
    SourceContractFailure,
    SourceUnauthorized,
)
from pipe_venture_builder.adapters.linear_oauth import (
    DEFAULT_SCOPES,
    AppTokenProvider,
)


def token_transport(*responses):
    """Devolve as respostas em ordem; registra o que foi enviado."""
    calls: list[dict[str, Any]] = []
    fila = list(responses)

    def transport(url: str, payload: bytes, headers: Mapping[str, str]):
        calls.append({"url": url, "body": payload.decode("utf-8"), "headers": dict(headers)})
        status, body = fila.pop(0) if fila else (200, {"access_token": "t", "expires_in": 100})
        raw = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        return status, raw, {}

    transport.calls = calls  # type: ignore[attr-defined]
    return transport


def provider_for(*responses, clock=None):
    transport = token_transport(*responses)
    relogio = clock or (lambda: 1000.0)
    return (
        AppTokenProvider(
            client_id_provider=lambda: "cid",
            client_secret_provider=lambda: "csecret",
            transport=transport,
            clock=relogio,
        ),
        transport,
    )


class TokenAcquisitionTests(TestCase):
    def test_asks_for_a_client_credentials_token_with_the_fixed_scopes(self) -> None:
        provider, transport = provider_for((200, {"access_token": "tok-1", "expires_in": 2591999}))
        self.assertEqual(provider(), "tok-1")

        body = transport.calls[0]["body"]
        self.assertIn("grant_type=client_credentials", body)
        self.assertIn("client_id=cid", body)
        self.assertIn(f"scope={DEFAULT_SCOPES.replace(',', '%2C')}", body)
        self.assertEqual(
            transport.calls[0]["headers"]["Content-Type"],
            "application/x-www-form-urlencoded",
        )

    def test_the_scope_set_is_fixed_and_not_per_call(self) -> None:
        """Pedir scopes diferentes revoga todos os tokens de app existentes.
        Variar scope por chamada seria um revoke silencioso em produção."""
        self.assertEqual(DEFAULT_SCOPES, "read,write")
        self.assertFalse(
            hasattr(AppTokenProvider, "scopes_for"),
            "não deve existir caminho para variar scope por chamada",
        )

    def test_the_token_is_cached_and_not_refetched_on_every_call(self) -> None:
        provider, transport = provider_for((200, {"access_token": "tok-1", "expires_in": 2591999}))
        self.assertEqual(provider(), "tok-1")
        self.assertEqual(provider(), "tok-1")
        self.assertEqual(len(transport.calls), 1, "token em cache não deve refazer a requisição")

    def test_an_expiring_token_is_renewed_before_it_dies(self) -> None:
        agora = [1000.0]
        provider, transport = provider_for(
            (200, {"access_token": "tok-1", "expires_in": 100}),
            (200, {"access_token": "tok-2", "expires_in": 100}),
            clock=lambda: agora[0],
        )
        self.assertEqual(provider(), "tok-1")
        agora[0] += 95  # dentro da margem de segurança
        self.assertEqual(provider(), "tok-2")
        self.assertEqual(len(transport.calls), 2)

    def test_invalidate_forces_a_new_token_on_the_next_call(self) -> None:
        """É assim que o 401 é tratado: não há refresh token, então a renovação
        é descartar o que está em cache e pedir outro."""
        provider, transport = provider_for(
            (200, {"access_token": "tok-1", "expires_in": 2591999}),
            (200, {"access_token": "tok-2", "expires_in": 2591999}),
        )
        self.assertEqual(provider(), "tok-1")
        provider.invalidate()
        self.assertEqual(provider(), "tok-2")
        self.assertEqual(len(transport.calls), 2)


class TokenFailureTests(TestCase):
    def test_rejected_credentials_are_unauthorized(self) -> None:
        provider, _ = provider_for((401, {"error": "invalid_client"}))
        with self.assertRaises(SourceUnauthorized):
            provider()

    def test_a_missing_client_credentials_toggle_is_reported_as_unauthorized(self) -> None:
        """Causa mais comum na estreia: o app foi criado sem marcar a opção."""
        provider, _ = provider_for(
            (400, {"error": "unauthorized_client", "error_description": "not enabled"})
        )
        with self.assertRaises(SourceUnauthorized):
            provider()

    def test_a_body_without_a_token_fails_closed(self) -> None:
        provider, _ = provider_for((200, {"token_type": "Bearer"}))
        with self.assertRaises(SourceContractFailure):
            provider()

    def test_a_non_json_body_never_leaks_into_the_error(self) -> None:
        provider, _ = provider_for((200, b"<html>proxy</html>"))
        with self.assertRaises(SourceContractFailure) as caught:
            provider()
        self.assertNotIn("html", str(caught.exception).lower())

    def test_neither_the_secret_nor_the_token_appears_in_a_raised_error(self) -> None:
        provider, _ = provider_for((401, {"error": "invalid_client", "hint": "csecret"}))
        with self.assertRaises(SourceUnauthorized) as caught:
            provider()
        mensagem = str(caught.exception)
        self.assertNotIn("csecret", mensagem)
        self.assertNotIn("cid", mensagem)

    def test_the_provider_exposes_no_way_to_read_the_cached_token(self) -> None:
        provider, _ = provider_for((200, {"access_token": "segredo", "expires_in": 100}))
        provider()
        self.assertNotIn("segredo", repr(provider))
        self.assertNotIn("segredo", str(vars(provider)) if hasattr(provider, "__dict__") else "")
