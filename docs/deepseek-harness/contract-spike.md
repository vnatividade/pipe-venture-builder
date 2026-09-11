# DeepSeek Harness — spike contratual fail-closed (PIP-899)

**Escopo desta evidência: nenhum runtime/provider real foi executado; compatibilidade não foi provada.** Tudo o que este documento descreve roda offline, com fixtures sintéticas autoradas para os testes e um transporte falso in-process. Nenhum DeepSeek Harness (DSH), provider, modelo, processo, rede, credencial ou dado real foi instalado, executado, sondado ou lido. O resultado mostra que a fronteira do ADR-004 é implementável e testável do lado do Pipe; não diz nada sobre o comportamento do DSH, de DeepSeek, Ollama, GPT-OSS ou de qualquer endpoint OpenAI-compatible.

- Ticket: PIP-899. Especificação normativa: `architecture/adr/adr-004-deepseek-harness-runtime-boundary.md` (versão corrigida por PIP-900, merge `7cb31b7`).
- Código: `src/pipe_venture_builder/adapters/deepseek_harness/` (experimental, não registrado em CLI, runtime registry, manifest ou capability operacional).
- Testes: `tests/deepseek_harness/`.
- Nomenclatura experimental, decisão técnica do orquestrador (não é aprovação humana nem identidade/schema canônica): pacote `deepseek_harness`, `DHE-*` para IDs de evento e `DHD-*` para IDs de dispatch.

## O que foi construído

| Módulo | Responsabilidade | ADR-004 |
|---|---|---|
| `context.py` — `DeepSeekHarnessRunContext` | Contexto só para workflows `review`/`check`; ticket Linear; refs de workspace canônicas e relativas; varredura da árvore inteira da fixture root antes de qualquer leitura, via descritores sem seguir symlink; recusa qualquer symlink (inclusive com alvo interno), `.git`, `.env*`, credenciais e arquivos especiais; fingerprint de manifesto; nunca expõe o root absoluto. | D2, D7, D13 |
| `session.py` — `SessionBinding`, `SessionRegistry` | Vínculo imutável de run/sessão/attempt, versões DSH/protocolo, perfil/hash de plugins, rota/modelo sintéticos allowlisted, hashes de workspace/contexto e consumidor único; linhagem forward-only; qualquer mudança exige novo attempt. | D3, D9 |
| `preflight.py` | Configuração sintética declarando env herdado, discovery de credencial/plugin, telemetria, hot reload ou rede falha antes de a sessão falsa existir; não lê env nem lança processo. | D8 (BDD 5) |
| `events.py` — `DeepSeekHarnessRuntimeEvent`, `DeepSeekHarnessEventSequence` | Evento só com metadados allowlisted; tipos que aprovam ou concluem run são proibidos; ferramentas só de leitura (`read_file`); sequência contígua a partir de 1, duplicata idêntica idempotente, gap/reorder/conflito bloqueiam para sempre. | D4, D10 |
| `adapter.py` — `DeepSeekHarnessRuntimeAdapter` | Compõe o `LocalControlPlaneStore` sem alterá-lo: dispatch só para run Pipe registrado com plano correspondente, binding mais recente, contexto vinculado e audit chain íntegra; eventos viram eventos de audit Pipe sem payload; handoff, proposta e conclusão dedicadas. | D1, D3, D6, D11, D12 |
| `checkpoint.py` — `DeepSeekHarnessCheckpointStore` | Checkpoint próprio por run: JSON canônico e fingerprintado, diretório `0700`, arquivo `0600`, escrita temporária + `fsync` + rename atômico; toda a cadeia de diretórios aberta a partir de `/` sem seguir symlink. | D5, D7 |
| `proposal.py` | Documento de proposta inerte e fingerprintado (`read_result` ou `action_handoff`), sem handle, callback ou referência executável. | D6, D12 |
| `normalizer.py` — `DeepSeekHarnessNormalizer` | Converte frames JSON-RPC/NDJSON sintéticos em eventos allowlisted; conteúdo bruto só existe dentro da função de normalização. | D4, D10, D13 |
| `transport.py` — `FakeNdjsonTransport`, `drive_session` | Transporte in-process roteirizado: sucesso, frame parcial remontado, timeout e EOF sem processo, socket, relógio, thread ou arquivo. `drive_session` entrega toda recusa do transporte ou do normalizador ao adapter (`refuse`), que bloqueia o attempt de forma durável. | D8, D9, D10 |

## O que o spike provou (sob fixtures sintéticas)

