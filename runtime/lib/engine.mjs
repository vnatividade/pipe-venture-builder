// Engine da fatia vertical: orquestração determinística do workflow idea-to-intake.
// O engine decide COM BASE NO ESTADO (máquina de estados + gates); o agente executa
// tarefa delimitada; o reviewer é advisory; o humano entra só em decisão bloqueadora.
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { newId, nowIso, slugify } from './ids.mjs';
import { info, warn } from './log.mjs';
import { assertEnabled } from './flag.mjs';
import { assertContract } from './contracts.mjs';
import { applyTransition } from './state-machine.mjs';
import { makeEmitter } from './events.mjs';
import { loadContext } from './context-loader.mjs';
import { ArtifactManager } from './artifact-manager.mjs';
import { DecisionQueue } from './decisions.mjs';
import { runIntakeAgent } from '../agents/intake-agent.mjs';
import { runIntakeReviewer } from '../reviewers/intake-reviewer.mjs';
import { runIntakeCompletenessGate } from '../gates/intake-completeness-gate.mjs';

const RUNTIME_DIR = join(dirname(fileURLToPath(import.meta.url)), '..');

export function loadWorkflowDef(workflowId) {
  const def = JSON.parse(readFileSync(join(RUNTIME_DIR, 'workflows', `${workflowId}.definition.json`), 'utf8'));
  return assertContract('Workflow', def);
}

export function loadAgentDef(agentId) {
  const def = JSON.parse(readFileSync(join(RUNTIME_DIR, 'agents', `${agentId}.definition.json`), 'utf8'));
  return assertContract('AgentDefinition', def);
}

// ---------- criação de projeto ----------
export function createProject({ store, name, description = '', ideaText, correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  if (!ideaText?.trim()) throw Object.assign(new Error('a ideia inicial não pode ser vazia'), { code: 'INVALID_INPUT' });
  const slug = slugify(name);
  if (store.projectExists(slug)) {
    const err = new Error(`projeto "${slug}" já existe (idempotência: criação não duplica; use show/run para continuar)`);
    err.code = 'DUPLICATE_PROJECT';
    throw err;
  }
  const ts = nowIso();
  const project = {
    id: newId('prj'), name, slug, description,
    current_state: 'CREATED', current_phase: 'intake', status: 'active',
    state_version: 1,
    next_action: { action: 'executar workflow idea-to-intake', command: `run --project ${slug}` },
    blockers: [], artifact_refs: [], decision_refs: [], run_refs: [],
    previous_state: null, created_at: ts, updated_at: ts,
  };
  assertContract('Project', project);
  store.initProject(project);
  store.writeSource(slug, 'idea-v1.md', ideaText.trim() + '\n');
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });
  emit('ProjectCreated', { name, slug, idea_chars: ideaText.length });
  info('project.created', { project_id: project.id, slug, correlation_id: correlationId });
  return project;
}

// ---------- transição persistida ----------
function transition(store, project, event, ctx, { emit, runId = null, gateResultId = null }) {
  const record = applyTransition(project, event, ctx);
  record.run_id = runId;
  record.gate_result_id = gateResultId;
  assertContract('Project', project);
  store.saveProject(project, project.state_version);
  store.appendTransition(project.slug, record);
  return record;
}

