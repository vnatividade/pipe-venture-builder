"""Hash-chained audit event construction and verification."""

from __future__ import annotations

from typing import Any, Mapping

from .model import (
    SCHEMA_VERSION,
    ControlPlaneContractError,
    fingerprint,
    parse_datetime,
    require_fingerprint,
    require_stable_id,
    safe_identifier,
    stable_id,
)


EVENT_TYPES = frozenset(
    {
        "run.created",
        "run.resumed",
        "run.interrupted",
        "run.completed",
        "run.failed",
        "plan.registered",
        "approval.recorded",
        "action.precondition_started",
        "action.precondition_passed",
        "action.blocked",
        "action.skipped",
        "action.apply_started",
        "action.apply_succeeded",
        "action.verify_started",
        "action.verified",
        "action.verify_failed",
    }
)
STATUSES = frozenset(
    {"pending", "running", "succeeded", "skipped", "blocked", "failed", "interrupted"}
)
REASON_CODES = frozenset(
    {
        None,
        "approval_missing",
        "approval_mismatch",
        "approval_expired",
        "approval_not_granted",
        "action_not_applicable",
        "action_blocked",
        "source_changed",
        "target_changed",
        "target_version_missing",
        "already_verified",
        "adapter_conflict",
        "adapter_failed",
        "verification_failed",
        "interrupted_after_apply",
        "audit_chain_invalid",
    }
)
CHECKPOINT_STATES = frozenset(
    {
        None,
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


def build_run_event(
    *,
    run_id: str,
    sequence: int,
    occurred_at: str,
    event_type: str,
    status: str,
    reason_code: str | None = None,
    plan_id: str | None = None,
    action_id: str | None = None,
    approval_id: str | None = None,
    idempotency_key: str | None = None,
    result_ref: str | None = None,
    plan_fingerprint: str | None = None,
    source_fingerprint: str | None = None,
    expected_target_fingerprint: str | None = None,
    observed_target_fingerprint: str | None = None,
    result_fingerprint: str | None = None,
    checkpoint_state: str | None = None,
    attempt: int = 0,
    previous_event_hash: str | None = None,
) -> dict[str, Any]:
    if event_type not in EVENT_TYPES or status not in STATUSES:
        raise ControlPlaneContractError("invalid audit event transition")
    if reason_code not in REASON_CODES or checkpoint_state not in CHECKPOINT_STATES:
        raise ControlPlaneContractError("invalid audit event classification")
    if not isinstance(sequence, int) or sequence < 1:
        raise ControlPlaneContractError("event sequence must be positive")
    if not isinstance(attempt, int) or attempt < 0:
        raise ControlPlaneContractError("checkpoint attempt must be non-negative")
    parse_datetime(occurred_at)
    require_stable_id(run_id, "RUN")
    for value, prefix in (
        (plan_id, "RP"),
        (action_id, "RA"),
        (approval_id, "AP"),
    ):
        if value is not None:
            require_stable_id(value, prefix)
    for value in (idempotency_key, result_ref):
        if value is not None:
            safe_identifier(value)
    for value in (
        plan_fingerprint,
        source_fingerprint,
        expected_target_fingerprint,
        observed_target_fingerprint,
        result_fingerprint,
        previous_event_hash,
    ):
        require_fingerprint(value, nullable=True)
    identity = {
        "runId": run_id,
        "sequence": sequence,
        "occurredAt": occurred_at,
        "eventType": event_type,
    }
    event = {
        "schemaVersion": SCHEMA_VERSION,
        "eventId": stable_id("EV", identity),
        **identity,
        "status": status,
        "reasonCode": reason_code,
        "references": {
            "planId": plan_id,
            "actionId": action_id,
            "approvalId": approval_id,
            "idempotencyKey": idempotency_key,
            "resultRef": result_ref,
        },
        "fingerprints": {
            "plan": plan_fingerprint,
            "source": source_fingerprint,
            "expectedTarget": expected_target_fingerprint,
            "observedTarget": observed_target_fingerprint,
            "result": result_fingerprint,
        },
        "checkpoint": {"state": checkpoint_state, "attempt": attempt},
        "constraints": {
            "rawPayloadPersisted": False,
            "credentialsPersisted": False,
            "customerDataPersisted": False,
            "productionDataPersisted": False,
        },
        "previousEventHash": previous_event_hash,
    }
    event["eventHash"] = fingerprint(event)
    return event


def verify_run_event(event: Mapping[str, Any], previous_hash: str | None) -> bool:
    if not isinstance(event, Mapping) or event.get("previousEventHash") != previous_hash:
        return False
    supplied = event.get("eventHash")
    try:
        require_fingerprint(supplied)
        unhashed = {key: value for key, value in event.items() if key != "eventHash"}
        return supplied == fingerprint(unhashed)
    except ControlPlaneContractError:
        return False
