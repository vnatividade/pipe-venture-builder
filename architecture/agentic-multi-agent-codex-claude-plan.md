# Agentic Multi-Agent Codex And Claude Code Plan

This is a living architecture plan for evolving `pipe-venture-builder` from a Codex-oriented operating repository into a tool-agnostic agentic execution system that can safely support Codex and Claude Code in parallel.

This file is not an implementation ticket and does not authorize Linear ticket creation, pull requests, production actions, customer contact, paid acquisition, billing, secrets handling, or external communications.

## 1. Decisao Arquitetural Central

Evoluir o repositorio de uma estrutura orientada principalmente a Codex para uma arquitetura agentic agnostica, com camada comum de contexto, instrucoes globais compartilhadas, adaptadores especificos para Codex e Claude Code, governanca explicita de execucao paralela, handoff padronizado e padrao de tickets Linear incrementado para futura orquestracao.

A decisao e incremental: preservar `AGENTS.md`, Linear como fonte de verdade de execucao, Git como fonte operacional, um ticket por branch/PR, approvals humanos e os contratos de agentes ja existentes. A evolucao adiciona o minimo necessario para Claude Code operar sem divergir do sistema, e prepara os tickets para serem consumidos por Codex, Claude Code e, depois, por um orquestrador.

## 2. Principios de Design

- Preservar o que ja funciona antes de adicionar estrutura nova.
- Incrementar o padrao atual do Linear, nao substituir.
- Contexto compartilhado antes de instrucao especifica por ferramenta.
- Adaptacao especifica por agente somente quando a ferramenta exigir.
- Git e a fonte operacional para branch, diff, PR, review e merge.
- Linear e a fonte de verdade para estado, prioridade, dependencias, blockers e handoff.
- Ticket e a unidade minima de trabalho.
- Um ticket deve produzir um resultado revisavel, nao uma promessa ampla.
- Handoff explicito vale mais que memoria conversacional.
- Decisoes duraveis devem ser rastreaveis em arquivos do repositorio.
- Paralelizacao exige ownership claro de arquivos, dominios e ordem de merge.
- Mudancas em arquivos compartilhados devem ser serializadas ou ter dono unico.
- Observabilidade entra no desenho de tickets tecnicos, nao apenas no fim.
- Metricas devem depender do tipo de entrega: tecnica, operacional, governanca ou produto.
- Evitar duplicacao de prompts entre `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.claude/`, skills e templates.
- Evitar acoplamento a uma unica ferramenta de agente.
- Preparar para Hermes/OpenClaw futuramente sem construir orquestracao agora.
- Nao importar bibliotecas inteiras de `product-architect-main` ou `solo-founder-superpowers-main`.
- Usar skills e especializacoes sob demanda para evitar poluir contexto.

## 3. Mudancas Necessarias

### MUD-001 - Criar camada comum de operacao multi-agent

**Problema que resolve:**
Hoje as regras comuns estao espalhadas entre `AGENTS.md`, `execution/*`, `.codex/agents/*` e skills. Claude Code precisa consumir as mesmas regras sem depender de documentos nomeados para Codex.

**Alteracao proposta:**
Criar um protocolo comum de operacao multi-agent que defina principios, fontes de verdade, fluxo por ticket, approvals, branch/PR, handoff, contexto minimo, paralelizacao e conflitos. `AGENTS.md`, futuro `CLAUDE.md`, `.codex/` e `.claude/` devem apontar para esse protocolo em vez de duplicar regras.

**Arquivos/diretorios envolvidos:**
- `execution/multi-agent-operating-protocol.md`
- `AGENTS.md`
- futuro `CLAUDE.md`
- `.codex/agents/README.md`
- futuro `.claude/README.md`

**Origem da recomendacao:**
- analise do repositorio atual
- output anterior de `product-architect-main`
- output anterior de `solo-founder-superpowers-main`
- inferencia arquitetural

**Impacto esperado:**
Alto.

**Esforco estimado:**
Medio.

**Complexidade:**
Media.

**Risco:**
Medio.

**Pode paralelizar?**
Parcialmente.

**Pre-requisitos:**
- Confirmar que `AGENTS.md` continua autoridade principal para agentes.
- Confirmar que `execution/approval-gates.md` permanece gate central.

**Dependencias:**
- Nenhuma tecnica dura.
- Deve preceder a criacao de `CLAUDE.md`.

**Risco se nao fizer:**
Codex e Claude Code podem interpretar regras diferentes, duplicar contexto, abrir branches conflitantes ou executar ticket com criterios divergentes.

**Definition of Ready:**
- Lista de documentos atuais que contem regras operacionais.
- Decisao de que o protocolo comum sera referenciado, nao copiado integralmente.

**Definition of Done:**
- Protocolo comum criado.
- `AGENTS.md` e readmes de agentes apontam para o protocolo.
- Nao ha mudanca que enfraqueca approval gates.
- Documento define como Codex e Claude Code compartilham contexto.

**Tipo de entrega:**
architecture, workflow, governance, documentation.

**Monitoramento necessario:**
- Revisar se tickets futuros citam o protocolo comum.
- Verificar em PRs se regras nao estao sendo duplicadas de forma divergente.

**Metricas de sucesso:**
- Menos campos de contexto duplicados entre instrucoes de agentes.
- Tickets executados por ferramentas diferentes seguem o mesmo handoff.
- Reducao de perguntas de clarificacao sobre workflow basico.

**Observacoes:**
Este e o primeiro ticket da baseline Codex + Claude Code.

### MUD-002 - Criar `CLAUDE.md` como adaptador, nao como nova fonte de verdade

**Problema que resolve:**
Claude Code espera convencoes proprias de entrada. Sem `CLAUDE.md`, o agente pode depender de inferencia, ler contexto demais ou ignorar parte do fluxo operacional.

**Alteracao proposta:**
Criar `CLAUDE.md` curto, acionavel e alinhado a `AGENTS.md`. Ele deve explicar como Claude Code deve operar neste repo, quais arquivos ler primeiro, como respeitar Linear/Git, como evitar conflitos com Codex e onde encontrar protocolos comuns.

**Arquivos/diretorios envolvidos:**
- `CLAUDE.md`
- `AGENTS.md`
- `execution/multi-agent-operating-protocol.md`
- `execution/ticket-pr-handoff-system.md`

**Origem da recomendacao:**
- output anterior de `solo-founder-superpowers-main`
- output anterior de `product-architect-main`
- analise do repositorio atual

**Impacto esperado:**
Alto.

**Esforco estimado:**
Baixo.

**Complexidade:**
Baixa.

**Risco:**
Medio.

**Pode paralelizar?**
Nao. Deve vir depois de MUD-001.

**Pre-requisitos:**
- MUD-001 concluida.

**Dependencias:**
- `execution/multi-agent-operating-protocol.md`.

**Risco se nao fizer:**
Claude Code pode operar com memoria local, convencoes genericas ou divergentes do fluxo Linear/Git existente.

**Definition of Ready:**
- Protocolo comum aprovado.
- Lista de comandos e restricoes especificas para Claude Code definida.

**Definition of Done:**
- `CLAUDE.md` existe.
- O arquivo e curto e aponta para documentos canonicos.
- Nao duplica integralmente `AGENTS.md`.
- Explicita que `AGENTS.md` e a politica do repo e que Linear/Git seguem os protocolos atuais.

**Tipo de entrega:**
documentation, prompt, governance.

**Monitoramento necessario:**
- Checar nos primeiros tickets executados por Claude Code se o agente segue branch, PR, review e handoff.

**Metricas de sucesso:**
- Claude Code consegue executar um ticket piloto sem perguntar pelo fluxo basico.
- Zero divergencias entre `CLAUDE.md` e `AGENTS.md` em approval gates.

