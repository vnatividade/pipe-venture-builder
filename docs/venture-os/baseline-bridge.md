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

## Fatia 2 — ENTREGUE (PIP-726)

A ponte agora é executável nas duas direções:

1. **Consumo:** `pipe-os create-project --from-baseline <arquivo.json>` valida o baseline contra o
   schema canônico (validador Node com `$ref`/`allOf`/`oneOf`/`pattern` — paridade com `jsonschema`
   verificada em teste), semeia nome/slug de `product`, converte `statements` em fonte rotulada
   **verbatim** (`ST-problem` → problema, `ST-target-user` → público, `ST-assumption` → premissas
   com kind hipótese; `missing` vira lacuna por ausência) e guarda o baseline como
   `baseline/baseline-v1.json` do projeto.
2. **Emissão:** ao aprovar o intake, o engine emite `baseline-v2.json` — **mesma identidade estável**
   (`baselineId`), `lifecycle.currentStage → founder_focus`, `nextAllowedStage → controle_evaluation`,
   brief registrado em `artifacts[]` (`product_context`), gate e decisões humanas resolvidas em
   `approvals[]`. A emissão é validada contra o schema canônico **antes** de gravar (inválida = não
   emite, com motivo registrado) e é idempotente (re-run não gera v3).
3. `project.baseline_ref` rastreia identidade, hash de importação e versão corrente — o contrato
   `Project` virou índice operacional; a fonte de verdade é o baseline.

Round-trip coberto por 8 testes em `runtime/tests/slice2.test.mjs` (fixture: baseline real gerado
pelo `pipe idea` na fatia 1). Sem mudanças no runtime Python.
