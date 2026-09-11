"""Minimal runtime adapter composing the Pipe control plane (ADR-004 D1, D3-D5).

Pipe stays canonical: a dispatch is accepted only for a registered Pipe run
whose plan matches, through the latest session binding of that run, with the
bound C1 context, and while the Pipe audit chain verifies. Runtime events are
recorded as payload-free Pipe audit events keyed by their ``DHE-*`` id. No
ApprovalRecord is required, recorded or invented for read-only review/check
runs, and no runtime event ever approves or completes the run.

With a checkpoint store, every dispatch and event is checkpointed write-ahead:
the intent is saved before the Pipe audit write and committed after it, so a
failure on either side is reconciled from the audit on recovery and never
guessed. Recovery is forward-only: a checkpoint behind the audit, claiming
unaudited events, or bound to another session is refused; a protocol block
survives restarts; and an attempt interrupted mid-turn is blocked as
``outcome_unknown`` until a new attempt is dispatched. Without a checkpoint
store, stream state is in memory and an audited dispatch unknown to the
adapter is refused as ``recovery_required``.

The Pipe audit, not the checkpoint or the in-memory session registry, is the
durable authority for attempt ownership and blocks: every dispatch audits its
``DHD-*`` id under its attempt, so a registry rebuilt after a restart cannot
rebind an audited attempt to another session or go back to an earlier one, and
a blocked attempt carries a ``DHD-*:blocked`` audit marker that no checkpoint
rewrite, fresh normalizer or second adapter instance can clear. A refusal
never rewrites a terminal run. The spike does not claim mutual exclusion
between processes.
"""

from __future__ import annotations

from typing import Any, Mapping

from pipe_venture_builder.control_plane import LocalControlPlaneStore
from pipe_venture_builder.control_plane.approval import (
    MUTATING_ACTIONS,
    find_action,
    validate_approval_for_action,
)
from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    ControlPlaneStateError,
    fingerprint,
    parse_datetime,
    stable_id,
)

from .checkpoint import (
    CHECKPOINT_CONSTRAINTS,
    SCHEMA_VERSION as CHECKPOINT_SCHEMA_VERSION,
    DeepSeekHarnessCheckpointStore,
)
from .context import DeepSeekHarnessRunContext
from .errors import BLOCKER_CODES, DeepSeekHarnessContractError
from .events import DeepSeekHarnessEventSequence, DeepSeekHarnessRuntimeEvent, record_of
from .proposal import (
    PROPOSAL_CONSTRAINTS,
    SCHEMA_VERSION as PROPOSAL_SCHEMA_VERSION,
    require_result,
    sign_proposal,
    validate_proposal,
)
from .session import SessionBinding, SessionRegistry


RESUMABLE_RUN_STATUSES = frozenset({"pending", "running", "interrupted"})
# Only a closed turn or an idle session is a known resting point. Any other
# last observation means the runtime outcome after a restart is unknown.
QUIESCENT_KINDS = frozenset({"turn.ended", "session.idle"})
PERSISTED_BLOCKERS = frozenset({"sequence_gap", "event_conflict"})
BLOCK_MARKER = "blocked"
_APPROVAL_REASONS = {
    "approval_mismatch": "approval_invalid",
    "approval_not_granted": "approval_inactive",
    "approval_expired": "approval_inactive",
}
_CONSTRAINTS = {
    "runtimeApprovalIsAuthority": False,
    "runtimeCompletionIsAuthority": False,
    "rawPayloadPersisted": False,
    "canonicalRuntimeIdentity": False,
}


class _Stream:
    __slots__ = (
        "binding",
        "dispatch_id",
        "plan_id",
        "plan_fingerprint",
        "sequence",
        "checkpoint",
        "proposal",
    )

    def __init__(
        self,
        binding: SessionBinding,
        dispatch_id: str,
        plan_id: str,
        plan_fingerprint: str,
        sequence: DeepSeekHarnessEventSequence,
        checkpoint: dict[str, Any] | None,
    ) -> None:
        self.binding = binding
        self.dispatch_id = dispatch_id
        self.plan_id = plan_id
        self.plan_fingerprint = plan_fingerprint
        self.sequence = sequence
        self.checkpoint = checkpoint
        # Fingerprint of the current issued result proposal, if any.
        self.proposal = checkpoint["proposalFingerprint"] if checkpoint is not None else None


