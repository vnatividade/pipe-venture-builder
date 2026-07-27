import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyTransition, InvalidTransitionError, STATES, TRANSITIONS, findTransition } from '../lib/state-machine.mjs';

const proj = (state, extra = {}) => ({ current_state: state, status: 'active', previous_state: null, ...extra });

test('caminho feliz: CREATED → ... → PRODUCT_STRATEGY_READY', () => {
  const p = proj('CREATED');
  applyTransition(p, 'START_INTAKE', { hasIdeaSource: true });
  assert.equal(p.current_state, 'INTAKE_IN_PROGRESS');
  applyTransition(p, 'BRIEF_PRODUCED', { briefArtifactValid: true });
  assert.equal(p.current_state, 'INTAKE_REVIEW');
  applyTransition(p, 'GATE_PASSED', { gateStatus: 'pass' });
  assert.equal(p.current_state, 'INTAKE_APPROVED');
  applyTransition(p, 'PREPARE_NEXT_PHASE', { blockingDecisionsPending: 0 });
  assert.equal(p.current_state, 'PRODUCT_STRATEGY_READY');
  assert.equal(p.status, 'ready_for_next_phase');
});

test('transições inválidas são recusadas sem mutar estado', () => {
  const p = proj('CREATED');
  assert.throws(() => applyTransition(p, 'GATE_PASSED', { gateStatus: 'pass' }), InvalidTransitionError);
  assert.equal(p.current_state, 'CREATED');
  assert.throws(() => applyTransition(p, 'EVENTO_INEXISTENTE'), InvalidTransitionError);
});

test('guards bloqueiam: START_INTAKE sem fonte; GATE_PASSED com gate fail', () => {
  assert.throws(() => applyTransition(proj('CREATED'), 'START_INTAKE', { hasIdeaSource: false }), InvalidTransitionError);
  assert.throws(() => applyTransition(proj('INTAKE_REVIEW'), 'GATE_PASSED', { gateStatus: 'fail' }), InvalidTransitionError);
  assert.throws(() => applyTransition(proj('INTAKE_APPROVED'), 'PREPARE_NEXT_PHASE', { blockingDecisionsPending: 2 }), InvalidTransitionError);
});

test('pass_with_warnings também satisfaz o guard de gate', () => {
  const p = proj('INTAKE_REVIEW');
  applyTransition(p, 'GATE_PASSED', { gateStatus: 'pass_with_warnings' });
  assert.equal(p.current_state, 'INTAKE_APPROVED');
});

test('fluxo humano: INTAKE_REVIEW → WAITING_HUMAN → INTAKE_IN_PROGRESS', () => {
  const p = proj('INTAKE_REVIEW');
  applyTransition(p, 'HUMAN_DECISION_REQUESTED', { blockingDecisionsPending: 1 });
  assert.equal(p.current_state, 'WAITING_HUMAN');
  assert.equal(p.status, 'waiting_human');
  applyTransition(p, 'HUMAN_DECISION_RECEIVED', { decisionResolved: true });
  assert.equal(p.current_state, 'INTAKE_IN_PROGRESS');
});

test('pause/resume volta ao estado anterior', () => {
  const p = proj('INTAKE_REVIEW');
  applyTransition(p, 'PAUSE');
  assert.equal(p.current_state, 'PAUSED');
  assert.equal(p.previous_state, 'INTAKE_REVIEW');
  applyTransition(p, 'RESUME');
  assert.equal(p.current_state, 'INTAKE_REVIEW');
});

test('estados terminais recusam qualquer evento', () => {
  for (const s of ['FAILED', 'CANCELLED']) {
    assert.throws(() => applyTransition(proj(s), 'PAUSE'), InvalidTransitionError);
    assert.throws(() => applyTransition(proj(s), 'CANCEL'), InvalidTransitionError);
  }
});

test('FAIL exige retryExhausted; CANCEL permitido de WAITING_HUMAN', () => {
  assert.throws(() => applyTransition(proj('INTAKE_REVIEW'), 'FAIL', { retryExhausted: false }), InvalidTransitionError);
  const p = proj('WAITING_HUMAN', { previous_state: 'INTAKE_REVIEW' });
  applyTransition(p, 'CANCEL');
  assert.equal(p.current_state, 'CANCELLED');
});

test('toda transição declarada referencia estados e guards válidos', () => {
  for (const t of TRANSITIONS) {
    const froms = Array.isArray(t.from) ? t.from : [t.from];
    for (const f of froms) assert.ok(STATES.includes(f), `from inválido: ${f}`);
    if (!['$previous', '$resume'].includes(t.to)) assert.ok(STATES.includes(t.to), `to inválido: ${t.to}`);
  }
  assert.ok(findTransition('START_INTAKE', 'CREATED'));
  assert.equal(findTransition('START_INTAKE', 'FAILED'), undefined);
});

test('registro de transição contém evento, origem, destino, guard e gate', () => {
  const p = proj('INTAKE_REVIEW');
  const rec = applyTransition(p, 'GATE_PASSED', { gateStatus: 'pass' });
  assert.equal(rec.event, 'GATE_PASSED');
  assert.equal(rec.from, 'INTAKE_REVIEW');
  assert.equal(rec.to, 'INTAKE_APPROVED');
  assert.equal(rec.guard, 'gatePassed');
  assert.equal(rec.gate, 'intake-completeness-gate');
});
