// Integração + E2E: ideia → projeto → run → brief → gate → (decisão humana) → retomada → próxima fase.
// Inclui cenários de falha: transição inválida, resposta inválida, duplicação, flag off, retomada pós-interrupção.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Store } from '../lib/store.mjs';
import { createProject, executeWorkflow, respondDecision, pauseProject, resumeProject, cancelProject } from '../lib/engine.mjs';
import { DecisionQueue } from '../lib/decisions.mjs';

process.env.VENTURE_OS_LOG_SILENT = '1';
const ENV = { VENTURE_OS_ENABLED: 'true', VENTURE_OS_LOG_SILENT: '1' };
const mkStore = () => new Store(mkdtempSync(join(tmpdir(), 'vos-e2e-')));

const IDEA_COMPLETA = `Hoje é difícil para barbeiros autônomos saberem quanto lucram por semana, e eles perdem dinheiro sem perceber.
Quero criar uma ferramenta simples para barbeiros que trabalham em barbearia de terceiros.
Funcionalidades:
- cadastrar cada corte e o valor recebido
- relatório semanal de ganhos
Restrições: não pode exigir cadastro complicado.
Risco: concorrência de aplicativos de agenda.`;

const IDEA_VAGA = 'Quero um app legal';

test('E2E caminho feliz: ideia completa chega a PRODUCT_STRATEGY_READY com rastreabilidade', () => {
  const store = mkStore();
  const project = createProject({ store, name: 'Barber Lucro', ideaText: IDEA_COMPLETA, env: ENV });
  assert.equal(project.current_state, 'CREATED');

  const result = executeWorkflow({ store, slug: project.slug, env: ENV });
  assert.equal(result.project.current_state, 'PRODUCT_STRATEGY_READY');
  assert.equal(result.run.status, 'completed');
  assert.notEqual(result.gateResult.status, 'fail');

  // Artefato versionado com hash e proveniência
  assert.equal(result.artifact.type, 'initial-brief');
  assert.equal(result.artifact.version, 1);
  assert.equal(result.artifact.hash.length, 64);
  assert.equal(result.artifact.agent_id, 'intake-agent');

  // Próxima ação determinada automaticamente
  const next = result.project.next_action;
  assert.equal(next.phase, 'product_strategy');
  assert.equal(next.pipe_pipeline_stage, 'founder_focus');
  assert.equal(next.human_intervention_required, false);

  // Rastreabilidade: eventos, transições e validação anexada ao artefato
  const events = store.listEvents(project.slug).map((e) => e.type);
  for (const t of ['ProjectCreated', 'RunCreated', 'PhaseStarted', 'AgentAssigned', 'ContextLoaded', 'ArtifactCreated', 'ArtifactValidated', 'GatePassed', 'PhaseCompleted']) {
    assert.ok(events.includes(t), `evento ausente: ${t}`);
  }
  const transitions = store.listTransitions(project.slug).map((t) => `${t.from}>${t.to}`);
  assert.deepEqual(transitions, ['CREATED>INTAKE_IN_PROGRESS', 'INTAKE_IN_PROGRESS>INTAKE_REVIEW', 'INTAKE_REVIEW>INTAKE_APPROVED', 'INTAKE_APPROVED>PRODUCT_STRATEGY_READY']);
  const manifest = store.loadManifest(project.slug);
  assert.equal(manifest.artifacts[0].validation.status, result.gateResult.status);
  // Correlation id presente em todos os eventos
  assert.ok(store.listEvents(project.slug).every((e) => e.correlation_id));
});

test('E2E com decisão humana: ideia vaga → WAITING_HUMAN → resposta → retomada → aprovado', () => {
  const store = mkStore();
  const project = createProject({ store, name: 'Ideia Vaga', ideaText: IDEA_VAGA, env: ENV });
  const r1 = executeWorkflow({ store, slug: project.slug, env: ENV });

  // Gate falhou por lacuna de insumo → decisão bloqueadora → WAITING_HUMAN
  assert.equal(r1.project.current_state, 'WAITING_HUMAN');
  assert.equal(r1.run.status, 'waiting_human');
  assert.equal(r1.gateResult.status, 'fail');
  assert.ok(r1.decision);
  assert.equal(r1.decision.priority, 'P1');
  assert.ok(r1.decision.safe_default.includes('NUNCA aprovam'));

  // Executar com decisão pendente é recusado (pausa só do fluxo afetado, sem burlar)
  assert.throws(() => executeWorkflow({ store, slug: project.slug, env: ENV }), /aguardando decisão humana/);

  // Reexecutar o pedido não duplica (idempotência da fila)
  assert.equal(new DecisionQueue(store).listPending(project.slug).length, 1);

  // Resposta humana com insumo → INTAKE_IN_PROGRESS
  const resp = respondDecision({
    store, slug: project.slug, decisionId: r1.decision.id, optionId: 'provide-info',
    freeText: 'O problema é que fotógrafos autônomos perdem clientes por não responder orçamentos rápido. A solução imaginada é um app que gera orçamento em um clique.',
    decidedBy: 'vitor', env: ENV,
  });
  assert.equal(resp.project.current_state, 'INTAKE_IN_PROGRESS');
  assert.equal(resp.decision.status, 'resolved');

  // Retomada: novo brief v2 usando a clarificação → gate aprova → pronto p/ estratégia
  const r2 = resumeProject({ store, slug: project.slug, env: ENV });
  assert.equal(r2.project.current_state, 'PRODUCT_STRATEGY_READY');
  assert.equal(r2.artifact.version, 2, 'brief regenerado como v2');
  assert.notEqual(r2.gateResult.status, 'fail');

  const events = store.listEvents(project.slug).map((e) => e.type);
  for (const t of ['GateFailed', 'HumanDecisionRequested', 'WorkflowPaused', 'HumanDecisionReceived', 'WorkflowResumed', 'GatePassed', 'PhaseCompleted']) {
    assert.ok(events.includes(t), `evento ausente: ${t}`);
  }
  // v1 superseded, v2 present
  const arts = store.loadManifest(project.slug).artifacts;
  assert.equal(arts.find((a) => a.version === 1).status, 'superseded');
  assert.equal(arts.find((a) => a.version === 2).status, 'present');
});

