// Fatia 3: fase product-strategy — máquina, compiler, gate, E2E com executor externo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Store } from '../lib/store.mjs';
import { applyTransition, InvalidTransitionError } from '../lib/state-machine.mjs';
import { createProject, executeWorkflow, startPhase, submitPhaseArtifacts, respondDecision } from '../lib/engine.mjs';
import { runStrategyCompletenessGate } from '../gates/strategy-completeness-gate.mjs';

process.env.VENTURE_OS_LOG_SILENT = '1';
const ENV = { VENTURE_OS_ENABLED: 'true', VENTURE_OS_LOG_SILENT: '1' };
const mkStore = () => new Store(mkdtempSync(join(tmpdir(), 'vos-strategy-')));
const tmp = () => mkdtempSync(join(tmpdir(), 'vos-exec-'));

const IDEA = `Hoje é difícil para pais transformarem fotos dos filhos em algo memorável, e as fotos se perdem.
Quero criar uma plataforma que gera histórias em quadrinho a partir das imagens e contexto que o usuário envia.
Funcionalidades:
- enviar fotos e contexto
- receber a história em quadrinho por e-mail quando o processo terminar
Risco: concorrência de apps de álbum.`;

const GOOD_VISION = `# Visão do produto

## Proposta de valor
- Transformar fotos e contexto enviados pelo usuário em uma história em quadrinho entregue por e-mail (fonte: idea-v1.md#s1)
- O processamento acontece em background e avisa quando termina (fonte: idea-v1.md#s3)

## Público
- Hipótese: pais que querem transformar fotos dos filhos em histórias (fonte: initial-brief v1, publico_mencionado)

## Problema e solução
- Problema: fotos dos filhos se perdem sem virar algo memorável; a solução gera a história em quadrinho automaticamente a partir delas (fonte: idea-v1.md#s0)
`;

const GOOD_HYPS = `# Hipóteses

## Hipóteses
- Pais valorizam receber a história pronta por e-mail em vez de montar manualmente (fonte: idea-v1.md#s3)
- O envio de fotos com contexto é esforço aceitável para o valor recebido (fonte: initial-brief v1, funcionalidades_sugeridas)

## Riscos
- Concorrência de apps de álbum (fonte: idea-v1.md#s4)
- Lacuna: público definitivo ainda é hipótese, não validação (fonte: baseline PB, statements missing)
`;

function readyProject(store) {
  const p = createProject({ store, name: 'HQ Teste', ideaText: IDEA, env: ENV });
  executeWorkflow({ store, slug: p.slug, env: ENV });
  return p.slug;
}

test('máquina: transições da fase de estratégia + retomada mapeada', () => {
  const p = { current_state: 'PRODUCT_STRATEGY_READY', status: 'x', previous_state: null };
  applyTransition(p, 'START_PHASE', { promptPackageReady: true });
  assert.equal(p.current_state, 'PRODUCT_STRATEGY_IN_PROGRESS');
  applyTransition(p, 'PHASE_ARTIFACTS_SUBMITTED', { phaseArtifactsValid: true });
  assert.equal(p.current_state, 'PRODUCT_STRATEGY_REVIEW');
  applyTransition(p, 'HUMAN_DECISION_REQUESTED', { blockingDecisionsPending: 1 });
  assert.equal(p.current_state, 'WAITING_HUMAN');
  applyTransition(p, 'HUMAN_DECISION_RECEIVED', { decisionResolved: true });
  assert.equal(p.current_state, 'PRODUCT_STRATEGY_IN_PROGRESS', 'retomada volta ao IN_PROGRESS da fase');
  applyTransition(p, 'PHASE_ARTIFACTS_SUBMITTED', { phaseArtifactsValid: true });
  applyTransition(p, 'GATE_PASSED', { gateStatus: 'pass' });
  applyTransition(p, 'PREPARE_NEXT_PHASE', { blockingDecisionsPending: 0 });
  assert.equal(p.current_state, 'MVP_REFINEMENT_READY');
  applyTransition(p, 'START_PHASE', { promptPackageReady: true });
  assert.equal(p.current_state, 'MVP_REFINEMENT_IN_PROGRESS', 'fase MVP entra pelo mesmo padrão');
  assert.throws(() => applyTransition({ current_state: 'CLAUDE_DESIGN_PROMPT_READY', previous_state: null }, 'START_PHASE', { promptPackageReady: true }), InvalidTransitionError, 'fase sem workflow ainda não inicia');
});

test('máquina: START_PHASE recusado sem pacote e fora do estado de entrada', () => {
  assert.throws(() => applyTransition({ current_state: 'PRODUCT_STRATEGY_READY', previous_state: null }, 'START_PHASE', {}), InvalidTransitionError);
  assert.throws(() => applyTransition({ current_state: 'INTAKE_REVIEW', previous_state: null }, 'START_PHASE', { promptPackageReady: true }), InvalidTransitionError);
});

