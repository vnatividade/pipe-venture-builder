"""PIP-832: o handoff canônico é lido do documento, nunca copiado."""

from __future__ import annotations

from unittest import TestCase

from pipe_venture_builder.tickets.handoff import (
    HandoffTemplateError,
    load_handoff_template,
)
from tests.helpers import REPOSITORY_ROOT


class HandoffTemplateTests(TestCase):
    def test_loads_the_canonical_block_from_the_governance_doc(self) -> None:
        template = load_handoff_template()
        self.assertIn("## Final execution handoff", template.body)
        self.assertIn("## Residual risks", template.body)
        self.assertNotIn("```", template.body, "o fence não faz parte do template")

    def test_field_labels_cover_the_evidence_the_governance_requires(self) -> None:
        labels = load_handoff_template().field_labels()
        for required in ("Branch", "PR", "Merge commit", "Linear ticket", "Review source", "P0"):
            self.assertIn(required, labels)

    def test_render_fills_only_the_given_labels(self) -> None:
        rendered = load_handoff_template().render({"Branch": "claude/pip-832", "P0": "0"})
        lines = rendered.splitlines()
        self.assertIn("Branch: claude/pip-832", lines)
        self.assertIn("- P0: 0", lines)
        # Rótulo não informado continua nu: "PR:" e não "PR: alguma coisa".
        self.assertIn("PR:", lines)
        self.assertIn("- P1:", lines)

    def test_unknown_label_fails_loud(self) -> None:
        """Engolir rótulo digitado errado publicaria evidência incompleta com cara de completa."""
        with self.assertRaises(HandoffTemplateError):
            load_handoff_template().render({"Branchh": "x"})

    def test_template_v2_no_longer_carries_a_second_copy(self) -> None:
        """A duplicata em linear-ticket-template-v2.md virou ponteiro (PIP-832)."""
        text = (REPOSITORY_ROOT / "execution/linear-ticket-template-v2.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("## Final execution handoff", text)
        self.assertIn("execution/ticket-pr-handoff-system.md", text)

    def test_the_codex_agent_handoff_is_a_different_artifact_and_stays(self) -> None:
        """`.codex/agents/agent-handoff-protocol.md` é handoff agente→agente, não de
        entrega. Colapsar os dois destruiria uma distinção real."""
        text = (REPOSITORY_ROOT / ".codex/agents/agent-handoff-protocol.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Agent Handoff", text)
        self.assertNotIn("## Final execution handoff", text)
