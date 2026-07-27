# Arquitetura da fatia

Estratégia aplicada: **C — runtime fino e determinístico** (recomendação da análise, confirmada pela
spec do Venture OS: "o orquestrador decide com base no estado, os agentes executam tarefas
delimitadas"). O runtime **executa o que a política do pipe declara; nunca decide o que a política
decide**. Nenhum orquestrador LLM (proibição vigente do repo até baseline de métricas).

```txt
CLI (pipe-os) ──► Engine ──► State Machine (transições + guards)
                    │              │
                    │              ├─► Gate Engine (intake-completeness-gate, determinístico)
                    │              └─► Reviewer (advisory, vira warnings do gate)
                    ├─► Context Loader (determinístico, precedência + hashes + omissões)
                    ├─► intake-agent (normalizador determinístico; contrato p/ LLM futuro)
                    ├─► Artifact Manager (versão, hash, proveniência, supersessão)
                    ├─► Decision Queue (human-in-the-loop, idempotente)
                    └─► Store (arquivos JSON atômicos + JSONL append-only)   [interface substituível]
```

| Módulo | Arquivo | Responsabilidade |
|---|---|---|
| Engine | `runtime/lib/engine.mjs` | Orquestração por estado; retry limitado; retomada |
| State machine | `runtime/lib/state-machine.mjs` | Estados, transições, guards nomeados, registro |
| Store | `runtime/lib/store.mjs` | Persistência atômica, versão otimista, anti path-traversal |
| Events | `runtime/lib/events.mjs` | Envelope padronizado + log append-only |
| Contracts | `runtime/lib/contracts.mjs` + `runtime/schemas/` | 8 contratos versionados validados em runtime |
| Context loader | `runtime/lib/context-loader.mjs` | Contexto mínimo determinístico |
| Artifact manager | `runtime/lib/artifact-manager.mjs` | initial-brief versionado |
| Decisions | `runtime/lib/decisions.mjs` | Fila de decisões humanas |
| Agent | `runtime/agents/intake-agent.mjs` (+`.definition.json`) | Normalização sem invenção |
| Gate | `runtime/gates/intake-completeness-gate.mjs` | 9 checks determinísticos |
| Reviewer | `runtime/reviewers/intake-reviewer.mjs` | 6 heurísticas adversariais advisory |
| Workflow | `runtime/workflows/idea-to-intake.definition.json` | Definição declarativa |
| CLI | `runtime/cli/pipe-os.mjs` | Interface de execução |
| Flag | `runtime/lib/flag.mjs` | `VENTURE_OS_ENABLED`, default off |

Reuso da arquitetura existente (sem tocar nos arquivos): enum de fases e vocabulário de gates do
repo (`pass|pass_with_warnings|fail`, severidades P0–P3, categorias no estilo `/pipe:check`);
convenções de schema (`$id` local, `x-pipe-schema-version`); leis do manual codificadas (silêncio
nunca aprova; supersessão marcada; fail-safe default; stop-and-record; anti-invenção de evidência).
