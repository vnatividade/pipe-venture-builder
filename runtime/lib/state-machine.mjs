// Máquina de estados da fatia vertical (ver docs/venture-os/state-machine.md).
// Estados do fluxo + estados transversais; transições declarativas com evento,
// origem, destino, guard nomeado, gate e estratégia de erro. Transições
// inválidas são recusadas com erro tipado e nada é persistido.
import { nowIso } from './ids.mjs';

export const STATES = [
  'CREATED', 'INTAKE_IN_PROGRESS', 'INTAKE_REVIEW', 'INTAKE_APPROVED', 'PRODUCT_STRATEGY_READY',
  'PRODUCT_STRATEGY_IN_PROGRESS', 'PRODUCT_STRATEGY_REVIEW', 'PRODUCT_STRATEGY_APPROVED', 'MVP_REFINEMENT_READY',
  'MVP_REFINEMENT_IN_PROGRESS', 'MVP_REFINEMENT_REVIEW', 'MVP_REFINEMENT_APPROVED', 'UX_ARCHITECTURE_READY',
  'UX_ARCHITECTURE_IN_PROGRESS', 'UX_ARCHITECTURE_REVIEW', 'UX_ARCHITECTURE_APPROVED', 'DESIGN_CONTEXT_READY', 'CLAUDE_DESIGN_PROMPT_READY',
  'PAUSED', 'BLOCKED', 'WAITING_HUMAN', 'FAILED', 'CANCELLED',
];

const ACTIVE_STATES = ['CREATED', 'INTAKE_IN_PROGRESS', 'INTAKE_REVIEW', 'INTAKE_APPROVED',
  'PRODUCT_STRATEGY_READY', 'PRODUCT_STRATEGY_IN_PROGRESS', 'PRODUCT_STRATEGY_REVIEW', 'PRODUCT_STRATEGY_APPROVED',
  'MVP_REFINEMENT_READY', 'MVP_REFINEMENT_IN_PROGRESS', 'MVP_REFINEMENT_REVIEW', 'MVP_REFINEMENT_APPROVED',
  'UX_ARCHITECTURE_READY', 'UX_ARCHITECTURE_IN_PROGRESS', 'UX_ARCHITECTURE_REVIEW', 'UX_ARCHITECTURE_APPROVED', 'DESIGN_CONTEXT_READY'];
const TERMINAL_STATES = ['CANCELLED', 'FAILED'];

// Retomada pós-decisão humana: a fase volta ao seu estado de execução.
const RESUME_MAP = {
  INTAKE_REVIEW: 'INTAKE_IN_PROGRESS',
  PRODUCT_STRATEGY_REVIEW: 'PRODUCT_STRATEGY_IN_PROGRESS',
  MVP_REFINEMENT_REVIEW: 'MVP_REFINEMENT_IN_PROGRESS',
  UX_ARCHITECTURE_REVIEW: 'UX_ARCHITECTURE_IN_PROGRESS',
};

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
  promptPackageReady: ({ ctx }) => Boolean(ctx?.promptPackageReady),
  phaseArtifactsValid: ({ ctx }) => Boolean(ctx?.phaseArtifactsValid),
  designPackageReady: ({ ctx }) => Boolean(ctx?.designPackageReady),
};

