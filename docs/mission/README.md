# Mission Loop — `Mission`, `MissionStore` e `pipe mission`

Ticket A do Mission Loop. Entrega o objeto durável **Mission**: contrato JSON versionado e fingerprintado, store SQLite próprio com eventos hash-chained, máquina de estados com pausa/cancel/`unknown`, fila de decisões humanas tipadas, evidência por critério e o CLI `pipe mission`. Não há supervisor, worker, revisor, worktree ou PR aqui — isso é o ticket B, que consome este módulo.

Desenho de origem: `10-desenho-mission-loop-mvp.md` (D1–D3, D5, D6, D8, D10; §3 contrato; §4 tabelas; §5 falhas).

## O que é uma Mission

Um documento `Mission` v0.1.0 (`schemas/Mission.schema.json`; contrato imposto em `src/pipe_venture_builder/mission/contract.py`) com:

- `missionId` `MSN-<12hex>`, gerado por `stable_id` só a partir do conteúdo (recriar o mesmo JSON é idempotente; missão nova muda conteúdo ou `version`); `fingerprint` cobre tudo menos `status`, `createdAt`, `updatedAt`, `fingerprint`.
- `successCriteria`: cada critério tem forma verificável — `check` (`command`, `cwd` opcional), `artifact` (`path`, `mustMatch` opcional) ou `rubric` (`question`). Critério sem forma é recusado.
- `constraints`: `maxCycles`, `maxBudgetUsd`, `maxTurnsPerRun` positivos; `productionAllowed`, `secretsAllowed`, `externalCommsAllowed`, `billingAllowed` **têm de ser `false`**. Gates absolutos não são escalados: são recusados na criação.
- `workspace.repo` absoluto, `baseRef`, `writeSet` relativo, não vazio, sem `..`.
- `delivery.kind ∈ {none, pull_request}` e `requireChecks`.
- O documento inteiro passa por `payload_is_safe`; sentinelas secret-shaped são recusadas com mensagem fixa, sem eco do valor.

## Estados e transições

`draft → active`; `active ↔ paused`; `active|paused → cancelled`; `active → blocked`; `blocked → active` (só sem decisão pendente); `active → completed`; `active|paused|blocked → unknown` **só** por `mark_unknown` (reconciliação). Transição inválida levanta `ControlPlaneStateError` e nada é persistido. `completed`, `cancelled` e `unknown` são terminais.

`complete` exige: cadeia de eventos válida, evidência `satisfied=true` mais recente para **todos** os critérios, nenhuma decisão pendente e, quando `delivery.kind = pull_request`, evento `delivery.pr_opened` (e `delivery.checks_passed` depois dele se `requireChecks`).

## Eventos

Allowlist fixa em `events.py` (`mission.*`, `run.*`, `verify.*`, `review.*`, `decision.*`, `delivery.*`, `budget.reached`). Cada evento traz `sequence`, `previousHash` e `eventHash = fingerprint(evento sem o hash)`. O payload aceita só identificadores, hashes, contagens, estados e refs: toda string passa por `safe_identifier`, então texto livre, prompt, saída de conversa ou diff não entram. `verify_chain(mission_id)` recomputa a cadeia inteira; `status` expõe `auditChainValid`.

## Decisões humanas

`open_decision(kind ∈ {approval, clarification, escalation, out_of_mission, budget}, context curto, options, safe_default, blocked_scope, deadline)`; pedido pendente idêntico não duplica. `resolve_decision(decision_id, option, decided_by)` exige opção válida e `decided_by` com prefixo `human:chat:`, `human:linear:` ou `human:cli:` — qualquer outra fonte (agente, supervisor) é recusada. Silêncio nunca aprova; o `safe_default` é informação para quem decide, não uma resolução automática.

## Store

`MissionStore(path)`; default `~/.pipe/mission/mission.sqlite3`. WAL, `busy_timeout`, recusa symlink, arquivos `0600`, `schema_version` em `metadata`. Tabelas: `missions`, `mission_events`, `mission_runs`, `decisions`, `criteria_evidence`. Custo acumulado = soma de `cost_usd` dos runs.

## CLI

```text
pipe mission create <mission.json> [--store PATH] [--at RFC3339] [--json]
pipe mission show <MSN-id>
pipe mission status <MSN-id> [--json]      # JSON ou "Onde estamos / Por quê / O que depende de você"
pipe mission activate|pause|resume|cancel|complete <MSN-id> [--at ...]
pipe mission decisions <MSN-id> [--pending]
pipe mission decide <DEC-id> --option <opção> --by human:chat:<quem>
```

Códigos: `MISSION_CONTRACT_VIOLATION` e `MISSION_STATE_CONFLICT` saem com `READINESS_BLOCKED` (9); `MISSION_NOT_FOUND` com `INPUT_UNAVAILABLE` (4); JSON inválido/inexistente segue `INPUT_INVALID_JSON`/`INPUT_UNAVAILABLE`. Mensagens são fixas e não ecoam o input.

## Limites desta entrega

- Nenhum processo roda: `supervisor.alive` em `status` é `null` (placeholder do ticket B).
- `unknown` é terminal aqui; sair dele é reconciliação, fora de escopo.
- Evidência não gera evento próprio (allowlist fixa); fica em `criteria_evidence` e é lida por `status`/`complete`.
- Nada de rede, credencial, Linear ou GitHub. O que o Pipe já governa (`AGENTS.md`, approval gates) continua valendo por cima.

## Testes

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests/mission -t . -q
```
