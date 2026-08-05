"""PIP-831: a tipagem declarada no runtime precisa chegar ao planner como intenção.

Este teste atravessa a fronteira Node↔Python de propósito. Ele lê os arquivos de
definição de workflow que o runtime consome e afirma que o planner Python reage a
eles. Sem esta amarração os dois lados derivam em silêncio — foi exatamente o que
aconteceu enquanto ``runtime/lib/engine.mjs`` gravava todo artefato como
``product_context``: conector, adapter e aprovação existiam, e mesmo assim nenhum
ticket jamais seria proposto.
"""

from __future__ import annotations

import copy
import json
from typing import Any
from unittest import TestCase

from pipe_venture_builder.reconcile import plan_reconciliation
from pipe_venture_builder.reconcile.planner import EXTERNAL_ARTIFACT_TARGETS
from tests.helpers import REPOSITORY_ROOT, valid_baseline
from tests.reconcile.helpers import snapshot


WORKFLOW_ROOT = REPOSITORY_ROOT / "runtime/workflows"
BASELINE_SCHEMA = REPOSITORY_ROOT / "schemas/ProductBaseline.schema.json"


def declared_artifact_types(workflow_id: str) -> dict[str, str]:
    definition = json.loads(
        (WORKFLOW_ROOT / f"{workflow_id}.definition.json").read_text(encoding="utf-8")
    )
    return definition.get("baseline_advance", {}).get("artifact_types", {})


def baseline_from_workflow(workflow_id: str) -> dict[str, Any]:
    """Baseline com um artefato por output declarado, como o runtime emitiria."""
    baseline = copy.deepcopy(valid_baseline())
    baseline["systems"]["linear"] = {
        "identifier": "project-pipe",
        "location": "https://linear.app/pipe/project/pipe",
        "status": "confirmed",
    }
    baseline["artifacts"] = [
        {
            "artifactId": f"ART-{output}-v1",
            "artifactType": artifact_type,
            "title": f"{output} v1 (venture-os phase loop)",
            "status": "present",
            "sourceRef": f"artifacts/{output}-v1.md",
            "externalRef": None,
            "provenanceStatementIds": [],
        }
        for output, artifact_type in declared_artifact_types(workflow_id).items()
    ]
    baseline["relationships"] = []
    baseline["governanceGaps"] = []
    baseline["reconciliationPlan"] = []
    return baseline


def linear_create_actions(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        action
        for action in plan["actions"]
        if action["targetSystem"] == "linear" and action["actionType"] == "create"
    ]


class BaselineToPlanTests(TestCase):
    def test_declared_types_exist_in_the_canonical_enum(self) -> None:
        schema = json.loads(BASELINE_SCHEMA.read_text(encoding="utf-8"))
        allowed = set(schema["$defs"]["artifact"]["properties"]["artifactType"]["enum"])
        for workflow_id in ("product-strategy", "mvp-refinement", "ux-architecture"):
            declared = declared_artifact_types(workflow_id)
            self.assertTrue(declared, f"{workflow_id} sem artifact_types declarado")
            for output, artifact_type in declared.items():
                with self.subTest(workflow=workflow_id, output=output):
                    self.assertIn(artifact_type, allowed)

    def test_mvp_refinement_artifacts_become_linear_create_intents(self) -> None:
        plan = plan_reconciliation(baseline_from_workflow("mvp-refinement"), [snapshot([])])

        actions = linear_create_actions(plan)
        self.assertTrue(
            actions,
            "mvp-refinement não produziu nenhuma ação create no Linear — "
            "a esteira artefato→ticket está quebrada",
        )
        for action in actions:
            self.assertTrue(action["idempotencyKey"])

    def test_ux_architecture_artifacts_become_linear_create_intents(self) -> None:
        plan = plan_reconciliation(baseline_from_workflow("ux-architecture"), [snapshot([])])

        self.assertTrue(linear_create_actions(plan))

    def test_product_strategy_does_not_create_tickets_before_mvp_scope(self) -> None:
        """core-pipeline-map.md: nada de ticket de build antes do MVP scope aceito."""
        plan = plan_reconciliation(baseline_from_workflow("product-strategy"), [snapshot([])])

        self.assertEqual(linear_create_actions(plan), [])

    def test_the_planner_still_ignores_product_context(self) -> None:
        """Guarda de regressão: se product_context virasse ticketizável, todo
        artefato de contexto de toda venture viraria ticket de uma vez."""
        self.assertNotIn("product_context", EXTERNAL_ARTIFACT_TARGETS)