### MUD-003 - Padronizar contexto e roteamento de leitura por tipo de tarefa

**Problema que resolve:**
O repo ja tem agentes, skills e muitos artefatos. Sem roteamento claro, agentes podem carregar contexto demais ou contexto errado.

**Alteracao proposta:**
Criar um context router comum para Codex e Claude Code com mapas por tipo de tarefa: architecture, documentation, prompt, skill, workflow, governance, code, infrastructure, automation, observability, product e orchestration-prep.

**Arquivos/diretorios envolvidos:**
- `execution/context-routing-protocol.md`
- `.codex/agents/agent-skill-trigger-rules.md`
- futuro `.claude/context-routing.md`
- `.agents/skills/core-skill-contracts.md`

**Origem da recomendacao:**
- output anterior de `product-architect-main`, especialmente SMART-LOADER/context routing
- analise do repositorio atual

**Impacto esperado:**
Alto.

**Esforco estimado:**
Medio.

**Complexidade:**
Media.

**Risco:**
Baixo.

**Pode paralelizar?**
Parcialmente.

**Pre-requisitos:**
- MUD-001 concluida ou em PR.

**Dependencias:**
- Contratos atuais em `.codex/agents/*`.
- Skills atuais em `.agents/skills/*`.

**Risco se nao fizer:**
Execucoes ficam lentas, inconsistentes e sujeitas a decisoes baseadas em documentos irrelevantes ou memoria de conversa.

**Definition of Ready:**
- Lista de tipos de ticket consolidada.
- Mapa de arquivos read-first por tipo definido.

**Definition of Done:**
- Protocolo define read-first minimo por tipo de tarefa.
- Protocolo define quando usar skills.
- Codex e Claude Code possuem referencia ao mesmo mapa.
- Nao duplica conteudo de cada documento, apenas aponta.

**Tipo de entrega:**
workflow, governance, documentation, prompt.

**Monitoramento necessario:**
- Em PRs, verificar se o agente citou ou usou os arquivos certos para o tipo de ticket.

**Metricas de sucesso:**
- Menos leitura desnecessaria em tickets simples.
- Menos alteracoes fora de escopo.
- Handoffs citam fontes corretas.

### MUD-004 - Criar protocolo de ownership e conflito para execucao paralela

**Problema que resolve:**
Codex e Claude Code em paralelo aumentam throughput, mas tambem aumentam risco de conflito em arquivos centrais como `AGENTS.md`, `execution/*`, `.codex/agents/*`, `growth/README.md` e templates compartilhados.

**Alteracao proposta:**
Criar regras explicitas para paralelizacao: ownership por ticket, write set declarado, arquivos bloqueados/compartilhados, ordem de merge, rebase/sync, conflitos de dominio, mudancas em templates globais e refactors.

**Arquivos/diretorios envolvidos:**
- `execution/parallel-execution-governance.md`
- `execution/ticket-pr-handoff-system.md`
- `execution/linear-governance-model.md`

**Origem da recomendacao:**
- analise do repositorio atual
- output anterior de `product-architect-main`
- inferencia arquitetural

**Impacto esperado:**
Alto.

**Esforco estimado:**
Medio.

**Complexidade:**
Media.

**Risco:**
Medio.

**Pode paralelizar?**
Nao para o protocolo em si. Depois de pronto, ele desbloqueia paralelizacao.

**Pre-requisitos:**
- MUD-001.
- Definir labels ou campos de paralelizacao no Linear.

**Dependencias:**
- `execution/ticket-pr-handoff-system.md`.
- `execution/linear-governance-model.md`.

**Risco se nao fizer:**
Dois agentes podem editar o mesmo artefato de governanca, criar PRs incompatíveis ou gerar tickets que parecem independentes mas brigam pelo mesmo dominio.

**Definition of Ready:**
- Lista inicial de arquivos compartilhados de alto risco.
- Definicao de como declarar write set no ticket.

**Definition of Done:**
- Protocolo define quando um ticket e paralelizavel.
- Protocolo define quando nao e.
- Protocolo define como declarar ownership e write set.
- Protocolo define como lidar com conflitos e refactors.
- Linear template incrementado referencia esses campos.

**Tipo de entrega:**
governance, workflow, documentation.

**Monitoramento necessario:**
- Acompanhar conflitos de merge, retrabalho por branch e PRs que tocam arquivos compartilhados.

**Metricas de sucesso:**
- Numero de PRs com conflito de merge.
- Numero de tickets bloqueados por ownership ambigua.
- Numero de PRs com mudanca fora do write set declarado.

### MUD-005 - Incrementar padrao de tickets Linear para execucao multi-agent

**Problema que resolve:**
O padrao atual e bom para execucao sequencial. Para Codex, Claude Code e futuro orquestrador, os tickets precisam declarar readiness, DoD, validacao, paralelizacao, metricas e dependencias tecnicas/operacionais de forma mais estruturada.

**Alteracao proposta:**
Atualizar o modelo de ticket em `execution/linear-governance-model.md`, `execution/ticket-orchestrator-workflow.md` e `execution/ticket-pr-handoff-system.md` preservando campos atuais e adicionando campos obrigatorios/condicionais.

**Arquivos/diretorios envolvidos:**
- `execution/linear-governance-model.md`
- `execution/ticket-orchestrator-workflow.md`
- `execution/ticket-pr-handoff-system.md`
- possivel `execution/linear-ticket-template-v2.md`

**Origem da recomendacao:**
- analise do repositorio atual
- inferencia arquitetural
- output anterior de `product-architect-main`

**Impacto esperado:**
Alto.

**Esforco estimado:**
Medio.

**Complexidade:**
Media.

**Risco:**
Medio.

**Pode paralelizar?**
Parcialmente.

**Pre-requisitos:**
- MUD-004 para campos de paralelizacao.

**Dependencias:**
- Padrão atual do Linear preservado.

**Risco se nao fizer:**
Tickets continuam bons para humanos, mas fracos para distribuicao entre agentes, avaliacao de readiness e futura orquestracao.

**Definition of Ready:**
- Lista de campos atuais preservados.
- Lista de campos novos obrigatorios e condicionais aprovada.

**Definition of Done:**
- Template incrementado existe.
- Campos por tipo de ticket definidos.
- Delivery update inclui monitoramento, metricas e next action.
- Nenhum campo atual relevante foi removido.

**Tipo de entrega:**
governance, workflow, documentation, orchestration-prep.

**Monitoramento necessario:**
- Verificar tickets criados apos a mudanca para aderencia ao template.

**Metricas de sucesso:**
- Percentual de tickets novos com DoR, DoD, validation plan e parallelization notes.
- Reducao de tickets que precisam de retrabalho antes de branch.

### MUD-006 - Criar matriz de tipos de ticket e campos obrigatorios

**Problema que resolve:**
Nem todo ticket precisa dos mesmos campos. Forcar tudo em todos cria ruido; omitir campos importantes cria risco.

**Alteracao proposta:**
Criar uma matriz pragmatica por tipo de entrega: architecture, documentation, prompt, skill, workflow, governance, code, infrastructure, automation, observability, product, orchestration-prep.

**Arquivos/diretorios envolvidos:**
- `execution/ticket-type-field-matrix.md`
- `execution/ticket-orchestrator-workflow.md`

**Origem da recomendacao:**
- pedido atual do usuario
- inferencia arquitetural

**Impacto esperado:**
Alto.

**Esforco estimado:**
Baixo.

**Complexidade:**
Baixa.

**Risco:**
Baixo.

**Pode paralelizar?**
Sim, se MUD-005 ja definiu o template base.

