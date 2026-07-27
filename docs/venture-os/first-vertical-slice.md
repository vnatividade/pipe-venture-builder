# Primeira fatia vertical — o que ela prova

Especificada em `~/Developer/analises/pipe-venture-builder-venture-os/docs/architecture/first-vertical-slice.md`;
este documento registra o que foi de fato entregue e demonstrado.

## Os 18 requisitos do fluxo, ponto a ponto

| # | Requisito | Onde está provado |
|---|---|---|
| 1 | Receber uma ideia inicial | `create-project --idea` → `sources/idea-v1.md` |
| 2 | Criar um projeto | contrato Project + `ProjectCreated` |
| 3 | Persistir o estado | `project.json` atômico com `state_version` |
| 4 | Criar uma execução | contrato Run + `RunCreated` |
| 5 | Iniciar uma fase | `START_INTAKE` + `PhaseStarted` |
| 6 | Selecionar um workflow | definição `idea-to-intake` validada por contrato |
| 7 | Selecionar um agente | `allowed_agents` do workflow + `AgentAssigned` |
| 8 | Carregar o contexto | context loader determinístico + `ContextLoaded` (hashes, omissões) |
| 9 | Executar uma etapa | steps com `StepStarted` e `current_step` na run |
| 10 | Produzir artefato versionado | `initial-brief` vN com hash, proveniência e supersessão |
| 11 | Avaliar o artefato | reviewer advisory + validação anexada ao manifesto |
| 12 | Executar um gate | `intake-completeness-gate` (9 checks) + `GatePassed/GateFailed` |
| 13 | Atualizar o estado | transições persistidas com guard/gate no histórico |
| 14 | Definir a próxima ação | `next_action` (fase, workflow, agente, dependências, advisories) |
| 15 | Decisão humana só quando necessário | apenas `input_gap`; agrupada; com recomendação e default seguro |
| 16 | Pausar apenas o fluxo afetado | `blocked_scope` + estados PAUSED/WAITING_HUMAN |
| 17 | Retomar após a resposta | `respond` → clarificação vira fonte → `resume` → brief v2 |
| 18 | Logs e rastreabilidade | eventos com correlation/causation + logs estruturados + históricos |

## Demonstração real executada (2026-07-27)

Ideia-amostra vaga ("Quero um app legal") → brief v1 → gate **fail** (score 0.89, falha única:
`problema_preliminar_presente`) → decisão bloqueadora com recomendação `provide-info` → resposta
humana com problema/solução → retomada → brief **v2** (v1 marcado superseded) → gate
**pass_with_warnings** (score 1.0, warning: público não identificado — advisory não bloqueante) →
`PRODUCT_STRATEGY_READY` com `next_action` = `product_strategy` / `founder_focus`.

## O que ficou fora (por design)

Fases além do intake; ProductBaseline (convergência em `migration-status.md`); connectors
Linear/GitHub; executor LLM; serialização DEC-XXX para canais humanos; custo/tokens reais;
busca semântica; event bus; UI.
