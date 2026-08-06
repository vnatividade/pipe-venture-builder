"""Deriva de ciclo de vida sobre registros de snapshot (PIP-834).

Torna executáveis duas regras que hoje são prosa:

- `execution/linear-governance-model.md:135` — "Do not close implementation tickets
  without a merged PR". Sem verificação, é exortação.
- `approval:granted` sem lastro. **Não** reprova o ticket: a política vigente aceita
  quatro canais de aprovação, e endurecer isso é mudança de regra de aprovação com
  ticket próprio. Aqui a label só é *sinalizada* para conferência humana.

Estas funções são puras: recebem registros já normalizados e devolvem achados. Não
existe caminho de mutação neste módulo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse

# Hosts que constituem evidência de entrega. Anexar um documento qualquer não prova
# que a entrega aconteceu — a lista é explícita de propósito.
DELIVERY_EVIDENCE_HOSTS = ("github.com", "gitlab.com", "bitbucket.org")

# Estados terminais que exigem evidência. `Canceled` encerra sem entrega por definição.
COMPLETED_STATES = ("done", "completed", "merged", "shipped")
CANCELLED_STATES = ("canceled", "cancelled", "duplicate")

APPROVAL_CLAIM_LABEL = "approval:granted"


@dataclass(frozen=True, slots=True)
class LifecycleFinding:
    source_key: str
    rule: str
    summary: str
    severity: str
    url: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "sourceKey": self.source_key,
            "rule": self.rule,
            "summary": self.summary,
            "severity": self.severity,
            "url": self.url,
        }


def _state_of(record: Mapping[str, Any]) -> str:
    return str(record.get("state") or "").strip().lower()


def _is_delivery_evidence(url: Any) -> bool:
    try:
        host = (urlparse(str(url)).hostname or "").lower()
    except ValueError:
        return False
    return any(host == known or host.endswith(f".{known}") for known in DELIVERY_EVIDENCE_HOSTS)


def _children_by_parent(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    children: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        for relationship in record.get("relationships") or []:
            if not isinstance(relationship, Mapping):
                continue
            if relationship.get("type") == "child_of" and relationship.get("targetSourceId"):
                children.setdefault(str(relationship["targetSourceId"]), []).append(record)
    return children


def _has_own_evidence(record: Mapping[str, Any]) -> bool:
    links = (record.get("attributes") or {}).get("deliveryLinks") or []
    return any(_is_delivery_evidence(link) for link in links)


def _children_carry_the_evidence(children: Sequence[Mapping[str, Any]]) -> bool:
    """Evidência transitiva (PIP-846): um guarda-chuva não tem PR próprio — a entrega
    vive nos filhos.

    A exigência é deliberadamente dura: **todos** concluídos **e cada um** com
    evidência. Aceitar apenas "tem filhos" faria qualquer ticket virar guarda-chuva e
    parar de pedir prova — a brecha óbvia. Aqui a prova continua obrigatória; ela só
    passa a poder vir por baixo.
    """
    if not children:
        return False
    return all(
        _state_of(child) in COMPLETED_STATES and _has_own_evidence(child)
        for child in children
    )


def find_lifecycle_drift(records: Iterable[Mapping[str, Any]]) -> list[LifecycleFinding]:
    records = list(records)
    children_by_parent = _children_by_parent(records)
    findings: list[LifecycleFinding] = []
    for record in records:
        if record.get("entityType") != "issue":
            continue
        key = str(record.get("sourceKey") or record.get("sourceId") or "")
        attributes = record.get("attributes") or {}
        labels = [str(label) for label in (attributes.get("labels") or [])]
        state = _state_of(record)
        children = children_by_parent.get(str(record.get("sourceId") or ""), [])

        if (
            state in COMPLETED_STATES
            and not _has_own_evidence(record)
            and not _children_carry_the_evidence(children)
        ):
            findings.append(
                LifecycleFinding(
                    source_key=key,
                    rule="completed_without_delivery_evidence",
                    summary=(
                        "Ticket fechado sem link de entrega (PR) anexado, e sem filhos "
                        "que carreguem essa evidência. Um ticket de implementação não "
                        "deveria fechar sem merge."
                    ),
                    severity="blocking",
                    url=record.get("url"),
                )
            )

        if APPROVAL_CLAIM_LABEL in labels and state not in CANCELLED_STATES:
            findings.append(
                LifecycleFinding(
                    source_key=key,
                    rule="approval_claimed_without_source",
                    summary=(
                        f"Label {APPROVAL_CLAIM_LABEL} presente. A política aceita quatro "
                        "canais de aprovação e o snapshot não vê nenhum deles — confira à mão."
                    ),
                    severity="advisory",
                    url=record.get("url"),
                )
            )
    return findings
