"""Inert, fingerprinted proposal documents (ADR-004 D6, D12 ``handoff``).

A proposal is plain JSON data: identifiers, hashes, an optional result
reference and, for an approvable action, the exact approved scope. It carries
no apply handle, callback or executable reference, and building or validating
one never applies, records or checkpoints a Pipe action. Application stays
behind the existing governed apply boundary, which this package never imports.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from pipe_venture_builder.adapters.safety import payload_is_safe
from pipe_venture_builder.control_plane.approval import MUTATING_ACTIONS
from pipe_venture_builder.control_plane.model import (
    FINGERPRINT_PATTERN,
    ControlPlaneContractError,
    fingerprint,
    parse_datetime,
)

from .context import WORKFLOW_KINDS
from .errors import DeepSeekHarnessContractError
from .session import MAX_ATTEMPTS


SCHEMA_VERSION = "0.1.0"
PROPOSAL_KINDS = frozenset({"read_result", "action_handoff"})
PROPOSAL_CONSTRAINTS = {
    "applyAuthorized": False,
    "externalMutationAllowed": False,
    "runtimeApprovalIsAuthority": False,
    "rawPayloadPersisted": False,
}
_FIELDS = frozenset(
    {
        "schemaVersion",
        "kind",
        "runId",
        "planId",
        "planFingerprint",
        "linearTicketId",
        "workflow",
        "sessionId",
        "attempt",
        "dispatchId",
        "bindingFingerprint",
        "contextFingerprint",
        "eventWatermark",
        "resultRef",
        "resultFingerprint",
        "action",
        "proposedAt",
        "constraints",
        "proposalFingerprint",
    }
)
_ACTION_FIELDS = frozenset({"actionId", "actionType", "approvalId", "idempotencyKey", "scope"})
_RESULT_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+=-]{0,255}")
_PATTERNS = {
    "runId": re.compile(r"RUN-[a-f0-9]{12}"),
    "planId": re.compile(r"RP-[a-f0-9]{12}"),
    "dispatchId": re.compile(r"DHD-[a-f0-9]{12}"),
    "linearTicketId": re.compile(r"PIP-[0-9]{1,9}"),
    "sessionId": re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+=-]{0,127}"),
    "planFingerprint": FINGERPRINT_PATTERN,
    "bindingFingerprint": FINGERPRINT_PATTERN,
    "contextFingerprint": FINGERPRINT_PATTERN,
    "proposalFingerprint": FINGERPRINT_PATTERN,
}
_ACTION_PATTERNS = {
    "actionId": re.compile(r"RA-[a-f0-9]{12}"),
    "approvalId": re.compile(r"AP-[a-f0-9]{12}"),
    "idempotencyKey": re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/+=-]{0,511}"),
}


def require_result(result_ref: Any, result_fingerprint: Any) -> None:
    """A result is referenced by a safe identifier and its fingerprint, never by content."""

    if (
        type(result_ref) is not str
        or _RESULT_REF.fullmatch(result_ref) is None
        or not payload_is_safe(result_ref)
        or type(result_fingerprint) is not str
        or FINGERPRINT_PATTERN.fullmatch(result_fingerprint) is None
    ):
        raise DeepSeekHarnessContractError("result_ref_invalid") from None


def sign_proposal(unsigned: Mapping[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in unsigned.items() if key != "proposalFingerprint"}
    try:
        document["proposalFingerprint"] = fingerprint(document)
    except ControlPlaneContractError:
        raise DeepSeekHarnessContractError("proposal_invalid") from None
    validate_proposal(document)
    return document


def validate_proposal(value: Any) -> None:
    """Refuse anything but an unaltered proposal in the closed, inert shape."""

    if not isinstance(value, Mapping) or set(value) != _FIELDS:
        _invalid()
    supplied = value["proposalFingerprint"]
    if type(supplied) is not str or FINGERPRINT_PATTERN.fullmatch(supplied) is None:
        _invalid()
    unsigned = {key: item for key, item in value.items() if key != "proposalFingerprint"}
    try:
        if fingerprint(unsigned) != supplied:
            _invalid()
    except ControlPlaneContractError:
        _invalid()
    if value["schemaVersion"] != SCHEMA_VERSION or value["kind"] not in PROPOSAL_KINDS:
        _invalid()
    for key, pattern in _PATTERNS.items():
        if type(value[key]) is not str or pattern.fullmatch(value[key]) is None:
            _invalid()
    if type(value["workflow"]) is not str or value["workflow"] not in WORKFLOW_KINDS:
        _invalid()
    if type(value["attempt"]) is not int or not 1 <= value["attempt"] <= MAX_ATTEMPTS:
        _invalid()
    if type(value["eventWatermark"]) is not int or value["eventWatermark"] < 0:
        _invalid()
    if type(value["proposedAt"]) is not str:
        _invalid()
    try:
        parse_datetime(value["proposedAt"])
    except ControlPlaneContractError:
        _invalid()
    if value["constraints"] != PROPOSAL_CONSTRAINTS:
        _invalid()
    if value["kind"] == "read_result":
        if value["action"] is not None:
            _invalid()
        try:
            require_result(value["resultRef"], value["resultFingerprint"])
        except DeepSeekHarnessContractError:
            _invalid()
    else:
        if value["resultRef"] is not None or value["resultFingerprint"] is not None:
            _invalid()
        _require_action(value["action"])
    if not payload_is_safe(dict(value)):
        _invalid()


def _require_action(action: Any) -> None:
    if not isinstance(action, Mapping) or set(action) != _ACTION_FIELDS:
        _invalid()
    for key, pattern in _ACTION_PATTERNS.items():
        if type(action[key]) is not str or pattern.fullmatch(action[key]) is None:
            _invalid()
    if action["actionType"] not in MUTATING_ACTIONS or not isinstance(action["scope"], Mapping):
        _invalid()


def _invalid() -> None:
    raise DeepSeekHarnessContractError("proposal_invalid") from None
