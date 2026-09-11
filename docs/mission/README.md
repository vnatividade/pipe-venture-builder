# Mission Loop — `Mission`, `MissionStore`, supervisor e `pipe mission`

O Mission Loop transforma uma missão confirmada pelo fundador em trabalho delegado, sem um LLM orquestrador conversando: um **supervisor determinístico em Python** despacha um worker Claude Code headless (`claude -p`) por ciclo num worktree dedicado, verifica o diff de forma mecânica, chama um **revisor de contexto limpo** (só leitura, veredito por JSON schema), roteia, abre o PR e só conclui com evidência de todos os critérios.

- Ticket A (PIP-901): contrato `Mission`, `MissionStore` (SQLite, eventos hash-chained), estados, decisões humanas, evidência e o CLI de estado.
- Ticket B (PIP-902): `worker.py`, `verify.py`, `reviewer.py`, `delivery.py`, `supervisor.py`, `pipe mission supervise|run-once|reconcile` e a skill `/missao` (`.claude/skills/missao/SKILL.md`).
- Ticket C (PIP-903): contrato v0.2.0 com `delegation`, `resolve_decision` com a fonte `delegated:orchestrator`, o supervisor concedendo `grant_cycle` sozinho quando a regra cobre, retry único do revisor em falha de infraestrutura e `delegatedDecisions` em `status`.

Desenho de origem: `10-desenho-mission-loop-mvp.md` (D1–D11; §3 contrato; §4 tabelas; §5 falhas; §7 missão-demo).

## O que é uma Mission

Um documento `Mission` v0.1.0 ou v0.2.0 (`schemas/Mission.schema.json`; contrato imposto em `src/pipe_venture_builder/mission/contract.py`) com:

- `missionId` `MSN-<12hex>`, gerado por `stable_id` só a partir do conteúdo (recriar o mesmo JSON é idempotente; missão nova muda conteúdo ou `version`); `fingerprint` cobre tudo menos `status`, `createdAt`, `updatedAt`, `fingerprint`.
- `successCriteria`: cada critério tem forma verificável — `check` (`command`, `cwd` opcional), `artifact` (`path`, `mustMatch` opcional) ou `rubric` (`question`). Critério sem forma é recusado.
- `delegation` (opcional, exige `schemaVersion: "0.2.0"`; `null` em v0.1.0 e na maioria das missões v0.2.0): só `{"grantCycle": {"maxTimes": 1-3, "maxCostFraction": (0, 0.8], "requireProgress": bool}}` — qualquer outra chave, no nível de `delegation` ou dentro de `grantCycle`, é recusada. Ver "Decisões delegadas" abaixo.
- `constraints`: `maxCycles`, `maxBudgetUsd`, `maxTurnsPerRun` positivos; `productionAllowed`, `secretsAllowed`, `externalCommsAllowed`, `billingAllowed` **têm de ser `false`**. Gates absolutos não são escalados: são recusados na criação.
- `workspace.repo` absoluto, `baseRef`, `writeSet` relativo, não vazio, sem `..`.
- `delivery.kind ∈ {none, pull_request}` e `requireChecks`.
- O documento inteiro passa por `payload_is_safe`; sentinelas secret-shaped são recusadas com mensagem fixa, sem eco do valor.

## Estados e transições

`draft → active`; `active ↔ paused`; `active|paused|blocked → cancelled`; `active → blocked`; `blocked → active` (só sem decisão pendente); `active → completed`; `active|paused|blocked → unknown` **só** por `mark_unknown` (reconciliação). Transição inválida levanta `ControlPlaneStateError` e nada é persistido. `completed`, `cancelled` e `unknown` são terminais.

`complete` exige: cadeia de eventos válida, evidência `satisfied=true` mais recente para **todos** os critérios, nenhuma decisão pendente e, quando `delivery.kind = pull_request`, evento `delivery.pr_opened` (e, se `requireChecks`, o **último** evento `delivery.checks_*` após o último `pr_opened` tem de ser `checks_passed` — uma falha posterior ou um novo `pr_opened` volta a bloquear).

