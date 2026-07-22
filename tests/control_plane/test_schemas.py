from __future__ import annotations

from unittest import TestCase

from jsonschema import Draft202012Validator

from pipe_venture_builder.control_plane.audit import build_run_event
from pipe_venture_builder.control_plane.model import fingerprint
from tests.control_plane.helpers import (
    DECIDED_AT,
    approval_for,
    assert_schema_valid,
    create_plan,
    schema,
)


class ControlPlaneSchemaTests(TestCase):
    def test_approval_schema_and_builder_are_closed_and_valid(self) -> None:
        contract = schema("ApprovalRecord.schema.json")
        record = approval_for(create_plan())

        Draft202012Validator.check_schema(contract)
        self.assertFalse(contract["additionalProperties"])
        self.assertFalse(
            contract["properties"]["constraints"]["properties"][
                "automaticApproval"
            ]["const"]
        )
        assert_schema_valid(self, "ApprovalRecord.schema.json", record)

    def test_run_event_schema_and_builder_are_closed_and_valid(self) -> None:
        contract = schema("RunEvent.schema.json")
        event = build_run_event(
            run_id="RUN-111111111111",
            sequence=1,
            occurred_at=DECIDED_AT,
            event_type="run.created",
            status="pending",
            plan_id="RP-111111111111",
            plan_fingerprint=fingerprint("plan"),
        )

        Draft202012Validator.check_schema(contract)
        self.assertFalse(contract["additionalProperties"])
        constraints = contract["properties"]["constraints"]["properties"]
        self.assertFalse(constraints["rawPayloadPersisted"]["const"])
        self.assertFalse(constraints["credentialsPersisted"]["const"])
        assert_schema_valid(self, "RunEvent.schema.json", event)

    def test_approval_action_enum_excludes_destructive_operations(self) -> None:
        allowed = schema("ApprovalRecord.schema.json")["properties"]["scope"][
            "properties"
        ]["actionType"]["enum"]

        self.assertEqual(allowed, ["create", "update", "link"])
        self.assertNotIn("delete", allowed)
        self.assertNotIn("archive", allowed)
        self.assertNotIn("close", allowed)
