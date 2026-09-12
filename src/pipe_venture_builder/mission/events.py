"""Hash-chained mission events: fixed allowlist, short payloads, no free text.

An event payload may carry identifiers, hashes, counts, states, and references.
Every string value must pass ``safe_identifier`` (which rejects whitespace and
secret shapes), so prompts, conversation output, or diffs cannot be smuggled in.
"""

from __future__ import annotations

import math
import re
from typing import Any, Mapping

from pipe_venture_builder.adapters.safety import payload_is_safe
from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    fingerprint,
    parse_datetime,
    require_fingerprint,
    require_stable_id,
    safe_identifier,
    stable_id,
)

from .contract import MISSION_ID_PREFIX, PROGRAM_ID_PREFIX_RAW, SCHEMA_VERSION


EVENT_ID_PREFIX = "MEV"
EVENT_TYPES = frozenset(
    {
        "mission.created",
        "mission.activated",
        "mission.paused",
        "mission.resumed",
        "mission.cancelled",
        "mission.blocked",
        "mission.completed",
        "mission.unknown",
        "run.dispatched",
        "run.collected",
        "run.interrupted",
        "run.failed",
        "run.unknown",
        "verify.passed",
        "verify.failed",
        "review.satisfied",
        "review.needs_revision",
        "review.out_of_mission",
        "review.blocked",
        "decision.opened",
        "decision.resolved",
        "decision.delegated",
        "delivery.pr_opened",
        "delivery.checks_passed",
        "delivery.checks_failed",
        "budget.reached",
    }
)

# A program's own hash-chained events (PIP-910): a separate allowlist and
# table (``program_events``) from a mission's, so ``EVENT_TYPES`` above stays
# the exact fixed set ``test_event_allowlist_is_fixed`` pins. ``decision.*``
# is shared: a decision opened on a program (``store.open_decision`` now
# accepts a ``PRG-`` subject too) is chained here the same way a mission's is
# chained in ``mission_events``.
PROGRAM_EVENT_ID_PREFIX = "PEV"
PROGRAM_EVENT_TYPES = frozenset(
    {
        "program.created",
        "program.activated",
        "program.paused",
        "program.resumed",
        "program.cancelled",
        "program.blocked",
        "program.completed",
        "program.stage_mission_recorded",
        "decision.opened",
        "decision.resolved",
        "decision.delegated",
    }
)

MAX_PAYLOAD_KEYS = 32
MAX_PAYLOAD_LIST_ITEMS = 64
MAX_PAYLOAD_BYTES = 4 * 1024
_PAYLOAD_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9]{0,31}$")


def validate_short_mapping(value: Any, *, what: str) -> dict[str, Any]:
    """A flat mapping of identifiers/hashes/counts/states; never long text."""

    if not isinstance(value, Mapping):
        raise ControlPlaneContractError(f"{what} must be a mapping")
    if len(value) > MAX_PAYLOAD_KEYS:
        raise ControlPlaneContractError(f"{what} has too many fields")
    if not payload_is_safe(value):
        raise ControlPlaneContractError(f"{what} failed the safety boundary")
    normalized: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not _PAYLOAD_KEY.fullmatch(key):
            raise ControlPlaneContractError(f"{what} has an invalid field name")
        if isinstance(item, list):
            if len(item) > MAX_PAYLOAD_LIST_ITEMS:
                raise ControlPlaneContractError(f"{what} list is too long")
            normalized[key] = [_scalar(entry, what) for entry in item]
        else:
            normalized[key] = _scalar(item, what)
    encoded = fingerprint(normalized)  # canonical JSON; raises on non-JSON
    del encoded
    return normalized


def build_mission_event(
    *,
    mission_id: str,
    sequence: int,
    occurred_at: str,
    event_type: str,
    payload: Mapping[str, Any],
    previous_hash: str | None,
) -> dict[str, Any]:
    if event_type not in EVENT_TYPES:
        raise ControlPlaneContractError("mission event type is not allowed")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise ControlPlaneContractError("event sequence must be positive")
    require_stable_id(mission_id, MISSION_ID_PREFIX)
    parse_datetime(occurred_at)
    require_fingerprint(previous_hash, nullable=True)
    identity = {
        "missionId": mission_id,
        "sequence": sequence,
        "occurredAt": occurred_at,
        "eventType": event_type,
    }
    event: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "eventId": stable_id(EVENT_ID_PREFIX, identity),
        **identity,
        "payload": validate_short_mapping(payload, what="mission event payload"),
        "previousHash": previous_hash,
    }
    event["eventHash"] = fingerprint(event)
    return event


def verify_mission_event(event: Mapping[str, Any], previous_hash: str | None) -> bool:
    if not isinstance(event, Mapping) or event.get("previousHash") != previous_hash:
        return False
    if event.get("eventType") not in EVENT_TYPES:
        return False
    supplied = event.get("eventHash")
    try:
        require_fingerprint(supplied)
        unhashed = {key: value for key, value in event.items() if key != "eventHash"}
        return supplied == fingerprint(unhashed)
    except ControlPlaneContractError:
        return False


def build_program_event(
    *,
    program_id: str,
    sequence: int,
    occurred_at: str,
    event_type: str,
    payload: Mapping[str, Any],
    previous_hash: str | None,
) -> dict[str, Any]:
    """A program's hash-chained event; same shape and rules as
    ``build_mission_event``, keyed by ``programId`` instead of ``missionId``."""

    if event_type not in PROGRAM_EVENT_TYPES:
        raise ControlPlaneContractError("program event type is not allowed")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise ControlPlaneContractError("event sequence must be positive")
    require_stable_id(program_id, PROGRAM_ID_PREFIX_RAW)
    parse_datetime(occurred_at)
    require_fingerprint(previous_hash, nullable=True)
    identity = {
        "programId": program_id,
        "sequence": sequence,
        "occurredAt": occurred_at,
        "eventType": event_type,
    }
    event: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "eventId": stable_id(PROGRAM_EVENT_ID_PREFIX, identity),
        **identity,
        "payload": validate_short_mapping(payload, what="program event payload"),
        "previousHash": previous_hash,
    }
    event["eventHash"] = fingerprint(event)
    return event


def verify_program_event(event: Mapping[str, Any], previous_hash: str | None) -> bool:
    if not isinstance(event, Mapping) or event.get("previousHash") != previous_hash:
        return False
    if event.get("eventType") not in PROGRAM_EVENT_TYPES:
        return False
    supplied = event.get("eventHash")
    try:
        require_fingerprint(supplied)
        unhashed = {key: value for key, value in event.items() if key != "eventHash"}
        return supplied == fingerprint(unhashed)
    except ControlPlaneContractError:
        return False


def _scalar(item: Any, what: str) -> Any:
    if item is None or isinstance(item, bool):
        return item
    if isinstance(item, int):
        return item
    if isinstance(item, float):
        if not math.isfinite(item):
            raise ControlPlaneContractError(f"{what} number must be finite")
        return item
    if isinstance(item, str):
        return safe_identifier(item)
    raise ControlPlaneContractError(f"{what} value has an unsupported type")
