# ADR-003 — Leitura delimitada da descrição de ticket para verificar conformidade

## Record

- ADR ID: ADR-003
- Title: Leitura delimitada da descrição de ticket para verificar conformidade
- Date: 2026-08-06
- Status: Accepted
- Owner: Vitor Natividade (fundador)
- Linear ticket: PIP-842
- PR: #175
- Related architecture review: `docs/connectors/README.md`, `execution/ticket-type-field-matrix.md`
- Supersedes: —
- Superseded by: —

## Context

- **Product ou MVP context:** o contrato de ticket existe como código desde PIP-832 —
  `contracts/ticket-field-matrix.json` define ~44 campos e quais são obrigatórios por tipo, e
  `pipe ticket check` sabe reprovar um corpo que não cumpra. O reconciliador (PIP-834) verifica
  cobertura e ciclo de vida sobre tickets reais.
- **Decision trigger:** a deriva de **contrato** é a única das três que o reconciliador reporta como
  `unavailable`. Não por omissão: os adapters excluem descrição, corpo e comentários por decisão
  registrada em `docs/connectors/README.md`, e o `ExternalSnapshot` sela `rawPayloadPersisted: false`.
  A consequência é que a governança de ~44 campos **é inauditável por construção** — o contrato
  existe e nada consegue verificar se um ticket real o cumpre.
- **Constraints:** a exclusão foi deliberada, não descuido. Qualquer abertura precisa preservar a
  intenção original — o snapshot não é lugar de conteúdo de fonte externa — e continuar valendo para
  todos os outros consumidores.
- **Evidence:** `docs/connectors/README.md` (linha da exclusão); `schemas/ExternalSnapshot.schema.json`
  (`rawPayloadPersisted` é `const: false`, não default); `src/pipe_venture_builder/linear/reconciler.py`
  (`CONTRACT_UNAVAILABLE_REASON`).
- **Human review required:** yes.
- **Approval record:** decisão D5, autorizada pelo fundador em 2026-08-06. O ADR foi exigido como
  pré-condição: nenhuma linha de implementação antes deste documento estar mergeado.

## Options Considered

| Option | Pros | Cons | Why accepted/rejected |
|---|---|---|---|
| **A. Não abrir** | Preserva a fronteira sem exceção. Zero risco novo. | A governança de ~44 campos permanece inauditável para sempre. O contrato de PIP-832 vira decoração: existe, e nada verifica. | **Rejeitada.** O custo é permanente e cresce com o tempo — quanto mais tickets, mais deriva silenciosa. |
| **B. Incluir a descrição no snapshot principal** | Um caminho só, sem código novo. Conformidade sai de graça. | Revoga a decisão original em vez de delimitá-la: conteúdo de fonte externa passa a ser persistido, e `rawPayloadPersisted: false` vira mentira. Todo consumidor do snapshot herda o texto. | **Rejeitada.** Resolve o sintoma destruindo a propriedade. |
| **C. Caminho separado, saída reduzida** | A fronteira do snapshot fica intacta. O texto entra no processo, é avaliado, e **não sai** — o que sai é booleano e nome de campo. | Código a mais. Duas leituras da mesma fonte. Exige disciplina para a saída não crescer. | **Aceita.** É a única que responde à pergunta sem revogar a decisão anterior. |

## Decision

- **Selected option:** C — caminho separado com saída reduzida.

- **Rationale:** a pergunta que a conformidade faz é *"o campo X está presente e não vazio?"*. Isso é
  respondível com um booleano. Persistir o texto para responder um booleano é guardar mil vezes mais
  do que a pergunta precisa — e é essa desproporção que a decisão original evitava.

- **Fronteira, em termos operacionais:**
  1. A descrição é lida por um caminho **próprio**, nunca pelo `ExternalSnapshot`. O snapshot segue
     selando `rawPayloadPersisted: false`, sem exceção e sem asterisco.
  2. O texto atravessa o mesmo `adapters/safety.py` do resto — mesmas guardas de tamanho, de
     identificador e de valor em formato de segredo.
  3. **A saída é apenas booleano e nome de campo.** `{"acceptanceCriteria": false}` é saída válida;
     o conteúdo de `acceptanceCriteria` nunca é.
  4. O texto **não é persistido em lugar nenhum**: nem em snapshot, nem em relatório de reconciliação,
     nem em log, nem em arquivo temporário. Vive na memória do processo pelo tempo da avaliação.
  5. Trecho de conteúdo em mensagem de erro é proibido. Um parser que falha diz *qual seção* não
     conseguiu ler, nunca *o que* estava escrito nela.

- **What this enables:** a deriva de contrato sai de `unavailable` e passa a ser calculável. A
  governança de tipos de ticket deixa de depender de disciplina humana.

- **What this intentionally does not solve:** comentários e corpo de PR continuam **fora**. Este ADR
  abre a descrição de issue, e só ela. Julgar a *qualidade* do conteúdo também fica fora: um ticket
  com `Acceptance Criteria: TBD` continua passando — presença não é qualidade, e um check que tenta
  julgar conteúdo vira ruído e acaba desligado.

## Consequences

- **Positive consequence:** o contrato de ticket vira verificável de ponta a ponta. O relatório diário
  passa a responder as três perguntas em vez de duas.

- **Tradeoff accepted:** mais material atravessa a fronteira do processo do que antes. A mitigação não
  é confiar em quem escreve o código — é a saída ser estruturalmente incapaz de carregar o texto.

- **Risk introduced:** o risco real não é a leitura, é a **erosão**. A saída começa como booleano e,
  algum dia, alguém acha útil incluir "só um trecho para ajudar a depurar". A partir daí a fronteira
  já caiu e ninguém percebeu.

- **Mitigation:** o teste que garante isso não pode ser sobre o caso feliz. Precisa afirmar que a
  saída serializada **não contém** o texto de entrada — um teste com conteúdo-sentinela na descrição
  que falha se a sentinela aparecer em qualquer lugar do relatório. Esse teste é a fronteira; o
  parágrafo acima é só a intenção.

- **Follow-up ticket:** a implementação é ticket próprio e só pode começar depois deste ADR mergeado.

## Review Trigger

Review este ADR quando:

- **a saída precisar carregar conteúdo**, e não só booleano e nome de campo — é o sinal de que a
  decisão está sendo contornada em vez de revista;
- comentários, corpo de PR ou qualquer outro texto de fonte externa forem propostos para o mesmo
  caminho;
- o Linear passar a expor conformidade por API, tornando a leitura desnecessária;
- aparecer P0/P1 de vazamento de conteúdo de fonte externa em log, relatório ou snapshot;
- data ou fase: revisar junto com a próxima revisão de `docs/connectors/README.md`.

## Links

- Linear: PIP-842 (este ADR) · PIP-832 (contrato) · PIP-834 (reconciliador, `CONTRACT_UNAVAILABLE_REASON`)
- PR: #175
- Architecture review: `docs/connectors/README.md`
- KDR/DAR: —
