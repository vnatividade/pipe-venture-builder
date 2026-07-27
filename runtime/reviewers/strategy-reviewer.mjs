// strategy-reviewer: revisão adversarial ADVISORY dos artefatos de estratégia.
// Independente do executor que os produziu; achados viram warnings do gate.
const PREMATURE = /\b(monetiza\w*|billing|pricing|marketplace|multi-?tenant|escala global|franquia|internacionaliza\w*)\b/i;
const EVIDENCE_CLAIM = /\b(validad\w+|comprovad\w+|clientes confirmaram|mercado de R\$|\d+% dos usu[áa]rios|pesquisas mostram)\b/i;

export function runStrategyReviewer({ files, sourceText }) {
  const findings = [];
  const add = (code, severity, message, evidence) => findings.push({ code, severity, message, evidence: evidence ?? null });
  const all = Object.values(files).filter(Boolean).join('\n');

  for (const line of all.split('\n').map((l) => l.trim()).filter((l) => l.startsWith('- '))) {
    if (EVIDENCE_CLAIM.test(line)) {
      add('claim_de_evidencia', 'P2', 'Afirmação com cara de evidência de mercado — estratégia nesta fase só registra hipóteses.', { line });
    }
    if (PREMATURE.test(line)) {
      add('escopo_prematuro', 'P3', 'Tema de fase posterior (monetização/escala) em artefato de estratégia.', { line });
    }
  }

  const srcTokens = new Set(String(sourceText).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').split(/[^a-z0-9]+/).filter((t) => t.length > 3));
  for (const line of all.split('\n').filter((l) => l.trim().startsWith('- '))) {
    const clean = line.replace(/\(fonte:[^)]+\)/i, '');
    const toks = clean.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').split(/[^a-z0-9]+/).filter((t) => t.length > 3);
    const hit = toks.filter((t) => srcTokens.has(t)).length;
    if (toks.length > 4 && hit / toks.length < 0.3) {
      add('baixa_rastreabilidade_semantica', 'P3', 'Item com pouca sobreposição com as fontes — verificar se é síntese legítima ou invenção.', { line: clean.slice(0, 100) });
    }
  }

  if (!/lacuna|em aberto|decis[ãa]o aberta|hip[óo]tese/i.test(all)) {
    add('sem_lacunas_ou_hipoteses_marcadas', 'P2', 'Nenhuma lacuna/decisão aberta registrada — improvável em estratégia honesta de fase inicial.');
  }

  return { reviewer_id: 'strategy-reviewer', reviewer_version: '0.1.0', findings };
}
