"""Durable, machine-local Mission store: SQLite, WAL, hash-chained events.

Same storage posture as the control plane (symlink refusal, 0600 files, busy
timeout), in its own database so ``control_plane/**`` stays untouched. Nothing
here persists prompts, conversation output, or diffs: documents are validated
by the contract, event payloads by ``events.validate_short_mapping``.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
    canonical_json,
    parse_datetime,
    require_fingerprint,
    require_stable_id,
    safe_identifier,
    stable_id,
    utc_now,
)

from .contract import (
    MISSION_ID_PREFIX,
    criterion_ids,
    is_human_source,
    validate_mission,
)
from .events import (
    build_mission_event,
    validate_short_mapping,
    verify_mission_event,
)


DATABASE_SCHEMA_VERSION = 1
RUN_ID_PREFIX = "MRUN"
RUN_DEFAULT_ROLE = "worker"
DECISION_ID_PREFIX = "DEC"

# Allowed transitions. ``unknown`` is deliberately absent: it is reachable only
# through ``mark_unknown`` (reconciliation), never through a routine verb.
# ``cancelled`` is reachable from every non-terminal state after ``draft`` so a
# founder can always end a mission, including one blocked on a pending decision.
TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"active"}),
    "active": frozenset({"paused", "cancelled", "blocked", "completed"}),
    "paused": frozenset({"active", "cancelled"}),
    "blocked": frozenset({"active", "cancelled"}),
    "completed": frozenset(),
    "cancelled": frozenset(),
    "unknown": frozenset(),
}
UNKNOWN_SOURCES = frozenset({"active", "paused", "blocked"})
RUN_OPEN_STATUS = "running"
RUN_FINAL_STATUSES = frozenset({"collected", "failed", "interrupted", "unknown"})
RUN_EVENT_BY_STATUS = {
    "collected": "run.collected",
    "failed": "run.failed",
    "interrupted": "run.interrupted",
    "unknown": "run.unknown",
}
VERDICTS = frozenset({"satisfied", "needs_revision", "out_of_mission", "blocked"})
BLOCK_REASONS = frozenset(
    {
        "budget_reached",
        "max_cycles",
        "review_blocked",
        "out_of_mission",
        "needs_revision_limit",
        "run_unknown",
        "run_failed",
        "delivery_checks_failed",
        "audit_chain_invalid",
    }
)
DECISION_KINDS = frozenset(
    {"approval", "clarification", "escalation", "out_of_mission", "budget"}
)
DECISION_STATUSES = frozenset({"pending", "resolved"})
DELIVERY_EVENTS = frozenset(
    {"delivery.pr_opened", "delivery.checks_passed", "delivery.checks_failed"}
)
MAX_DECISION_OPTIONS = 8


class MissionStore:
    """Machine-local recoverable state for missions and their audit chain."""

    def __init__(self, path: str | Path | None = None) -> None:
        target = self.default_path() if path is None else path
        self.path = str(target)
        database = self.path
        if self.path != ":memory:":
            database_path = Path(target).expanduser()
            if database_path.is_symlink():
                raise ControlPlaneStateError("mission database cannot be a symlink")
            database_path.parent.mkdir(parents=True, exist_ok=True)
            if database_path.parent.is_symlink():
                raise ControlPlaneStateError("mission directory cannot be a symlink")
            database = str(database_path)
            self.path = database
        self._connection = sqlite3.connect(database)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA busy_timeout = 5000")
        if database != ":memory:":
            self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize()
        if database != ":memory:":
            self._restrict_database_files(database)

    @staticmethod
    def default_path() -> Path:
        return Path.home() / ".pipe" / "mission" / "mission.sqlite3"

    @property
    def schema_version(self) -> int:
        row = self._connection.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version'"
        ).fetchone()
        return int(row["value"])

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> MissionStore:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    # -- missions -----------------------------------------------------------

    def create(self, document: Mapping[str, Any], *, at: str | None = None) -> str:
        mission = validate_mission(document)
        if mission["status"] != "draft":
            raise ControlPlaneContractError("a mission is created in draft status")
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        mission_id = mission["missionId"]
        with self._connection:
            existing = self._connection.execute(
                "SELECT fingerprint FROM missions WHERE mission_id = ?", (mission_id,)
            ).fetchone()
            if existing is not None:
                if existing["fingerprint"] != mission["fingerprint"]:
                    raise ControlPlaneStateError(
                        "mission identifier already has different content"
                    )
                return mission_id
            self._connection.execute(
                """
                INSERT INTO missions(
                    mission_id, version, status, document_json, fingerprint,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mission_id,
                    mission["version"],
                    mission["status"],
                    canonical_json(mission),
                    mission["fingerprint"],
                    mission["createdAt"],
                    mission["updatedAt"],
                ),
            )
            self._append_event(
                mission_id,
                event_type="mission.created",
                occurred_at=occurred_at,
                payload={
                    "missionId": mission_id,
                    "fingerprint": mission["fingerprint"],
                    "version": mission["version"],
                    "criteria": len(mission["successCriteria"]),
                },
            )
        return mission_id

    def get(self, mission_id: str) -> dict[str, Any]:
        return json.loads(self._mission_row(mission_id)["document_json"])

    def list_missions(self) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            """
            SELECT mission_id, version, status, fingerprint, created_at, updated_at
            FROM missions ORDER BY created_at, mission_id
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def activate(self, mission_id: str, *, at: str | None = None) -> None:
        self._transition(mission_id, "active", event_type="mission.activated", at=at)

    def pause(self, mission_id: str, *, at: str | None = None) -> None:
        self._transition(mission_id, "paused", event_type="mission.paused", at=at)

    def resume(self, mission_id: str, *, at: str | None = None) -> None:
        row = self._mission_row(mission_id)
        if row["status"] not in {"paused", "blocked"}:
            raise ControlPlaneStateError("mission status transition is not allowed")
        if row["status"] == "blocked" and self.pending_decisions(mission_id):
            raise ControlPlaneStateError(
                "blocked mission cannot resume with pending decisions"
            )
        self._transition(
            mission_id,
            "active",
            event_type="mission.resumed",
            at=at,
            payload={"from": row["status"]},
        )

    def cancel(self, mission_id: str, *, at: str | None = None) -> None:
        self._transition(mission_id, "cancelled", event_type="mission.cancelled", at=at)

    def block(self, mission_id: str, *, reason_code: str, at: str | None = None) -> None:
        if reason_code not in BLOCK_REASONS:
            raise ControlPlaneContractError("block reason code is not allowed")
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            row = self._mission_row(mission_id)
            self._require_transition(row["status"], "blocked")
            if reason_code == "budget_reached":
                self._append_event(
                    mission_id,
                    event_type="budget.reached",
                    occurred_at=occurred_at,
                    payload={
                        "costUsd": self.total_cost_usd(mission_id),
                        "maxBudgetUsd": json.loads(row["document_json"])["constraints"][
                            "maxBudgetUsd"
                        ],
                    },
                )
            self._apply_status(
                row,
                "blocked",
                event_type="mission.blocked",
                occurred_at=occurred_at,
                payload={"reasonCode": reason_code},
            )

    def mark_unknown(self, mission_id: str, *, at: str | None = None) -> None:
        """Reconciliation only: the supervisor lost track of the mission."""

        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            row = self._mission_row(mission_id)
            if row["status"] not in UNKNOWN_SOURCES:
                raise ControlPlaneStateError("mission status transition is not allowed")
            self._apply_status(
                row,
                "unknown",
                event_type="mission.unknown",
                occurred_at=occurred_at,
                payload={"from": row["status"]},
            )

    def complete(self, mission_id: str, *, at: str | None = None) -> None:
        """Explicit completion: evidence for every criterion, valid chain."""

        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            row = self._mission_row(mission_id)
            self._require_transition(row["status"], "completed")
            if not self.verify_chain(mission_id):
                raise ControlPlaneStateError("mission audit chain is invalid")
            document = json.loads(row["document_json"])
            evidence = self.criteria_status(mission_id)
            missing = [item["id"] for item in evidence if not item["satisfied"]]
            if missing:
                raise ControlPlaneStateError(
                    "mission cannot complete without evidence for every criterion"
                )
            if self.pending_decisions(mission_id):
                raise ControlPlaneStateError(
                    "mission cannot complete with pending decisions"
                )
            if document["delivery"]["kind"] == "pull_request":
                self._require_delivery(mission_id, document["delivery"]["requireChecks"])
            self._apply_status(
                row,
                "completed",
                event_type="mission.completed",
                occurred_at=occurred_at,
                payload={
                    "criteria": len(evidence),
                    "costUsd": self.total_cost_usd(mission_id),
                },
            )

    # -- events -------------------------------------------------------------

    def list_events(self, mission_id: str) -> list[dict[str, Any]]:
        require_stable_id(mission_id, MISSION_ID_PREFIX)
        rows = self._connection.execute(
            """
            SELECT event_json, event_hash, previous_hash FROM mission_events
            WHERE mission_id = ? ORDER BY sequence
            """,
            (mission_id,),
        ).fetchall()
        return [json.loads(row["event_json"]) for row in rows]

    def last_event(self, mission_id: str) -> dict[str, Any] | None:
        events = self.list_events(mission_id)
        return events[-1] if events else None

    def verify_chain(self, mission_id: str) -> bool:
        require_stable_id(mission_id, MISSION_ID_PREFIX)
        rows = self._connection.execute(
            """
            SELECT sequence, event_json, event_hash, previous_hash FROM mission_events
            WHERE mission_id = ? ORDER BY sequence
            """,
            (mission_id,),
        ).fetchall()
        if not rows:
            return False
        previous: str | None = None
        for expected_sequence, row in enumerate(rows, start=1):
            try:
                event = json.loads(row["event_json"])
            except ValueError:
                return False
            if (
                row["sequence"] != expected_sequence
                or event.get("sequence") != expected_sequence
                or event.get("missionId") != mission_id
                or row["event_hash"] != event.get("eventHash")
                or row["previous_hash"] != previous
                or not verify_mission_event(event, previous)
            ):
                return False
            previous = event["eventHash"]
        return True

    def record_delivery(
        self,
        mission_id: str,
        *,
        event_type: str,
        ref: str,
        at: str | None = None,
    ) -> dict[str, Any]:
        if event_type not in DELIVERY_EVENTS:
            raise ControlPlaneContractError("delivery event type is not allowed")
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            row = self._mission_row(mission_id)
            if row["status"] != "active":
                raise ControlPlaneStateError("delivery events require an active mission")
            return self._append_event(
                mission_id,
                event_type=event_type,
                occurred_at=occurred_at,
                payload={"ref": safe_identifier(ref)},
            )

    # -- runs ---------------------------------------------------------------

    def open_run(
        self,
        mission_id: str,
        *,
        cycle: int,
        attempt: int,
        executor: str,
        role: str = RUN_DEFAULT_ROLE,
        at: str | None = None,
    ) -> str:
        """Open a run. ``role`` separates the reviewer's run from the worker's
        in the same cycle/attempt; the default role keeps the historical id."""

        _positive_int(cycle, "run cycle")
        _positive_int(attempt, "run attempt")
        safe_identifier(executor)
        safe_identifier(role)
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        identity: dict[str, Any] = {"missionId": mission_id, "cycle": cycle, "attempt": attempt}
        if role != RUN_DEFAULT_ROLE:
            identity["role"] = role
        with self._connection:
            row = self._mission_row(mission_id)
            if row["status"] != "active":
                raise ControlPlaneStateError("runs can only be opened on an active mission")
            run_id = stable_id(RUN_ID_PREFIX, identity)
            existing = self._connection.execute(
                "SELECT run_id FROM mission_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if existing is not None:
                raise ControlPlaneStateError("run for this cycle and attempt already exists")
            self._connection.execute(
                """
                INSERT INTO mission_runs(
                    run_id, mission_id, attempt, cycle, executor, session_id, status,
                    started_at, ended_at, cost_usd, num_turns, result_ref,
                    result_fingerprint, verdict
                ) VALUES (?, ?, ?, ?, ?, NULL, ?, ?, NULL, 0, 0, NULL, NULL, NULL)
                """,
                (run_id, mission_id, attempt, cycle, executor, RUN_OPEN_STATUS, occurred_at),
            )
            self._append_event(
                mission_id,
                event_type="run.dispatched",
                occurred_at=occurred_at,
                payload={
                    "runId": run_id,
                    "cycle": cycle,
                    "attempt": attempt,
                    "executor": executor,
                },
            )
        return run_id

    def collect_run(
        self,
        run_id: str,
        *,
        session_id: str | None,
        cost_usd: float,
        num_turns: int,
        result_ref: str | None,
        result_fingerprint: str | None,
        status: str,
        at: str | None = None,
    ) -> None:
        if status not in RUN_FINAL_STATUSES:
            raise ControlPlaneContractError("run status is not allowed")
        if session_id is not None:
            safe_identifier(session_id)
        if result_ref is not None:
            safe_identifier(result_ref)
        require_fingerprint(result_fingerprint, nullable=True)
        cost = _non_negative_number(cost_usd, "run cost")
        if isinstance(num_turns, bool) or not isinstance(num_turns, int) or num_turns < 0:
            raise ControlPlaneContractError("run turns must be a non-negative integer")
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            run = self._run_row(run_id)
            if run["status"] != RUN_OPEN_STATUS:
                raise ControlPlaneStateError("run is not running")
            self._connection.execute(
                """
                UPDATE mission_runs
                SET session_id = ?, status = ?, ended_at = ?, cost_usd = ?, num_turns = ?,
                    result_ref = ?, result_fingerprint = ?
                WHERE run_id = ?
                """,
                (
                    session_id,
                    status,
                    occurred_at,
                    cost,
                    num_turns,
                    result_ref,
                    result_fingerprint,
                    run_id,
                ),
            )
            self._append_event(
                run["mission_id"],
                event_type=RUN_EVENT_BY_STATUS[status],
                occurred_at=occurred_at,
                payload={
                    "runId": run_id,
                    "cycle": run["cycle"],
                    "attempt": run["attempt"],
                    "sessionId": session_id,
                    "costUsd": cost,
                    "numTurns": num_turns,
                    "resultRef": result_ref,
                    "resultFingerprint": result_fingerprint,
                },
            )

    def record_verification(
        self,
        run_id: str,
        *,
        passed: bool,
        at: str | None = None,
        extra: Mapping[str, Any] | None = None,
        event_type: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(passed, bool):
            raise ControlPlaneContractError("verification result must be boolean")
        chosen = event_type or ("verify.passed" if passed else "verify.failed")
        if chosen not in {"verify.passed", "verify.failed"}:
            raise ControlPlaneContractError("mission event type is not allowed")
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        payload = validate_short_mapping(dict(extra or {}), what="verification payload")
        with self._connection:
            run = self._run_row(run_id)
            return self._append_event(
                run["mission_id"],
                event_type=chosen,
                occurred_at=occurred_at,
                payload={"runId": run_id, "cycle": run["cycle"], **payload},
            )

    def record_verdict(
        self, run_id: str, *, verdict: str, at: str | None = None
    ) -> dict[str, Any]:
        if verdict not in VERDICTS:
            raise ControlPlaneContractError("review verdict is not allowed")
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            run = self._run_row(run_id)
            self._connection.execute(
                "UPDATE mission_runs SET verdict = ? WHERE run_id = ?", (verdict, run_id)
            )
            return self._append_event(
                run["mission_id"],
                event_type=f"review.{verdict}",
                occurred_at=occurred_at,
                payload={"runId": run_id, "cycle": run["cycle"], "attempt": run["attempt"]},
            )

    def get_run(self, run_id: str) -> dict[str, Any]:
        return dict(self._run_row(run_id))

    def list_runs(self, mission_id: str) -> list[dict[str, Any]]:
        require_stable_id(mission_id, MISSION_ID_PREFIX)
        rows = self._connection.execute(
            "SELECT * FROM mission_runs WHERE mission_id = ? ORDER BY cycle, attempt",
            (mission_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def run_counts(self, mission_id: str) -> dict[str, int]:
        require_stable_id(mission_id, MISSION_ID_PREFIX)
        rows = self._connection.execute(
            """
            SELECT status, COUNT(*) AS total FROM mission_runs
            WHERE mission_id = ? GROUP BY status ORDER BY status
            """,
            (mission_id,),
        ).fetchall()
        return {row["status"]: row["total"] for row in rows}

    def total_cost_usd(self, mission_id: str) -> float:
        require_stable_id(mission_id, MISSION_ID_PREFIX)
        row = self._connection.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) AS total FROM mission_runs WHERE mission_id = ?",
            (mission_id,),
        ).fetchone()
        return float(row["total"])

    # -- decisions ----------------------------------------------------------

    def open_decision(
        self,
        mission_id: str,
        *,
        kind: str,
        context: Mapping[str, Any],
        options: list[str],
        safe_default: str,
        blocked_scope: str,
        deadline: str | None,
        at: str | None = None,
    ) -> str:
        if kind not in DECISION_KINDS:
            raise ControlPlaneContractError("decision kind is not allowed")
        short_context = validate_short_mapping(context, what="decision context")
        if (
            not isinstance(options, list)
            or len(options) < 2
            or len(options) > MAX_DECISION_OPTIONS
            or len(set(options)) != len(options)
        ):
            raise ControlPlaneContractError("decision needs two to eight distinct options")
        for option in options:
            safe_identifier(option)
        if safe_default not in options:
            raise ControlPlaneContractError("decision safe default must be one of the options")
        safe_identifier(blocked_scope)
        if deadline is not None:
            parse_datetime(deadline)
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            row = self._mission_row(mission_id)
            if row["status"] not in {"active", "paused", "blocked"}:
                raise ControlPlaneStateError("decisions require a live mission")
            decision_id = stable_id(
                DECISION_ID_PREFIX,
                {
                    "missionId": mission_id,
                    "kind": kind,
                    "context": short_context,
                    "options": options,
                    "openedAt": occurred_at,
                },
            )
            duplicate = self._connection.execute(
                """
                SELECT decision_id FROM decisions
                WHERE mission_id = ? AND kind = ? AND context_json = ? AND status = 'pending'
                """,
                (mission_id, kind, canonical_json(short_context)),
            ).fetchone()
            if duplicate is not None:
                return duplicate["decision_id"]
            self._connection.execute(
                """
                INSERT INTO decisions(
                    decision_id, mission_id, kind, status, context_json, options_json,
                    safe_default, blocked_scope, deadline, opened_at,
                    decided_by, decided_option, decided_at
                ) VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
                """,
                (
                    decision_id,
                    mission_id,
                    kind,
                    canonical_json(short_context),
                    canonical_json(options),
                    safe_default,
                    blocked_scope,
                    deadline,
                    occurred_at,
                ),
            )
            self._append_event(
                mission_id,
                event_type="decision.opened",
                occurred_at=occurred_at,
                payload={
                    "decisionId": decision_id,
                    "kind": kind,
                    "options": list(options),
                    "safeDefault": safe_default,
                    "blockedScope": blocked_scope,
                    "deadline": deadline,
                },
            )
        return decision_id

    def resolve_decision(
        self,
        decision_id: str,
        *,
        option: str,
        decided_by: str,
        at: str | None = None,
    ) -> dict[str, Any]:
        if not is_human_source(decided_by):
            raise ControlPlaneContractError("decisions are resolved by a named human source")
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            decision = self._decision_row(decision_id)
            if decision["status"] != "pending":
                raise ControlPlaneStateError("decision is already resolved")
            options = json.loads(decision["options_json"])
            if option not in options:
                raise ControlPlaneContractError("decision option is not one of the options")
            self._connection.execute(
                """
                UPDATE decisions
                SET status = 'resolved', decided_by = ?, decided_option = ?, decided_at = ?
                WHERE decision_id = ?
                """,
                (decided_by, option, occurred_at, decision_id),
            )
            self._append_event(
                decision["mission_id"],
                event_type="decision.resolved",
                occurred_at=occurred_at,
                payload={
                    "decisionId": decision_id,
                    "kind": decision["kind"],
                    "option": option,
                    "decidedBy": decided_by,
                },
            )
        return self.get_decision(decision_id)

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        return _decision_as_dict(self._decision_row(decision_id))

    def list_decisions(self, mission_id: str, *, pending_only: bool = False) -> list[dict[str, Any]]:
        require_stable_id(mission_id, MISSION_ID_PREFIX)
        query = "SELECT * FROM decisions WHERE mission_id = ?"
        if pending_only:
            query += " AND status = 'pending'"
        rows = self._connection.execute(
            query + " ORDER BY opened_at, decision_id", (mission_id,)
        ).fetchall()
        return [_decision_as_dict(row) for row in rows]

    def pending_decisions(self, mission_id: str) -> list[dict[str, Any]]:
        return self.list_decisions(mission_id, pending_only=True)

    # -- evidence -----------------------------------------------------------

    def record_evidence(
        self,
        mission_id: str,
        *,
        criterion_id: str,
        run_id: str | None,
        satisfied: bool,
        evidence_ref: str | None,
        evidence_fingerprint: str | None,
        at: str | None = None,
    ) -> None:
        if not isinstance(satisfied, bool):
            raise ControlPlaneContractError("evidence satisfied flag must be boolean")
        if evidence_ref is not None:
            safe_identifier(evidence_ref)
        require_fingerprint(evidence_fingerprint, nullable=True)
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            row = self._mission_row(mission_id)
            if row["status"] not in {"active", "paused", "blocked"}:
                raise ControlPlaneStateError("evidence requires a live mission")
            document = json.loads(row["document_json"])
            if criterion_id not in criterion_ids(document):
                raise ControlPlaneContractError("criterion is not part of the mission")
            if run_id is not None:
                run = self._run_row(run_id)
                if run["mission_id"] != mission_id:
                    raise ControlPlaneStateError("run belongs to a different mission")
            self._connection.execute(
                """
                INSERT INTO criteria_evidence(
                    mission_id, criterion_id, run_id, satisfied, evidence_ref,
                    evidence_fingerprint, at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mission_id,
                    criterion_id,
                    run_id,
                    1 if satisfied else 0,
                    evidence_ref,
                    evidence_fingerprint,
                    occurred_at,
                ),
            )

    def criteria_status(self, mission_id: str) -> list[dict[str, Any]]:
        """Latest evidence per criterion, in mission order; unset means False."""

        document = self.get(mission_id)
        rows = self._connection.execute(
            """
            SELECT criterion_id, satisfied, run_id, evidence_ref, at FROM criteria_evidence
            WHERE mission_id = ? ORDER BY evidence_id
            """,
            (mission_id,),
        ).fetchall()
        latest: dict[str, sqlite3.Row] = {}
        for row in rows:
            latest[row["criterion_id"]] = row
        result = []
        for criterion in document["successCriteria"]:
            row = latest.get(criterion["id"])
            result.append(
                {
                    "id": criterion["id"],
                    "kind": criterion["kind"],
                    "satisfied": bool(row["satisfied"]) if row else False,
                    "runId": row["run_id"] if row else None,
                    "evidenceRef": row["evidence_ref"] if row else None,
                    "at": row["at"] if row else None,
                }
            )
        return result

    # -- internals ----------------------------------------------------------

    def _transition(
        self,
        mission_id: str,
        target: str,
        *,
        event_type: str,
        at: str | None,
        payload: Mapping[str, Any] | None = None,
    ) -> None:
        occurred_at = at or utc_now()
        parse_datetime(occurred_at)
        with self._connection:
            row = self._mission_row(mission_id)
            self._require_transition(row["status"], target)
            self._apply_status(
                row,
                target,
                event_type=event_type,
                occurred_at=occurred_at,
                payload=dict(payload or {}),
            )

    @staticmethod
    def _require_transition(current: str, target: str) -> None:
        if target not in TRANSITIONS.get(current, frozenset()):
            raise ControlPlaneStateError("mission status transition is not allowed")

    def _apply_status(
        self,
        row: sqlite3.Row,
        target: str,
        *,
        event_type: str,
        occurred_at: str,
        payload: Mapping[str, Any],
    ) -> None:
        document = json.loads(row["document_json"])
        document["status"] = target
        document["updatedAt"] = occurred_at
        validate_mission(document)
        self._connection.execute(
            """
            UPDATE missions SET status = ?, document_json = ?, updated_at = ?
            WHERE mission_id = ?
            """,
            (target, canonical_json(document), occurred_at, row["mission_id"]),
        )
        self._append_event(
            row["mission_id"],
            event_type=event_type,
            occurred_at=occurred_at,
            payload={"status": target, **payload},
        )

    def _require_delivery(self, mission_id: str, require_checks: bool) -> None:
        """Gate ``complete`` on the delivery events recorded so far.

        A PR must have been opened; when checks are required, the *latest*
        ``delivery.checks_*`` event after the *latest* ``delivery.pr_opened``
        must be ``checks_passed`` (a later failure or a fresh PR resets it).
        """

        opened = False
        latest_checks = None
        for event in self.list_events(mission_id):
            event_type = event["eventType"]
            if event_type == "delivery.pr_opened":
                opened = True
                latest_checks = None
            elif opened and event_type in {
                "delivery.checks_passed",
                "delivery.checks_failed",
            }:
                latest_checks = event_type
        if not opened:
            raise ControlPlaneStateError("pull request delivery requires an opened PR")
        if require_checks and latest_checks != "delivery.checks_passed":
            raise ControlPlaneStateError("pull request delivery requires passing checks")

    def _append_event(
        self,
        mission_id: str,
        *,
        event_type: str,
        occurred_at: str,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        prior = self._connection.execute(
            """
            SELECT sequence, event_hash FROM mission_events
            WHERE mission_id = ? ORDER BY sequence DESC LIMIT 1
            """,
            (mission_id,),
        ).fetchone()
        sequence = prior["sequence"] + 1 if prior else 1
        previous_hash = prior["event_hash"] if prior else None
        event = build_mission_event(
            mission_id=mission_id,
            sequence=sequence,
            occurred_at=occurred_at,
            event_type=event_type,
            payload=payload,
            previous_hash=previous_hash,
        )
        self._connection.execute(
            """
            INSERT INTO mission_events(
                mission_id, sequence, event_id, event_type, event_json,
                event_hash, previous_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mission_id,
                sequence,
                event["eventId"],
                event_type,
                canonical_json(event),
                event["eventHash"],
                previous_hash,
            ),
        )
        return event

    def _mission_row(self, mission_id: str) -> sqlite3.Row:
        require_stable_id(mission_id, MISSION_ID_PREFIX)
        row = self._connection.execute(
            "SELECT * FROM missions WHERE mission_id = ?", (mission_id,)
        ).fetchone()
        if row is None:
            raise ControlPlaneStateError("mission is not registered")
        return row

    def _run_row(self, run_id: str) -> sqlite3.Row:
        require_stable_id(run_id, RUN_ID_PREFIX)
        row = self._connection.execute(
            "SELECT * FROM mission_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            raise ControlPlaneStateError("run is not registered")
        return row

    def _decision_row(self, decision_id: str) -> sqlite3.Row:
        require_stable_id(decision_id, DECISION_ID_PREFIX)
        row = self._connection.execute(
            "SELECT * FROM decisions WHERE decision_id = ?", (decision_id,)
        ).fetchone()
        if row is None:
            raise ControlPlaneStateError("decision is not registered")
        return row

    def _initialize(self) -> None:
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS metadata(
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS missions(
                    mission_id TEXT PRIMARY KEY,
                    version INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    document_json TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS mission_events(
                    mission_id TEXT NOT NULL REFERENCES missions(mission_id),
                    sequence INTEGER NOT NULL,
                    event_id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    previous_hash TEXT,
                    PRIMARY KEY(mission_id, sequence)
                );
                CREATE TABLE IF NOT EXISTS mission_runs(
                    run_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL REFERENCES missions(mission_id),
                    attempt INTEGER NOT NULL,
                    cycle INTEGER NOT NULL,
                    executor TEXT NOT NULL,
                    session_id TEXT,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    cost_usd REAL NOT NULL DEFAULT 0,
                    num_turns INTEGER NOT NULL DEFAULT 0,
                    result_ref TEXT,
                    result_fingerprint TEXT,
                    verdict TEXT
                );
                CREATE TABLE IF NOT EXISTS decisions(
                    decision_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL REFERENCES missions(mission_id),
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    context_json TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    safe_default TEXT NOT NULL,
                    blocked_scope TEXT NOT NULL,
                    deadline TEXT,
                    opened_at TEXT NOT NULL,
                    decided_by TEXT,
                    decided_option TEXT,
                    decided_at TEXT
                );
                CREATE TABLE IF NOT EXISTS criteria_evidence(
                    evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mission_id TEXT NOT NULL REFERENCES missions(mission_id),
                    criterion_id TEXT NOT NULL,
                    run_id TEXT REFERENCES mission_runs(run_id),
                    satisfied INTEGER NOT NULL,
                    evidence_ref TEXT,
                    evidence_fingerprint TEXT,
                    at TEXT NOT NULL
                );
                """
            )
            row = self._connection.execute(
                "SELECT value FROM metadata WHERE key = 'schema_version'"
            ).fetchone()
            if row is None:
                self._connection.execute(
                    "INSERT INTO metadata(key, value) VALUES ('schema_version', ?)",
                    (str(DATABASE_SCHEMA_VERSION),),
                )
            elif row["value"] != str(DATABASE_SCHEMA_VERSION):
                raise ControlPlaneStateError("unsupported mission database schema version")

    @staticmethod
    def _restrict_database_files(database: str) -> None:
        for candidate in (database, f"{database}-wal", f"{database}-shm"):
            path = Path(candidate)
            if path.exists():
                os.chmod(path, 0o600)


def _decision_as_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "decisionId": row["decision_id"],
        "missionId": row["mission_id"],
        "kind": row["kind"],
        "status": row["status"],
        "context": json.loads(row["context_json"]),
        "options": json.loads(row["options_json"]),
        "safeDefault": row["safe_default"],
        "blockedScope": row["blocked_scope"],
        "deadline": row["deadline"],
        "openedAt": row["opened_at"],
        "decidedBy": row["decided_by"],
        "decidedOption": row["decided_option"],
        "decidedAt": row["decided_at"],
    }


def _positive_int(value: Any, what: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ControlPlaneContractError(f"{what} must be a positive integer")


def _non_negative_number(value: Any, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ControlPlaneContractError(f"{what} must be a number")
    number = float(value)
    if number != number or number < 0 or number == float("inf"):
        raise ControlPlaneContractError(f"{what} must be non-negative")
    return number
