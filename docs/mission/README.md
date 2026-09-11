# Mission Loop — `Mission`, `MissionStore`, supervisor e `pipe mission`

O Mission Loop transforma uma missão confirmada pelo fundador em trabalho delegado, sem um LLM orquestrador conversando: um **supervisor determinístico em Python** despacha um worker Claude Code headless (`claude -p`) por ciclo num worktree dedicado, verifica o diff de forma mecânica, chama um **revisor de contexto limpo** (só leitura, veredito por JSON schema), roteia, abre o PR e só conclui com evidência de todos os critérios.

- Ticket A (PIP-901): contrato `Mission`, `MissionStore` (SQLite, eventos hash-chained), estados, decisões humanas, evidência e o CLI de estado.
- Ticket B (PIP-902): `worker.py`, `verify.py`, `reviewer.py`, `delivery.py`, `supervisor.py`, `pipe mission supervise|run-once|reconcile` e a skill `/missao` (`.claude/skills/missao/SKILL.md`).

Desenho de origem: `10-desenho-mission-loop-mvp.md` (D1–D11; §3 contrato; §4 tabelas; §5 falhas; §7 missão-demo).

## O que é uma Mission

Um documento `Mission` v0.1.0 (`schemas/Mission.schema.json`; contrato imposto em `src/pipe_venture_builder/mission/contract.py`) com:

- `missionId` `MSN-<12hex>`, gerado por `stable_id` só a partir do conteúdo (recriar o mesmo JSON é idempotente; missão nova muda conteúdo ou `version`); `fingerprint` cobre tudo menos `status`, `createdAt`, `updatedAt`, `fingerprint`.
- `successCriteria`: cada critério tem forma verificável — `check` (`command`, `cwd` opcional), `artifact` (`path`, `mustMatch` opcional) ou `rubric` (`question`). Critério sem forma é recusado.
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

