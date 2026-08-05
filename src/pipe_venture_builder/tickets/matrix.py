"""Registro de campos de ticket, carregado de contracts/ticket-field-matrix.json.

Fonte única (PIP-832). A tabela de execution/ticket-type-field-matrix.md é gerada
daqui — enquanto documento e código viviam separados em Markdown, podiam divergir
sem ninguém perceber, e divergiram.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field as dataclass_field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator, Literal, Mapping

Requirement = Literal["R", "C", "N"]

MATRIX_RELATIVE_PATH = "contracts/ticket-field-matrix.json"


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class TicketField:
    key: str
    heading: str
    aliases: tuple[str, ...] = ()
    by_type: Mapping[str, Requirement] = dataclass_field(default_factory=dict)
    note: str | None = None


@dataclass(frozen=True, slots=True)
class FieldRegistry:
    types: tuple[str, ...]
    baseline_fields: tuple[TicketField, ...]
    conditional_fields: tuple[TicketField, ...]
    unassigned_fields: tuple[TicketField, ...]
    legend: Mapping[str, str]

    def all_fields(self) -> Iterator[TicketField]:
        yield from self.baseline_fields
        yield from self.conditional_fields
        yield from self.unassigned_fields

    def by_key(self, key: str) -> TicketField | None:
        return next((f for f in self.all_fields() if f.key == key), None)

    def resolve_heading(self, heading: str) -> TicketField | None:
        """Casa o heading exato ou um alias declarado. Sem heurística de similaridade:
        adivinhar o que um humano quis dizer é como um check começa a mentir."""
        normalized = heading.strip()
        for candidate in self.all_fields():
            if normalized == candidate.heading or normalized in candidate.aliases:
                return candidate
        return None

    def requirement(self, key: str, ticket_type: str) -> Requirement:
        """R/C/N de um campo para um tipo.

        Baseline é R em todo tipo. Campo sem atribuição por tipo (os que existem no
        template e nunca ganharam linha na matriz) é sempre C: exigi-los seria
        inventar governança que ninguém aprovou.
        """
        if any(f.key == key for f in self.baseline_fields):
            return "R"
        for candidate in self.conditional_fields:
            if candidate.key == key:
                return candidate.by_type.get(ticket_type, "C")
        return "C"


def _field_from(raw: Mapping[str, Any]) -> TicketField:
    return TicketField(
        key=raw["key"],
        heading=raw["heading"],
        aliases=tuple(raw.get("aliases", ())),
        by_type=dict(raw.get("byType", {})),
        note=raw.get("note"),
    )


@lru_cache(maxsize=1)
def load_registry(path: Path | None = None) -> FieldRegistry:
    source = path or (_repository_root() / MATRIX_RELATIVE_PATH)
    raw = json.loads(source.read_text(encoding="utf-8"))
    return FieldRegistry(
        types=tuple(raw["types"]),
        baseline_fields=tuple(_field_from(f) for f in raw["baselineFields"]),
        conditional_fields=tuple(_field_from(f) for f in raw["conditionalFields"]),
        unassigned_fields=tuple(_field_from(f) for f in raw.get("unassignedFields", ())),
        legend=dict(raw["legend"]),
    )


BEGIN_MARKER = "<!-- BEGIN GENERATED: field-matrix -->"
END_MARKER = "<!-- END GENERATED: field-matrix -->"
PROVENANCE = (
    "<!-- Gerado de contracts/ticket-field-matrix.json por `pipe ticket matrix --emit-markdown`.\n"
    "     Não edite à mão: edite o JSON e regenere. O check de deriva reprova divergência. -->"
)


def emit_markdown_block(registry: FieldRegistry) -> str:
    """Bloco completo que vive entre os marcadores no documento.

    Emitir a procedência junto da tabela é o que permite comparação exata: se o
    documento e o gerador divergirem em um único byte, o check acusa.
    """
    return PROVENANCE + "\n" + emit_markdown_table(registry)


def emit_markdown_table(registry: FieldRegistry) -> str:
    """Renderiza a tabela R/C/N. Saída determinística: mesma entrada, mesmos bytes."""
    header = "| Field | " + " | ".join(registry.types) + " |"
    divider = "|---|" + "---|" * len(registry.types)
    rows = [
        "| "
        + field.heading
        + " | "
        + " | ".join(field.by_type.get(t, "C") for t in registry.types)
        + " |"
        for field in registry.conditional_fields
    ]
    return "\n".join([header, divider, *rows]) + "\n"
