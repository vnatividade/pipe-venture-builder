"""Clean-context blocker responder: one read-only ``claude -p`` call when a
worker returns ``blockers``, so the founder is not paged for a routine
technical question the repository itself can answer (PIP-906).

The responder never edits, writes, or runs a shell command: it only reads the
mission and the diff-free repository state and answers with the response
schema (``{"action": "instruct"|"escalate", "instructions": str, "reason":
str}``). Anything that is not a valid response is treated the same as
``escalate``: the supervisor never guesses an answer, and a deterministic
keyword guard (credential, merge, production/deploy, billing) overrides
``instruct`` regardless of what the model said — see
``supervisor.contains_sensitive_terms``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .worker import (
    DEFAULT_MODEL,
    DEFAULT_POLL_SECONDS,
    ClaudeProcess,
    ClaudeResult,
    _json_candidates,
    isolation_args,
    run_claude,
)


RESPONDER_MAX_TURNS = 10
# Read-only, and deliberately narrower than the reviewer's: no Bash at all
# (the reviewer is trusted to run `git diff`/`git log`; the responder only
# needs to read files to answer a technical question).
RESPONDER_ALLOWED_TOOLS = "Read,Grep,Glob"
RESPONDER_OUTPUT_INVALID = "responder_output_invalid"
RESPONDER_RUN_FAILED = "responder_run_failed"
DEFAULT_RESPONSE_TIMEOUT_SECONDS = 600.0
ACTIONS = ("instruct", "escalate")
MAX_INSTRUCTIONS_CHARS = 4000
MAX_REASON_CHARS = 600

# Sem "$schema": mesma restrição medida no revisor (VERDICT_SCHEMA).
RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["action", "instructions", "reason"],
    "properties": {
        "action": {"type": "string", "enum": list(ACTIONS)},
        "instructions": {"type": "string", "maxLength": MAX_INSTRUCTIONS_CHARS},
        "reason": {"type": "string", "maxLength": MAX_REASON_CHARS},
    },
}


@dataclass
class ResponseResult:
    action: str | None
    instructions: str | None
    valid: bool
    reason: str | None
    claude: ClaudeResult


def build_responder_prompt(mission: Mapping[str, Any], blockers: Sequence[str]) -> str:
    lines = [
        "Você é o respondedor de contexto limpo de UMA missão do Pipe. Um worker parou "
        "porque reportou bloqueios técnicos. Decida se a própria missão ou o repositório "
        "já respondem, sem executar nada (você só lê arquivos).",
        "",
        f"## Missão {mission['missionId']} v{mission['version']} — {mission['title']}",
        f"Intenção do fundador: {mission['intent']}",
        f"Problema: {mission['problem']}",
        "",
        "## Critérios de sucesso",
    ]
    for criterion in mission["successCriteria"]:
        lines.append(f"- {criterion['id']} ({criterion['kind']}): {criterion['text']}")
    lines += ["", "## Não-objetivos"]
    lines += [f"- {item}" for item in mission["nonGoals"]] or ["- (nenhum declarado)"]
    lines += ["", "## Reservado ao fundador (nunca responda por conta própria)"]
    lines += [f"- {item}" for item in mission["reservedToHuman"]] or ["- (nenhum declarado)"]
    lines += ["", "## Write set"]
    lines += [f"- {item}" for item in mission["workspace"]["writeSet"]]
    lines += ["", "## Bloqueios reportados pelo worker"]
    lines += [f"- {text}" for text in blockers]
    lines += [
        "",
        "## Instruções",
        "Responda `instruct` só quando a resposta está no repositório, na missão ou é uma "
        "orientação técnica objetiva dentro do escopo (write set, critérios, ferramentas "
        "permitidas); `instructions` deve ser a resposta pronta para o próximo worker, sem "
        "inventar evidência.",
        "Responda `escalate` (instructions vazio) para qualquer coisa que envolva "
        "credencial, segredo, merge, produção/deploy, cobrança/billing, comunicação externa "
        "ou que esteja fora do escopo desta missão: isso é do fundador, não seu.",
        "Responda apenas com o JSON do schema.",
    ]
    return "\n".join(lines) + "\n"


def responder_command(
    prompt: str,
    *,
    claude_bin: str,
    budget_left: float,
    model: str = DEFAULT_MODEL,
) -> list[str]:
    return [
        claude_bin,
        "-p",
        prompt,
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(RESPONSE_SCHEMA, separators=(",", ":")),
        "--max-turns",
        str(RESPONDER_MAX_TURNS),
        "--max-budget-usd",
        f"{budget_left:.2f}",
        "--permission-mode",
        "plan",
        "--allowedTools",
        RESPONDER_ALLOWED_TOOLS,
        *isolation_args(),
        "--model",
        model,
    ]


def run_responder(
    mission: Mapping[str, Any],
    blockers: Sequence[str],
    *,
    claude_bin: str,
    cwd: str | Path,
    budget_left: float,
    model: str = DEFAULT_MODEL,
    timeout: float = DEFAULT_RESPONSE_TIMEOUT_SECONDS,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    should_stop: Callable[[], bool] | None = None,
    env: Mapping[str, str] | None = None,
    on_start: Callable[[ClaudeProcess], None] | None = None,
) -> ResponseResult:
    prompt = build_responder_prompt(mission, blockers)
    command = responder_command(prompt, claude_bin=claude_bin, budget_left=budget_left, model=model)
    claude = run_claude(
        command,
        cwd=cwd,
        model=model,
        timeout=timeout,
        poll_seconds=poll_seconds,
        should_stop=should_stop,
        env=env,
        on_start=on_start,
    )
    if claude.status != "collected":
        return _failed(RESPONDER_RUN_FAILED, claude)
    parsed = parse_response(claude.structured_output, claude.result_text)
    if parsed is None:
        return _failed(RESPONDER_OUTPUT_INVALID, claude)
    return ResponseResult(
        action=parsed["action"],
        instructions=parsed["instructions"],
        valid=True,
        reason=None,
        claude=claude,
    )


def parse_response(structured_output: Any, result_text: str | None) -> dict[str, Any] | None:
    """A normalised response, or ``None`` when neither source holds a valid one."""

    candidates: list[Any] = []
    if structured_output is not None:
        candidates.append(structured_output)
    if result_text:
        candidates.extend(_json_candidates(result_text))
    for candidate in candidates:
        normalized = _normalize_response(candidate)
        if normalized is not None:
            return normalized
    return None


def _normalize_response(candidate: Any) -> dict[str, Any] | None:
    if not isinstance(candidate, Mapping) or candidate.get("action") not in ACTIONS:
        return None
    instructions = candidate.get("instructions")
    if not isinstance(instructions, str):
        return None
    return {"action": candidate["action"], "instructions": instructions}


def _failed(reason: str, claude: ClaudeResult) -> ResponseResult:
    return ResponseResult(action=None, instructions=None, valid=False, reason=reason, claude=claude)
