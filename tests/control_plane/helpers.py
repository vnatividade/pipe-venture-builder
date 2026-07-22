from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from pipe_venture_builder.control_plane import build_approval_record
from pipe_venture_builder.control_plane.model import fingerprint
from pipe_venture_builder.reconcile import plan_reconciliation
from tests.helpers import REPOSITORY_ROOT
from tests.reconcile.helpers import baseline_with_intent, linear_record, snapshot


DECIDED_AT = "2026-07-21T13:00:00Z"
EXECUTED_AT = "2026-07-21T14:00:00Z"
EXPIRES_AT = "2026-07-21T15:00:00Z"


def schema(name: str) -> dict[str, Any]:
    return json.loads(
        (REPOSITORY_ROOT / "schemas" / name).read_text(encoding="utf-8")
    )


def assert_schema_valid(test_case: Any, name: str, value: Any) -> None:
    contract = schema(name)
    Draft202012Validator.check_schema(contract)
    findings = list(
        Draft202012Validator(
            contract, format_checker=FormatChecker()
        ).iter_errors(value)
    )
    test_case.assertEqual(findings, [], [finding.message for finding in findings])


def create_plan(
    *,
    generated_at: str = "2026-07-21T12:00:00Z",
    observed_at: str = "2026-07-21T11:00:00Z",
) -> dict[str, Any]:
    baseline = baseline_with_intent(
        action_type="create",
        target_ref=None,
        match_strategy="manual",
        confidence="high",
        title="Create governed ticket",
        generated_at=generated_at,
    )
    return plan_reconciliation(
        baseline,
        [
            snapshot(
                [],
                captured_at=observed_at,
                snapshot_id=(
                    "ES-linear-111111111111"
                    if observed_at.startswith("2026-07-21")
                    else "ES-linear-222222222222"
                ),
            )
        ],
    )


def update_plan() -> dict[str, Any]:
    baseline = baseline_with_intent(
        action_type="update",
        target_ref="PIP-712",
        match_strategy="explicit_reference",
        confidence="high",
        title="Update governed ticket",
    )
    record = linear_record(
        "issue-712", "PIP-712", title="Update governed ticket"
    )
    return plan_reconciliation(baseline, [snapshot([record])])


def approval_for(
    plan: dict[str, Any],
    *,
    decided_at: str = DECIDED_AT,
    expires_at: str = EXPIRES_AT,
    decision: str = "approved",
) -> dict[str, Any]:
    return build_approval_record(
        plan,
        plan["actions"][0]["actionId"],
        actor_id="founder",
        decided_at=decided_at,
        expires_at=expires_at,
        source_ref="linear:PIP-712",
        decision=decision,
    )


def fixture_for(
    plan: dict[str, Any],
    *,
    apply_behavior: str = "success",
    verify_behavior: str = "success",
) -> dict[str, Any]:
    action = plan["actions"][0]
    before = action["targetFingerprint"]
    return {
        "schemaVersion": "0.1.0",
        "adapter": "fixture",
        "actions": [
            {
                "actionId": action["actionId"],
                "beforeExists": before is not None,
                "beforeFingerprint": before,
                "afterFingerprint": fingerprint(
                    {"actionId": action["actionId"], "state": "after"}
                ),
                "resultRef": f"fixture:{action['actionId']}",
                "applyBehavior": apply_behavior,
                "verifyBehavior": verify_behavior,
            }
        ],
    }


def write_json(path: Path, value: Any) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path
