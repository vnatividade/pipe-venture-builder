"""Render e parse do corpo de ticket — round-trip sobre o registro de campos.

O parser é deliberadamente tolerante. Ticket é escrito por humano e por agente, e um
heading renomeado à mão não pode derrubar a ferramenta: seção desconhecida vai para
`unparsed_sections` e a vida segue. Um check que quebra vira ruído, ruído vira
relatório ignorado, e relatório ignorado é pior que não ter check nenhum.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .matrix import FieldRegistry, load_registry

FENCE_PREFIX = "```"
HEADING_PREFIX = "## "


@dataclass(frozen=True, slots=True)
class UnparsedSection:
    heading: str
    body: str


@dataclass(frozen=True, slots=True)
class ParsedTicket:
    fields: dict[str, str]
    unparsed_sections: list[UnparsedSection]

    @property
    def ticket_type(self) -> str | None:
        value = self.fields.get("type", "").strip()
        return value or None


def render_ticket(fields: Mapping[str, str], registry: FieldRegistry | None = None) -> str:
    """Serializa na ordem do registro. Campo ausente é omitido, não renderizado vazio:
    seção vazia é indistinguível de campo não preenchido para quem lê depois."""
    reg = registry or load_registry()
    blocks: list[str] = []
    for field in reg.all_fields():
        if field.key not in fields:
            continue
        blocks.append(f"{HEADING_PREFIX}{field.heading}\n\n{fields[field.key]}".rstrip())
    return "\n\n".join(blocks) + "\n"


def parse_ticket(body: str, registry: FieldRegistry | None = None) -> ParsedTicket:
    """Nunca levanta exceção. Entrada ruim produz resultado pobre, não travamento."""
    reg = registry or load_registry()
    fields: dict[str, str] = {}
    unparsed: list[UnparsedSection] = []

    current_heading: str | None = None
    buffer: list[str] = []
    inside_fence = False

    def flush() -> None:
        if current_heading is None:
            return
        content = "\n".join(buffer).strip()
        field = reg.resolve_heading(current_heading)
        if field is not None:
            fields[field.key] = content
        elif current_heading.strip():
            unparsed.append(UnparsedSection(heading=current_heading.strip(), body=content))

    for line in (body or "").splitlines():
        # Heading dentro de fence é exemplo, não estrutura. Sem esta guarda, um ticket
        # que documenta o próprio template teria suas seções sequestradas pelo exemplo.
        if line.lstrip().startswith(FENCE_PREFIX):
            inside_fence = not inside_fence
            buffer.append(line)
            continue
        if not inside_fence and line.startswith(HEADING_PREFIX) and not line.startswith("### "):
            flush()
            current_heading = line[len(HEADING_PREFIX):]
            buffer = []
            continue
        buffer.append(line)
    flush()

    return ParsedTicket(fields=fields, unparsed_sections=unparsed)
