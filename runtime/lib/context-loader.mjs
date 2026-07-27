// Context Loader determinístico (sem busca semântica — decisão registrada).
// Recebe projeto/workflow/fase/agente/tarefa e devolve o contexto mínimo em
// ordem de precedência, com hashes, limite e registro do que foi omitido.
import { sha256, nowIso } from './ids.mjs';

const DEFAULT_LIMIT_CHARS = 32_000;

export function loadContext({ store, slug, project, workflowDef, agentDef, task, limitChars = DEFAULT_LIMIT_CHARS }) {
  // Precedência (maior primeiro), espelhando a hierarquia de autoridade do repo:
  // 1. estado do projeto  2. fontes (ideia + clarificações)  3. contrato do agente  4. definição do workflow
  const docs = [];
  const stateJson = JSON.stringify(project, null, 2);
  docs.push({ name: 'project-state', precedence: 1, content: stateJson });
  for (const src of store.listSources(slug)) {
    docs.push({ name: `source:${src.name}`, precedence: 2, content: src.content });
  }
  docs.push({ name: `agent:${agentDef.id}@${agentDef.version}`, precedence: 3, content: JSON.stringify(agentDef, null, 2) });
  docs.push({ name: `workflow:${workflowDef.id}@${workflowDef.version}`, precedence: 4, content: JSON.stringify(workflowDef, null, 2) });

  const included = [];
  const omitted = [];
  let used = 0;
  for (const doc of docs.sort((a, b) => a.precedence - b.precedence)) {
    const size = doc.content.length;
    if (used + size <= limitChars) {
      included.push(doc);
      used += size;
    } else {
      // Nunca omitir o estado do projeto nem as fontes (safety floor da fatia).
      if (doc.precedence <= 2) {
        const remaining = Math.max(0, limitChars - used);
        included.push({ ...doc, content: doc.content.slice(0, remaining), truncated: true });
        used = limitChars;
        omitted.push({ name: doc.name, reason: `truncado para caber no limite (${limitChars} chars)` });
      } else {
        omitted.push({ name: doc.name, reason: 'omitido por limite de contexto (precedência baixa)' });
      }
    }
  }

  return {
    task,
    limit_chars: limitChars,
    used_chars: used,
    loaded_at: nowIso(),
    documents: included.map((d) => ({
      name: d.name, precedence: d.precedence, chars: d.content.length,
      hash: sha256(d.content), truncated: Boolean(d.truncated),
    })),
    omitted,
    // conteúdo real entregue ao agente (não vai para logs — apenas hashes/tamanhos são logados)
    contents: Object.fromEntries(included.map((d) => [d.name, d.content])),
  };
}
