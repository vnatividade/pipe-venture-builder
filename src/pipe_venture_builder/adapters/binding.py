"""Vínculo Linear por venture: `.pipe/linear.json` (PIP-833).

Esta é a peça que faz a diretriz "toda venture do Pipe tem seus tickets no Linear"
valer sem alterar código: a venture declara o vínculo, o toolkit lê. O arquivo vive
no repositório da venture, nunca no toolkit.

O arquivo **não** carrega credencial. O token vem do ambiente, colocado lá pelo fluxo
Vaultwarden aprovado — manuseio de segredo é gate absoluto e não deve ficar dependendo
de disciplina de quem edita um JSON.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from ..errors import PipeError
from ..exit_codes import INPUT_INVALID_JSON, INPUT_UNAVAILABLE

BINDING_RELATIVE_PATH = ".pipe/linear.json"
BINDING_SCHEMA_RELATIVE_PATH = "schemas/LinearBinding.schema.json"
TOKEN_ENV = "LINEAR_API_KEY"

VAULT_ITEM = "Linear — API key pessoal (workspace Natiivis)"
TOKEN_HINT = (
    f"Defina {TOKEN_ENV} a partir do cofre antes de rodar: "
    f'export {TOKEN_ENV}="$(vw get item \'{VAULT_ITEM}\' | jq -r .notes)". '
    "O toolkit nunca lê o cofre sozinho — manuseio de segredo é gate absoluto."
)


def load_binding(product_root: Path, toolkit_root: Path) -> dict[str, Any]:
    path = product_root / BINDING_RELATIVE_PATH
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PipeError(
            code="LINEAR_BINDING_MISSING",
            message=(
                f"No Linear binding at {BINDING_RELATIVE_PATH}. "
                "Declare the workspace, team, and project this repository writes to."
            ),
            exit_code=INPUT_UNAVAILABLE,
        ) from exc

    try:
        binding = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PipeError(
            code="LINEAR_BINDING_INVALID_JSON",
            message=f"{BINDING_RELATIVE_PATH} is not valid JSON.",
            exit_code=INPUT_INVALID_JSON,
        ) from exc

    schema = json.loads(
        (toolkit_root / BINDING_SCHEMA_RELATIVE_PATH).read_text(encoding="utf-8")
    )
    findings = sorted(
        Draft202012Validator(schema).iter_errors(binding),
        key=lambda error: list(error.path),
    )
    if findings:
        raise PipeError(
            code="LINEAR_BINDING_INVALID",
            message=f"{BINDING_RELATIVE_PATH} does not match the Linear binding contract.",
            exit_code=INPUT_INVALID_JSON,
            details=[
                {
                    "path": "/".join(str(part) for part in error.path) or "(root)",
                    "message": error.message,
                    "rule": error.validator,
                }
                for error in findings
            ],
        )
    return binding


def read_token(environment: dict[str, str] | None = None) -> str:
    env = environment if environment is not None else dict(os.environ)
    token = (env.get(TOKEN_ENV) or "").strip()
    if not token:
        raise PipeError(
            code="LINEAR_TOKEN_MISSING",
            message=f"{TOKEN_ENV} is not set. {TOKEN_HINT}",
            exit_code=INPUT_UNAVAILABLE,
        )
    return token
