"""Clean-context reviewer: one read-only ``claude -p`` per cycle, JSON by schema.

The reviewer never sees the worker's transcript. It receives the mission
(criteria with kind/text/question, non-goals, write set) and the diff, and must
answer with the verdict schema (``reviewer-verdict.schema.json``). Anything that
is not a valid verdict is treated as ``blocked`` with a fixed reason: the
supervisor never guesses a verdict.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .worker import (
    DEFAULT_MODEL,
    DEFAULT_POLL_SECONDS,
    ClaudeProcess,
    ClaudeResult,
    _json_candidates,
    isolation_args,
    run_claude,
)


REVIEWER_MAX_TURNS = 20
REVIEWER_ALLOWED_TOOLS = "Read,Grep,Glob,Bash(git diff *),Bash(git log *)"
REVIEWER_OUTPUT_INVALID = "reviewer_output_invalid"
REVIEWER_RUN_FAILED = "reviewer_run_failed"
DEFAULT_REVIEW_TIMEOUT_SECONDS = 900.0
MAX_DIFF_CHARS = 200_000
# The prompt asks for short evidence; the schema accepts much more. With the
# two equal, a reviewer that overshoots by a few chars exhausts the CLI's
# structured-output retries and a correct verdict becomes an escalation.
EVIDENCE_PROMPT_CHARS = 300
EVIDENCE_SCHEMA_MAX_CHARS = 1000
REASON_SCHEMA_MAX_CHARS = 600
VERDICTS = ("satisfied", "needs_revision", "out_of_mission", "blocked")

# Sem "$schema": o validador do claude 2.1.267 recusa a URI draft 2020-12 e o
# run morre antes da sessão (medido na demo real de 11/09).
VERDICT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["verdict", "criteria", "reasons"],
    "properties": {
        "verdict": {"type": "string", "enum": list(VERDICTS)},
        "criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "met", "evidence"],
                "properties": {
                    "id": {"type": "string"},
                    "met": {"type": "boolean"},
                    "evidence": {"type": "string", "maxLength": EVIDENCE_SCHEMA_MAX_CHARS},
                },
            },
        },
        "reasons": {"type": "array", "items": {"type": "string", "maxLength": REASON_SCHEMA_MAX_CHARS}, "maxItems": 10},
        "revisionInstructions": {"type": "string", "maxLength": 1500},
    },
}


@dataclass
class ReviewResult:
    verdict: str
    valid: bool
    reason: str | None
    criteria_met: dict[str, bool]
    reasons: list[str]
    revision_instructions: str | None
    claude: ClaudeResult


def build_review_prompt(mission: Mapping[str, Any], diff_text: str) -> str:
    diff = diff_text
    if len(diff) > MAX_DIFF_CHARS:
        omitted = len(diff) - MAX_DIFF_CHARS
        diff = diff[:MAX_DIFF_CHARS] + f"\n[diff truncado: {omitted} caracteres omitidos]\n"
    lines = [
        "Você é o revisor independente de UMA missão do Pipe. Você não viu a transcrição do "
        "worker: julgue apenas o diff abaixo, lendo o repositório se precisar (só leitura).",
        "",
        f"## Missão {mission['missionId']} v{mission['version']} — {mission['title']}",
        f"Intenção: {mission['intent']}",
        f"Problema: {mission['problem']}",
        "",
        "## Critérios de sucesso",
    ]
    for criterion in mission["successCriteria"]:
        line = f"- {criterion['id']} ({criterion['kind']}): {criterion['text']}"
        if criterion["kind"] == "check":
            line += f" — comando: `{criterion['command']}`"
        elif criterion["kind"] == "artifact":
            line += f" — artefato: `{criterion['path']}`"
        else:
            line += f" — pergunta: {criterion['question']}"
        lines.append(line)
    lines += ["", "## Não-objetivos"]
    lines += [f"- {item}" for item in mission["nonGoals"]] or ["- (nenhum declarado)"]
    lines += ["", "## Write set"]
    lines += [f"- {item}" for item in mission["workspace"]["writeSet"]]
    lines += [
        "",
        "## Diff (base → estado atual do worktree)",
        "```diff",
        diff.rstrip("\n"),
        "```",
        "",
        "## Instruções",
        "Julgue SOMENTE contra os critérios e os não-objetivos acima. Para cada critério, "
        f"diga se está satisfeito e cite a evidência no diff ou no repositório (máx. {EVIDENCE_PROMPT_CHARS} chars).",
        "- `satisfied`: todos os critérios estão verdadeiros e nada viola um não-objetivo.",
        "- `needs_revision`: falta algo dentro da intenção; preencha `revisionInstructions` "
        "com o que o próximo ciclo deve fazer, de forma objetiva.",
        "- `out_of_mission`: o diff faz algo fora da intenção declarada (ainda que útil).",
        "- `blocked`: não dá para julgar com o que há (diff vazio, contexto insuficiente, "
        "mudança que exige decisão humana).",
        "Não invente evidência. Responda apenas com o JSON do schema.",
    ]
    return "\n".join(lines) + "\n"


def reviewer_command(
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
        json.dumps(VERDICT_SCHEMA, separators=(",", ":")),
        "--max-turns",
        str(REVIEWER_MAX_TURNS),
        "--max-budget-usd",
        f"{budget_left:.2f}",
        "--permission-mode",
        "plan",
        "--allowedTools",
        REVIEWER_ALLOWED_TOOLS,
        *isolation_args(),
        "--model",
        model,
    ]


def run_review(
    mission: Mapping[str, Any],
    diff_text: str,
    *,
    claude_bin: str,
    cwd: str | Path,
    budget_left: float,
    model: str = DEFAULT_MODEL,
    timeout: float = DEFAULT_REVIEW_TIMEOUT_SECONDS,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    should_stop: Callable[[], bool] | None = None,
    env: Mapping[str, str] | None = None,
    on_start: Callable[[ClaudeProcess], None] | None = None,
) -> ReviewResult:
    prompt = build_review_prompt(mission, diff_text)
    command = reviewer_command(prompt, claude_bin=claude_bin, budget_left=budget_left, model=model)
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
        return _blocked(REVIEWER_RUN_FAILED, claude)
    parsed = parse_verdict(claude.structured_output, claude.result_text)
    if parsed is None:
        return _blocked(REVIEWER_OUTPUT_INVALID, claude)
    return ReviewResult(
        verdict=parsed["verdict"],
        valid=True,
        reason=None,
        criteria_met={item["id"]: item["met"] for item in parsed["criteria"]},
        reasons=parsed["reasons"],
        revision_instructions=parsed["revisionInstructions"],
        claude=claude,
    )


def parse_verdict(structured_output: Any, result_text: str | None) -> dict[str, Any] | None:
    """A normalised verdict, or ``None`` when neither source holds a valid one."""

    candidates: list[Any] = []
    if structured_output is not None:
        candidates.append(structured_output)
    if result_text:
        candidates.extend(_json_candidates(result_text))
    for candidate in candidates:
        normalized = _normalize_verdict(candidate)
        if normalized is not None:
            return normalized
    return None


def _normalize_verdict(candidate: Any) -> dict[str, Any] | None:
    if not isinstance(candidate, Mapping) or candidate.get("verdict") not in VERDICTS:
        return None
    criteria_raw = candidate.get("criteria", [])
    if not isinstance(criteria_raw, list):
        return None
    criteria = []
    for item in criteria_raw:
        if (
            not isinstance(item, Mapping)
            or not isinstance(item.get("id"), str)
            or not isinstance(item.get("met"), bool)
        ):
            return None
        criteria.append({"id": item["id"], "met": item["met"]})
    reasons_raw = candidate.get("reasons", [])
    if not isinstance(reasons_raw, list):
        return None
    reasons = [str(reason) for reason in reasons_raw if isinstance(reason, str)]
    instructions = candidate.get("revisionInstructions")
    if not isinstance(instructions, str) or not instructions.strip():
        instructions = None
    return {
        "verdict": candidate["verdict"],
        "criteria": criteria,
        "reasons": reasons,
        "revisionInstructions": instructions,
    }


def _blocked(reason: str, claude: ClaudeResult) -> ReviewResult:
    return ReviewResult(
        verdict="blocked",
        valid=False,
        reason=reason,
        criteria_met={},
        reasons=[],
        revision_instructions=None,
        claude=claude,
    )
