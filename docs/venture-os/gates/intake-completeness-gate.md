# intake-completeness-gate

Implementação: `runtime/gates/intake-completeness-gate.mjs` · Saída: contrato `GateResult`
(vocabulário alinhado ao `/pipe:check`: `pass|pass_with_warnings|fail`, severidades, categorias).

## Checks (9)

| # | Check | Falha → categoria | Bloqueia? |
|---|---|---|---|
| 1 | `descricao_presente` | input_gap | sim |
| 2 | `problema_preliminar_presente` | input_gap | sim |
| 3 | `solucao_preliminar_presente` | input_gap | sim |
| 4 | `fatos_e_hipoteses_diferenciados` | structural | sim |
| 5 | `lacunas_registradas` (toda seção vazia tem lacuna) | structural | sim |
| 6 | `sem_requisitos_inventados` (todo fato rastreável à fonte, overlap ≥0.6) | unsupported_claims | sim |
| 7 | `proxima_acao_definida` | structural | sim |
| 8 | `decisoes_bloqueadoras_identificadas` (lacuna bloqueadora ⇒ decisão aberta) | structural | sim |
| 9 | `publico_mencionado` | — | **não** (warning P2) |

Achados do `intake-reviewer` entram como warnings (`reviewer:<code>`), nunca decidem o resultado.

## Saída e roteamento

`status` + `score` (checks aprovados/total) + `failures[]` + `warnings[]` + `evidence[]` (todos os
checks com resultado) + `recommended_actions[]` + `next_action`:
- sem falhas → `aprovar_intake`
- falha `input_gap`/`unsupported_claims` → `solicitar_decisao_humana` (engine agrupa em 1 pedido)
- falha estrutural → `reexecutar_agente` (retry limitado; esgotado → FAILED)

O resultado é anexado ao artefato (`validation`) e referenciado na transição — rastreável via
`gates`, `transitions` e `events` no CLI.
