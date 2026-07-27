// intake-reviewer: revisão adversarial simples e ADVISORY.
// Não substitui o gate determinístico (regra da spec e do repositório):
// os achados viram warnings no GateResult, nunca aprovam nem reprovam sozinhos.
const PREMATURE_SCOPE = /\b(marketplace|multi-?tenant|escala global|microservi\w*|blockchain|internacionaliza\w*|white-?label|franquia)\b/i;
const NEGATION = /\b(n[ãa]o|sem|nunca|proibid\w*)\b/i;

function tokens(text) {
  return new Set(String(text).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    .split(/[^a-z0-9]+/).filter((t) => t.length > 3));
}

export function runIntakeReviewer({ brief, sourceText }) {
  const findings = [];
  const add = (code, severity, message, evidence) => findings.push({ code, severity, message, evidence: evidence ?? null });

  // 1. Contradições ingênuas: restrição negada compartilhando termo com funcionalidade pedida.
  for (const r of brief.restricoes ?? []) {
    if (!NEGATION.test(r.text)) continue;
    const rt = tokens(r.text);
    for (const f of brief.funcionalidades_sugeridas ?? []) {
      const shared = [...tokens(f.text)].filter((t) => rt.has(t));
      if (shared.length >= 2) {
        add('possivel_contradicao', 'P2',
          `Restrição e funcionalidade compartilham termos (${shared.slice(0, 3).join(', ')}) — verificar contradição.`,
          { restricao: r.text, funcionalidade: f.text });
      }
    }
  }

  // 2. Invenção de requisitos (defesa em profundidade além do gate).
  const src = tokens(sourceText);
  for (const section of ['funcionalidades_sugeridas', 'problema', 'solucao_imaginada']) {
    for (const item of brief[section] ?? []) {
      if (item.kind !== 'fato') continue;
      const it = [...tokens(item.text)];
      const hit = it.filter((t) => src.has(t)).length;
      if (it.length > 0 && hit / it.length < 0.5) {
        add('conteudo_nao_rastreavel', 'P2', `Item de "${section}" com baixa rastreabilidade à fonte.`, { text: item.text });
      }
    }
  }

  // 3. Ausência de lacunas registradas.
  if (!Array.isArray(brief.lacunas) || brief.lacunas.length === 0) {
    const hasEmpty = ['publico_mencionado', 'restricoes', 'riscos_iniciais'].some((s) => (brief[s] ?? []).length === 0);
    if (hasEmpty) add('lacunas_ausentes', 'P2', 'Seções vazias sem nenhuma lacuna registrada.');
  }

  // 4. Escopo prematuro.
  for (const section of ['solucao_imaginada', 'funcionalidades_sugeridas']) {
    for (const item of brief[section] ?? []) {
      if (PREMATURE_SCOPE.test(item.text)) {
        add('escopo_prematuro', 'P3', 'Termo de escopo prematuro para fase de intake.', { text: item.text });
      }
    }
  }

  // 5. Texto não operacional (fonte curta demais para orientar as próximas fases).
  if (String(sourceText).trim().length < 80) {
    add('texto_nao_operacional', 'P2', 'Fonte muito curta; o brief tende a ser insuficiente para a estratégia.');
  }

  // 6. Falta de decisão seguinte quando há lacunas.
  if ((brief.lacunas ?? []).length > 0 && (brief.decisoes_abertas ?? []).length === 0) {
    add('sem_decisao_seguinte', 'P2', 'Há lacunas registradas mas nenhuma decisão aberta correspondente.');
  }

  return { reviewer_id: 'intake-reviewer', reviewer_version: '0.1.0', findings };
}