`open_decision(kind ∈ {approval, clarification, escalation, out_of_mission, budget}, context curto, options, safe_default, blocked_scope, deadline)`; pedido pendente idêntico não duplica. `resolve_decision(decision_id, option, decided_by)` exige opção válida e `decided_by` com prefixo `human:chat:`, `human:linear:` ou `human:cli:` — qualquer outra fonte (agente, supervisor) é recusada. Silêncio nunca aprova; o `safe_default` é informação para quem decide, não uma resolução automática.

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
pipe mission reconcile <MSN-id> [--store PATH] [--home DIR]
```

Todos aceitam `--store` (default `~/.pipe/mission/mission.sqlite3`) e `--json`. `--home` é a raiz das pastas por missão (default `~/.pipe/mission`).

Códigos: `MISSION_CONTRACT_VIOLATION` e `MISSION_STATE_CONFLICT` saem com `READINESS_BLOCKED` (9); `MISSION_NOT_FOUND` com `INPUT_UNAVAILABLE` (4); `MISSION_SUPERVISOR_REFUSED` (cadeia inválida, outro supervisor vivo) e `MISSION_SUPERVISOR_ERROR` (falha de `git`/`gh`/processo) com 9. Mensagens são fixas e não ecoam o input.

## Supervisor: o fluxo de um ciclo

`run_once` executa **um** ciclo a partir do estado durável e devolve o próximo estado (`status` da missão + `reason`); `supervise` repete `run_once` até a missão ficar `completed`, `cancelled`, `unknown`, `paused` ou `blocked`, ou até um ciclo terminar esperando decisão (`pending_decisions`) ou um pedido de parada (`interrupted`). A ordem é fixa:

1. **Recusas**: a cadeia de eventos tem de verificar (`auditChainValid`) e nenhum outro supervisor vivo pode ser dono da missão (pid em `supervisor.pid`). Caso contrário, `MISSION_SUPERVISOR_REFUSED` e nada é gravado.
2. **Reconciliação**: run `running` sem supervisor vivo (o anterior morreu com SIGKILL, queda da máquina) vira `run.unknown`; abre decisão `escalation` (`stop`/`revise_mission`, padrão seguro `stop`) e a missão vai para `unknown` (terminal). **Nada é re-executado**: um run de resultado desconhecido pode ter tido efeito.
3. **Estado**: só missão `active` e sem decisão pendente segue.
4. **Orçamento**: custo acumulado = soma de `cost_usd` de todos os runs (worker **e** revisor), lido de `total_cost_usd` do JSON do Claude Code. O worker recebe `--max-budget-usd` = `maxBudgetUsd` − custo − reserva do revisor (US$ 1,50); se isso ficar abaixo de US$ 1,50, `budget.reached` + `mission.blocked` + decisão `budget`. Antes do revisor, o restante tem de ser ≥ US$ 1,50.
5. **Worktree**: `git worktree add <home>/<MSN-id>/worktree -b claude/<MSN-id>-<slug> <baseRef>` (idempotente; reusa a branch se existir).
6. **Worker**: `claude -p <brief> --output-format json --max-turns <maxTurnsPerRun> --max-budget-usd <restante> --permission-mode acceptEdits --permission-prompts none --allowedTools "Read,Edit,Write,Grep,Glob,Bash(git *),Bash(<cada check>)" --append-system-prompt <regras fixas> --model <worker-model>`, stdin de `/dev/null`, contexto novo por ciclo (nunca `--resume`, nunca `--bare`). O ambiente é herdado do supervisor (o `claude` autentica pelo login local); o supervisor não acrescenta segredo. Enquanto roda, o store é lido a cada `--poll-seconds`: `paused`/`cancelled` → SIGTERM ao grupo do processo (SIGKILL após 10 s) → `run.interrupted` → fim.
7. **Coleta**: `session_id`, `total_cost_usd`, `num_turns`, `subtype` e contagem de `permission_denials` vão para o evento `run.*`; `subtype` de erro (`error_max_turns`, `error_max_budget_usd`…) ou resultado sem o JSON do worker → run `failed` com `reason`.
8. **Roteamento do worker**: `failed` → próximo ciclo (no último, `blocked` + decisão); `done:false` com `blockers` → decisão `clarification` + `paused` (padrão seguro `pause`); `permission_denials` → `needs_revision` com a instrução "a ferramenta X foi negada; não a use".
9. **Verificação determinística** (antes de gastar revisor): circuit breaker — mesmo `diffFingerprint` do ciclo anterior → `blocked` (`no_progress`) + decisão; arquivo fora do write set → `verify.failed` + `review.needs_revision` **sem revisor**; critérios `check` (exit 0, teto 600 s) e `artifact` gravam evidência e, se algum falha, `needs_revision` sem revisor.
10. **Revisor** (contexto limpo): `claude -p` com a missão + diff, `--json-schema` do veredito, `--permission-mode plan`, `--allowedTools "Read,Grep,Glob,Bash(git diff *),Bash(git log *)"`, `--max-turns 20`, `--model <reviewer-model>`. Veredito inválido ou run com erro = `blocked`. Rubrics viram evidência. `satisfied` sem evidência de todos os critérios é rebaixado a `blocked`.
11. **Rotas**: `satisfied` → entrega; `needs_revision` → próximo ciclo com as instruções (no ciclo `maxCycles`: `blocked` + decisão); `out_of_mission` → `paused` + decisão `out_of_mission` (padrão seguro `pause`); `blocked` → `blocked` + decisão.
12. **Entrega** (`delivery.kind = pull_request`): commit do que o worker deixou sem commit, `git push`, `gh pr create` **uma vez por branch** (consulta `gh pr list --head` antes; o evento `delivery.pr_opened` também não se repete), e polling de `gh pr checks` a cada 30 s por até 60 leituras. `passed` → `delivery.checks_passed` → `complete()`; `failed` → `delivery.checks_failed` + `needs_revision` no próximo ciclo; sem resposta no teto → `blocked` (`delivery_checks_timeout`) + decisão `stop`/`keep_waiting`. Com `delivery.kind = none`, conclui após o revisor.

`complete()` continua exigindo, no store, evidência `satisfied` de todos os critérios, cadeia válida, nenhuma decisão pendente e, para PR, `checks_passed` depois do último `pr_opened`.

### Decisões que o supervisor abre

| Situação | `kind` | Estado | Opções (padrão seguro primeiro) |
|---|---|---|---|
| run órfão | `escalation` | `unknown` | `stop`, `revise_mission` |
| orçamento | `budget` | `blocked` | `stop`, `revise_mission` |
| limite de ciclos (`needs_revision_limit`, `run_failed`, `delivery_checks_failed`, `max_cycles`), `no_progress`, `review_blocked` | `escalation` | `blocked` | `stop`, `grant_cycle` |
| checks sem resposta | `escalation` | `blocked` | `stop`, `keep_waiting` |
| worker com `blockers` | `clarification` | `paused` | `pause`, `retry` |
| revisor `out_of_mission` | `out_of_mission` | `paused` | `pause`, `retry_within_mission` |

O supervisor não age sobre a opção escolhida, com uma exceção: cada decisão resolvida com `grant_cycle` concede um ciclo além de `maxCycles`. Para continuar depois de decidir: `pipe mission resume <id>` e `pipe mission supervise <id> --detach`.

## Pausar, cancelar, retomar

- `pipe mission pause <id>`: o supervisor vê o estado em ≤ `--poll-seconds` (padrão 5 s), SIGTERM ao worker, `run.interrupted`, e termina. Nada novo parte enquanto `paused`.
- `pipe mission resume <id>` + `pipe mission supervise <id> --detach`: o mesmo ciclo é retomado com `attempt` novo (a pausa não consome ciclo). Se a pausa veio durante o revisor, só a revisão é refeita.
- `pipe mission cancel <id>`: igual à pausa, mas terminal.
- SIGTERM/SIGINT no próprio supervisor: termina o worker, registra `run.interrupted` e sai com a missão `active` (retomável).
- Supervisor morto com SIGKILL: `status` mostra `supervisor.alive=false` e um run `running`; `pipe mission reconcile <id>` (ou o próximo `supervise`) marca `unknown` e abre decisão.

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

Brief, prompt do revisor, texto de resultado do worker ou do revisor, diff e saída de comandos. O store guarda só ids (`sessionId`, `runId`), hashes (`resultFingerprint`, `diffFingerprint`), contagens, códigos (`reason`, `subtype`, modelo) e refs (URL do PR). Toda string de evento passa por `safe_identifier`; `collect_run(extra=...)` não aceita texto livre nem sobrescreve campos fixos. Testado varrendo o arquivo SQLite (e `-wal`) por uma sentinela do worker e do revisor.

## Limites

- **Sem merge automático.** O supervisor abre o PR e espera os checks; o merge é do fundador.
- **Sem Linear por código.** O handoff no Linear segue pelo MCP no chat (skill `/missao`).
- **Um escritor por vez.** Um supervisor por missão (pid); um worker por vez; nada de workers em paralelo.
- **Custo medido, não estimado**: `costUsd` é a soma de `total_cost_usd` reportado pelo `claude -p` de cada run. Run morto sem JSON conta US$ 0 (o custo real é desconhecido) e run reconciliado como `unknown` também.
- **Pid pode ser reutilizado** pelo sistema depois que o supervisor morre; se `status` disser `alive=true` sem supervisor, apague `supervisor.pid`.
- **`unknown` é terminal**: continuar exige uma missão nova (`version` nova ou outro conteúdo).
- **Rede**: só a que `git push` e `gh` já usam. O worker herda o ambiente do supervisor; não rode o supervisor num shell com segredos exportados que o worker não deva ver.
- Evidência não gera evento próprio (allowlist fixa); fica em `criteria_evidence` e é lida por `status`/`complete`.
- O que o Pipe já governa (`AGENTS.md`, approval gates) continua valendo por cima.

## Testes

Só executáveis falsos (`tests/mission/fakes/fake_claude.py`, `fake_gh.py`); nenhum `claude` ou `gh` real. As falhas §5 do desenho têm teste nomeado em `tests/mission/test_supervisor.py` (`test_f1_…` a `test_f9_…`), mais circuit breaker, blockers, permission denials, PR idempotente, checks, sentinela fora do SQLite e escritor único; o `--detach` real está em `tests/mission/test_supervisor_cli.py`.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests/mission -t . -q
```