**Pre-requisitos:**
- Acordo sobre tipos de entrega.

**Dependencias:**
- MUD-005.

**Risco se nao fizer:**
O template de tickets vira pesado demais ou permissivo demais.

**Definition of Ready:**
- Lista final de tipos aprovada.

**Definition of Done:**
- Matriz define campos obrigatorios por tipo.
- Matriz define campos condicionais.
- Matriz inclui metricas e monitoramento por tipo.

**Tipo de entrega:**
governance, documentation, workflow.

**Monitoramento necessario:**
- Revisar amostra de tickets novos por tipo.

**Metricas de sucesso:**
- Menos campos vazios em tickets.
- Mais tickets prontos para execucao sem clarificacao.

### MUD-007 - Padronizar handoff cross-agent e logs de progresso

**Problema que resolve:**
Codex e Claude Code precisam deixar rastros equivalentes. O handoff atual cobre PR/Linear, mas ainda pode ser mais explicito sobre agente executor, agente revisor, ownership, write set, metricas e progresso.

**Alteracao proposta:**
Incrementar o handoff para registrar executor, ferramenta, ticket type, write set, arquivos tocados, validacoes, monitoramento, metricas, follow-ups, riscos residuais e proximo agente sugerido.

**Arquivos/diretorios envolvidos:**
- `execution/ticket-pr-handoff-system.md`
- `.codex/agents/agent-handoff-protocol.md`
- futuro `.claude/handoff-protocol.md` ou referencia ao protocolo comum

**Origem da recomendacao:**
- analise do repositorio atual
- output anterior de `product-architect-main`

**Impacto esperado:**
Medio.

**Esforco estimado:**
Baixo.

**Complexidade:**
Baixa.

**Risco:**
Baixo.

**Pode paralelizar?**
Sim, apos MUD-001.

**Pre-requisitos:**
- Protocolo comum.

**Dependencias:**
- MUD-005.

**Risco se nao fizer:**
Futuros agentes nao conseguem entender o que foi feito sem reler PRs, conversas ou diffs extensos.

**Definition of Ready:**
- Template atual de delivery update revisado.

**Definition of Done:**
- Handoff inclui campos multi-agent.
- Handoff e compativel com comentarios finais no Linear.
- Handoff nao exige dados privados ou sensiveis.

**Tipo de entrega:**
workflow, governance, documentation.

**Monitoramento necessario:**
- Conferir se tickets Done possuem handoff suficiente para retomada por outro agente.

**Metricas de sucesso:**
- Menos reabertura de contexto em tickets seguintes.
- Menos perguntas sobre o que uma PR entregou.

### MUD-008 - Padronizar skills e prompts compartilhados

**Problema que resolve:**
O repo tem `.agents/skills` e `.codex/agents`, mas Claude Code pode precisar de instrucoes em formato proprio. Sem padrao, prompts podem duplicar ou divergir.

**Alteracao proposta:**
Definir uma convencao para skills e prompts agnosticos: quando algo vira skill, quando vira prompt, quando fica em workflow, como Codex e Claude Code consomem, e como evitar duplicacao.

**Arquivos/diretorios envolvidos:**
- `.agents/skills/core-skill-contracts.md`
- `.agents/skills/README.md`
- possivel `prompts/README.md`
- possivel `.claude/skills/README.md` apenas se necessario

**Origem da recomendacao:**
- output anterior de `solo-founder-superpowers-main`
- output anterior de `product-architect-main`
- analise do repositorio atual

**Impacto esperado:**
Medio.

**Esforco estimado:**
Medio.

**Complexidade:**
Media.

**Risco:**
Medio.

**Pode paralelizar?**
Parcialmente.

**Pre-requisitos:**
- MUD-003.

**Dependencias:**
- Skills atuais.

**Risco se nao fizer:**
O repo pode acumular skills, prompts e agentes redundantes, reduzindo confianca e aumentando custo de contexto.

**Definition of Ready:**
- Inventario curto de skills/prompts atuais.
- Decisao sobre diretorio compartilhado vs especifico.

**Definition of Done:**
- Convencao documentada.
- Skills continuam sob demanda.
- Prompts especificos por ferramenta so existem quando ha diferenca real.

**Tipo de entrega:**
skill, prompt, governance, documentation.

**Monitoramento necessario:**
- Checar duplicacao de prompts e instrucoes em PRs futuros.

**Metricas de sucesso:**
- Reducao de prompts duplicados.
- Aderencia de novas skills ao contrato comum.

### MUD-009 - Criar readiness validator para tickets multi-agent

**Problema que resolve:**
Antes de Codex ou Claude Code iniciarem um ticket, alguem precisa saber se o ticket esta realmente pronto: dependencias, approvals, write set, DoR, validacao e riscos.

**Alteracao proposta:**
Incrementar `execution/agent-readiness-validator.md` ou criar um checklist especifico para tickets multi-agent, com resultado `READY`, `NOT READY`, `READY WITH APPROVAL`, `BLOCKED`.

**Arquivos/diretorios envolvidos:**
- `execution/agent-readiness-validator.md`
- `execution/ticket-type-field-matrix.md`
- `execution/parallel-execution-governance.md`

**Origem da recomendacao:**
- analise do repositorio atual
- output anterior de `product-architect-main`

**Impacto esperado:**
Alto.

**Esforco estimado:**
Medio.

**Complexidade:**
Media.

**Risco:**
Baixo.

**Pode paralelizar?**
Sim, apos MUD-005 e MUD-006.

**Pre-requisitos:**
- Template incrementado.
- Matriz por tipo.

**Dependencias:**
- MUD-005.
- MUD-006.

**Risco se nao fizer:**
Agentes podem iniciar tickets incompletos e descobrir blockers tarde, gerando PRs parciais ou escopo improvisado.

**Definition of Ready:**
- Campos de ticket v2 aprovados.

**Definition of Done:**
- Validator cobre campos comuns e condicionais.
- Validator cobre paralelizacao.
- Validator cobre approvals e riscos.
- Validator produz decisao e motivos.

**Tipo de entrega:**
workflow, governance, observability.

**Monitoramento necessario:**
- Registrar quantos tickets entram como NOT READY e por qual motivo.

**Metricas de sucesso:**
- Reducao de tickets iniciados com dependencias faltantes.
- Percentual de tickets com readiness registrado antes de branch.

### MUD-010 - Criar observabilidade da operacao agentic

**Problema que resolve:**
Hoje a observabilidade fica no handoff, mas nao ha um modelo consolidado para medir saude da operacao agentic: throughput, retrabalho, conflitos, tempo em review, falhas de validacao e qualidade de tickets.

**Alteracao proposta:**
Criar um modelo leve de metricas operacionais para execucao agentic, sem automacao pesada inicial. O modelo deve definir metricas, onde registrar, cadencia de revisao e sinais de rollback/mitigacao.

**Arquivos/diretorios envolvidos:**
- `execution/agentic-operations-metrics.md`
- `execution/ticket-pr-handoff-system.md`
- `knowledge/knowledge-curator-workflow.md`

**Origem da recomendacao:**
- pedido atual do usuario
- inferencia arquitetural
- output anterior de `product-architect-main`

**Impacto esperado:**
Medio.

**Esforco estimado:**
Medio.

**Complexidade:**
Media.

**Risco:**
Baixo.

**Pode paralelizar?**
Sim, apos MUD-005.

**Pre-requisitos:**
- Handoff incrementado.

**Dependencias:**
- MUD-007.

**Risco se nao fizer:**
Nao sera claro se Codex + Claude Code estao aumentando throughput ou apenas criando mais retrabalho.

