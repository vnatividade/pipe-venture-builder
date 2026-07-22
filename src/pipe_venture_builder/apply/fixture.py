"""Local reversible fixture adapter used to validate the apply state machine."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from pipe_venture_builder.control_plane.model import (
    ControlPlaneContractError,
    require_fingerprint,
    safe_identifier,
)

from .contracts import (
    ApplyAdapterConflict,
    ApplyAdapterFailure,
    ApplyInterrupted,
    ApplyResult,
    TargetObservation,
    VerificationResult,
)


APPLY_BEHAVIORS = frozenset({"success", "interrupt_once", "fail", "conflict"})
VERIFY_BEHAVIORS = frozenset({"success", "fail_once", "fail"})


class FixtureApplyAdapter:
    """Mutate an in-memory normalized fixture and support explicit rollback."""

    adapter_name = "fixture"

    def __init__(self, fixture: Mapping[str, Any]) -> None:
        self._configuration = _validate_fixture(fixture)
        self._state = {
            action_id: {
                "exists": item["beforeExists"],
                "fingerprint": item["beforeFingerprint"],
            }
            for action_id, item in self._configuration.items()
        }
        self._applications: dict[str, ApplyResult] = {}
        self._interrupted: set[str] = set()
        self._verify_failed_once: set[str] = set()
        self.apply_calls = 0
        self.inspect_calls = 0
        self.verify_calls = 0
        self.mutation_count = 0

    def inspect(self, action: Mapping[str, Any]) -> TargetObservation:
        self.inspect_calls += 1
        state = self._state_for(action)
        return TargetObservation(state["exists"], state["fingerprint"])

    def apply(
        self, action: Mapping[str, Any], *, idempotency_key: str
    ) -> ApplyResult:
        self.apply_calls += 1
        safe_identifier(idempotency_key)
        if idempotency_key in self._applications:
            prior = self._applications[idempotency_key]
            return ApplyResult(
                result_ref=prior.result_ref,
                result_fingerprint=prior.result_fingerprint,
                already_applied=True,
            )
        configuration = self._configuration_for(action)
        behavior = configuration["applyBehavior"]
        if behavior == "conflict":
            raise ApplyAdapterConflict("fixture target rejected the transition")
        if behavior == "fail":
            raise ApplyAdapterFailure("fixture apply failed")
        result = ApplyResult(
            result_ref=configuration["resultRef"],
            result_fingerprint=configuration["afterFingerprint"],
        )
        self._state[action["actionId"]] = {
            "exists": True,
            "fingerprint": configuration["afterFingerprint"],
        }
        self._applications[idempotency_key] = result
        self.mutation_count += 1
        if behavior == "interrupt_once" and idempotency_key not in self._interrupted:
            self._interrupted.add(idempotency_key)
            raise ApplyInterrupted("fixture interrupted after idempotent mutation")
        return result

    def verify(
        self, action: Mapping[str, Any], result: ApplyResult
    ) -> VerificationResult:
        self.verify_calls += 1
        configuration = self._configuration_for(action)
        behavior = configuration["verifyBehavior"]
        if behavior == "fail":
            return VerificationResult(False, self._state_for(action)["fingerprint"])
        if behavior == "fail_once" and action["actionId"] not in self._verify_failed_once:
            self._verify_failed_once.add(action["actionId"])
            return VerificationResult(False, self._state_for(action)["fingerprint"])
        state = self._state_for(action)
        verified = (
            state["exists"]
            and state["fingerprint"] == configuration["afterFingerprint"]
            and result.result_fingerprint == configuration["afterFingerprint"]
        )
        return VerificationResult(verified, state["fingerprint"])

    def rollback(self, action_id: str) -> None:
        """Reset one fixture action; this never touches an external system."""

        configuration = self._configuration[action_id]
        self._state[action_id] = {
            "exists": configuration["beforeExists"],
            "fingerprint": configuration["beforeFingerprint"],
        }
        keys = [
            key
            for key, result in self._applications.items()
            if result.result_ref == configuration["resultRef"]
        ]
        for key in keys:
            del self._applications[key]

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self._state)

    def _configuration_for(self, action: Mapping[str, Any]) -> dict[str, Any]:
        action_id = action.get("actionId")
        if action_id not in self._configuration:
            raise ApplyAdapterFailure("fixture action is not configured")
        return self._configuration[action_id]

    def _state_for(self, action: Mapping[str, Any]) -> dict[str, Any]:
        action_id = action.get("actionId")
        if action_id not in self._state:
            raise ApplyAdapterFailure("fixture action is not configured")
        return self._state[action_id]


def _validate_fixture(fixture: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if not isinstance(fixture, Mapping):
        raise ControlPlaneContractError("fixture must be a mapping")
    if set(fixture) != {"schemaVersion", "adapter", "actions"}:
        raise ControlPlaneContractError("fixture fields do not match the contract")
    if fixture["schemaVersion"] != "0.1.0" or fixture["adapter"] != "fixture":
        raise ControlPlaneContractError("unsupported fixture adapter contract")
    if not isinstance(fixture["actions"], list):
        raise ControlPlaneContractError("fixture actions must be an array")
    configuration: dict[str, dict[str, Any]] = {}
    required = {
        "actionId",
        "beforeExists",
        "beforeFingerprint",
        "afterFingerprint",
        "resultRef",
        "applyBehavior",
        "verifyBehavior",
    }
    for item in fixture["actions"]:
        if not isinstance(item, Mapping) or set(item) != required:
            raise ControlPlaneContractError("fixture action fields are invalid")
        action_id = safe_identifier(item["actionId"])
        if action_id in configuration:
            raise ControlPlaneContractError("fixture action identity must be unique")
        if not isinstance(item["beforeExists"], bool):
            raise ControlPlaneContractError("fixture existence must be boolean")
        before = require_fingerprint(item["beforeFingerprint"], nullable=True)
        after = require_fingerprint(item["afterFingerprint"])
        if item["beforeExists"] != (before is not None):
            raise ControlPlaneContractError("fixture before state is inconsistent")
        if item["applyBehavior"] not in APPLY_BEHAVIORS:
            raise ControlPlaneContractError("invalid fixture apply behavior")
        if item["verifyBehavior"] not in VERIFY_BEHAVIORS:
            raise ControlPlaneContractError("invalid fixture verify behavior")
        configuration[action_id] = {
            **item,
            "resultRef": safe_identifier(item["resultRef"]),
            "beforeFingerprint": before,
            "afterFingerprint": after,
        }
    return configuration
