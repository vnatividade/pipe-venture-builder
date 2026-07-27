// Máquina de estados da fatia vertical (ver docs/venture-os/state-machine.md).
// Estados do fluxo + estados transversais; transições declarativas com evento,
// origem, destino, guard nomeado, gate e estratégia de erro. Transições
// inválidas são recusadas com erro tipado e nada é persistido.
import { nowIso } from './ids.mjs';

export const STATES = [
  'CREATED', 'INTAKE_IN_PROGRESS', 'INTAKE_REVIEW', 'INTAKE_APPROVED', 'PRODUCT_STRATEGY_READY',
  'PAUSED', 'BLOCKED', 'WAITING_HUMAN', 'FAILED', 'CANCELLED',
];

const ACTIVE_STATES = ['CREATED', 'INTAKE_IN_PROGRESS', 'INTAKE_REVIEW', 'INTAKE_APPROVED'];
const TERMINAL_STATES = ['CANCELLED', 'FAILED'];

// Guards nomeados (funções puras sobre {project, ctx}); o nome vai para o histórico.
const GUARDS = {
  always: () => true,
  hasIdeaSource: ({ ctx }) => Boolean(ctx?.hasIdeaSource),
  briefArtifactValid: ({ ctx }) => Boolean(ctx?.briefArtifactValid),
  gatePassed: ({ ctx }) => ctx?.gateStatus === 'pass' || ctx?.gateStatus === 'pass_with_warnings',
  gateFailed: ({ ctx }) => ctx?.gateStatus === 'fail',
  noBlockingDecisionsPending: ({ ctx }) => (ctx?.blockingDecisionsPending ?? 0) === 0,
  hasBlockingDecision: ({ ctx }) => (ctx?.blockingDecisionsPending ?? 0) > 0,
  humanRequested: ({ ctx }) => Boolean(ctx?.humanRequested),
  decisionResolved: ({ ctx }) => Boolean(ctx?.decisionResolved),
  retryExhausted: ({ ctx }) => Boolean(ctx?.retryExhausted),
};

export const TRANSITIONS = [
  { event: 'START_INTAKE',            from: 'CREATED',            to: 'INTAKE_IN_PROGRESS', guard: 'hasIdeaSource',              gate: null,                        onError: 'reject' },
  { event: 'BRIEF_PRODUCED',          from: 'INTAKE_IN_PROGRESS', to: 'INTAKE_REVIEW',      guard: 'briefArtifactValid',         gate: null,                        onError: 'retry' },
  { event: 'GATE_PASSED',             from: 'INTAKE_REVIEW',      to: 'INTAKE_APPROVED',    guard: 'gatePassed',                 gate: 'intake-completeness-gate',  onError: 'reject' },
  { event: 'GATE_FAILED_RETRY',       from: 'INTAKE_REVIEW',      to: 'INTAKE_IN_PROGRESS', guard: 'gateFailed',                 gate: 'intake-completeness-gate',  onError: 'reject' },
  { event: 'HUMAN_DECISION_REQUESTED',from: 'INTAKE_REVIEW',      to: 'WAITING_HUMAN',      guard: 'hasBlockingDecision',        gate: null,                        onError: 'reject' },
  { event: 'HUMAN_DECISION_RECEIVED', from: 'WAITING_HUMAN',      to: 'INTAKE_IN_PROGRESS', guard: 'decisionResolved',           gate: null,                        onError: 'reject' },
  { event: 'PREPARE_NEXT_PHASE',      from: 'INTAKE_APPROVED',    to: 'PRODUCT_STRATEGY_READY', guard: 'noBlockingDecisionsPending', gate: null,                    onError: 'reject' },
  { event: 'PAUSE',                   from: ACTIVE_STATES,        to: 'PAUSED',             guard: 'always',                     gate: null,                        onError: 'reject' },
  { event: 'RESUME',                  from: 'PAUSED',             to: '$previous',          guard: 'always',                     gate: null,                        onError: 'reject' },
  { event: 'FAIL',                    from: [...ACTIVE_STATES, 'WAITING_HUMAN'], to: 'FAILED', guard: 'retryExhausted',          gate: null,                        onError: 'reject' },
  { event: 'CANCEL',                  from: [...ACTIVE_STATES, 'WAITING_HUMAN', 'PAUSED', 'BLOCKED'], to: 'CANCELLED', guard: 'always', gate: null,                 onError: 'reject' },
];

export function findTransition(event, fromState) {
  return TRANSITIONS.find((t) => t.event === event &&
    (Array.isArray(t.from) ? t.from.includes(fromState) : t.from === fromState));
}

export class InvalidTransitionError extends Error {
  constructor(event, from, reason) {
    super(`transição inválida: evento=${event} origem=${from}${reason ? ` (${reason})` : ''}`);
    this.code = 'INVALID_TRANSITION';
    this.event = event;
    this.from = from;
  }
}

// Aplica uma transição ao projeto (mutação em memória) e retorna o registro
// para o histórico. A persistência (com controle de versão) é do chamador.
export function applyTransition(project, event, ctx = {}) {
  const from = project.current_state;
  if (TERMINAL_STATES.includes(from)) throw new InvalidTransitionError(event, from, 'estado terminal');
  const t = findTransition(event, from);
  if (!t) throw new InvalidTransitionError(event, from, 'nenhuma transição definida');
  const guardFn = GUARDS[t.guard];
  if (!guardFn) throw new Error(`guard desconhecido: ${t.guard}`);
  if (!guardFn({ project, ctx })) throw new InvalidTransitionError(event, from, `guard "${t.guard}" reprovou`);

  let to = t.to;
  if (to === '$previous') {
    to = project.previous_state;
    if (!to || !STATES.includes(to)) throw new InvalidTransitionError(event, from, 'sem estado anterior para retomar');
  }
  if (['PAUSED', 'WAITING_HUMAN'].includes(to)) project.previous_state = from === 'WAITING_HUMAN' ? project.previous_state : from;

  project.current_state = to;
  project.status = stateToStatus(to);
  return {
    ts: nowIso(), event, from, to, guard: t.guard, guard_result: true,
    gate: t.gate, on_error: t.onError, ctx_summary: summarizeCtx(ctx),
  };
}

function stateToStatus(state) {
  if (state === 'CANCELLED') return 'cancelled';
  if (state === 'FAILED') return 'failed';
  if (state === 'PAUSED') return 'paused';
  if (state === 'WAITING_HUMAN') return 'waiting_human';
  if (state === 'BLOCKED') return 'blocked';
  if (state === 'PRODUCT_STRATEGY_READY') return 'ready_for_next_phase';
  return 'active';
}

function summarizeCtx(ctx) {
  const out = {};
  for (const k of ['gateStatus', 'blockingDecisionsPending', 'retryExhausted', 'decisionResolved']) {
    if (ctx[k] !== undefined) out[k] = ctx[k];
  }
  return out;
}
