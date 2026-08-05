"""PIP-832: os comandos de contrato são offline e têm código de saída estável.

Código de saída importa mais que mensagem aqui: estes comandos vão para hook de
pre-push e para CI, onde ninguém lê a saída — só o zero ou não-zero.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.cli import main
from pipe_venture_builder.exit_codes import READINESS_BLOCKED, SUCCESS
from pipe_venture_builder.tickets import load_registry, render_ticket


def complete_ticket_body(ticket_type: str = "documentation") -> str:
    registry = load_registry()
    fields = {f.key: f"conteúdo de {f.heading}" for f in registry.baseline_fields}
    fields["type"] = ticket_type
    for field in registry.conditional_fields:
        if registry.requirement(field.key, ticket_type) == "R":
            fields[field.key] = f"conteúdo de {field.heading}"
    return render_ticket(fields)


class TicketCliTests(TestCase):
    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        code = main(argv, stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()

    def test_check_passes_on_a_complete_ticket(self) -> None:
        with TemporaryDirectory() as tmp:
            body = Path(tmp) / "ticket.md"
            body.write_text(complete_ticket_body(), encoding="utf-8")
            code, out, _ = self._run(["ticket", "check", str(body), "--json"])
        self.assertEqual(code, SUCCESS)
        self.assertTrue(json.loads(out)["ok"])

    def test_check_blocks_on_a_missing_required_field(self) -> None:
        with TemporaryDirectory() as tmp:
            body = Path(tmp) / "ticket.md"
            body.write_text("## Objective\n\nfazer X\n\n## Type\n\ncode\n", encoding="utf-8")
            code, _, err = self._run(["ticket", "check", str(body), "--json"])
        self.assertEqual(code, READINESS_BLOCKED)
        payload = json.loads(err)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("Acceptance Criteria" in d["message"] for d in payload["errors"]),
            payload["errors"],
        )

    def test_check_reports_an_unknown_type_instead_of_crashing(self) -> None:
        with TemporaryDirectory() as tmp:
            body = Path(tmp) / "ticket.md"
            body.write_text("## Type\n\nresearch\n", encoding="utf-8")
            code, _, err = self._run(["ticket", "check", str(body), "--json"])
        self.assertEqual(code, READINESS_BLOCKED)
        self.assertIn("research", err)

    def test_missing_file_is_a_clean_error_not_a_traceback(self) -> None:
        code, _, err = self._run(["ticket", "check", "/nao/existe.md", "--json"])
        self.assertNotEqual(code, SUCCESS)
        self.assertEqual(json.loads(err)["code"], "INPUT_UNAVAILABLE")

    def test_render_rejects_field_keys_outside_the_contract(self) -> None:
        with TemporaryDirectory() as tmp:
            fields = Path(tmp) / "fields.json"
            fields.write_text(json.dumps({"objective": "x", "inventado": "y"}), encoding="utf-8")
            code, _, err = self._run(["ticket", "render", str(fields), "--json"])
        self.assertEqual(code, READINESS_BLOCKED)
        self.assertIn("inventado", err)

    def test_matrix_emit_is_idempotent_against_the_committed_doc(self) -> None:
        """Se o documento estivesse fora de sincronia, este comando o mudaria —
        e `changed: true` é o sinal de que alguém editou o Markdown à mão."""
        code, out, _ = self._run(["ticket", "matrix", "--emit-markdown", "--json"])
        self.assertEqual(code, SUCCESS)
        self.assertFalse(json.loads(out)["changed"])

    def test_handoff_render_emits_the_canonical_block(self) -> None:
        code, out, _ = self._run(["handoff", "render", "--json"])
        self.assertEqual(code, SUCCESS)
        self.assertIn("## Final execution handoff", json.loads(out)["body"])
