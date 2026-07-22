"""Module CLI called by the portable Hermes skill."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
    utc_now,
)
from pipe_venture_builder.control_plane.store import LocalControlPlaneStore

from .adapter import HermesRuntimeAdapter
from .checkpoint import HermesCheckpointStore
from .model import (
    RECORDABLE_HERMES_EVENT_KINDS,
    HermesRunContext,
    HermesRuntimeEvent,
)
from .probe import probe_hermes


CONTROLLED_REFUSAL = 8
RUNTIME_FAILURE = 9


class HermesCliError(RuntimeError):
    def __init__(self, code: str, exit_code: int) -> None:
        super().__init__(code)
        self.code = code
        self.exit_code = exit_code


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "probe":
            result = probe_hermes(args.hermes_bin)
            _emit(result)
            return 0 if result["compatible"] else CONTROLLED_REFUSAL
        if args.command == "begin":
            result = _begin(args)
        elif args.command == "resume":
            result = _resume(args)
        elif args.command == "event":
            result = _event(args)
        elif args.command == "status":
            result = _status(args)
        else:  # pragma: no cover - argparse requires a known subcommand.
            raise HermesCliError("COMMAND_REQUIRED", CONTROLLED_REFUSAL)
        _emit(result)
        return 0
    except HermesCliError as exc:
        _emit_error(exc.code)
        return exc.exit_code
    except (ControlPlaneContractError, ControlPlaneStateError):
        _emit_error("HERMES_HANDOFF_REJECTED")
        return CONTROLLED_REFUSAL
    except OSError:
        _emit_error("HERMES_LOCAL_STATE_FAILED")
        return RUNTIME_FAILURE
    except Exception:
        _emit_error("HERMES_INTERNAL_ERROR")
        return RUNTIME_FAILURE


def _begin(args: argparse.Namespace) -> dict[str, Any]:
    plan = _load_json(args.plan, "PLAN")
    session_id = _session_id(args.session_id)
    context = HermesRunContext.build(
        product_id=args.product_id,
        linear_ticket_id=args.ticket_id,
        workflow=args.workflow,
        product_root=args.product_root,
        artifact_refs=args.artifact,
        plan=plan,
    )
    with LocalControlPlaneStore(args.store) as control_plane:
        adapter = HermesRuntimeAdapter(
            control_plane, HermesCheckpointStore(args.checkpoint_dir)
        )
        return adapter.begin(
            plan=plan,
            context=context,
            session_id=session_id,
            external_event_id=args.event_id,
            occurred_at=args.at or utc_now(),
        )


def _resume(args: argparse.Namespace) -> dict[str, Any]:
    with LocalControlPlaneStore(args.store) as control_plane:
        adapter = HermesRuntimeAdapter(
            control_plane, HermesCheckpointStore(args.checkpoint_dir)
        )
        return adapter.resume(
            run_id=args.run_id,
            session_id=_session_id(args.session_id),
            external_event_id=args.event_id,
            occurred_at=args.at or utc_now(),
        )


def _event(args: argparse.Namespace) -> dict[str, Any]:
    approval = _load_json(args.approval, "APPROVAL") if args.approval else None
    plan = _load_json(args.plan, "PLAN") if args.plan else None
    event = HermesRuntimeEvent.build(
        external_event_id=args.event_id,
        kind=args.kind,
        session_id=_session_id(args.session_id),
        occurred_at=args.at or utc_now(),
        action_id=args.action_id,
        approval_id=args.approval_id,
        tool_name=args.tool_name,
        result_ref=args.result_ref,
        payload_fingerprint=args.payload_fingerprint,
    )
    with LocalControlPlaneStore(args.store) as control_plane:
        adapter = HermesRuntimeAdapter(
            control_plane, HermesCheckpointStore(args.checkpoint_dir)
        )
        if approval is not None:
            if plan is None:
                raise HermesCliError("PLAN_REQUIRED_FOR_APPROVAL", CONTROLLED_REFUSAL)
            return adapter.grant_approval(
                run_id=args.run_id, event=event, approval=approval, plan=plan
            )
        return adapter.record_event(args.run_id, event)


def _status(args: argparse.Namespace) -> dict[str, Any]:
    with LocalControlPlaneStore(args.store) as control_plane:
        adapter = HermesRuntimeAdapter(
            control_plane, HermesCheckpointStore(args.checkpoint_dir)
        )
        result = adapter.status(args.run_id)
        result["auditChainValid"] = control_plane.verify_audit_chain(args.run_id)
        return result


def _load_json(path: str, kind: str) -> Any:
    source = Path(path).expanduser()
    if source.is_symlink():
        raise HermesCliError(f"{kind}_UNSAFE", CONTROLLED_REFUSAL)
    try:
        with source.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise HermesCliError(f"{kind}_UNAVAILABLE", RUNTIME_FAILURE) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HermesCliError(f"{kind}_INVALID_JSON", CONTROLLED_REFUSAL) from exc


def _session_id(argument: str | None) -> str:
    value = argument or os.environ.get("HERMES_SESSION_ID")
    if not value:
        raise HermesCliError("HERMES_SESSION_ID_REQUIRED", CONTROLLED_REFUSAL)
    return value


def _emit(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _emit_error(code: str) -> None:
    print(
        json.dumps(
            {"ok": False, "error": {"code": code}},
            sort_keys=True,
            separators=(",", ":"),
        ),
        file=sys.stderr,
    )


def _add_state_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--store", required=True)
    parser.add_argument("--checkpoint-dir", required=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m pipe_venture_builder.adapters.hermes",
        description="Supervised Hermes runtime handoff for Pipe runs.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    probe = commands.add_parser("probe", help="check Hermes 0.17+ without credentials")
    probe.add_argument("--hermes-bin", default="hermes")

    begin = commands.add_parser("begin", help="bind the active Hermes session")
    _add_state_args(begin)
    begin.add_argument("--plan", required=True)
    begin.add_argument("--product-root", required=True)
    begin.add_argument("--product-id", required=True)
    begin.add_argument("--ticket-id", required=True)
    begin.add_argument(
        "--workflow",
        required=True,
        choices=("idea", "adopt", "reconcile", "review", "check"),
    )
    begin.add_argument("--artifact", action="append", required=True)
    begin.add_argument("--session-id")
    begin.add_argument("--event-id", required=True)
    begin.add_argument("--at")

    resume = commands.add_parser("resume", help="resume a durable Pipe handoff")
    _add_state_args(resume)
    resume.add_argument("--run-id", required=True)
    resume.add_argument("--session-id")
    resume.add_argument("--event-id", required=True)
    resume.add_argument("--at")

    event = commands.add_parser("event", help="record one normalized runtime event")
    _add_state_args(event)
    event.add_argument("--run-id", required=True)
    event.add_argument(
        "--kind",
        required=True,
        choices=tuple(sorted(RECORDABLE_HERMES_EVENT_KINDS | {"approval.granted"})),
    )
    event.add_argument("--event-id", required=True)
    event.add_argument("--session-id")
    event.add_argument("--action-id")
    event.add_argument("--approval-id")
    event.add_argument("--approval")
    event.add_argument("--plan")
    event.add_argument("--tool-name")
    event.add_argument("--result-ref")
    event.add_argument("--payload-fingerprint")
    event.add_argument("--at")

    status = commands.add_parser("status", help="show a redacted durable checkpoint")
    _add_state_args(status)
    status.add_argument("--run-id", required=True)
    return parser