class DeepSeekHarnessRuntimeAdapter:
    """Bind DSH sessions to Pipe runs and audit allowlisted runtime events."""

    __slots__ = ("_store", "_sessions", "_checkpoints", "_streams")

    def __init__(self, store: Any, sessions: Any, *, checkpoints: Any = None) -> None:
        if (
            type(store) is not LocalControlPlaneStore
            or type(sessions) is not SessionRegistry
            or (checkpoints is not None and type(checkpoints) is not DeepSeekHarnessCheckpointStore)
        ):
            raise DeepSeekHarnessContractError("contract_violation") from None
        self._store = store
        self._sessions = sessions
        self._checkpoints = checkpoints
        self._streams: dict[str, _Stream] = {}

    def begin(
        self, *, plan: Any, context: Any, binding: Any, occurred_at: Any
    ) -> dict[str, Any]:
        """Dispatch or recover a bound session for its registered Pipe run."""

        binding = self._resolve(binding, context)
        _require_timestamp(occurred_at)
        run = self._run(binding)
        _require_plan(plan, run)
        self._require_resumable(binding, run)

        stream = self._streams.get(binding.session_id)
        if stream is not None:
            return self._dispatch_result(stream, context, duplicate=True, recovered=False)
        dispatch_id = _dispatch_id(binding)
        self._require_audited_lineage(binding, dispatch_id)
        checkpoint = None
        if self._checkpoints is not None:
            checkpoint = self._checkpoints.load(binding.pipe_run_id)
        if checkpoint is not None and checkpoint["attempt"] > binding.attempt:
            raise DeepSeekHarnessContractError("binding_superseded") from None
        if checkpoint is not None and checkpoint["attempt"] == binding.attempt:
            _require_checkpoint_matches(checkpoint, binding, context, run, dispatch_id)
            return self._recover(binding, context, run, checkpoint, occurred_at)
        if dispatch_id in self._audit_keys(binding):
            raise DeepSeekHarnessContractError("recovery_required") from None

        if self._checkpoints is None:
            self._audit(binding, run["plan_id"], run["plan_fingerprint"], occurred_at, "running", dispatch_id)
            return self._open(binding, context, run, dispatch_id, None, recovered=False)
        lineage = [item.session_id for item in self._sessions.lineage(binding.pipe_run_id)]
        if checkpoint is not None and checkpoint["sessionLineage"] != lineage[: checkpoint["attempt"]]:
            raise DeepSeekHarnessContractError("checkpoint_binding_mismatch") from None
        intent = self._checkpoints.save(
            _checkpoint_document(binding, context, run, dispatch_id, lineage, occurred_at)
        )
        self._audit(binding, run["plan_id"], run["plan_fingerprint"], occurred_at, "running", dispatch_id)
        committed = self._checkpoints.save({**intent, "state": "running"})
        return self._open(binding, context, run, dispatch_id, committed, recovered=False)

    def record_event(self, *, binding: Any, context: Any, event: Any) -> dict[str, Any]:
        """Sequence, deduplicate, checkpoint and audit one normalized runtime event."""

        if type(event) is not DeepSeekHarnessRuntimeEvent:
            raise DeepSeekHarnessContractError("event_field_invalid") from None
        binding = self._resolve(binding, context)
        stream = self._streams.get(binding.session_id)
        if stream is None or stream.binding != binding:
            raise DeepSeekHarnessContractError("dispatch_missing") from None
        if event.session_id != binding.session_id:
            raise DeepSeekHarnessContractError("session_mismatch") from None
        run = self._run(binding)
        if run["plan_fingerprint"] != stream.plan_fingerprint:
            raise DeepSeekHarnessContractError("plan_mismatch") from None
        self._require_resumable(binding, run)
        self._require_unmarked(stream)
        if stream.sequence.blocked_code is not None:
            raise DeepSeekHarnessContractError("stream_blocked") from None
        self._require_current(stream)

        refused = None
        try:
            fresh = stream.sequence.admit(event)
        except DeepSeekHarnessContractError as error:
            refused = error.code
        if refused is not None:
            if refused in PERSISTED_BLOCKERS:
                self._persist_block(stream, refused, event.occurred_at)
            raise DeepSeekHarnessContractError(refused) from None
        if not fresh:
            return self._event_result(stream, event, duplicate=True)
        record = record_of(event)
        if stream.checkpoint is not None:
            stream.checkpoint = self._save_or_block(
                stream, {**stream.checkpoint, "pendingEvent": record, "updatedAt": event.occurred_at}
            )
        try:
            self._audit(
                binding,
                stream.plan_id,
                stream.plan_fingerprint,
                event.occurred_at,
                "succeeded" if event.kind == "tool.succeeded" else "running",
                event.event_id,
            )
        except DeepSeekHarnessContractError as error:
            stream.sequence.block(error.code)
        if stream.checkpoint is not None:
            records = stream.sequence.records() + [record]
            stream.checkpoint = self._save_or_block(
                stream,
                {
                    **stream.checkpoint,
                    "processedEvents": records,
                    "expectedSequence": len(records) + 1,
                    "pendingEvent": None,
                },
            )
        stream.sequence.observe(event)
        return self._event_result(stream, event, duplicate=False)

    def refuse(self, *, binding: Any, context: Any, code: Any, occurred_at: Any) -> None:
        """Record a transport or protocol refusal for a dispatched session; always raises.

        A clean end of stream at a resting point is only reported. Any other
        refusal blocks the attempt in memory, in the Pipe audit and in the
        checkpoint, so neither a fresh normalizer nor a restart can resume it.
        """

        binding = self._resolve(binding, context)
        _require_timestamp(occurred_at)
        if type(code) is not str or code not in BLOCKER_CODES:
            raise DeepSeekHarnessContractError("contract_violation") from None
        stream = self._streams.get(binding.session_id)
        if stream is None or stream.binding != binding:
            raise DeepSeekHarnessContractError("dispatch_missing") from None
        # A refusal never touches a terminal run or a broken audit chain.
        self._require_resumable(binding, self._run(binding))
        if self._marker(stream) in self._audit_keys(binding):
            raise DeepSeekHarnessContractError("stream_blocked") from None
        if (
            code == "transport_eof"
            and stream.sequence.blocked_code is None
            and _at_rest(stream.sequence.records())
        ):
            raise DeepSeekHarnessContractError(code) from None
        # Also reached when the stream is blocked only in memory, so a block
        # that failed to persist earlier is persisted now.
        self._persist_block(stream, code, occurred_at)
        stream.sequence.block(code)

    def propose(
        self,
        *,
        binding: Any,
        context: Any,
        result_ref: Any,
        result_fingerprint: Any,
        occurred_at: Any,
    ) -> dict[str, Any]:
        """Issue the inert result proposal a read-only run can later complete with."""

        binding = self._resolve(binding, context)
        _require_timestamp(occurred_at)
        require_result(result_ref, result_fingerprint)
        stream = self._quiescent_stream(binding)
        proposal = sign_proposal(
            self._proposal_core(
                stream,
                context,
                "read_result",
                occurred_at,
                result_ref=result_ref,
                result_fingerprint=result_fingerprint,
            )
        )
        if stream.checkpoint is not None:
            stream.checkpoint = self._checkpoints.save(
                {
                    **stream.checkpoint,
                    "proposalFingerprint": proposal["proposalFingerprint"],
                    "updatedAt": occurred_at,
                }
            )
        stream.proposal = proposal["proposalFingerprint"]
        return proposal

    def handoff(
        self,
        *,
        binding: Any,
        context: Any,
        plan: Any,
        action_id: Any,
        approval: Any,
        occurred_at: Any,
    ) -> dict[str, Any]:
        """Validate the exact, active Pipe ApprovalRecord and return an inert proposal.

        Nothing is applied, recorded or checkpointed: the approval must already
        be recorded in the Pipe audit, and application stays behind the governed
        apply boundary.
        """

        binding = self._resolve(binding, context)
        _require_timestamp(occurred_at)
        stream = self._quiescent_stream(binding)
        run = self._run(binding)
        _require_plan(plan, run)
        try:
            action = find_action(plan, action_id)
        except (ControlPlaneContractError, AttributeError, TypeError):
            raise DeepSeekHarnessContractError("action_not_approvable") from None
        if (
            action.get("actionType") not in MUTATING_ACTIONS
            or action.get("status") != "proposed"
            or action.get("blockerIds")
            or action.get("approvalRequired") is not True
        ):
            raise DeepSeekHarnessContractError("action_not_approvable") from None
        if not isinstance(approval, Mapping):
            raise DeepSeekHarnessContractError("approval_missing") from None
        try:
            reason = validate_approval_for_action(approval, plan, action, at=occurred_at)
        except (ControlPlaneContractError, KeyError, TypeError):
            reason = "approval_mismatch"
        if reason is not None:
            raise DeepSeekHarnessContractError(_APPROVAL_REASONS.get(reason, "approval_invalid")) from None
        decisions = [
            event["references"]["approvalId"]
            for event in self._store.list_events(binding.pipe_run_id)
            if event["eventType"] == "approval.recorded"
            and event["references"]["actionId"] == action["actionId"]
        ]
        if approval["approvalId"] not in decisions:
            raise DeepSeekHarnessContractError("approval_missing") from None
        if decisions[-1] != approval["approvalId"]:
            # A later decision for the same action (for example a revocation)
            # supersedes this record.
            raise DeepSeekHarnessContractError("approval_inactive") from None
        return sign_proposal(
            self._proposal_core(
                stream,
                context,
                "action_handoff",
                occurred_at,
                action={
                    "actionId": action["actionId"],
                    "actionType": action["actionType"],
                    "approvalId": approval["approvalId"],
                    "idempotencyKey": approval["idempotencyKey"],
                    "scope": dict(approval["scope"]),
                },
            )
        )

    def complete(
        self, *, binding: Any, context: Any, proposal: Any, occurred_at: Any
    ) -> dict[str, Any]:
        """The only way this adapter completes a Pipe run: the issued, current result.

        Idle, turn end, EOF and status signals never reach here; the caller must
        present the unaltered result proposal this adapter issued for the
        session's current state, with the Pipe audit chain intact.
        """

        binding = self._resolve(binding, context)
        _require_timestamp(occurred_at)
        stream = self._quiescent_stream(binding)
        if stream.proposal is None:
            raise DeepSeekHarnessContractError("proposal_missing") from None
        validate_proposal(proposal)
        if (
            proposal["proposalFingerprint"] != stream.proposal
            or proposal["kind"] != "read_result"
            or proposal["eventWatermark"] != stream.sequence.expected_sequence - 1
        ):
            raise DeepSeekHarnessContractError("proposal_mismatch") from None
        digest = proposal["proposalFingerprint"].split(":", 1)[1]
        failed = False
        event: dict[str, Any] = {}
        try:
            event = self._store.record_run_event(
                binding.pipe_run_id,
                occurred_at=occurred_at,
                event_type="run.completed",
                event_status="succeeded",
                run_status="completed",
                plan_id=stream.plan_id,
                plan_fingerprint=stream.plan_fingerprint,
                idempotency_key=f"{stream.dispatch_id}:{digest}",
                attempt=binding.attempt,
            )
        except Exception:
            # Any storage failure, not only contract errors, fails closed.
            failed = True
        if failed:
            raise DeepSeekHarnessContractError("audit_write_failed") from None
        if stream.checkpoint is not None:
            stream.checkpoint = self._checkpoints.save(
                {**stream.checkpoint, "state": "completed", "updatedAt": occurred_at}
            )
        return {
            "runId": binding.pipe_run_id,
            "planId": stream.plan_id,
            "sessionId": binding.session_id,
            "attempt": binding.attempt,
            "dispatchId": stream.dispatch_id,
            "proposalFingerprint": proposal["proposalFingerprint"],
            "completionEventId": event["eventId"],
            "state": self._store.get_run(binding.pipe_run_id)["status"],
            "constraints": dict(_CONSTRAINTS),
        }

    def _quiescent_stream(self, binding: SessionBinding) -> _Stream:
        stream = self._streams.get(binding.session_id)
        if stream is None or stream.binding != binding:
            raise DeepSeekHarnessContractError("dispatch_missing") from None
        run = self._run(binding)
        if run["plan_fingerprint"] != stream.plan_fingerprint:
            raise DeepSeekHarnessContractError("plan_mismatch") from None
        self._require_resumable(binding, run)
        self._require_unmarked(stream)
        if stream.sequence.blocked_code is not None:
            raise DeepSeekHarnessContractError("stream_blocked") from None
        self._require_current(stream)
        if not _at_rest(stream.sequence.records()):
            raise DeepSeekHarnessContractError("stream_not_quiescent") from None
        return stream

    def _proposal_core(
        self,
        stream: _Stream,
        context: DeepSeekHarnessRunContext,
        kind: str,
        occurred_at: str,
        *,
        result_ref: str | None = None,
        result_fingerprint: str | None = None,
        action: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        binding = stream.binding
        return {
            "schemaVersion": PROPOSAL_SCHEMA_VERSION,
            "kind": kind,
            "runId": binding.pipe_run_id,
            "planId": stream.plan_id,
            "planFingerprint": stream.plan_fingerprint,
            "linearTicketId": context.linear_ticket_id,
            "workflow": context.workflow,
            "sessionId": binding.session_id,
            "attempt": binding.attempt,
            "dispatchId": stream.dispatch_id,
            "bindingFingerprint": binding.binding_fingerprint,
            "contextFingerprint": binding.context_fingerprint,
            "eventWatermark": stream.sequence.expected_sequence - 1,
            "resultRef": result_ref,
            "resultFingerprint": result_fingerprint,
            "action": action,
            "proposedAt": occurred_at,
            "constraints": dict(PROPOSAL_CONSTRAINTS),
        }

    def _recover(
        self,
        binding: SessionBinding,
        context: DeepSeekHarnessRunContext,
        run: Mapping[str, Any],
        checkpoint: dict[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Reconcile a checkpoint with the Pipe audit, forward only, before reopening."""

        state = checkpoint["state"]
        if state == "completed":
            raise DeepSeekHarnessContractError("run_terminal") from None
        if state == "outcome_unknown":
            raise DeepSeekHarnessContractError("outcome_unknown") from None
        if state == "blocked":
            raise DeepSeekHarnessContractError("stream_blocked") from None
        keys = self._audit_keys(binding)
        dispatch_id = checkpoint["dispatchId"]
        if state == "dispatch_pending":
            # begin never returned, so nothing was dispatched to the runtime.
            if dispatch_id not in keys:
                self._audit(
                    binding, run["plan_id"], run["plan_fingerprint"], occurred_at, "running", dispatch_id
                )
            committed = self._checkpoints.save(
                {**checkpoint, "state": "running", "updatedAt": occurred_at}
            )
            return self._open(binding, context, run, dispatch_id, committed, recovered=True)

        records = list(checkpoint["processedEvents"])
        if dispatch_id not in keys or any(item["eventId"] not in keys for item in records):
            raise DeepSeekHarnessContractError("checkpoint_audit_mismatch") from None
        pending = checkpoint["pendingEvent"]
        if pending is not None and pending["eventId"] in keys:
            records.append(dict(pending))
        audited_events = {key for key in keys if key.startswith("DHE-")}
        if audited_events != {item["eventId"] for item in records}:
            raise DeepSeekHarnessContractError("checkpoint_stale") from None
        reconciled = {
            **checkpoint,
            "processedEvents": records,
            "expectedSequence": len(records) + 1,
            "pendingEvent": None,
            "updatedAt": occurred_at,
        }
        if not _at_rest(records):
            self._checkpoints.save(
                {**reconciled, "state": "outcome_unknown", "blockerCode": "outcome_unknown"}
            )
            raise DeepSeekHarnessContractError("outcome_unknown") from None
        if reconciled != {**checkpoint, "updatedAt": occurred_at} or pending is not None:
            checkpoint = self._checkpoints.save(reconciled)
        return self._open(binding, context, run, dispatch_id, checkpoint, recovered=True)

    def _open(
        self,
        binding: SessionBinding,
        context: DeepSeekHarnessRunContext,
        run: Mapping[str, Any],
        dispatch_id: str,
        checkpoint: dict[str, Any] | None,
        *,
        recovered: bool,
    ) -> dict[str, Any]:
        sequence = (
            DeepSeekHarnessEventSequence.restore(checkpoint["processedEvents"])
            if checkpoint is not None
            else DeepSeekHarnessEventSequence()
        )
        stream = _Stream(
            binding, dispatch_id, run["plan_id"], run["plan_fingerprint"], sequence, checkpoint
        )
        for session_id, existing in list(self._streams.items()):
            if existing.binding.pipe_run_id == binding.pipe_run_id:
                del self._streams[session_id]
        self._streams[binding.session_id] = stream
        return self._dispatch_result(stream, context, duplicate=recovered, recovered=recovered)

    def _persist_block(self, stream: _Stream, code: str, occurred_at: str) -> None:
        """Persist a block in the Pipe audit, then the checkpoint; raise if either fails.

        The audit marker is the authority: ``begin``, ``record_event``,
        ``propose`` and ``complete`` refuse an attempt that carries it even when
        the checkpoint is missing, stale or rewritten, or another adapter holds
        the stream. Any storage failure maps to a fixed code, and the
        checkpoint block is still attempted after an audit failure. A run that
        is no longer resumable is never rewritten.
        """

        stream.sequence.block_quietly(code)
        failure = None
        binding = stream.binding
        try:
            if self._store.get_run(binding.pipe_run_id)["status"] not in RESUMABLE_RUN_STATUSES:
                failure = "run_terminal"
            elif self._marker(stream) not in self._audit_keys(binding):
                self._store.record_run_event(
                    binding.pipe_run_id,
                    occurred_at=occurred_at,
                    event_type="run.interrupted",
                    event_status="blocked",
                    run_status="interrupted",
                    plan_id=stream.plan_id,
                    plan_fingerprint=stream.plan_fingerprint,
                    reason_code="adapter_conflict",
                    idempotency_key=self._marker(stream),
                    attempt=binding.attempt,
                )
        except Exception:
            # Any storage failure, not only contract errors, fails closed.
            failure = "audit_write_failed"
        if failure != "run_terminal" and stream.checkpoint is not None:
            try:
                stream.checkpoint = self._checkpoints.save(
                    {
                        **stream.checkpoint,
                        "state": "blocked",
                        "blockerCode": code,
                        "pendingEvent": None,
                        "updatedAt": occurred_at,
                    }
                )
            except Exception as error:
                code_of = error.code if isinstance(error, DeepSeekHarnessContractError) else None
                failure = failure or code_of or "checkpoint_write_failed"
        if failure is not None:
            raise DeepSeekHarnessContractError(failure) from None

    @staticmethod
    def _marker(stream: _Stream) -> str:
        return f"{stream.dispatch_id}:{BLOCK_MARKER}"

    def _require_current(self, stream: _Stream) -> None:
        """Refuse a stale view: the audit and the checkpoint must match this stream.

        Another adapter instance may have advanced, blocked or completed the
        attempt; acting on this in-memory view would then tolerate a gap or
        complete an unknown outcome.
        """

        audited = {key for key in self._audit_keys(stream.binding) if key.startswith("DHE-")}
        if audited != {record["eventId"] for record in stream.sequence.records()}:
            stream.sequence.block_quietly("checkpoint_stale")
            raise DeepSeekHarnessContractError("checkpoint_stale") from None
        if stream.checkpoint is not None:
            stored = self._checkpoints.load(stream.binding.pipe_run_id)
            if stored is not None and stored["state"] == "blocked":
                stream.sequence.block_quietly("stream_blocked")
                raise DeepSeekHarnessContractError("stream_blocked") from None
            if stored != stream.checkpoint or stored["state"] != "running":
                stream.sequence.block_quietly("checkpoint_stale")
                raise DeepSeekHarnessContractError("checkpoint_stale") from None

    def _require_unmarked(self, stream: _Stream) -> None:
        """Refuse a stream whose attempt carries the audit block marker."""

        if self._marker(stream) in self._audit_keys(stream.binding):
            stream.sequence.block_quietly("stream_blocked")
            raise DeepSeekHarnessContractError("stream_blocked") from None

    def _save_or_block(self, stream: _Stream, document: dict[str, Any]) -> dict[str, Any]:
        try:
            return self._checkpoints.save(document)
        except DeepSeekHarnessContractError as error:
            stream.sequence.block(error.code)
            raise

    def _resolve(self, binding: Any, context: Any) -> SessionBinding:
        if type(binding) is not SessionBinding:
            raise DeepSeekHarnessContractError("binding_field_invalid") from None
        resolved = self._sessions.resolve(
            pipe_run_id=binding.pipe_run_id,
            session_id=binding.session_id,
            attempt=binding.attempt,
            consumer_id=binding.consumer_id,
            context=context,
        )
        if resolved != binding:
            raise DeepSeekHarnessContractError("binding_unknown") from None
        return resolved

    def _run(self, binding: SessionBinding) -> dict[str, Any]:
        try:
            return self._store.get_run(binding.pipe_run_id)
        except ControlPlaneStateError:
            raise DeepSeekHarnessContractError("run_unregistered") from None

    def _require_resumable(self, binding: SessionBinding, run: Mapping[str, Any]) -> None:
        if not self._store.verify_audit_chain(binding.pipe_run_id):
            raise DeepSeekHarnessContractError("audit_chain_invalid") from None
        if run["status"] not in RESUMABLE_RUN_STATUSES:
            raise DeepSeekHarnessContractError("run_terminal") from None

    def _audit_keys(self, binding: SessionBinding) -> set[str]:
        """Idempotency keys the Pipe audit holds for this binding's attempt."""

        return {
            event["references"]["idempotencyKey"]
            for event in self._store.list_events(binding.pipe_run_id)
            if event["checkpoint"]["attempt"] == binding.attempt
            and event["references"]["idempotencyKey"] is not None
        }

    def _require_audited_lineage(self, binding: SessionBinding, dispatch_id: str) -> None:
        """Refuse a binding the Pipe audit contradicts, whatever the registry says.

        Each audited attempt must belong to the dispatch of the registry's
        binding for that attempt; no later attempt may be audited; and a
        blocked attempt stays blocked.
        """

        lineage = self._sessions.lineage(binding.pipe_run_id)
        audited: dict[int, set[str]] = {}
        markers: set[str] = set()
        for event in self._store.list_events(binding.pipe_run_id):
            key = event["references"]["idempotencyKey"]
            if key is None or not key.startswith("DHD-"):
                continue
            base, _, suffix = key.partition(":")
            audited.setdefault(event["checkpoint"]["attempt"], set()).add(base)
            if suffix == BLOCK_MARKER:
                markers.add(base)
        if any(attempt > binding.attempt for attempt in audited):
            raise DeepSeekHarnessContractError("binding_superseded") from None
        for attempt, bases in audited.items():
            if not 1 <= attempt <= len(lineage) or bases != {_dispatch_id(lineage[attempt - 1])}:
                raise DeepSeekHarnessContractError("binding_immutable") from None
        if dispatch_id in markers:
            raise DeepSeekHarnessContractError("stream_blocked") from None

    def _audit(
        self,
        binding: SessionBinding,
        plan_id: str,
        plan_fingerprint: str,
        occurred_at: str,
        event_status: str,
        idempotency_key: str,
    ) -> None:
        failed = False
        try:
            self._store.record_run_event(
                binding.pipe_run_id,
                occurred_at=occurred_at,
                event_type="run.resumed",
                event_status=event_status,
                run_status="running",
                plan_id=plan_id,
                plan_fingerprint=plan_fingerprint,
                idempotency_key=idempotency_key,
                attempt=binding.attempt,
            )
        except Exception:
            # Any storage failure, not only contract errors, fails closed.
            failed = True
        if failed:
            raise DeepSeekHarnessContractError("audit_write_failed") from None

    def _dispatch_result(
        self,
        stream: _Stream,
        context: DeepSeekHarnessRunContext,
        *,
        duplicate: bool,
        recovered: bool,
    ) -> dict[str, Any]:
        binding = stream.binding
        return {
            "runId": binding.pipe_run_id,
            "planId": stream.plan_id,
            "sessionId": binding.session_id,
            "attempt": binding.attempt,
            "workflow": context.workflow,
            "linearTicketId": context.linear_ticket_id,
            "bindingFingerprint": binding.binding_fingerprint,
            "contextFingerprint": binding.context_fingerprint,
            "dispatchId": stream.dispatch_id,
            "state": self._store.get_run(binding.pipe_run_id)["status"],
            "expectedSequence": stream.sequence.expected_sequence,
            "duplicate": duplicate,
            "recovered": recovered,
            "constraints": dict(_CONSTRAINTS),
        }

    def _event_result(
        self, stream: _Stream, event: DeepSeekHarnessRuntimeEvent, *, duplicate: bool
    ) -> dict[str, Any]:
        binding = stream.binding
        return {
            "runId": binding.pipe_run_id,
            "sessionId": binding.session_id,
            "attempt": binding.attempt,
            "dispatchId": stream.dispatch_id,
            "eventId": event.event_id,
            "kind": event.kind,
            "sequence": event.sequence,
            "expectedSequence": stream.sequence.expected_sequence,
            "duplicate": duplicate,
            "state": self._store.get_run(binding.pipe_run_id)["status"],
            "constraints": dict(_CONSTRAINTS),
        }


def _at_rest(records: list[dict[str, Any]]) -> bool:
    """A closed turn or an idle session with no turn or tool call left open."""

    turn_open = False
    open_tools = 0
    for record in records:
        kind = record["kind"]
        if kind == "turn.started":
            turn_open = True
        elif kind == "turn.ended":
            turn_open = False
        elif kind == "tool.started":
            open_tools += 1
        elif kind == "tool.succeeded":
            open_tools -= 1
    return bool(records) and records[-1]["kind"] in QUIESCENT_KINDS and not turn_open and open_tools == 0


def _dispatch_id(binding: SessionBinding) -> str:
    return stable_id(
        "DHD",
        {
            "pipeRunId": binding.pipe_run_id,
            "sessionId": binding.session_id,
            "attempt": binding.attempt,
            "bindingFingerprint": binding.binding_fingerprint,
        },
    )


def _checkpoint_document(
    binding: SessionBinding,
    context: DeepSeekHarnessRunContext,
    run: Mapping[str, Any],
    dispatch_id: str,
    lineage: list[str],
    updated_at: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": CHECKPOINT_SCHEMA_VERSION,
        "runId": binding.pipe_run_id,
        "planId": run["plan_id"],
        "planFingerprint": run["plan_fingerprint"],
        "linearTicketId": context.linear_ticket_id,
        "workflow": context.workflow,
        "contextFingerprint": binding.context_fingerprint,
        "workspaceFingerprint": binding.workspace_fingerprint,
        "sessionId": binding.session_id,
        "attempt": binding.attempt,
        "bindingFingerprint": binding.binding_fingerprint,
        "dispatchId": dispatch_id,
        "sessionLineage": list(lineage),
        "state": "dispatch_pending",
        "expectedSequence": 1,
        "processedEvents": [],
        "pendingEvent": None,
        "blockerCode": None,
        "proposalFingerprint": None,
        "updatedAt": updated_at,
        "constraints": dict(CHECKPOINT_CONSTRAINTS),
    }


def _require_plan(plan: Any, run: Mapping[str, Any]) -> None:
    if not isinstance(plan, Mapping) or plan.get("planId") != run["plan_id"]:
        raise DeepSeekHarnessContractError("plan_mismatch") from None
    try:
        plan_fingerprint = fingerprint(plan)
    except ControlPlaneContractError:
        raise DeepSeekHarnessContractError("plan_mismatch") from None
    if plan_fingerprint != run["plan_fingerprint"]:
        raise DeepSeekHarnessContractError("plan_mismatch") from None


def _require_checkpoint_matches(
    checkpoint: Mapping[str, Any],
    binding: SessionBinding,
    context: DeepSeekHarnessRunContext,
    run: Mapping[str, Any],
    dispatch_id: str,
) -> None:
    expected = {
        "sessionId": binding.session_id,
        "bindingFingerprint": binding.binding_fingerprint,
        "dispatchId": dispatch_id,
        "planId": run["plan_id"],
        "planFingerprint": run["plan_fingerprint"],
        "contextFingerprint": binding.context_fingerprint,
        "workspaceFingerprint": binding.workspace_fingerprint,
        "linearTicketId": context.linear_ticket_id,
        "workflow": context.workflow,
    }
    if any(checkpoint[key] != value for key, value in expected.items()):
        raise DeepSeekHarnessContractError("checkpoint_binding_mismatch") from None


def _require_timestamp(value: Any) -> None:
    try:
        parse_datetime(value)
    except ControlPlaneContractError:
        raise DeepSeekHarnessContractError("timestamp_invalid") from None
