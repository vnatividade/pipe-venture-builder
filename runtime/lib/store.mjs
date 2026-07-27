// Persistência em arquivos estruturados, protegida por interface.
// NÃO é a solução final (ver ADR-VOS-001): estado durável em JSON com escrita
// atômica (tmp+rename), versionamento otimista (state_version), histórico de
// transições e log de eventos em JSONL. Substituível por SQLite sem mudar o domínio.
import { mkdirSync, readFileSync, writeFileSync, renameSync, existsSync, readdirSync, appendFileSync } from 'node:fs';
import { join, resolve, sep } from 'node:path';
import { homedir } from 'node:os';
import { nowIso } from './ids.mjs';

export function defaultProjectsRoot(env = process.env) {
  // Camada machine-local (portable-bootstrap): nunca dentro do repositório do pipe.
  return env.VENTURE_OS_PROJECTS_ROOT || join(homedir(), '.pipe', 'venture-os', 'projects');
}

export class Store {
  constructor(projectsRoot) {
    this.root = resolve(projectsRoot);
    mkdirSync(this.root, { recursive: true });
  }

  // Anti path-traversal: todo caminho resolvido precisa ficar sob a raiz.
  safePath(...parts) {
    const p = resolve(this.root, ...parts);
    if (p !== this.root && !p.startsWith(this.root + sep)) {
      throw Object.assign(new Error(`caminho fora da raiz do store: ${parts.join('/')}`), { code: 'PATH_TRAVERSAL' });
    }
    return p;
  }

  projectDir(slug) { return this.safePath(slug); }

  atomicWriteJson(path, obj) {
    const tmp = `${path}.tmp-${process.pid}-${Date.now()}`;
    writeFileSync(tmp, JSON.stringify(obj, null, 2) + '\n');
    renameSync(tmp, path);
  }

  atomicWriteText(path, text) {
    const tmp = `${path}.tmp-${process.pid}-${Date.now()}`;
    writeFileSync(tmp, text);
    renameSync(tmp, path);
  }

  readJson(path) { return JSON.parse(readFileSync(path, 'utf8')); }

  // ---- Project ----
  projectExists(slug) { return existsSync(this.safePath(slug, 'project.json')); }

  initProject(project) {
    const dir = this.projectDir(project.slug);
    if (this.projectExists(project.slug)) {
      const err = new Error(`projeto já existe: ${project.slug}`);
      err.code = 'DUPLICATE_PROJECT';
      throw err;
    }
    for (const sub of ['runs', 'artifacts', 'decisions', 'sources']) {
      mkdirSync(join(dir, sub), { recursive: true });
    }
    this.atomicWriteJson(join(dir, 'project.json'), project);
    return project;
  }

  loadProject(slug) {
    if (!this.projectExists(slug)) {
      const err = new Error(`projeto não encontrado: ${slug}`);
      err.code = 'NOT_FOUND';
      throw err;
    }
    return this.readJson(this.safePath(slug, 'project.json'));
  }

  // Atualização com concorrência otimista: falha se a versão em disco divergir.
  saveProject(project, expectedVersion) {
    const current = this.loadProject(project.slug);
    if (current.state_version !== expectedVersion) {
      const err = new Error(
        `conflito de versão em ${project.slug}: disco=${current.state_version}, esperado=${expectedVersion}`);
      err.code = 'VERSION_CONFLICT';
      throw err;
    }
    project.state_version = expectedVersion + 1;
    project.updated_at = nowIso();
    this.atomicWriteJson(this.safePath(project.slug, 'project.json'), project);
    return project;
  }

  listProjects() {
    return readdirSync(this.root, { withFileTypes: true })
      .filter((d) => d.isDirectory() && existsSync(join(this.root, d.name, 'project.json')))
      .map((d) => d.name);
  }

  // ---- Transitions history (auditoria) ----
  appendTransition(slug, record) {
    appendFileSync(this.safePath(slug, 'state-history.jsonl'), JSON.stringify(record) + '\n');
  }

  listTransitions(slug) {
    const p = this.safePath(slug, 'state-history.jsonl');
    if (!existsSync(p)) return [];
    return readFileSync(p, 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l));
  }

  // ---- Events (log append-only) ----
  appendEvent(slug, event) {
    appendFileSync(this.safePath(slug, 'events.jsonl'), JSON.stringify(event) + '\n');
  }

  listEvents(slug) {
    const p = this.safePath(slug, 'events.jsonl');
    if (!existsSync(p)) return [];
    return readFileSync(p, 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l));
  }

  // ---- Runs ----
  saveRun(slug, run) { this.atomicWriteJson(this.safePath(slug, 'runs', `${run.id}.json`), run); }

  loadRun(slug, runId) { return this.readJson(this.safePath(slug, 'runs', `${runId}.json`)); }

  listRuns(slug) {
    const dir = this.safePath(slug, 'runs');
    if (!existsSync(dir)) return [];
    return readdirSync(dir).filter((f) => f.endsWith('.json'))
      .map((f) => this.readJson(join(dir, f)))
      .sort((a, b) => a.started_at.localeCompare(b.started_at));
  }

  // ---- Artifacts ----
  artifactsManifestPath(slug) { return this.safePath(slug, 'artifacts', 'manifest.json'); }

  loadManifest(slug) {
    const p = this.artifactsManifestPath(slug);
    return existsSync(p) ? this.readJson(p) : { artifacts: [] };
  }

  saveManifest(slug, manifest) { this.atomicWriteJson(this.artifactsManifestPath(slug), manifest); }

  writeArtifactFile(slug, relPath, content) {
    const p = this.safePath(slug, 'artifacts', relPath);
    mkdirSync(resolve(p, '..'), { recursive: true });
    this.atomicWriteText(p, content);
    return p;
  }

  readArtifactFile(slug, relPath) { return readFileSync(this.safePath(slug, 'artifacts', relPath), 'utf8'); }

  // ---- Sources (ideia + clarificações) ----
  writeSource(slug, name, content) {
    const p = this.safePath(slug, 'sources', name);
    this.atomicWriteText(p, content);
    return p;
  }

  listSources(slug) {
    const dir = this.safePath(slug, 'sources');
    if (!existsSync(dir)) return [];
    return readdirSync(dir).sort().map((name) => ({ name, content: readFileSync(join(dir, name), 'utf8') }));
  }

  // ---- Human decisions ----
  saveDecision(slug, decision) {
    this.atomicWriteJson(this.safePath(slug, 'decisions', `${decision.id}.json`), decision);
  }

  listDecisions(slug) {
    const dir = this.safePath(slug, 'decisions');
    if (!existsSync(dir)) return [];
    return readdirSync(dir).filter((f) => f.endsWith('.json'))
      .map((f) => this.readJson(join(dir, f)))
      .sort((a, b) => a.created_at.localeCompare(b.created_at));
  }

  loadDecision(slug, id) { return this.readJson(this.safePath(slug, 'decisions', `${id}.json`)); }
}
