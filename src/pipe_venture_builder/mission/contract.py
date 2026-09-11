"""Mission contract v0.1.0: validation, identity, and fingerprint.

The contract is enforced here, in code. ``schemas/Mission.schema.json`` mirrors
it for external tooling and is cross-checked by tests. Error messages are fixed
strings: they never echo the offending value, so a rejected document cannot
leak through the message.
"""

from __future__ import annotations

import copy
import math
import re
from pathlib import PurePosixPath
from typing import Any, Mapping

from pipe_venture_builder.adapters.safety import payload_is_safe
from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    canonical_json,
    fingerprint,
    parse_datetime,
    require_fingerprint,
    require_stable_id,
    safe_identifier,
    stable_id,
    utc_now,
)


SCHEMA_VERSION = "0.1.0"
MISSION_ID_PREFIX = "MSN"

MISSION_STATUSES = frozenset(
    {"draft", "active", "paused", "blocked", "completed", "cancelled", "unknown"}
)
CRITERION_KINDS = frozenset({"check", "artifact", "rubric"})
DELIVERY_KINDS = frozenset({"none", "pull_request"})
ABSOLUTE_GATE_FLAGS = (
    "productionAllowed",
    "secretsAllowed",
    "externalCommsAllowed",
    "billingAllowed",
)
HUMAN_SOURCE_PREFIXES = ("human:chat:", "human:linear:", "human:cli:")
FINGERPRINT_EXCLUDED_FIELDS = frozenset(
    {"status", "createdAt", "updatedAt", "fingerprint"}
)

TOP_LEVEL_FIELDS = frozenset(
    {
        "schemaVersion",
        "missionId",
        "version",
        "supersedes",
        "title",
        "intent",
        "problem",
        "who",
        "successCriteria",
        "nonGoals",
        "delegable",
        "reservedToHuman",
        "constraints",
        "workspace",
        "delivery",
        "linearTicketIds",
        "status",
        "createdAt",
        "updatedAt",
        "fingerprint",
    }
)
CONSTRAINT_FIELDS = frozenset(
    {"maxCycles", "maxBudgetUsd", "maxTurnsPerRun", *ABSOLUTE_GATE_FLAGS}
)
CRITERION_FIELDS = {
    "check": (frozenset({"command"}), frozenset({"cwd"})),
    "artifact": (frozenset({"path"}), frozenset({"mustMatch"})),
    "rubric": (frozenset({"question"}), frozenset()),
}

MAX_DOCUMENT_BYTES = 64 * 1024
MAX_TITLE_CHARS = 200
MAX_TEXT_CHARS = 4000
MAX_CRITERION_TEXT_CHARS = 1000
MAX_COMMAND_CHARS = 2000
MAX_LIST_ITEMS = 64
MAX_PATH_CHARS = 1024
MAX_REGEX_CHARS = 500

_LINEAR_TICKET = re.compile(r"^[A-Z][A-Z0-9]{0,15}-[0-9]{1,9}$")
_CRITERION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_BASE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,255}$")


def mission_fingerprint(document: Mapping[str, Any]) -> str:
    """Fingerprint the document without status, timestamps, or its own hash."""

    if not isinstance(document, Mapping):
        raise ControlPlaneContractError("mission document must be a mapping")
    core = {
        key: value
        for key, value in document.items()
        if key not in FINGERPRINT_EXCLUDED_FIELDS
    }
    return fingerprint(core)


def build_mission(
    draft: Mapping[str, Any], *, created_at: str | None = None
) -> dict[str, Any]:
    """Complete a founder-authored draft into a validated Mission document.

    Optional bookkeeping fields (``missionId``, ``status``, timestamps,
    ``fingerprint``) are filled when absent and checked when present; nothing
    supplied is trusted without being recomputed.
    """

    if not isinstance(draft, Mapping):
        raise ControlPlaneContractError("mission document must be a mapping")
    document: dict[str, Any] = copy.deepcopy(dict(draft))
    document.setdefault("schemaVersion", SCHEMA_VERSION)
    document.setdefault("version", 1)
    document.setdefault("supersedes", None)
    for key in ("nonGoals", "delegable", "reservedToHuman", "linearTicketIds"):
        document.setdefault(key, [])
    document.setdefault("status", "draft")
    at = created_at or utc_now()
    document.setdefault("createdAt", at)
    document.setdefault("updatedAt", document["createdAt"])

    if "missionId" not in document:
        # Identity binds the content to its creation instant, so two missions
        # with the same text created at different times stay distinct.
        core = {
            key: value
            for key, value in document.items()
            if key not in FINGERPRINT_EXCLUDED_FIELDS
        }
        document["missionId"] = stable_id(
            MISSION_ID_PREFIX,
            {"core": fingerprint(core), "createdAt": document["createdAt"]},
        )

    supplied_fingerprint = document.pop("fingerprint", None)
    computed = mission_fingerprint(document)
    if supplied_fingerprint is not None and supplied_fingerprint != computed:
        raise ControlPlaneContractError("mission fingerprint does not match content")
    document["fingerprint"] = computed
    return validate_mission(document)