**Definition of Ready:**
- Definir se o registro inicial fica em Linear comments, arquivo de knowledge ou ambos.

**Definition of Done:**
- Documento define metricas operacionais.
- Documento define sinais de alerta.
- Documento define cadencia de revisao.
- Handoff final inclui campos minimos para metricas.

**Tipo de entrega:**
observability, governance, workflow.

**Monitoramento necessario:**
- Throughput por agente/ferramenta.
- PRs com conflito.
- P0/P1 por ticket type.
- Tempo em review.
- Tickets reabertos por falta de DoR.

**Metricas de sucesso:**
- Baseline de operacao agentic estabelecida.
- Identificacao de gargalos antes de adicionar orquestrador.

### MUD-011 - Criar piloto controlado Claude Code

**Problema que resolve:**
Mesmo com instrucoes boas, a unica prova real e Claude Code executar um ticket pequeno sem quebrar o fluxo.

**Alteracao proposta:**
Criar um ticket piloto para Claude Code executar uma mudanca documental ou de workflow de baixo risco, usando `CLAUDE.md`, o protocolo comum e o template Linear incrementado.

**Arquivos/diretorios envolvidos:**
- A definir pelo ticket piloto.
- `CLAUDE.md`
- `execution/multi-agent-operating-protocol.md`
- `execution/agentic-operations-metrics.md`

**Origem da recomendacao:**
- inferencia arquitetural
- analise do repositorio atual

**Impacto esperado:**
Alto.

**Esforco estimado:**
Baixo.

**Complexidade:**
Baixa.

**Risco:**
Baixo.

**Pode paralelizar?**
Nao. Deve acontecer apos baseline minima.

**Pre-requisitos:**
- MUD-001.
- MUD-002.
- MUD-004.
- MUD-005.

**Dependencias:**
- Baseline Claude Code ready.

**Risco se nao fizer:**
A arquitetura sera teorica; problemas de instrucao, branch, handoff e review so aparecerao tarde.

**Definition of Ready:**
- Ticket piloto pequeno e aprovado.
- Claude Code tem instrucoes e contexto.

**Definition of Done:**
- Claude Code executa um ticket de baixo risco.
- Branch, PR, review, merge e Linear handoff seguem o padrao.
- Aprendizados viram ajuste ou follow-up.

**Tipo de entrega:**
workflow, governance, documentation.

**Monitoramento necessario:**
- Tempo de execucao.
- Perguntas ou blockers.
- Aderencia ao protocolo.
- Conflitos com Codex.

**Metricas de sucesso:**
- Primeiro ticket Claude Code concluido sem desvio de approval gate.
- Handoff suficiente para Codex entender a entrega.

### MUD-012 - Preparar analise futura de orquestracao Hermes/OpenClaw

**Problema que resolve:**
A orquestracao futura precisa ser lembrada, mas nao deve contaminar a baseline atual com desenho prematuro.

**Alteracao proposta:**
Criar backlog item futuro para analisar readiness do repo para Hermes/OpenClaw somente depois que Codex + Claude Code estiverem operando bem.

**Arquivos/diretorios envolvidos:**
- Este arquivo como fonte inicial.
- Futuro `architecture/orchestration-readiness-analysis.md`.
- `execution/parallel-execution-governance.md`.
- `execution/agentic-operations-metrics.md`.

**Origem da recomendacao:**
- pedido atual do usuario
- inferencia arquitetural

**Impacto esperado:**
Medio futuro.

**Esforco estimado:**
Medio.

**Complexidade:**
Alta futura.

**Risco:**
Baixo agora, alto se antecipar.

**Pode paralelizar?**
Nao agora.

**Pre-requisitos:**
- Baseline Codex + Claude Code implementada.
- Pelo menos um ticket piloto executado por Claude Code.
- Metricas operacionais iniciais registradas.

**Dependencias:**
- MUD-001 a MUD-011.

**Risco se nao fazer:**
A decisao sobre orquestrador pode ser esquecida ou retomada de forma generica, sem observar a estrutura real implementada.

**Definition of Ready:**
- Codex e Claude Code ja operaram no repo com handoffs comparaveis.
- Existem exemplos de tickets paralelizaveis e nao paralelizaveis.
- Existem dados basicos de operacao agentic.

**Definition of Done:**
- Analise compara Hermes/OpenClaw contra a estrutura real do repo.
- Analise define como orquestrador le tickets, distribui tarefas, respeita ownership, aciona agentes, valida execucao, registra progresso, trata conflitos e cria follow-ups.
- Resultado e um plano de adaptacao futuro, nao implementacao imediata.

**Tipo de entrega:**
orchestration-prep, architecture, governance.

**Monitoramento necessario:**
- Nao aplicavel antes da rodada futura.

**Metricas de sucesso:**
- Backlog futuro existe.
- Dependencias impedem execucao prematura.
- Analise futura usa evidencias reais da baseline Codex + Claude Code.

**Observacoes:**
Titulo sugerido do ticket futuro: `[Orchestration] Analyze repository readiness for Hermes/OpenClaw orchestration after Codex and Claude Code baseline`.

## 4. Estrutura Recomendada de Diretorios e Arquivos

Adicionar apenas o que reduz ambiguidade real.

| Caminho | Finalidade | Consumidor principal | Comum ou especifico | Prioridade | Relacao com tickets futuros |
|---|---|---|---|---|---|
| `architecture/agentic-multi-agent-codex-claude-plan.md` | Fonte canonica deste plano e backlog ticket-ready. | Humanos, Codex, Claude Code, futuro orquestrador. | Comum | P0 | Fonte para criacao futura de tickets. |
| `execution/multi-agent-operating-protocol.md` | Regras comuns de operacao Codex + Claude Code. | Codex, Claude Code. | Comum | P0 | MUD-001. |
| `CLAUDE.md` | Adaptador curto para Claude Code ler o repo com seguranca. | Claude Code. | Especifico Claude | P0 | MUD-002. |
| `.claude/README.md` | Indice opcional para artefatos especificos do Claude, se houver necessidade real. | Claude Code. | Especifico Claude | P1 | Criar apenas se `CLAUDE.md` ficar insuficiente. |
| `execution/context-routing-protocol.md` | Mapa de leitura por tipo de ticket e tarefa. | Codex, Claude Code, ticket_orchestrator. | Comum | P0 | MUD-003. |
| `execution/parallel-execution-governance.md` | Ownership, write set, conflitos, serializacao de arquivos compartilhados. | Codex, Claude Code, futuro orquestrador. | Comum | P0 | MUD-004. |
| `execution/linear-ticket-template-v2.md` | Template incrementado sem quebrar o padrao atual do Linear. | ticket_orchestrator, Linear steward. | Comum | P0 | MUD-005. |
| `execution/ticket-type-field-matrix.md` | Campos obrigatorios/condicionais por tipo de entrega. | ticket_orchestrator, agentes executores. | Comum | P0 | MUD-006. |
| `execution/agentic-operations-metrics.md` | Metricas de throughput, retrabalho, conflito, qualidade de tickets e handoff. | Humanos, knowledge_curator, futuro orquestrador. | Comum | P1 | MUD-010. |
| `.codex/agents/*` | Contratos e especializacoes ja existentes para Codex. | Codex. | Especifico Codex, mas referenciavel. | Ja existe | Atualizar apenas quando necessario. |
| `.agents/skills/*` | Skills agnosticas e contratos de skill sob demanda. | Codex, Claude Code, futuro orquestrador. | Comum | Ja existe | MUD-008 pode melhorar convencao. |
| `knowledge/` | Decisoes, aprendizados, conflitos e memoria operacional. | Todos agentes. | Comum | Ja existe | Deve receber aprendizados da baseline. |
| `architecture/adr/` | Decisoes tecnicas e arquiteturais duraveis. | Software architect, risk reviewer. | Comum | Ja existe | Usar para mudancas tecnicas relevantes. |

