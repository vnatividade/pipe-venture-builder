# ADR-VOS-002 — Máquina de estados declarativa em código, subestados de idea_intake

Status: Accepted · 2026-07-27 · Reversível: sim

**Contexto/Problema.** A spec exige máquina de estados com transições guardadas; a análise mandou
reusar o enum `pipelineStage` (13 fases) sem inventar estados. A fatia opera só a fase de intake.

**Opções.** (A) Tabela declarativa em código (transições como dados, guards nomeados);
(B) YAML externo interpretado; (C) biblioteca de state machine (xstate etc.).

**Decisão.** A. Os 5 estados de fluxo do prompt (CREATED → INTAKE_IN_PROGRESS → INTAKE_REVIEW →
INTAKE_APPROVED → PRODUCT_STRATEGY_READY) + 5 transversais são **subestados de `idea_intake`** do
pipeline do pipe; a saída (`PRODUCT_STRATEGY_READY`) entrega `pipe_pipeline_stage: founder_focus`,
mantendo o mapa `core-pipeline-map.md` como autoridade da macrofase. Tabela declarativa
(`TRANSITIONS`) com guard nomeado, gate, estratégia de erro e registro em histórico dá o mesmo
benefício de YAML (dados inspecionáveis, testáveis por completude) sem interpretador novo; xstate
adicionaria dependência sem necessidade nesta escala.

**Consequências.** Novas fases = novas linhas na tabela + estados no enum (aditivo). **Rejeitada:**
criar macroestados novos que competissem com `pipelineStage`. **Revisão quando:** segunda fase for
implementada. **Migração:** o histórico de transições é compatível com o event log alvo.