test('cenário: cancelamento via decisão humana', () => {
  const store = mkStore();
  const project = createProject({ store, name: 'Vai Cancelar', ideaText: IDEA_VAGA, env: ENV });
  const r1 = executeWorkflow({ store, slug: project.slug, env: ENV });
  const resp = respondDecision({ store, slug: project.slug, decisionId: r1.decision.id, optionId: 'cancel-project', freeText: 'sem tempo agora', decidedBy: 'vitor', env: ENV });
  assert.equal(resp.project.current_state, 'CANCELLED');
  assert.equal(store.loadRun(project.slug, r1.run.id).status, 'cancelled');
  assert.throws(() => executeWorkflow({ store, slug: project.slug, env: ENV }), /terminal/);
});

test('cenário: pause/resume preserva o fluxo', () => {
  const store = mkStore();
  const project = createProject({ store, name: 'Pausavel', ideaText: IDEA_COMPLETA, env: ENV });
  pauseProject({ store, slug: project.slug, env: ENV });
  assert.equal(store.loadProject(project.slug).current_state, 'PAUSED');
  assert.throws(() => executeWorkflow({ store, slug: project.slug, env: ENV }), /pausado/);
  const r = resumeProject({ store, slug: project.slug, env: ENV });
  assert.equal(r.project.current_state, 'PRODUCT_STRATEGY_READY');
});

test('idempotência: projeto duplicado recusado; re-execução após conclusão recusada; artefato não duplica', () => {
  const store = mkStore();
  const project = createProject({ store, name: 'Unico', ideaText: IDEA_COMPLETA, env: ENV });
  assert.throws(() => createProject({ store, name: 'Unico', ideaText: 'outra', env: ENV }), /já existe/);
  executeWorkflow({ store, slug: project.slug, env: ENV });
  assert.throws(() => executeWorkflow({ store, slug: project.slug, env: ENV }), /já concluído/);
  assert.equal(store.loadManifest(project.slug).artifacts.length, 1);
});

test('cenário: retomada após interrupção no meio (run ativa é reutilizada, sem duplicar)', () => {
  const store = mkStore();
  const project = createProject({ store, name: 'Interrompido', ideaText: IDEA_COMPLETA, env: ENV });
  // Simula interrupção: run criada como 'running' e processo morre antes dos steps.
  const half = {
    id: 'run_interrompida', project_id: project.id, workflow_id: 'idea-to-intake', phase: 'intake',
    status: 'running', agent_id: 'intake-agent', current_step: 'load_context', attempt: 1,
    started_at: new Date().toISOString(), completed_at: null, error: null, result: null,
    costs: { tokens: null, cost: null, model: 'x' }, events: [], context_log: null,
  };
  store.saveRun(project.slug, half);
  const result = executeWorkflow({ store, slug: project.slug, env: ENV });
  assert.equal(result.run.id, 'run_interrompida', 'run ativa reutilizada');
  assert.equal(result.run.status, 'completed');
  assert.equal(store.listRuns(project.slug).length, 1, 'nenhuma run duplicada');
});

test('cenário de falha: flag desabilitada bloqueia mutações (comportamento atual preservado)', () => {
  const store = mkStore();
  assert.throws(() => createProject({ store, name: 'Sem Flag', ideaText: IDEA_COMPLETA, env: {} }), /desabilitado/);
  assert.throws(() => executeWorkflow({ store, slug: 'qualquer', env: {} }), /desabilitado/);
});

test('cenário de falha: entrada inválida e resposta humana inválida', () => {
  const store = mkStore();
  assert.throws(() => createProject({ store, name: 'X Y', ideaText: '   ', env: ENV }), /vazia/);
  const project = createProject({ store, name: 'Resposta Invalida', ideaText: IDEA_VAGA, env: ENV });
  const r1 = executeWorkflow({ store, slug: project.slug, env: ENV });
  assert.throws(() => respondDecision({ store, slug: project.slug, decisionId: r1.decision.id, optionId: 'nao-existe', decidedBy: 'v', env: ENV }), /opção inválida/);
  assert.throws(() => respondDecision({ store, slug: project.slug, decisionId: r1.decision.id, optionId: 'provide-info', freeText: '', decidedBy: 'v', env: ENV }), /texto complementar/);
  // Estado permanece WAITING_HUMAN após respostas inválidas
  assert.equal(store.loadProject(project.slug).current_state, 'WAITING_HUMAN');
});
