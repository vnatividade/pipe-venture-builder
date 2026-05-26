# Local pgvector Knowledge Runtime Spike

## Purpose

This spike plan defines a local-only, secret-free way to test whether pgvector-backed semantic recall could improve Pipe Venture Builder execution.

It is a proposal and dry-run design. It does not add Docker Compose files, create a database, run Postgres, integrate an embeddings provider, create an MCP server, or make pgvector part of the production architecture.

## Decision Boundary

The spike must preserve the Knowledge Runtime boundary:

- Markdown repository artifacts remain canonical memory.
- pgvector is recoverable recall infrastructure only.
- Every row must point back to a canonical or operational source artifact.
- The database must be disposable and rebuildable from source artifacts.
- No secrets, production data, customer data, or private evidence may be used.

Use this plan with:

- `architecture/knowledge-runtime-architecture.md`
- `architecture/context-pack-builder-spec.md`
- `schemas/LearningRecord.schema.json`
- `knowledge/learning-record-policy.md`
- `execution/approval-gates.md`

## Non-Goals

This spike does not:

- create production infrastructure
- create a checked-in Docker Compose file
- run Docker or Postgres
- integrate OpenAI, Anthropic, Cohere, Voyage, or any external embeddings provider
- store real customer data, production data, secrets, or private evidence
- implement a Knowledge MCP
- implement automated promotion
- replace `rg`, repository paths, Linear, or GitHub as source systems

## Proposed Local Docker Compose Shape

If a future ticket approves an executable local spike, use a local-only service similar to:

```yaml
services:
  pipe_pgvector:
    image: pgvector/pgvector:pg16
    container_name: pipe_pgvector_spike
    environment:
      POSTGRES_DB: pipe_knowledge_spike
      POSTGRES_USER: pipe_local
      POSTGRES_PASSWORD: pipe_local_only
    ports:
      - "127.0.0.1:55432:5432"
    volumes:
      - pipe_pgvector_spike_data:/var/lib/postgresql/data

volumes:
  pipe_pgvector_spike_data:
```

Rules:

- Bind only to `127.0.0.1`.
- Use local-only throwaway credentials.
- Do not commit real secrets.
- Do not connect to cloud databases.
- Do not ingest customer or production data.
- Keep the compose file out of the repository until an implementation ticket explicitly approves it.

## Proposed `knowledge_items` Table

The minimum spike table should store source-linked recall candidates, not canonical memory.

```sql
create extension if not exists vector;

create table knowledge_items (
  id bigserial primary key,
  source_type text not null check (
    source_type in (
      'repository_markdown',
      'schema',
      'linear_ticket',
      'github_pr',
      'learning_record',
      'decision_record',
      'failure_record',
      'capability_entry',
      'manual_synthetic'
    )
  ),
  record_type text not null check (
    record_type in (
      'learning',
      'decision',
      'capability',
      'idea',
      'run',
      'failure',
      'pattern'
    )
  ),
  canonicality text not null check (
    canonicality in ('canonical', 'operational', 'candidate', 'derived', 'synthetic')
  ),
  source_path_or_url text not null,
  source_id text,
  title text not null,
  summary text not null,
  tags text[] not null default '{}',
  promotion_level text not null check (
    promotion_level in ('L0', 'L1', 'L2', 'L3', 'L4', 'not_applicable')
  ),
  sensitivity text not null check (
    sensitivity in ('public_repo', 'internal', 'sensitive_excluded', 'synthetic')
  ),
  embedding_model text not null default 'synthetic-manual-vector',
  embedding vector(3) not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index knowledge_items_embedding_idx
  on knowledge_items
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 10);

create index knowledge_items_record_type_idx on knowledge_items(record_type);
create index knowledge_items_source_id_idx on knowledge_items(source_id);
```

Why `vector(3)` for the dry run:

- It avoids external embedding providers.
- It lets the team test insert/search mechanics with synthetic vectors.
- It prevents a fake benchmark from being mistaken for model-quality evidence.

A future approved implementation can change the vector dimension after selecting a local or external embedding model.

## Manual Synthetic Insert Flow

Use one synthetic LearningRecord-like row. Do not insert real customer data.

```sql
insert into knowledge_items (
  source_type,
  record_type,
  canonicality,
  source_path_or_url,
  source_id,
  title,
  summary,
  tags,
  promotion_level,
  sensitivity,
  embedding
) values (
  'learning_record',
  'learning',
  'candidate',
  'schemas/LearningRecord.schema.json',
  'LR-SYNTHETIC-0001',
  'Review gate failures require substantive review checks',
  'A PR review object is not enough if the reviewer errored or produced no substantive findings.',
  array['review', 'governance', 'failure'],
  'L1',
  'synthetic',
  '[0.90,0.10,0.10]'
);
```

