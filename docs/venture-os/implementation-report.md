# Relatório de implementação — fatia vertical 1 do Venture-to-Execution OS

2026-07-27 · Autor: Claude (Fable 5), sob instrução direta do fundador na thread · Branch de trabalho:
`codex/pip-700-local-source` (checkout pré-existente; **nenhum commit foi feito** — modo `restricted`
exige aprovação humana para PR/merge; os arquivos estão no working tree como untracked, em
namespaces novos).

## Estratégia adotada

Estratégia C da análise (`~/Developer/analises/pipe-venture-builder-venture-os/`): runtime fino e
**determinístico** que executa a política existente — sem orquestrador LLM, sem tocar governança.
Compatibilidade por namespace novo (`runtime/`, `docs/venture-os/`) + feature flag fail-safe
(`VENTURE_OS_ENABLED`, default off). Zero dependências externas (Node 26 nativo + node:test).

## Componentes reutilizados (da arquitetura existente, sem alterá-la)

Vocabulário de gates do `/pipe:check` (status/severidades/categorias); enum de fases do pipeline
(`next_action.pipe_pipeline_stage: founder_focus`); convenções de schema da
`canonical-schema-policy.md` (`$id` local, `x-pipe-schema-version`, semver); leis do manual
codificadas como comportamento (silêncio nunca aprova; fail-safe default; supersessão marcada;
stop-and-record; anti-invenção de evidência; "smallest safe step"); protocolo de trial
(ideia-amostra no primeiro run real).

## Componentes criados

| Componente | Arquivos | Linhas aprox. |
|---|---|---|
| Runtime lib | `runtime/lib/` (10 módulos: engine, state-machine, store, events, contracts, minischema, context-loader, artifact-manager, decisions, ids/log/flag) | ~900 |
| Agente + gate + reviewer | `runtime/agents/`, `runtime/gates/`, `runtime/reviewers/` | ~400 |
| Workflow + schemas | `runtime/workflows/` (1), `runtime/schemas/` (8) | ~350 |
| CLI | `runtime/cli/pipe-os.mjs` | ~150 |
| Testes | `runtime/tests/` (4 arquivos, 34 testes) | ~500 |
| Docs | `docs/venture-os/` (12 docs + 5 ADRs + este relatório) | — |

**47 arquivos novos; 0 arquivos existentes alterados; 0 arquivos movidos/apagados** (verificado por
`git status`: fora dos namespaces novos restam apenas as 2 mudanças pré-existentes do Atelier, que
não são desta entrega).

## ADRs

ADR-VOS-001 (persistência em arquivos atrás de interface, não-final) · 002 (state machine
declarativa; estados = subestados de `idea_intake`) · 003 (agente determinístico por default,
contrato aberto a executor LLM) · 004 (compatibilidade por namespace + flag) · 005 (eventos como
log append-only, sem bus).

## Contratos

8 contratos versionados 0.1.0 validados em runtime: Project, Run, Workflow, AgentDefinition,
ArtifactManifestEntry, GateResult, HumanDecisionRequest, EventEnvelope (`contracts.md`).

## Testes e resultado

`node --test "runtime/tests/*.test.mjs"` → **34/34 aprovados** (unitários, integração, E2E, falhas —
detalhamento em `testing.md`). E2E real via CLI executado e documentado em
`first-vertical-slice.md`: ideia vaga → gate fail → decisão humana → resposta → brief v2 → gate
pass_with_warnings → PRODUCT_STRATEGY_READY. Um bug real foi encontrado e corrigido durante os
testes (herança indevida de rótulo de seção no segmentador do agente).

## Cobertura (qualitativa)

Todos os módulos têm testes diretos; caminhos não cobertos conhecidos: erro de I/O do filesystem em
disco cheio/permissão (tratado como exceção → retry → FAILED, mas não simulado), truncamento de
contexto com fontes gigantes além do caso testado.

## Compatibilidade e feature flag

Flag off (default): mutações recusam com mensagem; leitura com aviso; nenhum fluxo existente do
manual é afetado em qualquer caso (não há hooks em fluxos existentes). Rollback: unset da flag e/ou
remoção dos 2 diretórios. Estado de usuário fica fora do repo (`~/.pipe/venture-os/projects`).

## Limitações

Ver `README.md` §Limitações: agente determinístico (não LLM), persistência em arquivos, uma fase,
sem Linear/GitHub, sem custo/tokens reais, sem ProductBaseline ainda, decisões consultáveis só por CLI.

## Riscos restantes e dívidas técnicas

1. **[RESOLVIDO em 2026-07-27]** Duplicidade com as branches pip-706..711: auditoria revelou que já
   estavam merged no main (PRs #146–#152, runtime Python `pipe` com 170 testes verdes). Fronteira
   decidida no ADR-VOS-006 (Python = estado canônico; Node = loop de execução; contrato =
   ProductBaseline). Sobreposição de intake resolvida por precedência (baseline canônico).
2. Contrato `Project` da fatia ≠ `ProductBaseline` canônico — mapeamento de convergência documentado.
3. Classificador por regras é sensível a fraseado — falha segura (pede clarificação), mas pode
   aumentar fricção; melhora natural com o implementador LLM validado pelo mesmo gate.
4. Sem lock multi-processo (concorrência otimista apenas) — suficiente para operador único.
5. Os arquivos estão untracked no working tree — precisam de ticket/PR humano para entrar em `main`
   (gate do modo `restricted`; fora do escopo autorizado desta execução).

## Próxima fatia recomendada

**Convergência de estado:** gerar o primeiro `ProductBaseline` schema-válido a partir do
brief+manifesto+decisões da fatia (mapeamento em `migration-status.md`), decidindo antes a fusão com
as branches pip-706..711 (fase 0 do plano). Em paralelo, barato: serialização DEC-XXX das decisões
para comentário Linear/Slack.

## Decisões humanas pendentes (para o fundador)

1. ~~Auditar/fundir as branches pip-706..711~~ — **resolvido** (já merged upstream; fronteira no
   ADR-VOS-006; fusão da fatia autorizada pelo fundador em 2026-07-27).
2. ~~Aprovar PR desta fatia~~ — autorizada pelo fundador em 2026-07-27; repo em `exploration`
   (PIP-716) com review path aplicado.
3. Fase 0 de higiene de governança (grants fora do git, checkout local defasado, índice do
   execution/README, docs pré-modes) — independente desta fatia.
4. Venture piloto real para o segundo trial (o primeiro usou ideia-amostra, como manda o protocolo).
