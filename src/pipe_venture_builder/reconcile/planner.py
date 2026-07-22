"""Pure reconciliation planner for ProductBaseline and ExternalSnapshot values."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
STALE_AFTER = timedelta(hours=24)
MUTATING_ACTIONS = frozenset({"create", "update", "link"})
INCOMPLETE_STATUSES = frozenset(
    {"partial", "unavailable", "unauthorized", "rate_limited", "failed", "blocked"}
)
EXTERNAL_ARTIFACT_TARGETS = {
    "product_requirement": "linear",
    "feature": "linear",
    "epic": "linear",
    "ticket": "linear",
}
TARGET_SYSTEMS = frozenset({"linear", "github", "repository"})
ACTION_TYPES = frozenset({"create", "update", "link", "ignore", "investigate"})
MATCH_STRATEGIES = frozenset(
    {
        "explicit_reference",
        "stable_external_id",
        "git_relationship",
        "semantic_candidate",
        "manual",
    }
)
CONFIDENCE_LEVELS = frozenset({"low", "medium", "high"})


class PlanningContractError(ValueError):
    """Raised when an input is not a safe canonical planning document."""


@dataclass(frozen=True, slots=True)
class Intent:
    source_artifact_ids: tuple[str, ...]
    target_system: str
    action_type: str
    target_ref: str | None
    seed_match_strategy: str
    seed_confidence: str


@dataclass(frozen=True, slots=True)
class Match:
    strategy: str
    confidence: str
    records: tuple[Mapping[str, Any], ...]
    reason: str


def plan_reconciliation(
    baseline: Mapping[str, Any],
    snapshots: Sequence[Mapping[str, Any]],
    *,
    verification_snapshots: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Return a stable plan without invoking adapters or mutating any input.

    ``verification_snapshots`` are optional second reads. A difference between an
    observed target and its verification snapshot blocks the affected proposal.
    """

    _validate_baseline(baseline)
    observed = _validate_snapshots(snapshots, role="observed")
    verification = _validate_snapshots(verification_snapshots, role="verification")
    artifacts = {
        artifact["artifactId"]: artifact for artifact in baseline.get("artifacts", [])
    }
    conflict_artifacts = _conflict_artifact_ids(baseline)
    intents = _build_intents(baseline, artifacts)
    snapshot_refs = _snapshot_references(observed, "observed") + _snapshot_references(
        verification, "verification"
    )

    actions: list[dict[str, Any]] = []
    blockers_by_id: dict[str, dict[str, Any]] = {}
    for intent in intents:
        action, blockers = _plan_intent(
            intent,
            baseline=baseline,
            artifacts=artifacts,
            conflict_artifacts=conflict_artifacts,
            observed=observed,
            verification=verification,
        )
        actions.append(action)
        for blocker in blockers:
            blockers_by_id[blocker["blockerId"]] = blocker

    actions.sort(key=lambda item: (item["idempotencyKey"], item["actionId"]))
    blockers = sorted(
        blockers_by_id.values(), key=lambda item: (item["type"], item["blockerId"])
    )
    source_times = [baseline["generatedAt"]] + [
        snapshot["capturedAt"] for snapshot in observed + verification
    ]
    generated_at = max(source_times, key=_parse_time)
    baseline_ref = {
        "baselineId": baseline["baselineId"],
        "generatedAt": baseline["generatedAt"],
        "fingerprint": _fingerprint(baseline),
    }
    identity = {
        "baseline": baseline_ref,
        "snapshots": snapshot_refs,
        "actions": actions,
        "blockers": blockers,
    }
    summary = {
        "total": len(actions),
        "proposed": sum(action["status"] == "proposed" for action in actions),
        "blocked": sum(action["status"] == "blocked" for action in actions),
        "alreadySatisfied": sum(
            action["status"] == "already_satisfied" for action in actions
        ),
        "investigate": sum(action["actionType"] == "investigate" for action in actions),
    }
    if blockers:
        status = "blocked"
    elif actions:
        status = "ready_for_review"
    else:
        status = "no_changes"
    return {
        "schemaVersion": SCHEMA_VERSION,
        "planId": _stable_id("RP", identity),
        "generatedAt": generated_at,
        "baseline": baseline_ref,
        "snapshots": snapshot_refs,
        "status": status,
        "summary": summary,
        "actions": actions,
        "blockers": blockers,
        "constraints": {
            "planOnly": True,
            "externalMutationPerformed": False,
            "mutationSurfaceExposed": False,
            "semanticMatchesAutoConfirmed": False,
            "destructiveActionsAllowed": False,
        },
    }