Nao criar agora:

- `prompts/`, salvo se MUD-008 provar que prompts compartilhados precisam de diretorio proprio.
- `mcp/`, salvo quando uma rodada aprovada de MCP sair do estado de design.
- `scripts/`, salvo se houver validadores automatizados reais.
- `docs/architecture/`, porque o repositorio ja usa `architecture/`.

## 5. Camada Comum vs Camada Especifica por Agente

### Camada comum

Compartilhado por Codex e Claude Code:

- `AGENTS.md` como politica do repo.
- `execution/approval-gates.md`.
- `execution/linear-governance-model.md`.
- `execution/ticket-pr-handoff-system.md`.
- `execution/multi-agent-operating-protocol.md` futuro.
- `execution/context-routing-protocol.md` futuro.
- `execution/parallel-execution-governance.md` futuro.
- `execution/linear-ticket-template-v2.md` futuro.
- `execution/ticket-type-field-matrix.md` futuro.
- `knowledge/*` para decisoes e aprendizados.
- `architecture/*` para decisoes tecnicas.
- `.agents/skills/*` quando a skill for agnostica.
- Templates de DoR, DoD, validation plan, handoff, branch, PR e Linear.
- Padrões de metricas por tipo de entrega.

### Camada especifica do Codex

Deve existir apenas para Codex:

- `.codex/agents/*` quando houver comportamento de roteamento especifico do Codex.
- `.codex/workflows/*` se o workflow depender da forma como Codex executa tarefas.
- `.codex/templates/*` se forem templates especificos de Codex.
- Instrucoes sobre uso de sub-agentes Codex, review via Codex e capacidades locais do Codex app.

Regra: a camada Codex nao deve redefinir approval gates nem o padrao Linear. Ela adapta execucao.

### Camada especifica do Claude Code

Deve existir apenas para Claude Code:

- `CLAUDE.md` como entrada curta e operacional.
- `.claude/README.md` somente se for util para organizar artefatos especificos.
- Instrucoes sobre como Claude Code deve carregar contexto, registrar handoff, evitar conflitos com Codex e respeitar o protocolo comum.
- Eventuais comandos ou hooks especificos de Claude, se aprovados depois.

Regra: Claude Code deve consumir a camada comum e nao criar um segundo sistema operacional.

### Camada futura de orquestracao

Preparar, mas nao implementar agora:

- Tickets com campos legiveis por orquestrador: dependencies, prerequisites, parallelizable, owner, write set, validation plan, DoR, DoD, monitoring, metrics.
- Handoff estruturado o suficiente para roteamento futuro.
- Metricas operacionais para avaliar se a orquestracao vale a pena.
- Backlog item futuro para Hermes/OpenClaw.

Nao criar agora:

- scheduler automatico.
- dispatch automatico entre Codex/Claude.
- agente master.
- resolucao automatica de conflitos.
- criacao automatica de follow-ups sem approval.

## 6. Governanca de Execucao Paralela

Unidade minima de trabalho:

- Um ticket Linear aprovado.
- Um branch por ticket.
- Uma PR por ticket.
- Um dono executor primario por ticket.
- Um write set declarado antes de iniciar.

Padrao de branch:

- Codex: `codex/<ticket>-short-description`.
- Claude Code: `claude/<ticket>-short-description`.
- Outros: `feature/`, `fix/`, `chore/` apenas quando fizer mais sentido e estiver no ticket.

Ownership:

- O ticket deve declarar `Suggested Owner/Agent`.
- O ticket deve declarar `Executor Tool`, quando ja se souber: Codex, Claude Code, human, future orchestrator.
- O ticket deve declarar arquivos provaveis e arquivos proibidos.
- Se mais de um agente precisar editar o mesmo arquivo, dividir o ticket ou serializar.

Quando pode paralelizar:

- Tickets com write sets disjuntos.
- Tickets em dominios diferentes.
- Tickets documentais sem arquivo compartilhado.
- Tickets em que um depende apenas do merge de outro e pode ser preparado sem editar os mesmos arquivos.
- Tickets que nao mexem em `AGENTS.md`, `execution/approval-gates.md`, template Linear ou contrato global.

Quando nao pode paralelizar:

- Mudancas em approval gates.
- Mudancas em `AGENTS.md`, `CLAUDE.md`, `execution/multi-agent-operating-protocol.md` ou template Linear global.
- Refactors amplos.
- Mudancas em arquitetura compartilhada.
- Tickets com dependencia sequencial de decisao.
- Tickets que alteram os mesmos arquivos ou familias de templates.
- Tarefas high-risk envolvendo dados, billing, deploy, claims, security ou external communication.

Como declarar dependencias:

- `Prerequisites`: o que precisa existir antes de iniciar.
- `Technical Dependencies`: arquivos, APIs, scripts, libs, schemas ou infraestrutura.
- `Operational Dependencies`: approvals, Linear status, review, decision records, human decision.
- `Blocks / Blocked By`: relacionamento Linear.
- `Unblock condition`: evidencia objetiva do desbloqueio.

Como declarar bloqueios:

- Registrar no Linear com motivo, arquivo/decisao afetado e proximo passo.
- Nao improvisar escopo.
- Se o blocker for fora do escopo, propor follow-up.

Como registrar handoff:

- Linear comment final.
- PR description atualizada.
- Links de branch, PR, merge commit.
- Validacoes.
- Review findings.
- Monitoramento e metricas, se aplicavel.
- Risco residual.
- Proximo ticket recomendado.

Como registrar decisao:

- Decisao operacional curta no ticket quando local ao ticket.
- KDR/DAR ou ADR quando a decisao afetar futuros agentes, arquitetura, estrategia, governance ou templates.

Como evitar conflito de arquivo:

- Declarar write set.
- Evitar mexer em README indices fora do escopo quando outro ticket tambem mexe.
- Para arquivos compartilhados, criar ticket sequencial ou dono unico.
- Rebase/sync antes de abrir PR e antes de corrigir review.

Como evitar conflito de dominio:

- Um agente por dominio principal: product, validation, growth, execution, architecture, knowledge.
- Se o ticket atravessa dominios, dividir ou declarar reviewer de apoio.

Como lidar com mudancas em arquivos compartilhados:

- `AGENTS.md`, `execution/approval-gates.md`, `execution/linear-governance-model.md`, `execution/ticket-pr-handoff-system.md`, `.codex/agents/core-agent-contracts.md` e futuro `CLAUDE.md` exigem serializacao.
- PRs que tocam esses arquivos devem ter review mais rigorosa.

Como lidar com refactors:

- Refactor amplo precisa de ticket proprio.
- Refactor nao deve entrar como "limpeza" dentro de ticket de feature/documentacao.
- Refactor em arquivo compartilhado nao deve rodar em paralelo.

Como lidar com tarefas de alto risco:

- Exigir approval explicito.
- Exigir risk review.
- Nao usar manual review fallback se branch protection ou risco exigir revisor especifico.
- Nao mergear com P0/P1 aberto.

## 7. Incremento do Padrao Atual do Linear

### Campos atuais que devem ser preservados

- Objective.
- Why This Matters.
- Source Rationale.
- C.O.N.T.R.O.L.E. Dimensions Supported.
- Included Scope.
- Excluded Scope.
- Deliverables.
- Acceptance Criteria.
- GO Conditions.
- NO-GO Conditions.
- Dependencies.
- Approval Requirement.
- Suggested Owner/Agent.
- Risk Level.
- Notes for Implementation.

