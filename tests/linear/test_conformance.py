"""PIP-845: conformidade de corpo sob o ADR-003.

O teste que importa aqui é o **sentinela**. O ADR-003 diz, com todas as letras, que a
fronteira é o teste e não a intenção escrita no documento: uma implementação que passe
em todos os outros e não tenha este NÃO cumpre o ADR.

Motivo: o risco registrado não é a leitura, é a erosão. A saída começa booleana e um
dia alguém acha útil incluir "só um trecho para ajudar a depurar". O sentinela é o que
faz esse dia virar um teste vermelho em vez de um vazamento silencioso.
"""

from __future__ import annotations

import json
from unittest import TestCase

from pipe_venture_builder.linear.conformance import (
    ContractFinding,
    evaluate_bodies,
    summarise,
)
from pipe_venture_builder.linear.reconciler import reconcile
from pipe_venture_builder.tickets import load_registry, render_ticket
from tests.linear.test_reconciler import issue_record
from tests.reconcile.helpers import snapshot

# String improvável de aparecer por acaso. Se ela sair em qualquer lugar da saída,
# a fronteira do ADR-003 caiu.
SENTINELA = "SENTINELA-b7f3a91c-CONTEUDO-QUE-NUNCA-DEVE-VAZAR"


def corpo_completo(ticket_type: str = "documentation", *, com_sentinela: bool = False) -> str:
    registry = load_registry()
    fields = {f.key: f"conteúdo de {f.heading}" for f in registry.baseline_fields}
    fields["type"] = ticket_type
    for field in registry.conditional_fields:
        if registry.requirement(field.key, ticket_type) == "R":
            fields[field.key] = f"conteúdo de {field.heading}"
    if com_sentinela:
        fields["objective"] = SENTINELA
    return render_ticket(fields)


class SentinelBoundaryTests(TestCase):
    """A fronteira do ADR-003, em teste. Estes são os testes que não podem sumir."""

    def test_the_body_never_reaches_the_finding(self) -> None:
        achados = evaluate_bodies({"PIP-1": corpo_completo(com_sentinela=True)})
        self.assertNotIn(SENTINELA, json.dumps([f.as_dict() for f in achados], ensure_ascii=False))

    def test_the_body_never_reaches_the_contract_summary(self) -> None:
        resumo = summarise(evaluate_bodies({"PIP-1": corpo_completo(com_sentinela=True)}))
        self.assertNotIn(SENTINELA, json.dumps(resumo, ensure_ascii=False))

    def test_the_body_never_reaches_the_serialized_report(self) -> None:
        """O caminho inteiro: corpo → conformidade → relatório de reconciliação."""
        achados = evaluate_bodies({"PIP-1": corpo_completo(com_sentinela=True)})
        relatorio = reconcile(
            None,
            snapshot([issue_record("PIP-1")]),
            contract=summarise(achados),
        ).as_dict()
        self.assertNotIn(SENTINELA, json.dumps(relatorio, ensure_ascii=False))

    def test_an_off_contract_ticket_still_does_not_leak(self) -> None:
        """O caminho de falha é o mais perigoso: é onde dá vontade de explicar."""
        corpo = f"## Objective\n\n{SENTINELA}\n\n## Type\n\ncode\n"
        resumo = summarise(evaluate_bodies({"PIP-1": corpo}))
        self.assertEqual(resumo["offContract"], 1)
        self.assertNotIn(SENTINELA, json.dumps(resumo, ensure_ascii=False))

    def test_an_unknown_type_does_not_echo_the_type_value(self) -> None:
        """Ecoar o tipo inválido seria a exceção mais tentadora e mais defensável.
        O ADR diz booleano e nome de campo, ponto — a primeira exceção é a erosão."""
        corpo = f"## Type\n\n{SENTINELA}\n"
        resumo = summarise(evaluate_bodies({"PIP-1": corpo}))
        self.assertNotIn(SENTINELA, json.dumps(resumo, ensure_ascii=False))
        self.assertFalse(resumo["findings"][0]["typeRecognised"])

    def test_an_unknown_section_heading_is_counted_not_named(self) -> None:
        """Heading é texto que um humano escreveu no corpo."""
        corpo = corpo_completo() + f"\n\n## {SENTINELA}\n\nalgo\n"
        resumo = summarise(evaluate_bodies({"PIP-1": corpo}))
        self.assertNotIn(SENTINELA, json.dumps(resumo, ensure_ascii=False))

    def test_the_finding_has_no_field_that_could_hold_free_text(self) -> None:
        """Guarda estrutural: se alguém acrescentar um campo de texto livre ao
        ContractFinding, este teste falha antes de o vazamento acontecer."""
        permitidos = {
            "source_key",
            "has_type",
            "type_recognised",
            "missing_fields",
            "unparsed_sections",
        }
        self.assertEqual(set(ContractFinding.__slots__), permitidos)


class ConformanceEvaluationTests(TestCase):
    def test_a_complete_ticket_is_ok(self) -> None:
        achados = evaluate_bodies({"PIP-1": corpo_completo()})
        self.assertTrue(achados[0].ok)
        self.assertEqual(achados[0].missing_fields, ())

    def test_a_missing_required_field_is_named_by_our_registry(self) -> None:
        registry = load_registry()
        fields = {f.key: "x" for f in registry.baseline_fields}
        fields["type"] = "documentation"
        del fields["acceptanceCriteria"]
        achados = evaluate_bodies({"PIP-1": render_ticket(fields)})
        self.assertIn("Acceptance Criteria", achados[0].missing_fields)

    def test_the_required_set_depends_on_the_type(self) -> None:
        """`technicalDependencies` é R para code e N para documentation."""
        registry = load_registry()

        def corpo(ticket_type: str) -> str:
            fields = {f.key: "x" for f in registry.baseline_fields}
            fields["type"] = ticket_type
            return render_ticket(fields)

        code = evaluate_bodies({"PIP-1": corpo("code")})[0]
        docs = evaluate_bodies({"PIP-1": corpo("documentation")})[0]
        self.assertIn("Technical Dependencies", code.missing_fields)
        self.assertNotIn("Technical Dependencies", docs.missing_fields)

    def test_an_empty_body_does_not_crash(self) -> None:
        achados = evaluate_bodies({"PIP-1": ""})
        self.assertFalse(achados[0].has_type)

    def test_the_summary_only_lists_tickets_that_are_off_contract(self) -> None:
        resumo = summarise(
            evaluate_bodies({"PIP-1": corpo_completo(), "PIP-2": "## Type\n\ncode\n"})
        )
        self.assertEqual(resumo["evaluated"], 2)
        self.assertEqual([f["sourceKey"] for f in resumo["findings"]], ["PIP-2"])
