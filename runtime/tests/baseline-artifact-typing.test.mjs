// PIP-831 — tipagem de artefato do baseline vinda da definição de workflow,
// vínculo externo nos contratos e redação das chaves do Linear no log.
//
// Motivo destes testes: enquanto engine.mjs gravava `artifactType: 'product_context'`
// literal, o planner Python (EXTERNAL_ARTIFACT_TARGETS) nunca via um tipo ticketizável
// e nenhum ticket jamais seria proposto. A regressão é silenciosa — só aparece na ponta.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { artifactTypeForOutput, loadWorkflowDef } from '../lib/engine.mjs';
import { validateContract } from '../lib/contracts.mjs';
import { log } from '../lib/log.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

// Espelha schemas/ProductBaseline.schema.json → properties.artifactType.enum.
// Se o enum canônico mudar, este teste falha de propósito: a lista é contrato, não conveniência.
const BASELINE_ARTIFACT_TYPES = new Set([
  'product_context', 'product_requirement', 'feature', 'epic', 'ticket', 'adr',
  'decision', 'code_artifact', 'audit_finding', 'validation_artifact',
  'research_artifact', 'learning_record', 'other',
]);

// Espelha src/pipe_venture_builder/reconcile/planner.py → EXTERNAL_ARTIFACT_TARGETS.
const TICKETIZABLE = new Set(['product_requirement', 'feature', 'epic', 'ticket']);

const WORKFLOWS_WITH_ADVANCE = ['product-strategy', 'mvp-refinement', 'ux-architecture'];

test('artifactTypeForOutput: usa o mapa da definição quando o output está declarado', () => {
  const def = { baseline_advance: { artifact_types: { 'features-rules': 'feature' } } };
  assert.equal(artifactTypeForOutput(def, 'features-rules'), 'feature');
});

test('artifactTypeForOutput: cai para product_context quando não há mapa ou output', () => {
  assert.equal(artifactTypeForOutput({}, 'qualquer'), 'product_context');
  assert.equal(artifactTypeForOutput({ baseline_advance: {} }, 'qualquer'), 'product_context');
  assert.equal(
    artifactTypeForOutput({ baseline_advance: { artifact_types: { outro: 'feature' } } }, 'qualquer'),
    'product_context',
  );
});

test('artifactTypeForOutput: recusa tipo fora do enum do ProductBaseline', () => {
  const def = { baseline_advance: { artifact_types: { x: 'nao_existe' } } };
  assert.throws(() => artifactTypeForOutput(def, 'x'), /artifact_type/);
});

test('toda definição com baseline_advance declara artifact_types para todos os seus outputs', () => {
  for (const id of WORKFLOWS_WITH_ADVANCE) {
    const def = loadWorkflowDef(id);
    const map = def.baseline_advance?.artifact_types;
    assert.ok(map, `${id}: baseline_advance.artifact_types ausente`);
    for (const output of def.outputs) {
      assert.ok(map[output], `${id}: output "${output}" sem artifact_type declarado`);
      assert.ok(
        BASELINE_ARTIFACT_TYPES.has(map[output]),
        `${id}: artifact_type "${map[output]}" fora do enum do ProductBaseline`,
      );
    }
  }
});

test('mvp-refinement e ux-architecture produzem ao menos um artefato ticketizável', () => {
  for (const id of ['mvp-refinement', 'ux-architecture']) {
    const types = Object.values(loadWorkflowDef(id).baseline_advance.artifact_types);
    assert.ok(
      types.some((t) => TICKETIZABLE.has(t)),
      `${id}: nenhum output vira tipo que o planner ticketiza (${types.join(', ')})`,
    );
  }
});

test('product-strategy NÃO produz tipo ticketizável (gate de pipeline: nada de build antes do MVP)', () => {
  const types = Object.values(loadWorkflowDef('product-strategy').baseline_advance.artifact_types);
  for (const t of types) {
    assert.ok(!TICKETIZABLE.has(t), `product-strategy emitiu "${t}", que criaria ticket antes do MVP scope`);
  }
});

test('idea-to-intake continua sem baseline_advance (o caminho é o baseline-bridge)', () => {
  assert.equal(loadWorkflowDef('idea-to-intake').baseline_advance, undefined);
});

