from __future__ import annotations

from unittest import TestCase

from pipe_venture_builder.reconcile import plan_reconciliation, render_reconciliation_plan
from tests.reconcile.helpers import baseline_with_intent, linear_record, snapshot


class ReconciliationRenderTests(TestCase):
    def test_render_is_stable_and_contains_only_review_safe_fields(self) -> None:
        baseline = baseline_with_intent()
        observed = snapshot([linear_record("issue-711", "PIP-711")])
        plan = plan_reconciliation(baseline, [observed])

        first = render_reconciliation_plan(plan)
        second = render_reconciliation_plan(plan)

        self.assertEqual(first, second)
        self.assertIn(plan["planId"], first)
        self.assertIn(plan["actions"][0]["actionId"], first)
        self.assertIn("0 investigate", first)
        self.assertIn("No external mutation was performed", first)
        self.assertNotIn("Legacy baseline proposal", first)
