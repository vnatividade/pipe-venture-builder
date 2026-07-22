from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from tests.helpers import REPOSITORY_ROOT

FIXTURE_ROOT = REPOSITORY_ROOT / "tests/fixtures/connectors"
CAPTURED_AT = "2026-07-21T12:00:00Z"


def external_snapshot_schema() -> dict[str, Any]:
    return json.loads(
        (REPOSITORY_ROOT / "schemas/ExternalSnapshot.schema.json").read_text(
            encoding="utf-8"
        )
    )


def assert_valid_snapshot(test_case: Any, snapshot: dict[str, Any]) -> None:
    schema = external_snapshot_schema()
    Draft202012Validator.check_schema(schema)
    findings = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            snapshot
        )
    )
    test_case.assertEqual(findings, [], [finding.message for finding in findings])