## Eventos

Allowlist fixa em `events.py` (`mission.*`, `run.*`, `verify.*`, `review.*`, `decision.*`, `delivery.*`, `budget.reached`). Cada evento traz `sequence`, `previousHash` e `eventHash = fingerprint(evento sem o hash)`. O payload aceita só identificadores, hashes, contagens, estados e refs: toda string passa por `safe_identifier`, então texto livre, prompt, saída de conversa ou diff não entram. `verify_chain(mission_id)` recomputa a cadeia inteira; `status` expõe `auditChainValid`.

## Decisões humanas

`open_decision(kind ∈ {approval, clarification, escalation, out_of_mission, budget}, context curto, options, safe_default, blocked_scope, deadline)`; pedido pendente idêntico não duplica. `resolve_decision(decision_id, option, decided_by)` exige opção válida e `decided_by` com prefixo `human:chat:`, `human:linear:` ou `human:cli:`, **ou** exatamente `delegated:orchestrator` (ver "Decisões delegadas") — qualquer outra fonte (agente, supervisor por conta própria) é recusada. Silêncio nunca aprova; o `safe_default` é informação para quem decide, não uma resolução automática.

### Decisões delegadas

O fundador pode declarar, na própria missão, um limite dentro do qual o supervisor concede sozinho um pedido rotineiro: `delegation.grantCycle`. É a única coisa delegável hoje — nunca merge, produção, segredos, comunicação externa, billing, orçamento (`kind: budget`) ou um veredito `out_of_mission`.

- `resolve_decision(decision_id, option="grant_cycle", decided_by="delegated:orchestrator")` só é aceito quando a decisão é `kind: escalation` com a opção `grant_cycle`, a missão tem `delegation.grantCycle`, o número de concessões já feitas (`decision.delegated` com `rule: grantCycle`) está abaixo de `maxTimes`, e o custo acumulado dividido por `maxBudgetUsd` está dentro de `maxCostFraction`. Qualquer outra combinação (opção, `kind`, regra ausente, limite estourado) é recusada com `ControlPlaneContractError`/`ControlPlaneStateError` — o mesmo par de exceções que qualquer outra violação de contrato ou de estado.
- Quando aceito, grava o mesmo jeito que qualquer decisão (linha em `decisions`, `status: resolved`), mas o evento é `decision.delegated` (payload `decisionId` + `rule: "grantCycle"`), nunca `decision.resolved` — assim `_max_cycles()` (que já soma decisões resolvidas com `grant_cycle`) e o resto do código continuam sem saber a diferença entre uma concessão humana e uma delegada.
- `requireProgress` (o ciclo que terminou satisfez mais critérios que o anterior; o primeiro compara com zero) é um julgamento por ciclo que só o supervisor tem contexto para fazer — o store não o verifica; é o supervisor que decide se tenta a delegação antes de chamar `resolve_decision`.
- O supervisor tenta a delegação exatamente onde hoje abriria uma decisão `escalation`/`grant_cycle` "de fábrica" (`no_progress`, `review_blocked`, `run_failed`, `delivery_checks_failed`, `max_cycles`, `needs_revision_limit`) — nunca nos casos com outras opções (`branch_mismatch`, `delivery_outside_write_set`, `git_config_tampered`, checks sem resposta) nem em `budget`. Se a regra cobre o caso, resolve a decisão como `delegated:orchestrator`, chama `resume()` e o ciclo seguinte já sai sem pedir nada ao fundador; senão, a decisão fica pendente exatamente como antes do PIP-903. Missões sem `delegation` (ou v0.1.0) se comportam de forma idêntica ao PIP-902.
- `status`/`build_status` expõe `delegatedDecisions`: a contagem de eventos `decision.delegated` da missão.

## Store