### Campos novos obrigatorios

Obrigatorios para todo ticket novo:

- Type.
- Effort.
- Complexity.
- Parallelizable.
- Parallelization Notes.
- Prerequisites.
- Definition of Ready.
- Definition of Done.
- Validation Plan.
- Success Metrics.
- Agent Execution Notes.
- Follow-up Ticket Criteria.

Obrigatorios quando houver execucao por ferramenta definida:

- Executor Tool: Codex / Claude Code / Human / Future Orchestrator.
- Expected Write Set.
- Restricted Files.

### Campos novos condicionais

Para tickets tecnicos/codigo:

- Technical Dependencies.
- Operational Dependencies.
- Observability Requirements.
- Monitoring Requirements.
- Rollback/Mitigation.
- Files Likely To Change.
- Runtime Risk.
- Healthcheck, logs, traces, metrics, audit signals quando aplicavel.

Para tickets de produto/valor:

- KPI Impact.
- Primary KPI.
- Secondary KPI.
- Conversion Event.
- Adoption Metric.
- Retention Metric, se aplicavel.
- Baseline, se existir.
- Post-release Follow-up.

Para governanca/documentacao/prompt/skill/workflow:

- Ambiguity Resolved.
- Protocol Affected.
- Agent Consumers.
- Adherence Criteria.
- Manual Validation.
- Risk Of Divergence If Not Done.

Para orchestration-prep:

- Future Trigger.
- Baseline Dependency.
- Orchestrator Questions.
- Required Evidence Before Execution.
- Explicit Not Now Boundary.

### Labels recomendadas

Manter:

- `priority:P0`, `priority:P1`, `priority:P2`, `priority:P3`.
- `risk:low`, `risk:medium`, `risk:high`.
- `type:*`.
- `horizon:*`.
- `source:*`.
- `approval:required`, `approval:granted`, `approval:blocker`.

Adicionar com parcimonia:

- `agent:codex`.
- `agent:claude`.
- `agent:orchestrator-future`.
- `parallelizable:yes`.
- `parallelizable:no`.
- `parallelizable:partial`.
- `complexity:low`, `complexity:medium`, `complexity:high`.
- `effort:low`, `effort:medium`, `effort:high`.

Evitar:

- Labels para cada arquivo.
- Labels para cada subagente quando o `Suggested Owner/Agent` ja resolve.
- Labels que duplicam texto do ticket sem ajudar filtro ou orquestracao.

### Comentario de delivery update

Template preservando o padrao atual e incrementando:

```md
## Ticket executado

- Linear:
- Executor tool:
- Branch:
- PR:
- Merge: Sim/Nao
- Merge commit:

## Entrega

- Resumo:
- Included scope entregue:
- Excluded scope preservado:
- Arquivos alterados:

## Review

- Review solicitada: Sim/Nao
- Review utilizada: Codex / Copilot / Manual fallback / Humana externa
- P0 encontrados:
- P1 encontrados:
- P2 encontrados:
- P3 encontrados:
- Corrigidos neste PR:
- Nao corrigidos:

## Validacoes

- Comando/check:
- Resultado:
- Validacoes nao executadas:
- Motivo:

## Monitoramento e metricas

- Monitoring requirements aplicaveis:
- Success metrics avaliadas:
- Baseline:
- Resultado observado ou pendente:
- Proximo checkpoint:

## Follow-ups criados

- Ticket:
- Motivo:

## Risco residual

- Risco:
- Mitigacao:
- Rollback/mitigation signal:

## Proxima acao recomendada

- Ticket:
- Motivo:
```

## 8. Harness de Tickets para Linear

Formato de titulo recomendado:

- Manter o padrao atual com codigo quando existir: `PVB-H2-HARDEN-XX - Nome do ticket`.
- Para backlog novo sem codigo ainda: `[Area] Verbo + objeto + resultado esperado`.

Modelo incrementado:

```md
# Title

## Objective

## Why This Matters

## Source Rationale

## C.O.N.T.R.O.L.E. Dimensions Supported

## Type
- architecture / documentation / prompt / skill / workflow / governance / code / infrastructure / automation / observability / product / orchestration-prep

## Included Scope

## Excluded Scope

## Deliverables

## Acceptance Criteria

## GO Conditions

## NO-GO Conditions

## Dependencies

## Prerequisites

## Technical Dependencies

## Operational Dependencies

## Approval Requirement

## Human Decision Required

## Suggested Owner/Agent

## Executor Tool
- Codex / Claude Code / Human / Future Orchestrator / Unassigned

## Risk Level

## Effort
- Low / Medium / High

## Complexity
- Low / Medium / High

## Parallelizable
- Yes / No / Partial

## Parallelization Notes

## Expected Write Set

## Restricted Files

## Definition of Ready

## Definition of Done

## Validation Plan

## Monitoring Requirements

## Observability Requirements

## Success Metrics

## KPI Impact

## Rollback or Mitigation

## Notes for Implementation

## Follow-up Ticket Criteria

## Agent Execution Notes
```

Regras por tipo:

### Tickets tecnicos/codigo

Success Metrics deve incluir quando aplicavel:

- logs necessarios
- eventos necessarios
- traces necessarios
- metricas operacionais
- erro esperado
- latencia
- healthcheck
- auditoria
- rollback signal

Obrigatorios:

- Definition of Ready.
- Definition of Done.
- Validation Plan.
- Monitoring Requirements.
- Observability Requirements.
- Rollback/Mitigation.
- Success Metrics tecnicos.
- Files likely to change.
- Dependencies.
- Risk.
- Parallelization Notes.

### Tickets de arquitetura/governanca/documentacao/prompt/skill

Success Metrics deve incluir:

- reducao de ambiguidade
- reducao de duplicidade
- melhoria de handoff
- melhoria de rastreabilidade
- reducao de conflito
- aderencia dos agentes ao protocolo
- clareza de ownership

Obrigatorios:

- problema de ambiguidade que resolve
- protocolo afetado
- agentes consumidores
- Definition of Done
- criterio de aderencia
- risco de divergencia se nao fizer
- validacao manual ou automatizada

### Tickets de produto/valor ao usuario

Success Metrics deve incluir:

- KPI principal
- KPI secundario
- evento de conversao
- baseline esperado
- metrica de adocao
- metrica de retencao, se aplicavel
- metrica de qualidade percebida, se aplicavel
- forma de acompanhamento pos-release

Obrigatorios:

- KPI Impact.
- Conversion Event.
- Monitoring Requirements.
- Post-release Follow-up.
- Validation Plan.
- Rollback/Mitigation se houver feature flag, fluxo critico ou risco operacional.

## 9. Backlog Proposto

Nao criar estes tickets no Linear ainda. Esta lista esta pronta para ser convertida em tickets quando o plano for aprovado.

### TICKET-001 - [Multi-Agent] Criar protocolo comum de operacao Codex + Claude Code

**Tipo:** governance, workflow, documentation
**Prioridade:** P0
**Impacto:** Alto
**Esforco:** Medio
**Complexidade:** Media
**Risco:** Medio
**Paralelizavel:** Nao
**Pre-requisitos:** Plano aprovado
**Dependencias:** Nenhuma
**Arquivos provaveis:** `execution/multi-agent-operating-protocol.md`, `AGENTS.md`, `.codex/agents/README.md`
**Definition of Ready:** Escopo do protocolo comum aprovado; approval gates preservados.
**Definition of Done:** Protocolo criado e referenciado sem duplicar regras; Codex e Claude Code compartilham fluxo por ticket.
**Metricas/monitoramento:** Reduçao de divergencia de instrucao; tickets citam protocolo comum.
**Observacoes para execucao:** Nao alterar approval gates alem de referencias.