// ---------- execução / retomada do workflow ----------
export function executeWorkflow({ store, slug, workflowId = 'idea-to-intake', correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  const startedAt = Date.now();
  let project = store.loadProject(slug);
  const workflowDef = loadWorkflowDef(workflowId);
  const agentId = workflowDef.allowed_agents[0];
  const agentDef = loadAgentDef(agentId);
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });
  const decisions = new DecisionQueue(store);
  const artifacts = new ArtifactManager(store);

  // Estados que não permitem execução direta.
  if (project.current_state === 'WAITING_HUMAN') {
    const pending = decisions.listPending(slug).map((d) => d.id);
    const err = new Error(`projeto aguardando decisão humana (${pending.join(', ')}); responda antes de retomar`);
    err.code = 'WAITING_HUMAN';
    throw err;
  }
  if (project.current_state === 'PAUSED') {
    const err = new Error('projeto pausado; use o comando resume');
    err.code = 'PAUSED';
    throw err;
  }
  if (project.current_state === 'PRODUCT_STRATEGY_READY') {
    const err = new Error('intake já concluído; próxima fase: product_strategy (fora do escopo desta fatia)');
    err.code = 'ALREADY_DONE';
    throw err;
  }
  if (['FAILED', 'CANCELLED'].includes(project.current_state)) {
    const err = new Error(`projeto em estado terminal: ${project.current_state}`);
    err.code = 'TERMINAL_STATE';
    throw err;
  }

  // Run: reutiliza run ativa do workflow (idempotência) ou cria nova.
  let run = store.listRuns(slug).find((r) => r.workflow_id === workflowId && ['running', 'resuming', 'waiting_human'].includes(r.status));
  const isNewRun = !run;
  if (isNewRun) {
    run = {
      id: newId('run'), project_id: project.id, workflow_id: workflowId, phase: 'intake',
      status: 'running', agent_id: agentId, current_step: null, attempt: 1,
      started_at: nowIso(), completed_at: null, error: null, result: null,
      costs: { tokens: null, cost: null, model: 'deterministic/rule-based@0.1.0', latency_ms: null, tool_calls: null },
      events: [], context_log: null,
    };
    assertContract('Run', run);
  } else {
    run.status = 'running';
  }
  const track = (evt) => { run.events.push(evt.id); };
  const step = (id) => { run.current_step = id; store.saveRun(slug, run); track(emit('StepStarted', { step: id, attempt: run.attempt }, { runId: run.id })); };

  if (isNewRun) {
    if (!project.run_refs.includes(run.id)) project.run_refs.push(run.id);
    track(emit('RunCreated', { workflow_id: workflowId, run_id: run.id }, { runId: run.id }));
    track(emit('PhaseStarted', { phase: 'intake' }, { runId: run.id }));
  } else {
    track(emit('WorkflowResumed', { run_id: run.id, reason: 'continuação de run ativa' }, { runId: run.id }));
  }
  track(emit('AgentAssigned', { agent_id: agentId, agent_version: agentDef.version }, { runId: run.id }));
  store.saveRun(slug, run);

  if (project.current_state === 'CREATED') {
    transition(store, project, 'START_INTAKE', { hasIdeaSource: store.listSources(slug).length > 0 }, { emit, runId: run.id });
  }

  const maxAttempts = workflowDef.max_attempts ?? 2;

  while (true) {
    try {
      // 1. contexto
      step('load_context');
      const context = loadContext({ store, slug, project, workflowDef, agentDef, task: 'gerar initial-brief' });
      run.context_log = { documents: context.documents, omitted: context.omitted, used_chars: context.used_chars, limit_chars: context.limit_chars };
      track(emit('ContextLoaded', run.context_log, { runId: run.id }));

      // 2. agente
      step('run_agent');
      const sources = store.listSources(slug);
      const agentOut = runIntakeAgent({ sources, agentDef });

      // 3. artefato versionado
      step('create_artifact');
      const content = JSON.stringify({ brief: agentOut.brief, assumptions: agentOut.assumptions, metadata: agentOut.metadata }, null, 2) + '\n';
      const { artifact, deduplicated } = artifacts.register({
        slug, projectId: project.id, runId: run.id, phase: 'intake',
        type: 'initial-brief', filename: 'initial-brief.json', content,
        createdBy: 'venture-os-runtime', agentId, model: agentOut.metadata.model,
        promptVersion: agentOut.metadata.prompt_version, sourceRefs: sources.map((s) => `sources/${s.name}`),
      });
      if (!deduplicated) {
        const renderRel = `initial-brief/v${artifact.version}/initial-brief.md`;
        store.writeArtifactFile(slug, renderRel, agentOut.markdown);
        artifact.render_path = `artifacts/${renderRel}`;
        const manifest = store.loadManifest(slug);
        manifest.artifacts.find((a) => a.id === artifact.id).render_path = artifact.render_path;
        store.saveManifest(slug, manifest);
      }
      assertContract('ArtifactManifestEntry', artifact);
      if (!project.artifact_refs.includes(artifact.id)) project.artifact_refs.push(artifact.id);
      track(emit('ArtifactCreated', { artifact_id: artifact.id, type: artifact.type, version: artifact.version, hash: artifact.hash, deduplicated }, { runId: run.id }));

      if (project.current_state === 'INTAKE_IN_PROGRESS') {
        transition(store, project, 'BRIEF_PRODUCED', { briefArtifactValid: true }, { emit, runId: run.id });
      }

      // 4. reviewer (advisory)
      step('review');
      const sourceText = sources.map((s) => s.content).join('\n');
      const review = runIntakeReviewer({ brief: agentOut.brief, sourceText });

      // 5. gate determinístico
      step('gate');
      const gateResult = runIntakeCompletenessGate({
        brief: agentOut.brief, sourceText,
        nextActionPlanned: workflowDef.next_phase_on_success,
        reviewerFindings: review.findings,
        projectId: project.id, runId: run.id,
      });
      assertContract('GateResult', gateResult);
      artifacts.attachValidation(slug, artifact.id, {
        gate_result_id: gateResult.id, gate_id: gateResult.gate_id, status: gateResult.status,
        score: gateResult.score, failures: gateResult.failures.length, warnings: gateResult.warnings.length,
        reviewer: { id: review.reviewer_id, findings: review.findings.length },
      });
      track(emit('ArtifactValidated', { artifact_id: artifact.id, gate_result_id: gateResult.id, status: gateResult.status }, { runId: run.id }));

      if (gateResult.status !== 'fail') {
        // ---- caminho de sucesso ----
        track(emit('GatePassed', { gate_result_id: gateResult.id, score: gateResult.score, warnings: gateResult.warnings.length }, { runId: run.id }));
        transition(store, project, 'GATE_PASSED', { gateStatus: gateResult.status }, { emit, runId: run.id, gateResultId: gateResult.id });

        step('prepare_next');
        const nonBlocking = agentOut.brief.decisoes_abertas.filter((d) => !d.blocking);
        project.next_action = {
          ...workflowDef.next_phase_on_success,
          dependencies: [`initial-brief v${artifact.version} aprovado (${artifact.id})`],
          blockers: [],
          advisories: nonBlocking.map((d) => d.topic),
          human_intervention_required: false,
        };
        transition(store, project, 'PREPARE_NEXT_PHASE', { blockingDecisionsPending: 0 }, { emit, runId: run.id });
        track(emit('PhaseCompleted', { phase: 'intake', next: project.next_action }, { runId: run.id }));

        run.status = 'completed';
        run.completed_at = nowIso();
        run.current_step = null;
        run.costs.latency_ms = Date.now() - startedAt;
        run.result = { artifact_id: artifact.id, gate: summarizeGate(gateResult), next_action: project.next_action };
        store.saveRun(slug, run);
        return { project, run, artifact, gateResult };
      }

      // ---- gate falhou ----
      track(emit('GateFailed', { gate_result_id: gateResult.id, failures: gateResult.failures.map((f) => f.check) }, { runId: run.id }));
      const inputGaps = gateResult.failures.filter((f) => f.category === 'input_gap' || f.category === 'unsupported_claims');

      if (inputGaps.length > 0) {
        // Falha por lacuna de insumo: agrupar em UMA decisão humana bloqueadora.
        const { decision, deduplicated: dedupDec } = decisions.request({
          slug, projectId: project.id, runId: run.id, phase: 'intake',
          priority: 'P1', category: 'input_gap',
          reasonCode: `intake_gaps:${inputGaps.map((f) => f.check).sort().join(',')}`,
          context: `O intake-agent normalizou a ideia sem inventar conteúdo e o gate de completude reprovou o brief v${artifact.version}. Lacunas: ${inputGaps.map((f) => f.message).join(' ')}`,
          reason: 'O agente é proibido de inventar requisitos; os insumos faltantes só podem vir de você.',
          impact: 'O workflow idea-to-intake fica pausado. Nenhum outro fluxo é afetado (fatia única).',
          options: [
            { id: 'provide-info', label: 'Fornecer as informações faltantes em texto livre', consequences: 'O texto vira fonte clarification-vN.md; o brief é regenerado (v seguinte) e o gate reexecuta.' },
            { id: 'cancel-project', label: 'Cancelar o projeto', consequences: 'Projeto vai para CANCELLED (terminal); nada é apagado.' },
          ],
          recommendation: { option_id: 'provide-info', rationale: 'A ideia tem potencial de ser destravada com poucos parágrafos cobrindo as lacunas apontadas.' },
          safeDefault: 'Permanecer em WAITING_HUMAN. Silêncio ou timeout NUNCA aprovam (política do pipe).',
          expectedResponse: { type: 'option', requires_free_text: true, free_text_hint: 'Descreva o problema e/ou a solução imaginada.' },
          blockedScope: { blocked: ['workflow idea-to-intake deste projeto'], not_blocked: ['outros projetos', 'consultas de leitura'] },
        });
        assertContract('HumanDecisionRequest', decision);
        if (!project.decision_refs.includes(decision.id)) project.decision_refs.push(decision.id);
        if (!project.blockers.includes(decision.id)) project.blockers.push(decision.id);
        track(emit('HumanDecisionRequested', { decision_id: decision.id, reason_code: decision.reason_code, deduplicated: dedupDec }, { runId: run.id }));
        transition(store, project, 'HUMAN_DECISION_REQUESTED', { blockingDecisionsPending: 1 }, { emit, runId: run.id, gateResultId: gateResult.id });
        track(emit('WorkflowPaused', { reason: 'aguardando decisão humana', decision_id: decision.id }, { runId: run.id }));

        run.status = 'waiting_human';
        run.current_step = null;
        run.result = { artifact_id: artifact.id, gate: summarizeGate(gateResult), pending_decision: decision.id };
        store.saveRun(slug, run);
        return { project, run, artifact, gateResult, decision };
      }

      // Falha estrutural (sem lacuna de insumo): retry limitado.
      if (run.attempt < maxAttempts) {
        warn('gate.structural_fail.retry', { run_id: run.id, attempt: run.attempt });
        transition(store, project, 'GATE_FAILED_RETRY', { gateStatus: 'fail' }, { emit, runId: run.id, gateResultId: gateResult.id });
        run.attempt += 1;
        store.saveRun(slug, run);
        continue;
      }
      return failRun({ store, slug, project, run, emit, error: { code: 'RETRY_EXHAUSTED', message: `gate estrutural reprovou após ${run.attempt} tentativa(s)`, gate_result_id: gateResult.id } });
    } catch (err) {
      if (err.code === 'INVALID_TRANSITION' || err.code === 'VERSION_CONFLICT' || err.code === 'CONTRACT_VIOLATION') throw err;
      if (run.attempt < maxAttempts) {
        warn('step.error.retry', { run_id: run.id, step: run.current_step, attempt: run.attempt, error: String(err.message) });
        run.attempt += 1;
        store.saveRun(slug, run);
        continue;
      }
      return failRun({ store, slug, project, run, emit, error: { code: err.code ?? 'STEP_ERROR', message: String(err.message), step: run.current_step } });
    }
  }
}