// Achado do review do PR #164: a lista de workflows acima é fixa, então um
// workflow novo com baseline_advance e sem artifact_types passaria por ela.
// O contrato fecha o buraco na origem — erro de digitação na chave vira
// violação de contrato no load, não fallback silencioso para product_context.
test('o contrato Workflow exige artifact_types quando há baseline_advance', () => {
  const base = loadWorkflowDef('mvp-refinement');
  const semMapa = structuredClone(base);
  delete semMapa.baseline_advance.artifact_types;
  const res = validateContract('Workflow', semMapa);
  assert.equal(res.valid, false, 'baseline_advance sem artifact_types deveria violar o contrato');
  assert.ok(res.errors.some((e) => /artifact_types/.test(e)), res.errors.join('; '));

  const chaveErrada = structuredClone(base);
  chaveErrada.baseline_advance.artifactTypes = chaveErrada.baseline_advance.artifact_types;
  delete chaveErrada.baseline_advance.artifact_types;
  assert.equal(validateContract('Workflow', chaveErrada).valid, false, 'typo na chave deveria falhar');
});

test('Project aceita external_refs e o schema declara o campo', () => {
  const schema = JSON.parse(readFileSync(join(ROOT, 'schemas', 'Project.schema.json'), 'utf8'));
  assert.ok(schema.properties.external_refs, 'Project.schema.json sem external_refs');

  const base = {
    id: 'prj_1', name: 'x', slug: 'venture-x', description: '', current_state: 'CREATED',
    current_phase: 'intake', status: 'active', state_version: 1, next_action: null,
    blockers: [], artifact_refs: [], decision_refs: [], run_refs: [],
    created_at: '2026-08-05T00:00:00.000Z', updated_at: '2026-08-05T00:00:00.000Z',
  };
  assert.equal(validateContract('Project', base).valid, true, 'projeto sem external_refs continua válido');

  const comRef = {
    ...base,
    external_refs: [{ system: 'linear', id: 'PIP-831', url: 'https://linear.app/x/issue/PIP-831', kind: 'issue' }],
  };
  const res = validateContract('Project', comRef);
  assert.equal(res.valid, true, `projeto com external_refs inválido: ${res.errors?.join('; ')}`);
});

test('ArtifactManifestEntry aceita external_ref nulo ou string', () => {
  const schema = JSON.parse(readFileSync(join(ROOT, 'schemas', 'ArtifactManifestEntry.schema.json'), 'utf8'));
  assert.ok(schema.properties.external_ref, 'ArtifactManifestEntry.schema.json sem external_ref');

  const base = {
    id: 'art_1', project_id: 'prj_1', run_id: 'run_1', type: 'features-rules', version: 1,
    path: 'artifacts/features-rules-v1.md', status: 'present', hash: 'a'.repeat(64),
    created_by: 'claude-code', agent_id: 'mvp-refinement-agent', model: 'claude-code/interactive',
    prompt_version: '1', source_refs: [], created_at: '2026-08-05T00:00:00.000Z',
  };
  assert.equal(validateContract('ArtifactManifestEntry', base).valid, true);
  assert.equal(validateContract('ArtifactManifestEntry', { ...base, external_ref: null }).valid, true);
  assert.equal(validateContract('ArtifactManifestEntry', { ...base, external_ref: 'PIP-831' }).valid, true);
});

test('log redige credenciais do Linear', () => {
  const original = process.stderr.write.bind(process.stderr);
  const linhas = [];
  process.stderr.write = (chunk) => { linhas.push(String(chunk)); return true; };
  const silent = process.env.VENTURE_OS_LOG_SILENT;
  delete process.env.VENTURE_OS_LOG_SILENT;
  try {
    log('info', 'teste', {
      linearApiKey: 'lin_api_SEGREDO', linear_token: 'SEGREDO', linearToken: 'SEGREDO',
      client_secret: 'SEGREDO', webhook_secret: 'SEGREDO',
      nested: { linearApiKey: 'SEGREDO' },
      inocente: 'visivel',
    });
  } finally {
    process.stderr.write = original;
    if (silent !== undefined) process.env.VENTURE_OS_LOG_SILENT = silent;
  }
  const saida = linhas.join('');
  assert.ok(!saida.includes('SEGREDO'), `segredo vazou no log: ${saida}`);
  assert.ok(saida.includes('visivel'), 'campo inocente deveria continuar visível');
  assert.match(saida, /\[REDACTED\]/);
});
