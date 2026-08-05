"""Identidade de app no Linear via `client_credentials` (PIP-838, decisão D1).

Por que app OAuth e não API key pessoal: com API key, todo ticket e comentário
criado por agente aparece assinado pelo fundador. Isso contraria o primeiro
princípio das diretrizes de agente da Linear — um agente deve sempre revelar que é
um agente — e é irreversível para trás: não dá para reatribuir histórico.

Duas propriedades deste fluxo governam o desenho, e as duas quebram em produção
semanas depois de funcionar se forem ignoradas:

1. **O token dura 30 dias e NÃO tem refresh token.** A doc é explícita: o servidor
   deve buscar um token novo ao receber 401. Sem essa reação, a integração morre
   calada um mês depois de entrar no ar — o pior modo de falha possível, porque
   até lá tudo parece perfeito.
2. **Pedir scopes diferentes revoga todos os tokens de app existentes.** Por isso
   o conjunto de scopes é constante de módulo e não há caminho para variá-lo por
   chamada: um scope dinâmico seria um revoke silencioso em produção.

Sem dependência nova: `urllib.request` da stdlib.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Mapping

from .contracts import (
    SourceContractFailure,
    SourceUnauthorized,
    SourceUnavailable,
)

TOKEN_ENDPOINT = "https://api.linear.app/oauth/token"
DEFAULT_TIMEOUT_SECONDS = 20
MAX_RESPONSE_BYTES = 256 * 1024

# Decidido uma vez, em PIP-838. `app:assignable`/`app:mentionable` ficam de fora de
# propósito: fariam o app aparecer como mencionável e delegável antes de existir
# qualquer coisa que responda a menção, e um agente que ignora quem o chama é pior
# que agente nenhum. Adicioná-los depois custa um revoke controlado.
DEFAULT_SCOPES = "read,write"

# Margem antes do vencimento. O token vale 30 dias; renovar com folga evita a
# corrida entre "ainda válido quando checamos" e "expirado quando chegou".
RENEWAL_MARGIN_SECONDS = 300

Transport = Callable[[str, bytes, Mapping[str, str]], tuple[int, bytes, Mapping[str, str]]]


def _urllib_transport(
    url: str, payload: bytes, headers: Mapping[str, str]
) -> tuple[int, bytes, Mapping[str, str]]:
    request = urllib.request.Request(url, data=payload, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            return response.status, response.read(MAX_RESPONSE_BYTES), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(MAX_RESPONSE_BYTES), dict(exc.headers or {})
    except urllib.error.URLError as exc:
        raise SourceUnavailable() from exc
    except TimeoutError as exc:
        raise SourceUnavailable() from exc


class AppTokenProvider:
    """Fornece o access token de ator `app`, buscando e renovando sob demanda.

    Nada aqui é persistido em disco: o token vive só na memória do processo. Ele
    também não aparece em `repr`, em log nem em exceção — as exceções levantadas são
    as classes fixas de `contracts.py`, que por contrato não carregam material da
    fonte nem credencial.
    """

    __slots__ = ("_client_id", "_client_secret", "_transport", "_clock", "_token", "_expires_at")

    def __init__(
        self,
        *,
        client_id_provider: Callable[[], str],
        client_secret_provider: Callable[[], str],
        transport: Transport | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._client_id = client_id_provider
        self._client_secret = client_secret_provider
        self._transport = transport or _urllib_transport
        self._clock = clock or time.monotonic
        self._token: str | None = None
        self._expires_at: float = 0.0

    def __repr__(self) -> str:  # nunca revela o token em cache
        estado = "com token" if self._token else "sem token"
        return f"<AppTokenProvider {estado}>"

    def __call__(self) -> str:
        if self._token is not None and self._clock() < self._expires_at:
            return self._token
        self._token, self._expires_at = self._fetch()
        return self._token

    def invalidate(self) -> None:
        """Descarta o token em cache.

        Este é o mecanismo de renovação inteiro: como não existe refresh token, a
        resposta correta a um 401 é esquecer o que temos e pedir outro.
        """
        self._token = None
        self._expires_at = 0.0

    def _fetch(self) -> tuple[str, float]:
        payload = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self._client_id(),
                "client_secret": self._client_secret(),
                "scope": DEFAULT_SCOPES,
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "pipe-venture-builder/linear-app-auth",
        }

        status, raw, _ = self._transport(TOKEN_ENDPOINT, payload, headers)

        if status in (400, 401, 403):
            # 400 com `unauthorized_client` é a estreia mais comum: o app foi criado
            # sem marcar "Enable client credentials token". Do ponto de vista do
            # chamador é o mesmo problema — a credencial não autoriza.
            raise SourceUnauthorized()
        if status >= 500:
            raise SourceUnavailable()

        try:
            body: Any = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            # Nunca reemitir o corpo: pode ser página de proxy com material arbitrário.
            raise SourceContractFailure() from exc
        if not isinstance(body, Mapping):
            raise SourceContractFailure()

        token = body.get("access_token")
        if not isinstance(token, str) or not token:
            raise SourceContractFailure()

        expires_in = body.get("expires_in")
        lifetime = float(expires_in) if isinstance(expires_in, (int, float)) else 0.0
        # Vida útil menor que a margem não vira instante negativo: no pior caso o
        # token é buscado de novo na próxima chamada, que é o comportamento seguro.
        expires_at = self._clock() + max(lifetime - RENEWAL_MARGIN_SECONDS, 0.0)
        return token, expires_at
