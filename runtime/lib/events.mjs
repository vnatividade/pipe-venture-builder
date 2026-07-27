// Eventos: envelope padronizado + registro em log append-only por projeto.
// Sem barramento distribuído (decisão registrada): o log JSONL é o consumidor único da fatia.
import { newId, nowIso } from './ids.mjs';
import { info } from './log.mjs';
import { assertContract } from './contracts.mjs';

export const EVENT_TYPES = [
  'ProjectCreated', 'RunCreated', 'PhaseStarted', 'AgentAssigned', 'ContextLoaded',
  'StepStarted', 'ArtifactCreated', 'ArtifactValidated', 'GatePassed', 'GateFailed',
  'HumanDecisionRequested', 'HumanDecisionReceived', 'WorkflowPaused', 'WorkflowResumed',
  'PhaseCompleted', 'WorkflowFailed',
];

export function makeEmitter(store, { projectId, slug, correlationId }) {
  let lastEventId = null;
  return function emit(type, payload = {}, { runId = null, causationId = null } = {}) {
    if (!EVENT_TYPES.includes(type)) throw new Error(`tipo de evento desconhecido: ${type}`);
    const event = {
      id: newId('evt'),
      type,
      version: '0.1.0',
      project_id: projectId,
      run_id: runId,
      ts: nowIso(),
      source: 'venture-os-runtime',
      payload,
      correlation_id: correlationId,
      causation_id: causationId ?? lastEventId,
    };
    assertContract('EventEnvelope', event);
    store.appendEvent(slug, event);
    lastEventId = event.id;
    info(`event:${type}`, { project_id: projectId, run_id: runId, event_id: event.id, correlation_id: correlationId });
    return event;
  };
}
