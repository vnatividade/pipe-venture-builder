"""Transporte GraphQL para a leitura viva do Linear (PIP-833).

Entra pela mesma porta que o conector do host: é um `ConnectorInvoker`, então a
paginação, a classificação de erro e a normalização já testadas em
`LinearConnectorSource` continuam valendo sem alteração.

Por que GraphQL e não o MCP nesta camada: o snapshot alimenta gate e reconciliação,
e isso exige seleção explícita de campos, shape versionado e erro estruturado. O MCP
não dá nenhum dos três — e a Linear não publica a lista de tools, então a superfície
pode mudar sem diff no nosso repositório.

Sem dependência nova: `urllib.request` da stdlib.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Mapping

from .contracts import (
    SourceContractFailure,
    SourceRateLimited,
    SourceUnauthorized,
    SourceUnavailable,
)

ENDPOINT = "https://api.linear.app/graphql"
DEFAULT_TIMEOUT_SECONDS = 20
MAX_RESPONSE_BYTES = 8 * 1024 * 1024

# Verbos internos do adapter. NÃO são nomes de tool do MCP: a versão anterior
# usava `linear_get_project`/`linear_list_issues`, que não existem em lugar nenhum
# (o MCP oficial expõe `get_project`/`list_issues`, e a escrita é `save_issue`).
# Nomes neutros evitam que a próxima pessoa leia isto como um contrato de MCP.
PROJECT_READ = "project.read"
ISSUES_LIST = "issues.list"

_QUERY_FILES = {
    PROJECT_READ: "project-read.graphql",
    ISSUES_LIST: "issues-list.graphql",
}

# `type` das relações que o normalizador consome. Qualquer outro tipo (related,
# duplicate, similar) é descartado de propósito: relação sem consumidor é ruído.
_BLOCKING_RELATION = "blocks"

Transport = Callable[[str, bytes, Mapping[str, str]], tuple[int, bytes, Mapping[str, str]]]


@lru_cache(maxsize=None)
def _load_query(operation: str) -> str:
    filename = _QUERY_FILES[operation]
    return (Path(__file__).resolve().parent / "queries" / filename).read_text(encoding="utf-8")


def _urllib_transport(
    url: str, payload: bytes, headers: Mapping[str, str]
) -> tuple[int, bytes, Mapping[str, str]]:
    request = urllib.request.Request(url, data=payload, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            return response.status, response.read(MAX_RESPONSE_BYTES), dict(response.headers)
    except urllib.error.HTTPError as exc:  # corpo de erro ainda importa: traz o código
        return exc.code, exc.read(MAX_RESPONSE_BYTES), dict(exc.headers or {})
    except urllib.error.URLError as exc:
        raise SourceUnavailable() from exc
    except TimeoutError as exc:
        raise SourceUnavailable() from exc


def _as_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _quota_from(headers: Mapping[str, str]) -> dict[str, int]:
    lowered = {str(k).lower(): v for k, v in headers.items()}
    mapping = {
        "requestsLimit": "x-ratelimit-requests-limit",
        "requestsRemaining": "x-ratelimit-requests-remaining",
        "complexityLimit": "x-ratelimit-complexity-limit",
        "complexityRemaining": "x-ratelimit-complexity-remaining",
        "complexity": "x-complexity",
    }
    quota: dict[str, int] = {}
    for key, header in mapping.items():
        parsed = _as_int(lowered.get(header))
        if parsed is not None:
            quota[key] = parsed
    return quota


def _error_codes(body: Mapping[str, Any]) -> set[str]:
    errors = body.get("errors")
    if not isinstance(errors, list):
        return set()
    codes: set[str] = set()
    for error in errors:
        if not isinstance(error, Mapping):
            continue
        extensions = error.get("extensions")
        if isinstance(extensions, Mapping) and extensions.get("code"):
            codes.add(str(extensions["code"]).strip().upper())
    return codes


def _relation_ids(container: Any, node_key: str) -> list[dict[str, str]]:
    nodes = container.get("nodes") if isinstance(container, Mapping) else None
    if not isinstance(nodes, list):
        return []
    out: list[dict[str, str]] = []
    for node in nodes:
        if not isinstance(node, Mapping):
            continue
        if str(node.get("type", "")).lower() != _BLOCKING_RELATION:
            continue
        target = node.get(node_key)
        if isinstance(target, Mapping) and target.get("id"):
            out.append({"id": str(target["id"])})
    return out


def _reshape_issue(issue: Mapping[str, Any]) -> dict[str, Any]:
    """Traduz o shape da API para o que `_normalize_linear` consome.

    A API devolve `relations.nodes[].type`; o normalizador espera
    `{"blocks": [...], "blockedBy": [...]}`. A tradução é responsabilidade do
    transporte — o normalizador não deve saber por qual cano o dado chegou.
    """
    reshaped = dict(issue)
    reshaped["relations"] = {
        "blocks": _relation_ids(issue.get("relations"), "relatedIssue"),
        "blockedBy": _relation_ids(issue.get("inverseRelations"), "issue"),
    }
    reshaped.pop("inverseRelations", None)
    # `status` é o nome do campo no Project; `state` é o que o normalizador lê.
    if "status" in reshaped and "state" not in reshaped:
        reshaped["state"] = reshaped.pop("status")
    return reshaped


class LinearGraphQLInvoker:
    """`ConnectorInvoker` sobre a API GraphQL do Linear. Só leitura.

    A credencial nunca é armazenada: `token_provider` é chamado por requisição, e o
    valor não aparece em nenhuma exceção — as exceções deste módulo são as classes
    fixas de `contracts.py`, que não carregam material da fonte.
    """

    def __init__(
        self,
        *,
        token_provider: Callable[[], str],
        endpoint: str = ENDPOINT,
        transport: Transport | None = None,
    ) -> None:
        self._token_provider = token_provider
        self._endpoint = endpoint
        self._transport = transport or _urllib_transport
        self.last_quota: dict[str, int] = {}

    def __call__(self, operation: str, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        if operation not in _QUERY_FILES:
            # Conjunto fechado de operações: o chamador não escolhe query arbitrária.
            raise SourceContractFailure()
        variables = self._variables(operation, arguments)
        body = self._post(_load_query(operation), variables)
        return self._shape(operation, body)

    def _variables(self, operation: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        if operation == PROJECT_READ:
            return {"id": str(arguments.get("query") or arguments.get("id") or "")}
        first = arguments.get("limit")
        variables: dict[str, Any] = {
            "id": str(arguments.get("project") or arguments.get("id") or ""),
            "first": int(first) if isinstance(first, int) and first > 0 else 50,
        }
        cursor = arguments.get("cursor")
        if cursor:
            variables["after"] = str(cursor)
        return variables

    def _post(self, query: str, variables: Mapping[str, Any]) -> Mapping[str, Any]:
        payload = json.dumps({"query": query, "variables": dict(variables)}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            # API key pessoal vai sem `Bearer`; só access token OAuth usa o prefixo.
            "Authorization": self._token_provider(),
            "User-Agent": "pipe-venture-builder/linear-read",
        }
        status, raw, response_headers = self._transport(self._endpoint, payload, headers)
        self.last_quota = _quota_from(response_headers)

        if status in (401, 403):
            raise SourceUnauthorized()
        if status == 429:
            raise SourceRateLimited()
        if status >= 500:
            raise SourceUnavailable()

        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            # Nunca reemitir o corpo: pode ser página de proxy com material arbitrário.
            raise SourceContractFailure() from exc
        if not isinstance(body, Mapping):
            raise SourceContractFailure()

        codes = _error_codes(body)
        # Cota estourada é HTTP 400 com RATELIMITED no corpo, NÃO 429. Classificar
        # por status code aqui transformaria "recusado por cota" em "falhou".
        if "RATELIMITED" in codes:
            raise SourceRateLimited()
        if codes & {"AUTHENTICATION_ERROR", "FORBIDDEN", "UNAUTHENTICATED"}:
            raise SourceUnauthorized()
        if body.get("errors"):
            raise SourceContractFailure()
        return body

    def _shape(self, operation: str, body: Mapping[str, Any]) -> Mapping[str, Any]:
        data = body.get("data")
        if not isinstance(data, Mapping):
            raise SourceContractFailure()
        project = data.get("project")
        if not isinstance(project, Mapping):
            raise SourceContractFailure()

        if operation == PROJECT_READ:
            return {"project": _reshape_issue(project)}

        issues = project.get("issues")
        if not isinstance(issues, Mapping) or not isinstance(issues.get("nodes"), list):
            raise SourceContractFailure()
        return {
            "issues": [_reshape_issue(node) for node in issues["nodes"] if isinstance(node, Mapping)],
            "pageInfo": issues.get("pageInfo") or {},
        }