def _build_intents(
    baseline: Mapping[str, Any], artifacts: Mapping[str, Mapping[str, Any]]
) -> list[Intent]:
    seeds = baseline.get("reconciliationPlan", [])
    intents: list[Intent] = []
    if seeds:
        for seed in seeds:
            _validate_seed(seed)
            source_ids = tuple(sorted(set(seed.get("sourceArtifactIds", []))))
            if not source_ids or any(source_id not in artifacts for source_id in source_ids):
                raise PlanningContractError(
                    "reconciliation intent references an unknown source artifact"
                )
            intents.append(
                Intent(
                    source_artifact_ids=source_ids,
                    target_system=seed["targetSystem"],
                    action_type=seed["actionType"],
                    target_ref=seed.get("targetRef"),
                    seed_match_strategy=seed["matchStrategy"],
                    seed_confidence=seed["confidence"],
                )
            )
    else:
        for artifact in sorted(artifacts.values(), key=lambda item: item["artifactId"]):
            target_system = _external_ref_system(artifact.get("externalRef"))
            if target_system:
                intents.append(
                    Intent(
                        (artifact["artifactId"],),
                        target_system,
                        "link",
                        artifact["externalRef"],
                        "explicit_reference",
                        "high",
                    )
                )
                continue
            target_system = EXTERNAL_ARTIFACT_TARGETS.get(artifact["artifactType"])
            if target_system and artifact["status"] != "superseded":
                intents.append(
                    Intent(
                        (artifact["artifactId"],),
                        target_system,
                        "create",
                        None,
                        "manual",
                        "high",
                    )
                )
    unique: dict[tuple[Any, ...], Intent] = {}
    for intent in intents:
        key = (
            intent.target_system,
            intent.action_type,
            intent.target_ref,
            intent.source_artifact_ids,
        )
        unique[key] = intent
    return sorted(
        unique.values(),
        key=lambda item: (
            item.target_system,
            item.source_artifact_ids,
            item.action_type,
            item.target_ref or "",
        ),
    )


