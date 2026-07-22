from __future__ import annotations

import copy
from unittest import TestCase

from pipe_venture_builder.control_plane.approval import (
    validate_approval_for_action,
    validate_approval_record,
)
from pipe_venture_builder.control_plane.model import ControlPlaneContractError
from tests.control_plane.helpers import (
    EXECUTED_AT,
    approval_for,
    create_plan,
)


class ApprovalRecordTests(TestCase):
    def test_approval_is_bound_to_exact_action_scope(self) -> None:
        plan = create_plan()
        action = plan["actions"][0]
        approval = approval_for(plan)

        self.assertIsNone(
            validate_approval_for_action(approval, plan, action, at=EXECUTED_AT)
        )

        changed = copy.deepcopy(action)
        changed["targetContainerId"] = "another-project"
        self.assertEqual(
            validate_approval_for_action(approval, plan, changed, at=EXECUTED_AT),
            "approval_mismatch",
        )

    def test_expired_denied_and_future_approval_are_rejected(self) -> None:
        plan = create_plan()
        action = plan["actions"][0]
        expired = approval_for(plan, expires_at="2026-07-21T13:30:00Z")
        denied = approval_for(plan, decision="denied")

        self.assertEqual(
            validate_approval_for_action(expired, plan, action, at=EXECUTED_AT),
            "approval_expired",
        )
        self.assertEqual(
            validate_approval_for_action(denied, plan, action, at=EXECUTED_AT),
            "approval_not_granted",
        )
        self.assertEqual(
            validate_approval_for_action(
                approval_for(plan), plan, action, at="2026-07-21T12:30:00Z"
            ),
            "approval_expired",
        )

    def test_tampered_record_fails_closed(self) -> None:
        approval = approval_for(create_plan())
        approval["actor"]["actorId"] = "different-human"

        with self.assertRaises(ControlPlaneContractError):
            validate_approval_record(approval)

    def test_actor_must_be_human_and_absolute_gates_remain_false(self) -> None:
        approval = approval_for(create_plan())
        approval["actor"]["actorType"] = "agent"

        with self.assertRaises(ControlPlaneContractError):
            validate_approval_record(approval)

    def test_runtime_rejects_ids_that_the_schema_would_reject(self) -> None:
        approval = approval_for(create_plan())
        approval["approvalId"] = "approval-readable-but-not-canonical"

        with self.assertRaises(ControlPlaneContractError):
            validate_approval_record(approval)
