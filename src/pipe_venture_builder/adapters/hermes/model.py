"""Strict, payload-free contracts for the Hermes runtime boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

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


SCHEMA_VERSION = "0.1.0"
MAX_ARTIFACT_REFS = 128
MAX_PROCESSED_EVENTS = 1024
WORKFLOW_KINDS = frozenset({"idea", "adopt", "reconcile", "review", "check"})
HERMES_EVENT_KINDS = frozenset(
    {
        "run.started",
        "run.resumed",
        "run.completed",
        "run.failed",
        "tool.started",
        "tool.succeeded",
        "tool.failed",
        "approval.requested",
        "approval.granted",
        "approval.denied",
        "runtime.unavailable",
        "runtime.timeout",
    }
)
RECORDABLE_HERMES_EVENT_KINDS = HERMES_EVENT_KINDS - {
    "run.started",
    "run.resumed",
    "approval.granted",
}
CHECKPOINT_STATES = frozenset(
    {
        "dispatch_pending",
        "running",
        "waiting_for_approval",
        "approval_granted",
        "approval_denied",
        "runtime_blocked",
        "interrupted",
        "failed",
        "completed",
    }
)


@dataclass(frozen=True)
class HermesRunContext:
    """The minimum canonical context a Hermes session may receive."""

    product_id: str
    linear_ticket_id: str
    workflow: str
    product_root: Path
    artifact_refs: tuple[str, ...]
    plan_id: str
    plan_fingerprint: str
    baseline_fingerprint: str

    @classmethod
    def build(
        cls,
        *,
        product_id: str,
        linear_ticket_id: str,
        workflow: str,
        product_root: str | Path,
        artifact_refs: Sequence[str],
        plan: Mapping[str, Any],
    ) -> HermesRunContext:
        product_id = safe_identifier(product_id)
        linear_ticket_id = safe_identifier(linear_ticket_id)
        if not linear_ticket_id.startswith("PIP-"):
            raise ControlPlaneContractError("Hermes handoff requires a Linear ticket")
        if workflow not in WORKFLOW_KINDS:
            raise ControlPlaneContractError("unsupported Hermes workflow")
        if not isinstance(plan, Mapping):
            raise ControlPlaneContractError("Hermes handoff plan must be a mapping")
        plan_id = require_stable_id(plan.get("planId"), "RP")
        baseline = plan.get("baseline")
        if not isinstance(baseline, Mapping):
            raise ControlPlaneContractError("Hermes handoff baseline is invalid")
        baseline_fingerprint = require_fingerprint(baseline.get("fingerprint"))
        if not payload_is_safe(plan):
            raise ControlPlaneContractError("Hermes handoff plan failed safety checks")

        root = Path(product_root).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ControlPlaneContractError("product root must be a directory")
        normalized_refs = normalize_artifact_refs(root, artifact_refs)
        return cls(
            product_id=product_id,
            linear_ticket_id=linear_ticket_id,
            workflow=workflow,
            product_root=root,
            artifact_refs=normalized_refs,
            plan_id=plan_id,
            plan_fingerprint=fingerprint(plan),
            baseline_fingerprint=baseline_fingerprint,
        )

    def document(self) -> dict[str, Any]:
        """Return the redacted, portable request included in the handoff."""

        return {
            "schemaVersion": SCHEMA_VERSION,
            "productId": self.product_id,
            "linearTicketId": self.linear_ticket_id,
            "workflow": self.workflow,
            "artifactRefs": list(self.artifact_refs),
            "planId": self.plan_id,
            "planFingerprint": self.plan_fingerprint,
            "baselineFingerprint": self.baseline_fingerprint,
            "constraints": {
                "repositoryCanonical": True,
                "linearCanonicalForExecution": True,
                "pipeApprovalRequired": True,
                "hermesApprovalIsAuthority": False,
                "externalMutationAllowed": False,
                "credentialsAllowed": False,
                "customerDataAllowed": False,
                "productionDataAllowed": False,
            },
        }


@dataclass(frozen=True)
class HermesRuntimeEvent:
    """A normalized Hermes event; raw runtime payloads are never accepted."""

    event_id: str
    kind: str
    session_id: str
    occurred_at: str
    action_id: str | None = None
    approval_id: str | None = None
    tool_name: str | None = None
    result_ref: str | None = None
    payload_fingerprint: str | None = None

    @classmethod
    def build(
        cls,
        *,
        external_event_id: str,
        kind: str,
        session_id: str,
        occurred_at: str,
        action_id: str | None = None,
        approval_id: str | None = None,
        tool_name: str | None = None,
        result_ref: str | None = None,
        payload_fingerprint: str | None = None,
    ) -> HermesRuntimeEvent:
        external_event_id = safe_identifier(external_event_id)
        session_id = safe_identifier(session_id)
        if kind not in HERMES_EVENT_KINDS:
            raise ControlPlaneContractError("unsupported Hermes event kind")
        parse_datetime(occurred_at)
        if action_id is not None:
            action_id = require_stable_id(action_id, "RA")
        if approval_id is not None:
            approval_id = require_stable_id(approval_id, "AP")
        if tool_name is not None:
            tool_name = safe_identifier(tool_name)
        if result_ref is not None:
            result_ref = safe_identifier(result_ref)
        if payload_fingerprint is not None:
            payload_fingerprint = require_fingerprint(payload_fingerprint)
        event_id = stable_id(
            "HE",
            {
                "externalEventId": external_event_id,
                "sessionId": session_id,
                "kind": kind,
            },
        )
        return cls(
            event_id=event_id,
            kind=kind,
            session_id=session_id,
            occurred_at=occurred_at,
            action_id=action_id,
            approval_id=approval_id,
            tool_name=tool_name,
            result_ref=result_ref,
            payload_fingerprint=payload_fingerprint,
        )

    def document(self) -> dict[str, Any]:
        document = {
            "schemaVersion": SCHEMA_VERSION,
            "eventId": self.event_id,
            "kind": self.kind,
            "sessionId": self.session_id,
            "occurredAt": self.occurred_at,
            "actionId": self.action_id,
            "approvalId": self.approval_id,
            "toolName": self.tool_name,
            "resultRef": self.result_ref,
            "payloadFingerprint": self.payload_fingerprint,
            "constraints": {
                "rawPayloadPersisted": False,
                "credentialsPersisted": False,
                "customerDataPersisted": False,
                "productionDataPersisted": False,
            },
        }
        if not payload_is_safe(document):
            raise ControlPlaneContractError("Hermes event failed safety checks")
        return document


def normalize_artifact_refs(root: Path, refs: Sequence[str]) -> tuple[str, ...]:
    if isinstance(refs, (str, bytes)) or not isinstance(refs, Sequence):
        raise ControlPlaneContractError("artifact references must be a sequence")
    if not refs or len(refs) > MAX_ARTIFACT_REFS:
        raise ControlPlaneContractError("artifact reference count is invalid")
    normalized: set[str] = set()
    for raw in refs:
        if not isinstance(raw, str) or not raw:
            raise ControlPlaneContractError("artifact reference is invalid")
        ref = PurePosixPath(raw.replace("\\", "/"))
        if ref.is_absolute() or any(part in {"", ".", ".."} for part in ref.parts):
            raise ControlPlaneContractError("artifact reference must be repository-relative")
        rendered = ref.as_posix()
        if len(rendered) > 512:
            raise ControlPlaneContractError("artifact reference is too long")
        candidate = (root / Path(*ref.parts)).resolve(strict=True)
        if not candidate.is_relative_to(root) or not candidate.is_file():
            raise ControlPlaneContractError("artifact reference escapes or is not a file")
        normalized.add(rendered)
    return tuple(sorted(normalized))