1. **Autoridade Pipe.** Um dispatch só ocorre para um run Pipe registrado cujo plano confere por `planId` e fingerprint, pelo binding mais recente do attempt, com o mesmo contexto e com a audit chain verificada. Run inexistente, plano divergente, binding superado, segundo consumidor, contexto divergente, audit adulterada e run terminal ou bloqueado são recusados sem mutação; uma recusa de protocolo nunca reescreve um run terminal. O audit Pipe é a autoridade durável sobre qual dispatch (`DHD-*`) é dono de cada attempt: um registry reconstruído após restart não consegue religar um attempt auditado a outra sessão (`binding_immutable`) nem voltar a um attempt anterior ao último auditado (`binding_superseded`), com ou sem checkpoint.
2. **Eventos sem payload.** O audit Pipe recebe só eventos sem payload: `run.resumed` com `idempotencyKey` `DHD-*`/`DHE-*` e o attempt, o marcador de bloqueio `run.interrupted` (`DHD-*:blocked`) e o `run.completed` da conclusão dedicada; nome de ferramenta, argumentos, resultados, mensagens e raciocínio nunca chegam a audit, checkpoint, proposta, erro ou disco. Os testes varrem todos os arquivos escritos no `TemporaryDirectory` à procura de sentinelas textuais e secret-shaped.
3. **Sequência e protocolo fail-closed.** Gap, reorder, duplicata conflitante e toda recusa da matriz (frame inválido, tipo desconhecido, truncamento, tool call literal ou malformado, raciocínio inconsistente, timeout e EOF fora de um ponto de repouso) bloqueiam o attempt. O bloqueio é gravado primeiro no audit Pipe, como um evento `run.interrupted`/`blocked` sem payload com chave `DHD-*:blocked`, e depois no checkpoint; se qualquer das escritas falhar, a falha é levantada. `begin`, `record_event`, `propose` e `complete` recusam um attempt com esse marcador mesmo que o checkpoint falte, esteja atrás ou tenha sido reassinado como `running`, ou que outra instância do adapter segure o stream, e um normalizador novo não retoma o stream. Qualquer falha de armazenamento no marcador vira código fixo e o checkpoint ainda é bloqueado; uma instância com visão desatualizada (audit ou checkpoint diferentes da sua cópia) é recusada com `checkpoint_stale` ou `stream_blocked` antes de gravar, propor ou concluir. Um attempt novo, com sessão nova, pode seguir um attempt bloqueado. Duplicata idêntica é idempotente, inclusive após restart.
4. **Checkpoint e recovery forward-only.** Intenção gravada antes do write no audit e confirmada depois (write-ahead). No recovery, a intenção é reconciliada com o audit, nunca adivinhada. Checkpoint atrás do audit (`checkpoint_stale`), com eventos ausentes do audit (`checkpoint_audit_mismatch`), de outro binding, adulterado, com modo errado ou symlinkado é recusado. Sem o arquivo, um dispatch já auditado exige recovery (`recovery_required`) e o attempt não pode ser religado a outra sessão. Attempt interrompido fora de um ponto de repouso fica bloqueado como `outcome_unknown` até um novo attempt; ponto de repouso é turno fechado ou sessão ociosa sem turno nem tool call aberto. Escrita interrompida nunca substitui o checkpoint válido.
5. **Aprovação nunca vem do runtime.** `approval.granted` do DSH é recusado. `handoff` só aceita um `ApprovalRecord` Pipe exato, `approved`, dentro da validade, já registrado no audit Pipe e não superado por decisão posterior, para ação `create`/`update`/`link` (cada uma com plano gerado pelo planner e teste próprio). Ele valida e devolve proposta inerte, sem aplicar, registrar ou checkpointar a ação Pipe, e nunca chama o `SupervisedApplyService`, que o pacote não importa. Workflows de leitura nunca exigem, registram ou fabricam `ApprovalRecord`.
6. **Conclusão só pelo método dedicado.** `session.idle`, `turn.ended`, EOF, timeout e status nunca produzem `run.completed`. `complete` exige stream em repouso e não bloqueado, a proposta `read_result` exata emitida para o estado atual (fingerprint e marca d'água de eventos) e audit chain íntegra; o `run.completed` referencia a proposta por `DHD-*:<fingerprint>`.
7. **Fronteira de host.** Teste AST garante que o pacote não importa diretamente `subprocess`, `socket`, `ssl`, `urllib`, `http`, `requests`, `logging`, `asyncio`, `multiprocessing`, Hermes ou `pipe_venture_builder.apply`, nem referencia env/home/processos. Importar o pacote carrega transitivamente alguns desses módulos via `pipe_venture_builder.adapters` (inventário), sem usá-los; `pipe_venture_builder.apply` não é carregado. Testes de runtime registram e recusam acesso a env, processo, rede e (onde aplicável) filesystem. Recusas de decode não guardam o frame bruto nem em `__context__`.

## O que o spike NÃO provou

- Qualquer compatibilidade com o DSH real, seu protocolo (`initialize`, `session/prompt`, `shutdown`), plugins, perfis ou versões; os frames são uma forma de notificação escrita para este spike.
- Qualquer propriedade de DeepSeek, Ollama, GPT-OSS, endpoints OpenAI-compatible ou de qualquer modelo/provider.
- Comportamento sob concorrência entre processos, múltiplos hosts, relógios reais, falhas reais de disco ou do SQLite além das injetadas nos testes.
- Segurança contra código Python hostil no mesmo processo; as garantias são de contrato, não sandbox.
- Captura de runtime real; exige execução real, é proibida por D9 nesta fase e precisa de ticket e aprovação próprios.

## Matriz de compatibilidade sintética

Hipóteses de risco de protocolo e suas recusas, não alegações sobre o DSH. Cada cenário tem teste nomeado `test_matrix_<cenário>` em `tests/deepseek_harness/test_transport.py` e blocker code estável em `BLOCKER_CODES`.

| Cenário | Blocker code | Hipótese exercitada |
|---|---|---|
| `literal_tool_call` | `tool_call_literal` | Chamada de ferramenta emitida como texto literal na mensagem, em vez de frame estruturado. |
| `malformed_tool_call` | `tool_call_malformed` | Argumentos que não são objeto, JSON quebrado, id ausente/duplicado ou resultado para chamada desconhecida. |
| `truncated_frame` | `frame_truncated` | Fim de stream no meio de um frame. |
| `inconsistent_reasoning` | `reasoning_inconsistent` | Raciocínio fora de um turno ou depois da resposta. |
| `timeout` | `transport_timeout` | Transporte sem progresso; o stream fecha e não se recupera. |
| `eof` | `transport_eof` | Fim de stream limpo; nunca conclui o run. |
| `invalid_framing` | `frame_invalid` | JSON inválido, não-objeto, não UTF-8, versão JSON-RPC errada, chaves extras ou duplicadas, constantes não finitas. |
| `unknown_type` | `frame_type_unknown` | Método, tipo de update ou status fora da allowlist, ou request do runtime para o cliente. |

Recusas adicionais do normalizador: `frame_too_large`, `turn_state_invalid`, `session_mismatch`, `tool_not_allowlisted`, `runtime_error` e, depois de qualquer recusa, `stream_blocked`.

## Limites conhecidos e follow-ups

- **Tipo de evento no audit.** Sem mudança de schema (D11), eventos de runtime usam `run.resumed` com `idempotencyKey` `DHE-*`; um envelope genérico de runtime events exigiria ticket próprio.
- **Registry em memória.** `SessionRegistry` vive no processo; após restart, os bindings são reapresentados pelo orquestrador. O audit Pipe ancora a posse de cada attempt auditado pelo `DHD-*`, mas um attempt que nunca chegou ao audit (falha antes do write) só é protegido pelo checkpoint; um registry durável fica para ticket próprio.
- **Bloqueio sem audit.** Se a própria escrita do marcador no audit falhar (qualquer erro de armazenamento), o bloqueio fica só no checkpoint e em memória, e o erro é levantado; uma recusa posterior no mesmo stream tenta persistir o marcador de novo. Qualquer erro de armazenamento nas escritas de audit do adapter vira `audit_write_failed`.
- **Concorrência.** Cada chamada relê o marcador, os eventos auditados do attempt e o checkpoint, então duas instâncias que agem em sequência sobre o mesmo attempt não se contradizem. O spike não prova exclusão mútua entre processos simultâneos: não há lock entre a leitura e a escrita do audit ou do checkpoint. Uma falha na escrita do evento no audit não bloqueia de forma durável: o evento não auditado é descartado no recovery e a retransmissão é aceita, porque nada auditado foi contradito.
- **Preflight é obrigação do orquestrador.** `validate_preflight(start_session=...)` falha antes de criar a sessão, mas `begin`/`drive_session` não exigem prova de preflight; o orquestrador deve criar toda sessão por esse caminho.
- **Tempo informado pelo chamador.** A validade do `ApprovalRecord` é avaliada no `occurred_at` do chamador (mesmo precedente do Hermes), e `drive_session` recebe um `clock` para datar recusas.
- **Diretório de checkpoint pré-existente.** Na construção, um diretório existente com modo diferente de `0700` é corrigido com `fchmod` em vez de recusado; operações seguintes recusam modo errado.
- **Política de repouso.** Só `turn.ended` e `session.idle` são pontos de repouso; qualquer outro último evento (inclusive nenhum evento após o dispatch) torna o resultado desconhecido após restart. É deliberadamente conservador.
- **Handoff não aplica.** A aplicação real continua atrás do boundary governado existente; o spike não liga proposta a `ApplyService`.
- **Subagentes** permanecem fora de escopo (D3).
- Promover a capability, instalar ou executar o DSH exige decisão e ticket próprios; este spike não autoriza nada operacional.

## Como reproduzir

```bash
PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests/deepseek_harness -t . -q
PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests -t . -q
```
