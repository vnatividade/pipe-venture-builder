# ADR-VOS-003 — intake-agent determinístico por default, contrato aberto a executor LLM

Status: Accepted · 2026-07-27 · Reversível: sim

**Contexto/Problema.** O agente da fatia precisa "usar os mecanismos atuais de modelo do
repositório sempre que possível" — mas o mecanismo atual do pipe É o executor LLM interativo
(Claude Code/Codex); não há infraestrutura de chamada de API de modelo, e adicioná-la exigiria
segredo/custo/fornecedor (gate humano pela própria política da tarefa).

**Opções.** (A) Normalizador determinístico implementando o contrato do agente; (B) chamada direta a
API de LLM; (C) exigir executor LLM interativo no loop.

**Decisão.** A, com o contrato (`intake-agent.definition.json`) escrito para dois implementadores.
O determinístico é testável, sem rede, sem custo, e **estruturalmente incapaz de inventar
requisitos** (todo item é verbatim da fonte com referência) — a garantia mais difícil de obter de um
LLM vira propriedade de construção. Ele erra nuance semântica, e o erro é SEGURO: lacuna
falsa-positiva vira pergunta ao humano, nunca conteúdo inventado. B exige segredos/custo/fornecedor
(bloqueado sem decisão humana); C impediria testes automatizados da fatia.

**Consequências.** Briefs de ideias muito coloquiais pedirão clarificação com mais frequência.
**Revisão quando:** houver executor LLM plugado — o gate de rastreabilidade e o reviewer já foram
desenhados para validar output de LLM. **Migração:** troca de implementação não muda engine, gate,
contratos ou testes de contrato.
