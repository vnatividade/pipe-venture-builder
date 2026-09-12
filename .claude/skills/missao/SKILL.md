---
name: missao
description: Entrada pelo chat para o Mission Loop do Pipe. Use quando o fundador disser "quero fazer X", "tenho a dor X" ou "delega isso": conduz o refinamento pelo front door do Pipe, decide entre UMA missão e um PROGRAMA de ondas encadeadas, grava com critérios verificáveis, confirma com o fundador e inicia o supervisor em background. Nunca começa a executar sem a confirmação.
---

# /missao — do chat à missão delegada

Referência completa: `docs/mission/README.md`. Os comandos abaixo usam `pipe`; se não estiver no PATH, use `.venv/bin/pipe` na raiz do repositório (ou `PYTHONPATH=src .venv/bin/python -m pipe_venture_builder` dentro de um worktree ainda não mergeado).

## 0. Uma missão ou um programa?

Decida a forma **depois do refinamento e antes de escrever critério**. A pergunta que decide não é "isso é grande?" — é: **consigo escrever, hoje, um critério verificável para o resultado final?**

**Uma missão**, quando as três forem verdade: o resultado cabe num write set que você lista agora; todo critério já tem forma verificável hoje (`check`/`artifact`/`rubric`); nenhum critério depende de decisão que ainda não foi tomada.

**Um programa**, quando qualquer uma aparecer:

1. **Um critério só fica escrevível depois de outro trabalho.** "A tela mostra os lançamentos" não é verificável antes de existir esquema. O sinal é você se pegar escrevendo um `rubric` vago porque o `check` ainda não tem como existir.
2. **Há portão humano no meio** — direção de design, escolha de arquitetura, aprovação de escopo. Isso não é "revisão do PR": é decisão do fundador no meio do caminho.
3. **O write set muda de natureza** (documento → migration → tela). Um write set que cobre os três não protege nada.
4. **Etapas pedem executores diferentes** (onda mecânica pode ir para modelo local; arquitetura, não).
5. **O fundador já descreveu em ondas.** Se ele falou "primeiro X, depois Y", não achate isso numa missão só.

Na dúvida, **programa de duas ondas** é a escolha segura: o custo do erro é um PR a mais, contra uma missão que trava no meio. **Tamanho de diff sozinho nunca justifica programa.**

Se for missão única, siga dos passos 1 a 9. Se for programa, siga o passo 10 — que usa os passos 1 a 3 para cada onda.

