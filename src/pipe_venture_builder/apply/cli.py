"""Fixture-only supervised apply command surface for PIP-712."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from pipe_venture_builder.control_plane import (
    ControlPlaneContractError,
    ControlPlaneStateError,
    LocalControlPlaneStore,
    build_approval_record,
)
from pipe_venture_builder.control_plane.model import utc_now

from .fixture import FixtureApplyAdapter
from .service import SupervisedApplyService


CONTROLLED_REFUSAL = 8
CONTROL_PLANE_FAILURE = 9
RUN_INTERRUPTED = 10


class ApplyCliError(RuntimeError):
    def __init__(self, code: str, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "approve":
            output = _approve(args)
            _emit(output)
            return 0
        if args.command == "execute":
            output = _execute(args)
            _emit(output)
            return {
                "verified": 0,
                "skipped": 0,
                "blocked": CONTROLLED_REFUSAL,
                "failed": CONTROL_PLANE_FAILURE,
                "interrupted": RUN_INTERRUPTED,
            }[output["status"]]
        if args.command == "audit":
            output = _audit(args)
            _emit(output)
            return 0 if output["auditChainValid"] else CONTROL_PLANE_FAILURE
        parser.error("a command is required")
    except ApplyCliError as exc:
        _emit_error(exc.code, exc.message)
        return exc.exit_code
    except (ControlPlaneContractError, ControlPlaneStateError, OSError) as exc:
        _emit_error("CONTROL_PLANE_REJECTED", _safe_failure_message(exc))
        return CONTROL_PLANE_FAILURE
    return 2


def _approve(args: argparse.Namespace) -> dict[str, Any]:
    plan = _load_json(args.plan, "plan")
    decided_at = args.at or utc_now()
    approval = build_approval_record(
        plan,
        args.action,
        actor_id=args.actor,
        decided_at=decided_at,
        expires_at=args.expires_at,
        source_ref=args.source_ref,
        decision=args.decision,
    )
    output_path = Path(args.output).expanduser()
    if output_path.exists() or output_path.is_symlink():
        raise ApplyCliError(
            "APPROVAL_OUTPUT_EXISTS",
            "The approval output already exists; no file was overwritten.",
            CONTROLLED_REFUSAL,
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.parent.is_symlink():
        raise ApplyCliError(
            "APPROVAL_OUTPUT_UNSAFE",
            "The approval output directory cannot be a symlink.",
            CONTROLLED_REFUSAL,
        )
    with LocalControlPlaneStore(args.store) as store:
        run_id = store.register_plan(plan, at=decided_at)
        store.record_approval(approval, at=decided_at)
        with output_path.open("x", encoding="utf-8") as handle:
            json.dump(approval, handle, sort_keys=True, indent=2)
            handle.write("\n")
    return {
        "status": "recorded",
        "runId": run_id,
        "approvalId": approval["approvalId"],
        "actionId": approval["actionId"],
        "decision": approval["decision"],
        "expiresAt": approval["expiresAt"],
        "output": str(output_path),
    }


def _execute(args: argparse.Namespace) -> dict[str, Any]:
    plan = _load_json(args.plan, "plan")
    approval = _load_json(args.approval, "approval")
    fixture = _load_json(args.fixture, "fixture")
    adapter = FixtureApplyAdapter(fixture)
    with LocalControlPlaneStore(args.store) as store:
        return SupervisedApplyService(store).execute_action(
            plan,
            args.action,
            approval=approval,
            adapter=adapter,
            current_source_fingerprint=args.source_fingerprint,
            at=args.at or utc_now(),
            pause_after_apply=args.pause_after_apply,
        )


def _audit(args: argparse.Namespace) -> dict[str, Any]:
    with LocalControlPlaneStore(args.store) as store:
        run = store.get_run(args.run_id)
        events = store.list_events(args.run_id)
        event_chain_valid = store.verify_audit_chain(args.run_id)
        checkpoints_valid = store.verify_checkpoints(args.run_id)
        return {
            "runId": args.run_id,
            "planId": run["plan_id"],
            "status": run["status"],
            "eventCount": len(events),
            "lastEventType": events[-1]["eventType"] if events else None,
            "eventChainValid": event_chain_valid,
            "checkpointsValid": checkpoints_valid,
            "auditChainValid": event_chain_valid and checkpoints_valid,
        }


def _load_json(path: str, kind: str) -> Any:
    source = Path(path).expanduser()
    if source.is_symlink():
        raise ApplyCliError(
            f"{kind.upper()}_UNSAFE",
            f"The {kind} input cannot be a symlink.",
            CONTROLLED_REFUSAL,
        )
    try:
        with source.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ApplyCliError(
            f"{kind.upper()}_UNAVAILABLE",
            f"The {kind} input is unavailable.",
            CONTROL_PLANE_FAILURE,
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApplyCliError(
            f"{kind.upper()}_INVALID_JSON",
            f"The {kind} input is not valid UTF-8 JSON.",
            CONTROL_PLANE_FAILURE,
        ) from exc


def _emit(value: MappingLike) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _emit_error(code: str, message: str) -> None:
    print(
        json.dumps(
            {"ok": False, "error": {"code": code, "message": message}},
            sort_keys=True,
            separators=(",", ":"),
        ),
        file=sys.stderr,
    )


def _safe_failure_message(exc: Exception) -> str:
    if isinstance(exc, ControlPlaneContractError):
        return "The input does not satisfy the control-plane contract."
    if isinstance(exc, ControlPlaneStateError):
        return "The durable control-plane state conflicts with this operation."
    return "The local control-plane operation failed."


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m pipe_venture_builder.apply",
        description="Supervised fixture-only reconciliation apply flow.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    approve = commands.add_parser("approve", help="record one human decision")
    approve.add_argument("--store", required=True)
    approve.add_argument("--plan", required=True)
    approve.add_argument("--action", required=True)
    approve.add_argument("--actor", required=True)
    approve.add_argument("--source-ref", required=True)
    approve.add_argument("--expires-at", required=True)
    approve.add_argument("--at")
    approve.add_argument(
        "--decision", choices=("approved", "denied", "revoked"), default="approved"
    )
    approve.add_argument("--output", required=True)

    execute = commands.add_parser("execute", help="apply one approved fixture action")
    execute.add_argument("--store", required=True)
    execute.add_argument("--plan", required=True)
    execute.add_argument("--approval", required=True)
    execute.add_argument("--fixture", required=True)
    execute.add_argument("--action", required=True)
    execute.add_argument("--source-fingerprint", required=True)
    execute.add_argument("--at")
    execute.add_argument("--pause-after-apply", action="store_true")

    audit = commands.add_parser("audit", help="verify one local run audit chain")
    audit.add_argument("--store", required=True)
    audit.add_argument("--run-id", required=True)
    return parser


MappingLike = dict[str, Any]
