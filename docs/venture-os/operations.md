# Operação

## Variáveis

| Variável | Default | Efeito |
|---|---|---|
| `VENTURE_OS_ENABLED` | (vazio = off) | Habilita comandos mutantes; off = recusa com mensagem (fail-safe) |
| `VENTURE_OS_PROJECTS_ROOT` | `~/.pipe/venture-os/projects` | Raiz machine-local dos projetos |
| `VENTURE_OS_LOG_SILENT` | (vazio) | `1` silencia logs estruturados (usado em testes) |

## Layout de um projeto em disco

```txt
<root>/<slug>/
├── project.json            # contrato Project (estado, versão, refs)
├── state-history.jsonl     # transições (evento, from, to, guard, gate) — append-only
├── events.jsonl            # eventos (envelope com correlation/causation) — append-only
├── sources/                # idea-v1.md + clarification-v*.md (imutáveis)
├── runs/<runId>.json       # contrato Run
├── artifacts/manifest.json # manifesto (hash, proveniência, validação, supersessão)
├── artifacts/initial-brief/vN/initial-brief.{json,md}
└── decisions/<decId>.json  # contrato HumanDecisionRequest
```

## Observabilidade

- **Logs estruturados** (JSON lines, stderr): ts, level, msg, project/run/event/correlation ids,
  step, attempt, erro. Chaves sensíveis são redigidas; conteúdo de ideia/prompt **não** é logado
  (apenas hashes e tamanhos).
- **Correlation ID** por invocação do CLI; **causation ID** encadeia eventos.
- **Duração**: `run.costs.latency_ms`. Tokens/custo/modelo: campos presentes, `null` até haver
  executor LLM (sem simulação de valores).
- Inspeção: `events --tail N`, `transitions`, `runs`, `gates`.

## Runbook

| Situação | Ação |
|---|---|
| Gate reprovou por lacuna | `decisions --pending` → `respond --option provide-info --text ...` → `resume` |
| Projeto pausado | `resume` (volta ao estado anterior e continua se executável) |
| Processo interrompido no meio | `run` de novo — a run ativa é reutilizada (sem duplicar) |
| Conflito de versão (`VERSION_CONFLICT`) | outra escrita concorrente venceu; releia (`show`) e repita a operação |
| Desabilitar tudo | remover `VENTURE_OS_ENABLED`; estado em disco permanece intacto para retomada futura |
