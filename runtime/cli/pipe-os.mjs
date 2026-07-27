#!/usr/bin/env node
// CLI da fatia vertical do Venture-to-Execution OS.
// Uso: node runtime/cli/pipe-os.mjs <comando> [opções]
// Comandos mutantes exigem VENTURE_OS_ENABLED=true (default: desabilitado).
// Nome "pipe-os" evita colisão com o futuro CLI oficial `pipe` (branches pip-706+).
import { readFileSync } from 'node:fs';
import { Store, defaultProjectsRoot } from '../lib/store.mjs';
import { ventureOsEnabled } from '../lib/flag.mjs';
import { newId } from '../lib/ids.mjs';
import {
  createProject, createProjectFromBaseline, executeWorkflow, respondDecision, pauseProject, resumeProject, cancelProject,
} from '../lib/engine.mjs';
import { DecisionQueue } from '../lib/decisions.mjs';

function parseArgs(argv) {
  const [cmd, ...rest] = argv;
  const opts = {};
  for (let i = 0; i < rest.length; i++) {
    if (rest[i].startsWith('--')) {
      const key = rest[i].slice(2);
      const val = rest[i + 1] && !rest[i + 1].startsWith('--') ? rest[++i] : true;
      opts[key] = val;
    }
  }
  return { cmd, opts };
}

const HELP = `pipe-os — fatia vertical do Venture-to-Execution OS (feature flag: VENTURE_OS_ENABLED)

Comandos mutantes (exigem VENTURE_OS_ENABLED=true):
  create-project --name <nome> (--idea "<texto>" | --idea-file <caminho>) [--description "<...>"]
  create-project --from-baseline <baseline.json>   semeia projeto de um ProductBaseline canônico (pipe idea/adopt)
  run            --project <slug>
  resume         --project <slug>
  pause          --project <slug>
  cancel         --project <slug>
  respond        --project <slug> --decision <id> --option <id> [--text "<...>"] --by <nome>

Comandos de leitura:
  show           --project <slug>       estado do projeto
  projects                              lista projetos
  runs           --project <slug>
  artifacts      --project <slug>
  gates          --project <slug>       validações de gate por artefato
  decisions      --project <slug> [--pending]
  events         --project <slug> [--tail <n>]
  transitions    --project <slug>

Variáveis: VENTURE_OS_PROJECTS_ROOT (default ~/.pipe/venture-os/projects), VENTURE_OS_LOG_SILENT=1`;

function out(obj) { process.stdout.write(JSON.stringify(obj, null, 2) + '\n'); }

export function main(argv = process.argv.slice(2), env = process.env) {
  const { cmd, opts } = parseArgs(argv);
  const store = new Store(defaultProjectsRoot(env));
  const correlationId = newId('cor');

  if (!cmd || cmd === 'help' || cmd === '--help') { process.stdout.write(HELP + '\n'); return 0; }

  const READ_CMDS = ['show', 'projects', 'runs', 'artifacts', 'gates', 'decisions', 'events', 'transitions'];
  if (READ_CMDS.includes(cmd) && !ventureOsEnabled(env)) {
    process.stderr.write('aviso: VENTURE_OS_ENABLED não está ativa; leitura permitida, comandos mutantes recusarão.\n');
  }

  const slug = opts.project;
  switch (cmd) {
    case 'create-project': {
      if (typeof opts['from-baseline'] === 'string') {
        const project = createProjectFromBaseline({ store, baselinePath: opts['from-baseline'], correlationId, env });
        out({ ok: true, project: { id: project.id, slug: project.slug, state: project.current_state, baseline: project.baseline_ref, next_action: project.next_action } });
        return 0;
      }
      const ideaText = opts['idea-file'] ? readFileSync(opts['idea-file'], 'utf8') : (typeof opts.idea === 'string' ? opts.idea : '');
      const project = createProject({ store, name: String(opts.name ?? ''), description: String(opts.description ?? ''), ideaText, correlationId, env });
      out({ ok: true, project: { id: project.id, slug: project.slug, state: project.current_state, next_action: project.next_action } });
      return 0;
    }
    case 'run': {
      const result = executeWorkflow({ store, slug, correlationId, env });
      out(renderRunResult(result));
      return result.error ? 1 : 0;
    }
    case 'resume': {
      const result = resumeProject({ store, slug, correlationId, env });
      out(result.run ? renderRunResult(result) : { ok: true, project_state: result.project.current_state });
      return 0;
    }
    case 'pause': out({ ok: true, project_state: pauseProject({ store, slug, correlationId, env }).current_state }); return 0;
    case 'cancel': out({ ok: true, project_state: cancelProject({ store, slug, correlationId, env }).current_state }); return 0;
    case 'respond': {
      const result = respondDecision({
        store, slug, decisionId: opts.decision, optionId: opts.option,
        freeText: typeof opts.text === 'string' ? opts.text : null, decidedBy: String(opts.by ?? ''), correlationId, env,
      });
      out({ ok: true, decision: result.decision.id, resolution: result.decision.resolution, project_state: result.project.current_state, next: result.project.next_action });
      return 0;
    }
    case 'show': {
      const p = store.loadProject(slug);
      out(p);
      return 0;
    }
    case 'projects': out(store.listProjects()); return 0;
    case 'runs': out(store.listRuns(slug)); return 0;
    case 'artifacts': out(store.loadManifest(slug).artifacts); return 0;
    case 'gates': {
      out(store.loadManifest(slug).artifacts
        .filter((a) => a.validation)
        .map((a) => ({ artifact: `${a.type} v${a.version}`, artifact_id: a.id, ...a.validation })));
      return 0;
    }
    case 'decisions': {
      const q = new DecisionQueue(store);
      out(opts.pending ? q.listPending(slug) : store.listDecisions(slug));
      return 0;
    }
    case 'events': {
      const events = store.listEvents(slug);
      out(opts.tail ? events.slice(-Number(opts.tail)) : events);
      return 0;
    }
    case 'transitions': out(store.listTransitions(slug)); return 0;
    default:
      process.stderr.write(`comando desconhecido: ${cmd}\n${HELP}\n`);
      return 2;
  }
}

function renderRunResult(result) {
  const base = { ok: !result.error, project_state: result.project.current_state, run: { id: result.run?.id, status: result.run?.status, attempt: result.run?.attempt } };
  if (result.artifact) base.artifact = { id: result.artifact.id, type: result.artifact.type, version: result.artifact.version, path: result.artifact.path };
  if (result.gateResult) base.gate = { id: result.gateResult.id, status: result.gateResult.status, score: result.gateResult.score, failures: result.gateResult.failures.map((f) => f.check), warnings: result.gateResult.warnings.length };
  if (result.decision) base.pending_decision = { id: result.decision.id, options: result.decision.options.map((o) => o.id), recommendation: result.decision.recommendation, safe_default: result.decision.safe_default };
  if (result.project.next_action) base.next_action = result.project.next_action;
  if (result.error) base.error = result.error;
  return base;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    process.exit(main());
  } catch (err) {
    process.stderr.write(`erro${err.code ? ` [${err.code}]` : ''}: ${err.message}\n`);
    process.exit(1);
  }
}
