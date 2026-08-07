"""Conformidade de corpo de ticket sob o ADR-003 (PIP-845).

O ADR autoriza ler a descrição de issue e impõe a fronteira: **o texto entra no
processo, é avaliado, e não sai**. O que sai é booleano e nome de campo.

Como essa fronteira é construída aqui, e não só prometida:

- A descrição nunca entra no `ExternalSnapshot`. Este é um caminho próprio.
- `ContractFinding` é **estruturalmente incapaz** de carregar o texto: todos os seus
  campos são booleano, contagem, ou heading vindo do NOSSO registro
  (`contracts/ticket-field-matrix.json`) — nunca do corpo lido.
- Nada aqui ecoa valor extraído do corpo. Nem o tipo de ticket, que seria a exceção
  mais tentadora e mais defensável. O ADR diz "booleano e nome de campo", ponto; abrir
  a primeira exceção no primeiro dia é exatamente a erosão que ele previu.
- `unparsed_sections` é **contagem**, não a lista de headings: heading é texto que um
  humano escreveu no corpo.

Quem precisar saber *o que* está errado abre o ticket. O relatório diz *onde*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..tickets import check_conformance, parse_ticket


@dataclass(frozen=True, slots=True)
class ContractFinding:
    """Resultado reduzido de um ticket. Não carrega conteúdo do corpo, por construção."""

    source_key: str
    has_type: bool
    type_recognised: bool
    missing_fields: tuple[str, ...]
    unparsed_sections: int

    @property
    def ok(self) -> bool:
        return self.has_type and self.type_recognised and not self.missing_fields

    def as_dict(self) -> dict[str, Any]:
        return {
            "sourceKey": self.source_key,
            "hasType": self.has_type,
            "typeRecognised": self.type_recognised,
            "missingFields": list(self.missing_fields),
            "unparsedSections": self.unparsed_sections,
            "ok": self.ok,
        }


def evaluate_bodies(bodies: Mapping[str, str]) -> list[ContractFinding]:
    """Avalia `{identificador: descrição}` e devolve só o resultado reduzido.

    O texto vive no argumento e morre no fim desta função. Nenhum valor extraído
    dele aparece no retorno.
    """
    findings: list[ContractFinding] = []
    for source_key, body in sorted(bodies.items()):
        parsed = parse_ticket(body or "")
        report = check_conformance(parsed)
        findings.append(
            ContractFinding(
                source_key=str(source_key),
                has_type=parsed.ticket_type is not None,
                # `problems` do relatório carrega o valor do tipo lido do corpo, então
                # não é repassado: derivamos só o booleano.
                type_recognised=not report.problems,
                # Headings do nosso registro, não do corpo — seguros por construção.
                missing_fields=tuple(item.heading for item in report.missing),
                unparsed_sections=len(report.unparsed),
            )
        )
    return findings


def summarise(findings: list[ContractFinding]) -> dict[str, Any]:
    """Bloco de contrato para o relatório de reconciliação."""
    off_contract = [f for f in findings if not f.ok]
    return {
        "status": "available",
        "evaluated": len(findings),
        "offContract": len(off_contract),
        "findings": [f.as_dict() for f in off_contract],
    }


def fetch_bodies(
    invoke: Any,
    project_id: str,
    *,
    operation: str,
    page_size: int = 25,
    max_pages: int = 20,
) -> dict[str, str]:
    """Pagina as descrições pelo caminho separado.

    Página menor que a do snapshot de propósito: descrição é o campo mais pesado da
    issue, e o teto de complexidade da Linear é por query. Paginar mais vezes é barato.

    O dicionário devolvido é a única coisa que carrega texto neste fluxo, e ele morre
    em `evaluate_bodies`.
    """
    bodies: dict[str, str] = {}
    cursor: str | None = None
    for _ in range(max_pages):
        arguments: dict[str, Any] = {"project": project_id, "limit": page_size}
        if cursor:
            arguments["cursor"] = cursor
        page = invoke(operation, arguments)
        bodies.update(page.get("bodies") or {})
        page_info = page.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
    return bodies