`MissionStore(path)`; default `~/.pipe/mission/mission.sqlite3`. WAL, `busy_timeout`, recusa symlink, arquivos `0600`, `schema_version` em `metadata`. Tabelas: `missions`, `mission_events`, `mission_runs`, `decisions`, `criteria_evidence`. Custo acumulado = soma de `cost_usd` dos runs.

Concorrência (follow-up A7 do PIP-901): supervisor e CLI são dois escritores no mesmo arquivo. Todo método mutante abre `BEGIN IMMEDIATE` antes de ler o estado que valida (`resume` inclusive), então um `pause` do fundador espera o lock em vez de comitar entre a checagem e a escrita do supervisor. Testado com duas conexões (`tests/mission/test_store_concurrency.py`).

## CLI

```text
pipe mission create <mission.json> [--store PATH] [--at RFC3339] [--json]
pipe mission show <MSN-id>
pipe mission status <MSN-id> [--home DIR] [--json]   # "Onde estamos / Por quê / O que depende de você"
pipe mission activate|pause|resume|cancel|complete <MSN-id> [--at ...]
pipe mission decisions <MSN-id> [--pending]
pipe mission decide <DEC-id> --option <opção> --by human:chat:<quem>

pipe mission supervise <MSN-id> [--detach] [--claude-bin claude] [--gh-bin gh] [--store PATH]
                       [--home DIR] [--poll-seconds 5] [--worker-model sonnet] [--reviewer-model sonnet]
pipe mission run-once  <MSN-id> [mesmas flags, sem --detach]
pipe mission reconcile <MSN-id> [--store PATH] [--home DIR] [--claude-bin claude]
```

Todos aceitam `--store` (default `~/.pipe/mission/mission.sqlite3`) e `--json`. `--home` é a raiz das pastas por missão (default `~/.pipe/mission`).

Códigos: `MISSION_CONTRACT_VIOLATION` e `MISSION_STATE_CONFLICT` saem com `READINESS_BLOCKED` (9); `MISSION_NOT_FOUND` com `INPUT_UNAVAILABLE` (4); `MISSION_SUPERVISOR_REFUSED` (cadeia inválida, outro supervisor vivo) e `MISSION_SUPERVISOR_ERROR` (falha de `git`/`gh`/processo) com 9. Mensagens são fixas e não ecoam o input.

## Supervisor: o fluxo de um ciclo

`run_once` executa **um** ciclo a partir do estado durável e devolve o próximo estado (`status` da missão + `reason`); `supervise` repete `run_once` até a missão ficar `completed`, `cancelled`, `unknown`, `paused` ou `blocked`, ou até um ciclo terminar esperando decisão (`pending_decisions`) ou um pedido de parada (`interrupted`). A ordem é fixa:

