"""Action-scoped, time-bounded human approval records."""

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


MUTATING_ACTIONS = frozenset({"create", "update", "link"})
DECISIONS = frozenset({"approved", "denied", "revoked"})
REQUIRED_FALSE_CONSTRAINTS = {
    "automaticApproval",
    "productionAuthorized",
    "secretsAuthorized",
    "customerDataAuthorized",
    "destructiveActionsAuthorized",
}


def build_approval_record(
    plan: Mapping[str, Any],
    action_id: str,
    *,
    actor_id: str,
    decided_at: str,
    expires_at: str,
    source_ref: str,
    decision: str = "approved",
) -> dict[str, Any]:
    """Build a tamper-evident decision bound to one exact plan action."""

    action = find_action(plan, action_id)
    _validate_approvable_action(action)
    if decision not in DECISIONS:
        raise ControlPlaneContractError("invalid approval decision")
    decided = parse_datetime(decided_at)
    expires = parse_datetime(expires_at)
    if expires <= decided:
        raise ControlPlaneContractError("approval expiry must follow its decision time")
    actor = safe_identifier(actor_id, limit=256)
    source = safe_identifier(source_ref, limit=256)
    source_fingerprint = require_fingerprint(plan.get("baseline", {}).get("fingerprint"))
    action_version = _action_version(action["idempotencyKey"])
    core = {
        "schemaVersion": SCHEMA_VERSION,
        "planId": plan["planId"],
        "actionId": action["actionId"],
        "actionVersion": action_version,
        "idempotencyKey": action["idempotencyKey"],
        "decision": decision,
        "actor": {"actorId": actor, "actorType": "human"},
        "decidedAt": decided_at,
        "expiresAt": expires_at,
        "sourceRef": source,
        "scope": {
            "targetSystem": action["targetSystem"],
            "targetContainerId": action["targetContainerId"],
            "actionType": action["actionType"],
            "sourceArtifactIds": sorted(action["sourceArtifactIds"]),
            "targetRecordIds": sorted(action["targetRecordIds"]),
            "sourceFingerprint": source_fingerprint,
            "targetFingerprint": require_fingerprint(
                action.get("targetFingerprint"), nullable=True
            ),
        },
        "constraints": {
            "automaticApproval": False,
            "productionAuthorized": False,
            "secretsAuthorized": False,
            "customerDataAuthorized": False,
            "destructiveActionsAuthorized": False,
        },
    }
    record = {"approvalId": stable_id("AP", core), **core}
    record["recordFingerprint"] = fingerprint(record)
    return record


def validate_approval_record(record: Mapping[str, Any]) -> None:
    """Fail closed on malformed or modified approval records."""

    if not isinstance(record, Mapping):
        raise ControlPlaneContractError("approval must be a mapping")
    required = {
        "schemaVersion",
        "approvalId",
        "planId",
        "actionId",
        "actionVersion",
        "idempotencyKey",
        "decision",
        "actor",
        "decidedAt",
        "expiresAt",
        "sourceRef",
        "scope",
        "constraints",
        "recordFingerprint",
    }
    if set(record) != required:
        raise ControlPlaneContractError("approval fields do not match the contract")
    if record["schemaVersion"] != SCHEMA_VERSION:
        raise ControlPlaneContractError("unsupported approval schema version")
    if record["decision"] not in DECISIONS:
        raise ControlPlaneContractError("invalid approval decision")
    require_stable_id(record["approvalId"], "AP")
    require_stable_id(record["planId"], "RP")
    require_stable_id(record["actionId"], "RA")
    safe_identifier(record["actionVersion"])
    safe_identifier(record["idempotencyKey"])
    safe_identifier(record["sourceRef"], limit=256)
    actor = record["actor"]
    if not isinstance(actor, Mapping) or set(actor) != {"actorId", "actorType"}:
        raise ControlPlaneContractError("approval actor is invalid")
    if actor["actorType"] != "human":
        raise ControlPlaneContractError("approval actor must be human")
    safe_identifier(actor["actorId"], limit=256)
    decided = parse_datetime(record["decidedAt"])
    expires = parse_datetime(record["expiresAt"])
    if expires <= decided:
        raise ControlPlaneContractError("approval expiry must follow its decision time")
    constraints = record["constraints"]
    if not isinstance(constraints, Mapping) or set(constraints) != REQUIRED_FALSE_CONSTRAINTS:
        raise ControlPlaneContractError("approval constraints are invalid")
    if any(constraints.values()):
        raise ControlPlaneContractError("approval cannot authorize an absolute gate")
    _validate_scope(record["scope"])
    supplied = require_fingerprint(record["recordFingerprint"])
    unhashed = {key: value for key, value in record.items() if key != "recordFingerprint"}
    if supplied != fingerprint(unhashed):
        raise ControlPlaneContractError("approval fingerprint mismatch")
    identity = {key: value for key, value in unhashed.items() if key != "approvalId"}
    if record["approvalId"] != stable_id("AP", identity):
        raise ControlPlaneContractError("approval identifier mismatch")


