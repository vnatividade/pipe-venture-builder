"""Stable, payload-free blocker codes for the DeepSeek Harness contract spike."""

from __future__ import annotations

from typing import Any

from pipe_venture_builder.control_plane.model import ControlPlaneContractError


_MESSAGES = {
    # Context (ADR-004 D2, D7).
    "workflow_unsupported": "workflow is not an enabled read-only workflow",
    "linear_ticket_invalid": "a Linear ticket identifier is required",
    "fixture_root_invalid": "fixture root must be an existing absolute directory",
    "fixture_root_forbidden": "fixture root must not be inside a git worktree",
    "symlink_forbidden": "symlinks are refused without being followed",
    "path_forbidden": "forbidden path class in fixture workspace",
    "workspace_refs_invalid": "workspace references must be a non-empty list",
    "workspace_ref_invalid": "workspace reference must be canonical and relative",
    "workspace_ref_not_file": "workspace reference is not a regular fixture file",
    "workspace_ref_too_large": "workspace reference exceeds the size bound",
    "workspace_too_large": "fixture workspace exceeds the scan bound",
    "workspace_changed": "fixture workspace changed while being inspected",
    "context_invalid": "context must be built through the validated builder",
    "platform_unsupported": "platform lacks no-follow filesystem primitives",
    # Session binding (ADR-004 D3, D9).
    "binding_field_invalid": "session binding element is invalid",
    "fingerprint_invalid": "session binding fingerprint is invalid",
    "route_not_allowlisted": "route is not an allowlisted synthetic identifier",
    "model_not_allowlisted": "model is not an allowlisted synthetic identifier",
    "profile_forbidden": "profile is forbidden by the runtime boundary",
    "consumer_conflict": "session already has a different consumer",
    "binding_immutable": "session binding is immutable; use a new attempt and session",
    "lineage_invalid": "attempt lineage must be contiguous and forward-only",
    "binding_unknown": "no session binding matches the request",
    "binding_superseded": "session binding was superseded by a newer attempt",
    "context_mismatch": "context does not match the session binding",
    # Preflight (ADR-004 D8, BDD 5).
    "preflight_config_invalid": "preflight configuration shape is invalid",
    "preflight_environment_inherited": "preflight refuses inherited environment",
    "preflight_credential_discovery": "preflight refuses credential discovery",
    "preflight_plugin_discovery": "preflight refuses plugin discovery",
    "preflight_telemetry": "preflight refuses telemetry",
    "preflight_hot_reload": "preflight refuses plugin hot reload",
    "preflight_network": "preflight refuses network access",
    # Runtime events and sequencing (ADR-004 D4, D10).
    "event_field_unknown": "runtime event carries a field outside the allowlist",
    "event_field_invalid": "runtime event metadata is missing or malformed",
    "event_kind_unknown": "runtime event kind is not allowlisted",
    "event_kind_forbidden": "runtime events cannot approve or complete a Pipe run",
    "tool_not_allowlisted": "tool is not an allowlisted read-only tool",
    "sequence_gap": "runtime event sequence has a gap or reorder",
    "event_conflict": "runtime event conflicts with an already observed event",
    "stream_blocked": "runtime event stream is blocked after a failure",
    # Pipe run binding and audit (ADR-004 D1, D3, D11).
    "timestamp_invalid": "timestamp must be RFC 3339 text with a timezone",
    "run_unregistered": "Pipe run is not registered",
    "plan_mismatch": "plan does not match the registered Pipe run",
    "run_terminal": "Pipe run is not in a resumable state",
    "audit_chain_invalid": "Pipe audit chain failed verification",
    "audit_write_failed": "Pipe audit event could not be recorded",
    "dispatch_missing": "session has not been dispatched by this adapter",
    "session_mismatch": "runtime event belongs to a different session",
    "recovery_required": "dispatch exists in the audit; forward-only recovery required",
    # Checkpoint and recovery (ADR-004 D5, D7, D10).
    "checkpoint_path_invalid": "checkpoint directory must be an absolute real directory",
    "checkpoint_path_changed": "checkpoint directory changed while being used",
    "checkpoint_mode_invalid": "checkpoint permissions must be 0700 directory and 0600 file",
    "checkpoint_invalid": "checkpoint shape or encoding is invalid",
    "checkpoint_tampered": "checkpoint fingerprint does not match its content",
    "checkpoint_write_failed": "checkpoint could not be written atomically",
    "checkpoint_stale": "checkpoint is behind the Pipe audit; recovery is forward-only",
    "checkpoint_audit_mismatch": "checkpoint claims events absent from the Pipe audit",
    "checkpoint_binding_mismatch": "checkpoint does not match the session binding",
    "outcome_unknown": "runtime outcome is unknown; a new attempt is required",
    # Approval handoff, proposal and completion (ADR-004 D3, D6, D12).
    "stream_not_quiescent": "session is not at a closed turn or idle",
    "action_not_approvable": "action is not an approvable create, update or link",
    "approval_missing": "an exact Pipe ApprovalRecord recorded in the audit is required",
    "approval_invalid": "ApprovalRecord does not match the exact plan action",
    "approval_inactive": "ApprovalRecord is not granted, expired or superseded",
    "result_ref_invalid": "result reference or fingerprint is invalid",
    "proposal_missing": "no result proposal was issued for this session",
    "proposal_invalid": "proposal is altered or outside the inert shape",
    "proposal_mismatch": "proposal is not the current result issued for this session",
    # Fake transport and normalization (ADR-004 D4, D10, D13; synthetic only).
    "frame_invalid": "frame is not a valid JSON-RPC 2.0 object in the spike shape",
    "frame_type_unknown": "frame method or update type is not allowlisted",
    "frame_truncated": "stream ended inside a frame",
    "frame_too_large": "frame exceeds the size bound",
    "transport_timeout": "transport timed out; the stream is closed",
    "transport_eof": "transport reached end of stream",
    "tool_call_literal": "tool call appeared as literal text instead of a structured frame",
    "tool_call_malformed": "tool call or result frame is malformed",
    "reasoning_inconsistent": "reasoning frame is outside or after the turn answer",
    "turn_state_invalid": "frame is inconsistent with the turn state",
    "runtime_error": "runtime answered a request with an error",
    "contract_violation": "DeepSeek Harness contract violation",
}

BLOCKER_CODES = frozenset(_MESSAGES)


class DeepSeekHarnessContractError(ControlPlaneContractError):
    """Fail-closed refusal carrying only a stable code and a fixed message.

    The message never includes caller input, paths, or runtime payloads.
    Raise it with ``from None`` so no underlying exception is chained.
    """

    def __init__(self, code: str) -> None:
        if not isinstance(code, str) or code not in _MESSAGES:
            code = "contract_violation"
        self.code = code
        super().__init__(f"{code}: {_MESSAGES[code]}")

    def __reduce__(self) -> tuple[Any, ...]:
        return (type(self), (self.code,))
