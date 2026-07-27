# ADR-VOS-007 — Claude Design (claude.ai/design) manual-first e executor Claude Code

Status: Accepted · 2026-07-27 · Decisões do fundador na thread (DEC-AP-001/002 da auditoria em
`~/Developer/analises/agentic-pipeline-audit/`)

**DEC-AP-001 — Design/prototipação.** Ferramenta oficial da fase de design: **claude.ai/design**.
Fluxo decidido: a pasta com o conteúdo aprovado do produto é o **farol**; o usuário faz o input
manual desse pacote no Claude Design; o resultado retorna ao agente para registro e revisão
(Prototype Reviewer). **Se houver API do Claude Design, a conexão direta é preferida** — investigar
disponibilidade na fase F3 antes de construir o adapter; o adapter **traduz contexto aprovado,
nunca decide produto**.

**DEC-AP-002 — Executor das fases criativas (estratégia/MVP/UX).** **Claude Code interativo**
(recomendação aceita): consome o pacote do Prompt Compiler, produz os artefatos com a convenção de
rastreabilidade `(fonte: ...)`, submete via `pipe-os submit`. Sem API key nova, sem custo
recorrente novo, sem segredo — o gate determinístico e o reviewer validam o output
independentemente de quem o produziu.

**Consequências.** A fase product-strategy (fatia 3) implementa o padrão; F3 (design context +
adapter) fica desbloqueada com o desenho manual-first; upgrade para API é aditivo. **Revisão
quando:** API do Claude Design disponível/confirmada, ou volume justificar executor via API (custo
→ gate absoluto).