def validate_approval_for_action(
    record: Mapping[str, Any],
    plan: Mapping[str, Any],
    action: Mapping[str, Any],
    *,
    at: str,
) -> str | None:
    """Return a fixed reason code when approval cannot authorize this action."""

    try:
        validate_approval_record(record)
    except ControlPlaneContractError:
        return "approval_mismatch"
    if record["decision"] != "approved":
        return "approval_not_granted"
    now = parse_datetime(at)
    if now < parse_datetime(record["decidedAt"]) or now >= parse_datetime(
        record["expiresAt"]
    ):
        return "approval_expired"
    expected_scope = {
        "targetSystem": action["targetSystem"],
        "targetContainerId": action["targetContainerId"],
        "actionType": action["actionType"],
        "sourceArtifactIds": sorted(action["sourceArtifactIds"]),
        "targetRecordIds": sorted(action["targetRecordIds"]),
        "sourceFingerprint": plan["baseline"]["fingerprint"],
        "targetFingerprint": action["targetFingerprint"],
    }
    exact = (
        record["planId"] == plan["planId"]
        and record["actionId"] == action["actionId"]
        and record["actionVersion"] == _action_version(action["idempotencyKey"])
        and record["idempotencyKey"] == action["idempotencyKey"]
        and record["scope"] == expected_scope
    )
    return None if exact else "approval_mismatch"


def find_action(plan: Mapping[str, Any], action_id: str) -> Mapping[str, Any]:
    matches = [action for action in plan.get("actions", []) if action.get("actionId") == action_id]
    if len(matches) != 1:
        raise ControlPlaneContractError("plan must contain one exact action")
    return matches[0]


def _validate_approvable_action(action: Mapping[str, Any]) -> None:
    if action.get("actionType") not in MUTATING_ACTIONS:
        raise ControlPlaneContractError("only create, update, and link can be approved")
    if action.get("status") != "proposed" or action.get("blockerIds"):
        raise ControlPlaneContractError("blocked or terminal actions cannot be approved")
    if action.get("confidence") == "low":
        raise ControlPlaneContractError("low-confidence actions cannot be approved")
    if action.get("approvalRequired") is not True:
        raise ControlPlaneContractError("state-changing actions must require approval")


def _validate_scope(scope: Any) -> None:
    if not isinstance(scope, Mapping):
        raise ControlPlaneContractError("approval scope is invalid")
    required = {
        "targetSystem",
        "targetContainerId",
        "actionType",
        "sourceArtifactIds",
        "targetRecordIds",
        "sourceFingerprint",
        "targetFingerprint",
    }
    if set(scope) != required or scope["actionType"] not in MUTATING_ACTIONS:
        raise ControlPlaneContractError("approval scope is invalid")
    if scope["targetSystem"] not in {"linear", "github", "repository"}:
        raise ControlPlaneContractError("approval target system is invalid")
    safe_identifier(scope["targetContainerId"], limit=256)
    for key in ("sourceArtifactIds", "targetRecordIds"):
        values = scope[key]
        if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
            raise ControlPlaneContractError("approval scope identifiers are invalid")
        if values != sorted(set(values)):
            raise ControlPlaneContractError("approval scope identifiers must be sorted and unique")
        for value in values:
            safe_identifier(value, limit=256)
    if not scope["sourceArtifactIds"]:
        raise ControlPlaneContractError("approval source scope cannot be empty")
    require_fingerprint(scope["sourceFingerprint"])
    require_fingerprint(scope["targetFingerprint"], nullable=True)


def _action_version(idempotency_key: str) -> str:
    safe_identifier(idempotency_key)
    version = idempotency_key.rsplit(":", 1)[-1]
    if not version.startswith("v") or not version[1:].isdigit():
        raise ControlPlaneContractError("action idempotency version is invalid")
    return version
