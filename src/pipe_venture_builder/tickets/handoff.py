"""Render do handoff canônico de entrega.

O template NÃO é copiado para cá. Ele é lido de `execution/ticket-pr-handoff-system.md`,
que é a fonte de verdade declarada pela governança. Uma segunda cópia em JSON ou em
código seria o mesmo erro que esta fatia existe para corrigir — a duplicata que
diverge em silêncio e só aparece quando um agente segue a cópia errada.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

HANDOFF_DOC = "execution/ticket-pr-handoff-system.md"
HANDOFF_ANCHOR = "## Final execution handoff"
FENCE = "```"


class HandoffTemplateError(RuntimeError):
    """O documento canônico não contém o bloco de handoff esperado."""


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class HandoffTemplate:
    body: str

    def field_labels(self) -> list[str]:
        """Rótulos `Campo:` do template, na ordem — o que o preenchedor precisa cobrir."""
        return [
            match.group(1).strip()
            for match in re.finditer(r"^-?\s*([A-Z][^:\n]*):\s*$", self.body, re.MULTILINE)
        ]

    def render(self, values: Mapping[str, str] | None = None) -> str:
        """Preenche os rótulos informados e deixa os demais em branco.

        Rótulo desconhecido é erro do chamador e falha alto: um handoff que engole
        campo digitado errado publica evidência incompleta parecendo completa.
        """
        if not values:
            return self.body
        known = set(self.field_labels())
        unknown = sorted(set(values) - known)
        if unknown:
            raise HandoffTemplateError(
                f"rótulos fora do template canônico: {', '.join(unknown)}"
            )

        lines = self.body.splitlines()
        out: list[str] = []
        for line in lines:
            match = re.match(r"^(-?\s*)([A-Z][^:\n]*):\s*$", line)
            if match and match.group(2).strip() in values:
                out.append(f"{match.group(1)}{match.group(2)}: {values[match.group(2).strip()]}")
            else:
                out.append(line)
        return "\n".join(out) + ("\n" if self.body.endswith("\n") else "")


def load_handoff_template(root: Path | None = None) -> HandoffTemplate:
    path = (root or _repository_root()) / HANDOFF_DOC
    text = path.read_text(encoding="utf-8")

    anchor = text.find(HANDOFF_ANCHOR)
    if anchor == -1:
        raise HandoffTemplateError(f"{HANDOFF_DOC} não contém '{HANDOFF_ANCHOR}'")

    start = text.rfind(FENCE, 0, anchor)
    if start == -1:
        raise HandoffTemplateError(f"{HANDOFF_DOC}: bloco de handoff sem abertura de fence")
    start = text.index("\n", start) + 1

    end = text.find(f"\n{FENCE}", start)
    if end == -1:
        raise HandoffTemplateError(f"{HANDOFF_DOC}: bloco de handoff sem fechamento de fence")

    return HandoffTemplate(body=text[start:end] + "\n")
