"""Immutable run/session/attempt binding and forward-only lineage (ADR-004 D3).

A binding pins every D3 element: Pipe run, DSH session and attempt, DSH and
protocol versions, profile and plugin-tree hash, synthetic route/model,
workspace and context hashes, and the single consumer. Bindings are never
rewritten: any change requires a new attempt with a new session. Binding
metadata is identifiers, hashes and counts only; never raw runtime payload.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from pipe_venture_builder.adapters.safety import payload_is_safe
from pipe_venture_builder.control_plane.model import FINGERPRINT_PATTERN, fingerprint

from .context import DeepSeekHarnessRunContext
from .errors import DeepSeekHarnessContractError


SCHEMA_VERSION = "0.1.0"
# Synthetic identifiers only; never a real provider route or model (ADR-004).
SYNTHETIC_ROUTE_IDS = frozenset({"synthetic-route-a", "synthetic-route-b"})
SYNTHETIC_MODEL_IDS = frozenset({"synthetic-model-a", "synthetic-model-b"})
# ADR-004 D9: sdk-minimal exposes danger-full-access, shell and editor.
FORBIDDEN_PROFILE_IDS = frozenset({"sdk-minimal", "danger-full-access"})
MAX_ATTEMPTS = 1024
BINDING_ELEMENTS = (
    "pipe_run_id",
    "session_id",
    "attempt",
    "dsh_version",
    "protocol_version",
    "profile_id",
    "plugin_tree_fingerprint",
    "route_id",
    "model_id",
    "workspace_fingerprint",
    "context_fingerprint",
    "consumer_id",
)

_RUN_ID = re.compile(r"RUN-[a-f0-9]{12}")
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+=-]{0,127}")


@dataclass(frozen=True)
class SessionBinding:
    """One attempt of one Pipe run bound to exactly one DSH session.

    Validation runs in ``__post_init__``, so direct construction and
    ``dataclasses.replace`` are held to the same contract as ``build``.
    """

    pipe_run_id: str
    session_id: str
    attempt: int
    dsh_version: str
    protocol_version: str
    profile_id: str
    plugin_tree_fingerprint: str
    route_id: str
    model_id: str
    workspace_fingerprint: str
    context_fingerprint: str
    consumer_id: str
    binding_fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.pipe_run_id) is not str or _RUN_ID.fullmatch(self.pipe_run_id) is None:
            raise DeepSeekHarnessContractError("binding_field_invalid") from None
        if type(self.attempt) is not int or not 1 <= self.attempt <= MAX_ATTEMPTS:
            raise DeepSeekHarnessContractError("binding_field_invalid") from None
        for value in (
            self.session_id,
            self.dsh_version,
            self.protocol_version,
            self.profile_id,
            self.consumer_id,
        ):
            _require_identifier(value)
        folded_profile = self.profile_id.casefold()
        if folded_profile in FORBIDDEN_PROFILE_IDS or "danger-full-access" in folded_profile:
            raise DeepSeekHarnessContractError("profile_forbidden") from None
        for value in (
            self.plugin_tree_fingerprint,
            self.workspace_fingerprint,
            self.context_fingerprint,
        ):
            if type(value) is not str or FINGERPRINT_PATTERN.fullmatch(value) is None:
                raise DeepSeekHarnessContractError("fingerprint_invalid") from None
        if type(self.route_id) is not str or self.route_id not in SYNTHETIC_ROUTE_IDS:
            raise DeepSeekHarnessContractError("route_not_allowlisted") from None
        if type(self.model_id) is not str or self.model_id not in SYNTHETIC_MODEL_IDS:
            raise DeepSeekHarnessContractError("model_not_allowlisted") from None
        object.__setattr__(self, "binding_fingerprint", fingerprint(self._core()))

    @classmethod
    def build(
        cls,
        *,
        pipe_run_id: Any,
        session_id: Any,
        attempt: Any,
        dsh_version: Any,
        protocol_version: Any,
        profile_id: Any,
        plugin_tree_fingerprint: Any,
        route_id: Any,
        model_id: Any,
        workspace_fingerprint: Any,
        context_fingerprint: Any,
        consumer_id: Any,
    ) -> SessionBinding:
        return cls(
            pipe_run_id=pipe_run_id,
            session_id=session_id,
            attempt=attempt,
            dsh_version=dsh_version,
            protocol_version=protocol_version,
            profile_id=profile_id,
            plugin_tree_fingerprint=plugin_tree_fingerprint,
            route_id=route_id,
            model_id=model_id,
            workspace_fingerprint=workspace_fingerprint,
            context_fingerprint=context_fingerprint,
            consumer_id=consumer_id,
        )

    def document(self) -> dict[str, Any]:
        """Return a fresh metadata-only document of the binding."""

        document = self._core()
        document["bindingFingerprint"] = self.binding_fingerprint
        return document

    def _core(self) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "pipeRunId": self.pipe_run_id,
            "sessionId": self.session_id,
            "attempt": self.attempt,
            "dshVersion": self.dsh_version,
            "protocolVersion": self.protocol_version,
            "profileId": self.profile_id,
            "pluginTreeFingerprint": self.plugin_tree_fingerprint,
            "routeId": self.route_id,
            "modelId": self.model_id,
            "workspaceFingerprint": self.workspace_fingerprint,
            "contextFingerprint": self.context_fingerprint,
            "consumerId": self.consumer_id,
        }


class SessionRegistry:
    """In-memory, per-instance registry enforcing D3 binding invariants."""

    __slots__ = ("_by_session", "_by_run")

    def __init__(self) -> None:
        self._by_session: dict[str, SessionBinding] = {}
        self._by_run: dict[str, list[SessionBinding]] = {}

    def bind(self, binding: Any) -> SessionBinding:
        """Bind a new attempt; refusal order is consumer, immutability, lineage.

        * ``consumer_conflict``: the session or the (run, attempt) is already
          bound to another consumer.
        * ``binding_immutable``: the session or the (run, attempt) is already
          bound; bindings are never rewritten or reused.
        * ``lineage_invalid``: the attempt is not exactly the next one.
        """

        binding = _revalidated(binding)
        lineage = self._by_run.get(binding.pipe_run_id, [])
        existing = [
            candidate
            for candidate in (
                self._by_session.get(binding.session_id),
                lineage[binding.attempt - 1] if binding.attempt <= len(lineage) else None,
            )
            if candidate is not None
        ]
        if any(candidate.consumer_id != binding.consumer_id for candidate in existing):
            raise DeepSeekHarnessContractError("consumer_conflict") from None
        if existing:
            raise DeepSeekHarnessContractError("binding_immutable") from None
        if binding.attempt != len(lineage) + 1:
            raise DeepSeekHarnessContractError("lineage_invalid") from None
        self._by_session[binding.session_id] = binding
        self._by_run.setdefault(binding.pipe_run_id, []).append(binding)
        return binding

    def lineage(self, pipe_run_id: Any) -> tuple[SessionBinding, ...]:
        if type(pipe_run_id) is not str:
            return ()
        return tuple(self._by_run.get(pipe_run_id, ()))

    def resolve(
        self,
        *,
        pipe_run_id: Any,
        session_id: Any,
        attempt: Any,
        consumer_id: Any,
        context: Any,
    ) -> SessionBinding:
        """Return the binding only for its latest attempt, consumer and context."""

        binding = (
            self._by_session.get(session_id) if type(session_id) is str else None
        )
        if (
            binding is None
            or binding.pipe_run_id != pipe_run_id
            or type(attempt) is not int
            or binding.attempt != attempt
        ):
            raise DeepSeekHarnessContractError("binding_unknown") from None
        if consumer_id != binding.consumer_id:
            raise DeepSeekHarnessContractError("consumer_conflict") from None
        if self._by_run[binding.pipe_run_id][-1] is not binding:
            raise DeepSeekHarnessContractError("binding_superseded") from None
        if (
            type(context) is not DeepSeekHarnessRunContext
            or context.context_fingerprint != binding.context_fingerprint
            or context.workspace_fingerprint != binding.workspace_fingerprint
        ):
            raise DeepSeekHarnessContractError("context_mismatch") from None
        return binding


def _require_identifier(value: Any) -> None:
    if (
        type(value) is not str
        or _IDENTIFIER.fullmatch(value) is None
        or not payload_is_safe(value)
    ):
        raise DeepSeekHarnessContractError("binding_field_invalid") from None


def _revalidated(binding: Any) -> SessionBinding:
    """Rebuild from elements so post-construction tampering is refused."""

    if type(binding) is not SessionBinding:
        raise DeepSeekHarnessContractError("binding_field_invalid") from None
    rebuilt = SessionBinding(
        **{element: getattr(binding, element) for element in BINDING_ELEMENTS}
    )
    if rebuilt != binding:
        raise DeepSeekHarnessContractError("binding_field_invalid") from None
    return rebuilt
