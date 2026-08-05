"""PIP-834: o reconciliador das três derivas.

Ele existe para o sistema parar de confiar na disciplina de quem executou. O que
guarda aqui é o comportamento que torna o relatório confiável:

- deriva que o snapshot **não consegue** enxergar é reportada como `unavailable`
  com motivo, nunca omitida. Omitir vira "tudo certo" quando na verdade é "não olhei".
- o reconciliador **propõe** e nunca corrige: não existe caminho de mutação aqui.
"""

from __future__ import annotations

import copy
from unittest import TestCase

from pipe_venture_builder.linear.lifecycle import (
    DELIVERY_EVIDENCE_HOSTS,
    find_lifecycle_drift,
)
from pipe_venture_builder.linear.reconciler import reconcile
from tests.helpers import valid_baseline
from tests.reconcile.helpers import snapshot


def issue_record(
    key: str,
    *,
    state: str = "Done",
    delivery_links: list[str] | None = None,
    labels: list[str] | None = None,
) -> dict:
    return {
        "recordId": f"REC-{key}",
        "sourceSystem": "linear",
        "sourceId": f"id-{key}",
        "sourceKey": key,
        "entityType": "issue",
        "observedAt": "2026-08-05T11:00:00Z",
        "title": f"ticket {key}",
        "state": state,
        "url": f"https://linear.app/x/issue/{key}",
        "sourceCreatedAt": "2026-08-01T11:00:00Z",
        "sourceUpdatedAt": "2026-08-05T11:00:00Z",
        "sourceClosedAt": "2026-08-05T11:00:00Z" if state == "Done" else None,
        "relationships": [],
        "attributes": {
            "number": 1,
            "priority": 2,
            "labels": labels or [],
            "deliveryLinks": delivery_links if delivery_links is not None else [],
        },
    }


def baseline_with_artifacts(artifact_types: list[str]) -> dict:
    baseline = copy.deepcopy(valid_baseline())
    baseline["systems"]["linear"] = {
        "identifier": "project-pipe",
        "location": "https://linear.app/pipe/project/pipe",
        "status": "confirmed",
    }
    baseline["artifacts"] = [
        {
            "artifactId": f"ART-{artifact_type}-{index}",
            "artifactType": artifact_type,
            "title": f"{artifact_type} {index}",
            "status": "present",
            "sourceRef": f"artifacts/{artifact_type}-{index}.md",
            "externalRef": None,
            "provenanceStatementIds": [],
        }
        for index, artifact_type in enumerate(artifact_types)
    ]
    baseline["relationships"] = []
    baseline["governanceGaps"] = []
    baseline["reconciliationPlan"] = []
    return baseline


class LifecycleDriftTests(TestCase):
    def test_completed_ticket_without_delivery_evidence_is_drift(self) -> None:
        findings = find_lifecycle_drift([issue_record("PIP-1", delivery_links=[])])
        self.assertEqual([f.source_key for f in findings], ["PIP-1"])
        self.assertEqual(findings[0].rule, "completed_without_delivery_evidence")

    def test_completed_ticket_with_a_pull_request_link_is_clean(self) -> None:
        findings = find_lifecycle_drift(
            [issue_record("PIP-1", delivery_links=["https://github.com/o/r/pull/164"])]
        )
        self.assertEqual(findings, [])

    def test_a_link_that_is_not_delivery_evidence_does_not_count(self) -> None:
        """Anexar um Google Doc não prova que a entrega existiu."""
        findings = find_lifecycle_drift(
            [issue_record("PIP-1", delivery_links=["https://docs.google.com/x"])]
        )
        self.assertEqual([f.rule for f in findings], ["completed_without_delivery_evidence"])

    def test_open_tickets_are_not_evaluated_for_delivery_evidence(self) -> None:
        for state in ("Backlog", "Todo", "In Progress", "In Review"):
            with self.subTest(state=state):
                self.assertEqual(find_lifecycle_drift([issue_record("PIP-1", state=state)]), [])

    def test_canceled_tickets_are_not_drift(self) -> None:
        self.assertEqual(find_lifecycle_drift([issue_record("PIP-1", state="Canceled")]), [])

    def test_approval_granted_label_without_evidence_is_reported_separately(self) -> None:
        findings = find_lifecycle_drift(
            [
                issue_record(
                    "PIP-2",
                    state="In Progress",
                    labels=["approval:granted"],
                )
            ]
        )
        self.assertEqual([f.rule for f in findings], ["approval_claimed_without_source"])

    def test_the_project_record_is_never_evaluated_as_a_ticket(self) -> None:
        project = issue_record("proj")
        project["entityType"] = "project"
        self.assertEqual(find_lifecycle_drift([project]), [])

    def test_github_and_linear_hosts_are_the_recognised_evidence(self) -> None:
        self.assertIn("github.com", DELIVERY_EVIDENCE_HOSTS)


