"""PIP-832: o contrato de ticket precisa ser código, não prosa.

A governança define ~44 campos e quais são obrigatórios por tipo, tudo em Markdown
e sem nada que verifique. O resultado empírico é o workspace: os tickets recentes não
seguem o template e não têm label nenhuma. Estes testes existem para que "conformidade"
deixe de depender de disciplina humana.

O parser é deliberadamente TOLERANTE: heading editado à mão não pode derrubar a
ferramenta. Um check que quebra vira ruído, ruído vira relatório ignorado, e relatório
ignorado é pior que não ter check.
"""

from __future__ import annotations

import json
from unittest import TestCase

from pipe_venture_builder.tickets import (
    FieldRegistry,
    check_conformance,
    parse_ticket,
    render_ticket,
)
from pipe_venture_builder.tickets.matrix import (
    BEGIN_MARKER,
    END_MARKER,
    emit_markdown_block,
    load_registry,
)
from tests.helpers import REPOSITORY_ROOT


MATRIX_PATH = REPOSITORY_ROOT / "contracts/ticket-field-matrix.json"
MATRIX_DOC = REPOSITORY_ROOT / "execution/ticket-type-field-matrix.md"
TEMPLATE_DOC = REPOSITORY_ROOT / "execution/linear-ticket-template-v2.md"


def minimal_ticket(ticket_type: str = "automation") -> dict[str, str]:
    registry = load_registry()
    fields = {field.key: f"conteúdo de {field.heading}" for field in registry.baseline_fields}
    fields["type"] = ticket_type
    for field in registry.conditional_fields:
        if registry.requirement(field.key, ticket_type) == "R":
            fields[field.key] = f"conteúdo de {field.heading}"
    return fields


class RegistryTests(TestCase):
    def test_registry_loads_the_twelve_approved_types(self) -> None:
        registry = load_registry()
        self.assertEqual(len(registry.types), 12)
        self.assertIn("automation", registry.types)
        self.assertNotIn("research", registry.types, "research não está no enum aprovado")

    def test_every_conditional_field_covers_every_type(self) -> None:
        registry = load_registry()
        for field in registry.conditional_fields:
            for ticket_type in registry.types:
                with self.subTest(field=field.key, type=ticket_type):
                    self.assertIn(registry.requirement(field.key, ticket_type), {"R", "C", "N"})

    def test_keys_are_unique_across_all_field_groups(self) -> None:
        raw = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        keys = [
            field["key"]
            for group in ("baselineFields", "conditionalFields", "unassignedFields")
            for field in raw[group]
        ]
        self.assertEqual(len(keys), len(set(keys)), "chave duplicada entre grupos de campo")

    def test_unassigned_fields_never_block_conformance(self) -> None:
        """Tactical Execution Plan e Development Execution Loop aparecem no template
        e nunca ganharam linha na matriz. Exigi-los seria inventar governança."""
        registry = load_registry()
        for field in registry.unassigned_fields:
            for ticket_type in registry.types:
                self.assertEqual(registry.requirement(field.key, ticket_type), "C")


class RenderParseTests(TestCase):
    def test_round_trip_preserves_every_field(self) -> None:
        fields = minimal_ticket()
        parsed = parse_ticket(render_ticket(fields))
        self.assertEqual(parsed.fields, fields)
        self.assertEqual(parsed.unparsed_sections, [])

    def test_render_follows_the_registry_order(self) -> None:
        registry = load_registry()
        body = render_ticket(minimal_ticket())
        headings = [line[3:].strip() for line in body.splitlines() if line.startswith("## ")]
        expected = [f.heading for f in registry.baseline_fields if f.key in minimal_ticket()]
        self.assertEqual(headings[: len(expected)], expected)

    def test_parser_keeps_unknown_sections_instead_of_raising(self) -> None:
        body = render_ticket(minimal_ticket()) + "\n\n## Seção Inventada\n\nalgo que um humano escreveu\n"
        parsed = parse_ticket(body)
        self.assertEqual([s.heading for s in parsed.unparsed_sections], ["Seção Inventada"])
        self.assertIn("algo que um humano escreveu", parsed.unparsed_sections[0].body)

    def test_parser_accepts_declared_aliases(self) -> None:
        parsed = parse_ticket("## Rationale\n\nporque sim\n\n## Objective\n\nfazer X\n")
        self.assertEqual(parsed.fields["whyThisMatters"], "porque sim")
        self.assertEqual(parsed.fields["objective"], "fazer X")

    def test_parser_never_raises_on_garbage(self) -> None:
        for body in ("", "sem heading nenhum", "#### nível errado\n\nx", "## \n\nheading vazio"):
            with self.subTest(body=body[:20]):
                parse_ticket(body)

    def test_parser_ignores_headings_inside_code_fences(self) -> None:
        body = "## Objective\n\nfazer X\n\n```md\n## Included Scope\n\nisto é exemplo\n```\n"
        parsed = parse_ticket(body)
        self.assertNotIn("includedScope", parsed.fields)
        self.assertIn("## Included Scope", parsed.fields["objective"])