1. **Recusas**: a cadeia de eventos tem de verificar (`auditChainValid`) e nenhum outro supervisor vivo pode ser dono da missão (pid em `supervisor.pid`). Caso contrário, `MISSION_SUPERVISOR_REFUSED` e nada é gravado.
2. **Reconciliação**: run `running` sem supervisor vivo (o anterior morreu com SIGKILL, queda da máquina) vira `run.unknown`; abre decisão `escalation` (`stop`/`revise_mission`, padrão seguro `stop`) e a missão vai para `unknown` (terminal). **Nada é re-executado**: um run de resultado desconhecido pode ter tido efeito.
3. **Estado**: só missão `active` e sem decisão pendente segue.
4. **Orçamento**: custo acumulado = soma de `cost_usd` de todos os runs (worker **e** revisor), lido de `total_cost_usd` do JSON do Claude Code. O worker recebe `--max-budget-usd` = `maxBudgetUsd` − custo − reserva do revisor (US$ 1,50); se isso ficar abaixo de US$ 1,50, `budget.reached` + `mission.blocked` + decisão `budget`. Antes do revisor, o restante tem de ser ≥ US$ 1,50.
5. **Worktree**: `git worktree add <home>/<MSN-id>/worktree -b claude/<MSN-id>-<slug> <baseRef>` (idempotente; reusa a branch se existir). Um caminho existente só é reaproveitado se for o topo de um worktree de `workspace.repo` (mesmo `--git-common-dir`) na branch da missão; qualquer outra coisa com conteúdo (diretório dentro de outro repositório, worktree de outro repo ou de outra branch) → erro, nada roda.
6. **Worker**: `claude -p <brief> --output-format json --max-turns <maxTurnsPerRun> --max-budget-usd <restante> --permission-mode acceptEdits --permission-prompts none --allowedTools "Read,Edit,Write,Grep,Glob,Bash(git status*),Bash(git diff*),Bash(git log*),Bash(git show*),Bash(ls *),Bash(<cada check>)" --setting-sources project --strict-mcp-config --disallowedTools <deny-list> --append-system-prompt <regras fixas> --model <worker-model>`, stdin de `/dev/null`, contexto novo por ciclo (nunca `--resume`, nunca `--bare`). Ver "Isolamento do worker e do revisor" abaixo. O ambiente é herdado do supervisor (o `claude` autentica pelo login local); o supervisor não acrescenta segredo. Enquanto roda, o store é lido a cada `--poll-seconds`: `paused`/`cancelled` → SIGTERM ao grupo do processo (SIGKILL ao grupo após 10 s se o `claude` não sair) → `run.interrupted` → fim. Depois que o `claude` sai, por qualquer motivo (fim normal, pausa, timeout), o que restou do grupo recebe SIGKILL: um neto que ignora SIGTERM não sobrevive ao run.
7. **Config git**: antes de cada run do worker o supervisor tira um snapshot (só hashes) de `git config --local --list` e `git config --worktree --list` (quando o git aceita) no checkout principal e no worktree, e compara depois do run. Divergência → `mission.blocked` com `git_config_tampered` + decisão `escalation` (`stop`/`restore_and_resume`), sem verificar, revisar, commitar nem fazer push; o diff desse run nunca é entregue (um run coletado fica com `review.blocked`), então a retomada despacha um worker novo — restaure a config antes de retomar. Um worktree grava na config **comum** do checkout principal, e o supervisor roda `git commit`/`git push` com essa config (hooks, `core.sshCommand`, `remote.origin.url`).
8. **Coleta**: `session_id`, `total_cost_usd`, `num_turns`, `subtype` e contagem de `permission_denials` vão para o evento `run.*`; `subtype` de erro (`error_max_turns`, `error_max_budget_usd`…) ou resultado sem o JSON do worker → run `failed` com `reason`.
9. **Roteamento do worker**: `failed` → próximo ciclo (no último, `blocked` + decisão); `done:false` com `blockers` → decisão `clarification` + `paused` (padrão seguro `pause`). **Negação de permissão não é veredito**: o ciclo segue para a verificação e o revisor como qualquer outro (na demo MSN-4a06360ef387 o worker fez o trabalho certo e teve `ls`/`node --test` negados). As chamadas negadas (`WebFetch`, `Bash(<comando>)`) e a lista de ferramentas permitidas só entram no arquivo de revisão se o ciclo terminar em `needs_revision`, depois das instruções.
10. **Verificação determinística** (antes de gastar revisor): HEAD tem de estar na branch da missão (senão `blocked` `branch_mismatch`); circuit breaker — mesmo `diffFingerprint` do ciclo anterior → `blocked` (`no_progress`) + decisão; arquivo fora do write set (`git diff --name-only --no-renames <baseRef>...HEAD` + `git status --porcelain --no-renames`: um rename conta origem **e** destino) → `verify.failed` + `review.needs_revision` **sem revisor**; critérios `check` (exit 0, teto 600 s) e `artifact` gravam evidência e, se algum falha, `needs_revision` sem revisor.
11. **Revisor** (contexto limpo): `claude -p` com a missão + diff, `--json-schema` do veredito, `--permission-mode plan`, `--allowedTools "Read,Grep,Glob,Bash(git diff *),Bash(git log *)"`, as mesmas `--setting-sources project --strict-mcp-config --disallowedTools <deny-list>` do worker, `--max-turns 20`, `--model <reviewer-model>`. Uma falha de infraestrutura (`reviewer_run_failed`: o run não terminou `collected`; `reviewer_output_invalid`: terminou mas sem um veredito válido no schema) não é um julgamento — ganha **uma** nova tentativa de revisão, sem novo worker, sobre o mesmo diff; se a segunda tentativa falhar do mesmo jeito, aí sim vira `blocked`. Um veredito `blocked` que o próprio revisor devolveu (run válido, JSON válido, `verdict: "blocked"`) nunca é repetido. Rubrics viram evidência. `satisfied` sem evidência de todos os critérios é rebaixado a `blocked`.
12. **Rotas**: `satisfied` → entrega; `needs_revision` → próximo ciclo com as instruções (no ciclo `maxCycles`: `blocked` + decisão); `out_of_mission` → `paused` + decisão `out_of_mission` (padrão seguro `pause`); `blocked` → `blocked` + decisão.
13. **Entrega** (`delivery.kind = pull_request`): imediatamente antes do commit do supervisor e de novo antes do push, HEAD tem de estar na branch da missão (`branch_mismatch`) e `changed_files` é refeito contra o write set (`delivery_outside_write_set`); qualquer falha → `blocked` + decisão (`stop`/`fix_and_resume`), sem commit, push nem PR. Depois: commit do que o worker deixou no worktree, `git push origin HEAD:refs/heads/<branch>` (publica o HEAD verificado, nunca a ref local pelo nome), `gh pr create` **uma vez por branch** (consulta `gh pr list --head` antes; o evento `delivery.pr_opened` também não se repete), e polling de `gh pr checks` a cada 30 s por até 60 leituras. `passed` → `delivery.checks_passed` → `complete()`; `failed` → `delivery.checks_failed` + `needs_revision` no próximo ciclo; sem resposta no teto → `blocked` (`delivery_checks_timeout`) + decisão `stop`/`keep_waiting`. Com `delivery.kind = none`, conclui após o revisor.

