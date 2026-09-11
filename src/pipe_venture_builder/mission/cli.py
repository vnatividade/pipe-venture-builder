"""``pipe mission`` subcommands.

The store verbs are offline. ``supervise``/``run-once`` run the Mission Loop
supervisor, which executes ``claude`` and ``gh`` (injectable with
``--claude-bin``/``--gh-bin``); nothing here reads or passes a secret.

Handlers return the same payload shape as the main CLI and raise ``PipeError``
with fixed messages. Contract and state failures never echo the input.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
)
from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.exit_codes import INPUT_UNAVAILABLE, READINESS_BLOCKED
from pipe_venture_builder.validation import load_json_document

from .contract import build_mission
from .status import build_status, default_mission_home, render_status_text
from .store import MissionStore
from .supervisor import (
    Step,
    SupervisorRefusal,
    claim_supervisor,
    live_supervisor_pid,
    reconcile,
    run_once,
    supervise,
    supervisor_log_path,
    supervisor_pid_path,
)
from .worker import DEFAULT_MODEL, DEFAULT_POLL_SECONDS


CONTRACT_VIOLATION = "MISSION_CONTRACT_VIOLATION"
STATE_CONFLICT = "MISSION_STATE_CONFLICT"
NOT_FOUND = "MISSION_NOT_FOUND"
SUPERVISOR_REFUSED = "MISSION_SUPERVISOR_REFUSED"
SUPERVISOR_ERROR = "MISSION_SUPERVISOR_ERROR"
_NOT_FOUND_MESSAGES = frozenset(
    {"mission is not registered", "run is not registered", "decision is not registered"}
)


def register_mission_commands(commands: argparse._SubParsersAction) -> None:
    mission_parser = commands.add_parser(
        "mission",
        help="Create, steer and supervise durable missions (Mission Loop).",
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
    _home_option(status)

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

    supervise_parser = _subcommand(
        subcommands,
        "supervise",
        "Run the supervisor until the mission is terminal, paused, blocked or waits on a decision.",
        _handle_supervise,
    )
    supervise_parser.add_argument("mission_id")
    supervise_parser.add_argument(
        "--detach",
        action="store_true",
        help="Start the supervisor in its own session (survives the chat); pid and log in --home.",
    )
    _supervisor_options(supervise_parser)

    once = _subcommand(
        subcommands, "run-once", "Run exactly one supervisor cycle and print the next state.", _handle_run_once
    )
    once.add_argument("mission_id")
    _supervisor_options(once)

    reconcile_parser = _subcommand(
        subcommands,
        "reconcile",
        "Mark runs left running by a dead supervisor as unknown (opens a decision).",
        _handle_reconcile,
    )
    reconcile_parser.add_argument("mission_id")
    _home_option(reconcile_parser)


def _home_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--home",
        help="Mission home root (pid, log, worktree). Defaults to ~/.pipe/mission.",
    )


def _positive_seconds(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number of seconds") from exc
    if not seconds > 0:
        raise argparse.ArgumentTypeError("must be positive")
    return seconds


def _supervisor_options(parser: argparse.ArgumentParser) -> None:
    _home_option(parser)
    parser.add_argument("--claude-bin", default="claude", help="Claude Code executable (default: claude).")
    parser.add_argument("--gh-bin", default="gh", help="GitHub CLI executable (default: gh).")
    parser.add_argument(
        "--poll-seconds",
        type=_positive_seconds,
        default=DEFAULT_POLL_SECONDS,
        help="How often the store is read while a worker runs (pause/cancel latency).",
    )
    parser.add_argument("--worker-model", default=DEFAULT_MODEL, help="--model for the worker.")
    parser.add_argument("--reviewer-model", default=DEFAULT_MODEL, help="--model for the reviewer.")


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
        except SupervisorRefusal as exc:
            raise PipeError(
                code=SUPERVISOR_REFUSED,
                message="The supervisor refuses to act on this mission.",
                exit_code=READINESS_BLOCKED,
                details=[{"path": "-", "message": str(exc), "rule": "mission-supervisor"}],
            ) from exc
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
        except (RuntimeError, OSError) as exc:
            # git/gh/claude failures carry fixed messages (command + exit code).
            raise PipeError(
                code=SUPERVISOR_ERROR,
                message="The supervisor stopped on a git, gh or process error.",
                exit_code=READINESS_BLOCKED,
                details=[{"path": "-", "message": type(exc).__name__ + ": " + str(exc)[:200],
                          "rule": "mission-supervisor"}],
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


def _home(args: argparse.Namespace) -> Path:
    return Path(args.home).expanduser().resolve() if args.home else default_mission_home()


def _handle_status(args: argparse.Namespace) -> dict[str, Any]:
    with _open_store(args) as store:
        status = build_status(store, args.mission_id, home=_home(args))
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


# -- supervisor ----------------------------------------------------------------


def _supervisor_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "claude_bin": args.claude_bin,
        "gh_bin": args.gh_bin,
        "home": _home(args),
        "worker_model": args.worker_model,
        "reviewer_model": args.reviewer_model,
        "poll_seconds": args.poll_seconds,
    }


def _step_payload(command: str, mission_id: str, step: Step) -> dict[str, Any]:
    return {
        "ok": True,
        "command": command,
        "missionId": mission_id,
        "status": step.status,
        "reason": step.reason,
        "cycle": step.cycle,
        "message": f"Mission {mission_id} is {step.status} ({step.reason}, cycle {step.cycle}).",
    }


def _handle_supervise(args: argparse.Namespace) -> dict[str, Any]:
    if args.detach:
        return _detach_supervisor(args)
    with _open_store(args) as store:
        step = supervise(args.mission_id, store=store, **_supervisor_kwargs(args))
    return _step_payload("mission.supervise", args.mission_id, step)


def _handle_run_once(args: argparse.Namespace) -> dict[str, Any]:
    home = _home(args)
    with _open_store(args) as store:
        store.get(args.mission_id)
        claim_supervisor(home, args.mission_id)
        step = run_once(args.mission_id, store=store, **_supervisor_kwargs(args))
    return _step_payload("mission.run-once", args.mission_id, step)


def _handle_reconcile(args: argparse.Namespace) -> dict[str, Any]:
    with _open_store(args) as store:
        reconciled = reconcile(args.mission_id, store=store, home=_home(args))
        status = store.get(args.mission_id)["status"]
    return {
        "ok": True,
        "command": "mission.reconcile",
        "missionId": args.mission_id,
        "reconciled": reconciled,
        "status": status,
        "message": (
            f"{len(reconciled)} orphan run(s) marked unknown; mission is {status}."
            if reconciled
            else f"No orphan runs; mission is {status}."
        ),
    }


def _detach_supervisor(args: argparse.Namespace) -> dict[str, Any]:
    """``supervise`` without ``--detach`` in its own session; stdout/stderr to the log."""

    home = _home(args)
    store_path = str(Path(args.store).expanduser().resolve()) if args.store else None
    with _open_store(args) as store:
        document = store.get(args.mission_id)
        if not store.verify_chain(args.mission_id):
            raise SupervisorRefusal("mission audit chain is invalid; the supervisor refuses to continue")
        if document["status"] != "active":
            raise ControlPlaneStateError("only an active mission can be supervised")
    if live_supervisor_pid(home, args.mission_id) is not None:
        raise SupervisorRefusal("another supervisor is alive for this mission")

    command = [
        sys.executable, "-m", "pipe_venture_builder", "mission", "supervise", args.mission_id,
        "--home", str(home),
        "--claude-bin", _executable(args.claude_bin),
        "--gh-bin", _executable(args.gh_bin),
        "--poll-seconds", repr(args.poll_seconds),
        "--worker-model", args.worker_model,
        "--reviewer-model", args.reviewer_model,
        "--json",
    ]
    if store_path:
        command += ["--store", store_path]
    log_path = supervisor_log_path(home, args.mission_id)
    pid_path = supervisor_pid_path(home, args.mission_id)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(log_path.parent, 0o700)
    descriptor = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, "ab") as log, open(os.devnull, "rb") as devnull:
        process = subprocess.Popen(
            command,
            stdin=devnull,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
            env=_child_env(),
        )
    pid_descriptor = os.open(pid_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(pid_descriptor, "w", encoding="utf-8") as handle:
        handle.write(f"{process.pid}\n")
    return {
        "ok": True,
        "command": "mission.supervise",
        "missionId": args.mission_id,
        "detached": True,
        "pid": process.pid,
        "pidFile": str(pid_path),
        "log": str(log_path),
        "message": (
            f"Supervisor for {args.mission_id} started in background (pid {process.pid}). "
            f"Follow with: pipe mission status {args.mission_id}"
        ),
    }


def _executable(value: str) -> str:
    """Resolve a path-like executable; keep a bare name for PATH lookup."""

    return str(Path(value).expanduser().resolve()) if os.sep in value else value


def _child_env() -> dict[str, str]:
    """The inherited environment, with this package's source root first on
    PYTHONPATH so the detached supervisor runs the same code as this process."""

    env = dict(os.environ)
    source_root = str(Path(__file__).resolve().parents[2])
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = source_root + (os.pathsep + existing if existing else "")
    return env
