# Workflow `idea-to-intake`

Definição declarativa: `runtime/workflows/idea-to-intake.definition.json` (contrato `Workflow`).
Fase 0 do Venture OS (Intake e normalização): descrição livre → brief estruturado.

## Passos

| Passo | O que faz | Evento(s) |
|---|---|---|
| `load_context` | Contexto mínimo determinístico (estado, fontes, contratos) com precedência, hashes e omissões | `ContextLoaded` |
| `run_agent` | `intake-agent` normaliza as fontes (ideia + clarificações) | — |
| `create_artifact` | Registra `initial-brief` vN (JSON + render Markdown) com hash e proveniência; dedup por hash | `ArtifactCreated` |
| `review` | `intake-reviewer` (advisory) — achados viram warnings do gate | — |
| `gate` | `intake-completeness-gate` determinístico; validação anexada ao artefato | `ArtifactValidated`, `GatePassed`/`GateFailed` |
| `prepare_next` | Determina próxima fase/workflow/agente/dependências/bloqueadores | `PhaseCompleted` |

## Saídas por resultado do gate

- **pass / pass_with_warnings** → `INTAKE_APPROVED` → `PRODUCT_STRATEGY_READY`; `next_action` do
  projeto aponta `product_strategy` (≙ `founder_focus` no pipeline do pipe), com dependências e
  advisories (ex.: público não identificado).
- **fail por lacuna de insumo** (`input_gap`/`unsupported_claims`) → **uma** decisão humana
  bloqueadora agrupando todas as lacunas → `WAITING_HUMAN`. Resposta `provide-info` vira fonte
  `clarification-vN.md`; `resume` regenera o brief (vN+1) e reexecuta o gate.
- **fail estrutural** → retry (máx. 2 tentativas) → `FAILED` com erro registrado.

Entrada: texto livre não vazio (`create-project --idea`). A ideia é gravada como
`sources/idea-v1.md` — fonte imutável; clarificações são fontes novas, nunca edição da original.
