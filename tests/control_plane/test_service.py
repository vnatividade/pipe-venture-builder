from __future__ import annotations

from unittest import TestCase

from pipe_venture_builder.apply import (
    ApplyAdapterFailure,
    ApplyResult,
    FixtureApplyAdapter,
    SupervisedApplyService,
    TargetObservation,
    VerificationResult,
)
from pipe_venture_builder.control_plane import LocalControlPlaneStore
from pipe_venture_builder.control_plane.model import fingerprint
from tests.control_plane.helpers import (
    EXECUTED_AT,
    approval_for,
    assert_schema_valid,
    create_plan,
    fixture_for,
    update_plan,
)


class SupervisedApplyServiceTests(TestCase):
    def setUp(self) -> None:
        self.store = LocalControlPlaneStore(":memory:")
        self.service = SupervisedApplyService(self.store)

    def tearDown(self) -> None:
        self.store.close()

    def test_missing_approval_blocks_before_adapter_access(self) -> None:
        plan = create_plan()
        adapter = FixtureApplyAdapter(fixture_for(plan))

        outcome = self.service.execute_action(
            plan,
            plan["actions"][0]["actionId"],
            approval=None,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )

        self.assertEqual(outcome["status"], "blocked")
        self.assertEqual(outcome["reasonCode"], "approval_missing")
        self.assertEqual(adapter.inspect_calls, 0)
        self.assertEqual(adapter.mutation_count, 0)

    def test_expired_approval_and_changed_source_block_before_inspect(self) -> None:
        plan = create_plan()
        expired_adapter = FixtureApplyAdapter(fixture_for(plan))
        expired = self.service.execute_action(
            plan,
            plan["actions"][0]["actionId"],
            approval=approval_for(plan, expires_at="2026-07-21T13:30:00Z"),
            adapter=expired_adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )
        self.assertEqual(expired["reasonCode"], "approval_expired")
        self.assertEqual(expired_adapter.inspect_calls, 0)

        changed_adapter = FixtureApplyAdapter(fixture_for(plan))
        changed = self.service.execute_action(
            plan,
            plan["actions"][0]["actionId"],
            approval=approval_for(plan),
            adapter=changed_adapter,
            current_source_fingerprint=fingerprint("changed-source"),
            at=EXECUTED_AT,
        )
        self.assertEqual(changed["reasonCode"], "source_changed")
        self.assertEqual(changed_adapter.inspect_calls, 0)

    def test_changed_target_blocks_without_apply(self) -> None:
        plan = update_plan()
        fixture = fixture_for(plan)
        fixture["actions"][0]["beforeFingerprint"] = fingerprint("changed-target")
        adapter = FixtureApplyAdapter(fixture)

        outcome = self.service.execute_action(
            plan,
            plan["actions"][0]["actionId"],
            approval=approval_for(plan),
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )

        self.assertEqual(outcome["reasonCode"], "target_changed")
        self.assertEqual(adapter.apply_calls, 0)
        self.assertEqual(adapter.mutation_count, 0)

    def test_success_is_verified_audited_and_idempotent_on_rerun(self) -> None:
        plan = create_plan()
        approval = approval_for(plan)
        adapter = FixtureApplyAdapter(fixture_for(plan))
        action_id = plan["actions"][0]["actionId"]

        first = self.service.execute_action(
            plan,
            action_id,
            approval=approval,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )
        second = self.service.execute_action(
            plan,
            action_id,
            approval=approval,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at="2026-07-21T14:10:00Z",
        )

        self.assertEqual(first["status"], "verified")
        self.assertEqual(second["status"], "skipped")
        self.assertEqual(second["reasonCode"], "already_verified")
        self.assertEqual(adapter.mutation_count, 1)
        self.assertEqual(adapter.apply_calls, 1)
        self.assertTrue(first["auditChainValid"])
        events = self.store.list_events(first["runId"])
        self.assertEqual(events[-1]["eventType"], "action.skipped")
        for event in events:
            assert_schema_valid(self, "RunEvent.schema.json", event)

    def test_new_plan_with_same_idempotency_key_does_not_duplicate_apply(self) -> None:
        first_plan = create_plan()
        second_plan = create_plan(
            generated_at="2026-07-22T12:00:00Z",
            observed_at="2026-07-22T11:00:00Z",
        )
        self.assertNotEqual(first_plan["planId"], second_plan["planId"])
        self.assertEqual(
            first_plan["actions"][0]["idempotencyKey"],
            second_plan["actions"][0]["idempotencyKey"],
        )
        adapter = FixtureApplyAdapter(fixture_for(first_plan))

        first = self.service.execute_action(
            first_plan,
            first_plan["actions"][0]["actionId"],
            approval=approval_for(first_plan),
            adapter=adapter,
            current_source_fingerprint=first_plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )
        second = self.service.execute_action(
            second_plan,
            second_plan["actions"][0]["actionId"],
            approval=None,
            adapter=adapter,
            current_source_fingerprint=second_plan["baseline"]["fingerprint"],
            at="2026-07-22T14:00:00Z",
        )

        self.assertEqual(first["status"], "verified")
        self.assertEqual(second["status"], "skipped")
        self.assertEqual(second["reasonCode"], "already_verified")
        self.assertEqual(adapter.mutation_count, 1)
        self.assertEqual(adapter.apply_calls, 1)

    def test_pause_after_apply_resumes_at_verification_without_reapply(self) -> None:
        plan = create_plan()
        approval = approval_for(plan)
        adapter = FixtureApplyAdapter(fixture_for(plan))
        action_id = plan["actions"][0]["actionId"]

        paused = self.service.execute_action(
            plan,
            action_id,
            approval=approval,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
            pause_after_apply=True,
        )
        resumed = self.service.execute_action(
            plan,
            action_id,
            approval=None,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at="2026-07-21T14:05:00Z",
        )

        self.assertEqual(paused["status"], "interrupted")
        self.assertEqual(resumed["status"], "verified")
        self.assertEqual(adapter.mutation_count, 1)
        self.assertEqual(adapter.apply_calls, 1)
        self.assertEqual(adapter.verify_calls, 1)

    def test_uncertain_interruption_retries_same_key_without_duplicate(self) -> None:
        plan = create_plan()
        approval = approval_for(plan)
        adapter = FixtureApplyAdapter(
            fixture_for(plan, apply_behavior="interrupt_once")
        )
        action_id = plan["actions"][0]["actionId"]

        interrupted = self.service.execute_action(
            plan,
            action_id,
            approval=approval,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )
        resumed = self.service.execute_action(
            plan,
            action_id,
            approval=approval,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at="2026-07-21T14:05:00Z",
        )

        self.assertEqual(interrupted["status"], "interrupted")
        self.assertEqual(resumed["status"], "verified")
        self.assertEqual(adapter.apply_calls, 2)
        self.assertEqual(adapter.mutation_count, 1)
        self.assertTrue(resumed["auditChainValid"])

    def test_verify_failure_resumes_verification_without_reapply(self) -> None:
        plan = create_plan()
        approval = approval_for(plan)
        adapter = FixtureApplyAdapter(
            fixture_for(plan, verify_behavior="fail_once")
        )
        action_id = plan["actions"][0]["actionId"]

        failed = self.service.execute_action(
            plan,
            action_id,
            approval=approval,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )
        recovered = self.service.execute_action(
            plan,
            action_id,
            approval=None,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at="2026-07-21T14:05:00Z",
        )

        self.assertEqual(failed["reasonCode"], "verification_failed")
        self.assertEqual(recovered["status"], "verified")
        self.assertEqual(adapter.apply_calls, 1)
        self.assertEqual(adapter.mutation_count, 1)
        self.assertEqual(adapter.verify_calls, 2)

    def test_verified_boolean_cannot_override_wrong_target_fingerprint(self) -> None:
        class LyingFixtureAdapter(FixtureApplyAdapter):
            def verify(
                self, action: object, result: ApplyResult
            ) -> VerificationResult:
                return VerificationResult(True, fingerprint("wrong-target"))

        plan = create_plan()
        adapter = LyingFixtureAdapter(fixture_for(plan))

        outcome = self.service.execute_action(
            plan,
            plan["actions"][0]["actionId"],
            approval=approval_for(plan),
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )

        self.assertEqual(outcome["status"], "failed")
        self.assertEqual(outcome["reasonCode"], "verification_failed")

    def test_invalid_audit_chain_blocks_before_adapter_access(self) -> None:
        plan = create_plan()
        adapter = FixtureApplyAdapter(fixture_for(plan))
        run_id = self.store.register_plan(plan, at=EXECUTED_AT)
        self.store._connection.execute(
            "UPDATE events SET event_json = '{}' WHERE run_id = ? AND sequence = 1",
            (run_id,),
        )
        self.store._connection.commit()

        outcome = self.service.execute_action(
            plan,
            plan["actions"][0]["actionId"],
            approval=approval_for(plan),
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at="2026-07-21T14:05:00Z",
        )

        self.assertEqual(outcome["status"], "blocked")
        self.assertEqual(outcome["reasonCode"], "audit_chain_invalid")
        self.assertEqual(adapter.inspect_calls, 0)
        self.assertEqual(adapter.apply_calls, 0)

    def test_conflict_and_failure_are_classified_without_mutation(self) -> None:
        for behavior, status, reason in (
            ("conflict", "blocked", "adapter_conflict"),
            ("fail", "failed", "adapter_failed"),
        ):
            with self.subTest(behavior=behavior):
                plan = create_plan()
                adapter = FixtureApplyAdapter(
                    fixture_for(plan, apply_behavior=behavior)
                )
                outcome = self.service.execute_action(
                    plan,
                    plan["actions"][0]["actionId"],
                    approval=approval_for(plan),
                    adapter=adapter,
                    current_source_fingerprint=plan["baseline"]["fingerprint"],
                    at=EXECUTED_AT,
                )
                self.assertEqual(outcome["status"], status)
                self.assertEqual(outcome["reasonCode"], reason)
                self.assertEqual(adapter.mutation_count, 0)

    def test_adapter_error_details_never_enter_audit(self) -> None:
        sentinel = "sk-this-must-never-appear-1234567890"

        class LeakyAdapter:
            adapter_name = "fixture"

            def inspect(self, _action: object) -> TargetObservation:
                return TargetObservation(False, None)

            def apply(self, _action: object, *, idempotency_key: str) -> ApplyResult:
                raise ApplyAdapterFailure(sentinel)

            def verify(
                self, _action: object, _result: ApplyResult
            ) -> VerificationResult:
                return VerificationResult(False, None)

        plan = create_plan()
        outcome = self.service.execute_action(
            plan,
            plan["actions"][0]["actionId"],
            approval=approval_for(plan),
            adapter=LeakyAdapter(),
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )

        rendered = str(self.store.list_events(outcome["runId"]))
        self.assertNotIn(sentinel, rendered)
        self.assertEqual(outcome["reasonCode"], "adapter_failed")

    def test_non_mutating_or_blocked_action_never_reaches_adapter(self) -> None:
        plan = create_plan()
        action = plan["actions"][0]
        action["actionType"] = "investigate"
        action["approvalRequired"] = False
        adapter = FixtureApplyAdapter(fixture_for(create_plan()))

        outcome = self.service.execute_action(
            plan,
            action["actionId"],
            approval=None,
            adapter=adapter,
            current_source_fingerprint=plan["baseline"]["fingerprint"],
            at=EXECUTED_AT,
        )

        self.assertEqual(outcome["reasonCode"], "action_not_applicable")
        self.assertEqual(adapter.inspect_calls, 0)
        self.assertEqual(adapter.apply_calls, 0)
