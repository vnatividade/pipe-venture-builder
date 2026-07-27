# Status de migração (Venture OS × pipe-venture-builder)

Plano de referência: `~/Developer/analises/pipe-venture-builder-venture-os/docs/architecture/migration-plan.md`.

| Fase do plano | Status | Nota |
|---|---|---|
| 0 — Higiene de governança | **pendente** | grants fora do git, índice do execution/README, docs pré-modes, worktrees stale, auditoria das branches pip-706..711 — decisões/PRs do fundador; esta fatia não tocou governança |
| 1 — Estado persistente | **parcial (esta fatia)** | Projeto/Run/eventos/transições duráveis e retomáveis; **sem** ProductBaseline ainda |
| 2 — Artefatos e contexto | **parcial (esta fatia)** | Artifact manifest com hash/proveniência/supersessão + context loader determinístico; frontmatter de contratos de agente do manual: pendente |
| 3 — Gates e runner /pipe:check | **iniciada** | Gate da fatia usa o vocabulário do /pipe:check; o runner do contrato completo continua pendente |
| 4 — HITL estruturado | **parcial (esta fatia)** | Fila com contrato, idempotência e retomada; serialização DEC-XXX p/ Linear/Slack pendente |
| 5 — Identidade de agentes | **iniciada** | intake-agent tem definição máquina-legível; demais contratos do manual pendentes |
| 6 — Fluxo completo + connectors | **pendente** | — |

## Convergência com o ProductBaseline — ENTREGUE na fatia 2 (PIP-726)

`--from-baseline` + emissão pós-intake implementados (ver `baseline-bridge.md` §Fatia 2). A tabela
abaixo permanece como referência do mapeamento conceitual original.

## Convergência com o ProductBaseline (mapeamento original da fatia 1)

A fatia usa o contrato `Project` (enxuto, do prompt de implementação) em vez de instanciar o
`ProductBaseline.schema.json` (1.009 linhas). Mapeamento previsto para a próxima fatia:

| Fatia (Project/brief) | ProductBaseline |
|---|---|
| `current_phase`/estados da fatia | `lifecycle.currentStage` (subestados de `idea_intake`) |
| itens do brief com kind fato/hipotese/lacuna | `statements[]` com classification fact/assumption/missing |
| manifesto de artefatos | `artifacts[]` + `relationships[]` |
| decisões abertas + pedidos humanos | `governanceGaps[]` + `approvals[]` + `nextActions[]` |
| fontes (idea/clarifications) | `sources[]` |

## Convergência com o runtime Python (RESOLVIDA — ADR-VOS-006)

Auditoria de 2026-07-27: as branches `pip-706..711` e `pip-716` **já estavam merged** no
`origin/main` (PRs #146–#152), incluindo o modo `exploration` ativado pelo fundador (PIP-716,
2026-07-21). O main contém o CLI Python `pipe` (idea/adopt → ProductBaseline, bootstrap/doctor,
connectors read-only, reconciliation planner; **170 testes verdes** verificados). Fronteira
decidida (ADR-VOS-006): Python = geração de estado canônico (ProductBaseline); Node `pipe-os` =
loop de execução (state machine, gates, HITL); contrato de integração = ProductBaseline.

Higiene pendente da fase 0 (sem mudança): checkout principal local defasado em
`codex/pip-700-local-source` com 2 mudanças não relacionadas; grants fora do git; índice do
`execution/README.md`; docs pré-operating-modes.