1. **Refinar** (front door do Pipe, `execution/conversational-founder-guide.md`): uma pergunta por vez até ter usuário, problema, evidência, resultado esperado, não-escopo e o que é reservado ao fundador. Não transforme dor em software automaticamente.
2. **Traduzir em critérios verificáveis**: cada critério vira `check` (comando cujo exit 0 prova), `artifact` (arquivo que deve existir e casar `mustMatch`) ou `rubric` (pergunta sim/não para o revisor). Se um critério não tem forma verificável, pergunte ao fundador como ele saberia que ficou pronto. Defina também `workspace.repo` (caminho absoluto), `baseRef` (ex.: `origin/main`, depois de `git fetch`), `writeSet` (só os arquivos que podem mudar), `delivery` (`pull_request` com `requireChecks: true`, ou `none`) e `constraints` (`maxCycles`, `maxBudgetUsd` ≥ 3 por ciclo, `maxTurnsPerRun`; os quatro `*Allowed` são sempre `false`).
3. **Delegar o rotineiro (`schemaVersion: "0.2.0"`)**: por padrão, escreva `delegation: {"grantCycle": {"maxTimes": 1, "maxCostFraction": 0.6, "requireProgress": true}}`. Com isso o supervisor concede sozinho **só** mais um ciclo além de `maxCycles`, e só quando a missão bate o limite de ciclos (`max_cycles` ou `needs_revision_limit`), no máximo `maxTimes` vezes, e só se o custo acumulado estiver em até `maxCostFraction` do `maxBudgetUsd` (0.6 = até 60% gasto) e o ciclo que acabou tiver satisfeito mais critérios que o anterior. A decisão aparece como `decision.delegated` e em `delegatedDecisions` no `status`. Revisor que responde `blocked`, falha repetida do revisor, missão sem progresso, run que falhou e checks da entrega falhando continuam chegando ao fundador, com ou sem a regra. Nada além de `grant_cycle` é delegável: nunca merge, produção, segredos, comunicação externa, billing, orçamento, `clarification`, config git alterada ou veredito `out_of_mission` (ver "Decisões delegadas" em `docs/mission/README.md`). Avise o fundador desse padrão em uma frase; se ele preferir decidir cada ciclo pessoalmente, grave `delegation: null`.
4. **Gravar**: `mkdir -p ~/.pipe/mission/drafts`, escreva o JSON (`schemas/Mission.schema.json`) em `~/.pipe/mission/drafts/<slug>.json` e rode `pipe mission create <arquivo> --json`. Mostre ao fundador um resumo na linguagem dele: objetivo, critérios, o que é delegável, o que fica com ele, orçamento e ciclos. `pipe mission show <MSN-id>` imprime o documento gravado.
5. **Confirmar**: só após o "vai" explícito do fundador, `pipe mission activate <MSN-id> --json` e `pipe mission supervise <MSN-id> --detach --json` (modelos: `--worker-model sonnet --reviewer-model sonnet` por padrão). Informe o id, o pid e como acompanhar: `pipe mission status <MSN-id>`. O supervisor roda em sessão própria e sobrevive ao fechamento do chat; pid e log ficam em `~/.pipe/mission/<MSN-id>/supervisor.pid|supervisor.log`.
6. **Enquanto roda**: não fique perguntando "ainda quer?"; responda perguntas com `pipe mission status <MSN-id>` (texto: onde estamos, por quê, o que depende de você; `--json` para detalhes, inclusive `supervisor.alive` e `delivery.pullRequest`).
7. **Decisões**: o supervisor para (e o processo termina) quando a missão fica `paused` ou `blocked` ou quando há decisão pendente. Liste com `pipe mission decisions <MSN-id> --pending`; apresente contexto, opções, `safeDefault` e prazo; registre a resposta do fundador com `pipe mission decide <DEC-id> --option <opção> --by human:chat:<sessionId>`. Nunca decida pelo fundador: silêncio não aprova e a sua mensagem não é consentimento. A única exceção é a concessão de ciclo que a própria missão delegou em `delegation.grantCycle`: quem a faz é o supervisor, sozinho e dentro dos limites; você não usa `delegated:orchestrator` no `decide`, apenas relata a concessão ao fundador. Para continuar: `pipe mission resume <MSN-id>` e de novo `pipe mission supervise <MSN-id> --detach`. A opção `grant_cycle` concede um ciclo além de `maxCycles`; `stop` deixa a missão parada (encerre com `cancel` se o fundador quiser); `revise_mission` pede uma versão nova da missão (novo `create`). `restore_and_resume` (config git do repositório mudou durante o worker) e `fix_and_resume` (HEAD fora da branch da missão ou diff fora do write set na entrega) pedem que alguém confira e corrija o repositório/worktree antes do `resume`; mostre ao fundador o que mudou (`git config --local --list`, `git -C ~/.pipe/mission/<MSN-id>/worktree status`) e não corrija sem o aval dele.
8. **Pausar/cancelar**: `pipe mission pause <MSN-id>` ou `pipe mission cancel <MSN-id>`. O supervisor lê o estado a cada `--poll-seconds` (padrão 5 s), envia SIGTERM ao worker e registra `run.interrupted`. Confirme com `status` que `supervisor.alive` virou `false` e que nenhum run novo partiu. Se o supervisor morreu sem registrar o fim de um run, `status` mostra run `running` com `supervisor.alive=false` — e o worker pode continuar vivo, editando o worktree (roda em sessão própria): rode `pipe mission reconcile <MSN-id>` (com `--claude-bin` igual ao do `supervise`, se não foi o padrão `claude`). Ele encerra o worker se o pid de `~/.pipe/mission/<MSN-id>/worker.pid` ainda for do `claude -p`, marca o run `unknown` (o evento diz `workerKilled`), abre decisão; nada é re-executado. Se `workerAlive` vier `true` com `workerKilled` `false`, confira o processo com `ps -p <pid>` antes de concluir que acabou.
9. **Entrega**: quando `status` mostrar `completed`, apresente o PR (`delivery.pullRequest`), as evidências por critério e o custo (`costUsd`, soma de `total_cost_usd` de worker e revisor). Merge é decisão do fundador; o supervisor nunca faz merge e não escreve no Linear — o handoff no Linear é feito por você, pelo MCP, citando o `missionId`.

