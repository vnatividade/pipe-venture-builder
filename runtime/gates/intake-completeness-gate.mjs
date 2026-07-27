// intake-completeness-gate: gate determinístico da fase de intake.
// Vocabulário de saída alinhado ao contrato de /pipe:check do repositório
// (status pass|pass_with_warnings|fail; findings com severidade e categoria).
import { newId, nowIso } from '../lib/ids.mjs';

const CONTENT_SECTIONS = [
  'descricao_da_ideia', 'problema', 'solucao_imaginada', 'publico_mencionado',
  'funcionalidades_sugeridas', 'contexto', 'restricoes', 'dependencias', 'premissas', 'riscos_iniciais',
];

function tokens(text) {
  return new Set(String(text).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    .split(/[^a-z0-9]+/).filter((t) => t.length > 2));
}

function traceable(itemText, sourceText) {
  const it = tokens(itemText);
  if (it.size === 0) return true;
  const src = tokens(sourceText);
  let hit = 0;
  for (const t of it) if (src.has(t)) hit++;
  return hit / it.size >= 0.6;
}

export function runIntakeCompletenessGate({ brief, sourceText, nextActionPlanned, reviewerFindings = [], projectId, runId }) {
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

  check('descricao_presente', brief.descricao_da_ideia?.length > 0,
    { failure: 'Brief sem descrição da ideia.', category: 'input_gap' });

  check('problema_preliminar_presente', brief.problema?.length > 0,
    { failure: 'Nenhum problema preliminar identificado na fonte.', category: 'input_gap' });

  check('solucao_preliminar_presente', brief.solucao_imaginada?.length > 0,
    { failure: 'Nenhuma solução preliminar identificada na fonte.', category: 'input_gap' });

  const unlabeled = CONTENT_SECTIONS.flatMap((s) => brief[s] ?? [])
    .filter((i) => !['fato', 'hipotese'].includes(i.kind));
  check('fatos_e_hipoteses_diferenciados', unlabeled.length === 0,
    { failure: `${unlabeled.length} item(ns) sem classificação fato/hipótese.`, detail: unlabeled.slice(0, 3).map((i) => i.text) });

  const emptySections = CONTENT_SECTIONS.filter((s) => (brief[s] ?? []).length === 0);
  const lacunasText = (brief.lacunas ?? []).join(' ');
  const unregistered = emptySections.filter((s) => !lacunasText.includes(`"${s}"`));
  check('lacunas_registradas', Array.isArray(brief.lacunas) && unregistered.length === 0,
    { failure: `Seções vazias sem lacuna registrada: ${unregistered.join(', ')}.`, detail: unregistered });

  const invented = CONTENT_SECTIONS.flatMap((s) => brief[s] ?? [])
    .filter((i) => i.kind === 'fato' && (!i.source || !traceable(i.text, sourceText)));
  check('sem_requisitos_inventados', invented.length === 0,
    { failure: `${invented.length} fato(s) sem rastreabilidade até a fonte (possível invenção).`,
      category: 'unsupported_claims', detail: invented.slice(0, 3).map((i) => i.text) });

  check('proxima_acao_definida', Boolean(nextActionPlanned),
    { failure: 'Próxima ação não determinada pelo runtime.' });

  const blockingGaps = ['problema', 'solucao_imaginada'].filter((s) => (brief[s] ?? []).length === 0);
  const declaredBlocking = (brief.decisoes_abertas ?? []).filter((d) => d.blocking).map((d) => d.topic);
  const undeclared = blockingGaps.filter((s) => !declaredBlocking.some((t) => t.startsWith(s)));
  check('decisoes_bloqueadoras_identificadas', undeclared.length === 0,
    { failure: `Lacunas bloqueadoras sem decisão aberta correspondente: ${undeclared.join(', ')}.`, detail: undeclared });

  // Público ausente não bloqueia o intake (hipótese provisória — Fase 0 da spec), mas gera advertência.
  check('publico_mencionado', brief.publico_mencionado?.length > 0,
    { failure: 'Público não mencionado na fonte — tratar como hipótese provisória na estratégia.', warningOnly: true });

  for (const f of reviewerFindings) {
    warnings.push({ check: `reviewer:${f.code}`, severity: f.severity, message: f.message, detail: f.evidence ?? null });
  }

  const status = failures.length > 0 ? 'fail' : warnings.length > 0 ? 'pass_with_warnings' : 'pass';
  return {
    id: newId('gate'),
    gate_id: 'intake-completeness-gate',
    gate_version: '0.1.0',
    project_id: projectId,
    run_id: runId,
    status,
    score: Number((passed / checks).toFixed(2)),
    failures,
    warnings,
    evidence,
    recommended_actions: failures.map((f) =>
      f.category === 'input_gap'
        ? `Solicitar ao humano o insumo faltante: ${f.check}`
        : `Corrigir artefato e reexecutar o gate: ${f.check}`),
    next_action: failures.length === 0
      ? 'aprovar_intake'
      : failures.some((f) => f.category === 'input_gap') ? 'solicitar_decisao_humana' : 'reexecutar_agente',
    created_at: nowIso(),
  };
}
