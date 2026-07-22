from __future__ import annotations

from unittest import TestCase

from jsonschema import Draft202012Validator

from tests.reconcile.helpers import reconciliation_schema


class ReconciliationPlanSchemaTests(TestCase):
    def test_schema_is_valid_and_closes_mutation_boundaries(self) -> None:
        schema = reconciliation_schema()

        Draft202012Validator.check_schema(schema)
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["$defs"]["action"]["additionalProperties"])
        constraints = schema["properties"]["constraints"]["properties"]
        self.assertTrue(constraints["planOnly"]["const"])
        self.assertFalse(constraints["externalMutationPerformed"]["const"])
        self.assertFalse(constraints["mutationSurfaceExposed"]["const"])
        self.assertFalse(constraints["semanticMatchesAutoConfirmed"]["const"])
        self.assertFalse(constraints["destructiveActionsAllowed"]["const"])

    def test_schema_does_not_allow_destructive_action_types(self) -> None:
        allowed = reconciliation_schema()["$defs"]["action"]["properties"][
            "actionType"
        ]["enum"]

        self.assertEqual(allowed, ["create", "update", "link", "ignore", "investigate"])
        self.assertNotIn("delete", allowed)
        self.assertNotIn("archive", allowed)
        self.assertNotIn("close", allowed)
