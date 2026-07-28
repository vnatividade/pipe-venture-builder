// ux-completeness-gate: fluxos cobrem as funcionalidades do MVP; estados, exceções e dados definidos.
import { newId, nowIso } from '../lib/ids.mjs';

const REF_RE = /\(fonte:\s*[^)]+\)\s*$/;
const HINT = /(idea-v\d|clarification-v\d|initial-brief|baseline|PB-|dec_|DEC-|#s\d|product-vision|hypotheses|mvp-scope|features-rules)/i;
function section(md, title) {
  const lines = (md ?? '').split('\n');
  const re = new RegExp(`^##\\s*${title}\\s*$`, 'i');
  const i = lines.findIndex((l) => re.test(l.trim()));
  if (i === -1) return null;
  const rest = lines.slice(i + 1);
  const end = rest.findIndex((l) => /^##\s/.test(l));
  return rest.slice(0, end === -1 ? rest.length : end).join('\n').trim();
}
const bullets = (t) => (t ?? '').split('\n').map((l) => l.trim()).filter((l) => /^(-|\d+\.)\s/.test(l));
const toks = (t) => new Set(String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').split(/[^a-z0-9]+/).filter((x) => x.length > 3));

export function runUxCompletenessGate({ files, mvpFeaturesText = '', nextActionPlanned, reviewerFindings = [], projectId, runId }) {
  const flows = files['user-flows'];
  const states = files['states-exceptions'];
  const failures = []; const warnings = []; const evidence = [];
  let checks = 0; let passed = 0;
  const check = (name, ok, { failure, category = 'structural', severity = 'P1', detail } = {}) => {
    checks++;
    if (ok) { passed++; evidence.push({ check: name, result: 'pass' }); }
    else { failures.push({ check: name, severity, category, message: failure, detail: detail ?? null }); evidence.push({ check: name, result: 'fail' }); }
  };

  check('artefatos_presentes', Boolean(flows && states), { failure: 'user-flows.md e states-exceptions.md são obrigatórios.', category: 'input_gap' });
  if (flows) {
    check('fluxo_principal', bullets(section(flows, 'Fluxo principal')).length >= 2, { failure: 'Fluxo principal precisa de ≥2 passos.', category: 'input_gap' });
    check('fluxos_alternativos', Boolean(section(flows, 'Fluxos alternativos')), { failure: 'Seção "Fluxos alternativos" ausente (registre ao menos lacuna).', category: 'input_gap' });
  }
  if (states) {
    check('estados_definidos', bullets(section(states, 'Estados')).length >= 1, { failure: 'Estados ausentes.', category: 'input_gap' });
    check('excecoes_definidas', bullets(section(states, 'Exce[çc][õo]es')).length >= 1, { failure: 'Exceções ausentes.', category: 'input_gap' });
    check('dados_necessarios', bullets(section(states, 'Dados')).length >= 1, { failure: 'Dados necessários/visíveis ausentes.', category: 'input_gap' });
  }
  // Cobertura: cada funcionalidade obrigatória do MVP aparece nos fluxos (sobreposição de tokens).
  const featLines = (mvpFeaturesText.match(/^- .+$/gm) ?? []).map((l) => l.replace(/\(fonte:[^)]+\)/i, ''));
  const flowToks = toks(flows ?? '');
  const uncovered = featLines.filter((f) => {
    const ft = [...toks(f)];
    return ft.length > 0 && ft.filter((t) => flowToks.has(t)).length / ft.length < 0.4;
  });
  check('funcionalidades_representadas_em_fluxos', featLines.length > 0 && uncovered.length === 0,
    { failure: `${uncovered.length} funcionalidade(s) do MVP sem representação nos fluxos.`, category: 'input_gap', detail: uncovered.slice(0, 3) });

  const all = [...bullets(flows ?? ''), ...bullets(states ?? '')];
  const bad = all.filter((b) => !REF_RE.test(b) || !HINT.test(b.match(REF_RE)?.[0] ?? ''));
  check('sem_conteudo_inventado', all.length > 0 && bad.length === 0,
    { failure: `${bad.length} item(ns) sem fonte reconhecida.`, category: 'unsupported_claims', detail: bad.slice(0, 3) });
  check('proxima_acao_definida', Boolean(nextActionPlanned), { failure: 'Próxima ação não determinada.' });

  for (const f of reviewerFindings) warnings.push({ check: `reviewer:${f.code}`, severity: f.severity, message: f.message, detail: f.evidence ?? null });
  const status = failures.length > 0 ? 'fail' : warnings.length > 0 ? 'pass_with_warnings' : 'pass';
  return {
    id: newId('gate'), gate_id: 'ux-completeness-gate', gate_version: '0.1.0',
    project_id: projectId, run_id: runId, status, score: Number((passed / checks).toFixed(2)),
    failures, warnings, evidence,
    recommended_actions: failures.map((f) => `Corrigir: ${f.check}`),
    next_action: failures.length === 0 ? 'aprovar_ux' : 'reexecutar_agente_ou_decisao_humana',
    created_at: nowIso(),
  };
}