`complete()` continua exigindo, no store, evidência `satisfied` de todos os critérios, cadeia válida, nenhuma decisão pendente e, para PR, `checks_passed` depois do último `pr_opened`.

### Decisões que o supervisor abre

| Situação | `kind` | Estado | Opções (padrão seguro primeiro) |
|---|---|---|---|
| run órfão | `escalation` | `unknown` | `stop`, `revise_mission` |
| orçamento | `budget` | `blocked` | `stop`, `revise_mission` |
| limite de ciclos (`needs_revision_limit`, `run_failed`, `delivery_checks_failed`, `max_cycles`), `no_progress`, `review_blocked` | `escalation` | `blocked` (ou concedida sozinha — ver "Decisões delegadas" — e a missão continua `active`) | `stop`, `grant_cycle` |
| checks sem resposta | `escalation` | `blocked` | `stop`, `keep_waiting` |
| config git alterada durante o worker (`git_config_tampered`) | `escalation` | `blocked` | `stop`, `restore_and_resume` |
| HEAD fora da branch da missão (`branch_mismatch`), diff fora do write set na entrega (`delivery_outside_write_set`) | `escalation` | `blocked` | `stop`, `fix_and_resume` |
| worker com `blockers` | `clarification` | `paused` | `pause`, `retry` |
| revisor `out_of_mission` | `out_of_mission` | `paused` | `pause`, `retry_within_mission` |

O supervisor não age sobre a opção escolhida, com uma exceção: cada decisão resolvida com `grant_cycle` (por um humano ou, dentro da regra declarada, por `delegated:orchestrator`) concede um ciclo além de `maxCycles`. Para continuar depois de uma decisão humana: `pipe mission resume <id>` e `pipe mission supervise <id> --detach`; uma decisão delegada já resume e segue sozinha, dentro do mesmo `supervise`.

## Pausar, cancelar, retomar

