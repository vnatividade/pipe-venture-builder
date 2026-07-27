// Unitários: agente, gate, reviewer, artefatos, decisões, contratos, context loader, flag.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Store } from '../lib/store.mjs';
import { ArtifactManager } from '../lib/artifact-manager.mjs';
import { DecisionQueue } from '../lib/decisions.mjs';
import { runIntakeAgent } from '../agents/intake-agent.mjs';
import { runIntakeCompletenessGate } from '../gates/intake-completeness-gate.mjs';
import { runIntakeReviewer } from '../reviewers/intake-reviewer.mjs';
import { loadContext } from '../lib/context-loader.mjs';
import { assertContract, validateContract } from '../lib/contracts.mjs';
import { loadWorkflowDef, loadAgentDef } from '../lib/engine.mjs';
import { ventureOsEnabled, assertEnabled } from '../lib/flag.mjs';

const mkStore = () => new Store(mkdtempSync(join(tmpdir(), 'vos-unit-')));
const agentDef = loadAgentDef('intake-agent');
const workflowDef = loadWorkflowDef('idea-to-intake');

const IDEA_RICA = `Hoje é difícil para casais controlarem os gastos do mês sem brigar por causa da planilha.
Quero criar um aplicativo para casais que precisam registrar gastos de forma simples.
Funcionalidades:
- cadastrar despesas por categoria
- relatório mensal do casal
Restrições: não pode usar emoji na interface.
Depende de integração com Pix.
Acho que o público inicial seriam casais jovens.
Risco: concorrência de planilhas gratuitas.`;

test('intake-agent: classifica sem inventar, diferencia fato/hipótese, registra lacunas', () => {
  const out = runIntakeAgent({ sources: [{ name: 'idea-v1.md', content: IDEA_RICA }], agentDef });
  assert.ok(out.brief.problema.length > 0, 'problema detectado');
  assert.ok(out.brief.solucao_imaginada.length > 0, 'solução detectada');
  assert.ok(out.brief.funcionalidades_sugeridas.length >= 2, 'bullets herdam rótulo funcionalidades');
  assert.ok(out.brief.restricoes.some((r) => /emoji/.test(r.text)));
  assert.ok(out.brief.dependencias.some((d) => /pix/i.test(d.text)));
  assert.ok(out.brief.premissas.some((p) => p.kind === 'hipotese'), 'hedge vira hipótese');
  assert.ok(out.assumptions.length > 0);
  // Todo fato tem fonte rastreável.
  for (const section of Object.keys(out.brief)) {
    if (!Array.isArray(out.brief[section])) continue;
    for (const item of out.brief[section]) {
      if (item?.kind === 'fato') assert.ok(item.source, `fato sem fonte em ${section}`);
    }
  }
  assert.ok(out.markdown.includes('# Initial Brief'));
});

test('intake-agent: ideia vazia de conteúdo gera lacunas bloqueadoras e decisões abertas', () => {
  const out = runIntakeAgent({ sources: [{ name: 'idea-v1.md', content: 'Quero um app legal' }], agentDef });
  assert.equal(out.brief.problema.length, 0);
  assert.ok(out.brief.lacunas.some((l) => l.includes('problema')));
  assert.ok(out.brief.decisoes_abertas.some((d) => d.blocking && d.topic.startsWith('problema')));
});

test('gate: aprova brief completo; reprova brief com lacuna bloqueadora', () => {
  const rich = runIntakeAgent({ sources: [{ name: 'idea-v1.md', content: IDEA_RICA }], agentDef });
  const pass = runIntakeCompletenessGate({ brief: rich.brief, sourceText: IDEA_RICA, nextActionPlanned: workflowDef.next_phase_on_success, projectId: 'p', runId: 'r' });
  assert.notEqual(pass.status, 'fail');
  assert.ok(pass.score > 0.8);
  assertContract('GateResult', pass);

  const poor = runIntakeAgent({ sources: [{ name: 'idea-v1.md', content: 'Quero um app legal' }], agentDef });
  const fail = runIntakeCompletenessGate({ brief: poor.brief, sourceText: 'Quero um app legal', nextActionPlanned: workflowDef.next_phase_on_success, projectId: 'p', runId: 'r' });
  assert.equal(fail.status, 'fail');
  assert.ok(fail.failures.some((f) => f.category === 'input_gap'));
  assert.equal(fail.next_action, 'solicitar_decisao_humana');
});

test('gate: detecta requisito inventado (fato sem rastreabilidade)', () => {
  const rich = runIntakeAgent({ sources: [{ name: 'idea-v1.md', content: IDEA_RICA }], agentDef });
  rich.brief.funcionalidades_sugeridas.push({ text: 'exportação automática para blockchain corporativa federada', kind: 'fato', source: 'idea-v1.md#s99' });
  const res = runIntakeCompletenessGate({ brief: rich.brief, sourceText: IDEA_RICA, nextActionPlanned: {}, projectId: 'p', runId: 'r' });
  assert.equal(res.status, 'fail');
  assert.ok(res.failures.some((f) => f.check === 'sem_requisitos_inventados'));
});

test('reviewer: acha escopo prematuro e conteúdo não rastreável; é advisory', () => {
  const rich = runIntakeAgent({ sources: [{ name: 'idea-v1.md', content: IDEA_RICA }], agentDef });
  rich.brief.solucao_imaginada.push({ text: 'virar um marketplace multi-tenant de escala global', kind: 'fato', source: 'x#s1' });
  const rev = runIntakeReviewer({ brief: rich.brief, sourceText: IDEA_RICA });
  assert.ok(rev.findings.some((f) => f.code === 'escopo_prematuro'));
  assert.ok(rev.findings.some((f) => f.code === 'conteudo_nao_rastreavel'));
  assert.ok(rev.findings.every((f) => ['P2', 'P3'].includes(f.severity)));
});

