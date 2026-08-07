"""Reconciliador das três derivas (PIP-834).

Expõe pela primeira vez o `plan_reconciliation` de `reconcile/planner.py`, que era
código vivo, testado e inalcançável por CLI.

Ele **propõe** e nunca corrige: não existe caminho de mutação neste módulo nem no
relatório que ele devolve.

Uma decisão de honestidade governa o desenho: deriva que o snapshot não consegue
enxergar é reportada como `unavailable` **com motivo**, nunca omitida. Um relatório
que omite o que não olhou é lido como "está tudo certo", e é assim que uma
verificação começa a mentir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..reconcile import plan_reconciliation
from .lifecycle import find_lifecycle_drift

SCHEMA_VERSION = "0.1.0"

# Por que a conformidade de corpo não é verificável a partir do snapshot: os adapters
# excluem descrição, corpo e comentários por decisão registrada em
# docs/connectors/README.md, e o snapshot sela rawPayloadPersisted: false. Abrir essa
# exceção exige ADR próprio (decisão D5, em aberto com o fundador).
CONTRACT_UNAVAILABLE_REASON = (
    "O snapshot não carrega a descrição do ticket: os adapters excluem descrição, "
    "corpo e comentários por decisão registrada em docs/connectors/README.md, e o "
    "snapshot sela rawPayloadPersisted: false. Verificar conformidade de corpo exige "
    "abrir essa exceção num caminho separado, com ADR próprio (decisão D5)."
)

# Sem baseline aprovado não há com o que comparar o inventário. Devolver zero
# propostas afirmaria "todo artefato virou ticket" sem ter olhado para artefato
# nenhum — mesma armadilha da deriva de contrato, mesma resposta (PIP-835).
COVERAGE_UNAVAILABLE_REASON = (
    "Nenhum ProductBaseline aprovado foi informado, então não há com o que comparar "
    "o inventário: a deriva de cobertura não foi calculada. Passe o baseline para "
    "que artefato sem ticket apareça."
)


@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    """Resultado somente-leitura. Não expõe apply, create, update nem write."""

    coverage: list[dict[str, Any]] = field(default_factory=list)
    lifecycle: list[dict[str, Any]] = field(default_factory=list)
    contract: dict[str, Any] = field(default_factory=dict)
    coverage_status: dict[str, Any] = field(default_factory=dict)
    blockers: list[dict[str, Any]] = field(default_factory=list)
    plan_id: str | None = None

    @property
    def summary(self) -> dict[str, Any]:
        blocking = sum(1 for f in self.lifecycle if f.get("severity") == "blocking")
        coverage_ran = self.coverage_status.get("status") == "available"
        contract_ran = self.contract.get("status") == "available"
        off_contract = int(self.contract.get("offContract") or 0)
        return {
            "coverageProposals": len(self.coverage),
            "lifecycleFindings": len(self.lifecycle),
            "lifecycleBlocking": blocking,
            "contractStatus": self.contract.get("status"),
            "coverageStatus": self.coverage_status.get("status"),
            "blockers": len(self.blockers),
            # Nenhuma deriva encontrada não é o mesmo que nenhuma deriva existente.
            # `clean` exige que a cobertura tenha REALMENTE rodado: dizer "em dia"
            # com metade da verificação pulada é a mentira que este campo evita.
            "offContract": off_contract,
            "clean": (
                coverage_ran
                and contract_ran
                and not self.coverage
                and blocking == 0
                and off_contract == 0
                and not self.blockers
            ),
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "planId": self.plan_id,
            "summary": self.summary,
            "coverage": list(self.coverage),
            "coverageStatus": dict(self.coverage_status),
            "lifecycle": list(self.lifecycle),
            "contract": dict(self.contract),
            "blockers": list(self.blockers),
        }


def reconcile(
    baseline: Mapping[str, Any] | None,
    observed: Mapping[str, Any],
    *,
    verification: Mapping[str, Any] | None = None,
    contract: Mapping[str, Any] | None = None,
) -> ReconciliationReport:
    """Compara o baseline aprovado com o inventário observado e propõe.

    `verification` é uma segunda leitura opcional: divergência entre a leitura e a
    verificação bloqueia a proposta afetada, no planner que já existe.

    `contract` é o resultado **já reduzido** da conformidade de corpo (ADR-003,
    PIP-845) — booleanos e nomes de campo. O reconciliador nunca recebe a descrição
    do ticket: a redução acontece antes, em `linear/conformance.py`, para que o texto
    não chegue nem ao raio de alcance deste módulo. Ausente, a deriva de contrato
    segue `unavailable` com motivo.
    """
    lifecycle = [
        finding.as_dict() for finding in find_lifecycle_drift(observed.get("records", []))
    ]
    contract = dict(contract) if contract else {
        "status": "unavailable",
        "reason": CONTRACT_UNAVAILABLE_REASON,
    }

    if baseline is None:
        return ReconciliationReport(
            coverage=[],
            coverage_status={"status": "unavailable", "reason": COVERAGE_UNAVAILABLE_REASON},
            lifecycle=lifecycle,
            contract=contract,
        )

    plan = plan_reconciliation(
        baseline,
        [observed],
        verification_snapshots=(verification,) if verification else (),
    )
    coverage = [
        action
        for action in plan.get("actions", [])
        if action.get("targetSystem") == "linear" and action.get("actionType") == "create"
    ]

    return ReconciliationReport(
        coverage=coverage,
        coverage_status={"status": "available"},
        lifecycle=lifecycle,
        contract=contract,
        blockers=list(plan.get("blockers", [])),
        plan_id=plan.get("planId"),
    )
