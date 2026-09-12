"""Program contract v0.1.0: a dor em ondas de missões (PIP-910).

A Program chains Mission-shaped stages behind a verifiable gate
(``startWhen``), never merging anything itself. This module only builds and
validates the Program document — identity and fingerprint the same way
``mission.contract.build_mission`` does for a Mission. The loop that turns a
validated Program into running missions is ``program_supervisor.py``; the
durable store is ``MissionStore`` (``store.py``).

Heavy reuse of ``mission.contract`` on purpose (PIP-910 review criterion:
"reaproveita o que existe, não duplica"): a stage's ``missionDraft`` is a
Mission document missing only ``missionId``/``status``/timestamps/
``fingerprint`` and ``workspace.baseRef`` (the Program resolves the base by
branch chaining — see ``program_supervisor._resolve_stage_base``), so its
validation calls straight into ``contract``'s private helpers instead of
re-implementing them.
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
    stable_id,
    utc_now,
)

from .contract import (
    CRITERION_FIELDS,
    EXECUTOR_KIND_LOCAL,
    EXECUTOR_KINDS,
    MAX_COMMAND_CHARS,
    MAX_CRITERION_TEXT_CHARS,
    MAX_LIST_ITEMS,
    MAX_PATH_CHARS,
    MAX_REGEX_CHARS,
    MAX_TEXT_CHARS,
    MAX_TITLE_CHARS,
    MISSION_ID_PREFIX,
    PROGRAM_ID_PREFIX_RAW,
    STAGE_ID_PATTERN,
    SUPPORTED_SCHEMA_VERSIONS,
    TOP_LEVEL_FIELDS,
    _BASE_REF,
    _CRITERION_ID,
    _text,
    _text_list,
    _validate_constraints,
    _validate_criteria,
    _validate_delegation,
    _validate_delivery,
    _validate_ticket_ids,
    relative_path,
)


SCHEMA_VERSION = "0.1.0"
# Dash-included, per the PIP-910 contract (``build_program(...)["programId"]
# .startswith(PROGRAM_ID_PREFIX)``); ``PROGRAM_ID_PREFIX_RAW`` (no dash, in
# ``contract.py``) is what ``stable_id``/``require_stable_id`` take.
PROGRAM_ID_PREFIX = f"{PROGRAM_ID_PREFIX_RAW}-"

PROGRAM_STATUSES = frozenset(
    {"draft", "active", "paused", "blocked", "completed", "cancelled"}
)
# ``startWhen``/``doneWhen`` are verified mechanically, from outside, before a
# mission is even created (or before the program is declared done) — a
# ``rubric`` needs a model's judgement, which has nothing to check against yet.
STAGE_CRITERION_KINDS = frozenset({"check", "artifact"})
MAX_DOCUMENT_BYTES = 64 * 1024
MAX_STAGES = 64
EXECUTION_FIELDS = frozenset({"workerModel", "reviewerModel", "executor"})

PROGRAM_TOP_LEVEL_FIELDS = frozenset(
    {
        "schemaVersion",
        "programId",
        "version",
        "supersedes",
        "objective",
        "doneWhen",
        "workspace",
        "constraints",
        "stages",
        "status",
        "createdAt",
        "updatedAt",
        "fingerprint",
    }
)
FINGERPRINT_EXCLUDED_FIELDS = frozenset({"status", "createdAt", "updatedAt", "fingerprint"})

STAGE_ALLOWED_FIELDS = frozenset(
    {"id", "missionDraft", "dependsOn", "startWhen", "requiresFounder", "execution", "chainFrom"}
)
STAGE_REQUIRED_FIELDS = STAGE_ALLOWED_FIELDS - {"chainFrom"}

# A stage's ``missionDraft``: every Mission field except the ones the Program
# (``missionId``/``status``/timestamps/``fingerprint``) or its supervisor
# (``workspace.baseRef``, resolved by branch chaining; ``program``, stamped
# once the stage's mission is created) fills in later — a draft can never set
# ``program`` itself, the same way it can never set ``missionId``.
MISSION_DRAFT_ALLOWED_FIELDS = TOP_LEVEL_FIELDS - {
    "missionId", "status", "createdAt", "updatedAt", "fingerprint", "program",
}
MISSION_DRAFT_REQUIRED_FIELDS = MISSION_DRAFT_ALLOWED_FIELDS - {"delegation"}


def program_fingerprint(document: Mapping[str, Any]) -> str:
    """Fingerprint the document without status, timestamps, or its own hash."""

    if not isinstance(document, Mapping):
        raise ControlPlaneContractError("program document must be a mapping")
    core = {key: value for key, value in document.items() if key not in FINGERPRINT_EXCLUDED_FIELDS}
    return fingerprint(core)


def build_program(draft: Mapping[str, Any], *, created_at: str | None = None) -> dict[str, Any]:
    """Complete a founder-authored Program draft into a validated document.

    Mirrors ``mission.contract.build_mission``: bookkeeping fields
    (``programId``, ``status``, timestamps, ``fingerprint``) are filled when
    absent and checked when present.
    """

    if not isinstance(draft, Mapping):
        raise ControlPlaneContractError("program document must be a mapping")
    document: dict[str, Any] = copy.deepcopy(dict(draft))
    document.setdefault("schemaVersion", SCHEMA_VERSION)
    document.setdefault("version", 1)
    document.setdefault("supersedes", None)
    document.setdefault("status", "draft")
    at = created_at or utc_now()
    document.setdefault("createdAt", at)
    document.setdefault("updatedAt", document["createdAt"])

    if "programId" not in document:
        core = {key: value for key, value in document.items() if key not in FINGERPRINT_EXCLUDED_FIELDS}
        document["programId"] = stable_id(PROGRAM_ID_PREFIX_RAW, {"core": fingerprint(core)})

    supplied_fingerprint = document.pop("fingerprint", None)
    computed = program_fingerprint(document)
    if supplied_fingerprint is not None and supplied_fingerprint != computed:
        raise ControlPlaneContractError("program fingerprint does not match content")
    document["fingerprint"] = computed
    return validate_program(document)


def validate_program(document: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deep copy of *document* after enforcing the full contract."""

    if not isinstance(document, Mapping):
        raise ControlPlaneContractError("program document must be a mapping")
    keys = set(document)
    if keys - PROGRAM_TOP_LEVEL_FIELDS:
        raise ControlPlaneContractError("program document has unknown fields")
    if PROGRAM_TOP_LEVEL_FIELDS - keys:
        raise ControlPlaneContractError("program document is missing required fields")
    if not payload_is_safe(document):
        raise ControlPlaneContractError("program document failed the safety boundary")
    if len(canonical_json(document).encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise ControlPlaneContractError("program document is too large")

    if document["schemaVersion"] != SCHEMA_VERSION:
        raise ControlPlaneContractError("unsupported program schema version")
    require_stable_id(document["programId"], PROGRAM_ID_PREFIX_RAW)
    _positive_int(document["version"], "program version")
    if document["supersedes"] is not None:
        require_stable_id(document["supersedes"], PROGRAM_ID_PREFIX_RAW)
        if document["supersedes"] == document["programId"]:
            raise ControlPlaneContractError("program cannot supersede itself")
    _text(document["objective"], "program objective", MAX_TEXT_CHARS)
    _validate_stage_criteria(document["doneWhen"], what="program doneWhen")
    _validate_program_workspace(document["workspace"])
    _validate_program_constraints(document["constraints"])
    _validate_stages(document["stages"])
    if document["status"] not in PROGRAM_STATUSES:
        raise ControlPlaneContractError("invalid program status")
    created = parse_datetime(document["createdAt"])
    updated = parse_datetime(document["updatedAt"])
    if updated < created:
        raise ControlPlaneContractError("program updatedAt precedes createdAt")
    require_fingerprint(document["fingerprint"])
    if document["fingerprint"] != program_fingerprint(document):
        raise ControlPlaneContractError("program fingerprint does not match content")
    return copy.deepcopy(dict(document))


def stage_by_id(program: Mapping[str, Any], stage_id: str) -> dict[str, Any]:
    for stage in program["stages"]:
        if stage["id"] == stage_id:
            return stage
    raise ControlPlaneContractError("program has no stage with this id")


def chain_from_stage_id(stage: Mapping[str, Any]) -> str | None:
    """The dependency a stage's mission branches from, or ``None`` for a
    first-wave stage (which branches from the program's own ``baseRef``)."""

    depends_on = stage["dependsOn"]
    if not depends_on:
        return None
    return stage.get("chainFrom") or depends_on[0]


# -- workspace / constraints ----------------------------------------------------


def _validate_program_workspace(workspace: Any) -> None:
    if not isinstance(workspace, Mapping) or set(workspace) != {"repo", "baseRef"}:
        raise ControlPlaneContractError("program workspace is incomplete")
    repo = workspace["repo"]
    if (
        not isinstance(repo, str)
        or not repo.startswith("/")
        or len(repo) > MAX_PATH_CHARS
        or "\x00" in repo
        or ".." in PurePosixPath(repo).parts
    ):
        raise ControlPlaneContractError("program workspace repo must be an absolute path")
    base_ref = workspace["baseRef"]
    if not isinstance(base_ref, str) or not _BASE_REF.fullmatch(base_ref) or ".." in base_ref:
        raise ControlPlaneContractError("program workspace baseRef is invalid")


def _validate_program_constraints(constraints: Any) -> None:
    if not isinstance(constraints, Mapping) or set(constraints) != {"maxBudgetUsd"}:
        raise ControlPlaneContractError("program constraints are incomplete")
    budget = constraints["maxBudgetUsd"]
    if (
        isinstance(budget, bool)
        or not isinstance(budget, (int, float))
        or not math.isfinite(budget)
        or budget <= 0
    ):
        raise ControlPlaneContractError("program maxBudgetUsd must be a positive number")


# -- stages ----------------------------------------------------------------------


def _validate_stages(stages: Any) -> None:
    if not isinstance(stages, list) or not stages or len(stages) > MAX_STAGES:
        raise ControlPlaneContractError("program needs at least one stage")
    declared: set[str] = set()
    for stage in stages:
        if not isinstance(stage, Mapping):
            raise ControlPlaneContractError("program stage must be a mapping")
        keys = set(stage)
        if keys - STAGE_ALLOWED_FIELDS:
            raise ControlPlaneContractError("program stage has unknown fields")
        if STAGE_REQUIRED_FIELDS - keys:
            raise ControlPlaneContractError("program stage is missing required fields")
        stage_id = stage["id"]
        if not isinstance(stage_id, str) or not STAGE_ID_PATTERN.fullmatch(stage_id):
            raise ControlPlaneContractError("program stage id is invalid")
        if stage_id in declared:
            raise ControlPlaneContractError("program stage ids must be unique")

        depends_on = stage["dependsOn"]
        if (
            not isinstance(depends_on, list)
            or len(depends_on) > MAX_STAGES
            or len(set(depends_on)) != len(depends_on)
        ):
            raise ControlPlaneContractError("program stage dependsOn is invalid")
        for dependency in depends_on:
            # Only a stage declared *before* this one may be depended on: this
            # single rule rejects both an unknown id and a cycle (a cycle
            # always needs at least one forward reference to close).
            if not isinstance(dependency, str) or dependency not in declared:
                raise ControlPlaneContractError(
                    "program stage dependsOn references an undeclared stage"
                )

        chain_from = stage.get("chainFrom")
        if len(depends_on) > 1:
            if not isinstance(chain_from, str) or chain_from not in depends_on:
                raise ControlPlaneContractError(
                    "program stage with two or more dependencies needs chainFrom"
                )
        elif chain_from is not None and chain_from not in depends_on:
            raise ControlPlaneContractError("program stage chainFrom must be one of dependsOn")

        _validate_mission_draft(stage["missionDraft"])
        _validate_stage_criteria(stage["startWhen"], what="program stage startWhen")
        if not isinstance(stage["requiresFounder"], bool):
            raise ControlPlaneContractError("program stage requiresFounder must be boolean")
        _validate_execution(stage["execution"], stage["missionDraft"])
        declared.add(stage_id)


def _validate_execution(execution: Any, mission_draft: Mapping[str, Any]) -> None:
    if not isinstance(execution, Mapping) or set(execution) - EXECUTION_FIELDS:
        raise ControlPlaneContractError("program stage execution is invalid")
    for key in {"workerModel", "reviewerModel"} & set(execution):
        _text(execution[key], f"program stage execution {key}", MAX_TITLE_CHARS)
    if "executor" in execution:
        executor = execution["executor"]
        if executor not in EXECUTOR_KINDS:
            raise ControlPlaneContractError("program stage execution executor is not allowed")
        # Deterministic policy (PIP-911), not a prompt: a rubric criterion is
        # judged by the reviewer, and the reviewer is never local (it has no
        # executor field of its own — supervisor._review/_answer_blockers
        # hardcode ``claude``). A wave whose own successCriteria has a
        # rubric therefore cannot declare its worker executor ``local``
        # either, so the whole wave's judgement stays on a real model.
        if executor == EXECUTOR_KIND_LOCAL and _stage_has_rubric_criterion(mission_draft):
            raise ControlPlaneContractError(
                "program stage with a rubric success criterion cannot declare "
                "a local executor"
            )


def _stage_has_rubric_criterion(mission_draft: Mapping[str, Any]) -> bool:
    return any(
        isinstance(criterion, Mapping) and criterion.get("kind") == "rubric"
        for criterion in mission_draft.get("successCriteria", [])
    )


# -- missionDraft ------------------------------------------------------------


def _validate_mission_draft(draft: Any) -> None:
    if not isinstance(draft, Mapping):
        raise ControlPlaneContractError("stage missionDraft must be a mapping")
    keys = set(draft)
    if keys - MISSION_DRAFT_ALLOWED_FIELDS:
        raise ControlPlaneContractError("stage missionDraft has unknown fields")
    if MISSION_DRAFT_REQUIRED_FIELDS - keys:
        raise ControlPlaneContractError("stage missionDraft is missing required fields")
    if not payload_is_safe(draft):
        raise ControlPlaneContractError("stage missionDraft failed the safety boundary")

    if draft["schemaVersion"] not in SUPPORTED_SCHEMA_VERSIONS:
        raise ControlPlaneContractError("unsupported mission schema version in stage missionDraft")
    _positive_int(draft["version"], "stage missionDraft version")
    if draft["supersedes"] is not None:
        require_stable_id(draft["supersedes"], MISSION_ID_PREFIX)
    _text(draft["title"], "stage missionDraft title", MAX_TITLE_CHARS)
    for key in ("intent", "problem", "who"):
        _text(draft[key], f"stage missionDraft {key}", MAX_TEXT_CHARS)
    _validate_stage_mission_criteria(draft["successCriteria"])
    for key in ("nonGoals", "delegable", "reservedToHuman"):
        _text_list(draft[key], f"stage missionDraft {key}")
    _validate_delegation(draft.get("delegation"), draft["schemaVersion"])
    _validate_constraints(draft["constraints"])
    _validate_mission_draft_workspace(draft["workspace"])
    _validate_delivery(draft["delivery"])
    _validate_ticket_ids(draft["linearTicketIds"])


def _validate_stage_mission_criteria(criteria: Any) -> None:
    """The stage mission's own ``successCriteria``: unlike ``startWhen``/
    ``doneWhen``, these may be any Mission criterion kind (including
    ``rubric``) — they are the stage's own worker/reviewer contract, run by
    the ordinary mission supervisor, not the Program's outside check."""

    _validate_criteria(criteria)


def _validate_mission_draft_workspace(workspace: Any) -> None:
    if not isinstance(workspace, Mapping) or set(workspace) != {"writeSet"}:
        raise ControlPlaneContractError(
            "stage missionDraft workspace must declare only writeSet; "
            "the program resolves repo and baseRef"
        )
    write_set = workspace["writeSet"]
    if not isinstance(write_set, list) or not write_set or len(write_set) > MAX_LIST_ITEMS:
        raise ControlPlaneContractError("stage missionDraft writeSet must be a non-empty list")
    seen: set[str] = set()
    for entry in write_set:
        candidate = relative_path(entry, what="writeSet entry")
        if candidate in seen:
            raise ControlPlaneContractError("stage missionDraft writeSet entries must be unique")
        seen.add(candidate)


# -- startWhen / doneWhen criteria (check/artifact only, may be empty) ----------


def _validate_stage_criteria(criteria: Any, *, what: str) -> None:
    """Unlike a mission's ``successCriteria``, ids here need not be unique:
    the same gate criterion (e.g. ``delivered(stage)``'s ``"G1"``) is often
    repeated once per dependency a multi-dependency stage's ``startWhen``
    confirms, and nothing indexes these criteria by id afterwards (no
    per-criterion evidence record, no ``criteriaSelfAssessment``)."""

    if not isinstance(criteria, list) or len(criteria) > MAX_LIST_ITEMS:
        raise ControlPlaneContractError(f"{what} must be a list of criteria")
    for criterion in criteria:
        if not isinstance(criterion, Mapping):
            raise ControlPlaneContractError(f"{what} criterion must be a mapping")
        kind = criterion.get("kind")
        if kind not in STAGE_CRITERION_KINDS:
            raise ControlPlaneContractError(f"{what} criterion has no verifiable kind")
        required, optional = CRITERION_FIELDS[kind]
        keys = set(criterion)
        base = {"id", "text", "kind"}
        if not (base | required) <= keys or not keys <= (base | required | optional):
            raise ControlPlaneContractError(f"{what} criterion fields do not match its kind")
        identifier = criterion["id"]
        if not isinstance(identifier, str) or not _CRITERION_ID.fullmatch(identifier):
            raise ControlPlaneContractError(f"{what} criterion id is invalid")
        _text(criterion["text"], f"{what} criterion text", MAX_CRITERION_TEXT_CHARS)
        if kind == "check":
            _text(criterion["command"], f"{what} check command", MAX_COMMAND_CHARS)
            if "cwd" in criterion:
                relative_path(criterion["cwd"], what=f"{what} check cwd", allow_dot=True)
        else:
            relative_path(criterion["path"], what=f"{what} artifact path")
            if "mustMatch" in criterion:
                pattern = criterion["mustMatch"]
                _text(pattern, f"{what} artifact pattern", MAX_REGEX_CHARS)
                try:
                    re.compile(pattern)
                except re.error as exc:
                    raise ControlPlaneContractError(
                        f"{what} artifact pattern is not a valid regular expression"
                    ) from exc


def _positive_int(value: Any, what: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ControlPlaneContractError(f"{what} must be a positive integer")