test('artifact manager: versiona, deduplica por hash e marca supersessão', () => {
  const store = mkStore();
  store.initProject({ id: 'p', name: 'x-test', slug: 'x-test', description: '', current_state: 'CREATED', current_phase: 'intake', status: 'active', state_version: 1, next_action: null, blockers: [], artifact_refs: [], decision_refs: [], run_refs: [], previous_state: null, created_at: 't', updated_at: 't' });
  const am = new ArtifactManager(store);
  const base = { slug: 'x-test', projectId: 'p', runId: 'r', phase: 'intake', type: 'initial-brief', filename: 'b.json', createdBy: 'rt', agentId: 'intake-agent', model: 'm', promptVersion: '0.1.0', sourceRefs: [] };
  const a1 = am.register({ ...base, content: '{"v":1}' });
  assert.equal(a1.artifact.version, 1);
  const dup = am.register({ ...base, content: '{"v":1}' });
  assert.ok(dup.deduplicated, 'mesmo hash não duplica');
  const a2 = am.register({ ...base, content: '{"v":2}' });
  assert.equal(a2.artifact.version, 2);
  const all = am.list('x-test');
  assert.equal(all.find((a) => a.version === 1).status, 'superseded');
  assert.equal(all.find((a) => a.version === 1).superseded_by, a2.artifact.id);
  assert.equal(am.current('x-test', 'initial-brief').version, 2);
});

test('decisões: idempotência por reason_code, validação de resposta, resolvida não reprocessa', () => {
  const store = mkStore();
  store.initProject({ id: 'p', name: 'y-test', slug: 'y-test', description: '', current_state: 'CREATED', current_phase: 'intake', status: 'active', state_version: 1, next_action: null, blockers: [], artifact_refs: [], decision_refs: [], run_refs: [], previous_state: null, created_at: 't', updated_at: 't' });
  const q = new DecisionQueue(store);
  const req = { slug: 'y-test', projectId: 'p', runId: 'r', phase: 'intake', category: 'input_gap', reasonCode: 'rc1', context: 'c', reason: 'r', impact: 'i', options: [{ id: 'a', label: 'A' }, { id: 'b', label: 'B' }], recommendation: { option_id: 'a', rationale: 'x' }, safeDefault: 'bloqueado', expectedResponse: { type: 'option', requires_free_text: true }, blockedScope: { blocked: [], not_blocked: [] } };
  const d1 = q.request(req);
  const d2 = q.request(req);
  assert.ok(d2.deduplicated, 'pedido aberto não duplica');
  assert.equal(q.listPending('y-test').length, 1);
  assert.throws(() => q.respond({ slug: 'y-test', decisionId: d1.decision.id, optionId: 'zzz', decidedBy: 'v' }), /opção inválida/);
  assert.throws(() => q.respond({ slug: 'y-test', decisionId: d1.decision.id, optionId: 'a', decidedBy: 'v' }), /texto complementar/);
  assert.throws(() => q.respond({ slug: 'y-test', decisionId: d1.decision.id, optionId: 'a', freeText: 'ok', decidedBy: '' }), /decided_by/);
  const resolved = q.respond({ slug: 'y-test', decisionId: d1.decision.id, optionId: 'a', freeText: 'ok', decidedBy: 'vitor' });
  assert.equal(resolved.status, 'resolved');
  assert.throws(() => q.respond({ slug: 'y-test', decisionId: d1.decision.id, optionId: 'a', freeText: 'ok', decidedBy: 'vitor' }), /já resolvida/);
});

test('context loader: precedência, hashes, limite e omissões registradas', () => {
  const store = mkStore();
  store.initProject({ id: 'p', name: 'z-test', slug: 'z-test', description: '', current_state: 'CREATED', current_phase: 'intake', status: 'active', state_version: 1, next_action: null, blockers: [], artifact_refs: [], decision_refs: [], run_refs: [], previous_state: null, created_at: 't', updated_at: 't' });
  store.writeSource('z-test', 'idea-v1.md', 'ideia teste com conteúdo');
  const project = store.loadProject('z-test');
  const ctx = loadContext({ store, slug: 'z-test', project, workflowDef, agentDef, task: 't' });
  assert.ok(ctx.documents.length >= 4);
  assert.equal(ctx.documents[0].name, 'project-state');
  assert.ok(ctx.documents.every((d) => d.hash.length === 64));
  const tight = loadContext({ store, slug: 'z-test', project, workflowDef, agentDef, task: 't', limitChars: 900 });
  assert.ok(tight.omitted.length > 0, 'omissões registradas sob limite apertado');
  assert.ok(tight.used_chars <= 900);
});

test('contratos: validação recusa objeto inválido', () => {
  const bad = validateContract('Project', { id: 'x' });
  assert.equal(bad.valid, false);
  assert.ok(bad.errors.some((e) => e.includes('slug')));
  assert.throws(() => assertContract('Run', { id: 'r' }), /violação do contrato/);
  assert.throws(() => assertContract('Inexistente', {}), /contrato desconhecido/);
});

test('feature flag: default desabilitado; habilita por env', () => {
  assert.equal(ventureOsEnabled({}), false);
  assert.equal(ventureOsEnabled({ VENTURE_OS_ENABLED: 'true' }), true);
  assert.equal(ventureOsEnabled({ VENTURE_OS_ENABLED: '1' }), true);
  assert.equal(ventureOsEnabled({ VENTURE_OS_ENABLED: 'no' }), false);
  assert.throws(() => assertEnabled({}), /desabilitado/);
});
