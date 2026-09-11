"""``pipe mission`` subcommands. Offline by construction: no network, no secret.

Handlers return the same payload shape as the main CLI and raise ``PipeError``
with fixed messages. Contract and state failures never echo the input.
"""

from __future__ import annotations

import argparse
from typing import Any, Callable

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
)
from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import INPUT_UNAVAILABLE, READINESS_BLOCKED
from pipe_venture_builder.validation import load_json_document

from .contract import build_mission
from .status import build_status, render_status_text
from .store import MissionStore


CONTRACT_VIOLATION = "MISSION_CONTRACT_VIOLATION"
STATE_CONFLICT = "MISSION_STATE_CONFLICT"
NOT_FOUND = "MISSION_NOT_FOUND"
_NOT_FOUND_MESSAGES = frozenset(
    {"mission is not registered", "run is not registered", "decision is not registered"}
)


def register_mission_commands(commands: argparse._SubParsersAction) -> None:
    mission_parser = commands.add_parser(
        "mission",
        help="Create and steer durable missions (Mission Loop). Offline; no worker here.",
    )
    subcommands = mission_parser.add_subparsers(dest="mission_command", required=True)

    create = _subcommand(
        subcommands, "create", "Validate, fingerprint, and persist a Mission JSON file.", _handle_create
    )
    create.add_argument("source", help="Mission JSON file (a draft without ids is accepted).")
    create.add_argument("--at", help="Creation timestamp (RFC 3339). Defaults to now.")

    show = _subcommand(subcommands, "show", "Print the stored Mission document.", _handle_show)
    show.add_argument("mission_id")

    status = _subcommand(
        subcommands, "status", "Where we are, why, and what depends on you.", _handle_status
    )
    status.add_argument("mission_id")

    for verb, help_text in (
        ("activate", "draft -> active."),
        ("pause", "active -> paused. Nothing new is dispatched while paused."),
        ("resume", "paused|blocked -> active. Blocked needs its decisions resolved."),
        ("cancel", "active|paused -> cancelled."),
        ("complete", "active -> completed, only with evidence for every criterion."),
    ):
        parser = _subcommand(subcommands, verb, help_text, _transition_handler(verb))
        parser.add_argument("mission_id")
        parser.add_argument("--at", help="Transition timestamp (RFC 3339). Defaults to now.")

    decisions = _subcommand(
        subcommands, "decisions", "List the mission's human decisions.", _handle_decisions
    )
    decisions.add_argument("mission_id")
    decisions.add_argument("--pending", action="store_true", help="Only pending decisions.")

    decide = _subcommand(
        subcommands, "decide", "Resolve a pending decision as a named human.", _handle_decide
    )
    decide.add_argument("decision_id")
    decide.add_argument("--option", required=True, help="One of the decision's options.")
    decide.add_argument(
        "--by",
        required=True,
        dest="decided_by",
        help="Human source ref: human:chat:<who>, human:linear:<ref>, or human:cli:<who>.",
    )
    decide.add_argument("--at", help="Decision timestamp (RFC 3339). Defaults to now.")


