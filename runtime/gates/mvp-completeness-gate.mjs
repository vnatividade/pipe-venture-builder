// mvp-completeness-gate: fecha o MVP — 1 público prioritário, 1 caso de uso principal,
// funcionalidades obrigatórias, fora do escopo, regras e critérios rastreáveis.
import { newId, nowIso } from '../lib/ids.mjs';

const REF_RE = /\(fonte:\s*[^)]+\)\s*$/;
const VALID_REF_HINT = /(idea-v\d|clarification-v\d|initial-brief|baseline|PB-|dec_|DEC-|statement|#s\d|product-vision|hypotheses)/i;

function section(md, title) {
  const lines = (md ?? '').split('\n');
  const re = new RegExp(`^##\\s*${title}\\s*$`, 'i');
  const start = lines.findIndex((l) => re.test(l.trim()));
  if (start === -1) return null;
  const rest = lines.slice(start + 1);
  const end = rest.findIndex((l) => /^##\s/.test(l));
  return rest.slice(0, end === -1 ? rest.length : end).join('\n').trim();
}
const bullets = (t) => (t ?? '').split('\n').map((l) => l.trim()).filter((l) => l.startsWith('- '));

export function runMvpCompletenessGate({ files, nextActionPlanned, reviewerFindings = [], projectId, runId }) {
  const scope = files['mvp-scope'];
  const feats = files['features-rules'];
  const failures = []; const warnings = []; const evidence = [];
  let checks = 0; let passed = 0;
  const check = (name, ok, { failure, category = 'structural', severity = 'P1', detail } = {}) => {
    checks++;
    if (ok) { passed++; evidence.push({ check: name, result: 'pass' }); }
    else { failures.push({ check: name, severity, category, message: failure, detail: detail ?? null }); evidence.push({ check: name, result: 'fail' }); }
  };

  check('artefatos_presentes', Boolean(scope && feats), { failure: 'mvp-scope.md e features-rules.md são obrigatórios.', category: 'input_gap' });
  if (scope) {
    check('um_publico_prioritario', bullets(section(scope, 'P[úu]blico priorit[áa]rio')).length === 1,
      { failure: 'Exatamente 1 público prioritário é exigido.', category: 'input_gap' });
    check('um_caso_de_uso_principal', bullets(section(scope, 'Caso de uso principal')).length === 1,
      { failure: 'Exatamente 1 caso de uso principal é exigido.', category: 'input_gap' });
    check('criterios_de_sucesso', bullets(section(scope, 'Crit[ée]rios de sucesso')).length >= 1,
      { failure: 'Critérios de sucesso ausentes.', category: 'input_gap' });
    check('fora_do_escopo_explicito', bullets(section(scope, 'Fora do escopo')).length >= 1,
      { failure: 'Fora do escopo precisa ser explícito.', category: 'input_gap' });
  }
  if (feats) {
    check('funcionalidades_obrigatorias', bullets(section(feats, 'Funcionalidades obrigat[óo]rias')).length >= 1,
      { failure: 'Funcionalidades obrigatórias ausentes.', category: 'input_gap' });
    check('regras_de_negocio', bullets(section(feats, 'Regras de neg[óo]cio')).length >= 1,
      { failure: 'Regras de negócio ausentes.', category: 'input_gap' });
  }
  const all = [...bullets(scope ?? ''), ...bullets(feats ?? '')];
  const bad = all.filter((b) => !REF_RE.test(b) || !VALID_REF_HINT.test(b.match(REF_RE)?.[0] ?? ''));
  check('sem_conteudo_inventado', all.length > 0 && bad.length === 0,
    { failure: `${bad.length} item(ns) sem fonte reconhecida — tratados como invenção.`, category: 'unsupported_claims', detail: bad.slice(0, 3) });
  check('proxima_acao_definida', Boolean(nextActionPlanned), { failure: 'Próxima ação não determinada.' });

  for (const f of reviewerFindings) warnings.push({ check: `reviewer:${f.code}`, severity: f.severity, message: f.message, detail: f.evidence ?? null });
  const status = failures.length > 0 ? 'fail' : warnings.length > 0 ? 'pass_with_warnings' : 'pass';
  return {
    id: newId('gate'), gate_id: 'mvp-completeness-gate', gate_version: '0.1.0',
    project_id: projectId, run_id: runId, status, score: Number((passed / checks).toFixed(2)),
    failures, warnings, evidence,
    recommended_actions: failures.map((f) => `Corrigir: ${f.check}`),
    next_action: failures.length === 0 ? 'aprovar_mvp' : 'reexecutar_agente_ou_decisao_humana',
    created_at: nowIso(),
  };
}