- `pipe mission pause <id>`: o supervisor vê o estado em ≤ `--poll-seconds` (padrão 5 s), SIGTERM ao worker, `run.interrupted`, e termina. Nada novo parte enquanto `paused`.
- `pipe mission resume <id>` + `pipe mission supervise <id> --detach`: o mesmo ciclo é retomado com `attempt` novo (a pausa não consome ciclo). Se a pausa veio durante o revisor, só a revisão é refeita.
- `pipe mission cancel <id>`: igual à pausa, mas terminal.
- SIGTERM/SIGINT/SIGHUP no próprio supervisor (`supervise` e `run-once`; SIGHUP chega quando o terminal de um `supervise` em primeiro plano fecha): termina o worker, registra `run.interrupted` e sai com a missão `active` (retomável).
- Supervisor morto com SIGKILL (ou queda): o worker roda em sessão própria e **continua vivo**, editando o worktree. `status` mostra `supervisor.alive=false` e um run `running`; `pipe mission reconcile <id> [--claude-bin <o mesmo do supervise>]` (ou o próximo `supervise`/`run-once`) primeiro encerra o worker (SIGTERM ao grupo, SIGKILL após 5 s) — só se o pid de `worker.pid` ainda for líder de sessão rodando `<claude-bin> -p`, para não matar um processo que herdou o pid —, depois marca o run `unknown` (`workerKilled` no evento) e abre decisão.

## Onde ficam as coisas

| O quê | Onde |
|---|---|
| Store | `~/.pipe/mission/mission.sqlite3` (0600, WAL) |
| Pid do supervisor | `~/.pipe/mission/<MSN-id>/supervisor.pid` — o mesmo arquivo que `status` lê para `supervisor.alive`; fica após a saída (então `alive=false`) |
| Log | `~/.pipe/mission/<MSN-id>/supervisor.log` — uma linha por evento, só ids, códigos e contagens; com `--detach`, stdout/stderr do supervisor também vão para ele |
| Worktree | `~/.pipe/mission/<MSN-id>/worktree`, branch `claude/<MSN-id>-<slug>` |
| Pid do worker em execução | `~/.pipe/mission/<MSN-id>/worker.pid` (removido ao fim do run) |
| Instruções de revisão do ciclo *n* | `~/.pipe/mission/<MSN-id>/revisions/cycle-<n>.md` (0600): texto do revisor, arquivos fora do write set, ferramentas negadas. Nunca no SQLite |

## O que nunca vai para o SQLite

Brief, prompt do revisor, texto de resultado do worker ou do revisor, diff e saída de comandos. O store guarda só ids (`sessionId`, `runId`), hashes (`resultFingerprint`, `diffFingerprint`), contagens, códigos (`reason`, `subtype`, modelo) e refs (URL do PR). Toda string de evento passa por `safe_identifier`; `collect_run(extra=...)` não aceita texto livre nem sobrescreve campos fixos. Testado varrendo o arquivo SQLite (e `-wal`) por uma sentinela do worker e do revisor. O `diffFingerprint` é o hash de um diff único da merge-base com `baseRef` até a working tree (mais arquivos não rastreados): commitar o mesmo conteúdo não o altera.

## Isolamento do worker e do revisor

O worker roda sem ninguém para responder a um pedido de permissão (`--permission-prompts none`), então o que ele pode fazer é só o que as flags liberam:

- **Sem as configurações do usuário**: `--setting-sources project` (as regras de allow e os hooks de `~/.claude/settings.json` — por exemplo `gh pr merge *`, `railway up *` — não se aplicam; `--allowedTools` **soma** às regras das fontes carregadas, não as substitui) e `--strict-mcp-config` sem `--mcp-config` (nenhum servidor MCP). Medido com o CLI real 2.1.267: sem isolamento o worker executou `gh pr review --help`; com as flags, negado, e a autenticação continua funcionando.
- **Pode**: `Read`, `Edit`, `Write`, `Grep`, `Glob`, `git status|diff|log|show`, `ls` e exatamente os comandos dos critérios `check`. Deixa as mudanças no worktree; quem commita é o supervisor, depois de verificar.
- **Não pode** (`--disallowedTools`; negar vence permitir, inclusive regras que viessem das settings do projeto): `gh`, `railway`, `git push|config|remote|-c|-C|checkout|switch|reset|worktree|commit|add|rebase|merge`, `curl`, `wget`, `WebFetch`, `WebSearch`. Qualquer outro comando também é negado (não está no allow). O brief e as regras fixas dizem isso ao worker.
- **O que o supervisor confere depois**: config git (snapshot antes/depois), branch do HEAD, write set sem detecção de rename, e de novo branch e write set antes do commit e antes do push.

