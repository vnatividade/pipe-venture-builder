// Prompt Compiler v0 (implementa o essencial de architecture/context-pack-builder-spec.md).
// Gera o pacote de instruções de um agente por REFERÊNCIA às fontes oficiais (nunca cópia
// integral), com precedência, escopo, decisões, suposições, gate e handoff. O pacote é
// registrado como artefato versionado (hash/proveniência) — prompt não é texto descartável.
import { sha256, nowIso } from './ids.mjs';
import { loadProjectBaseline } from './baseline-bridge.mjs';

export const COMPILER_VERSION = '0.1.0';

export function compilePromptPackage({ store, slug, project, workflowDef, agentDef, artifacts }) {
  const brief = artifacts.current(slug, 'initial-brief');
  const baseline = loadProjectBaseline(store, slug);
  const decisions = store.listDecisions(slug).filter((d) => d.status === 'resolved');
  const sources = store.listSources(slug);

  const refs = [
    brief && { name: `brief:${brief.path}`, hash: brief.hash, precedence: 2, note: 'brief aprovado (fatos/hipóteses/lacunas com fonte)' },
    baseline && { name: `baseline:baseline/baseline-v${baseline.version}.json`, hash: sha256(JSON.stringify(baseline.baseline)), precedence: 1, note: 'estado canônico (statements classificados)' },
    ...sources.map((s) => ({ name: `source:sources/${s.name}`, hash: sha256(s.content), precedence: 3, note: 'fonte original do fundador' })),
  ].filter(Boolean);

  const assumptions = brief
    ? JSON.parse(store.readArtifactFile(slug, brief.path.replace(/^artifacts\//, ''))).assumptions ?? []
    : [];

  const markdown = [
    `# Pacote de instruções — ${agentDef.id}@${agentDef.version}`,
    '',
    `Compilado por prompt-compiler@${COMPILER_VERSION} em ${nowIso()} · projeto ${project.slug} · workflow ${workflowDef.id}@${workflowDef.version} · executor-alvo: ${agentDef.executor ?? 'claude-code'}`,
    '',
    '## Papel', agentDef.mission,
    '',
    '## Objetivo',
    `Produzir os entregáveis da fase ${workflowDef.next_phase_on_success?.phase ?? workflowDef.id} listados em Saídas, usando SOMENTE as fontes referenciadas.`,
    '',
    '## Contexto mínimo (referências, em ordem de precedência — não copiar integralmente)',
    ...refs.sort((a, b) => a.precedence - b.precedence).map((r) => `- [P${r.precedence}] ${r.name} (sha256 ${r.hash.slice(0, 12)}) — ${r.note}`),
    '',
    '## Decisões aprovadas',
    decisions.length ? decisions.map((d) => `- ${d.id} (${d.reason_code}): ${d.resolution.option_id} por ${d.resolution.decided_by}${d.resolution.free_text ? ` — "${d.resolution.free_text}"` : ''}`).join('\n') : '_Nenhuma._',
    '',
    '## Suposições registradas',
    assumptions.length ? assumptions.map((a) => `- ${a.text} (${a.source})`).join('\n') : '_Nenhuma._',
    '',
    '## Escopo', ...(workflowDef.scope ?? ['Definido pelos entregáveis abaixo.']).map((s) => `- ${s}`),
    '',
    '## Fora do escopo', ...(workflowDef.out_of_scope ?? []).map((s) => `- ${s}`),
    '',
    '## Entradas', 'As referências do Contexto mínimo. Nada além delas.',
    '',
    '## Saídas esperadas',
    ...(workflowDef.outputs ?? []).map((o) => `- \`${o}.md\``),
    '',
    '**Convenção obrigatória de rastreabilidade:** todo item afirmativo termina com `(fonte: <ref>)` apontando para brief/baseline/fonte/decisão. Item sem fonte é tratado como invenção pelo gate.',
    '',
    '## Restrições de ferramentas',
    ...(agentDef.forbidden_actions ?? []).map((f) => `- NÃO: ${f}`),
    '',
    '## Critérios de qualidade / Gate',
    ...(workflowDef.gates ?? []).map((g) => `- Gate determinístico: \`${g}\` (reprova invenção, seções ausentes e itens sem fonte).`),
    '',
    '## Handoff esperado',
    `Submeter via \`pipe-os submit --project ${project.slug} --files <caminhos>\`; o gate decide aprovar, pedir correção ou escalar decisão humana.`,
    '',
  ].join('\n');

  return {
    markdown,
    metadata: {
      compiler_version: COMPILER_VERSION,
      agent: `${agentDef.id}@${agentDef.version}`,
      workflow: `${workflowDef.id}@${workflowDef.version}`,
      refs: refs.map((r) => ({ name: r.name, hash: r.hash, precedence: r.precedence })),
      decisions: decisions.map((d) => d.id),
      chars: markdown.length,
    },
  };
}
