from __future__ import annotations

import copy
from unittest import TestCase

from pipe_venture_builder.reconcile import PlanningContractError, plan_reconciliation
from tests.reconcile.helpers import (
    assert_valid_plan,
    baseline_with_intent,
    golden_cases,
    linear_project_record,
    linear_record,
    snapshot,
)


class ReconciliationPlannerTests(TestCase):
    def test_golden_matching_and_blocker_cases(self) -> None:
        for case in golden_cases():
            with self.subTest(case=case["name"]):
                baseline = baseline_with_intent(**case.get("baseline", {}))
                records = [linear_record(**item) for item in case.get("records", [])]
                observed = snapshot(records, **case.get("snapshot", {}))
                plan = plan_reconciliation(baseline, [observed])

                assert_valid_plan(self, plan)
                action = plan["actions"][0]
                self.assertEqual(action["actionType"], case["expected"]["actionType"])
                self.assertEqual(action["status"], case["expected"]["status"])
                self.assertEqual(
                    action["matchStrategy"], case["expected"]["matchStrategy"]
                )
                self.assertEqual(action["confidence"], case["expected"]["confidence"])
                if "reason" in case["expected"]:
                    self.assertEqual(action["reason"], case["expected"]["reason"])
                self.assertEqual(
                    sorted(blocker["type"] for blocker in plan["blockers"]),
                    sorted(case["expected"]["blockers"]),
                )

    def test_identical_inputs_produce_identical_plan_and_keys(self) -> None:
        baseline = baseline_with_intent(action_type="create")
        observed = snapshot([linear_record("issue-711", "PIP-711")])

        first = plan_reconciliation(copy.deepcopy(baseline), [copy.deepcopy(observed)])
        second = plan_reconciliation(copy.deepcopy(baseline), [copy.deepcopy(observed)])

        self.assertEqual(first, second)
        self.assertEqual(first["planId"], second["planId"])
        self.assertEqual(
            first["actions"][0]["idempotencyKey"],
            second["actions"][0]["idempotencyKey"],
        )

    def test_satisfied_create_becomes_ignore_instead_of_duplicate(self) -> None:
        baseline = baseline_with_intent(action_type="create")
        observed = snapshot([linear_record("issue-711", "PIP-711")])

        plan = plan_reconciliation(baseline, [observed])

        action = plan["actions"][0]
        self.assertEqual(action["actionType"], "ignore")
        self.assertEqual(action["status"], "already_satisfied")
        self.assertFalse(action["approvalRequired"])
        self.assertEqual(plan["summary"]["alreadySatisfied"], 1)

    def test_distinct_seed_intents_have_distinct_idempotency_keys(self) -> None:
        baseline = baseline_with_intent(action_type="create", target_ref=None)
        second = copy.deepcopy(baseline["reconciliationPlan"][0])
        second["actionId"] = "REC-governance-planner-link"
        second["actionType"] = "link"
        second["targetRef"] = "PIP-711"
        baseline["reconciliationPlan"].append(second)

        plan = plan_reconciliation(
            baseline, [snapshot([linear_record("issue-711", "PIP-711")])]
        )

        keys = [action["idempotencyKey"] for action in plan["actions"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_unique_title_match_is_never_auto_confirmed(self) -> None:
        baseline = baseline_with_intent(
            action_type="create", target_ref=None, match_strategy="manual"
        )
        observed = snapshot([linear_record("issue-900", "PIP-900")])

        plan = plan_reconciliation(baseline, [observed])

        action = plan["actions"][0]
        self.assertEqual(action["actionType"], "investigate")
        self.assertEqual(action["matchStrategy"], "semantic_candidate")
        self.assertEqual(action["confidence"], "low")
        self.assertEqual(action["status"], "proposed")
        self.assertFalse(action["approvalRequired"])

    def test_semantic_match_ignores_container_record(self) -> None:
        baseline = baseline_with_intent(
            action_type="create", target_ref=None, match_strategy="manual"
        )

        plan = plan_reconciliation(baseline, [snapshot([linear_project_record()])])

        self.assertEqual(plan["actions"][0]["actionType"], "create")
        self.assertEqual(plan["actions"][0]["matchStrategy"], "manual")

    def test_non_latin_titles_remain_distinct_semantic_candidates(self) -> None:
        baseline = baseline_with_intent(
            action_type="create",
            target_ref=None,
            match_strategy="manual",
            title="治理规划器",
        )
        observed = snapshot(
            [
                linear_record("issue-900", "PIP-900", title="治理规划器"),
                linear_record("issue-901", "PIP-901", title="别的功能"),
            ]
        )

        plan = plan_reconciliation(baseline, [observed])

        self.assertEqual(plan["actions"][0]["actionType"], "investigate")
        self.assertEqual(len(plan["actions"][0]["targetRecordIds"]), 1)

    def test_low_confidence_seed_is_always_investigate(self) -> None:
        baseline = baseline_with_intent(
            action_type="create",
            target_ref=None,
            match_strategy="manual",
            confidence="low",
            title="No matching title",
        )

        plan = plan_reconciliation(baseline, [snapshot([])])

        self.assertEqual(plan["actions"][0]["actionType"], "investigate")
        self.assertEqual(plan["actions"][0]["confidence"], "low")

    def test_changed_target_after_snapshot_is_review_blocker(self) -> None:
        baseline = baseline_with_intent()
        observed = snapshot([linear_record("issue-711", "PIP-711")])
        verification = snapshot(
            [
                linear_record(
                    "issue-711",
                    "PIP-711",
                    state="Done",
                    observed_at="2026-07-21T13:00:00Z",
                )
            ],
            captured_at="2026-07-21T13:00:00Z",
            snapshot_id="ES-linear-222222222222",
        )

        plan = plan_reconciliation(
            baseline, [observed], verification_snapshots=[verification]
        )

        self.assertEqual(plan["status"], "blocked")
        self.assertEqual(plan["actions"][0]["actionType"], "investigate")
        self.assertIn("changed_target", {item["type"] for item in plan["blockers"]})
        assert_valid_plan(self, plan)

    def test_incomplete_snapshot_blocks_mutating_proposal(self) -> None:
        plan = plan_reconciliation(
            baseline_with_intent(action_type="create", target_ref=None),
            [snapshot([], status="partial")],
        )

        self.assertEqual(plan["actions"][0]["status"], "blocked")
        self.assertIn("unavailable_source", {item["type"] for item in plan["blockers"]})

    def test_rejects_snapshot_that_exposes_mutation_surface(self) -> None:
        unsafe = snapshot([])
        unsafe["constraints"]["mutationSurfaceExposed"] = True

        with self.assertRaises(PlanningContractError):
            plan_reconciliation(baseline_with_intent(), [unsafe])

    def test_declared_container_mismatch_blocks_instead_of_retargeting(self) -> None:
        other = snapshot([linear_record("issue-711", "PIP-711")])
        other["sourceContainer"]["id"] = "another-project"

        plan = plan_reconciliation(baseline_with_intent(), [other])

        self.assertEqual(plan["actions"][0]["targetContainerId"], "project-pipe")
        self.assertEqual(plan["actions"][0]["status"], "blocked")
        self.assertIn("unavailable_source", {item["type"] for item in plan["blockers"]})

    def test_malformed_seed_enum_fails_closed(self) -> None:
        baseline = baseline_with_intent()
        baseline["reconciliationPlan"][0]["actionType"] = "delete"

        with self.assertRaises(PlanningContractError):
            plan_reconciliation(baseline, [snapshot([])])

    def test_malformed_source_artifact_ids_fail_with_contract_error(self) -> None:
        baseline = baseline_with_intent()
        baseline["reconciliationPlan"][0]["sourceArtifactIds"] = [42]

        with self.assertRaises(PlanningContractError):
            plan_reconciliation(baseline, [snapshot([])])

    def test_repository_intent_is_planned_without_external_snapshot(self) -> None:
        baseline = baseline_with_intent()
        seed = baseline["reconciliationPlan"][0]
        seed["targetSystem"] = "repository"
        seed["actionType"] = "update"
        seed["targetRef"] = "docs/reconciliation/README.md"
        seed["matchStrategy"] = "manual"

        plan = plan_reconciliation(baseline, [])

        self.assertEqual(plan["actions"][0]["targetSystem"], "repository")
        self.assertEqual(plan["actions"][0]["status"], "proposed")
        self.assertEqual(
            plan["actions"][0]["targetContainerId"],
            baseline["systems"]["repository"]["identifier"],
        )

    def test_missing_repository_system_fails_closed(self) -> None:
        baseline = baseline_with_intent()
        baseline["systems"]["repository"] = None

        with self.assertRaises(PlanningContractError):
            plan_reconciliation(baseline, [snapshot([])])

    def test_does_not_call_write_like_methods_on_mapping_inputs(self) -> None:
        class PoisonSnapshot(dict):
            def write(self, *_args: object, **_kwargs: object) -> None:
                raise AssertionError("planner attempted an external write")

            def apply(self, *_args: object, **_kwargs: object) -> None:
                raise AssertionError("planner attempted an external apply")

        observed = PoisonSnapshot(snapshot([linear_record("issue-711", "PIP-711")]))

        plan = plan_reconciliation(baseline_with_intent(), [observed])

        self.assertFalse(plan["constraints"]["externalMutationPerformed"])
        self.assertFalse(plan["constraints"]["mutationSurfaceExposed"])