### TICKET-002 - [Claude] Criar CLAUDE.md como adaptador do protocolo comum

**Tipo:** prompt, documentation, governance
**Prioridade:** P0
**Impacto:** Alto
**Esforco:** Baixo
**Complexidade:** Baixa
**Risco:** Medio
**Paralelizavel:** Nao
**Pre-requisitos:** TICKET-001
**Dependencias:** Protocolo comum
**Arquivos provaveis:** `CLAUDE.md`
**Definition of Ready:** Protocolo comum mergeado.
**Definition of Done:** `CLAUDE.md` curto, operacional e sem divergencia de `AGENTS.md`.
**Metricas/monitoramento:** Claude Code consegue iniciar ticket piloto sem pedir fluxo basico.
**Observacoes para execucao:** Nao criar um segundo AGENTS.md.

### TICKET-003 - [Context] Criar protocolo de roteamento de contexto por tipo de ticket

**Tipo:** workflow, governance, prompt
**Prioridade:** P0
**Impacto:** Alto
**Esforco:** Medio
**Complexidade:** Media
**Risco:** Baixo
**Paralelizavel:** Parcial
**Pre-requisitos:** TICKET-001
**Dependencias:** `.codex/agents/agent-skill-trigger-rules.md`, `.agents/skills/core-skill-contracts.md`
**Arquivos provaveis:** `execution/context-routing-protocol.md`, `.codex/agents/agent-skill-trigger-rules.md`
**Definition of Ready:** Tipos de ticket aprovados.
**Definition of Done:** Mapa read-first por tipo criado e referenciado por Codex/Claude.
**Metricas/monitoramento:** Menos contexto irrelevante carregado; menos alteracoes fora de escopo.
**Observacoes para execucao:** Nao copiar conteudo de todos os docs no roteador.

### TICKET-004 - [Parallel Execution] Definir ownership, write set e conflito entre agentes

**Tipo:** governance, workflow
**Prioridade:** P0
**Impacto:** Alto
**Esforco:** Medio
**Complexidade:** Media
**Risco:** Medio
**Paralelizavel:** Nao
**Pre-requisitos:** TICKET-001
**Dependencias:** `execution/ticket-pr-handoff-system.md`, `execution/linear-governance-model.md`
**Arquivos provaveis:** `execution/parallel-execution-governance.md`
**Definition of Ready:** Lista de arquivos compartilhados de alto risco definida.
**Definition of Done:** Regras de paralelizacao, ownership, write set e conflitos documentadas.
**Metricas/monitoramento:** Conflitos de merge; PRs fora do write set; tickets bloqueados por ownership ambigua.
**Observacoes para execucao:** Serializar mudancas em `AGENTS.md`, approval gates e templates globais.

### TICKET-005 - [Linear] Incrementar template de tickets para execucao multi-agent

**Tipo:** governance, workflow, orchestration-prep
**Prioridade:** P0
**Impacto:** Alto
**Esforco:** Medio
**Complexidade:** Media
**Risco:** Medio
**Paralelizavel:** Parcial
**Pre-requisitos:** TICKET-004
**Dependencias:** Padrão atual do Linear
**Arquivos provaveis:** `execution/linear-ticket-template-v2.md`, `execution/linear-governance-model.md`, `execution/ticket-orchestrator-workflow.md`
**Definition of Ready:** Campos novos obrigatorios e condicionais aprovados.
**Definition of Done:** Template v2 preserva campos atuais e adiciona DoR, DoD, validation plan, metrics e parallelization notes.
**Metricas/monitoramento:** Percentual de tickets novos com campos de readiness e validacao completos.
**Observacoes para execucao:** Nao apagar template atual antes de validar v2.

### TICKET-006 - [Linear] Criar matriz de campos obrigatorios por tipo de ticket

**Tipo:** governance, documentation, workflow
**Prioridade:** P0
**Impacto:** Alto
**Esforco:** Baixo
**Complexidade:** Baixa
**Risco:** Baixo
**Paralelizavel:** Sim, depois de TICKET-005
**Pre-requisitos:** TICKET-005
**Dependencias:** Tipos de entrega aprovados
**Arquivos provaveis:** `execution/ticket-type-field-matrix.md`
**Definition of Ready:** Template v2 existe.
**Definition of Done:** Matriz define obrigatorios/condicionais por tipo e metricas por tipo.
**Metricas/monitoramento:** Menos campos vazios e menos tickets NOT READY.
**Observacoes para execucao:** Manter pragmatismo; nao forcar campos de produto em docs.

### TICKET-007 - [Handoff] Incrementar handoff cross-agent e delivery update

**Tipo:** workflow, governance, documentation
**Prioridade:** P1
**Impacto:** Medio
**Esforco:** Baixo
**Complexidade:** Baixa
**Risco:** Baixo
**Paralelizavel:** Sim
**Pre-requisitos:** TICKET-005
**Dependencias:** `execution/ticket-pr-handoff-system.md`
**Arquivos provaveis:** `execution/ticket-pr-handoff-system.md`, `.codex/agents/agent-handoff-protocol.md`
**Definition of Ready:** Delivery update v2 aprovado.
**Definition of Done:** Handoff inclui executor tool, write set, metricas, monitoramento e next action.
**Metricas/monitoramento:** Menos perguntas de contexto entre tickets.
**Observacoes para execucao:** Nao incluir dados privados no handoff.

### TICKET-008 - [Skills] Padronizar skills e prompts compartilhados para Codex e Claude Code

**Tipo:** skill, prompt, governance
**Prioridade:** P1
**Impacto:** Medio
**Esforco:** Medio
**Complexidade:** Media
**Risco:** Medio
**Paralelizavel:** Parcial
**Pre-requisitos:** TICKET-003
**Dependencias:** `.agents/skills/core-skill-contracts.md`
**Arquivos provaveis:** `.agents/skills/README.md`, `.agents/skills/core-skill-contracts.md`, possivel `prompts/README.md`
**Definition of Ready:** Decisao sobre diretorio de prompts tomada.
**Definition of Done:** Convencao define quando usar skill, prompt ou workflow, e evita duplicacao Codex/Claude.
**Metricas/monitoramento:** Novas skills seguem contrato; menos prompts duplicados.
**Observacoes para execucao:** Nao importar bibliotecas inteiras dos repos de referencia.

### TICKET-009 - [Readiness] Atualizar validator para tickets multi-agent

**Tipo:** workflow, governance, observability
**Prioridade:** P1
**Impacto:** Alto
**Esforco:** Medio
**Complexidade:** Media
**Risco:** Baixo
**Paralelizavel:** Sim
**Pre-requisitos:** TICKET-005, TICKET-006
**Dependencias:** `execution/agent-readiness-validator.md`
**Arquivos provaveis:** `execution/agent-readiness-validator.md`
**Definition of Ready:** Campos v2 e matriz por tipo existem.
**Definition of Done:** Validator classifica READY / NOT READY / READY WITH APPROVAL / BLOCKED com motivos.
**Metricas/monitoramento:** Tickets iniciados sem readiness; blockers por tipo.
**Observacoes para execucao:** Deve ser checklist primeiro, automacao depois se fizer sentido.

### TICKET-010 - [Observability] Criar metricas da operacao agentic

