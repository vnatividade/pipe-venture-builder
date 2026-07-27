# Ponte pipe (Python) ↔ pipe-os (Node) via ProductBaseline

Fronteira do ADR-VOS-006: o CLI Python `pipe` gera o **estado canônico** (`ProductBaseline`);
o runtime Node `pipe-os` executa o **loop** (máquina de estados, gates, HITL). O contrato de
integração entre os dois é o `schemas/ProductBaseline.schema.json`.

## Primeira instância real (demonstração executada em 2026-07-27)

Brainstorm de amostra (formato Markdown de `docs/cli/idea.md`) → `pipe idea`:

```bash
PYTHONPATH=src python3 -m pipe_venture_builder idea brainstorm-amostra.md --root . --output product-baseline-amostra.json
# → "Idea ProductBaseline written. Review is required before founder focus."
```

Validação independente com `jsonschema` (Draft 2020-12) contra o schema canônico: **0 erros**.
Conteúdo: `entryMode: idea` · `status: review_required` · `lifecycle.currentStage: idea_intake` ·
13 statements classificados · 1 governanceGap · 1 nextAction. Foi a **primeira instância
schema-válida do ProductBaseline** desde a criação do schema (PIP-700).

Dependências de execução: Python ≥3.11 + `jsonschema` + `rfc3339-validator` (declaradas em
`pyproject.toml`); rodar da raiz do toolkit ou apontar `--root`.

## Divisão de trabalho no intake (dedup do ADR-VOS-006)

| Preocupação | Dono | Artefato |
|---|---|---|
| Estado canônico do venture (fatos/inferências/assunções/lacunas com proveniência, gaps de governança, plano de reconciliação) | `pipe idea` / `pipe adopt` (Python) | `ProductBaseline` (schema canônico) |
| Loop operacional da fase (transições, gate de completude, decisões humanas, retomada, eventos) | `pipe-os` (Node) | `Project` + `initial-brief` + `HumanDecisionRequest` (contratos da fatia) |

Precedência: em divergência, o **baseline canônico vence** o brief operacional (mesma regra
autoridade-canônica > operacional do repo).

## Próxima fatia (recomendada)

`pipe-os` passa a **consumir e emitir** o baseline: (1) `pipe-os create-project --from-baseline
<arquivo>` semeia o projeto a partir dos statements; (2) ao aprovar o intake, `pipe-os` atualiza
`lifecycle`/`nextActions` do baseline (supersessão por identidade estável, regra do dual-entry);
(3) o contrato `Project` da fatia vira índice operacional, não fonte de verdade. Sem mudanças no
runtime Python.