def _subcommand(
    subcommands: argparse._SubParsersAction,
    name: str,
    help_text: str,
    handler: Callable[[argparse.Namespace], dict[str, Any]],
) -> argparse.ArgumentParser:
    parser = subcommands.add_parser(name, help=help_text)
    parser.add_argument(
        "--store",
        help="SQLite path. Defaults to ~/.pipe/mission/mission.sqlite3.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.set_defaults(handler=_guarded(handler))
    return parser


def _guarded(
    handler: Callable[[argparse.Namespace], dict[str, Any]],
) -> Callable[[argparse.Namespace], dict[str, Any]]:
    def run(args: argparse.Namespace) -> dict[str, Any]:
        try:
            return handler(args)
        except ControlPlaneContractError as exc:
            raise PipeError(
                code=CONTRACT_VIOLATION,
                message="The request violates the Mission contract.",
                exit_code=READINESS_BLOCKED,
                details=[{"path": "-", "message": str(exc), "rule": "mission-contract"}],
            ) from exc
        except ControlPlaneStateError as exc:
            if str(exc) in _NOT_FOUND_MESSAGES:
                raise PipeError(
                    code=NOT_FOUND,
                    message="The requested mission record does not exist in this store.",
                    exit_code=INPUT_UNAVAILABLE,
                    details=[{"path": "-", "message": str(exc), "rule": "mission-store"}],
                ) from exc
            raise PipeError(
                code=STATE_CONFLICT,
                message="Durable mission state refuses this transition.",
                exit_code=READINESS_BLOCKED,
                details=[{"path": "-", "message": str(exc), "rule": "mission-state"}],
            ) from exc

    return run


def _open_store(args: argparse.Namespace) -> MissionStore:
    return MissionStore(args.store) if args.store else MissionStore()


def _handle_create(args: argparse.Namespace) -> dict[str, Any]:
    draft = load_json_document(args.source, kind="mission")
    mission = build_mission(draft, created_at=args.at)
    with _open_store(args) as store:
        mission_id = store.create(mission, at=args.at)
        stored = store.get(mission_id)
    return {
        "ok": True,
        "command": "mission.create",
        "missionId": mission_id,
        "status": stored["status"],
        "fingerprint": stored["fingerprint"],
        "criteria": len(stored["successCriteria"]),
        "message": (
            f"Mission {mission_id} stored as {stored['status']} "
            f"({len(stored['successCriteria'])} criteria). Activate it to start."
        ),
    }


def _handle_show(args: argparse.Namespace) -> dict[str, Any]:
    with _open_store(args) as store:
        mission = store.get(args.mission_id)
    return {
        "ok": True,
        "command": "mission.show",
        "missionId": mission["missionId"],
        "mission": mission,
        "message": _render_document(mission),
    }


def _handle_status(args: argparse.Namespace) -> dict[str, Any]:
    with _open_store(args) as store:
        status = build_status(store, args.mission_id)
    return {
        "ok": True,
        "command": "mission.status",
        "missionId": status["missionId"],
        "status": status,
        "message": render_status_text(status),
    }


def _transition_handler(verb: str) -> Callable[[argparse.Namespace], dict[str, Any]]:
    def handle(args: argparse.Namespace) -> dict[str, Any]:
        with _open_store(args) as store:
            getattr(store, verb)(args.mission_id, at=args.at)
            document = store.get(args.mission_id)
            last = store.last_event(args.mission_id)
        return {
            "ok": True,
            "command": f"mission.{verb}",
            "missionId": document["missionId"],
            "status": document["status"],
            "lastEvent": last["eventType"] if last else None,
            "message": f"Mission {document['missionId']} is now {document['status']}.",
        }

    return handle


def _handle_decisions(args: argparse.Namespace) -> dict[str, Any]:
    with _open_store(args) as store:
        decisions = store.list_decisions(args.mission_id, pending_only=args.pending)
    if not decisions:
        message = "No pending decisions." if args.pending else "No decisions recorded."
    else:
        lines = []
        for decision in decisions:
            lines.append(
                f"{decision['decisionId']} [{decision['kind']}] {decision['status']}; "
                f"blocks {decision['blockedScope']}; options: {', '.join(decision['options'])}; "
                f"safe default: {decision['safeDefault']}; deadline: {decision['deadline'] or '-'}"
            )
        message = "\n".join(lines)
    return {
        "ok": True,
        "command": "mission.decisions",
        "missionId": args.mission_id,
        "pendingOnly": bool(args.pending),
        "decisions": decisions,
        "message": message,
    }


def _handle_decide(args: argparse.Namespace) -> dict[str, Any]:
    with _open_store(args) as store:
        decision = store.resolve_decision(
            args.decision_id, option=args.option, decided_by=args.decided_by, at=args.at
        )
    return {
        "ok": True,
        "command": "mission.decide",
        "decisionId": decision["decisionId"],
        "missionId": decision["missionId"],
        "decision": decision,
        "message": (
            f"Decision {decision['decisionId']} resolved with {decision['decidedOption']} "
            f"by {decision['decidedBy']}."
        ),
    }


def _render_document(mission: dict[str, Any]) -> str:
    criteria = "\n".join(
        f"  - {item['id']} [{item['kind']}] {item['text']}" for item in mission["successCriteria"]
    )
    return (
        f"{mission['missionId']} v{mission['version']} {mission['status']}\n"
        f"title: {mission['title']}\n"
        f"workspace: {mission['workspace']['repo']} @ {mission['workspace']['baseRef']}\n"
        f"writeSet: {', '.join(mission['workspace']['writeSet'])}\n"
        f"delivery: {mission['delivery']['kind']}"
        f" (requireChecks={str(mission['delivery']['requireChecks']).lower()})\n"
        f"criteria:\n{criteria}\n"
        f"fingerprint: {mission['fingerprint']}"
    )
