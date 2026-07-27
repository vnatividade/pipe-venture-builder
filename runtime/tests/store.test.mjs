import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Store } from '../lib/store.mjs';

const mkStore = () => new Store(mkdtempSync(join(tmpdir(), 'vos-store-')));

const mkProject = (slug) => ({
  id: 'prj_1', name: slug, slug, description: '', current_state: 'CREATED', current_phase: 'intake',
  status: 'active', state_version: 1, next_action: null, blockers: [], artifact_refs: [],
  decision_refs: [], run_refs: [], previous_state: null, created_at: 't', updated_at: 't',
});

test('init/load/list de projeto; duplicação recusada', () => {
  const store = mkStore();
  store.initProject(mkProject('alpha-test'));
  assert.equal(store.loadProject('alpha-test').slug, 'alpha-test');
  assert.deepEqual(store.listProjects(), ['alpha-test']);
  assert.throws(() => store.initProject(mkProject('alpha-test')), /DUPLICATE|já existe/);
});

test('concorrência otimista: versão divergente é recusada', () => {
  const store = mkStore();
  const p = store.initProject(mkProject('beta-test'));
  store.saveProject({ ...p }, 1);                 // v1 → v2
  const stale = { ...p, state_version: 1 };
  assert.throws(() => store.saveProject(stale, 1), /conflito de versão/);
  const fresh = store.loadProject('beta-test');
  assert.equal(fresh.state_version, 2);
  store.saveProject(fresh, 2);
  assert.equal(store.loadProject('beta-test').state_version, 3);
});

test('escrita atômica: project.json é sempre JSON válido', () => {
  const store = mkStore();
  const p = store.initProject(mkProject('gamma-test'));
  for (let i = 0; i < 20; i++) {
    const cur = store.loadProject('gamma-test');
    store.saveProject(cur, cur.state_version);
    JSON.parse(readFileSync(store.safePath('gamma-test', 'project.json'), 'utf8'));
  }
});

test('anti path-traversal: caminhos fora da raiz são recusados', () => {
  const store = mkStore();
  assert.throws(() => store.safePath('..', 'fora'), /PATH_TRAVERSAL|fora da raiz/);
  assert.throws(() => store.safePath('proj', '..', '..', 'etc'), /PATH_TRAVERSAL|fora da raiz/);
});

test('eventos e transições são append-only e legíveis', () => {
  const store = mkStore();
  store.initProject(mkProject('delta-test'));
  store.appendEvent('delta-test', { id: 'e1', type: 'X' });
  store.appendEvent('delta-test', { id: 'e2', type: 'Y' });
  store.appendTransition('delta-test', { event: 'A', from: '1', to: '2' });
  assert.equal(store.listEvents('delta-test').length, 2);
  assert.equal(store.listTransitions('delta-test')[0].event, 'A');
});

test('sources: ideia + clarificações em ordem', () => {
  const store = mkStore();
  store.initProject(mkProject('epsilon-test'));
  store.writeSource('epsilon-test', 'idea-v1.md', 'ideia');
  store.writeSource('epsilon-test', 'clarification-v2.md', 'mais info');
  const names = store.listSources('epsilon-test').map((s) => s.name);
  assert.deepEqual(names, ['clarification-v2.md', 'idea-v1.md'].sort());
});
