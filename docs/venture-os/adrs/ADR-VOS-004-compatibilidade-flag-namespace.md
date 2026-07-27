# ADR-VOS-004 — Compatibilidade por namespace novo + feature flag fail-safe

Status: Accepted · 2026-07-27 · Reversível: sim (é o próprio mecanismo de reversão)

**Contexto/Problema.** O repo é o manual compartilhado em modo `restricted`; a implementação não
pode alterar comportamento atual nem tocar arquivos de governança.

**Opções.** (A) Namespaces novos (`runtime/`, `docs/venture-os/`) + flag `VENTURE_OS_ENABLED`
default off; (B) integrar aos diretórios existentes (`.codex/workflows/`, `schemas/`);
(C) repositório separado.

**Decisão.** A. Zero arquivos existentes alterados (verificável por `git status`); flag com o mesmo
fail-safe do `mode.json` (ausente = desabilitado); CLI `pipe-os` não colide com o CLI `pipe`
(runtime Python já em `main` — fronteira no ADR-VOS-006). B tocaria áreas de governança serializadas e o namespace `schemas/` canônico
(exige ticket/review). C fragmentaria a distribuição em 3 camadas decidida no ADR-001 do repo
(runtime pertence ao toolkit).

**Comportamento.** Flag off: comandos mutantes recusam com mensagem; leitura funciona com aviso;
nenhum fluxo existente é afetado em nenhum caso (não há hook em fluxo existente). Rollback total:
apagar os dois diretórios. Testes cobrem flag on/off.

**Consequências.** A promoção de contratos da fatia a `schemas/` canônico e o registro da capability
no registry ficam para PRs normais com review humano. **Revisão quando:** fase 0/auditoria das
branches decidir a fusão com o CLI `pipe`.
