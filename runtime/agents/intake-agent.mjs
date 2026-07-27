// intake-agent (implementação determinística — ver intake-agent.definition.json).
// Normaliza a ideia crua em brief estruturado SEM inventar conteúdo:
// - fato      = texto explícito da fonte, com referência rastreável (fonte#sentença)
// - hipótese  = frase com hedge ("acho", "talvez"...) — registrada como premissa
// - lacuna    = seção obrigatória sem conteúdo na fonte — registrada, nunca preenchida
// Por construção, o agente não consegue inventar requisitos: todo item vem verbatim da fonte.

const SECTION_LABEL = /^(#+\s*)?(problema|solu[çc][ãa]o|p[úu]blico|usu[áa]rios?|funcionalidades?|features?|contexto|restri[çc][õo]es?|depend[êe]ncias?|premissas?|riscos?)\s*[:—-]\s*(.*)$/i;

const RULES = [
  { section: 'problema',        re: /\b(problema|dor(es)?\b|dificuldade|dif[íi]cil|frustra|sofr\w*|perde(m|mos)?\b|n[ãa]o consegue|hoje (n[ãa]o|é|e) )/i },
  { section: 'restricoes',      re: /\b(n[ãa]o pode|sem usar|restri[çc]\w*|proibid|apenas|somente|limite de|lgpd|zero emoji)\b/i },
  { section: 'dependencias',    re: /\b(depende\w*|integra[çc][ãa]o com|integrar com|api d[oa]\b|via (whatsapp|telegram|stripe|pix))\b/i },
  { section: 'riscos',          re: /\b(risco\w*|banid|multa|concorr\w*|vazamento|fraude|inseguran)\b/i },
  { section: 'funcionalidades', re: /\b(deve (permitir|ter|mostrar)|precisa (ter|de)|permitir que|funcionalidade|cadastr\w*|relat[óo]rio|notifica\w*|dashboard|login|exportar)\b/i },
  { section: 'solucao',         re: /\b(quero (criar|construir|fazer|um|uma)|solu[çc][ãa]o|criar um|construir um|app\b|aplicativo|plataforma|sistema|ferramenta|bot\b|site)\b/i },
  { section: 'publico',         re: /\b(p[úu]blico|personas?|clientes?|usu[áa]ri[oa]s?)\b/i },
];

const HEDGE = /\b(acho|talvez|provavelmente|imagino|assumindo|acredito que|pode ser|possivelmente|suponho)\b/i;
const AUDIENCE_PATTERN = /\bpara (os |as |um |uma )?([a-zà-ú]+(?: [a-zà-ú]+){0,4}?) que\b/i;

const EMPTY_BRIEF = () => ({
  descricao_da_ideia: [], problema: [], solucao_imaginada: [], publico_mencionado: [],
  funcionalidades_sugeridas: [], contexto: [], restricoes: [], dependencias: [],
  premissas: [], lacunas: [], riscos_iniciais: [], decisoes_abertas: [],
});

const SECTION_KEY = {
  problema: 'problema', solucao: 'solucao_imaginada', publico: 'publico_mencionado',
  funcionalidades: 'funcionalidades_sugeridas', contexto: 'contexto', restricoes: 'restricoes',
  dependencias: 'dependencias', premissas: 'premissas', riscos: 'riscos_iniciais',
};

function segments(sourceName, content) {
  const out = [];
  let idx = 0;
  let currentSection = null; // rótulo ativo: herdado apenas por bullets subsequentes
  for (const rawLine of content.split(/\n+/)) {
    const line = rawLine.trim();
    if (!line) continue;
    const label = line.match(SECTION_LABEL);
    if (label) {
      currentSection = normalizeLabel(label[2]);
      const rest = label[3]?.trim();
      if (rest) out.push({ text: rest.replace(/[.!?]+$/, ''), source: `${sourceName}#s${idx++}`, labeled: currentSection });
      continue;
    }
    const bullet = line.replace(/^[-*•]\s+/, '');
    const isBullet = bullet !== line;
    if (!isBullet) currentSection = null; // frase solta encerra a seção rotulada
    for (const sentence of bullet.split(/(?<=[.!?])\s+/)) {
      const text = sentence.trim().replace(/[.!?]+$/, '');
      if (text.length < 3) continue;
      out.push({ text, source: `${sourceName}#s${idx++}`, bullet: isBullet, labeled: isBullet ? currentSection : null });
    }
  }
  return out;
}

function normalizeLabel(word) {
  const w = word.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  if (w.startsWith('solu')) return 'solucao';
  if (w.startsWith('publ') || w.startsWith('usuari')) return 'publico';
  if (w.startsWith('func') || w.startsWith('feat')) return 'funcionalidades';
  if (w.startsWith('restr')) return 'restricoes';
  if (w.startsWith('depend')) return 'dependencias';
  if (w.startsWith('premis')) return 'premissas';
  if (w.startsWith('risc')) return 'riscos';
  if (w.startsWith('prob')) return 'problema';
  return 'contexto';
}

function classify(seg) {
  if (seg.labeled) return seg.labeled;
  if (HEDGE.test(seg.text)) return 'premissas';
  for (const rule of RULES) if (rule.re.test(seg.text)) return rule.section;
  return 'contexto';
}

export function runIntakeAgent({ sources, agentDef }) {
  const brief = EMPTY_BRIEF();
  const assumptions = [];
  const allSegments = sources.flatMap((s) => segments(s.name, s.content));

  for (const seg of allSegments) {
    const section = classify(seg);
    // Rótulo "premissas" força hipótese: premissa é hipótese por definição de seção.
    const kind = section === 'premissas' || HEDGE.test(seg.text) ? 'hipotese' : 'fato';
    if (kind === 'hipotese') {
      assumptions.push({ text: seg.text, source: seg.source, rationale: 'frase com marcador de incerteza na fonte' });
    }
    brief[SECTION_KEY[section]].push({ text: seg.text, kind, source: seg.source });
    // Extração secundária de público via padrão "para <grupo> que ..." (verbatim = fato).
    const aud = seg.text.match(AUDIENCE_PATTERN);
    if (aud && section !== 'publico') {
      brief.publico_mencionado.push({ text: aud[2].trim(), kind: 'fato', source: seg.source });
    }
  }

  brief.descricao_da_ideia = allSegments.slice(0, 3).map((s) => ({ text: s.text, kind: 'fato', source: s.source }));

  // Lacunas e decisões abertas — nunca preencher, sempre registrar.
  const gaps = [];
  if (brief.problema.length === 0) gaps.push({ section: 'problema', blocking: true });
  if (brief.solucao_imaginada.length === 0) gaps.push({ section: 'solucao_imaginada', blocking: true });
  if (brief.publico_mencionado.length === 0) gaps.push({ section: 'publico_mencionado', blocking: false });
  for (const key of ['funcionalidades_sugeridas', 'contexto', 'restricoes', 'dependencias', 'premissas', 'riscos_iniciais']) {
    if (brief[key].length === 0) gaps.push({ section: key, blocking: false });
  }
  for (const gap of gaps) {
    brief.lacunas.push(`Seção "${gap.section}" sem conteúdo na fonte${gap.blocking ? ' (bloqueadora para o gate de intake)' : ''}.`);
  }
  for (const gap of gaps.filter((g) => g.blocking)) {
    brief.decisoes_abertas.push({
      topic: `${gap.section}_nao_identificado`, blocking: true,
      reason: `A fonte não contém ${gap.section === 'problema' ? 'um problema preliminar' : 'uma solução imaginada'}; o agente não inventa conteúdo — decisão/insumo humano necessário.`,
    });
  }
  if (brief.publico_mencionado.length === 0) {
    brief.decisoes_abertas.push({
      topic: 'publico_nao_identificado', blocking: false,
      reason: 'Público não mencionado na fonte; tratado como hipótese provisória a definir na fase de estratégia (não bloqueia o intake).',
    });
  }

  const metadata = {
    agent_id: agentDef.id,
    agent_version: agentDef.version,
    implementation: agentDef.implementation,
    model: 'deterministic/rule-based@0.1.0',
    prompt_version: agentDef.version,
    sources: sources.map((s) => s.name),
    stats: { segments: allSegments.length, assumptions: assumptions.length, gaps: gaps.length },
  };

  return { brief, assumptions, metadata, markdown: renderMarkdown(brief, metadata) };
}

const SECTION_TITLES = [
  ['descricao_da_ideia', 'Descrição da ideia'], ['problema', 'Problema'],
  ['solucao_imaginada', 'Solução imaginada'], ['publico_mencionado', 'Público mencionado'],
  ['funcionalidades_sugeridas', 'Funcionalidades sugeridas'], ['contexto', 'Contexto'],
  ['restricoes', 'Restrições'], ['dependencias', 'Dependências'], ['premissas', 'Premissas'],
  ['riscos_iniciais', 'Riscos iniciais'],
];

function renderMarkdown(brief, metadata) {
  const lines = ['# Initial Brief', '', `Gerado por ${metadata.agent_id}@${metadata.agent_version} (${metadata.implementation}) a partir de: ${metadata.sources.join(', ')}.`, ''];
  for (const [key, title] of SECTION_TITLES) {
    lines.push(`## ${title}`, '');
    if (brief[key].length === 0) lines.push('_Sem conteúdo na fonte (ver Lacunas)._', '');
    else {
      for (const item of brief[key]) lines.push(`- [${item.kind}] ${item.text} _(fonte: ${item.source})_`);
      lines.push('');
    }
  }
  lines.push('## Lacunas', '');
  brief.lacunas.forEach((l) => lines.push(`- ${l}`));
  lines.push('', '## Decisões abertas', '');
  if (brief.decisoes_abertas.length === 0) lines.push('_Nenhuma._');
  else brief.decisoes_abertas.forEach((d) => lines.push(`- ${d.blocking ? '**[bloqueadora]**' : '[não bloqueadora]'} ${d.topic}: ${d.reason}`));
  lines.push('');
  return lines.join('\n');
}