def _plan_intent(
    intent: Intent,
    *,
    baseline: Mapping[str, Any],
    artifacts: Mapping[str, Mapping[str, Any]],
    conflict_artifacts: set[str],
    observed: list[Mapping[str, Any]],
    verification: list[Mapping[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source_artifacts = [artifacts[source_id] for source_id in intent.source_artifact_ids]
    candidates = _candidate_snapshots(intent.target_system, baseline, observed)
    container_id = _container_id(intent.target_system, baseline, candidates)
    records = tuple(record for snapshot in candidates for record in snapshot["records"])
    match = _match(intent, source_artifacts, records)
    snapshot_ids = sorted(snapshot["snapshotId"] for snapshot in candidates)
    target_record_ids = sorted(record["recordId"] for record in match.records)
    blockers: list[dict[str, Any]] = []

    if intent.target_system != "repository" and not candidates:
        blockers.append(
            _blocker(
                "unavailable_source",
                intent.source_artifact_ids,
                (),
                (),
            )
        )
    for snapshot in candidates:
        if snapshot["status"] in INCOMPLETE_STATUSES and intent.action_type in MUTATING_ACTIONS:
            blockers.append(
                _blocker(
                    "unavailable_source",
                    intent.source_artifact_ids,
                    target_record_ids,
                    (snapshot["snapshotId"],),
                )
            )
        if _is_stale(snapshot["capturedAt"], baseline["generatedAt"]):
            blockers.append(
                _blocker(
                    "stale_snapshot",
                    intent.source_artifact_ids,
                    target_record_ids,
                    (snapshot["snapshotId"],),
                )
            )
    if len(match.records) > 1:
        blocker_type = (
            "duplicate_target"
            if match.strategy != "semantic_candidate"
            else "ambiguous_match"
        )
        blockers.append(
            _blocker(
                blocker_type,
                intent.source_artifact_ids,
                target_record_ids,
                tuple(snapshot_ids),
            )
        )
    if any(source_id in conflict_artifacts for source_id in intent.source_artifact_ids):
        blockers.append(
            _blocker(
                "source_conflict",
                intent.source_artifact_ids,
                target_record_ids,
                tuple(snapshot_ids),
            )
        )
    if candidates and _target_changed(
        candidates, verification, match.records, intent, source_artifacts
    ):
        verification_ids = tuple(
            snapshot["snapshotId"]
            for snapshot in verification
            if _same_container_set(snapshot, candidates)
        )
        blockers.append(
            _blocker(
                "changed_target",
                intent.source_artifact_ids,
                target_record_ids,
                tuple(sorted(set(snapshot_ids).union(verification_ids))),
            )
        )

    action_type, status, reason = _disposition(intent, match, blockers)
    blocker_ids = sorted({blocker["blockerId"] for blocker in blockers})
    target_fingerprint = (
        _fingerprint([_record_state(record) for record in match.records])
        if match.records
        else None
    )
    intent_discriminator = _fingerprint(
        {
            "actionType": intent.action_type,
            "targetRef": intent.target_ref,
            "sourceArtifactIds": intent.source_artifact_ids,
        }
    ).split(":", 1)[1][:16]
    entity_type = (
        f"{source_artifacts[0]['artifactType']}.{intent.action_type}."
        f"{intent_discriminator}"
    )
    idempotency_key = (
        f"{intent.target_system}:{_key_part(container_id)}:{_key_part(entity_type)}:"
        f"{intent.source_artifact_ids[0]}:v1"
    )
    identity = {
        "idempotencyKey": idempotency_key,
        "actionType": action_type,
        "sourceArtifactIds": intent.source_artifact_ids,
        "targetRecordIds": target_record_ids,
    }
    return (
        {
            "actionId": _stable_id("RA", identity),
            "idempotencyKey": idempotency_key,
            "targetSystem": intent.target_system,
            "targetContainerId": container_id,
            "actionType": action_type,
            "status": status,
            "sourceArtifactIds": list(intent.source_artifact_ids),
            "targetRecordIds": target_record_ids,
            "snapshotIds": snapshot_ids,
            "matchStrategy": match.strategy,
            "confidence": match.confidence,
            "targetFingerprint": target_fingerprint,
            "reason": reason,
            "expectedEffect": _expected_effect(action_type),
            "approvalRequired": action_type in MUTATING_ACTIONS,
            "reviewRequired": True,
            "blockerIds": blocker_ids,
        },
        blockers,
    )


def _match(
    intent: Intent,
    artifacts: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
) -> Match:
    explicit_refs = {
        ref
        for ref in [intent.target_ref, *(artifact.get("externalRef") for artifact in artifacts)]
        if ref
    }
    exact = tuple(record for record in records if _record_references(record) & explicit_refs)
    if exact:
        return Match(
            "explicit_reference",
            "high",
            _unique_records(exact),
            "A declared external reference resolved to one record.",
        )

    stable_refs = {
        artifact.get("sourceRef")
        for artifact in artifacts
        if artifact.get("sourceRef")
    }
    exact = tuple(
        record
        for record in records
        if {record["sourceId"], record["sourceKey"]} & stable_refs
    )
    if exact:
        return Match(
            "stable_external_id",
            "high",
            _unique_records(exact),
            "A stable source identifier resolved to one record.",
        )

    if intent.target_system == "github":
        exact = tuple(
            record for record in records if _git_references(record) & stable_refs
        )
        if exact:
            return Match(
                "git_relationship",
                "high",
                _unique_records(exact),
                "A Git branch or commit identifier resolved to one record.",
            )

    titles = {_normalize_title(artifact["title"]) for artifact in artifacts}
    semantic = tuple(
        record
        for record in records
        if record.get("title")
        and _semantic_record_allowed(intent.target_system, record)
        and _normalize_title(record["title"]) in titles
    )
    if semantic:
        reason = (
            "A title-only candidate requires human confirmation."
            if len(semantic) == 1
            else "Multiple external records are plausible matches."
        )
        return Match("semantic_candidate", "low", _unique_records(semantic), reason)

    return Match(intent.seed_match_strategy, intent.seed_confidence, (), "")


def _disposition(
    intent: Intent, match: Match, blockers: Sequence[Mapping[str, Any]]
) -> tuple[str, str, str]:
    blocker_types = {blocker["type"] for blocker in blockers}
    if "changed_target" in blocker_types:
        return (
            "investigate",
            "blocked",
            "The observed target differs from the verification snapshot.",
        )
    if "stale_snapshot" in blocker_types:
        return "investigate", "blocked", "The observed snapshot is too old for a safe proposal."
    if "unavailable_source" in blocker_types:
        return "investigate", "blocked", "The source inventory is incomplete or unavailable."
    if "source_conflict" in blocker_types:
        return "investigate", "blocked", "Source evidence contains an unresolved conflict."
    if len(match.records) > 1:
        reason = (
            match.reason
            if match.strategy == "semantic_candidate"
            else "An exact identity resolved to multiple external records."
        )
        return "investigate", "blocked", reason
    if match.confidence == "low":
        reason = match.reason or "The baseline declares a manual reconciliation intent."
        return "investigate", "proposed", reason
    if match.strategy == "semantic_candidate" and match.records:
        return "investigate", "proposed", match.reason
    if intent.target_system == "repository":
        return (
            intent.action_type,
            "proposed",
            match.reason or "The baseline declares a manual reconciliation intent.",
        )
    if len(match.records) == 1:
        artifact_already_linked = intent.target_ref is not None
        if intent.action_type == "create" or (
            intent.action_type == "link" and artifact_already_linked
        ):
            return (
                "ignore",
                "already_satisfied",
                "The declared relationship is already represented.",
            )
        return intent.action_type, "proposed", match.reason
    if intent.target_ref or intent.action_type in {"update", "link"}:
        return (
            "investigate",
            "blocked",
            "The declared target was not present in the observed snapshot.",
        )
    if intent.action_type == "create":
        return "create", "proposed", "No external record matched the declared create intent."
    return "investigate", "proposed", "The baseline declares a manual reconciliation intent."


def _expected_effect(action_type: str) -> str:
    return {
        "create": "Create one missing external record after approval.",
        "update": "Update one confirmed external record after approval.",
        "link": "Link one source artifact to one confirmed external record after approval.",
        "ignore": "Record that no external change is needed.",
        "investigate": "Resolve the candidate or blocker before any external change.",
    }[action_type]


def _blocker(
    blocker_type: str,
    source_artifact_ids: Iterable[str],
    target_record_ids: Iterable[str],
    snapshot_ids: Iterable[str],
) -> dict[str, Any]:
    descriptions = {
        "stale_snapshot": (
            "The observed snapshot predates the baseline by more than the allowed "
            "planning window."
        ),
        "changed_target": "The target changed after the observed snapshot was captured.",
        "duplicate_target": "More than one record has the same exact external identity.",
        "ambiguous_match": "More than one record is a plausible semantic match.",
        "unavailable_source": "The source inventory is incomplete or unavailable for this action.",
        "source_conflict": "The source artifact depends on an unresolved conflict.",
    }
    severities = {
        "stale_snapshot": "P2",
        "changed_target": "P1",
        "duplicate_target": "P1",
        "ambiguous_match": "P2",
        "unavailable_source": "P1",
        "source_conflict": "P1",
    }
    identity = {
        "type": blocker_type,
        "sourceArtifactIds": sorted(set(source_artifact_ids)),
        "targetRecordIds": sorted(set(target_record_ids)),
        "snapshotIds": sorted(set(snapshot_ids)),
    }
    return {
        "blockerId": _stable_id("RB", identity),
        "type": blocker_type,
        "severity": severities[blocker_type],
        "description": descriptions[blocker_type],
        "sourceArtifactIds": identity["sourceArtifactIds"],
        "targetRecordIds": identity["targetRecordIds"],
        "snapshotIds": identity["snapshotIds"],
        "reviewRequired": True,
    }


def _target_changed(
    observed: Sequence[Mapping[str, Any]],
    verification: Sequence[Mapping[str, Any]],
    matched_records: Sequence[Mapping[str, Any]],
    intent: Intent,
    artifacts: Sequence[Mapping[str, Any]],
) -> bool:
    relevant_verification = [
        candidate
        for candidate in verification
        if _same_container_set(candidate, observed)
        and _parse_time(candidate["capturedAt"])
        > max(_parse_time(snapshot["capturedAt"]) for snapshot in observed)
    ]
    if not relevant_verification:
        return False
    observed_by_source = {record["sourceId"]: record for record in matched_records}
    verification_records = tuple(
        record for snapshot in relevant_verification for record in snapshot["records"]
    )
    if observed_by_source:
        current_by_source = {record["sourceId"]: record for record in verification_records}
        return any(
            source_id not in current_by_source
            or _fingerprint(_record_state(record))
            != _fingerprint(_record_state(current_by_source[source_id]))
            for source_id, record in observed_by_source.items()
        )
    if intent.action_type == "create":
        return bool(_match(intent, artifacts, verification_records).records)
    return False


def _candidate_snapshots(
    target_system: str,
    baseline: Mapping[str, Any],
    snapshots: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    if target_system == "repository":
        return []
    candidates = [snapshot for snapshot in snapshots if snapshot["sourceSystem"] == target_system]
    system_ref = baseline.get("systems", {}).get(target_system)
    if system_ref:
        identifier = system_ref.get("identifier")
        selected = [
            snapshot
            for snapshot in candidates
            if snapshot["sourceContainer"]["id"] == identifier
        ]
        if selected:
            return sorted(selected, key=lambda item: item["snapshotId"])
        return []
    if len(candidates) > 1:
        return []
    return sorted(candidates, key=lambda item: item["snapshotId"])


def _container_id(
    target_system: str,
    baseline: Mapping[str, Any],
    snapshots: Sequence[Mapping[str, Any]],
) -> str:
    if len(snapshots) == 1:
        return snapshots[0]["sourceContainer"]["id"]
    system_ref = baseline.get("systems", {}).get(target_system)
    if system_ref:
        return _key_part(system_ref["identifier"])
    if target_system == "repository":
        return "repository"
    return "unresolved"


def _conflict_artifact_ids(baseline: Mapping[str, Any]) -> set[str]:
    conflict_statements = {
        statement["statementId"]
        for statement in baseline.get("statements", [])
        if statement["classification"] == "conflict"
        or statement["disposition"] in {"resolve_conflict", "blocked"}
    }
    artifact_ids = {
        artifact["artifactId"]
        for artifact in baseline.get("artifacts", [])
        if artifact["status"] == "conflicting"
        or conflict_statements.intersection(artifact["provenanceStatementIds"])
    }
    for gap in baseline.get("governanceGaps", []):
        if gap["status"] == "blocked" or (
            gap["status"] == "open" and gap["severity"] in {"P0", "P1"}
        ):
            artifact_ids.update(gap["affectedArtifactIds"])
    return artifact_ids


def _snapshot_references(
    snapshots: Sequence[Mapping[str, Any]], role: str
) -> list[dict[str, Any]]:
    return sorted(
        (
            {
                "role": role,
                "snapshotId": snapshot["snapshotId"],
                "sourceSystem": snapshot["sourceSystem"],
                "sourceContainerId": snapshot["sourceContainer"]["id"],
                "capturedAt": snapshot["capturedAt"],
                "status": snapshot["status"],
                "fingerprint": _fingerprint(snapshot),
            }
            for snapshot in snapshots
        ),
        key=lambda item: (
            item["role"],
            item["sourceSystem"],
            item["sourceContainerId"],
            item["snapshotId"],
        ),
    )


def _validate_baseline(baseline: Mapping[str, Any]) -> None:
    if not isinstance(baseline, Mapping):
        raise PlanningContractError("baseline must be a mapping")
    required = {
        "schemaVersion",
        "baselineId",
        "generatedAt",
        "systems",
        "artifacts",
        "reconciliationPlan",
    }
    if not required.issubset(baseline):
        raise PlanningContractError("baseline is missing required planning fields")
    if baseline["schemaVersion"] != SCHEMA_VERSION:
        raise PlanningContractError("unsupported ProductBaseline schema version")
    _parse_time(baseline["generatedAt"])
    systems = baseline["systems"]
    if not isinstance(systems, Mapping):
        raise PlanningContractError("baseline systems must be a mapping")
    repository = systems.get("repository")
    if not isinstance(repository, Mapping) or not isinstance(
        repository.get("identifier"), str
    ):
        raise PlanningContractError("baseline repository system is invalid")
    if not isinstance(baseline["artifacts"], list) or not isinstance(
        baseline["reconciliationPlan"], list
    ):
        raise PlanningContractError("baseline planning collections must be arrays")


def _validate_seed(seed: Mapping[str, Any]) -> None:
    if not isinstance(seed, Mapping):
        raise PlanningContractError("reconciliation intent must be a mapping")
    if seed.get("targetSystem") not in TARGET_SYSTEMS:
        raise PlanningContractError("reconciliation intent has an invalid target system")
    if seed.get("actionType") not in ACTION_TYPES:
        raise PlanningContractError("reconciliation intent has an invalid action type")
    if seed.get("matchStrategy") not in MATCH_STRATEGIES:
        raise PlanningContractError("reconciliation intent has an invalid match strategy")
    if seed.get("confidence") not in CONFIDENCE_LEVELS:
        raise PlanningContractError("reconciliation intent has an invalid confidence")
    source_ids = seed.get("sourceArtifactIds")
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or any(not isinstance(source_id, str) for source_id in source_ids)
    ):
        raise PlanningContractError(
            "reconciliation intent source artifact IDs must be a non-empty text array"
        )
    target_ref = seed.get("targetRef")
    if target_ref is not None and not isinstance(target_ref, str):
        raise PlanningContractError("reconciliation target reference must be text or null")


def _validate_snapshots(
    snapshots: Sequence[Mapping[str, Any]], *, role: str
) -> list[Mapping[str, Any]]:
    if isinstance(snapshots, (str, bytes)) or not isinstance(snapshots, Sequence):
        raise PlanningContractError(f"{role} snapshots must be a sequence")
    validated: list[Mapping[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for snapshot in snapshots:
        if not isinstance(snapshot, Mapping):
            raise PlanningContractError(f"{role} snapshot must be a mapping")
        required = {
            "schemaVersion",
            "snapshotId",
            "sourceSystem",
            "sourceContainer",
            "capturedAt",
            "status",
            "records",
            "constraints",
        }
        if not required.issubset(snapshot):
            raise PlanningContractError(f"{role} snapshot is missing required fields")
        if snapshot["schemaVersion"] != SCHEMA_VERSION:
            raise PlanningContractError("unsupported ExternalSnapshot schema version")
        constraints = snapshot["constraints"]
        if not isinstance(constraints, Mapping):
            raise PlanningContractError("snapshot constraints must be a mapping")
        if (
            constraints.get("readOnly") is not True
            or constraints.get("mutationSurfaceExposed") is not False
        ):
            raise PlanningContractError("snapshot does not preserve the read-only boundary")
        if not isinstance(snapshot["records"], list):
            raise PlanningContractError("snapshot records must be an array")
        _parse_time(snapshot["capturedAt"])
        identity = (snapshot["sourceSystem"], snapshot["sourceContainer"]["id"])
        if identity in identities:
            raise PlanningContractError(f"duplicate {role} snapshot container")
        identities.add(identity)
        validated.append(snapshot)
    return sorted(
        validated,
        key=lambda item: (
            item["sourceSystem"],
            item["sourceContainer"]["id"],
            item["snapshotId"],
        ),
    )


def _record_references(record: Mapping[str, Any]) -> set[str]:
    return {
        value
        for value in (
            record.get("sourceId"),
            record.get("sourceKey"),
            record.get("url"),
        )
        if value
    }


def _git_references(record: Mapping[str, Any]) -> set[str]:
    attributes = record.get("attributes", {})
    return {
        value
        for key in ("headBranch", "headSha", "mergeCommitSha", "tag")
        if (value := attributes.get(key))
    }


def _record_state(record: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "observedAt"}


def _same_container_set(
    candidate: Mapping[str, Any], snapshots: Sequence[Mapping[str, Any]]
) -> bool:
    return any(
        candidate["sourceSystem"] == snapshot["sourceSystem"]
        and candidate["sourceContainer"]["id"] == snapshot["sourceContainer"]["id"]
        for snapshot in snapshots
    )


def _is_stale(captured_at: str, baseline_generated_at: str) -> bool:
    return _parse_time(baseline_generated_at) - _parse_time(captured_at) > STALE_AFTER


def _parse_time(value: str) -> datetime:
    try:
        candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(candidate)
    except (AttributeError, ValueError) as exc:
        raise PlanningContractError("planning timestamps must be RFC 3339 date-times") from exc
    if parsed.tzinfo is None:
        raise PlanningContractError("planning timestamps must include a timezone")
    return parsed


def _normalize_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[^\W_]+", normalized, flags=re.UNICODE))


def _semantic_record_allowed(
    target_system: str, record: Mapping[str, Any]
) -> bool:
    if target_system == "linear":
        return record.get("entityType") == "issue"
    if target_system == "github":
        return record.get("entityType") in {"issue", "pull_request", "release"}
    return False


def _external_ref_system(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    lowered = value.lower()
    if lowered.startswith("linear:") or "linear.app/" in lowered:
        return "linear"
    if lowered.startswith("github:") or "github.com/" in lowered:
        return "github"
    return None


def _unique_records(records: Iterable[Mapping[str, Any]]) -> tuple[Mapping[str, Any], ...]:
    unique = {record["recordId"]: record for record in records}
    return tuple(unique[key] for key in sorted(unique))


def _key_part(value: Any) -> str:
    candidate = re.sub(r"[^A-Za-z0-9._:/+=-]+", "-", str(value)).strip("-")
    return candidate or "unresolved"


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return f"sha256:{hashlib.sha256(encoded.encode('utf-8')).hexdigest()}"


def _stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}-{_fingerprint(value).split(':', 1)[1][:12]}"
