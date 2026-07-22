from __future__ import annotations

from unittest import TestCase

from jsonschema import Draft202012Validator

from tests.adapters.helpers import external_snapshot_schema


class ExternalSnapshotSchemaTests(TestCase):
    def test_schema_is_valid_draft_2020_12_and_closed_by_default(self) -> None:
        schema = external_snapshot_schema()

        Draft202012Validator.check_schema(schema)
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["$defs"]["record"]["additionalProperties"])
        self.assertEqual(
            schema["properties"]["constraints"]["properties"]["readOnly"]["const"], True
        )
        self.assertEqual(
            schema["properties"]["constraints"]["properties"]["mutationSurfaceExposed"][
                "const"
            ],
            False,
        )
