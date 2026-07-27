// strategy-completeness-gate: gate determinístico da fase de estratégia.
// Reprova invenção (item sem fonte), seções ausentes e desconexão problema↔solução.
import { newId, nowIso } from '../lib/ids.mjs';

const REF_RE = /\(fonte:\s*[^)]+\)\s*$/;
const VALID_REF_HINT = /(idea-v\d|clarification-v\d|initial-brief|baseline|PB-|dec_|DEC-|statement|#s\d)/i;

function section(md, title) {
  const lines = (md ?? '').split('\n');
  const re = new RegExp(`^##\\s*${title}\\s*$`, 'i');
  const start = lines.findIndex((l) => re.test(l.trim()));
  if (start === -1) return null;
  const rest = lines.slice(start + 1);
  const end = rest.findIndex((l) => /^##\s/.test(l));
  return rest.slice(0, end === -1 ? rest.length : end).join('\n').trim();
}

function bullets(text) {
  return (text ?? '').split('\n').map((l) => l.trim()).filter((l) => l.startsWith('- '));
}

export function runStrategyCompletenessGate({ files, nextActionPlanned, reviewerFindings = [], projectId, runId }) {
  const vision = files['product-vision'];
  const hypotheses = files['hypotheses'];
  const failures = [];
  const warnings = [];
  const evidence = [];
  let checks = 0;
  let passed = 0;

  const check = (name, ok, { failure, category = 'structural', severity = 'P1', warningOnly = false, detail } = {}) => {
    checks++;
    if (ok) { passed++; evidence.push({ check: name, result: 'pass', detail: detail ?? null }); }
    else if (warningOnly) { warnings.push({ check: name, severity: 'P2', message: failure, detail: detail ?? null }); evidence.push({ check: name, result: 'warning', detail: detail ?? null }); passed++; }
    else { failures.push({ check: name, severity, category, message: failure, detail: detail ?? null }); evidence.push({ check: name, result: 'fail', detail: detail ?? null }); }
  };

  check('artefatos_presentes', Boolean(vision && hypotheses),
    { failure: 'product-vision.md e hypotheses.md são obrigatórios.', category: 'input_gap' });

  if (vision) {
    const proposta = section(vision, 'Proposta de valor');
    const publico = section(vision, 'P[úu]blico');
    const probSol = section(vision, 'Problema e solu[çc][ãa]o');
    check('proposta_de_valor_clara', Boolean(proposta && proposta.length > 20),
      { failure: 'Seção "Proposta de valor" ausente ou vazia.', category: 'input_gap' });
    check('publico_identificavel', Boolean(publico && publico.length > 10),
      { failure: 'Seção "Público" ausente ou vazia (registre ao menos a hipótese de público).', category: 'input_gap' });
    check('problema_solucao_conectados', Boolean(probSol && /problema/i.test(probSol) && /solu[çc][ãa]o|resolve/i.test(probSol)),
      { failure: 'Seção "Problema e solução" precisa conectar explicitamente os dois.', category: 'input_gap' });
  }

  if (hypotheses) {
    const hyps = bullets(section(hypotheses, 'Hip[óo]teses') ?? hypotheses);
    check('hipoteses_explicitas', hyps.length >= 2,
      { failure: `São necessárias ≥2 hipóteses explícitas (encontradas: ${hyps.length}).`, category: 'input_gap' });
    const riscos = bullets(section(hypotheses, 'Riscos') ?? '');
    check('riscos_registrados', riscos.length >= 1,
      { failure: 'Seção "Riscos" precisa de ao menos 1 item.', category: 'input_gap' });
  }

  // Rastreabilidade: todo bullet afirmativo termina com (fonte: ...) plausível.
  const allBullets = [...bullets(vision ?? ''), ...bullets(hypotheses ?? '')];
  const unreferenced = allBullets.filter((b) => !REF_RE.test(b));
  const badRefs = allBullets.filter((b) => REF_RE.test(b) && !VALID_REF_HINT.test(b.match(REF_RE)[0]));
  check('sem_conteudo_inventado', allBullets.length > 0 && unreferenced.length === 0 && badRefs.length === 0,
    { failure: `${unreferenced.length} item(ns) sem fonte e ${badRefs.length} com fonte não reconhecida — tratados como invenção.`,
      category: 'unsupported_claims', detail: [...unreferenced, ...badRefs].slice(0, 3) });

  check('proxima_acao_definida', Boolean(nextActionPlanned), { failure: 'Próxima ação não determinada pelo runtime.' });

  for (const f of reviewerFindings) {
    warnings.push({ check: `reviewer:${f.code}`, severity: f.severity, message: f.message, detail: f.evidence ?? null });
  }

  const status = failures.length > 0 ? 'fail' : warnings.length > 0 ? 'pass_with_warnings' : 'pass';
  return {
    id: newId('gate'),
    gate_id: 'strategy-completeness-gate',
    gate_version: '0.1.0',
    project_id: projectId,
    run_id: runId,
    status,
    score: Number((passed / checks).toFixed(2)),
    failures,
    warnings,
    evidence,
    recommended_actions: failures.map((f) => f.category === 'input_gap'
      ? `Solicitar insumo/correção: ${f.check}`
      : `Corrigir artefato e reexecutar: ${f.check}`),
    next_action: failures.length === 0 ? 'aprovar_estrategia'
      : failures.some((f) => f.category === 'input_gap' || f.category === 'unsupported_claims') ? 'reexecutar_agente_ou_decisao_humana' : 'reexecutar_agente',
    created_at: nowIso(),
  };
}
