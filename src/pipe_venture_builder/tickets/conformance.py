"""Conformidade do corpo de ticket com o contrato do seu tipo.

Regra central do relatório: **"campo ausente" e "não consegui ler" são coisas
diferentes** e aparecem separadas. Misturar as duas é o começo do relatório que
ninguém lê.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field

from .document import ParsedTicket
from .matrix import FieldRegistry, TicketField, load_registry


@dataclass(frozen=True, slots=True)
class MissingField:
    key: str
    heading: str
    requirement: str


@dataclass(slots=True)
class ConformanceReport:
    ticket_type: str | None
    missing: list[MissingField] = dataclass_field(default_factory=list)
    problems: list[str] = dataclass_field(default_factory=list)
    unparsed: list[str] = dataclass_field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Seção desconhecida NÃO reprova: o humano pode acrescentar contexto próprio.
        O que reprova é campo obrigatório ausente ou tipo inválido."""
        return not self.missing and not self.problems

    def as_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "ticketType": self.ticket_type,
            "missing": [
                {"key": m.key, "heading": m.heading, "requirement": m.requirement}
                for m in self.missing
            ],
            "problems": list(self.problems),
            "unparsedSections": list(self.unparsed),
        }


def _is_present(value: str | None) -> bool:
    return bool(value and value.strip())


def check_conformance(
    ticket: ParsedTicket,
    registry: FieldRegistry | None = None,
) -> ConformanceReport:
    reg = registry or load_registry()
    ticket_type = ticket.ticket_type
    report = ConformanceReport(ticket_type=ticket_type)
    report.unparsed = [section.heading for section in ticket.unparsed_sections]

    if ticket_type is None:
        report.problems.append("campo Type ausente: sem tipo não dá para saber o que é obrigatório")
        return report
    if ticket_type not in reg.types:
        report.problems.append(
            f'tipo "{ticket_type}" fora do enum aprovado ({", ".join(reg.types)})'
        )
        return report

    def record(field: TicketField) -> None:
        requirement = reg.requirement(field.key, ticket_type)
        if requirement == "R" and not _is_present(ticket.fields.get(field.key)):
            report.missing.append(
                MissingField(key=field.key, heading=field.heading, requirement=requirement)
            )

    for field in reg.baseline_fields:
        record(field)
    for field in reg.conditional_fields:
        record(field)

    return report
