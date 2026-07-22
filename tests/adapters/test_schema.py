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

    def test_schema_rejects_credentials_in_url_userinfo(self) -> None:
        schema = external_snapshot_schema()
        url_schema = schema["$defs"]["safeUrl"]

        findings = list(
            Draft202012Validator(url_schema).iter_errors(
                "https://user:password@github.com/example/product"
            )
        )

        self.assertTrue(findings)