## 10. Programa: a dor em ondas encadeadas

Objeto `PRG-`, acima da missão, com a mesma disciplina (SQLite, eventos encadeados por hash, decisões tipadas). Contrato em `schemas/Program.schema.json`.

**Como quebrar em ondas.** Uma onda é **uma entrega verificável por fora**. O teste da fronteira: *consigo provar que a onda terminou sem abrir o código que ela escreveu?* Se não, ou a onda é grande demais, ou o critério é opinião. Cada onda entrega artefato, não progresso ("começar o esquema" não é onda; "`docs/esquema.md` com todas as entidades" é). `dependsOn` é **grafo, não fila** — duas ondas que dependem da mesma anterior e não dependem entre si não devem ser serializadas. Mire 1 a 3 dias de trabalho por onda.

**`startWhen` — o portão que responde "o que garante concluir uma onda e começar a próxima".** Não é "a missão anterior disse que terminou": missão que termina só afirma que os critérios *dela* passaram, medidos por ela. `startWhen` é a mesma evidência conferida **de novo, do zero**, num worktree descartável da base da onda. Regras:

- Só `check` ou `artifact`. **Nunca `rubric`** — o schema recusa. Se o portão precisa de julgamento, o que você quer é `requiresFounder: true`.
- Escreva o `startWhen` da onda N+1 olhando para **a entrega da onda N** ("o que a anterior tinha que deixar pronto?"), não para o que a N+1 vai precisar.
- **Um `startWhen` que passaria num repositório sem a onda anterior está quebrado.** Antes de gravar, rode o comando no `main` de hoje e confirme que ele **falha**. Se `pytest -q` passa em repo vazio, ele não prova nada.
- Quando a onda anterior produz documento, o `mustMatch` cita o conteúdo específico (cada entidade, cada id de requisito), não só o nome do arquivo.

Insatisfeito → o programa **bloqueia**, abre decisão `escalation` (`stop`/`revise_stage`) e **nenhuma missão é criada**.

**Encadeamento por branch, e o limite que vem junto.** A onda 1 nasce de `workspace.baseRef`; uma onda com dependência nasce da **branch da missão** da onda de `chainFrom`. O programa **nunca mergeia**. Consequência que precisa ser dita ao fundador: uma onda enxerga só a sua `chainFrom`, então um `startWhen` que cobra a entrega de *outra* dependência paralela **bloqueia** — e isso está certo. Para reconvergir, ou serialize as ondas, ou o fundador mergeia.

**Estrutura de cada onda** (`stages[]`): `id`, `missionDraft` (o documento da missão **sem** `missionId`/`status`/timestamps/`fingerprint`, e cujo `workspace` declara **só** `writeSet` — repo e `baseRef` o programa resolve), `dependsOn`, `chainFrom` (obrigatório com mais de uma dependência, e tem que estar em `dependsOn`), `startWhen`, `requiresFounder`, `execution` (`workerModel`/`reviewerModel`, opcionais).

**Comandos** (conferidos contra o CLI):

```
mkdir -p ~/.pipe/mission/drafts
pipe program create ~/.pipe/mission/drafts/<slug>.json --json
pipe program show <PRG-id> --json
pipe program activate <PRG-id> --json
pipe program supervise <PRG-id> --detach --json
pipe program status <PRG-id>          # --json traz o objeto inteiro em `status`
pipe program decisions <PRG-id> --pending --json
pipe program pause|resume|cancel <PRG-id> --json
```

Decisão de programa se resolve com **`pipe mission decide <DEC-id> --option <opção> --by human:chat:<sessionId>`** — não existe `program decide`; o verbo é o mesmo porque a decisão é identificada pelo `DEC-id`, e o sujeito pode ser `MSN-` ou `PRG-`.

**Ao acompanhar**, nunca responda "o programa está rodando". Diga sempre: **qual onda está rodando, qual foi a última concluída, e qual `startWhen` está bloqueando**, se houver.

**O que NÃO muda com o programa** — diga isto ao fundador em uma frase ao apresentar: o programa não mergeia nada (cada onda entrega por PR com CI verde, merge continua dele); o que é delegável continua o de `delegation`; gates absolutos continuam do fundador; missão parada por decisão **para** o programa; estouro de orçamento **bloqueia** e abre decisão (`resume` só depois de resolver), nunca corta escopo sozinho; `doneWhen` só é avaliado depois de todas as ondas, contra as folhas do grafo.