**Tipo:** observability, governance, workflow
**Prioridade:** P1
**Impacto:** Medio
**Esforco:** Medio
**Complexidade:** Media
**Risco:** Baixo
**Paralelizavel:** Sim
**Pre-requisitos:** TICKET-007
**Dependencias:** Handoff incrementado
**Arquivos provaveis:** `execution/agentic-operations-metrics.md`, `knowledge/knowledge-curator-workflow.md`
**Definition of Ready:** Decidir onde registrar metricas iniciais.
**Definition of Done:** Documento define metricas, sinais de alerta e cadencia.
**Metricas/monitoramento:** Throughput, conflito, review time, P0/P1, tickets NOT READY, retrabalho.
**Observacoes para execucao:** Comecar manual; nao criar dashboard prematuro.

### TICKET-011 - [Claude Pilot] Executar ticket piloto de baixo risco com Claude Code

**Tipo:** workflow, governance, documentation
**Prioridade:** P1
**Impacto:** Alto
**Esforco:** Baixo
**Complexidade:** Baixa
**Risco:** Baixo
**Paralelizavel:** Nao
**Pre-requisitos:** TICKET-001 a TICKET-005
**Dependencias:** `CLAUDE.md`, protocolo comum, template Linear v2
**Arquivos provaveis:** A definir pelo ticket piloto
**Definition of Ready:** Ticket piloto aprovado e de baixo risco.
**Definition of Done:** Claude Code executa branch, PR, review, merge e handoff sem desviar do protocolo.
**Metricas/monitoramento:** Aderencia ao protocolo, tempo de execucao, blockers, qualidade de handoff.
**Observacoes para execucao:** Escolher ticket documental pequeno; nao testar em arquivo global critico.

### TICKET-012 - [Orchestration] Analyze repository readiness for Hermes/OpenClaw orchestration after Codex and Claude Code baseline

**Tipo:** orchestration-prep, architecture, governance
**Prioridade:** P3
**Impacto:** Medio futuro
**Esforco:** Medio
**Complexidade:** Alta
**Risco:** Baixo agora, alto se antecipar
**Paralelizavel:** Nao agora
**Pre-requisitos:** Baseline Codex + Claude Code operando; ticket piloto Claude concluido; metricas iniciais registradas
**Dependencias:** TICKET-001 a TICKET-011
**Arquivos provaveis:** `architecture/orchestration-readiness-analysis.md`, `execution/agentic-operations-metrics.md`, `execution/parallel-execution-governance.md`
**Definition of Ready:** Existem exemplos reais de execucao Codex e Claude Code, inclusive paralelizacao ou decisao de nao paralelizar.
**Definition of Done:** Analise compara Hermes/OpenClaw com a estrutura real implementada e gera plano futuro de adaptacao.
**Metricas/monitoramento:** Nao executar antes da baseline; usar dados reais de throughput, conflitos e readiness.
**Observacoes para execucao:** Este ticket deve ficar em horizonte futuro e nao deve implementar orquestrador.

## 10. Sequenciamento

### Onda 0 - Preparacao

Objetivo: criar base de governanca sem mudar o modo de execucao ainda.

- TICKET-001 - Protocolo comum.
- TICKET-003 - Context routing inicial, se pequeno e sem conflito.

### Onda 1 - Claude Code Ready

Objetivo: permitir Claude Code operar com seguranca minima.

- TICKET-002 - `CLAUDE.md`.
- TICKET-004 - Governanca de execucao paralela.

### Onda 2 - Execucao Paralela

Objetivo: reduzir conflito entre Codex e Claude Code.

- TICKET-007 - Handoff cross-agent.
- Ajustes derivados dos primeiros usos do protocolo.

### Onda 3 - Ticketizacao e Linear

Objetivo: tornar tickets melhores para agentes e futuro orquestrador sem substituir o padrao atual.

- TICKET-005 - Template Linear v2.
- TICKET-006 - Matriz por tipo.
- TICKET-009 - Readiness validator.

### Onda 4 - Observabilidade e Metricas

Objetivo: saber se a operacao multi-agent esta melhorando throughput ou criando retrabalho.

- TICKET-010 - Metricas de operacao agentic.
- TICKET-011 - Piloto Claude Code de baixo risco.

### Onda 5 - Orquestracao Futura

Objetivo: apenas preparar analise futura, sem implementar orquestrador.

- TICKET-012 - Analise Hermes/OpenClaw depois da baseline.

## 11. Decisoes Pendentes

### Decisao 1 - `CLAUDE.md` minimo ou `.claude/` completo

- **Opcoes:** apenas `CLAUDE.md`; `CLAUDE.md` + `.claude/README.md`; estrutura `.claude/` com skills/prompts.
- **Recomendacao:** comecar apenas com `CLAUDE.md`.
- **Trade-off:** menos estrutura agora, menos risco de duplicacao; pode exigir `.claude/` depois.
- **Impacto se adiar:** baixo, desde que `CLAUDE.md` exista antes do piloto.

### Decisao 2 - Criar `execution/linear-ticket-template-v2.md` ou editar templates existentes

- **Opcoes:** arquivo v2 separado; editar `linear-governance-model.md`; editar `ticket-pr-handoff-system.md`.
- **Recomendacao:** criar v2 separado e depois referenciar nos existentes.
- **Trade-off:** evita quebrar padrao atual; exige um link a mais.
- **Impacto se adiar:** medio; tickets novos podem continuar no padrao antigo por inercia.

### Decisao 3 - Labels novas no Linear

- **Opcoes:** adicionar todas as labels sugeridas; adicionar apenas `agent:*` e `parallelizable:*`; nao adicionar labels, usar campos no corpo do ticket.
- **Recomendacao:** adicionar poucas labels: `agent:codex`, `agent:claude`, `agent:orchestrator-future`, `parallelizable:*`, `complexity:*`, `effort:*`.
- **Trade-off:** filtros melhores vs risco de ruido.
- **Impacto se adiar:** medio; orquestracao e triagem ficam menos filtraveis, mas corpo do ticket ainda resolve.

### Decisao 4 - Onde registrar metricas operacionais

- **Opcoes:** apenas Linear comments; arquivo `execution/agentic-operations-metrics.md`; knowledge log; dashboard externo futuro.
- **Recomendacao:** comecar com arquivo + handoff Linear, sem dashboard.
- **Trade-off:** simples e versionado, mas menos automatizado.
- **Impacto se adiar:** medio; fica dificil avaliar ganho real de Codex + Claude.

### Decisao 5 - Ferramenta do primeiro piloto Claude Code

- **Opcoes:** ticket documental pequeno; ticket de workflow; ticket tecnico simples.
- **Recomendacao:** ticket documental pequeno com write set isolado.
- **Trade-off:** testa governanca antes de testar codigo.
- **Impacto se adiar:** alto; sem piloto, a baseline continua teorica.

### Decisao 6 - Quando retomar Hermes/OpenClaw

- **Opcoes:** agora; depois de `CLAUDE.md`; depois de piloto Claude; depois de metricas de operacao.
- **Recomendacao:** depois de baseline Codex + Claude, piloto Claude e metricas iniciais.
- **Trade-off:** menos fantasia arquitetural agora, decisao futura mais informada.
- **Impacto se adiar:** baixo, desde que TICKET-012 exista no backlog futuro.

## 12. Proxima Acao Recomendada

1. Revisar este arquivo como fonte canonica do plano.
2. Aprovar o caminho `architecture/agentic-multi-agent-codex-claude-plan.md` como base para ticketizacao.
3. Aprovar a criacao futura dos tickets TICKET-001 a TICKET-012 no Linear.
4. Executar primeiro a Onda 0, com TICKET-001.
5. Criar `CLAUDE.md` somente depois do protocolo comum.
6. Incrementar Linear e readiness antes de rodar trabalho paralelo serio.
7. Executar um ticket piloto pequeno com Claude Code.
8. Registrar metricas iniciais de operacao agentic.
9. Retomar Hermes/OpenClaw apenas pelo ticket futuro de orchestration-prep.