function failRun({ store, slug, project, run, emit, error }) {
  transition(store, project, 'FAIL', { retryExhausted: true }, { emit, runId: run.id });
  const evt = emit('WorkflowFailed', { error }, { runId: run.id });
  run.events.push(evt.id);
  run.status = 'failed';
  run.completed_at = nowIso();
  run.error = error;
  store.saveRun(slug, run);
  return { project, run, error };
}

function summarizeGate(g) {
  return { gate_result_id: g.id, gate_id: g.gate_id, status: g.status, score: g.score, failures: g.failures.length, warnings: g.warnings.length, next_action: g.next_action };
}

// ---------- resposta humana ----------
export function respondDecision({ store, slug, decisionId, optionId, freeText = null, decidedBy, correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  let project = store.loadProject(slug);
  const decisions = new DecisionQueue(store);
  const decision = decisions.respond({ slug, decisionId, optionId, freeText, decidedBy });
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });
  emit('HumanDecisionReceived', { decision_id: decision.id, option_id: optionId, decided_by: decidedBy }, { runId: decision.run_id });

  project.blockers = project.blockers.filter((b) => b !== decision.id);
  const run = store.loadRun(slug, decision.run_id);

  if (optionId === 'cancel-project') {
    transition(store, project, 'CANCEL', {}, { emit, runId: decision.run_id });
    run.status = 'cancelled';
    run.completed_at = nowIso();
    store.saveRun(slug, run);
    return { project, decision, run };
  }

  // provide-info: o texto vira nova fonte e a execução volta a INTAKE_IN_PROGRESS.
  const n = store.listSources(slug).filter((s) => s.name.startsWith('clarification-')).length + 2;
  store.writeSource(slug, `clarification-v${n}.md`, (freeText ?? '').trim() + '\n');
  transition(store, project, 'HUMAN_DECISION_RECEIVED', { decisionResolved: true }, { emit, runId: decision.run_id });
  emit('WorkflowResumed', { decision_id: decision.id, new_source: `clarification-v${n}.md` }, { runId: decision.run_id });
  run.status = 'resuming';
  store.saveRun(slug, run);
  project.next_action = { action: 'retomar workflow idea-to-intake', command: `resume --project ${slug}` };
  store.saveProject(project, project.state_version);
  return { project, decision, run };
}

// ---------- pausa / retomada / cancelamento ----------
export function pauseProject({ store, slug, reason = 'pausa solicitada', correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  const project = store.loadProject(slug);
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });
  transition(store, project, 'PAUSE', {}, { emit });
  emit('WorkflowPaused', { reason });
  return project;
}

export function resumeProject({ store, slug, correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  let project = store.loadProject(slug);
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });
  if (project.current_state === 'PAUSED') {
    transition(store, project, 'RESUME', {}, { emit });
    emit('WorkflowResumed', { from: 'PAUSED', to: project.current_state });
  }
  if (['CREATED', 'INTAKE_IN_PROGRESS'].includes(project.current_state)) {
    return executeWorkflow({ store, slug, correlationId, env });
  }
  return { project };
}

export function cancelProject({ store, slug, correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  const project = store.loadProject(slug);
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });
  transition(store, project, 'CANCEL', {}, { emit });
  return project;
}
