# ADR-VOS-001 — Persistência em arquivos estruturados atrás de interface

Status: Accepted · 2026-07-27 · Escopo: fatia vertical 1 · Reversível: sim

**Contexto/Problema.** A fatia precisa de estado durável, versionado, atômico, auditável e retomável.
O repo não tem banco; a análise recomendou run store machine-local (SQLite) como alvo.

**Opções.** (A) JSON/JSONL atômicos atrás da interface `Store`; (B) `node:sqlite`; (C) SQLite via
dependência nativa.

**Trade-offs.** A: zero dependências, transparente (inspecionável com cat/git), atomicidade por
tmp+rename e concorrência otimista por versão; sem transações multiobjeto. B: transações reais, mas
API ainda instável entre versões de Node e menos inspecionável. C: adiciona supply chain nativa
(contra a política de segurança do repo para uma fatia).

**Decisão.** A — arquivos estruturados, **explicitamente não-final**, protegidos pela interface
`Store` (`runtime/lib/store.mjs`): domínio nunca toca filesystem diretamente; trocar para SQLite é
implementar a mesma interface. Consistência necessária à fatia coberta por escrita atômica +
`state_version` (conflito → `VERSION_CONFLICT`) + logs append-only.

**Consequências.** Sem locks entre processos além do otimista; suficiente para operador único.
**Revisão quando:** multiusuário/multiprocesso real, ou fase 2+ da migração. **Alternativa
rejeitada:** apresentar arquivos como solução final. **Impacto na migração:** nenhum lock-in — o
layout em disco é o formato de exportação natural.
