# Human-in-the-loop (fatia 1)

Implementação: `runtime/lib/decisions.mjs` · Contrato: `HumanDecisionRequest`.

## Princípios (herdados da política do pipe, agora executáveis)

- **Silêncio, timeout ou memória nunca aprovam.** O `safe_default` de decisão bloqueadora é sempre
  "permanecer em WAITING_HUMAN"; não existe caminho de código de auto-aprovação.
- **Seletividade:** só falha por lacuna de insumo (`input_gap`) gera pedido — e as lacunas são
  **agrupadas em um único pedido** com opções, recomendação e consequências (a spec: "não transforme
  o usuário em gerente operacional").
- **Bloqueio parcial:** `blocked_scope` declara o que fica bloqueado (o workflow deste projeto) e o
  que segue (outros projetos, leitura).
- **Resposta validada:** opção precisa existir; `provide-info` exige texto; `decided_by` exige um
  humano nomeado. Resposta inválida não muda estado. Decisão resolvida não reprocessa (idempotência).
- **Idempotência do pedido:** chave `(run, reason_code)` — reexecutar com pedido aberto não duplica.

## Ciclo

```txt
GateFailed(input_gap) ─► HumanDecisionRequested ─► WAITING_HUMAN (WorkflowPaused)
      resposta válida ─► HumanDecisionReceived ─► INTAKE_IN_PROGRESS (WorkflowResumed)
        provide-info: texto vira sources/clarification-vN.md → resume regenera brief vN+1
        cancel-project: CANCEL → CANCELLED (terminal; nada é apagado)
```

## Comandos

```bash
node runtime/cli/pipe-os.mjs decisions --project <slug> --pending
node runtime/cli/pipe-os.mjs respond --project <slug> --decision <id> --option provide-info --text "..." --by <nome>
node runtime/cli/pipe-os.mjs resume --project <slug>
```

Formato DEC-XXX da spec (Contexto/Por quê/Impacto/Opções/Recomendação/Default/Resposta): os campos
do contrato mapeiam 1:1; a serialização Markdown para canais humanos (Linear/Slack) fica para a
próxima fatia — hoje o pedido é consultável pelo CLI em JSON.
