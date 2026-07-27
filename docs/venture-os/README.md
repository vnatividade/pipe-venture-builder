# Venture-to-Execution OS — fatia vertical 1

Runtime determinístico mínimo que executa a Fase 0 (intake) do Venture-to-Execution OS sobre a
política existente do `pipe-venture-builder`. Implementa: projeto com estado durável, máquina de
estados, workflow `idea-to-intake`, `intake-agent`, artefato versionado, `intake-completeness-gate`,
reviewer advisory, fila de decisões humanas, retomada, eventos e logs.

**Análise-base:** `~/Developer/analises/pipe-venture-builder-venture-os/` (estratégia C — runtime
fino e determinístico; "use IA para produzir conteúdo, regras determinísticas para controlar o fluxo").

## Execução rápida

```bash
export VENTURE_OS_ENABLED=true            # feature flag (default: desabilitado)
node runtime/cli/pipe-os.mjs create-project --name "Minha Ideia" --idea "texto livre da ideia"
node runtime/cli/pipe-os.mjs run --project minha-ideia
# se o gate reprovar por lacuna de insumo:
node runtime/cli/pipe-os.mjs decisions --project minha-ideia --pending
node runtime/cli/pipe-os.mjs respond --project minha-ideia --decision <id> --option provide-info --text "..." --by <seu-nome>
node runtime/cli/pipe-os.mjs resume --project minha-ideia
```

## Como testar

```bash
node --test "runtime/tests/*.test.mjs"    # 34 testes (unitários + integração + E2E + falhas)
```

## Como inspecionar estado

```bash
node runtime/cli/pipe-os.mjs show --project <slug>          # projeto (estado, fase, next_action)
node runtime/cli/pipe-os.mjs transitions --project <slug>   # histórico da máquina de estados
node runtime/cli/pipe-os.mjs events --project <slug>        # log de eventos (envelope padronizado)
node runtime/cli/pipe-os.mjs artifacts --project <slug>     # manifesto com hash/proveniência
node runtime/cli/pipe-os.mjs gates --project <slug>         # validações de gate por artefato
```

Estado em disco: `~/.pipe/venture-os/projects/<slug>/` (configurável via `VENTURE_OS_PROJECTS_ROOT`)
— camada machine-local; **nunca** dentro deste repositório.

## Como desabilitar (rollback)

1. `unset VENTURE_OS_ENABLED` (ou não definir) — comandos mutantes recusam; nada mais roda.
2. Remoção total: apagar `runtime/` e `docs/venture-os/` — nenhum arquivo existente do manual foi
   alterado por esta fatia.

## Limitações (honestas)

- O `intake-agent` é um **normalizador determinístico** (não LLM): estrutura e classifica texto
  explícito, nunca interpreta semanticamente. O mecanismo canônico do repo (executor LLM lendo o
  contrato) é um segundo implementador previsto — ver `agents/intake-agent.md`.
- Persistência em arquivos JSON atômicos, protegida por interface — não é a solução final (ADR-VOS-001).
- Uma fase apenas (intake); `product_strategy` em diante permanece manual (por design da fatia).
- Sem integração Linear/GitHub, sem custo/tokens reais (campos existem, valores `null`).
- Sem instância de `ProductBaseline` ainda — convergência mapeada em `migration-status.md`.

## Relação com o CLI Python `pipe`

O main contém o runtime Python (`src/pipe_venture_builder`, PRs #146–#152): `pipe idea`/`pipe adopt`
geram o **ProductBaseline canônico**; este runtime Node executa o **loop** da fase. Fronteira e
contrato de integração: `adrs/ADR-VOS-006` + `baseline-bridge.md` (inclui a primeira instância real
schema-válida do ProductBaseline, gerada e validada em 2026-07-27).

## Documentos

`architecture.md` · `state-machine.md` · `first-vertical-slice.md` · `contracts.md` ·
`workflows/idea-to-intake.md` · `agents/intake-agent.md` · `gates/intake-completeness-gate.md` ·
`human-in-the-loop.md` · `operations.md` · `testing.md` · `migration-status.md` ·
`baseline-bridge.md` · `implementation-report.md` · `adrs/`
