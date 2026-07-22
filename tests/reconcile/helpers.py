from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from pipe_venture_builder.adapters.snapshot import make_record
from tests.helpers import REPOSITORY_ROOT, valid_baseline


FIXTURE_ROOT = REPOSITORY_ROOT / "tests/fixtures/reconcile"
BASELINE_AT = "2026-07-21T12:00:00Z"
OBSERVED_AT = "2026-07-21T11:00:00Z"


def reconciliation_schema() -> dict[str, Any]:
    return json.loads(
        (REPOSITORY_ROOT / "schemas/ReconciliationPlan.schema.json").read_text(
            encoding="utf-8"
        )
    )


def assert_valid_plan(test_case: Any, plan: dict[str, Any]) -> None:
    schema = reconciliation_schema()
    Draft202012Validator.check_schema(schema)
    findings = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(plan)
    )
    test_case.assertEqual(findings, [], [finding.message for finding in findings])


def baseline_with_intent(
    *,
    action_type: str = "update",
    target_ref: str | None = "PIP-711",
    match_strategy: str = "explicit_reference",
    confidence: str = "high",
    title: str = "Governance planner",
    artifact_status: str = "present",
    generated_at: str = BASELINE_AT,
) -> dict[str, Any]:
    baseline = copy.deepcopy(valid_baseline())
    baseline["generatedAt"] = generated_at
    baseline["systems"]["linear"] = {
        "identifier": "project-pipe",
        "location": "https://linear.app/pipe/project/pipe",
        "status": "confirmed",
    }
    baseline["artifacts"] = [
        {
            "artifactId": "ART-governance-planner",
            "artifactType": "ticket",
            "title": title,
            "status": artifact_status,
            "sourceRef": None,
            "externalRef": target_ref,
            "provenanceStatementIds": ["ST-implemented-feature"],
        }
    ]
    baseline["relationships"] = []
    baseline["governanceGaps"] = []
    baseline["reconciliationPlan"] = [
        {
            "actionId": "REC-governance-planner",
            "targetSystem": "linear",
            "actionType": action_type,
            "targetRef": target_ref,
            "sourceArtifactIds": ["ART-governance-planner"],
            "matchStrategy": match_strategy,
            "confidence": confidence,
            "idempotencyKey": "legacy-key",
            "reason": "Legacy baseline proposal.",
            "expectedEffect": "Legacy baseline proposal.",
            "approvalRequired": True,
            "status": "proposed",
        }
    ]
    return baseline


def linear_record(
    source_id: str,
    source_key: str,
    *,
    title: str = "Governance planner",
    state: str = "In Progress",
    observed_at: str = OBSERVED_AT,
) -> dict[str, Any]:
    return make_record(
        source_system="linear",
        source_id=source_id,
        source_key=source_key,
        entity_type="issue",
        observed_at=observed_at,
        title=title,
        state=state,
        url=f"https://linear.app/pipe/issue/{source_key.lower()}",
    )


def linear_project_record(
    *, title: str = "Governance planner", observed_at: str = OBSERVED_AT
) -> dict[str, Any]:
    return make_record(
        source_system="linear",
        source_id="project-pipe",
        source_key="PIPE",
        entity_type="project",
        observed_at=observed_at,
        title=title,
        state="active",
        url="https://linear.app/pipe/project/pipe",
    )


def snapshot(
    records: list[dict[str, Any]],
    *,
    captured_at: str = OBSERVED_AT,
    snapshot_id: str = "ES-linear-111111111111",
    status: str = "complete",
) -> dict[str, Any]:
    return {
        "schemaVersion": "0.1.0",
        "snapshotId": snapshot_id,
        "sourceSystem": "linear",
        "sourceContainer": {
            "type": "project",
            "id": "project-pipe",
            "url": "https://linear.app/pipe/project/pipe",
        },
        "capturedAt": captured_at,
        "status": status,
        "records": records,
        "pagination": {
            "limit": 200,
            "returnedCount": len(records),
            "pagesRead": 1,
            "truncated": status == "partial",
        },
        "constraints": {
            "readOnly": True,
            "mutationSurfaceExposed": False,
            "credentialsPersisted": False,
            "rawPayloadPersisted": False,
        },
        "diagnostics": [],
    }


def golden_cases() -> list[dict[str, Any]]:
    return json.loads((FIXTURE_ROOT / "golden-cases.json").read_text(encoding="utf-8"))
