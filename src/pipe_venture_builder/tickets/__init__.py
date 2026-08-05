"""Contrato de ticket do Pipe (PIP-832): registro de campos, render, parse, conformidade."""

from .conformance import ConformanceReport, MissingField, check_conformance
from .document import ParsedTicket, UnparsedSection, parse_ticket, render_ticket
from .matrix import FieldRegistry, TicketField, emit_markdown_table, load_registry

__all__ = [
    "ConformanceReport",
    "FieldRegistry",
    "MissingField",
    "ParsedTicket",
    "TicketField",
    "UnparsedSection",
    "check_conformance",
    "emit_markdown_table",
    "load_registry",
    "parse_ticket",
    "render_ticket",
]