export const TRANSITIONS = [
  { event: 'START_INTAKE',            from: 'CREATED',            to: 'INTAKE_IN_PROGRESS', guard: 'hasIdeaSource',              gate: null,                        onError: 'reject' },
  { event: 'BRIEF_PRODUCED',          from: 'INTAKE_IN_PROGRESS', to: 'INTAKE_REVIEW',      guard: 'briefArtifactValid',         gate: null,                        onError: 'retry' },
  { event: 'GATE_PASSED',             from: 'INTAKE_REVIEW',      to: 'INTAKE_APPROVED',    guard: 'gatePassed',                 gate: 'intake-completeness-gate',  onError: 'reject' },
  { event: 'GATE_FAILED_RETRY',       from: 'INTAKE_REVIEW',      to: 'INTAKE_IN_PROGRESS', guard: 'gateFailed',                 gate: 'intake-completeness-gate',  onError: 'reject' },
  { event: 'HUMAN_DECISION_REQUESTED',from: 'INTAKE_REVIEW',      to: 'WAITING_HUMAN',      guard: 'hasBlockingDecision',        gate: null,                        onError: 'reject' },
  { event: 'HUMAN_DECISION_RECEIVED', from: 'WAITING_HUMAN',      to: '$resume',            guard: 'decisionResolved',           gate: null,                        onError: 'reject' },
  { event: 'PREPARE_NEXT_PHASE',      from: 'INTAKE_APPROVED',    to: 'PRODUCT_STRATEGY_READY', guard: 'noBlockingDecisionsPending', gate: null,                    onError: 'reject' },
  // Fase product-strategy (padrão genérico de fase: READY → IN_PROGRESS → REVIEW → APPROVED → próxima READY)
  { event: 'START_PHASE',             from: 'PRODUCT_STRATEGY_READY', to: 'PRODUCT_STRATEGY_IN_PROGRESS', guard: 'promptPackageReady', gate: null,                  onError: 'reject' },
  { event: 'PHASE_ARTIFACTS_SUBMITTED', from: 'PRODUCT_STRATEGY_IN_PROGRESS', to: 'PRODUCT_STRATEGY_REVIEW', guard: 'phaseArtifactsValid', gate: null,              onError: 'retry' },
  { event: 'GATE_PASSED',             from: 'PRODUCT_STRATEGY_REVIEW', to: 'PRODUCT_STRATEGY_APPROVED', guard: 'gatePassed',        gate: 'strategy-completeness-gate', onError: 'reject' },
  { event: 'GATE_FAILED_RETRY',       from: 'PRODUCT_STRATEGY_REVIEW', to: 'PRODUCT_STRATEGY_IN_PROGRESS', guard: 'gateFailed',     gate: 'strategy-completeness-gate', onError: 'reject' },
  { event: 'HUMAN_DECISION_REQUESTED',from: 'PRODUCT_STRATEGY_REVIEW', to: 'WAITING_HUMAN',  guard: 'hasBlockingDecision',        gate: null,                        onError: 'reject' },
  { event: 'PREPARE_NEXT_PHASE',      from: 'PRODUCT_STRATEGY_APPROVED', to: 'MVP_REFINEMENT_READY', guard: 'noBlockingDecisionsPending', gate: null,               onError: 'reject' },
  // Fase mvp-refinement (mesmo padrão)
  { event: 'START_PHASE',             from: 'MVP_REFINEMENT_READY', to: 'MVP_REFINEMENT_IN_PROGRESS', guard: 'promptPackageReady', gate: null,                      onError: 'reject' },
  { event: 'PHASE_ARTIFACTS_SUBMITTED', from: 'MVP_REFINEMENT_IN_PROGRESS', to: 'MVP_REFINEMENT_REVIEW', guard: 'phaseArtifactsValid', gate: null,                  onError: 'retry' },
  { event: 'GATE_PASSED',             from: 'MVP_REFINEMENT_REVIEW', to: 'MVP_REFINEMENT_APPROVED', guard: 'gatePassed',            gate: 'mvp-completeness-gate',  onError: 'reject' },
  { event: 'GATE_FAILED_RETRY',       from: 'MVP_REFINEMENT_REVIEW', to: 'MVP_REFINEMENT_IN_PROGRESS', guard: 'gateFailed',         gate: 'mvp-completeness-gate',  onError: 'reject' },
  { event: 'HUMAN_DECISION_REQUESTED',from: 'MVP_REFINEMENT_REVIEW', to: 'WAITING_HUMAN',  guard: 'hasBlockingDecision',            gate: null,                     onError: 'reject' },
  { event: 'PREPARE_NEXT_PHASE',      from: 'MVP_REFINEMENT_APPROVED', to: 'UX_ARCHITECTURE_READY', guard: 'noBlockingDecisionsPending', gate: null,                onError: 'reject' },
  // Fase ux-architecture (mesmo padrão) + compilação do pacote de design
  { event: 'START_PHASE',             from: 'UX_ARCHITECTURE_READY', to: 'UX_ARCHITECTURE_IN_PROGRESS', guard: 'promptPackageReady', gate: null,                    onError: 'reject' },
  { event: 'PHASE_ARTIFACTS_SUBMITTED', from: 'UX_ARCHITECTURE_IN_PROGRESS', to: 'UX_ARCHITECTURE_REVIEW', guard: 'phaseArtifactsValid', gate: null,                onError: 'retry' },
  { event: 'GATE_PASSED',             from: 'UX_ARCHITECTURE_REVIEW', to: 'UX_ARCHITECTURE_APPROVED', guard: 'gatePassed',          gate: 'ux-completeness-gate',   onError: 'reject' },
  { event: 'GATE_FAILED_RETRY',       from: 'UX_ARCHITECTURE_REVIEW', to: 'UX_ARCHITECTURE_IN_PROGRESS', guard: 'gateFailed',       gate: 'ux-completeness-gate',   onError: 'reject' },
  { event: 'HUMAN_DECISION_REQUESTED',from: 'UX_ARCHITECTURE_REVIEW', to: 'WAITING_HUMAN',  guard: 'hasBlockingDecision',          gate: null,                     onError: 'reject' },
  { event: 'PREPARE_NEXT_PHASE',      from: 'UX_ARCHITECTURE_APPROVED', to: 'DESIGN_CONTEXT_READY', guard: 'noBlockingDecisionsPending', gate: null,                onError: 'reject' },
  { event: 'DESIGN_PACKAGE_COMPILED', from: 'DESIGN_CONTEXT_READY', to: 'CLAUDE_DESIGN_PROMPT_READY', guard: 'designPackageReady', gate: 'design-context-gate',    onError: 'reject' },
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
  if (to === '$resume') {
    to = RESUME_MAP[project.previous_state];
    if (!to) throw new InvalidTransitionError(event, from, `sem mapeamento de retomada para "${project.previous_state}"`);
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
  if (state.endsWith('_READY')) return 'ready_for_next_phase';
  return 'active';
}

function summarizeCtx(ctx) {
  const out = {};
  for (const k of ['gateStatus', 'blockingDecisionsPending', 'retryExhausted', 'decisionResolved']) {
    if (ctx[k] !== undefined) out[k] = ctx[k];
  }
  return out;
}
