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
import { loadBaselineFile, seedMarkdownFromBaseline, writeBaselineVersion, latestBaselineVersion, emitUpdatedBaseline, loadProjectBaseline, validateBaseline } from './baseline-bridge.mjs';
import { compilePromptPackage, COMPILER_VERSION } from './prompt-compiler.mjs';
import { runStrategyReviewer } from '../reviewers/strategy-reviewer.mjs';
import { runStrategyCompletenessGate } from '../gates/strategy-completeness-gate.mjs';
import { runMvpCompletenessGate } from '../gates/mvp-completeness-gate.mjs';

const PHASE_GATES = { 'strategy-completeness-gate': runStrategyCompletenessGate, 'mvp-completeness-gate': runMvpCompletenessGate };
import { basename } from 'node:path';

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

// ---------- criação de projeto a partir de ProductBaseline canônico (fatia 2) ----------
export function createProjectFromBaseline({ store, baselinePath, correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  const { baseline, hash } = loadBaselineFile(baselinePath);
  const slug = /^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$/.test(baseline.product.productId)
    ? baseline.product.productId
    : slugify(baseline.product.name);
  if (store.projectExists(slug)) {
    const err = new Error(`projeto "${slug}" já existe (idempotência: baseline não re-importado; use show/run)`);
    err.code = 'DUPLICATE_PROJECT';
    throw err;
  }
  const ts = nowIso();
  const project = {
    id: newId('prj'), name: baseline.product.name, slug,
    description: baseline.product.summary ?? '',
    current_state: 'CREATED', current_phase: 'intake', status: 'active',
    state_version: 1,
    next_action: { action: 'executar workflow idea-to-intake', command: `run --project ${slug}` },
    blockers: [], artifact_refs: [], decision_refs: [], run_refs: [],
    previous_state: null, created_at: ts, updated_at: ts,
    baseline_ref: { baseline_id: baseline.baselineId, imported_from: baselinePath, import_hash: hash, current_version: 1 },
  };
  assertContract('Project', project);
  store.initProject(project);
  store.writeSource(slug, 'baseline-import.md', seedMarkdownFromBaseline(baseline));
  writeBaselineVersion(store, slug, baseline);
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });
  emit('ProjectCreated', { name: project.name, slug, from_baseline: baseline.baselineId, import_hash: hash });
  info('project.created_from_baseline', { project_id: project.id, slug, baseline_id: baseline.baselineId, correlation_id: correlationId });
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
    const err = new Error(`intake já concluído; inicie a estratégia com: run-phase --project ${slug}`);
    err.code = 'ALREADY_DONE';
    throw err;
  }
  if (/_(IN_PROGRESS|REVIEW|APPROVED)$/.test(project.current_state) && !project.current_state.startsWith('INTAKE')) {
    const err = new Error('fase de estratégia em andamento; use run-phase/submit');
    err.code = 'USE_RUN_PHASE';
    throw err;
  }
  if (['MVP_REFINEMENT_READY', 'UX_ARCHITECTURE_READY'].includes(project.current_state)) {
    const err = new Error(`fase anterior concluída; use run-phase --project ${slug} --workflow <workflow>`);
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

        // Fatia 2: se o projeto foi semeado de um baseline canônico, emite a
        // atualização (lifecycle → founder_focus, brief em artifacts, aprovações).
        let baselineUpdate = null;
        if (latestBaselineVersion(store, slug) > 0) {
          const resolved = store.listDecisions(slug);
          baselineUpdate = emitUpdatedBaseline({ store, slug, artifact, gateResult, decisions: resolved });
          if (baselineUpdate.emitted) {
            project.baseline_ref = { ...(project.baseline_ref ?? {}), current_version: baselineUpdate.version };
            store.saveProject(project, project.state_version);
            track(emit('ArtifactCreated', { kind: 'product-baseline', baseline_id: baselineUpdate.baselineId, baseline_version: baselineUpdate.version, path: baselineUpdate.path }, { runId: run.id }));
          } else {
            warn('baseline.emit_skipped', { run_id: run.id, reason: baselineUpdate.reason });
          }
        }

        run.status = 'completed';
        run.completed_at = nowIso();
        run.current_step = null;
        run.costs.latency_ms = Date.now() - startedAt;
        run.result = { artifact_id: artifact.id, gate: summarizeGate(gateResult), next_action: project.next_action, baseline_update: baselineUpdate };
        store.saveRun(slug, run);
        return { project, run, artifact, gateResult, baselineUpdate };
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

  // provide-info: o texto vira nova fonte e a execução volta ao estado de execução da fase ($resume).
  const n = store.listSources(slug).filter((s) => s.name.startsWith('clarification-')).length + 2;
  store.writeSource(slug, `clarification-v${n}.md`, (freeText ?? '').trim() + '\n');
  transition(store, project, 'HUMAN_DECISION_RECEIVED', { decisionResolved: true }, { emit, runId: decision.run_id });
  emit('WorkflowResumed', { decision_id: decision.id, new_source: `clarification-v${n}.md` }, { runId: decision.run_id });
  if (/_IN_PROGRESS$/.test(project.current_state) && !project.current_state.startsWith('INTAKE')) {
    run.status = 'awaiting_executor';
    project.next_action = { action: 'executor corrige e reenvia os artefatos de estratégia considerando a clarificação', command: `submit --project ${slug} --files <arquivos corrigidos>` };
  } else {
    run.status = 'resuming';
    project.next_action = { action: 'retomar workflow idea-to-intake', command: `resume --project ${slug}` };
  }
  store.saveRun(slug, run);
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

// ---------- fase product-strategy (padrão genérico de fase, fatia 3) ----------
export function startPhase({ store, slug, workflowId = 'product-strategy', correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  let project = store.loadProject(slug);
  const workflowDef = loadWorkflowDef(workflowId);
  const agentDef = loadAgentDef(workflowDef.allowed_agents[0]);
  const artifacts = new ArtifactManager(store);
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });

  // Idempotência: fase já em andamento → devolve o pacote e a run existentes.
  if (project.current_state === workflowDef.in_progress_state) {
    const pkg = artifacts.current(slug, `prompt-package-${workflowId}`);
    const run = store.listRuns(slug).find((r) => r.workflow_id === workflowId && ['awaiting_executor', 'running'].includes(r.status));
    return { project, run, packageArtifact: pkg, idempotent: true };
  }
  if (project.current_state !== workflowDef.entry_state) {
    const err = new Error(`fase ${workflowId} exige estado ${workflowDef.entry_state}; atual: ${project.current_state}`);
    err.code = 'INVALID_PHASE_START';
    throw err;
  }

  const pkg = compilePromptPackage({ store, slug, project, workflowDef, agentDef, artifacts });
  const { artifact: packageArtifact } = artifacts.register({
    slug, projectId: project.id, runId: null, phase: workflowDef.phase_key,
    type: `prompt-package-${workflowId}`, filename: 'prompt-package.md', content: pkg.markdown,
    createdBy: 'prompt-compiler', agentId: agentDef.id, model: `prompt-compiler@${COMPILER_VERSION}`,
    promptVersion: agentDef.version, sourceRefs: pkg.metadata.refs.map((r) => r.name),
  });

  const run = {
    id: newId('run'), project_id: project.id, workflow_id: workflowId, phase: workflowDef.phase_key,
    status: 'awaiting_executor', agent_id: agentDef.id, current_step: 'await_executor', attempt: 1,
    started_at: nowIso(), completed_at: null, error: null, result: null,
    costs: { tokens: null, cost: null, model: agentDef.executor ?? 'claude-code', latency_ms: null, tool_calls: null },
    events: [], context_log: { documents: pkg.metadata.refs, omitted: [], used_chars: pkg.metadata.chars, limit_chars: null },
  };
  assertContract('Run', run);
  project.run_refs.push(run.id);
  if (!project.artifact_refs.includes(packageArtifact.id)) project.artifact_refs.push(packageArtifact.id);
  const track = (evt) => run.events.push(evt.id);
  track(emit('RunCreated', { workflow_id: workflowId, run_id: run.id }, { runId: run.id }));
  track(emit('PhaseStarted', { phase: workflowDef.phase_key }, { runId: run.id }));
  track(emit('AgentAssigned', { agent_id: agentDef.id, agent_version: agentDef.version, executor: agentDef.executor }, { runId: run.id }));
  track(emit('ContextLoaded', run.context_log, { runId: run.id }));
  track(emit('ArtifactCreated', { artifact_id: packageArtifact.id, type: packageArtifact.type, version: packageArtifact.version, hash: packageArtifact.hash }, { runId: run.id }));
  track(emit('StepStarted', { step: 'await_executor', attempt: 1 }, { runId: run.id }));
  store.saveRun(slug, run);

  project.next_action = {
    action: `executor ${agentDef.executor ?? 'claude-code'} produz ${workflowDef.outputs.map((o) => o + '.md').join(' e ')} conforme o pacote`,
    command: `submit --project ${slug} --files <caminhos>`,
    package: packageArtifact.path,
  };
  transition(store, project, 'START_PHASE', { promptPackageReady: true }, { emit, runId: run.id });
  return { project, run, packageArtifact, packageMarkdown: pkg.markdown };
}

