// Ponte pipe (Python) ↔ pipe-os (Node) — ADR-VOS-006.
// Importa um ProductBaseline canônico como fonte de projeto (seed) e emite a
// atualização do baseline quando o intake é aprovado. Regras do dual-entry:
// supersessão por identidade estável (mesmo baselineId, versão nova em arquivo
// novo), nunca baseline paralelo; nunca emitir instância inválida.
import { readFileSync, existsSync, readdirSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validate } from './minischema.mjs';
import { nowIso, sha256 } from './ids.mjs';

const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const CANONICAL_SCHEMA = JSON.parse(readFileSync(join(REPO_ROOT, 'schemas', 'ProductBaseline.schema.json'), 'utf8'));

export function validateBaseline(baseline) {
  return validate(CANONICAL_SCHEMA, baseline);
}

export function loadBaselineFile(path) {
  const raw = readFileSync(path, 'utf8');
  const baseline = JSON.parse(raw);
  const { valid, errors } = validateBaseline(baseline);
  if (!valid) {
    const err = new Error(`baseline inválido contra o schema canônico: ${errors.slice(0, 5).join('; ')}`);
    err.code = 'INVALID_BASELINE';
    err.errors = errors;
    throw err;
  }
  return { baseline, hash: sha256(raw) };
}

// Statements → markdown rotulado que o intake-agent classifica deterministicamente.
// Conteúdo é SEMPRE verbatim do baseline; apenas o rótulo de seção é mapeado
// a partir do statementId (semântica definida pelo gerador Python de PIP-708).
const SECTION_BY_STATEMENT = [
  [/^ST-problem/, 'problema'],
  [/^ST-target-user/, 'público'],
  [/^ST-mechanism/, 'solução'],
  [/^ST-assumption/, 'premissas'],
  [/^ST-channel/, 'contexto'],
  [/^ST-solution-path/, 'contexto'],
  [/^ST-promise/, 'contexto'],
];

export function seedMarkdownFromBaseline(baseline) {
  const lines = [
    `Fonte: ProductBaseline ${baseline.baselineId} (entryMode: ${baseline.entryMode}, gerado em ${baseline.generatedAt}).`,
    '',
  ];
  for (const st of baseline.statements) {
    if (st.classification === 'missing') continue;               // lacuna: o agente registra pela ausência
    if (st.statementId === 'ST-brainstorm-source') continue;      // meta-statement do gerador
    if (st.statementId === 'ST-product-name') continue;           // já usado em name/slug
    const section = SECTION_BY_STATEMENT.find(([re]) => re.test(st.statementId))?.[1];
    lines.push(section ? `${section}: ${st.text}` : st.text);
  }
  lines.push('');
  return lines.join('\n');
}

export function baselineDir(store, slug) {
  const dir = store.safePath(slug, 'baseline');
  mkdirSync(dir, { recursive: true });
  return dir;
}

export function latestBaselineVersion(store, slug) {
  const dir = baselineDir(store, slug);
  const versions = readdirSync(dir)
    .map((f) => f.match(/^baseline-v(\d+)\.json$/)?.[1])
    .filter(Boolean).map(Number);
  return versions.length ? Math.max(...versions) : 0;
}

export function writeBaselineVersion(store, slug, baseline) {
  const version = latestBaselineVersion(store, slug) + 1;
  const path = join(baselineDir(store, slug), `baseline-v${version}.json`);
  store.atomicWriteText(path, JSON.stringify(baseline, null, 2) + '\n');
  return { version, path };
}

export function loadProjectBaseline(store, slug) {
  const v = latestBaselineVersion(store, slug);
  if (v === 0) return null;
  return {
    version: v,
    baseline: JSON.parse(readFileSync(join(baselineDir(store, slug), `baseline-v${v}.json`), 'utf8')),
  };
}

// Emissão pós-aprovação do intake: lifecycle avança para founder_focus,
// o brief entra em artifacts[], a aprovação do gate entra em approvals[].
// Retorna null (com motivo) se a atualização não puder ser emitida válida.
export function emitUpdatedBaseline({ store, slug, artifact, gateResult, decisions = [] }) {
  const current = loadProjectBaseline(store, slug);
  if (!current) return { emitted: false, reason: 'projeto sem baseline importado' };
  const b = structuredClone(current.baseline);

  b.generatedAt = nowIso();
  b.lifecycle.currentStage = 'founder_focus';
  b.lifecycle.nextAllowedStage = 'controle_evaluation';

  const artifactId = `ART-initial-brief-v${artifact.version}`;
  if (!b.artifacts.some((a) => a.artifactId === artifactId)) {
    b.artifacts.push({
      artifactId,
      artifactType: 'product_context',
      title: `Initial brief v${artifact.version} (venture-os intake loop)`,
      status: 'present',
      sourceRef: artifact.path,
      externalRef: null,
      provenanceStatementIds: [],
    });
  }
  b.approvals.push({
    action: `intake-completeness-gate ${gateResult.status} (venture-os loop, score ${gateResult.score})`,
    required: true,
    status: 'granted',
    sourceRef: gateResult.id,
  });
  for (const dec of decisions.filter((d) => d.status === 'resolved')) {
    b.approvals.push({
      action: `human decision ${dec.id} (${dec.reason_code}) resolved by ${dec.resolution.decided_by}`,
      required: true,
      status: 'granted',
      sourceRef: dec.id,
    });
  }
  b.nextActions = [{
    actionId: 'NEXT-founder-focus',
    title: 'Narrow founder focus and confirm the solution path',
    ownerRole: 'Product Strategist',
    priority: 'P2',
    blockedByGapIds: [],
    approvalRequired: false,
    suggestedCommand: '/pipe:discover',
  }];

  const { valid, errors } = validateBaseline(b);
  if (!valid) return { emitted: false, reason: `atualização inválida, não emitida: ${errors.slice(0, 3).join('; ')}` };
  const { version, path } = writeBaselineVersion(store, slug, b);
  return { emitted: true, version, path, baselineId: b.baselineId };
}
