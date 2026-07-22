"""Approval-aware, resumable apply and verification state machine."""

from __future__ import annotations

from typing import Any, Mapping

from pipe_venture_builder.control_plane.approval import (
    find_action,
    validate_approval_for_action,
    validate_approval_record,
)
from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    fingerprint,
    require_fingerprint,
    safe_identifier,
    utc_now,
)
from pipe_venture_builder.control_plane.store import LocalControlPlaneStore

from .contracts import (
    ApplyAdapter,
    ApplyAdapterConflict,
    ApplyAdapterFailure,
    ApplyInterrupted,
    ApplyResult,
)


MUTATING_ACTIONS = frozenset({"create", "update", "link"})


class SupervisedApplyService:
    """Execute only one exact approved fixture action and persist every transition."""

    def __init__(self, store: LocalControlPlaneStore) -> None:
        self.store = store

    def execute_action(
        self,
        plan: Mapping[str, Any],
        action_id: str,
        *,
        approval: Mapping[str, Any] | None,
        adapter: ApplyAdapter,
        current_source_fingerprint: str,
        at: str | None = None,
        pause_after_apply: bool = False,
    ) -> dict[str, Any]:
        occurred_at = at or utc_now()
        source_fingerprint = require_fingerprint(current_source_fingerprint)
        run_id = self.store.register_plan(plan, at=occurred_at)
        action = find_action(plan, action_id)
        plan_fingerprint = fingerprint(plan)
        if not self.store.verify_audit_chain(run_id) or not self.store.verify_checkpoints(
            run_id
        ):
            return {
                "runId": run_id,
                "actionId": action_id,
                "status": "blocked",
                "reasonCode": "audit_chain_invalid",
                "checkpointState": None,
                "attempt": 0,
                "resultRef": None,
                "resultFingerprint": None,
                "auditChainValid": False,
            }
        checkpoint = self.store.get_checkpoint(run_id, action_id)
        prior_checkpoint = self.store.find_checkpoint_by_idempotency_key(
            action["idempotencyKey"], excluding_run_id=run_id
        )

        if checkpoint and checkpoint["state"] in {"verified", "skipped"}:
            self.store.append_event(
                run_id,
                occurred_at=occurred_at,
                event_type="action.skipped",
                status="skipped",
                reason_code="already_verified",
                plan_id=plan["planId"],
                action_id=action_id,
                approval_id=checkpoint["approval_id"],
                idempotency_key=action["idempotencyKey"],
                result_ref=checkpoint["result_ref"],
                plan_fingerprint=plan_fingerprint,
                source_fingerprint=source_fingerprint,
                expected_target_fingerprint=action["targetFingerprint"],
                observed_target_fingerprint=checkpoint["target_fingerprint"],
                result_fingerprint=checkpoint["result_fingerprint"],
                checkpoint_state=checkpoint["state"],
                attempt=checkpoint["attempt"],
            )
            return self._outcome(run_id, action_id, "skipped", "already_verified")

        if prior_checkpoint and prior_checkpoint["state"] in {"verified", "skipped"}:
            self.store.record_transition(
                run_id=run_id,
                action_id=action_id,
                idempotency_key=action["idempotencyKey"],
                state="skipped",
                attempt=0,
                approval_id=prior_checkpoint["approval_id"],
                source_fingerprint=source_fingerprint,
                target_fingerprint=action["targetFingerprint"],
                result_fingerprint=prior_checkpoint["result_fingerprint"],
                result_ref=prior_checkpoint["result_ref"],
                occurred_at=occurred_at,
                event_type="action.skipped",
                event_status="skipped",
                reason_code="already_verified",
                plan_id=plan["planId"],
                plan_fingerprint=plan_fingerprint,
                run_status="completed",
            )
            return self._outcome(run_id, action_id, "skipped", "already_verified")

        if prior_checkpoint and prior_checkpoint["state"] not in {"blocked", "failed"}:
            return self._block(
                plan,
                run_id,
                action,
                approval_id=None,
                source_fingerprint=source_fingerprint,
                observed_target_fingerprint=None,
                attempt=0,
                reason_code="action_blocked",
                at=occurred_at,
            )

        if checkpoint and checkpoint["result_fingerprint"] and checkpoint["result_ref"]:
            self._resume_run(plan, run_id, action, checkpoint, occurred_at)
            result = ApplyResult(
                checkpoint["result_ref"],
                checkpoint["result_fingerprint"],
                already_applied=True,
            )
            return self._verify(
                plan,
                run_id,
                action,
                approval_id=checkpoint["approval_id"],
                attempt=checkpoint["attempt"],
                source_fingerprint=checkpoint["source_fingerprint"],
                result=result,
                adapter=adapter,
                occurred_at=occurred_at,
            )

        rejection = _action_rejection(action)
        if rejection:
            return self._block(
                plan,
                run_id,
                action,
                approval_id=None,
                source_fingerprint=source_fingerprint,
                observed_target_fingerprint=None,
                attempt=(checkpoint["attempt"] if checkpoint else 0),
                reason_code=rejection,
                at=occurred_at,
            )

        if approval is None:
            return self._block(
                plan,
                run_id,
                action,
                approval_id=None,
                source_fingerprint=source_fingerprint,
                observed_target_fingerprint=None,
                attempt=(checkpoint["attempt"] if checkpoint else 0),
                reason_code="approval_missing",
                at=occurred_at,
            )
        try:
            validate_approval_record(approval)
        except ControlPlaneContractError:
            return self._block(
                plan,
                run_id,
                action,
                approval_id=None,
                source_fingerprint=source_fingerprint,
                observed_target_fingerprint=None,
                attempt=(checkpoint["attempt"] if checkpoint else 0),
                reason_code="approval_mismatch",
                at=occurred_at,
            )
        approval_reason = validate_approval_for_action(
            approval, plan, action, at=occurred_at
        )
        if approval["planId"] == plan["planId"]:
            self.store.record_approval(approval, at=occurred_at)
        if approval_reason:
            return self._block(
                plan,
                run_id,
                action,
                approval_id=approval.get("approvalId"),
                source_fingerprint=source_fingerprint,
                observed_target_fingerprint=None,
                attempt=(checkpoint["attempt"] if checkpoint else 0),
                reason_code=approval_reason,
                at=occurred_at,
            )
        approval_id = approval["approvalId"]

        if source_fingerprint != plan["baseline"]["fingerprint"]:
            return self._block(
                plan,
                run_id,
                action,
                approval_id=approval_id,
                source_fingerprint=source_fingerprint,
                observed_target_fingerprint=None,
                attempt=(checkpoint["attempt"] if checkpoint else 0),
                reason_code="source_changed",
                at=occurred_at,
            )

        attempt = (checkpoint["attempt"] if checkpoint else 0) + 1
        uncertain_retry = bool(
            checkpoint
            and checkpoint["state"] in {"applying", "interrupted"}
            and not checkpoint["result_fingerprint"]
        )
        if uncertain_retry:
            self._resume_run(plan, run_id, action, checkpoint, occurred_at)
        self.store.record_transition(
            run_id=run_id,
            action_id=action_id,
            idempotency_key=action["idempotencyKey"],
            state="pending",
            attempt=attempt,
            approval_id=approval_id,
            source_fingerprint=source_fingerprint,
            target_fingerprint=action["targetFingerprint"],
            result_fingerprint=None,
            result_ref=None,
            occurred_at=occurred_at,
            event_type="action.precondition_started",
            event_status="running",
            plan_id=plan["planId"],
            plan_fingerprint=plan_fingerprint,
            run_status="running",
        )
        try:
            observation = adapter.inspect(action)
            if not isinstance(observation.exists, bool):
                raise ControlPlaneContractError("adapter existence must be boolean")
            require_fingerprint(observation.fingerprint, nullable=True)
        except (ApplyAdapterFailure, ControlPlaneContractError):
            return self._fail(
                plan,
                run_id,
                action,
                approval_id,
                source_fingerprint,
                action["targetFingerprint"],
                None,
                None,
                attempt,
                "adapter_failed",
                occurred_at,
            )
        target_reason = (
            None
            if uncertain_retry
            else _target_precondition(
                action, observation.exists, observation.fingerprint
            )
        )
        if target_reason:
            return self._block(
                plan,
                run_id,
                action,
                approval_id=approval_id,
                source_fingerprint=source_fingerprint,
                observed_target_fingerprint=observation.fingerprint,
                attempt=attempt,
                reason_code=target_reason,
                at=occurred_at,
            )

        self.store.record_transition(
            run_id=run_id,
            action_id=action_id,
            idempotency_key=action["idempotencyKey"],
            state="precondition_passed",
            attempt=attempt,
            approval_id=approval_id,
            source_fingerprint=source_fingerprint,
            target_fingerprint=action["targetFingerprint"],
            result_fingerprint=None,
            result_ref=None,
            occurred_at=occurred_at,
            event_type="action.precondition_passed",
            event_status="succeeded",
            plan_id=plan["planId"],
            plan_fingerprint=plan_fingerprint,
            observed_target_fingerprint=observation.fingerprint,
        )
        self.store.record_transition(
            run_id=run_id,
            action_id=action_id,
            idempotency_key=action["idempotencyKey"],
            state="applying",
            attempt=attempt,
            approval_id=approval_id,
            source_fingerprint=source_fingerprint,
            target_fingerprint=action["targetFingerprint"],
            result_fingerprint=None,
            result_ref=None,
            occurred_at=occurred_at,
            event_type="action.apply_started",
            event_status="running",
            plan_id=plan["planId"],
            plan_fingerprint=plan_fingerprint,
            observed_target_fingerprint=observation.fingerprint,
        )
        try:
            result = adapter.apply(
                action, idempotency_key=action["idempotencyKey"]
            )
            safe_identifier(result.result_ref)
            require_fingerprint(result.result_fingerprint)
        except ApplyInterrupted:
            self.store.record_transition(
                run_id=run_id,
                action_id=action_id,
                idempotency_key=action["idempotencyKey"],
                state="interrupted",
                attempt=attempt,
                approval_id=approval_id,
                source_fingerprint=source_fingerprint,
                target_fingerprint=action["targetFingerprint"],
                result_fingerprint=None,
                result_ref=None,
                occurred_at=occurred_at,
                event_type="run.interrupted",
                event_status="interrupted",
                reason_code="interrupted_after_apply",
                plan_id=plan["planId"],
                plan_fingerprint=plan_fingerprint,
                run_status="interrupted",
            )
            return self._outcome(
                run_id, action_id, "interrupted", "interrupted_after_apply"
            )
        except ApplyAdapterConflict:
            return self._block(
                plan,
                run_id,
                action,
                approval_id=approval_id,
                source_fingerprint=source_fingerprint,
                observed_target_fingerprint=observation.fingerprint,
                attempt=attempt,
                reason_code="adapter_conflict",
                at=occurred_at,
            )
        except (ApplyAdapterFailure, ControlPlaneContractError):
            return self._fail(
                plan,
                run_id,
                action,
                approval_id,
                source_fingerprint,
                action["targetFingerprint"],
                observation.fingerprint,
                None,
                attempt,
                "adapter_failed",
                occurred_at,
            )

        self.store.record_transition(
            run_id=run_id,
            action_id=action_id,
            idempotency_key=action["idempotencyKey"],
            state="applied",
            attempt=attempt,
            approval_id=approval_id,
            source_fingerprint=source_fingerprint,
            target_fingerprint=action["targetFingerprint"],
            result_fingerprint=result.result_fingerprint,
            result_ref=result.result_ref,
            occurred_at=occurred_at,
            event_type="action.apply_succeeded",
            event_status="succeeded",
            plan_id=plan["planId"],
            plan_fingerprint=plan_fingerprint,
            observed_target_fingerprint=observation.fingerprint,
        )
        if pause_after_apply:
            self.store.record_run_event(
                run_id,
                occurred_at=occurred_at,
                event_type="run.interrupted",
                event_status="interrupted",
                run_status="interrupted",
                reason_code="interrupted_after_apply",
                plan_id=plan["planId"],
                plan_fingerprint=plan_fingerprint,
                action_id=action_id,
                approval_id=approval_id,
                idempotency_key=action["idempotencyKey"],
                checkpoint_state="applied",
                attempt=attempt,
            )
            return self._outcome(
                run_id, action_id, "interrupted", "interrupted_after_apply"
            )
        return self._verify(
            plan,
            run_id,
            action,
            approval_id=approval_id,
            attempt=attempt,
            source_fingerprint=source_fingerprint,
            result=result,
            adapter=adapter,
            occurred_at=occurred_at,
        )

    def _verify(
        self,
        plan: Mapping[str, Any],
        run_id: str,
        action: Mapping[str, Any],
        *,
        approval_id: str | None,
        attempt: int,
        source_fingerprint: str,
        result: ApplyResult,
        adapter: ApplyAdapter,
        occurred_at: str,
    ) -> dict[str, Any]:
        plan_fingerprint = fingerprint(plan)
        self.store.record_transition(
            run_id=run_id,
            action_id=action["actionId"],
            idempotency_key=action["idempotencyKey"],
            state="verifying",
            attempt=attempt,
            approval_id=approval_id,
            source_fingerprint=source_fingerprint,
            target_fingerprint=action["targetFingerprint"],
            result_fingerprint=result.result_fingerprint,
            result_ref=result.result_ref,
            occurred_at=occurred_at,
            event_type="action.verify_started",
            event_status="running",
            plan_id=plan["planId"],
            plan_fingerprint=plan_fingerprint,
        )
        try:
            verification = adapter.verify(action, result)
            if not isinstance(verification.verified, bool):
                raise ControlPlaneContractError(
                    "adapter verification status must be boolean"
                )
            require_fingerprint(verification.target_fingerprint, nullable=True)
        except (ApplyAdapterFailure, ControlPlaneContractError):
            return self._fail(
                plan,
                run_id,
                action,
                approval_id,
                source_fingerprint,
                action["targetFingerprint"],
                None,
                result,
                attempt,
                "verification_failed",
                occurred_at,
            )
        if (
            not verification.verified
            or verification.target_fingerprint != result.result_fingerprint
        ):
            return self._fail(
                plan,
                run_id,
                action,
                approval_id,
                source_fingerprint,
                action["targetFingerprint"],
                verification.target_fingerprint,
                result,
                attempt,
                "verification_failed",
                occurred_at,
            )
        self.store.record_transition(
            run_id=run_id,
            action_id=action["actionId"],
            idempotency_key=action["idempotencyKey"],
            state="verified",
            attempt=attempt,
            approval_id=approval_id,
            source_fingerprint=source_fingerprint,
            target_fingerprint=action["targetFingerprint"],
            result_fingerprint=result.result_fingerprint,
            result_ref=result.result_ref,
            occurred_at=occurred_at,
            event_type="action.verified",
            event_status="succeeded",
            plan_id=plan["planId"],
            plan_fingerprint=plan_fingerprint,
            observed_target_fingerprint=verification.target_fingerprint,
        )
        eligible = [
            item["actionId"]
            for item in plan["actions"]
            if item["actionType"] in MUTATING_ACTIONS
            and item["status"] == "proposed"
            and not item["blockerIds"]
        ]
        if self.store.all_actions_verified(run_id, eligible):
            self.store.record_run_event(
                run_id,
                occurred_at=occurred_at,
                event_type="run.completed",
                event_status="succeeded",
                run_status="completed",
                plan_id=plan["planId"],
                plan_fingerprint=plan_fingerprint,
                action_id=action["actionId"],
                approval_id=approval_id,
                idempotency_key=action["idempotencyKey"],
                checkpoint_state="verified",
                attempt=attempt,
            )
        return self._outcome(run_id, action["actionId"], "verified", None)

    def _block(
        self,
        plan: Mapping[str, Any],
        run_id: str,
        action: Mapping[str, Any],
        *,
        approval_id: str | None,
        source_fingerprint: str,
        observed_target_fingerprint: str | None,
        attempt: int,
        reason_code: str,
        at: str,
    ) -> dict[str, Any]:
        self.store.record_transition(
            run_id=run_id,
            action_id=action["actionId"],
            idempotency_key=action["idempotencyKey"],
            state="blocked",
            attempt=attempt,
            approval_id=approval_id,
            source_fingerprint=source_fingerprint,
            target_fingerprint=action["targetFingerprint"],
            result_fingerprint=None,
            result_ref=None,
            occurred_at=at,
            event_type="action.blocked",
            event_status="blocked",
            reason_code=reason_code,
            plan_id=plan["planId"],
            plan_fingerprint=fingerprint(plan),
            observed_target_fingerprint=observed_target_fingerprint,
            run_status="blocked",
        )
        return self._outcome(run_id, action["actionId"], "blocked", reason_code)

    def _fail(
        self,
        plan: Mapping[str, Any],
        run_id: str,
        action: Mapping[str, Any],
        approval_id: str | None,
        source_fingerprint: str,
        target_fingerprint: str | None,
        observed_target_fingerprint: str | None,
        result: ApplyResult | None,
        attempt: int,
        reason_code: str,
        at: str,
    ) -> dict[str, Any]:
        self.store.record_transition(
            run_id=run_id,
            action_id=action["actionId"],
            idempotency_key=action["idempotencyKey"],
            state="failed",
            attempt=attempt,
            approval_id=approval_id,
            source_fingerprint=source_fingerprint,
            target_fingerprint=target_fingerprint,
            result_fingerprint=(result.result_fingerprint if result else None),
            result_ref=(result.result_ref if result else None),
            occurred_at=at,
            event_type=(
                "action.verify_failed"
                if reason_code == "verification_failed"
                else "run.failed"
            ),
            event_status="failed",
            reason_code=reason_code,
            plan_id=plan["planId"],
            plan_fingerprint=fingerprint(plan),
            observed_target_fingerprint=observed_target_fingerprint,
            run_status="failed",
        )
        return self._outcome(run_id, action["actionId"], "failed", reason_code)

    def _resume_run(
        self,
        plan: Mapping[str, Any],
        run_id: str,
        action: Mapping[str, Any],
        checkpoint: Mapping[str, Any],
        at: str,
    ) -> None:
        self.store.record_run_event(
            run_id,
            occurred_at=at,
            event_type="run.resumed",
            event_status="running",
            run_status="running",
            plan_id=plan["planId"],
            plan_fingerprint=fingerprint(plan),
            action_id=action["actionId"],
            approval_id=checkpoint["approval_id"],
            idempotency_key=action["idempotencyKey"],
            checkpoint_state=checkpoint["state"],
            attempt=checkpoint["attempt"],
        )

    def _outcome(
        self, run_id: str, action_id: str, status: str, reason_code: str | None
    ) -> dict[str, Any]:
        checkpoint = self.store.get_checkpoint(run_id, action_id)
        return {
            "runId": run_id,
            "actionId": action_id,
            "status": status,
            "reasonCode": reason_code,
            "checkpointState": checkpoint["state"] if checkpoint else None,
            "attempt": checkpoint["attempt"] if checkpoint else 0,
            "resultRef": checkpoint["result_ref"] if checkpoint else None,
            "resultFingerprint": (
                checkpoint["result_fingerprint"] if checkpoint else None
            ),
            "auditChainValid": (
                self.store.verify_audit_chain(run_id)
                and self.store.verify_checkpoints(run_id)
            ),
        }


def _action_rejection(action: Mapping[str, Any]) -> str | None:
    if action.get("actionType") not in MUTATING_ACTIONS:
        return "action_not_applicable"
    if action.get("status") != "proposed" or action.get("blockerIds"):
        return "action_blocked"
    if action.get("confidence") == "low" or action.get("approvalRequired") is not True:
        return "action_not_applicable"
    return None


def _target_precondition(
    action: Mapping[str, Any], exists: bool, observed_fingerprint: str | None
) -> str | None:
    expected = action.get("targetFingerprint")
    if action["actionType"] == "create":
        return "target_changed" if exists or observed_fingerprint is not None else None
    if expected is None:
        return "target_version_missing"
    if not exists or observed_fingerprint != expected:
        return "target_changed"
    return None