O revisor recebe as mesmas flags de isolamento e o mesmo deny-list, com `--permission-mode plan` e allow só de leitura.

## Limites

- **Sem merge automático.** O supervisor abre o PR e espera os checks; o merge é do fundador.
- **Sem Linear por código.** O handoff no Linear segue pelo MCP no chat (skill `/missao`).
- **Um escritor por vez.** Um supervisor por missão (pid); um worker por vez; nada de workers em paralelo.
- **Custo medido, não estimado**: `costUsd` é a soma de `total_cost_usd` reportado pelo `claude -p` de cada run. Run morto sem JSON conta US$ 0 (o custo real é desconhecido) e run reconciliado como `unknown` também.
- **Pid pode ser reutilizado** pelo sistema depois que o supervisor morre; se `status` disser `alive=true` sem supervisor, apague `supervisor.pid`. O `reconcile` só mata o pid de `worker.pid` se ele ainda for líder de sessão rodando `<claude-bin> -p`; o SIGKILL ao grupo depois que o líder sai tem a mesma janela teórica de reuso (o id de um grupo vazio pode voltar a existir).
- **Neto que sai do grupo escapa**: um processo que o worker inicie com `setsid` (sessão nova) não recebe o SIGTERM/SIGKILL do grupo na pausa, no timeout nem no `reconcile`. Não há solução simples no macOS; confira `ps -g <pgid>` depois de uma pausa se suspeitar.
- **`git diff` do allow aceita `--output=<arquivo>`** (grava um arquivo); dentro do worktree isso aparece no write set, fora dele depende das regras de escrita do Claude Code. Não verificado com o CLI real.
- **Só o pid do worker é gravado**: um revisor que fique vivo depois de um SIGKILL no supervisor não é encerrado pelo `reconcile` (ele é só leitura, mas gasta).
- **`unknown` é terminal**: continuar exige uma missão nova (`version` nova ou outro conteúdo).
- **Rede**: só a do supervisor (`git push`, `gh`), com as credenciais e a conta `gh` ativas da máquina. O worker não tem `gh`, `git push`, `curl`, `wget`, `WebFetch` nem `WebSearch`, mas herda o ambiente do supervisor; não rode o supervisor num shell com segredos exportados que o worker não deva ver.
- Evidência não gera evento próprio (allowlist fixa); fica em `criteria_evidence` e é lida por `status`/`complete`.
- O que o Pipe já governa (`AGENTS.md`, approval gates) continua valendo por cima.

## Testes

Só executáveis falsos (`tests/mission/fakes/fake_claude.py`, `fake_gh.py`); nenhum `claude` ou `gh` real. As falhas §5 do desenho têm teste nomeado em `tests/mission/test_supervisor.py` (`test_f1_…` a `test_f9_…`), mais circuit breaker, blockers, negação de permissão (não é veredito), PR idempotente, checks, sentinela fora do SQLite, escritor único, config git adulterada, rename de arquivo restrito, netos na pausa (inclusive o que ignora SIGTERM), `reconcile` com worker vivo (e o controle com pid de outro processo), branch e write set na entrega; o `--detach` real, o SIGHUP no `run-once` e o SIGKILL no `supervise` seguido de `reconcile` estão em `tests/mission/test_supervisor_cli.py`. As flags de isolamento e o deny-list são fixados literalmente em `test_worker.py`/`test_reviewer.py`.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests/mission -t . -q
```
