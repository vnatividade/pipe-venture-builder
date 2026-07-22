"""Portable SQLite store for runs, approvals, checkpoints, and audit events."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from pipe_venture_builder.adapters.safety import payload_is_safe

from .approval import validate_approval_record
from .audit import build_run_event, verify_run_event
from .model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
    canonical_json,
    fingerprint,
    parse_datetime,
    require_fingerprint,
    require_stable_id,
    safe_identifier,
    stable_id,
)


DATABASE_SCHEMA_VERSION = 1
RUN_STATUSES = frozenset(
    {"pending", "running", "interrupted", "blocked", "failed", "completed"}
)
CHECKPOINT_STATES = frozenset(
    {
        "pending",
        "precondition_passed",
        "applying",
        "applied",
        "verifying",
        "verified",
        "skipped",
        "blocked",
        "failed",
        "interrupted",
    }
)


class LocalControlPlaneStore:
    """A machine-local, recoverable store with append-only hash-chained events."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        database = self.path
        if self.path != ":memory:":
            database_path = Path(path).expanduser()
            if database_path.exists() and database_path.is_symlink():
                raise ControlPlaneStateError("control-plane database cannot be a symlink")
            database_path.parent.mkdir(parents=True, exist_ok=True)
            if database_path.parent.is_symlink():
                raise ControlPlaneStateError("control-plane directory cannot be a symlink")
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

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> LocalControlPlaneStore:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def register_plan(self, plan: Mapping[str, Any], *, at: str) -> str:
        _validate_plan(plan)
        parse_datetime(at)
        plan_fingerprint = fingerprint(plan)
        run_id = stable_id(
            "RUN", {"planId": plan["planId"], "fingerprint": plan_fingerprint}
        )
        with self._connection:
            existing = self._connection.execute(
                "SELECT plan_fingerprint FROM plans WHERE plan_id = ?",
                (plan["planId"],),
            ).fetchone()
            if existing and existing["plan_fingerprint"] != plan_fingerprint:
                raise ControlPlaneStateError("plan identifier already has different content")
            if existing:
                return run_id
            self._connection.execute(
                "INSERT INTO plans(plan_id, plan_fingerprint, document_json) VALUES (?, ?, ?)",
                (plan["planId"], plan_fingerprint, canonical_json(plan)),
            )
            self._connection.execute(
                """
                INSERT INTO runs(
                    run_id, plan_id, plan_fingerprint, status, created_at, updated_at
                ) VALUES (?, ?, ?, 'pending', ?, ?)
                """,
                (run_id, plan["planId"], plan_fingerprint, at, at),
            )
            self._append_event(
                run_id,
                occurred_at=at,
                event_type="run.created",
                status="pending",
                plan_id=plan["planId"],
                plan_fingerprint=plan_fingerprint,
            )
            self._append_event(
                run_id,
                occurred_at=at,
                event_type="plan.registered",
                status="succeeded",
                plan_id=plan["planId"],
                plan_fingerprint=plan_fingerprint,
            )
        return run_id

    def record_approval(self, approval: Mapping[str, Any], *, at: str) -> bool:
        validate_approval_record(approval)
        parse_datetime(at)
        with self._connection:
            run = self._connection.execute(
                "SELECT run_id, plan_fingerprint FROM runs WHERE plan_id = ?",
                (approval["planId"],),
            ).fetchone()
            if run is None:
                raise ControlPlaneStateError("approval plan is not registered")
            existing = self._connection.execute(
                "SELECT record_fingerprint FROM approvals WHERE approval_id = ?",
                (approval["approvalId"],),
            ).fetchone()
            if existing:
                if existing["record_fingerprint"] != approval["recordFingerprint"]:
                    raise ControlPlaneStateError(
                        "approval identifier already has different content"
                    )
                return False
            self._connection.execute(
                """
                INSERT INTO approvals(
                    approval_id, plan_id, action_id, idempotency_key,
                    decision, expires_at, record_fingerprint, document_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval["approvalId"],
                    approval["planId"],
                    approval["actionId"],
                    approval["idempotencyKey"],
                    approval["decision"],
                    approval["expiresAt"],
                    approval["recordFingerprint"],
                    canonical_json(approval),
                ),
            )
            self._append_event(
                run["run_id"],
                occurred_at=at,
                event_type="approval.recorded",
                status="succeeded",
                plan_id=approval["planId"],
                action_id=approval["actionId"],
                approval_id=approval["approvalId"],
                idempotency_key=approval["idempotencyKey"],
                plan_fingerprint=run["plan_fingerprint"],
                source_fingerprint=approval["scope"]["sourceFingerprint"],
                expected_target_fingerprint=approval["scope"]["targetFingerprint"],
            )
        return True

    def append_event(self, run_id: str, *, occurred_at: str, **fields: Any) -> dict[str, Any]:
        parse_datetime(occurred_at)
        with self._connection:
            return self._append_event(run_id, occurred_at=occurred_at, **fields)

    def update_run_status(self, run_id: str, status: str, *, at: str) -> None:
        if status not in RUN_STATUSES:
            raise ControlPlaneContractError("invalid run status")
        parse_datetime(at)
        with self._connection:
            updated = self._connection.execute(
                "UPDATE runs SET status = ?, updated_at = ? WHERE run_id = ?",
                (status, at, run_id),
            ).rowcount
            if updated != 1:
                raise ControlPlaneStateError("run is not registered")

    def upsert_checkpoint(
        self,
        *,
        run_id: str,
        action_id: str,
        idempotency_key: str,
        state: str,
        attempt: int,
        approval_id: str | None,
        source_fingerprint: str,
        target_fingerprint: str | None,
        result_fingerprint: str | None,
        result_ref: str | None,
        at: str,
    ) -> None:
        if state not in CHECKPOINT_STATES:
            raise ControlPlaneContractError("invalid checkpoint state")
        if not isinstance(attempt, int) or attempt < 0:
            raise ControlPlaneContractError("invalid checkpoint attempt")
        for value in (run_id, action_id, idempotency_key, approval_id, result_ref):
            if value is not None:
                safe_identifier(value)
        require_fingerprint(source_fingerprint)
        require_fingerprint(target_fingerprint, nullable=True)
        require_fingerprint(result_fingerprint, nullable=True)
        parse_datetime(at)
        with self._connection:
            self._upsert_checkpoint(
                run_id=run_id,
                action_id=action_id,
                idempotency_key=idempotency_key,
                state=state,
                attempt=attempt,
                approval_id=approval_id,
                source_fingerprint=source_fingerprint,
                target_fingerprint=target_fingerprint,
                result_fingerprint=result_fingerprint,
                result_ref=result_ref,
                at=at,
            )

    def record_transition(
        self,
        *,
        run_id: str,
        action_id: str,
        idempotency_key: str,
        state: str,
        attempt: int,
        approval_id: str | None,
        source_fingerprint: str,
        target_fingerprint: str | None,
        result_fingerprint: str | None,
        result_ref: str | None,
        occurred_at: str,
        event_type: str,
        event_status: str,
        reason_code: str | None = None,
        plan_id: str | None = None,
        plan_fingerprint: str | None = None,
        observed_target_fingerprint: str | None = None,
        run_status: str | None = None,
    ) -> dict[str, Any]:
        """Persist one checkpoint/event transition atomically."""

        if state not in CHECKPOINT_STATES:
            raise ControlPlaneContractError("invalid checkpoint state")
        if run_status is not None and run_status not in RUN_STATUSES:
            raise ControlPlaneContractError("invalid run status")
        parse_datetime(occurred_at)
        with self._connection:
            self._upsert_checkpoint(
                run_id=run_id,
                action_id=action_id,
                idempotency_key=idempotency_key,
                state=state,
                attempt=attempt,
                approval_id=approval_id,
                source_fingerprint=source_fingerprint,
                target_fingerprint=target_fingerprint,
                result_fingerprint=result_fingerprint,
                result_ref=result_ref,
                at=occurred_at,
            )
            if run_status is not None:
                self._connection.execute(
                    "UPDATE runs SET status = ?, updated_at = ? WHERE run_id = ?",
                    (run_status, occurred_at, run_id),
                )
            return self._append_event(
                run_id,
                occurred_at=occurred_at,
                event_type=event_type,
                status=event_status,
                reason_code=reason_code,
                plan_id=plan_id,
                action_id=action_id,
                approval_id=approval_id,
                idempotency_key=idempotency_key,
                result_ref=result_ref,
                plan_fingerprint=plan_fingerprint,
                source_fingerprint=source_fingerprint,
                expected_target_fingerprint=target_fingerprint,
                observed_target_fingerprint=observed_target_fingerprint,
                result_fingerprint=result_fingerprint,
                checkpoint_state=state,
                attempt=attempt,
            )

    def record_run_event(
        self,
        run_id: str,
        *,
        occurred_at: str,
        event_type: str,
        event_status: str,
        run_status: str,
        plan_id: str,
        plan_fingerprint: str,
        reason_code: str | None = None,
        action_id: str | None = None,
        approval_id: str | None = None,
        idempotency_key: str | None = None,
        checkpoint_state: str | None = None,
        attempt: int = 0,
    ) -> dict[str, Any]:
        if run_status not in RUN_STATUSES:
            raise ControlPlaneContractError("invalid run status")
        parse_datetime(occurred_at)
        with self._connection:
            updated = self._connection.execute(
                "UPDATE runs SET status = ?, updated_at = ? WHERE run_id = ?",
                (run_status, occurred_at, run_id),
            ).rowcount
            if updated != 1:
                raise ControlPlaneStateError("run is not registered")
            return self._append_event(
                run_id,
                occurred_at=occurred_at,
                event_type=event_type,
                status=event_status,
                reason_code=reason_code,
                plan_id=plan_id,
                action_id=action_id,
                approval_id=approval_id,
                idempotency_key=idempotency_key,
                plan_fingerprint=plan_fingerprint,
                checkpoint_state=checkpoint_state,
                attempt=attempt,
            )

    def get_checkpoint(self, run_id: str, action_id: str) -> dict[str, Any] | None:
        row = self._connection.execute(
            "SELECT * FROM checkpoints WHERE run_id = ? AND action_id = ?",
            (run_id, action_id),
        ).fetchone()
        return self._verified_checkpoint(row) if row else None

    def find_checkpoint_by_idempotency_key(
        self, idempotency_key: str, *, excluding_run_id: str | None = None
    ) -> dict[str, Any] | None:
        safe_identifier(idempotency_key)
        if excluding_run_id is None:
            row = self._connection.execute(
                """
                SELECT * FROM checkpoints
                WHERE idempotency_key = ?
                ORDER BY updated_at DESC, run_id DESC LIMIT 1
                """,
                (idempotency_key,),
            ).fetchone()
        else:
            row = self._connection.execute(
                """
                SELECT * FROM checkpoints
                WHERE idempotency_key = ? AND run_id != ?
                ORDER BY updated_at DESC, run_id DESC LIMIT 1
                """,
                (idempotency_key, excluding_run_id),
            ).fetchone()
        return self._verified_checkpoint(row) if row else None

    def get_run(self, run_id: str) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT * FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            raise ControlPlaneStateError("run is not registered")
        return dict(row)

    def list_events(self, run_id: str) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            "SELECT event_json FROM events WHERE run_id = ? ORDER BY sequence",
            (run_id,),
        ).fetchall()
        return [json.loads(row["event_json"]) for row in rows]

    def verify_audit_chain(self, run_id: str) -> bool:
        previous: str | None = None
        events = self.list_events(run_id)
        if not events:
            return False
        for expected_sequence, event in enumerate(events, start=1):
            if event.get("sequence") != expected_sequence:
                return False
            if not verify_run_event(event, previous):
                return False
            previous = event["eventHash"]
        return True

    def verify_checkpoints(self, run_id: str) -> bool:
        rows = self._connection.execute(
            "SELECT * FROM checkpoints WHERE run_id = ? ORDER BY action_id",
            (run_id,),
        ).fetchall()
        try:
            for row in rows:
                self._verified_checkpoint(row)
        except ControlPlaneStateError:
            return False
        return True

    def all_actions_verified(
        self, run_id: str, action_ids: list[str]
    ) -> bool:
        if not action_ids:
            return True
        placeholders = ",".join("?" for _ in action_ids)
        rows = self._connection.execute(
            f"""
            SELECT * FROM checkpoints
            WHERE run_id = ? AND action_id IN ({placeholders})
            """,
            (run_id, *action_ids),
        ).fetchall()
        checkpoints = [self._verified_checkpoint(row) for row in rows]
        states = {item["action_id"]: item["state"] for item in checkpoints}
        return all(states.get(action_id) in {"verified", "skipped"} for action_id in action_ids)

    def _append_event(
        self, run_id: str, *, occurred_at: str, **fields: Any
    ) -> dict[str, Any]:
        run = self._connection.execute(
            "SELECT run_id FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if run is None:
            raise ControlPlaneStateError("run is not registered")
        prior = self._connection.execute(
            """
            SELECT sequence, event_hash FROM events
            WHERE run_id = ? ORDER BY sequence DESC LIMIT 1
            """,
            (run_id,),
        ).fetchone()
        sequence = prior["sequence"] + 1 if prior else 1
        previous_hash = prior["event_hash"] if prior else None
        event = build_run_event(
            run_id=run_id,
            sequence=sequence,
            occurred_at=occurred_at,
            previous_event_hash=previous_hash,
            **fields,
        )
        self._connection.execute(
            """
            INSERT INTO events(
                run_id, sequence, event_id, event_type, event_hash, event_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                sequence,
                event["eventId"],
                event["eventType"],
                event["eventHash"],
                canonical_json(event),
            ),
        )
        return event

    def _upsert_checkpoint(
        self,
        *,
        run_id: str,
        action_id: str,
        idempotency_key: str,
        state: str,
        attempt: int,
        approval_id: str | None,
        source_fingerprint: str,
        target_fingerprint: str | None,
        result_fingerprint: str | None,
        result_ref: str | None,
        at: str,
    ) -> None:
        checkpoint = {
            "run_id": run_id,
            "action_id": action_id,
            "idempotency_key": idempotency_key,
            "state": state,
            "attempt": attempt,
            "approval_id": approval_id,
            "source_fingerprint": source_fingerprint,
            "target_fingerprint": target_fingerprint,
            "result_fingerprint": result_fingerprint,
            "result_ref": result_ref,
            "updated_at": at,
        }
        checkpoint_hash = fingerprint(checkpoint)
        self._connection.execute(
            """
            INSERT INTO checkpoints(
                run_id, action_id, idempotency_key, state, attempt,
                approval_id, source_fingerprint, target_fingerprint,
                result_fingerprint, result_ref, updated_at, checkpoint_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id, action_id) DO UPDATE SET
                idempotency_key = excluded.idempotency_key,
                state = excluded.state,
                attempt = excluded.attempt,
                approval_id = excluded.approval_id,
                source_fingerprint = excluded.source_fingerprint,
                target_fingerprint = excluded.target_fingerprint,
                result_fingerprint = excluded.result_fingerprint,
                result_ref = excluded.result_ref,
                updated_at = excluded.updated_at,
                checkpoint_hash = excluded.checkpoint_hash
            """,
            (
                *checkpoint.values(),
                checkpoint_hash,
            ),
        )

    @staticmethod
    def _verified_checkpoint(row: sqlite3.Row) -> dict[str, Any]:
        checkpoint = dict(row)
        supplied = checkpoint.pop("checkpoint_hash")
        if supplied != fingerprint(checkpoint):
            raise ControlPlaneStateError("checkpoint fingerprint mismatch")
        checkpoint["checkpoint_hash"] = supplied
        return checkpoint

    def _initialize(self) -> None:
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS metadata(
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS plans(
                    plan_id TEXT PRIMARY KEY,
                    plan_fingerprint TEXT NOT NULL,
                    document_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs(
                    run_id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL UNIQUE REFERENCES plans(plan_id),
                    plan_fingerprint TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS approvals(
                    approval_id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL REFERENCES plans(plan_id),
                    action_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    record_fingerprint TEXT NOT NULL,
                    document_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events(
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    sequence INTEGER NOT NULL,
                    event_id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    PRIMARY KEY(run_id, sequence)
                );
                CREATE TABLE IF NOT EXISTS checkpoints(
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    action_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    state TEXT NOT NULL,
                    attempt INTEGER NOT NULL,
                    approval_id TEXT,
                    source_fingerprint TEXT NOT NULL,
                    target_fingerprint TEXT,
                    result_fingerprint TEXT,
                    result_ref TEXT,
                    updated_at TEXT NOT NULL,
                    checkpoint_hash TEXT NOT NULL,
                    PRIMARY KEY(run_id, action_id)
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
                raise ControlPlaneStateError(
                    "unsupported control-plane database schema version"
                )

    @staticmethod
    def _restrict_database_files(database: str) -> None:
        for candidate in (database, f"{database}-wal", f"{database}-shm"):
            path = Path(candidate)
            if path.exists():
                os.chmod(path, 0o600)


def _validate_plan(plan: Mapping[str, Any]) -> None:
    if not isinstance(plan, Mapping):
        raise ControlPlaneContractError("reconciliation plan must be a mapping")
    required = {"schemaVersion", "planId", "baseline", "actions", "constraints"}
    if not required.issubset(plan):
        raise ControlPlaneContractError("reconciliation plan is missing required fields")
    if plan["schemaVersion"] != "0.1.0":
        raise ControlPlaneContractError("unsupported reconciliation plan version")
    if not payload_is_safe(plan):
        raise ControlPlaneContractError("reconciliation plan failed the safety boundary")
    require_stable_id(plan["planId"], "RP")
    baseline = plan["baseline"]
    if not isinstance(baseline, Mapping):
        raise ControlPlaneContractError("reconciliation plan baseline is invalid")
    require_fingerprint(baseline.get("fingerprint"))
    if not isinstance(plan["actions"], list):
        raise ControlPlaneContractError("reconciliation plan actions must be an array")
    action_ids: set[str] = set()
    idempotency_keys: set[str] = set()
    required_action_fields = {
        "actionId",
        "idempotencyKey",
        "targetSystem",
        "targetContainerId",
        "actionType",
        "status",
        "sourceArtifactIds",
        "targetRecordIds",
        "snapshotIds",
        "matchStrategy",
        "confidence",
        "targetFingerprint",
        "reason",
        "expectedEffect",
        "approvalRequired",
        "reviewRequired",
        "blockerIds",
    }
    for action in plan["actions"]:
        if not isinstance(action, Mapping) or set(action) != required_action_fields:
            raise ControlPlaneContractError("reconciliation action must be a mapping")
        action_id = require_stable_id(action.get("actionId"), "RA")
        idempotency_key = safe_identifier(action.get("idempotencyKey"))
        if action_id in action_ids or idempotency_key in idempotency_keys:
            raise ControlPlaneContractError("reconciliation action identity must be unique")
        action_ids.add(action_id)
        idempotency_keys.add(idempotency_key)
        if action["targetSystem"] not in {"linear", "github", "repository"}:
            raise ControlPlaneContractError("reconciliation target system is invalid")
        safe_identifier(action["targetContainerId"])
        if action["actionType"] not in {
            "create",
            "update",
            "link",
            "ignore",
            "investigate",
        }:
            raise ControlPlaneContractError("reconciliation action type is invalid")
        if action["status"] not in {"proposed", "blocked", "already_satisfied"}:
            raise ControlPlaneContractError("reconciliation action status is invalid")
        if action["confidence"] not in {"low", "medium", "high"}:
            raise ControlPlaneContractError("reconciliation confidence is invalid")
        if action["matchStrategy"] not in {
            "explicit_reference",
            "stable_external_id",
            "git_relationship",
            "semantic_candidate",
            "manual",
        }:
            raise ControlPlaneContractError("reconciliation match strategy is invalid")
        require_fingerprint(action["targetFingerprint"], nullable=True)
        if not isinstance(action["approvalRequired"], bool):
            raise ControlPlaneContractError("reconciliation approval flag is invalid")
        if action["reviewRequired"] is not True:
            raise ControlPlaneContractError("reconciliation review flag is invalid")
        for key, allow_empty in (
            ("sourceArtifactIds", False),
            ("targetRecordIds", True),
            ("snapshotIds", True),
            ("blockerIds", True),
        ):
            values = action[key]
            if (
                not isinstance(values, list)
                or (not allow_empty and not values)
                or any(not isinstance(value, str) for value in values)
                or values != sorted(set(values))
            ):
                raise ControlPlaneContractError(
                    "reconciliation action references are invalid"
                )
            for value in values:
                safe_identifier(value)
    constraints = plan["constraints"]
    if (
        not isinstance(constraints, Mapping)
        or constraints.get("planOnly") is not True
        or constraints.get("externalMutationPerformed") is not False
        or constraints.get("mutationSurfaceExposed") is not False
        or constraints.get("semanticMatchesAutoConfirmed") is not False
        or constraints.get("destructiveActionsAllowed") is not False
    ):
        raise ControlPlaneContractError("reconciliation plan safety constraints are invalid")