function advanceBaselineAfterPhase({ store, slug, registered, gateResult, advance }) {
  const current = loadProjectBaseline(store, slug);
  if (!current) return { emitted: false, reason: 'projeto sem baseline importado' };
  const b = structuredClone(current.baseline);
  b.generatedAt = nowIso();
  b.lifecycle.currentStage = advance.currentStage;
  b.lifecycle.nextAllowedStage = advance.nextAllowedStage;
  for (const art of registered) {
    const artifactId = `ART-${art.type}-v${art.version}`;
    if (!b.artifacts.some((a) => a.artifactId === artifactId)) {
      b.artifacts.push({
        artifactId, artifactType: 'product_context',
        title: `${art.type} v${art.version} (venture-os phase loop)`,
        status: 'present', sourceRef: art.path, externalRef: null, provenanceStatementIds: [],
      });
    }
  }
  b.approvals.push({
    action: `${gateResult.gate_id} ${gateResult.status} (venture-os loop, score ${gateResult.score})`,
    required: true, status: 'granted', sourceRef: gateResult.id,
  });
  b.nextActions = [{
    actionId: advance.nextActionId,
    title: advance.nextActionTitle,
    ownerRole: advance.nextActionOwner ?? 'Product Strategist', priority: 'P2', blockedByGapIds: [],
    approvalRequired: true, suggestedCommand: null,
  }];
  const validation = validateBaseline(b);
  if (!validation.valid) return { emitted: false, reason: `baseline atualizado inválido: ${validation.errors?.slice(0, 2).join('; ')}` };
  const { version, path } = writeBaselineVersion(store, slug, b);
  return { emitted: true, version, path };
}