test('gate de estratégia: aprova artefatos rastreáveis; reprova invenção e seções ausentes', () => {
  const pass = runStrategyCompletenessGate({ files: { 'product-vision': GOOD_VISION, hypotheses: GOOD_HYPS }, nextActionPlanned: {}, projectId: 'p', runId: 'r' });
  assert.notEqual(pass.status, 'fail');

  const invented = GOOD_VISION + '\n- Mercado de R$ 2 bi validado com clientes\n';
  const failInv = runStrategyCompletenessGate({ files: { 'product-vision': invented, hypotheses: GOOD_HYPS }, nextActionPlanned: {}, projectId: 'p', runId: 'r' });
  assert.equal(failInv.status, 'fail');
  assert.ok(failInv.failures.some((f) => f.check === 'sem_conteudo_inventado'));

  const noPublic = GOOD_VISION.replace(/## Público[\s\S]*?## Problema/, '## Problema');
  const failPub = runStrategyCompletenessGate({ files: { 'product-vision': noPublic, hypotheses: GOOD_HYPS }, nextActionPlanned: {}, projectId: 'p', runId: 'r' });
  assert.equal(failPub.status, 'fail');
  assert.ok(failPub.failures.some((f) => f.check === 'publico_identificavel'));
});

test('E2E estratégia: run-phase compila pacote → submit → aprovado → MVP_REFINEMENT_READY', () => {
  const store = mkStore();
  const slug = readyProject(store);
  const started = startPhase({ store, slug, env: ENV });
  assert.equal(started.project.current_state, 'PRODUCT_STRATEGY_IN_PROGRESS');
  assert.equal(started.run.status, 'awaiting_executor');
  assert.ok(started.packageMarkdown.includes('## Contexto mínimo'));
  assert.ok(started.packageMarkdown.includes('(fonte:'), 'pacote instrui a convenção de rastreabilidade');

  // Idempotência do início da fase
  const again = startPhase({ store, slug, env: ENV });
  assert.ok(again.idempotent);

  const dir = tmp();
  writeFileSync(join(dir, 'product-vision.md'), GOOD_VISION);
  writeFileSync(join(dir, 'hypotheses.md'), GOOD_HYPS);
  const result = submitPhaseArtifacts({ store, slug, files: [join(dir, 'product-vision.md'), join(dir, 'hypotheses.md')], env: ENV });
  assert.equal(result.project.current_state, 'MVP_REFINEMENT_READY');
  assert.equal(result.run.status, 'completed');
  assert.notEqual(result.gateResult.status, 'fail');
  assert.equal(result.project.next_action.phase, 'mvp_refinement');
  assert.equal(result.baselineUpdate.emitted, false, 'sem baseline importado → avanço registrado como não emitido, sem quebrar');
  const events = store.listEvents(slug).map((e) => e.type);
  for (const t of ['PhaseStarted', 'AgentAssigned', 'ContextLoaded', 'ArtifactCreated', 'GatePassed', 'PhaseCompleted']) {
    assert.ok(events.includes(t), `evento ausente: ${t}`);
  }
});

test('E2E estratégia: gate reprova → retry do executor → esgotado → decisão humana → retomada', () => {
  const store = mkStore();
  const slug = readyProject(store);
  startPhase({ store, slug, env: ENV });
  const dir = tmp();
  const bad = '# Visão\n\n## Proposta de valor\n- Vamos dominar o mercado global\n\n## Público\n- Todo mundo\n\n## Problema e solução\n- O problema é resolvido pela solução\n';
  writeFileSync(join(dir, 'product-vision.md'), bad);
  writeFileSync(join(dir, 'hypotheses.md'), '# Hipóteses\n\n## Hipóteses\n- Vai dar certo\n\n## Riscos\n- Nenhum\n');

  const r1 = submitPhaseArtifacts({ store, slug, files: [join(dir, 'product-vision.md'), join(dir, 'hypotheses.md')], env: ENV });
  assert.ok(r1.retry, '1ª reprovação volta ao executor');
  assert.equal(r1.project.current_state, 'PRODUCT_STRATEGY_IN_PROGRESS');
  assert.equal(r1.run.attempt, 2);

  const r2 = submitPhaseArtifacts({ store, slug, files: [join(dir, 'product-vision.md'), join(dir, 'hypotheses.md')], env: ENV });
  assert.equal(r2.project.current_state, 'WAITING_HUMAN', '2ª reprovação escala para humano');
  assert.ok(r2.decision);

  const resp = respondDecision({ store, slug, decisionId: r2.decision.id, optionId: 'provide-info', freeText: 'Use somente o que está no brief; problema: fotos se perdem sem virar história.', decidedBy: 'vitor', env: ENV });
  assert.equal(resp.project.current_state, 'PRODUCT_STRATEGY_IN_PROGRESS', 'retomada volta à fase de estratégia');
  assert.ok(resp.project.next_action.command.startsWith('submit'));

  writeFileSync(join(dir, 'product-vision.md'), GOOD_VISION);
  writeFileSync(join(dir, 'hypotheses.md'), GOOD_HYPS);
  const r3 = submitPhaseArtifacts({ store, slug, files: [join(dir, 'product-vision.md'), join(dir, 'hypotheses.md')], env: ENV });
  assert.equal(r3.project.current_state, 'MVP_REFINEMENT_READY');
});

test('governança: submit fora de estado recusa; saída não permitida recusa; intake não roda em fase de estratégia', () => {
  const store = mkStore();
  const slug = readyProject(store);
  const dir = tmp();
  writeFileSync(join(dir, 'product-vision.md'), GOOD_VISION);
  assert.throws(() => submitPhaseArtifacts({ store, slug, files: [join(dir, 'product-vision.md')], env: ENV }), /PRODUCT_STRATEGY_IN_PROGRESS/);
  startPhase({ store, slug, env: ENV });
  writeFileSync(join(dir, 'malicioso.md'), 'x');
  assert.throws(() => submitPhaseArtifacts({ store, slug, files: [join(dir, 'malicioso.md')], env: ENV }), /não permitida/);
  assert.throws(() => executeWorkflow({ store, slug, env: ENV }), /USE_RUN_PHASE|run-phase/);
});
