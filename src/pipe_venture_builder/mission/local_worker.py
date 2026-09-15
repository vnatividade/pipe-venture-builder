"""One-shot local-executor turn (PIP-911 onda 2).

A mechanical wave's whole unit of work, expressed as ONE tool call to a
local OpenAI-compatible endpoint (see ``local_adapter``), reduced to the same
output shape ``worker.extract_worker_output`` already produces from a
headless Claude Code worker — nothing downstream needs to know which
executor produced a cycle's result.

Writes only inside the given worktree, and only paths inside the mission's
own write set (``verify.outside_write_set``, the same rule the supervisor
checks afterwards) — a model asked to report ``filesChanged`` cannot use
this tool to reach outside it either.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from pipe_venture_builder.control_plane.model import ControlPlaneContractError, fingerprint

from .contract import relative_path
from .local_adapter import LocalEndpointError, Transport, request_tool_call
from .verify import outside_write_set
from .worker import compile_brief


SUBMIT_TOOL_NAME = "submit_mission_result"
DEFAULT_TIMEOUT_SECONDS = 30.0

SUBMIT_TOOL_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": SUBMIT_TOOL_NAME,
        "description": (
            "Report this cycle's outcome: whether the mission is done, a summary, "
            "every file written (path and full new content), a self-assessment per "
            "success criterion, and any blockers."
        ),
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "required": ["done", "summary", "filesChanged", "criteriaSelfAssessment", "blockers"],
            "properties": {
                "done": {"type": "boolean"},
                "summary": {"type": "string"},
                "filesChanged": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["path", "content"],
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                        },
                    },
                },
                "criteriaSelfAssessment": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["id", "met"],
                        "properties": {
                            "id": {"type": "string"},
                            "met": {"type": "boolean"},
                            "note": {"type": "string"},
                        },
                    },
                },
                "blockers": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}


@dataclass
class LocalWorkerResult:
    """Duck-type compatible with the fields of ``worker.WorkerResult`` the
    supervisor actually reads, plus the envelope/content split PIP-911 needs
    kept apart (see ``local_adapter.ToolCallEnvelope``)."""

    status: str  # collected | failed
    reason: str | None
    session_id: str | None
    cost_usd: float
    num_turns: int
    subtype: str | None
    permission_denials: int
    denied_tools: list[str]
    result_text: str | None
    result_fingerprint: str | None
    output: dict[str, Any] | None
    envelope_present: bool
    content_recovered: bool
    tool_call_source: str | None
    denied_calls: list[str] = field(default_factory=list)


def run_local_worker(
    mission: Mapping[str, Any],
    *,
    worktree: str | Path,
    base_url: str,
    model: str,
    cycle: int = 1,
    revision_instructions: str | None = None,
    transport: Transport | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> LocalWorkerResult:
    """Compile the same brief a Claude Code worker would get, send it as one
    user turn with the ``submit_mission_result`` tool, and apply whatever
    file writes the recovered call asked for. A run that never recovers a
    call at all (envelope absent AND no native XML) fails as
    ``local_no_tool_call``; one that calls the wrong tool, or one whose
    arguments do not match the schema, fails too — neither is a verification
    failure, so neither counts toward the two-strikes downgrade
    (``supervisor._Cycle._resolve_dispatch_executor`` only counts a cycle
    that actually reached ``verify_criteria``)."""

    brief = compile_brief(mission, cycle, revision_instructions)
    messages = [{"role": "user", "content": brief}]
    try:
        envelope = request_tool_call(
            base_url, model=model, messages=messages, tools=[SUBMIT_TOOL_SCHEMA],
            transport=transport, timeout=timeout,
        )
    except LocalEndpointError:
        return _failed("local_endpoint_unavailable", envelope_present=False, content_recovered=False, source=None)

    call = next((item for item in envelope.calls if item.name == SUBMIT_TOOL_NAME), None)
    if call is None:
        reason = "local_no_tool_call" if not envelope.calls else "local_unexpected_tool"
        return _failed(
            reason, envelope_present=envelope.envelope_present,
            content_recovered=envelope.content_recovered, source=envelope.source,
        )

    try:
        output = _apply_result(mission, worktree, call.arguments)
    except ControlPlaneContractError:
        return _failed(
            "local_arguments_invalid", envelope_present=envelope.envelope_present,
            content_recovered=envelope.content_recovered, source=envelope.source,
        )

    return LocalWorkerResult(
        status="collected",
        reason=None,
        session_id=None,
        cost_usd=0.0,
        num_turns=1,
        subtype="success",
        permission_denials=0,
        denied_tools=[],
        result_text=None,
        result_fingerprint=fingerprint(output),
        output=output,
        envelope_present=envelope.envelope_present,
        content_recovered=envelope.content_recovered,
        tool_call_source=envelope.source,
    )


def _failed(
    reason: str, *, envelope_present: bool, content_recovered: bool, source: str | None
) -> LocalWorkerResult:
    return LocalWorkerResult(
        status="failed",
        reason=reason,
        session_id=None,
        cost_usd=0.0,
        num_turns=1,
        subtype=None,
        permission_denials=0,
        denied_tools=[],
        result_text=None,
        result_fingerprint=None,
        output=None,
        envelope_present=envelope_present,
        content_recovered=content_recovered,
        tool_call_source=source,
    )


def _apply_result(
    mission: Mapping[str, Any], worktree: str | Path, arguments: Mapping[str, Any]
) -> dict[str, Any]:
    if not isinstance(arguments, Mapping):
        raise ControlPlaneContractError("local tool call arguments must be a mapping")
    done = arguments.get("done")
    if not isinstance(done, bool):
        raise ControlPlaneContractError("local tool call done must be boolean")
    summary = arguments.get("summary")
    summary = summary if isinstance(summary, str) else ""
    files = arguments.get("filesChanged")
    if not isinstance(files, list):
        raise ControlPlaneContractError("local tool call filesChanged must be a list")
    root = Path(worktree)
    root_real = root.resolve()
    write_set = mission["workspace"]["writeSet"]
    # Duas passadas (revisão do PR #207): TUDO é validado antes de qualquer
    # escrita. Escrever um a um e falhar no terceiro deixava os dois primeiros
    # no worktree — sujeira que nenhum run assume, herdada pelo ciclo seguinte.
    planned: list[tuple[str, Path, str]] = []
    for entry in files:
        if not isinstance(entry, Mapping):
            raise ControlPlaneContractError("local tool call file entry must be a mapping")
        path = entry.get("path")
        content = entry.get("content")
        if not isinstance(path, str) or not isinstance(content, str):
            raise ControlPlaneContractError("local tool call file entry is invalid")
        relative = relative_path(path, what="local tool call file path")
        if outside_write_set([relative], write_set):
            raise ControlPlaneContractError("local tool call file path is outside the write set")
        target = root / relative
        # O texto do caminho não basta: um link simbólico sob um prefixo do
        # write set (`docs -> /tmp/fora`) levava a escrita para fora do
        # worktree — verificado. O executor local não tem a parede do
        # `--worktree` do CLI; a contenção é esta checagem, pelo caminho REAL.
        if not target.resolve().is_relative_to(root_real):
            raise ControlPlaneContractError("local tool call file path escapes the worktree")
        planned.append((relative, target, content))
    paths: list[str] = []
    for relative, target, content in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.resolve().is_relative_to(root_real):
            raise ControlPlaneContractError("local tool call file path escapes the worktree")
        target.write_text(content, encoding="utf-8")
        paths.append(relative)
    criteria = arguments.get("criteriaSelfAssessment")
    criteria = criteria if isinstance(criteria, list) else []
    blockers_raw = arguments.get("blockers")
    blockers = [item for item in blockers_raw if isinstance(item, str)] if isinstance(blockers_raw, list) else []
    return {
        "done": done,
        "summary": summary,
        "filesChanged": paths,
        "criteriaSelfAssessment": criteria,
        "blockers": blockers,
    }