export function submitPhaseArtifacts({ store, slug, files, workflowId = 'product-strategy', correlationId = newId('cor'), env = process.env }) {
  assertEnabled(env);
  let project = store.loadProject(slug);
  const workflowDef = loadWorkflowDef(workflowId);
  if (project.current_state !== workflowDef.in_progress_state) {
    const err = new Error(`submissão exige ${workflowDef.in_progress_state}; atual: ${project.current_state}`);
    err.code = 'INVALID_PHASE_STATE';
    throw err;
  }
  const agentDef = loadAgentDef(workflowDef.allowed_agents[0]);
  const artifacts = new ArtifactManager(store);
  const decisions = new DecisionQueue(store);
  const emit = makeEmitter(store, { projectId: project.id, slug, correlationId });
  const run = store.listRuns(slug).find((r) => r.workflow_id === workflowId && ['awaiting_executor', 'running'].includes(r.status));
  if (!run) throw Object.assign(new Error('nenhuma run aguardando executor para esta fase'), { code: 'NO_ACTIVE_RUN' });
  const track = (evt) => run.events.push(evt.id);
  run.status = 'running';
  run.current_step = 'register_artifacts';
  track(emit('StepStarted', { step: 'register_artifacts', attempt: run.attempt }, { runId: run.id }));

  const contents = {};
  const registered = [];
  for (const filePath of files) {
    const type = basename(filePath).replace(/\.md$/i, '');
    if (!workflowDef.outputs.includes(type)) {
      throw Object.assign(new Error(`saída "${type}" não permitida; esperadas: ${workflowDef.outputs.join(', ')}`), { code: 'INVALID_INPUT' });
    }
    const content = readFileSync(filePath, 'utf8');
    contents[type] = content;
    const { artifact } = artifacts.register({
      slug, projectId: project.id, runId: run.id, phase: workflowDef.phase_key,
      type, filename: `${type}.md`, content,
      createdBy: agentDef.executor ?? 'claude-code', agentId: agentDef.id,
      model: `${agentDef.executor ?? 'claude-code'}/interactive`, promptVersion: agentDef.version,
      sourceRefs: [artifacts.current(slug, `prompt-package-${workflowId}`)?.path].filter(Boolean),
    });
    registered.push(artifact);
    if (!project.artifact_refs.includes(artifact.id)) project.artifact_refs.push(artifact.id);
    track(emit('ArtifactCreated', { artifact_id: artifact.id, type, version: artifact.version }, { runId: run.id }));
  }
  const complete = workflowDef.outputs.every((o) => contents[o]);
  transition(store, project, 'PHASE_ARTIFACTS_SUBMITTED', { phaseArtifactsValid: complete }, { emit, runId: run.id });

  run.current_step = 'review';
  const sourceText = [
    store.listSources(slug).map((s) => s.content).join('\n'),
    artifacts.current(slug, 'initial-brief') ? store.readArtifactFile(slug, artifacts.current(slug, 'initial-brief').path.replace(/^artifacts\//, '')) : '',
    JSON.stringify(loadProjectBaseline(store, slug)?.baseline ?? {}),
  ].join('\n');
  const review = runStrategyReviewer({ files: contents, sourceText });

  run.current_step = 'gate';
  track(emit('StepStarted', { step: 'gate', attempt: run.attempt }, { runId: run.id }));
  const gateResult = (PHASE_GATES[workflowDef.gates[0]] ?? runStrategyCompletenessGate)({
    files: contents, nextActionPlanned: workflowDef.next_phase_on_success,
    reviewerFindings: review.findings, projectId: project.id, runId: run.id,
  });
  assertContract('GateResult', gateResult);
  for (const art of registered) {
    artifacts.attachValidation(slug, art.id, {
      gate_result_id: gateResult.id, gate_id: gateResult.gate_id, status: gateResult.status,
      score: gateResult.score, failures: gateResult.failures.length, warnings: gateResult.warnings.length,
      reviewer: { id: review.reviewer_id, findings: review.findings.length },
    });
    track(emit('ArtifactValidated', { artifact_id: art.id, gate_result_id: gateResult.id, status: gateResult.status }, { runId: run.id }));
  }

  if (gateResult.status !== 'fail') {
    track(emit('GatePassed', { gate_result_id: gateResult.id, score: gateResult.score }, { runId: run.id }));
    transition(store, project, 'GATE_PASSED', { gateStatus: gateResult.status }, { emit, runId: run.id, gateResultId: gateResult.id });
    run.current_step = 'prepare_next';
    const baselineUpdate = workflowDef.baseline_advance ? advanceBaselineAfterPhase({ store, slug, registered, gateResult, advance: workflowDef.baseline_advance }) : { emitted: false, reason: 'workflow sem baseline_advance' };
    project.next_action = {
      ...workflowDef.next_phase_on_success,
      dependencies: registered.map((a) => `${a.type} v${a.version} aprovado (${a.id})`),
      blockers: [], human_intervention_required: false,
    };
    transition(store, project, 'PREPARE_NEXT_PHASE', { blockingDecisionsPending: 0 }, { emit, runId: run.id });
    track(emit('PhaseCompleted', { phase: workflowDef.phase_key, next: project.next_action, baseline: baselineUpdate }, { runId: run.id }));
    run.status = 'completed';
    run.completed_at = nowIso();
    run.current_step = null;
    run.result = { artifacts: registered.map((a) => a.id), gate: { gate_result_id: gateResult.id, status: gateResult.status, score: gateResult.score }, baseline: baselineUpdate, next_action: project.next_action };
    store.saveRun(slug, run);
    return { project, run, registered, gateResult, baselineUpdate };
  }

  track(emit('GateFailed', { gate_result_id: gateResult.id, failures: gateResult.failures.map((f) => f.check) }, { runId: run.id }));
  const inputGaps = gateResult.failures.filter((f) => ['input_gap', 'unsupported_claims'].includes(f.category));
  if (inputGaps.length > 0 && run.attempt >= (workflowDef.max_attempts ?? 2)) {
    // Correção pelo executor esgotada: escala para decisão humana.
    const { decision } = decisions.request({
      slug, projectId: project.id, runId: run.id, phase: workflowDef.phase_key,
      priority: 'P1', category: 'input_gap',
      reasonCode: `${workflowDef.phase_key}_gaps:${inputGaps.map((f) => f.check).sort().join(',')}`,
      context: `O gate de estratégia reprovou após ${run.attempt} tentativa(s) do executor. Falhas: ${inputGaps.map((f) => f.message).join(' ')}`,
      reason: 'O executor não pode inventar o insumo faltante; correção exige orientação ou conteúdo do fundador.',
      impact: 'A fase de estratégia deste projeto fica pausada; nada mais é afetado.',
      options: [
        { id: 'provide-info', label: 'Fornecer orientação/insumo em texto livre', consequences: 'Vira clarification-vN.md; o executor corrige e reenvia.' },
        { id: 'cancel-project', label: 'Cancelar o projeto', consequences: 'Projeto vai para CANCELLED; nada é apagado.' },
      ],
      recommendation: { option_id: 'provide-info', rationale: 'As falhas apontam exatamente o que falta.' },
      safeDefault: 'Permanecer em WAITING_HUMAN. Silêncio ou timeout NUNCA aprovam.',
      expectedResponse: { type: 'option', requires_free_text: true },
      blockedScope: { blocked: [`fase ${workflowDef.phase_key} de ${slug}`], not_blocked: ['outros projetos', 'leitura'] },
    });
    assertContract('HumanDecisionRequest', decision);
    if (!project.decision_refs.includes(decision.id)) project.decision_refs.push(decision.id);
    if (!project.blockers.includes(decision.id)) project.blockers.push(decision.id);
    track(emit('HumanDecisionRequested', { decision_id: decision.id, reason_code: decision.reason_code }, { runId: run.id }));
    transition(store, project, 'HUMAN_DECISION_REQUESTED', { blockingDecisionsPending: 1 }, { emit, runId: run.id, gateResultId: gateResult.id });
    track(emit('WorkflowPaused', { reason: 'aguardando decisão humana', decision_id: decision.id }, { runId: run.id }));
    run.status = 'waiting_human';
    run.current_step = null;
    run.result = { gate: { gate_result_id: gateResult.id, status: 'fail' }, pending_decision: decision.id };
    store.saveRun(slug, run);
    return { project, run, registered, gateResult, decision };
  }

  // Reprovou mas ainda há tentativa: devolve ao executor com as correções recomendadas.
  transition(store, project, 'GATE_FAILED_RETRY', { gateStatus: 'fail' }, { emit, runId: run.id, gateResultId: gateResult.id });
  run.attempt += 1;
  run.status = 'awaiting_executor';
  run.current_step = 'await_executor';
  store.saveRun(slug, run);
  project.next_action = {
    action: `executor corrige (${gateResult.recommended_actions.join('; ')}) e reenvia`,
    command: `submit --project ${slug} --files <arquivos corrigidos>`,
  };
  store.saveProject(project, project.state_version);
  return { project, run, registered, gateResult, retry: true };
}
