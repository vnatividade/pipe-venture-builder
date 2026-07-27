# intake-agent

Contrato: `runtime/agents/intake-agent.definition.json` (id, versão, missão, ferramentas, contexto
obrigatório, caminhos de escrita permitidos, ações proibidas, nível de autonomia 2, critérios de
conclusão). Implementação da fatia: `runtime/agents/intake-agent.mjs`.

## O que faz

Lê as fontes (`idea-v1.md` + `clarification-v*.md`) e produz o brief estruturado com 12 seções
(descrição, problema, solução, público, funcionalidades, contexto, restrições, dependências,
premissas, lacunas, riscos, decisões abertas), em JSON (artefato de registro) + Markdown (render).

## Como garante "não inventar requisitos"

A implementação da fatia é um **normalizador determinístico**: todo item vem **verbatim** da fonte,
com referência rastreável (`fonte#sentença`). Classificação:

- **fato** — texto explícito da fonte (rotulado por seção `problema:`/bullets, ou por regras de
  palavra-chave); sempre com `source`.
- **hipótese** — frase com marcador de incerteza (`acho`, `talvez`, `provavelmente`...); registrada
  também em `assumptions` com racional.
- **lacuna** — seção obrigatória sem conteúdo; **nunca preenchida**, sempre registrada. Lacunas de
  problema/solução são bloqueadoras e geram `decisoes_abertas[blocking=true]`.

Público ausente NÃO bloqueia (hipótese provisória para a estratégia — Fase 0 da spec: "não
interrompa o usuário por lacunas que possam ser tratadas como hipóteses provisórias").

## Relação com o mecanismo canônico do repositório

O mecanismo atual do pipe é o executor LLM (Claude Code/Codex) lendo contratos. Este contrato foi
escrito para os dois implementadores: um executor LLM pode assumir o papel lendo
`intake-agent.definition.json` e produzindo o mesmo shape de brief — o gate e o reviewer validam o
resultado do mesmo jeito (a defesa anti-invenção por rastreabilidade vale ainda mais para LLM).
A troca de implementação não muda engine, gate, contratos nem testes de contrato.

## Limites conhecidos

Classificação por regras erra nuance semântica (ex.: problema descrito sem palavras-chave de
problema cai em contexto → lacuna falsa-positiva → decisão humana pede o insumo — falha SEGURA,
nunca silenciosa). Metadados registram `model: deterministic/rule-based@0.1.0`.
