# ADR-004 — DeepSeek Harness: fronteira de runtime subordinado (decisão documental, sem implementação)

## Record

- ADR ID: ADR-004
- Title: DeepSeek Harness — fronteira de runtime subordinado (decisão documental, sem implementação)
- Date: 2026-09-10
- Status: Accepted
- Owner: Vitor Natividade (fundador)
- Linear ticket: PIP-898
- PR: [#180](https://github.com/vnatividade/pipe-venture-builder/pull/180) — mergeado no commit `5b3bef4c255b0246ca5a0a643b744b3adb783b42`.
- Revision note: emenda PIP-900 (sem novo ADR; histórico preservado no git). Restaura D7, D13 e o BDD 4 à redação dos Acceptance Criteria do PIP-898, aprovada explicitamente pelo fundador em 2026-09-10 (ver "Approval record" abaixo), que é a única base desta restauração. Também alinha as linhas `execute`/`handoff` da tabela dos 8 verbos ao contrato `ApprovalRecord` existente (`src/pipe_venture_builder/control_plane/approval.py`), registra o merge do PR #180 e distingue fixture sintética autorada de captura de runtime. Origem: revisão de prontidão do PIP-899, comentário de auditoria `65ced0c6-e87c-40e3-aae5-221dccdabc5c` (<https://linear.app/pipe-venture-builder/issue/PIP-899/deepseek-harness-implementar-spike-contratual-fail-closed-com#comment-65ced0c6-e87c-40e3-aae5-221dccdabc5c>). Nenhuma decisão nova e nenhuma aprovação humana nova são alegadas.
- Related architecture review: `docs/hermes/README.md`, `setup/portable-bootstrap-and-runtime-boundaries.md`, `capabilities/entries/capability.future.deepseek-harness.json`, `architecture/adr/adr-003-ticket-body-conformance-read.md`
- Supersedes: —
- Superseded by: —

## Context

- **Product ou MVP context:** o Pipe já opera um control plane local governado (planos, aprovações, checkpoints, audit trail hash-chained) e um adapter Hermes real e supervisionado (`docs/hermes/README.md`), que serve como precedente de autoridade: o runtime é subordinado, nunca dono de política, priorização ou aprovação. O DeepSeek Harness (DSH) foi registrado como candidato futuro em `capabilities/entries/capability.future.deepseek-harness.json` — lifecycle `proposed`, `toolAccess.accessType: none`, nenhuma operação autorizada além de registro e comparação — pelo PIP-897, via PR [#179](https://github.com/vnatividade/pipe-venture-builder/pull/179), mergeado no commit `f370460`.
- **Decision trigger:** a própria entrada de capability declara, em `governance.updatePolicy`, que "lifecycle promotion additionally requires the runtime-boundary ADR and a new explicit human decision on installation, data, and tool boundaries" e, em `review.reviewNotes`, que esse ADR "seria numerado ADR-004" e "não existe ainda". Este documento preenche esse requisito: fixa a fronteira de runtime antes de qualquer código, schema, instalação ou execução relacionados ao DSH.
- **Pré-condição satisfeita:** PIP-897 mergeado (PR #179, commit `f370460`), capability em lifecycle `proposed`, legível e íntegra. Este ADR não altera essa entrada.
- **Constraints:**
  - Nenhuma linha de código, teste, fixture, schema, adapter, plugin ou profile é criada por este ticket.
  - Nenhuma instalação, download, build, execução, rede, credencial, modelo, provider ou dado é usada ou autorizada aqui.
  - `schemas/RunEvent.schema.json` não é alterado por este ADR; qualquer ambiguidade de identidade de runtime múltiplo exige ticket de schema próprio antes de produção (ver D11).
  - Pipe/Linear/GitHub e o control plane local permanecem a autoridade canônica; o DSH, se algum dia integrado, é executor subordinado — nunca decisor.
  - O lifecycle da capability permanece `proposed`; este ADR não promove o candidato.
  - Divergências intencionais frente ao adapter Hermes real devem ser nomeadas explicitamente, não assumidas por semelhança.
- **Evidence or source artifacts:**
  - `capabilities/entries/capability.future.deepseek-harness.json` (fonte canônica do candidato registrado).
  - `docs/hermes/README.md` e `setup/portable-bootstrap-and-runtime-boundaries.md` (baseline de autoridade e contrato de adapter de 8 verbos).
  - `schemas/RunEvent.schema.json` (enum fechado de eventos; `references.idempotencyKey` como único campo hoje usado para carregar identidade de runtime externo, herdado do Hermes).
  - `architecture/adr/adr-003-ticket-body-conformance-read.md` (precedente: ADR mergeado antes de qualquer implementação).
  - Avaliação técnica somente-leitura de 2026-09-02, `deepseek-harness-pipe-avaliacao.md`, e fontes oficiais DSH nela pinadas no commit `49a606bc5b5934603f22a26957a07dc799ab0291` (release `dsh-v0.1.2-alpha.5`) — ver seção Links.
- **Human review required:** yes.
- **Approval record:** decisões D1 (autoridade), D7 (workspace), D8 (segurança), D9 (modos proibidos) e D13 (observabilidade) foram aprovadas explicitamente pelo fundador em 2026-09-10, como exigido para qualquer conteúdo que fixe postura de segurança e boundary de dados neste repositório. As decisões D2–D6, D10–D12 são consequência direta e sem alegação de dado/segredo/rede/credencial das mesmas fontes e do mesmo pacote de aprovação, e são registradas juntas neste documento.

## Options Considered

| Option | Pros | Cons | Why accepted/rejected |
|---|---|---|---|
| **A. Adiar a decisão de fronteira até que exista um spike técnico** | Evita escrever regras para um sistema ainda não testado empiricamente pelo Pipe. Zero esforço documental agora. | Deixa a promoção de lifecycle, a autoridade de sessão/evento/aprovação e a interação com o schema `RunEvent` indefinidas — exatamente o que a entrada de capability exige resolver antes de qualquer promoção. Um spike sem fronteira prévia arrisca decidir "sobre a mesa" enquanto código é escrito, misturando decisão e implementação. | **Rejeitada.** O próprio registro da capability (PIP-897) condiciona qualquer avanço a este ADR existir primeiro; adiar apenas empurra o mesmo trabalho para dentro de um ticket de código, onde é mais caro reverter. |
| **B. Tratar o DSH como par de confiança do Hermes, reutilizando a mesma fronteira sem ajuste** | Reaproveita código, testes e vocabulário já validados (35 testes do adapter Hermes verdes); menor esforço de design. | O DSH ainda é *developer preview* alpha, sem auditoria de segurança (`SAFETY.md` do próprio projeto), com SDK sem replay/cursor do log de eventos e com um cliente Python que herda o ambiente do processo por padrão. Copiar a fronteira do Hermes sem reforço trataria essas lacunas como se já estivessem mitigadas, quando não estão. | **Rejeitada.** A fronteira Hermes é o piso, não o teto: o DSH exige restrições adicionais (workspace descartável, ambiente allowlisted, ausência de replay tratada como bloqueador, aprovação sempre `never` no runtime) que a paridade simples não cobriria. |
| **C. Fixar o DSH como executor estritamente subordinado, mais restrito que o Hermes, com fronteiras explícitas de sessão/evento/checkpoint/aprovação/workspace/segurança/observabilidade e todos os 8 verbos de adapter marcados como desenho futuro não executado** | Preserva a autoridade do Pipe sem ambiguidade; permite que um futuro ticket de spike (Fase 1, fake/offline) comece sem precisar rediscutir autoridade, dados, sessão, recovery ou aprovação; nomeia as divergências do Hermes em vez de escondê-las; não compromete o schema `RunEvent` nem o lifecycle da capability. | Mais texto normativo agora, sem nenhum código para validar as decisões empiricamente; existe risco de a fronteira precisar de ajuste quando o spike técnico rodar contra o protocolo real. | **Aceita.** É a única opção que cumpre a pré-condição da capability (`governance.updatePolicy`), preserva a autoridade Pipe/lifecycle `proposed`, e produz um documento revisável e citável por tickets futuros, sem autorizar nada operacional. |

## Decision

- **Selected option:** C — o DeepSeek Harness é modelado como executor estritamente subordinado ao control plane do Pipe, mais restrito que o adapter Hermes real, com as 13 decisões abaixo (D1–D13) como contrato normativo para qualquer ticket futuro de design ou spike.

- **Rationale:** o Hermes prova que um runtime pode ser útil sem ser autoridade — mas o DSH parte de uma maturidade menor (alpha, sem auditoria de segurança, SDK sem replay/cursor, cliente que herda ambiente por padrão). Herdar a fronteira Hermes sem reforço trataria lacunas conhecidas como resolvidas. A opção C mantém o mesmo princípio de autoridade (Pipe decide, registra, executa por adapter governado, verifica) e adiciona as restrições que a maturidade observada do DSH exige.

- **What this enables:** um futuro ticket de spike contratual (offline, com transporte falso e fixtures, sem instalar ou executar o DSH real) pode começar a modelar contexto, evento e checkpoint experimentais citando este ADR, sem reabrir a discussão de autoridade, workspace, segurança ou aprovação. O ADR também dá ao registry (`capability.future.deepseek-harness`) a peça que faltava para qualquer decisão futura de promoção de lifecycle.

- **What this intentionally does not solve:**
  - Não implementa adapter, modelo, fixture, teste, schema ou transporte.
  - Não instala, baixa, compila, credencia ou executa o DSH, nem abre rede.
  - Não altera `schemas/RunEvent.schema.json` nem resolve a sobrecarga de `references.idempotencyKey` (ver D11) — isso exige ticket de schema próprio, antes de produção.
  - Não promove o lifecycle da capability além de `proposed`.
  - Não decide sobre o plugin Honcho, sobre provedores/modelos reais, sobre compatibilidade Ollama/GPT-OSS/OpenAI-compatible, nem sobre qualquer uso pago.
  - Não certifica segurança, qualidade, desempenho ou custo do DSH.

### D1–D13 — Decisões de fronteira

**D1 — Autoridade.** O repositório Pipe, Linear, GitHub e o control plane local (SQLite append-only com encadeamento de hash) permanecem a fonte canônica de produto, arquitetura, execução, aprovação e auditoria. Um eventual DSH atua exclusivamente como executor/proponente dentro do escopo de um ticket aprovado; nunca decide, aprova, prioriza ou fecha ticket/PR por conta própria. *(Aprovação humana registrada em 2026-09-10.)*

**D2 — Workflows habilitados.** Um eventual spike inicial (fora do escopo deste ADR) só pode modelar workflows de `review` e `check` — leitura e verificação, sem efeito. Workflows de `idea`, `adopt` ou `reconcile` via DSH exigem revisão própria deste ADR ou um ADR sucessor antes de serem sequer desenhados, porque tocam produção de artefatos canônicos (ProductBaseline, ReconciliationPlan) que hoje pertencem aos comandos Pipe existentes.

**D3 — Sessão.** Uma tentativa (`attempt`) de run Pipe, se um dia vinculada a uma sessão DSH, prende exatamente: `pipeRunId`, identificador de sessão DSH, versão do DSH, versão de protocolo, hash do perfil/plugin tree, rota/modelo declarado, hash do manifesto de workspace e hash de contexto. Qualquer mudança em um desses vínculos exige nova tentativa/sessão — nunca reaproveitamento silencioso. Um único consumidor por sessão. `session.status=idle` ou o fechamento de um turno (`turn/end`) são sinais operacionais do runtime, não conclusão de run Pipe — a conclusão exige validação de artefato/resultado e integridade do audit trail, como no Hermes (`docs/hermes/README.md`, mapeamento de eventos). Subagentes ficam fora de escopo de qualquer desenho até existir decisão própria de identidade causal, orçamento e checkpoint.

**D4 — Eventos.** A fonte durável observável é o evento tipado (`session.event`), nunca o status efêmero. Tipos de evento desconhecidos, sequência com gap, reordenamento ou conteúdo conflitante para a mesma identidade bloqueiam o processamento — nunca são inferidos ou ignorados. Apenas campos allowlisted (identificadores, sequência, tipo, timestamp, nome de ferramenta permitido, motivo de término, contagens, fingerprints e referências controladas) podem ser considerados em qualquer desenho futuro; prompt, mensagem, argumento bruto, stdout/stderr ou resultado de ferramenta bruto nunca atravessam essa fronteira — mesmo princípio do ADR-003 aplicado a fonte externa de outro tipo.

**D5 — Checkpoints.** O checkpoint de transcript/sessão do DSH (se um dia existir integração) e o checkpoint de ação do Pipe são conceitos distintos e não substituíveis um pelo outro. Qualquer store futuro para o DSH deve seguir o padrão já usado pelo `HermesCheckpointStore`: arquivo próprio, atômico, fingerprintado, diretório `0700`/arquivo `0600`, sem seguir symlink. O checkpoint Pipe continua sendo a única fonte de verdade sobre plano, ação, aprovação e verificação.

**D6 — Aprovação.** Uma aprovação interna do DSH (o plugin de `user-approval`, ligado a um turno aberto) nunca cria, representa ou substitui um `ApprovalRecord` Pipe. Só um `ApprovalRecord` exato, vinculado ao plano e ação registrados, pode autorizar qualquer efeito fora do processo — mesmo padrão já aplicado ao Hermes, em que `approval.granted` é rejeitado sem o record Pipe correspondente.

**D7 — Workspace.** Qualquer workspace usado por um DSH futuro deve ser descartável, fora do worktree real do Pipe, construído a partir de uma allowlist de fixtures não sensíveis — nunca o diretório de trabalho do repositório. Ficam excluídos `.git`, `.env`, sockets, caches de usuário, home real e qualquer symlink, seja qual for o seu alvo. *(Aprovação humana registrada em 2026-09-10.)*

**D8 — Segurança.** Qualquer desenho futuro deve manter desabilitados, por padrão: telemetria (o bundle base do DSH configura `FEEDBACK_ONLY` sem redaction embutida), descoberta de credenciais/plugins do usuário, hot reload de plugin, e herança do ambiente do processo pai — o cliente Python do DSH, na versão observada, herda `os.environ` inteiro por padrão antes de aplicar overrides, o que é inaceitável para um processo Pipe que possa ter segredos no ambiente. Rede deve ser bloqueada externamente ao processo (o modelo de sandbox do DSH não cobre toda a superfície de rede). *(Aprovação humana registrada em 2026-09-10.)*

**D9 — Modos proibidos.** Nenhum desenho ou spike futuro pode usar o perfil `sdk-minimal` (que expõe `danger-full-access`, shell e editor), o nível de sandbox `danger-full-access`, execução unattended/YOLO/gateway/cron do DSH, ferramenta com efeito de escrita, ou lançamento de subprocesso real dentro do escopo deste ADR ou de um eventual spike de Fase 1. Isso espelha a mesma exclusão deliberada já aplicada ao Hermes (`docs/hermes/README.md`, seção "Deliberate Exclusions"). *(Aprovação humana registrada em 2026-09-10.)*

**D10 — Recovery.** A SDK Python/protocolo do DSH observada na versão pinada (`dsh-v0.1.2-alpha.5`, commit `49a606bc5b5934603f22a26957a07dc799ab0291`) expõe apenas `initialize`, `session/prompt` e `shutdown` como métodos cliente→servidor, sem negociação de versão, sem replay/query do log de eventos e sem cursor de consumo — conforme as fontes oficiais pinadas (`packages/sdk/protocol/src/types.ts`, `packages/sdk/server/README.md`, `python/sdk/README.md`). Essa é uma **observação pinada à fonte oficial, não uma alegação adicional**: a ausência de replay/cursor é registrada aqui como **bloqueador de produção**. Nenhum desenho futuro pode inferir conclusão de run a partir de um gap de sequência; um gap sempre interrompe/bloqueia, nunca é preenchido por suposição.

**D11 — Schema.** `schemas/RunEvent.schema.json` não é alterado por este ADR nem pode ser alterado lateralmente por um eventual ticket de spike (Fase 1). O adapter Hermes já reaproveita `references.idempotencyKey` para guardar identificadores `HE-*` como solução pontual, documentada como limitação herdável em `docs/hermes/README.md`. Adicionar um segundo runtime candidato sobre o mesmo campo aprofundaria essa ambiguidade de origem/idempotência. Qualquer necessidade real de identidade de runtime genérica (um envelope tipo `RuntimeEvent`, versionado e separado de idempotência de ação) exige **ticket de schema próprio, aprovado separadamente, antes de qualquer uso em produção** — nunca uma decisão implícita dentro de um spike de contrato.

**D12 — Os 8 verbos do contrato de adapter.** Ver tabela dedicada abaixo. Todos os 8 verbos definidos em `setup/portable-bootstrap-and-runtime-boundaries.md` (seção "Adapter Contract") recebem aqui apenas **desenho conceitual**; nenhum é implementado, executado ou testado neste ticket.

**D13 — Observabilidade.** O audit trail canônico permanece exclusivamente no control plane do Pipe (SQLite local, hash-chained). Qualquer desenho futuro de integração DSH só pode persistir metadados redigidos: identificadores, sequência, hashes de versão/protocolo/perfil/workspace, contagens agregadas e estados de execução. Conteúdo bruto do DSH — prompt, saída de modelo, argumento ou resultado de ferramenta, frame de protocolo, log de sessão, stdout/stderr — nunca é persistido em lugar nenhum: nem no control plane, nem no repositório, nem em checkpoint, nem em diretório temporário, inclusive para depuração de um spike futuro. Só persistem os metadados redigidos listados acima. *(Aprovação humana registrada em 2026-09-10.)*

### Os 8 verbos do contrato de adapter — desenho futuro, não executado neste ticket

Fonte do contrato: `setup/portable-bootstrap-and-runtime-boundaries.md`, seção "Adapter Contract". Para cada verbo, este ADR registra apenas a intenção de desenho compatível com D1–D13; nenhuma linha abaixo autoriza execução.

| Verbo | Comportamento exigido pelo contrato | Intenção de desenho para um eventual adapter DSH | Status neste ticket |
|---|---|---|---|
| `detect` | Reportar versão/disponibilidade instalada sem mutação. | Checar, sem instalar, se um binário/pacote DSH pinado existe localmente; nunca baixar ou instalar como efeito colateral da detecção. | Não executado — apenas desenhado |
| `install` | Criar somente links/configuração locais documentados; idempotente e seguro contra conflito. | Não aplicável a este ADR: qualquer instalação real do DSH permanece fora de escopo de qualquer ticket até uma Fase 2 com aprovação própria. O verbo é registrado apenas para manter paridade de contrato com os demais adapters. | Não executado — apenas desenhado |
| `doctor` | Validar caminhos, versões, dependências e estado de conector, com redação. | Validaria pin de commit/versão, hash de perfil estático e ausência de plugins de credencial/telemetria antes de qualquer uso — sem nunca imprimir segredo ou payload bruto. | Não executado — apenas desenhado |
| `prepare_context` | Construir um Context Pack limitado e rastreável à fonte. | Montaria um manifesto mínimo (hashes de workspace/perfil/contexto) a partir de fixtures allowlisted, nunca do worktree real. | Não executado — apenas desenhado |
| `execute` | Rodar apenas um ticket aprovado ou pedido de planejamento. | Executaria, no máximo, um workflow de leitura `review`/`check` (D2) sob a autorização do ticket Pipe aprovado. Leitura não gera `ApprovalRecord`, e nenhum `ApprovalRecord` é fabricado para leitura. O `ApprovalRecord` Pipe é action-scoped: só é emitido para ações aprováveis pelo contrato existente (`create`/`update`/`link`, `MUTATING_ACTIONS` em `src/pipe_venture_builder/control_plane/approval.py`) e é validado no `handoff`/boundary governado antes de qualquer efeito externo (D6). Qualquer ferramenta com efeito de escrita fica fora de escopo até revisão própria. | Não executado — apenas desenhado |
| `checkpoint` | Persistir estado operacional recuperável. | Persistiria checkpoint Pipe próprio (D5), distinto do transcript DSH, com os mesmos padrões de atomicidade/fingerprint/permissão do `HermesCheckpointStore`. | Não executado — apenas desenhado |
| `handoff` | Escrever ou propor handoff canônico para Linear/GitHub/repositório. | Proporia apenas documentos inertes (`pipe_propose`-like), nunca aplicaria mutação. É neste ponto que um `ApprovalRecord` Pipe exato e action-scoped seria validado (D6), e a validação nunca aplica a ação; aplicação real permanece atrás do `ApplyService`/adapter governado existente. | Não executado — apenas desenhado |
| `uninstall` | Remover somente itens criados pelo próprio adapter; listar o que resta. | Removeria apenas artefatos/checkpoints locais criados por um eventual adapter DSH, nunca estado do control plane compartilhado. | Não executado — apenas desenhado |

## Consequences

- **Positive consequence:** a entrada de capability `capability.future.deepseek-harness` passa a ter o ADR de fronteira que seu próprio `governance.updatePolicy` exige para qualquer promoção futura; um eventual ticket de spike contratual (fixtures/transporte falso, offline) pode começar citando D1–D13 sem reabrir autoridade, sessão, evento, checkpoint, aprovação, workspace, segurança ou observabilidade.
- **Tradeoff accepted:** o documento é normativo antes de qualquer evidência empírica de um spike rodando contra o protocolo real do DSH; algumas decisões (especialmente D3/D4/D5, sobre forma exata de vínculo de sessão/evento) podem precisar de ajuste quando um spike futuro as exercitar — nesse caso, este ADR é revisado ou superseded, não contornado silenciosamente. O spike de Fase 1 usa apenas fixtures sintéticas autoradas a partir das formas públicas pinadas do protocolo, sem executar o DSH. Captura de runtime (gravação de frames/eventos de um processo DSH real) exige execução real, é proibida por D9 no escopo de Fase 1 e precisa de ticket e aprovação próprios.
- **Risk introduced:** a existência deste ADR pode ser mal lida como autorização de execução, instalação, rede, credencial ou dado. Mitigado por linguagem explícita de "desenho futuro, não executado" em cada seção operacional e pela ausência de qualquer comando, script ou caminho de execução no diff deste ticket.
- **Risk introduced:** a ausência de replay/cursor na SDK do DSH (D10) pode ser contornada por um futuro executor que trate `idle`/`turn/end` como conclusão para simplificar a implementação. Mitigado por D3, D4 e D10 nomearem esse anti-padrão explicitamente como proibido, e pelo requisito de cenário BDD prospectivo #2 abaixo.
- **Risk introduced:** um futuro ticket de schema pode ser tentado a resolver D11 "de passagem" dentro de um spike de contrato, misturando decisão de schema com fixture experimental. Mitigado por D11 exigir ticket próprio e aprovado separadamente antes de produção.
- **Mitigation:** todo o texto operacional usa "desenho", "proporia", "não executado neste ticket" — nunca tempo verbal de execução real — e qualquer PR que cite este ADR para justificar instalação, rede, credencial ou dado real está, por definição, fora do que este documento autoriza.
- **Follow-up ticket:** ticket de spike contratual (Fase 1, fake/offline, sem instalar DSH) só pode começar depois deste ADR mergeado, e deve citar D1–D13 explicitamente. Um ticket de schema/`RuntimeEvent` genérico é necessário antes de qualquer produção que envolva mais de um runtime externo (D11). Um ticket de conformidade de provider/modelo (incluindo a hipótese Ollama/open models abaixo) é necessário antes de qualquer Fase 3. A correção da ausência de ADR-003 no índice de ADRs é follow-up documental separado, fora do escopo deste ADR.

### Hipótese de compatibilidade explicitamente não comprovada — Ollama/open models

Um relato público em uma rede social (não uma fonte oficial do projeto DSH) sugere execução problemática com GPT-OSS/OpenAI-compatible via DSH. **Esse relato não é usado como evidência neste ADR e não sustenta nenhuma decisão aqui.** O que este ADR registra, com base apenas nas fontes oficiais pinadas (`packages/llm/llm-pi-ai/README.md` e as discussões públicas do próprio repositório oficial, tratadas como relatos de usuário e não como garantia dos mantenedores), é:

- a documentação oficial do adapter multi-provider (`llm-pi-ai`) reconhece limitações conhecidas em endpoints "OpenAI-compatible" (ausência de suporte a `tool_choice`, necessidade de placeholder de autenticação mesmo em endpoint local sem auth, perda de status HTTP do provider, entre outras);
- discussões oficiais do repositório relatam, como relatos de usuário, tool calls renderizadas como texto, problemas de autenticação com Ollama, timeout de modelos locais e IDs/nomes de tool call vazios ou malformados;
- **nenhuma dessas fontes prova ou refuta compatibilidade real do DSH com Ollama ou outros modelos abertos** — a compatibilidade permanece uma hipótese de teste, rotulável como H-PROTOCOL-01, a ser verificada por um futuro ticket de conformidade com fixtures declarativas, nunca assumida como fato arquitetural.
- Este ADR não autoriza nenhum teste real contra Ollama, GPT-OSS ou qualquer provider; qualquer verificação empírica exige ticket e aprovação próprios (Fase 3, fora de escopo).

### Plugins — superfície oficial, sem claim de qualidade ou segurança

A arquitetura de plugins Cordis do DSH é uma superfície real e documentada oficialmente (`docs/architecture.md`, `docs/cookbook/extension-cookbook.md`), e o plugin de terceiros `dsh-honcho` (Plastic Labs, público em `https://github.com/plastic-labs/dsh-honcho`) confirma que essa superfície é utilizável por terceiros para registrar contexto, ferramentas e persistência de memória externa. Este ADR registra apenas a **existência** dessa superfície oficial como fato observável nas fontes pinadas. Não há, aqui ou em qualquer fonte oficial consultada, uma auditoria de segurança ou uma avaliação de qualidade dos plugins — o próprio `SAFETY.md` do DSH não certifica isolamento entre plugin e runtime. Nenhuma decisão deste ADR depende da qualidade ou segurança de qualquer plugin específico, incluindo o Honcho, que permanece fora de escopo (exigiria credencial/serviço externo e movimentação de dados de memória, ambos proibidos por D1, D7, D8 e pelos gates absolutos de `AGENTS.md`).

## Review Trigger

Revisar este ADR quando:

- a versão do DSH, o protocolo da SDK, ou o conjunto de métodos expostos (`initialize`, `session/prompt`, `shutdown`) mudar de forma que afete D3, D4, D5 ou D10;
- a SDK oficial passar a expor replay, query ou cursor do log de eventos — o que mudaria diretamente o bloqueio de produção registrado em D10;
- `schemas/RunEvent.schema.json` ou `references.idempotencyKey` forem propostos para mudança (D11), ou um ticket de `RuntimeEvent` genérico for aberto;
- qualquer promoção de lifecycle da capability `capability.future.deepseek-harness` além de `proposed` for proposta;
- um ticket de spike técnico (Fase 1), que usa apenas fixtures sintéticas autoradas a partir das formas públicas pinadas do protocolo, sem executar o DSH, revelar que alguma decisão D1–D13 é inexequível como desenhada; captura de runtime (gravação de frames/eventos de um processo DSH real) exige execução real, é proibida por D9 no escopo de Fase 1 e precisa de ticket e aprovação próprios;
- surgir P0/P1 relacionado a vazamento de payload bruto, herança de credencial/ambiente, ou confusão entre aprovação DSH e `ApprovalRecord` Pipe;
- o plugin Honcho, qualquer outro plugin de memória externa, ou qualquer decisão de provider/modelo real (incluindo a hipótese Ollama/open models) for proposto para avaliação própria;
- data ou fase: antes de qualquer ticket de spike de Fase 1 ser movido para READY, e antes de qualquer nova aprovação humana de instalação, dados ou ferramentas do DSH.

## Links

- Linear: PIP-898 (este ADR) · PIP-897 (registro da capability, pré-condição mergeada)
- PR: [#179](https://github.com/vnatividade/pipe-venture-builder/pull/179) — registro da capability `capability.future.deepseek-harness`, mergeado no commit `f370460`. O PR deste próprio ADR é [#180](https://github.com/vnatividade/pipe-venture-builder/pull/180), mergeado no commit `5b3bef4c255b0246ca5a0a643b744b3adb783b42`.
- Architecture review: `docs/hermes/README.md`, `setup/portable-bootstrap-and-runtime-boundaries.md`, `architecture/adr/adr-003-ticket-body-conformance-read.md`
- Fontes oficiais DSH pinadas (commit `49a606bc5b5934603f22a26957a07dc799ab0291`, release `dsh-v0.1.2-alpha.5`):
  - Repositório/commit: <https://github.com/deepseek-ai/deepseek-harness/tree/49a606bc5b5934603f22a26957a07dc799ab0291>
  - Release: <https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.1.2-alpha.5>
  - Safety notice: <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/SAFETY.md>
  - License: <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/LICENSE>
  - SDK protocol types: <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/packages/sdk/protocol/src/types.ts>
  - Python SDK client (herança de ambiente): <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/python/sdk/src/deepseek_harness/client.py>
  - Multi-provider/compat (`llm-pi-ai`): <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/packages/llm/llm-pi-ai/README.md>
  - Architecture: <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/docs/architecture.md>
  - Extension cookbook: <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/docs/cookbook/extension-cookbook.md>
  - SDK server README: <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/packages/sdk/server/README.md>
  - Python SDK README: <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/python/sdk/README.md>
  - Telemetry (bundle base `FEEDBACK_ONLY`, referenciado em D8): <https://github.com/deepseek-ai/deepseek-harness/tree/49a606bc5b5934603f22a26957a07dc799ab0291/packages/plugins/telemetry-otel>
  - Base bundle/profile: <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/packages/bundle/base/cordis.patch.yml>
  - SDK minimal profile (referenciado em D9): <https://github.com/deepseek-ai/deepseek-harness/tree/49a606bc5b5934603f22a26957a07dc799ab0291/packages/profile/sdk-minimal>
  - User approval (referenciado em D6): <https://github.com/deepseek-ai/deepseek-harness/blob/49a606bc5b5934603f22a26957a07dc799ab0291/packages/plugins/user-approval/README.md>
  - Sandbox (referenciado em D9): <https://github.com/deepseek-ai/deepseek-harness/tree/49a606bc5b5934603f22a26957a07dc799ab0291/packages/plugins/sandbox>
  - Discussões oficiais (relatos de usuário, não garantia dos mantenedores): <https://github.com/deepseek-ai/deepseek-harness/discussions/3609>, <https://github.com/deepseek-ai/deepseek-harness/discussions/5125>, <https://github.com/deepseek-ai/deepseek-harness/discussions/5124>, <https://github.com/deepseek-ai/deepseek-harness/discussions/231>, <https://github.com/deepseek-ai/deepseek-harness/discussions/1263>, <https://github.com/deepseek-ai/deepseek-harness/discussions/2540>, <https://github.com/deepseek-ai/deepseek-harness/discussions/2823>, <https://github.com/deepseek-ai/deepseek-harness/discussions/2979>
  - Audit comment (registro PIP-897): <https://linear.app/pipe-venture-builder/issue/PIP-897/capability-registry-registrar-deepseek-harness-como-capability-futura#comment-5ba0a5eb-8287-4de2-803d-0099dc054157>
- KDR/DAR: —

## Matriz BDD prospectiva (não executada — desenho para validação de um futuro spike)

Todos os cenários abaixo descrevem comportamento esperado de um **futuro** ticket de spike contratual (offline, fake, sem instalar o DSH). Nenhum é executado, testado ou implementado por este ADR.

| # | Given | When | Then |
|---|---|---|---|
| 1 | Uma aprovação concedida pelo runtime DSH sem `ApprovalRecord` Pipe correspondente | é recebida pelo adapter | a ação permanece bloqueada; nenhuma aprovação Pipe é inferida (D6) |
| 2 | `session.status=idle` ou uma notificação de `turn/end` | é observada pelo adapter | o run Pipe não é marcado como concluído; conclusão exige validação de artefato/resultado e audit trail íntegro (D3) |
| 3 | Um evento com gap de sequência, reordenamento, tipo desconhecido ou conflito de conteúdo para a mesma identidade | é normalizado | o processamento bloqueia; o trecho perdido nunca é inferido ou preenchido por suposição (D4, D10) |
| 4 | Um workspace fora da allowlist, contendo qualquer symlink, ou apontando para o worktree real do Pipe | é preparado para uma sessão | a preparação é recusada antes de qualquer lançamento de runtime (D7) |
| 5 | Ambiente herdado do processo pai, plugin de telemetria/credencial habilitado, ou tentativa de acesso à rede no preflight | falha a validação de preflight | nenhum subprocesso ou sessão é iniciado (D8, D9) |
| 6 | A necessidade de um novo campo ou semântica em `RunEvent` para representar identidade de runtime DSH | surge durante um ticket de spike futuro | o trabalho para e abre um ticket de schema próprio; o schema não é alterado lateralmente dentro do spike (D11) |
| 7 | Qualquer um dos 8 verbos do contrato de adapter (`detect`, `install`, `doctor`, `prepare_context`, `execute`, `checkpoint`, `handoff`, `uninstall`) | é lido a partir deste ADR | existe uma posição de desenho explícita e a marcação "não executado neste ticket" (D12) |