def validate_mission(document: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deep copy of *document* after enforcing the full contract."""

    if not isinstance(document, Mapping):
        raise ControlPlaneContractError("mission document must be a mapping")
    keys = set(document)
    if keys != TOP_LEVEL_FIELDS:
        if keys - TOP_LEVEL_FIELDS:
            raise ControlPlaneContractError("mission document has unknown fields")
        raise ControlPlaneContractError("mission document is missing required fields")
    if not payload_is_safe(document):
        raise ControlPlaneContractError("mission document failed the safety boundary")
    if len(canonical_json(document).encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise ControlPlaneContractError("mission document is too large")

    if document["schemaVersion"] != SCHEMA_VERSION:
        raise ControlPlaneContractError("unsupported mission schema version")
    require_stable_id(document["missionId"], MISSION_ID_PREFIX)
    _positive_int(document["version"], "mission version")
    if document["supersedes"] is not None:
        require_stable_id(document["supersedes"], MISSION_ID_PREFIX)
        if document["supersedes"] == document["missionId"]:
            raise ControlPlaneContractError("mission cannot supersede itself")
    _text(document["title"], "mission title", MAX_TITLE_CHARS)
    for key in ("intent", "problem", "who"):
        _text(document[key], f"mission {key}", MAX_TEXT_CHARS)
    _validate_criteria(document["successCriteria"])
    for key in ("nonGoals", "delegable", "reservedToHuman"):
        _text_list(document[key], f"mission {key}")
    _validate_constraints(document["constraints"])
    _validate_workspace(document["workspace"])
    _validate_delivery(document["delivery"])
    _validate_ticket_ids(document["linearTicketIds"])
    if document["status"] not in MISSION_STATUSES:
        raise ControlPlaneContractError("invalid mission status")
    created = parse_datetime(document["createdAt"])
    updated = parse_datetime(document["updatedAt"])
    if updated < created:
        raise ControlPlaneContractError("mission updatedAt precedes createdAt")
    require_fingerprint(document["fingerprint"])
    if document["fingerprint"] != mission_fingerprint(document):
        raise ControlPlaneContractError("mission fingerprint does not match content")
    return copy.deepcopy(dict(document))


def criterion_ids(document: Mapping[str, Any]) -> list[str]:
    return [criterion["id"] for criterion in document["successCriteria"]]


def is_human_source(source_ref: Any) -> bool:
    """Only a named human channel may decide; agent-shaped refs are refused."""

    try:
        candidate = safe_identifier(source_ref)
    except ControlPlaneContractError:
        return False
    return any(
        candidate.startswith(prefix) and len(candidate) > len(prefix)
        for prefix in HUMAN_SOURCE_PREFIXES
    )


def relative_path(value: Any, *, what: str, allow_dot: bool = False) -> str:
    """A repository-relative POSIX path that cannot escape the repository."""

    if not isinstance(value, str) or not value or len(value) > MAX_PATH_CHARS:
        raise ControlPlaneContractError(f"{what} must be a relative path")
    if "\x00" in value or "\\" in value or value.startswith("~"):
        raise ControlPlaneContractError(f"{what} must be a relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        raise ControlPlaneContractError(f"{what} must not escape the repository")
    if not pure.parts and not allow_dot:
        raise ControlPlaneContractError(f"{what} must name a file or directory")
    return value


def _validate_criteria(criteria: Any) -> None:
    if not isinstance(criteria, list) or not criteria or len(criteria) > MAX_LIST_ITEMS:
        raise ControlPlaneContractError("mission needs at least one success criterion")
    seen: set[str] = set()
    for criterion in criteria:
        if not isinstance(criterion, Mapping):
            raise ControlPlaneContractError("success criterion must be a mapping")
        kind = criterion.get("kind")
        if kind not in CRITERION_KINDS:
            raise ControlPlaneContractError("success criterion has no verifiable kind")
        required, optional = CRITERION_FIELDS[kind]
        keys = set(criterion)
        base = {"id", "text", "kind"}
        if not (base | required) <= keys or not keys <= (base | required | optional):
            raise ControlPlaneContractError("success criterion fields do not match its kind")
        identifier = criterion["id"]
        if not isinstance(identifier, str) or not _CRITERION_ID.fullmatch(identifier):
            raise ControlPlaneContractError("success criterion id is invalid")
        if identifier in seen:
            raise ControlPlaneContractError("success criterion ids must be unique")
        seen.add(identifier)
        _text(criterion["text"], "success criterion text", MAX_CRITERION_TEXT_CHARS)
        if kind == "check":
            _text(criterion["command"], "check command", MAX_COMMAND_CHARS)
            if "cwd" in criterion:
                relative_path(criterion["cwd"], what="check cwd", allow_dot=True)
        elif kind == "artifact":
            relative_path(criterion["path"], what="artifact path")
            if "mustMatch" in criterion:
                pattern = criterion["mustMatch"]
                _text(pattern, "artifact pattern", MAX_REGEX_CHARS)
                try:
                    re.compile(pattern)
                except re.error as exc:
                    raise ControlPlaneContractError(
                        "artifact pattern is not a valid regular expression"
                    ) from exc
        else:
            _text(criterion["question"], "rubric question", MAX_CRITERION_TEXT_CHARS)


def _validate_constraints(constraints: Any) -> None:
    if not isinstance(constraints, Mapping) or set(constraints) != CONSTRAINT_FIELDS:
        raise ControlPlaneContractError("mission constraints are incomplete")
    _positive_int(constraints["maxCycles"], "maxCycles")
    _positive_int(constraints["maxTurnsPerRun"], "maxTurnsPerRun")
    budget = constraints["maxBudgetUsd"]
    if (
        isinstance(budget, bool)
        or not isinstance(budget, (int, float))
        or not math.isfinite(budget)
        or budget <= 0
    ):
        raise ControlPlaneContractError("maxBudgetUsd must be a positive number")
    for flag in ABSOLUTE_GATE_FLAGS:
        if constraints[flag] is not False:
            raise ControlPlaneContractError(
                "absolute gates cannot be opened by a mission"
            )


def _validate_workspace(workspace: Any) -> None:
    if not isinstance(workspace, Mapping) or set(workspace) != {
        "repo",
        "baseRef",
        "writeSet",
    }:
        raise ControlPlaneContractError("mission workspace is incomplete")
    repo = workspace["repo"]
    if (
        not isinstance(repo, str)
        or not repo.startswith("/")
        or len(repo) > MAX_PATH_CHARS
        or "\x00" in repo
        or ".." in PurePosixPath(repo).parts
    ):
        raise ControlPlaneContractError("workspace repo must be an absolute path")
    base_ref = workspace["baseRef"]
    if not isinstance(base_ref, str) or not _BASE_REF.fullmatch(base_ref) or ".." in base_ref:
        raise ControlPlaneContractError("workspace baseRef is invalid")
    write_set = workspace["writeSet"]
    if (
        not isinstance(write_set, list)
        or not write_set
        or len(write_set) > MAX_LIST_ITEMS
    ):
        raise ControlPlaneContractError("workspace writeSet must be a non-empty list")
    seen: set[str] = set()
    for entry in write_set:
        candidate = relative_path(entry, what="writeSet entry")
        if candidate in seen:
            raise ControlPlaneContractError("workspace writeSet entries must be unique")
        seen.add(candidate)


def _validate_delivery(delivery: Any) -> None:
    if not isinstance(delivery, Mapping) or set(delivery) != {"kind", "requireChecks"}:
        raise ControlPlaneContractError("mission delivery is incomplete")
    if delivery["kind"] not in DELIVERY_KINDS:
        raise ControlPlaneContractError("invalid delivery kind")
    if not isinstance(delivery["requireChecks"], bool):
        raise ControlPlaneContractError("delivery requireChecks must be boolean")


def _validate_ticket_ids(values: Any) -> None:
    if not isinstance(values, list) or len(values) > MAX_LIST_ITEMS:
        raise ControlPlaneContractError("linearTicketIds must be a list")
    for value in values:
        if not isinstance(value, str) or not _LINEAR_TICKET.fullmatch(value):
            raise ControlPlaneContractError("linearTicketIds entries are invalid")
    if len(set(values)) != len(values):
        raise ControlPlaneContractError("linearTicketIds entries must be unique")


def _text(value: Any, what: str, limit: int) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ControlPlaneContractError(f"{what} must be non-empty text within limits")


def _text_list(values: Any, what: str) -> None:
    if not isinstance(values, list) or len(values) > MAX_LIST_ITEMS:
        raise ControlPlaneContractError(f"{what} must be a list of text")
    for value in values:
        _text(value, what, MAX_CRITERION_TEXT_CHARS)


def _positive_int(value: Any, what: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ControlPlaneContractError(f"{what} must be a positive integer")
