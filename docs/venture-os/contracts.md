# Contratos (fatia 1)

Todos em `runtime/schemas/*.schema.json` (draft 2020-12, `$id` local, `x-pipe-schema-version: 0.1.0`,
mesmas convenções de `architecture/canonical-schema-policy.md`), validados em runtime por
`runtime/lib/contracts.mjs` nos pontos de criação/persistência. **Namespace separado de `schemas/`**
(contratos canônicos do manual) de propósito: os contratos da fatia são operacionais e evoluem com o
runtime; promoção a `schemas/` canônico exige ticket + review (política vigente).

| Contrato | Validado em | Campos-chave |
|---|---|---|
| `Project` | criação e toda transição | id, name, slug, description, current_state (10 estados), current_phase, status, **state_version**, next_action, blockers, artifact_refs, decision_refs, run_refs, created/updated_at |
| `Run` | criação | id, project_id, workflow_id, phase, status (7), agent_id, current_step, **attempt**, started/completed_at, error, result, costs {tokens, cost, model, latency_ms, tool_calls}, events[], context_log |
| `Workflow` | carga da definição | id, version, name, entry_state, steps[], transitions[], gates[], allowed_agents[], outputs[], max_attempts, next_phase_on_success |
| `AgentDefinition` | carga da definição | id, version, mission, implementation, allowed_tools, required_context, allowed_outputs, **allowed_write_paths**, forbidden_actions, **autonomy_level**, completion_criteria |
| `ArtifactManifestEntry` | registro de artefato | id, project/run_id, type, **version**, path, status (present/superseded/invalid), **hash sha256**, created_by, agent_id, model, prompt_version, source_refs, render_path, superseded_by, validation |
| `GateResult` | execução do gate | id, gate_id, project/run_id, status (pass/pass_with_warnings/fail), **score**, failures[{check, severity, category, message}], warnings[], evidence[], recommended_actions[], next_action |
| `HumanDecisionRequest` | criação do pedido | id, project/run_id, phase, status, priority (P0–P3), category, **reason_code** (chave de idempotência), context, reason, impact, options[], recommendation, **safe_default**, expected_response, **blocked_scope**, resolution |
| `EventEnvelope` | toda emissão | id, type (16 tipos), version, project_id, run_id, ts, source, payload, **correlation_id**, causation_id |

Versionamento: mudanças seguem a mesma semântica semver da política canônica (patch = texto;
minor = campo opcional; major = required/rename/enum). Compatibilidade: consumidores devem ignorar
campos desconhecidos (additionalProperties permitido nos contratos da fatia).

Exemplos reais: qualquer projeto criado gera instâncias válidas — ver `operations.md` para inspecionar.
