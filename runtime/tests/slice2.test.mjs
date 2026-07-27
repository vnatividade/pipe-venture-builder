// Fatia 2: ponte com o ProductBaseline canônico (ADR-VOS-006).
// Round-trip: baseline → seed de projeto → loop de intake → baseline atualizado
// schema-válido; idempotência; paridade do validador Node com o schema canônico.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Store } from '../lib/store.mjs';
import { createProject, createProjectFromBaseline, executeWorkflow, loadAgentDef } from '../lib/engine.mjs';
import { validateBaseline, loadBaselineFile, seedMarkdownFromBaseline, loadProjectBaseline } from '../lib/baseline-bridge.mjs';
import { runIntakeAgent } from '../agents/intake-agent.mjs';

process.env.VENTURE_OS_LOG_SILENT = '1';
const ENV = { VENTURE_OS_ENABLED: 'true', VENTURE_OS_LOG_SILENT: '1' };
const FIXTURE = join(dirname(fileURLToPath(import.meta.url)), 'fixtures', 'baseline-amostra.json');
const SLUG = 'amostra-trial---cobranca-recorrente-pilates';
const mkStore = () => new Store(mkdtempSync(join(tmpdir(), 'vos-s2-')));

test('validador Node aceita o baseline canônico gerado pelo pipe idea (paridade com jsonschema)', () => {
  const baseline = JSON.parse(readFileSync(FIXTURE, 'utf8'));
  const { valid, errors } = validateBaseline(baseline);
  assert.deepEqual(errors, [], 'baseline da fixture deve validar com 0 erros');
  assert.ok(valid);
});

test('validador Node recusa baseline corrompido (required, enum)', () => {
  const baseline = JSON.parse(readFileSync(FIXTURE, 'utf8'));
  delete baseline.lifecycle.currentStage;
  baseline.entryMode = 'invalido';
  const { valid, errors } = validateBaseline(baseline);
  assert.equal(valid, false);
  assert.ok(errors.some((e) => e.includes('currentStage')));
  assert.ok(errors.some((e) => e.includes('entryMode')));
});

test('seed markdown: verbatim, rotulado por statementId, sem meta-statements', () => {
  const { baseline } = loadBaselineFile(FIXTURE);
  const md = seedMarkdownFromBaseline(baseline);
  assert.ok(md.includes('problema: '), 'ST-problem vira seção problema');
  assert.ok(md.includes('público: '), 'ST-target-user vira seção público');
  assert.ok(md.includes('premissas: '), 'ST-assumption vira premissas');
  assert.ok(!md.includes('safely parsed'), 'meta-statement ST-brainstorm-source excluído');
  for (const st of baseline.statements.filter((s) => s.classification !== 'missing' && !['ST-brainstorm-source', 'ST-product-name'].includes(s.statementId))) {
    assert.ok(md.includes(st.text), `texto verbatim presente: ${st.statementId}`);
  }
});

test('round-trip completo: from-baseline → intake aprovado → baseline v2 schema-válido', () => {
  const store = mkStore();
  const project = createProjectFromBaseline({ store, baselinePath: FIXTURE, env: ENV });
  assert.equal(project.slug, SLUG, 'slug vem do product.productId do baseline');
  assert.equal(project.baseline_ref.current_version, 1);
  assert.equal(project.baseline_ref.baseline_id, 'PB-amostra-trial---cobranca-recorrente-pilates-idea');

  const result = executeWorkflow({ store, slug: project.slug, env: ENV });
  assert.equal(result.project.current_state, 'PRODUCT_STRATEGY_READY');
  assert.notEqual(result.gateResult.status, 'fail');

  assert.ok(result.baselineUpdate?.emitted, `emissão falhou: ${result.baselineUpdate?.reason}`);
  const { version, baseline: updated } = loadProjectBaseline(store, project.slug);
  assert.equal(version, 2);
  assert.equal(updated.baselineId, project.baseline_ref.baseline_id, 'mesma identidade estável (nunca baseline paralelo)');
  assert.equal(updated.lifecycle.currentStage, 'founder_focus');
  assert.equal(updated.lifecycle.nextAllowedStage, 'controle_evaluation');
  assert.ok(updated.artifacts.some((a) => a.artifactId.startsWith('ART-initial-brief-v')));
  assert.ok(updated.approvals.some((a) => a.action.includes('intake-completeness-gate')));
  const { valid, errors } = validateBaseline(updated);
  assert.deepEqual(errors, [], 'baseline emitido deve ser schema-válido');
  assert.ok(valid);
  assert.equal(store.loadProject(project.slug).baseline_ref.current_version, 2);
});

test('idempotência: re-import recusado; re-run após conclusão não emite v3', () => {
  const store = mkStore();
  const project = createProjectFromBaseline({ store, baselinePath: FIXTURE, env: ENV });
  assert.throws(() => createProjectFromBaseline({ store, baselinePath: FIXTURE, env: ENV }), /já existe/);
  executeWorkflow({ store, slug: project.slug, env: ENV });
  assert.throws(() => executeWorkflow({ store, slug: project.slug, env: ENV }), /já concluído/);
  assert.equal(loadProjectBaseline(store, project.slug).version, 2, 'sem v3 após tentativa repetida');
});

test('baseline inválido é recusado na importação com erro claro', () => {
  const store = mkStore();
  const bad = join(mkdtempSync(join(tmpdir(), 'vos-s2-bad-')), 'bad.json');
  const baseline = JSON.parse(readFileSync(FIXTURE, 'utf8'));
  delete baseline.statements;
  writeFileSync(bad, JSON.stringify(baseline));
  assert.throws(() => createProjectFromBaseline({ store, baselinePath: bad, env: ENV }), /inválido/);
});

test('projeto sem baseline importado não emite atualização (fatia 1 preservada)', () => {
  const store = mkStore();
  const project = createProject({
    store, name: 'Sem Baseline',
    ideaText: 'Hoje é difícil controlar gastos. Quero criar um app simples de controle.',
    env: ENV,
  });
  const result = executeWorkflow({ store, slug: project.slug, env: ENV });
  assert.equal(result.project.current_state, 'PRODUCT_STRATEGY_READY');
  assert.equal(result.baselineUpdate, null);
});

test('premissas rotuladas viram hipótese (semântica de seção)', () => {
  const agentDef = loadAgentDef('intake-agent');
  const out = runIntakeAgent({ sources: [{ name: 'baseline-import.md', content: 'premissas: o dono aceita registrar os alunos uma única vez.\nQuero criar uma ferramenta de cobrança.' }], agentDef });
  assert.ok(out.brief.premissas.length > 0);
  assert.ok(out.brief.premissas.every((p) => p.kind === 'hipotese'));
});