## Manual Synthetic Search Flow

Use a synthetic query vector. This validates retrieval mechanics only.

```sql
select
  id,
  record_type,
  canonicality,
  source_path_or_url,
  title,
  summary,
  1 - (embedding <=> '[0.85,0.12,0.10]') as cosine_similarity
from knowledge_items
order by embedding <=> '[0.85,0.12,0.10]'
limit 5;
```

Expected conceptual result:

- The inserted synthetic learning row is returned first.
- The row includes the canonical source pointer.
- The result is treated as a candidate recall hit, not a canonical rule.

This validates one LearningRecord insert and one retrieval query conceptually without secrets.

## Dry-Run Evaluation Questions

The spike is useful only if it can answer:

1. Can agents retrieve relevant decisions, failures, capabilities, and constraints faster than with manual `rg` alone?
2. Does retrieval preserve source paths and canonicality labels clearly enough for agents to avoid hidden memory?
3. Can the index be rebuilt from repository, Linear, and GitHub sources?
4. Does the Context Pack Builder stay small when recall returns many candidates?
5. Does pgvector add enough value to justify local runtime maintenance?

If the answer is no, keep using Markdown, Linear, GitHub, and `rg` until recall value is clearer.

## Rollback And Delete Plan

For a future local executable spike:

```bash
docker compose down -v
```

Expected deletion behavior:

- container removed
- local volume removed
- all synthetic spike data deleted
- no canonical repository artifact deleted
- no Linear or GitHub state changed

If any real private data was accidentally inserted, stop immediately, delete the volume, document the incident, and create a follow-up ticket for data-boundary review.

## Secret-Free Operation Rules

Allowed:

- synthetic records
- public repository artifact paths
- manually assigned vectors
- local-only credentials
- source pointers to already-approved repository docs

Forbidden:

- API keys or embedding provider secrets
- customer interviews, customer quotes, or private validation data
- production data
- private Linear/GitHub content that should not be indexed
- legal, financial, compliance, privacy, or security-sensitive claims not already approved
- automatic promotion from retrieved result to canonical rule

## Cost And Maintenance Implications

| Area | Implication | Mitigation |
|---|---|---|
| Local runtime | Requires Docker, Postgres, and pgvector maintenance. | Keep as spike until measured value exists. |
| Data hygiene | Index can drift from canonical Markdown. | Rebuild from source artifacts; store source paths and freshness metadata. |
| Embeddings | Useful embeddings may require model selection, cost, or secrets. | Start with synthetic vectors; require a future approval for real providers. |
| Context bloat | Retrieval can return too much context. | Use `architecture/context-pack-builder-spec.md` size and relevance limits. |
| Governance risk | Agents may treat recall as canonical. | Keep canonicality and promotion-level fields mandatory. |
| Security/privacy | Accidental sensitive data ingestion is possible. | Default to synthetic/public repo data only; delete local volume on any breach. |

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Premature infrastructure | High | Do not commit runnable infra until a later implementation ticket approves it. |
| Hidden memory | High | Require source pointers, canonicality, and promotion level for every row. |
| Sensitive data ingestion | High | Use only synthetic/public repo records; delete local volume if violated. |
| False confidence from synthetic vectors | Medium | Treat synthetic search as mechanics validation only, not retrieval-quality proof. |
| Maintenance drag | Medium | Proceed only if the spike improves agent context quality measurably. |
| Coupling before MCP contract | Medium | Keep direct DB use local-only; future production access should go through a Knowledge MCP or adapter. |

## Success Criteria

The spike should be considered successful only when:

- a synthetic LearningRecord-like item can be inserted
- a synthetic query can retrieve it
- the result includes source path, canonicality, promotion level, and sensitivity status
- the database can be deleted without losing canonical memory
- the team can articulate whether recall improves context-pack creation

It is not successful merely because pgvector runs.

## Decision Gates Before Implementation

Before creating executable infra, require a follow-up ticket that answers:

- Should the spike live under `infra/`, `scripts/`, or remain only in docs?
- Which embedding model, if any, is approved?
- Is local-only Docker acceptable on the user's machine?
- Which source artifacts are allowed to be indexed?
- What is the deletion/audit protocol?
- How will context-pack quality be measured?

## Recommended Next Step

Do not implement Docker Compose yet.

The next useful step is to review this spike plan after the Knowledge MCP contract exists, then decide whether pgvector should remain a local research spike or become an approved retrieval component behind a governed interface.
