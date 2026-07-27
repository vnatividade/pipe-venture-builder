// Human-in-the-loop: fila de decisões humanas.
// Regras herdadas da política do pipe: silêncio nunca aprova; timeout nunca vira
// aprovação; default seguro de decisão bloqueadora é PERMANECER bloqueado;
// idempotência por (projeto, run, reason_code) — pedido aberto não duplica.
import { newId, nowIso } from './ids.mjs';

export class DecisionQueue {
  constructor(store) { this.store = store; }

  request({ slug, projectId, runId, phase, priority = 'P1', category, reasonCode, context, reason, impact, options, recommendation, safeDefault, expectedResponse, blockedScope }) {
    const open = this.store.listDecisions(slug)
      .find((d) => d.status === 'pending' && d.reason_code === reasonCode && d.run_id === runId);
    if (open) return { decision: open, deduplicated: true };

    if (!Array.isArray(options) || options.length < 2) {
      throw new Error('uma decisão humana precisa de pelo menos 2 opções');
    }
    const decision = {
      id: newId('dec'),
      project_id: projectId,
      run_id: runId,
      phase,
      status: 'pending',
      priority,
      category,
      reason_code: reasonCode,
      context,
      reason,
      impact,
      options,          // [{id, label, consequences}]
      recommendation,   // id da opção recomendada + racional
      safe_default: safeDefault,
      expected_response: expectedResponse, // ex.: {type: 'option', free_text_allowed: true}
      blocked_scope: blockedScope,         // o que fica bloqueado (e o que segue)
      created_at: nowIso(),
      resolved_at: null,
      resolution: null,
    };
    this.store.saveDecision(slug, decision);
    return { decision, deduplicated: false };
  }

  listPending(slug) { return this.store.listDecisions(slug).filter((d) => d.status === 'pending'); }

  respond({ slug, decisionId, optionId, freeText = null, decidedBy }) {
    const decision = this.store.loadDecision(slug, decisionId);
    if (decision.status !== 'pending') {
      const err = new Error(`decisão ${decisionId} já resolvida (${decision.status}) — resposta ignorada (idempotência)`);
      err.code = 'ALREADY_RESOLVED';
      throw err;
    }
    const option = decision.options.find((o) => o.id === optionId);
    if (!option) {
      const err = new Error(`opção inválida "${optionId}"; válidas: ${decision.options.map((o) => o.id).join(', ')}`);
      err.code = 'INVALID_RESPONSE';
      throw err;
    }
    if (decision.expected_response?.requires_free_text && !freeText?.trim()) {
      const err = new Error('esta decisão exige texto complementar (free_text) na resposta');
      err.code = 'INVALID_RESPONSE';
      throw err;
    }
    if (!decidedBy?.trim()) {
      const err = new Error('decided_by é obrigatório: decisão humana precisa de um humano nomeado');
      err.code = 'INVALID_RESPONSE';
      throw err;
    }
    decision.status = 'resolved';
    decision.resolved_at = nowIso();
    decision.resolution = { option_id: optionId, free_text: freeText, decided_by: decidedBy, consequence: option.consequences ?? null };
    this.store.saveDecision(slug, decision);
    return decision;
  }
}
