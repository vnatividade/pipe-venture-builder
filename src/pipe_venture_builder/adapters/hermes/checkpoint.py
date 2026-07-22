"""Atomic, machine-local Hermes handoff checkpoints."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from pipe_venture_builder.adapters.safety import payload_is_safe
from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
    canonical_json,
    fingerprint,
    parse_datetime,
    require_fingerprint,
    require_stable_id,
    safe_identifier,
)

from .model import (
    CHECKPOINT_STATES,
    HERMES_EVENT_KINDS,
    MAX_PROCESSED_EVENTS,
    SCHEMA_VERSION,
)


class HermesCheckpointStore:
    """One fingerprinted JSON checkpoint per Pipe run."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory).expanduser()
        if self.directory.exists() and self.directory.is_symlink():
            raise ControlPlaneStateError("Hermes checkpoint directory cannot be a symlink")
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.directory.is_symlink() or not self.directory.is_dir():
            raise ControlPlaneStateError("Hermes checkpoint path must be a directory")
        os.chmod(self.directory, 0o700)

    def load(self, run_id: str) -> dict[str, Any] | None:
        path = self._path(run_id)
        if not path.exists():
            return None
        if path.is_symlink() or not path.is_file():
            raise ControlPlaneStateError("Hermes checkpoint must be a regular file")
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ControlPlaneStateError("Hermes checkpoint is unreadable") from exc
        validate_checkpoint(document)
        supplied = document["checkpointFingerprint"]
        unsigned = dict(document)
        unsigned.pop("checkpointFingerprint")
        if supplied != fingerprint(unsigned):
            raise ControlPlaneStateError("Hermes checkpoint fingerprint mismatch")
        return document

    def save(self, document: Mapping[str, Any]) -> dict[str, Any]:
        unsigned = dict(document)
        unsigned.pop("checkpointFingerprint", None)
        unsigned["checkpointFingerprint"] = fingerprint(unsigned)
        validate_checkpoint(unsigned)
        path = self._path(unsigned["runId"])
        if path.exists() and path.is_symlink():
            raise ControlPlaneStateError("Hermes checkpoint cannot replace a symlink")
        encoded = f"{canonical_json(unsigned)}\n"
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=self.directory
        )
        temporary = Path(temporary_name)
        try:
            os.fchmod(file_descriptor, 0o600)
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            os.chmod(path, 0o600)
            directory_descriptor = os.open(self.directory, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
        finally:
            if temporary.exists():
                temporary.unlink()
        return unsigned

    def _path(self, run_id: str) -> Path:
        run_id = require_stable_id(run_id, "RUN")
        return self.directory / f"{run_id}.json"


def validate_checkpoint(value: Mapping[str, Any]) -> None:
    if not isinstance(value, Mapping):
        raise ControlPlaneContractError("Hermes checkpoint must be a mapping")
    required = {
        "schemaVersion",
        "runId",
        "planId",
        "productId",
        "linearTicketId",
        "workflow",
        "artifactRefs",
        "requestFingerprint",
        "dispatchToken",
        "sessionId",
        "sessionLineage",
        "state",
        "attempt",
        "pendingActionId",
        "blockerCode",
        "processedEvents",
        "updatedAt",
        "constraints",
        "checkpointFingerprint",
    }
    if set(value) != required or value.get("schemaVersion") != SCHEMA_VERSION:
        raise ControlPlaneContractError("Hermes checkpoint shape is invalid")
    require_stable_id(value.get("runId"), "RUN")
    require_stable_id(value.get("planId"), "RP")
    safe_identifier(value.get("productId"))
    ticket = safe_identifier(value.get("linearTicketId"))
    if not ticket.startswith("PIP-"):
        raise ControlPlaneContractError("Hermes checkpoint ticket is invalid")
    safe_identifier(value.get("workflow"))
    require_fingerprint(value.get("requestFingerprint"))
    require_stable_id(value.get("dispatchToken"), "HD")
    session_id = value.get("sessionId")
    if session_id is not None:
        safe_identifier(session_id)
    lineage = value.get("sessionLineage")
    if (
        not isinstance(lineage, list)
        or any(not isinstance(item, str) for item in lineage)
        or len(lineage) > 64
        or len(lineage) != len(set(lineage))
    ):
        raise ControlPlaneContractError("Hermes session lineage is invalid")
    for item in lineage:
        safe_identifier(item)
    if session_id is not None and (not lineage or lineage[-1] != session_id):
        raise ControlPlaneContractError("Hermes session lineage is inconsistent")
    refs = value.get("artifactRefs")
    if (
        not isinstance(refs, list)
        or not refs
        or refs != sorted(set(refs))
        or any(not isinstance(item, str) or len(item) > 512 for item in refs)
    ):
        raise ControlPlaneContractError("Hermes checkpoint artifact references are invalid")
    for item in refs:
        ref = PurePosixPath(item.replace("\\", "/"))
        if (
            "\\" in item
            or ref.is_absolute()
            or ref.as_posix() != item
            or any(part in {"", ".", ".."} for part in ref.parts)
        ):
            raise ControlPlaneContractError(
                "Hermes checkpoint artifact reference is not portable"
            )
    if value.get("state") not in CHECKPOINT_STATES:
        raise ControlPlaneContractError("Hermes checkpoint state is invalid")
    if not isinstance(value.get("attempt"), int) or value["attempt"] < 1:
        raise ControlPlaneContractError("Hermes checkpoint attempt is invalid")
    pending_action_id = value.get("pendingActionId")
    if pending_action_id is not None:
        require_stable_id(pending_action_id, "RA")
    blocker = value.get("blockerCode")
    if blocker is not None:
        safe_identifier(blocker)
    events = value.get("processedEvents")
    if not isinstance(events, list) or len(events) > MAX_PROCESSED_EVENTS:
        raise ControlPlaneContractError("Hermes processed event list is invalid")
    event_ids: set[str] = set()
    for event in events:
        if not isinstance(event, Mapping) or set(event) != {
            "eventId",
            "fingerprint",
            "kind",
            "occurredAt",
            "actionId",
            "approvalId",
            "toolName",
            "resultRef",
            "payloadFingerprint",
        }:
            raise ControlPlaneContractError("Hermes processed event is invalid")
        event_id = require_stable_id(event.get("eventId"), "HE")
        require_fingerprint(event.get("fingerprint"))
        if event.get("kind") not in HERMES_EVENT_KINDS:
            raise ControlPlaneContractError("Hermes processed event kind is invalid")
        parse_datetime(event.get("occurredAt"))
        if event.get("actionId") is not None:
            require_stable_id(event.get("actionId"), "RA")
        if event.get("approvalId") is not None:
            require_stable_id(event.get("approvalId"), "AP")
        for key in ("toolName", "resultRef"):
            if event.get(key) is not None:
                safe_identifier(event.get(key))
        if event.get("payloadFingerprint") is not None:
            require_fingerprint(event.get("payloadFingerprint"))
        if event_id in event_ids:
            raise ControlPlaneContractError("Hermes processed event identity is duplicated")
        event_ids.add(event_id)
    parse_datetime(value.get("updatedAt"))
    constraints = value.get("constraints")
    if constraints != {
        "rawPayloadPersisted": False,
        "credentialsPersisted": False,
        "customerDataPersisted": False,
        "productionDataPersisted": False,
        "hermesApprovalIsAuthority": False,
        "externalMutationAllowed": False,
    }:
        raise ControlPlaneContractError("Hermes checkpoint constraints are invalid")
    require_fingerprint(value.get("checkpointFingerprint"))
    if not payload_is_safe(value):
        raise ControlPlaneContractError("Hermes checkpoint failed safety checks")
