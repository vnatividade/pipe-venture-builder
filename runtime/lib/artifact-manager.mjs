// Artifact Manager: cria, versiona e registra artefatos com proveniência e hash.
// Idempotência: mesmo (projeto, tipo, hash de conteúdo) não duplica — retorna o existente.
// Supersessão é marcada, nunca apagada (lei do repositório).
import { newId, nowIso, sha256 } from './ids.mjs';

export class ArtifactManager {
  constructor(store) { this.store = store; }

  register({ slug, projectId, runId, phase, type, filename, content, createdBy, agentId, model, promptVersion, sourceRefs }) {
    const manifest = this.store.loadManifest(slug);
    const hash = sha256(content);

    const dup = manifest.artifacts.find((a) => a.type === type && a.hash === hash && a.status === 'present');
    if (dup) return { artifact: dup, deduplicated: true };

    const priorVersions = manifest.artifacts.filter((a) => a.type === type);
    const version = priorVersions.length + 1;
    for (const prior of priorVersions.filter((a) => a.status === 'present')) {
      prior.status = 'superseded';
      prior.superseded_by = null; // preenchido abaixo
    }

    const relPath = `${type}/v${version}/${filename}`;
    this.store.writeArtifactFile(slug, relPath, content);

    const artifact = {
      id: newId('art'),
      project_id: projectId,
      run_id: runId,
      phase,
      type,
      version,
      path: `artifacts/${relPath}`,
      status: 'present',
      hash,
      created_by: createdBy,
      agent_id: agentId,
      model,
      prompt_version: promptVersion,
      source_refs: sourceRefs ?? [],
      validation: null,
      created_at: nowIso(),
    };
    for (const prior of priorVersions) if (prior.superseded_by === null) prior.superseded_by = artifact.id;
    manifest.artifacts.push(artifact);
    this.store.saveManifest(slug, manifest);
    return { artifact, deduplicated: false };
  }

  attachValidation(slug, artifactId, validation) {
    const manifest = this.store.loadManifest(slug);
    const artifact = manifest.artifacts.find((a) => a.id === artifactId);
    if (!artifact) throw new Error(`artefato não encontrado: ${artifactId}`);
    artifact.validation = validation;
    this.store.saveManifest(slug, manifest);
    return artifact;
  }

  current(slug, type) {
    const manifest = this.store.loadManifest(slug);
    return manifest.artifacts.find((a) => a.type === type && a.status === 'present') ?? null;
  }

  list(slug) { return this.store.loadManifest(slug).artifacts; }
}
