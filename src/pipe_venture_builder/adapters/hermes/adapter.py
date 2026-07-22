"""Supervised Hermes-to-Pipe runtime handoff."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from pipe_venture_builder.control_plane.approval import (
    find_action,
    validate_approval_for_action,
)
from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
    fingerprint,
    parse_datetime,
    require_stable_id,
    safe_identifier,
    stable_id,
)
from pipe_venture_builder.control_plane.store import LocalControlPlaneStore

from .checkpoint import HermesCheckpointStore
from .model import HermesRunContext, HermesRuntimeEvent, SCHEMA_VERSION


_EVENT_MAPPING: dict[str, tuple[str, str, str, str, str | None]] = {
    # Hermes kind: Pipe event type, event status, run status, checkpoint, reason.
    "run.started": ("run.resumed", "running", "running", "running", None),
    "run.resumed": ("run.resumed", "running", "running", "running", None),
    "run.completed": ("run.completed", "succeeded", "completed", "completed", None),
    "run.failed": ("run.failed", "failed", "failed", "failed", "adapter_failed"),
    "tool.started": ("run.resumed", "running", "running", "running", None),
    "tool.succeeded": ("run.resumed", "succeeded", "running", "running", None),
    "tool.failed": (
        "run.interrupted",
        "interrupted",
        "interrupted",
        "interrupted",
        "adapter_failed",
    ),
    "approval.requested": (
        "run.interrupted",
        "interrupted",
        "interrupted",
        "waiting_for_approval",
        "approval_missing",
    ),
    "approval.granted": (
        "run.resumed",
        "succeeded",
        "running",
        "approval_granted",
        None,
    ),
    "approval.denied": (
        "run.interrupted",
        "blocked",
        "interrupted",
        "approval_denied",
        "approval_not_granted",
    ),
    "runtime.unavailable": (
        "run.interrupted",
        "blocked",
        "interrupted",
        "runtime_blocked",
        "adapter_failed",
    ),
    "runtime.timeout": (
        "run.interrupted",
        "interrupted",
        "interrupted",
        "runtime_blocked",
        "adapter_failed",
    ),
}


class HermesRuntimeAdapter:
    """Bind a Hermes session to one audited Pipe run without dispatching it."""

    def __init__(
        self,
        control_plane: LocalControlPlaneStore,
        checkpoints: HermesCheckpointStore,
    ) -> None:
        self.control_plane = control_plane
        self.checkpoints = checkpoints

    def begin(
        self,
        *,
        plan: Mapping[str, Any],
        context: HermesRunContext,
        session_id: str,
        external_event_id: str,
        occurred_at: str,
    ) -> dict[str, Any]:
        session_id = safe_identifier(session_id)
        parse_datetime(occurred_at)
        if context.plan_id != plan.get("planId") or fingerprint(plan) != context.plan_fingerprint:
            raise ControlPlaneContractError("Hermes context does not match the plan")
        run_id = self.control_plane.register_plan(plan, at=occurred_at)
        request = context.document()
        request_fingerprint = fingerprint(request)
        start_event = HermesRuntimeEvent.build(
            external_event_id=external_event_id,
            kind="run.started",
            session_id=session_id,
            occurred_at=occurred_at,
        )
        existing = self.checkpoints.load(run_id)
        if existing is not None:
            if existing["requestFingerprint"] != request_fingerprint:
                raise ControlPlaneStateError("Hermes run is already bound to different context")
            duplicate = self._duplicate_result(existing, start_event)
            if duplicate is not None:
                return duplicate
            if existing["state"] == "dispatch_pending" and existing["sessionId"] == session_id:
                return self._process_event(existing, start_event)
            return self.resume(
                run_id=run_id,
                session_id=session_id,
                external_event_id=external_event_id,
                occurred_at=occurred_at,
            )
        checkpoint = {
            "schemaVersion": SCHEMA_VERSION,
            "runId": run_id,
            "planId": context.plan_id,
            "productId": context.product_id,
            "linearTicketId": context.linear_ticket_id,
            "workflow": context.workflow,
            "artifactRefs": list(context.artifact_refs),
            "requestFingerprint": request_fingerprint,
            "dispatchToken": stable_id(
                "HD", {"runId": run_id, "requestFingerprint": request_fingerprint}
            ),
            "sessionId": session_id,
            "sessionLineage": [session_id],
            "state": "dispatch_pending",
            "attempt": 1,
            "pendingActionId": None,
            "blockerCode": None,
            "processedEvents": [],
            "updatedAt": occurred_at,
            "constraints": _checkpoint_constraints(),
        }
        checkpoint = self.checkpoints.save(checkpoint)
        return self._process_event(checkpoint, start_event)

    def resume(
        self,
        *,
        run_id: str,
        session_id: str,
        external_event_id: str,
        occurred_at: str,
    ) -> dict[str, Any]:
        run_id = require_stable_id(run_id, "RUN")
        session_id = safe_identifier(session_id)
        parse_datetime(occurred_at)
        checkpoint = self._require_checkpoint(run_id)
        self._require_event_time(checkpoint, occurred_at)
        if checkpoint["state"] in {"completed", "failed", "approval_denied"}:
            raise ControlPlaneStateError("terminal Hermes run cannot be resumed")
        lineage = list(checkpoint["sessionLineage"])
        if not lineage or lineage[-1] != session_id:
            if session_id in lineage:
                raise ControlPlaneStateError("Hermes session lineage cannot move backwards")
            lineage.append(session_id)
        pending = deepcopy(checkpoint)
        pending.update(
            {
                "sessionId": session_id,
                "sessionLineage": lineage,
                "state": "dispatch_pending",
                "attempt": checkpoint["attempt"] + 1,
                "blockerCode": None,
                "updatedAt": occurred_at,
            }
        )
        pending = self.checkpoints.save(pending)
        event = HermesRuntimeEvent.build(
            external_event_id=external_event_id,
            kind="run.resumed",
            session_id=session_id,
            occurred_at=occurred_at,
        )
        return self._process_event(pending, event)

    def record_event(self, run_id: str, event: HermesRuntimeEvent) -> dict[str, Any]:
        run_id = require_stable_id(run_id, "RUN")
        checkpoint = self._require_checkpoint(run_id)
        if checkpoint["sessionId"] != event.session_id:
            raise ControlPlaneStateError("Hermes event session does not match the handoff")
        if event.kind == "approval.granted":
            raise ControlPlaneContractError(
                "approval.granted requires a canonical Pipe ApprovalRecord"
            )
        if event.kind == "approval.requested" and event.action_id is None:
            raise ControlPlaneContractError("approval request requires an action identifier")
        if event.kind == "approval.denied" and event.action_id is None:
            raise ControlPlaneContractError("approval denial requires an action identifier")
        duplicate = self._duplicate_result(checkpoint, event)
        if duplicate is not None:
            return duplicate
        self._require_transition(checkpoint, event.kind)
        return self._process_event(checkpoint, event)

    def grant_approval(
        self,
        *,
        run_id: str,
        event: HermesRuntimeEvent,
        approval: Mapping[str, Any],
        plan: Mapping[str, Any],
    ) -> dict[str, Any]:
        run_id = require_stable_id(run_id, "RUN")
        if event.kind != "approval.granted":
            raise ControlPlaneContractError("approval handoff requires approval.granted")
        checkpoint = self._require_checkpoint(run_id)
        if checkpoint["sessionId"] != event.session_id:
            raise ControlPlaneStateError("Hermes approval session does not match the handoff")
        duplicate = self._duplicate_result(checkpoint, event)
        if duplicate is not None:
            return duplicate
        self._require_event_time(checkpoint, event.occurred_at)
        if checkpoint["state"] != "waiting_for_approval":
            raise ControlPlaneStateError("Hermes run is not waiting for Pipe approval")
        run = self.control_plane.get_run(run_id)
        if (
            plan.get("planId") != checkpoint["planId"]
            or fingerprint(plan) != run["plan_fingerprint"]
        ):
            raise ControlPlaneContractError("Pipe approval plan does not match the run")
        action = find_action(plan, event.action_id or "")
        approval_reason = validate_approval_for_action(
            approval, plan, action, at=event.occurred_at
        )
        if approval_reason is not None:
            raise ControlPlaneContractError("Pipe approval cannot grant this handoff")
        if (
            event.action_id is None
            or event.approval_id is None
            or checkpoint["pendingActionId"] != event.action_id
            or approval.get("actionId") != event.action_id
            or approval.get("approvalId") != event.approval_id
            or approval.get("planId") != checkpoint["planId"]
        ):
            raise ControlPlaneContractError("Pipe approval does not match the Hermes handoff")
        self.control_plane.record_approval(approval, at=event.occurred_at)
        return self._process_event(checkpoint, event)

    def status(self, run_id: str) -> dict[str, Any]:
        checkpoint = self._require_checkpoint(run_id)
        return _public_result(checkpoint, duplicate=False)

    def _require_checkpoint(self, run_id: str) -> dict[str, Any]:
        checkpoint = self.checkpoints.load(run_id)
        if checkpoint is None:
            raise ControlPlaneStateError("Hermes checkpoint is not registered")
        run = self.control_plane.get_run(run_id)
        if run["plan_id"] != checkpoint["planId"]:
            raise ControlPlaneStateError("Hermes checkpoint plan does not match the run")
        if not self.control_plane.verify_audit_chain(run_id):
            raise ControlPlaneStateError("Pipe audit chain is invalid")
        return checkpoint

    @staticmethod
    def _require_event_time(checkpoint: Mapping[str, Any], occurred_at: str) -> None:
        if parse_datetime(occurred_at) < parse_datetime(checkpoint["updatedAt"]):
            raise ControlPlaneStateError("Hermes event is older than the checkpoint")

    @staticmethod
    def _require_transition(checkpoint: Mapping[str, Any], kind: str) -> None:
        state = checkpoint["state"]
        if state in {"completed", "failed", "approval_denied"}:
            raise ControlPlaneStateError("terminal Hermes run rejects new events")
        if kind in {"run.started", "run.resumed", "approval.granted"}:
            raise ControlPlaneContractError("Hermes event requires its dedicated handoff")
        if state in {"runtime_blocked", "interrupted", "dispatch_pending"}:
            raise ControlPlaneStateError("interrupted Hermes run must be resumed first")
        if state == "waiting_for_approval" and kind not in {
            "approval.denied",
            "runtime.unavailable",
            "runtime.timeout",
            "run.failed",
        }:
            raise ControlPlaneStateError("Hermes run is waiting for Pipe approval")
        if kind == "approval.denied" and state != "waiting_for_approval":
            raise ControlPlaneStateError("Hermes run is not waiting for approval")
        if kind == "approval.requested" and state not in {"running", "approval_granted"}:
            raise ControlPlaneStateError("Hermes approval request is out of sequence")
        if kind == "run.completed" and state not in {"running", "approval_granted"}:
            raise ControlPlaneStateError("Hermes completion is out of sequence")

    @staticmethod
    def _duplicate_result(
        checkpoint: Mapping[str, Any], event: HermesRuntimeEvent
    ) -> dict[str, Any] | None:
        event_fingerprint = fingerprint(event.document())
        for item in checkpoint["processedEvents"]:
            if item["eventId"] == event.event_id:
                if item["fingerprint"] != event_fingerprint:
                    raise ControlPlaneStateError(
                        "Hermes event identifier has conflicting content"
                    )
                return _public_result(checkpoint, duplicate=True)
        return None

    def _process_event(
        self, checkpoint: Mapping[str, Any], event: HermesRuntimeEvent
    ) -> dict[str, Any]:
        event_document = event.document()
        event_fingerprint = fingerprint(event_document)
        processed = list(checkpoint["processedEvents"])
        for item in processed:
            if item["eventId"] == event.event_id:
                if item["fingerprint"] != event_fingerprint:
                    raise ControlPlaneStateError(
                        "Hermes event identifier has conflicting content"
                    )
                return _public_result(checkpoint, duplicate=True)

        self._require_event_time(checkpoint, event.occurred_at)

        pipe_events = self.control_plane.list_events(checkpoint["runId"])
        already_recorded = any(
            item["references"]["idempotencyKey"] == event.event_id
            for item in pipe_events
        )
        event_type, event_status, run_status, state, reason = _EVENT_MAPPING[event.kind]
        if not already_recorded:
            self.control_plane.record_run_event(
                checkpoint["runId"],
                occurred_at=event.occurred_at,
                event_type=event_type,
                event_status=event_status,
                run_status=run_status,
                plan_id=checkpoint["planId"],
                plan_fingerprint=self.control_plane.get_run(checkpoint["runId"])[
                    "plan_fingerprint"
                ],
                reason_code=reason,
                action_id=event.action_id,
                approval_id=event.approval_id,
                # RunEvent has no runtime-event reference. Reuse its generic,
                # nullable safe idempotency reference as the recovery key.
                idempotency_key=event.event_id,
                attempt=checkpoint["attempt"],
            )
        else:
            self.control_plane.update_run_status(
                checkpoint["runId"], run_status, at=event.occurred_at
            )

        updated = deepcopy(dict(checkpoint))
        processed.append(
            {
                "eventId": event.event_id,
                "fingerprint": event_fingerprint,
                "kind": event.kind,
                "occurredAt": event.occurred_at,
                "actionId": event.action_id,
                "approvalId": event.approval_id,
                "toolName": event.tool_name,
                "resultRef": event.result_ref,
                "payloadFingerprint": event.payload_fingerprint,
            }
        )
        updated.update(
            {
                "state": state,
                "processedEvents": processed,
                "updatedAt": event.occurred_at,
                "blockerCode": reason,
            }
        )
        if event.kind == "approval.requested":
            updated["pendingActionId"] = event.action_id
        elif event.kind in {"approval.granted", "approval.denied"}:
            updated["pendingActionId"] = None
        elif event.kind in {"runtime.unavailable", "runtime.timeout", "run.failed"}:
            updated["pendingActionId"] = None
        saved = self.checkpoints.save(updated)
        return _public_result(saved, duplicate=already_recorded)


def _checkpoint_constraints() -> dict[str, bool]:
    return {
        "rawPayloadPersisted": False,
        "credentialsPersisted": False,
        "customerDataPersisted": False,
        "productionDataPersisted": False,
        "hermesApprovalIsAuthority": False,
        "externalMutationAllowed": False,
    }


def _public_result(checkpoint: Mapping[str, Any], *, duplicate: bool) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "runId": checkpoint["runId"],
        "planId": checkpoint["planId"],
        "productId": checkpoint["productId"],
        "linearTicketId": checkpoint["linearTicketId"],
        "workflow": checkpoint["workflow"],
        "artifactRefs": list(checkpoint["artifactRefs"]),
        "dispatchToken": checkpoint["dispatchToken"],
        "sessionId": checkpoint["sessionId"],
        "state": checkpoint["state"],
        "attempt": checkpoint["attempt"],
        "pendingActionId": checkpoint["pendingActionId"],
        "blockerCode": checkpoint["blockerCode"],
        "duplicate": duplicate,
        "checkpointFingerprint": checkpoint["checkpointFingerprint"],
        "constraints": _checkpoint_constraints(),
    }