class ReconcileTests(TestCase):
    def test_artifact_without_a_ticket_becomes_a_coverage_proposal(self) -> None:
        report = reconcile(baseline_with_artifacts(["feature"]), snapshot([]))
        self.assertTrue(report.coverage)
        self.assertTrue(all(action["actionType"] == "create" for action in report.coverage))

    def test_product_context_never_produces_a_coverage_proposal(self) -> None:
        report = reconcile(baseline_with_artifacts(["product_context"]), snapshot([]))
        self.assertEqual(report.coverage, [])

    def test_contract_drift_is_unavailable_with_a_reason_not_silently_empty(self) -> None:
        """O snapshot descarta descrição por decisão registrada. Reportar `unavailable`
        com motivo é a diferença entre 'não encontrei problema' e 'não olhei'."""
        report = reconcile(baseline_with_artifacts(["feature"]), snapshot([]))
        self.assertEqual(report.contract["status"], "unavailable")
        self.assertIn("descri", report.contract["reason"].lower())

    def test_lifecycle_drift_reaches_the_report(self) -> None:
        report = reconcile(
            baseline_with_artifacts([]), snapshot([issue_record("PIP-9", delivery_links=[])])
        )
        self.assertEqual([f["sourceKey"] for f in report.lifecycle], ["PIP-9"])

    def test_the_report_serializes_without_any_source_text(self) -> None:
        report = reconcile(
            baseline_with_artifacts(["feature"]), snapshot([issue_record("PIP-9")])
        )
        payload = report.as_dict()
        self.assertEqual(payload["schemaVersion"], "0.1.0")
        self.assertIn("summary", payload)
        self.assertNotIn("description", str(payload).lower())

    def test_running_twice_over_unchanged_inputs_gives_the_same_report(self) -> None:
        baseline = baseline_with_artifacts(["feature"])
        observed = snapshot([issue_record("PIP-9")])
        first = reconcile(copy.deepcopy(baseline), copy.deepcopy(observed)).as_dict()
        second = reconcile(copy.deepcopy(baseline), copy.deepcopy(observed)).as_dict()
        self.assertEqual(first, second)

    def test_there_is_no_mutation_surface_on_the_report(self) -> None:
        report = reconcile(baseline_with_artifacts(["feature"]), snapshot([]))
        self.assertFalse(
            {"apply", "create", "update", "write", "execute"}.intersection(dir(report))
        )


class ReconcileWithoutBaselineTests(TestCase):
    """PIP-835: o job agendado roda sobre um repositório que pode não ter baseline.

    Sem baseline, a deriva de cobertura não é calculável. Ela é reportada como
    `unavailable` com motivo — mesma regra da deriva de contrato. Devolver zero
    seria afirmar "todo artefato virou ticket" sem ter olhado para artefato nenhum.
    """

    def test_coverage_is_unavailable_when_there_is_no_baseline(self) -> None:
        report = reconcile(None, snapshot([issue_record("PIP-1")]))
        self.assertEqual(report.coverage_status["status"], "unavailable")
        self.assertIn("baseline", report.coverage_status["reason"].lower())
        self.assertEqual(report.coverage, [])

    def test_lifecycle_still_runs_without_a_baseline(self) -> None:
        report = reconcile(None, snapshot([issue_record("PIP-1", delivery_links=[])]))
        self.assertEqual([f["sourceKey"] for f in report.lifecycle], ["PIP-1"])

    def test_clean_is_false_when_coverage_could_not_be_computed(self) -> None:
        """`clean` não pode dizer 'em dia' quando metade da verificação não rodou."""
        report = reconcile(None, snapshot([]))
        self.assertFalse(report.summary["clean"])

    def test_coverage_is_available_when_a_baseline_is_given(self) -> None:
        report = reconcile(baseline_with_artifacts(["feature"]), snapshot([]))
        self.assertEqual(report.coverage_status["status"], "available")
