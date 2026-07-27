# ADR-VOS-005 — Eventos como log append-only local (sem barramento)

Status: Accepted · 2026-07-27 · Reversível: sim

**Contexto/Problema.** A spec pede 16 eventos com envelope (id, tipo, versão, projeto, run,
timestamp, origem, payload, correlation, causation); a análise classificou event bus como
overengineering para operador único.

**Opções.** (A) JSONL append-only por projeto + envelope validado por contrato; (B) barramento
interno em memória com subscribers; (C) infraestrutura externa (Redis/NATS).

**Decisão.** A. O log É a fonte de auditoria e a base de retomada/observabilidade; consumidores da
fatia são o CLI (`events`) e os testes. Correlation id por invocação; causation id encadeando ao
evento anterior da mesma emissão. B/C adicionam infraestrutura sem consumidor real — a regra do
repo ("decision usefulness, not dashboard theater") aplicada a eventos.

**Consequências.** Sem reação assíncrona a eventos (por design; o engine é síncrono). **Revisão
quando:** existir segundo consumidor real (ex.: espelho Linear automático). **Migração:** o formato
do envelope é o contrato; um bus futuro consome o mesmo shape.