class ConformanceTests(TestCase):
    def test_complete_ticket_passes(self) -> None:
        report = check_conformance(parse_ticket(render_ticket(minimal_ticket())))
        self.assertTrue(report.ok, report.missing)

    def test_missing_baseline_field_is_reported_by_name(self) -> None:
        fields = minimal_ticket()
        del fields["acceptanceCriteria"]
        report = check_conformance(parse_ticket(render_ticket(fields)))
        self.assertFalse(report.ok)
        self.assertIn("Acceptance Criteria", [item.heading for item in report.missing])

    def test_required_conditional_depends_on_the_type(self) -> None:
        """technicalDependencies é R para code e N para documentation."""
        code = minimal_ticket("code")
        del code["technicalDependencies"]
        self.assertFalse(check_conformance(parse_ticket(render_ticket(code))).ok)

        docs = minimal_ticket("documentation")
        docs.pop("technicalDependencies", None)
        self.assertTrue(check_conformance(parse_ticket(render_ticket(docs))).ok)

    def test_unknown_type_is_a_finding_not_a_crash(self) -> None:
        fields = minimal_ticket()
        fields["type"] = "inventado"
        report = check_conformance(parse_ticket(render_ticket(fields)))
        self.assertFalse(report.ok)
        self.assertTrue(any("inventado" in problem for problem in report.problems))

    def test_empty_field_counts_as_missing_not_present(self) -> None:
        fields = minimal_ticket()
        fields["objective"] = "   "
        report = check_conformance(parse_ticket(render_ticket(fields)))
        self.assertIn("Objective", [item.heading for item in report.missing])

    def test_report_separates_missing_from_unreadable(self) -> None:
        body = render_ticket(minimal_ticket()) + "\n\n## Coisa Estranha\n\nx\n"
        report = check_conformance(parse_ticket(body))
        self.assertTrue(report.ok, "seção desconhecida não reprova o ticket")
        self.assertEqual(report.unparsed, ["Coisa Estranha"])


class GeneratedDocTests(TestCase):
    def test_matrix_markdown_in_the_doc_matches_the_json(self) -> None:
        """Guarda de deriva: editar o JSON sem regenerar o Markdown falha aqui."""
        current = MATRIX_DOC.read_text(encoding="utf-8")
        self.assertIn(BEGIN_MARKER, current)
        self.assertIn(END_MARKER, current)
        start = current.index(BEGIN_MARKER) + len(BEGIN_MARKER)
        end = current.index(END_MARKER)
        self.assertEqual(
            current[start:end].strip(),
            emit_markdown_block(load_registry()).strip(),
            "matriz do documento fora de sincronia com o JSON — rode `pipe ticket matrix --emit-markdown`",
        )

    def test_every_template_heading_exists_in_the_registry(self) -> None:
        """Se o template ganhar uma seção que o registro não conhece, ela viraria
        `unparsedSections` para sempre e ninguém perceberia."""
        registry = load_registry()
        known = {f.heading for f in registry.all_fields()}
        for field in registry.all_fields():
            known.update(field.aliases)

        template = TEMPLATE_DOC.read_text(encoding="utf-8").splitlines()
        inside_fence = False
        headings: list[str] = []
        for line in template:
            if line.startswith("```"):
                inside_fence = not inside_fence
                continue
            if inside_fence and line.startswith("## "):
                headings.append(line[3:].strip())

        self.assertTrue(headings, "não achei o bloco do template")
        unknown = [h for h in headings if h not in known]
        self.assertEqual(unknown, [], f"seções do template fora do registro: {unknown}")
