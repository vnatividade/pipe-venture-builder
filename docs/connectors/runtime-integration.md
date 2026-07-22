# Runtime Integration For Read-Only Connectors

The adapter package separates credential-owning tooling from Pipe's normalization code. A runtime may bind an authenticated connector only after the applicable approval is recorded; no token or header is passed into the adapter.

## Linear Host Contract

`LinearConnectorSource` accepts one callable with this shape:

```python
def invoke(tool_name: str, arguments: Mapping[str, Any]) -> Mapping[str, Any]: ...
```

The source chooses the tool name. The host cannot ask it to call arbitrary operations:

- `linear_get_project` with the configured project identifier
- `linear_list_issues` with project, bounded limit, and optional cursor

The host returns a decoded, non-sensitive mapping. It should translate connector authentication, availability, and rate-limit failures into either the documented safe error code or the corresponding adapter exception. It must not include response headers, credential material, raw request envelopes, issue bodies, or comments.

The adapter recognizes these safe result forms:

- project mapping directly, or `{ "project": { ... } }`
- issue list under `issues`, `items`, `nodes`, or `data`
- pagination under `pageInfo` or `nextCursor`/`hasMore`
- error code under `error.code`, `error.type`, `error.status`, or `errorCode`

All other shapes fail closed as `source_contract_failed`.

## GitHub CLI Contract

`GitHubGhCliSource` invokes only these read commands using an argument array, never a shell:

```txt
gh repo view OWNER/REPO --json ...
gh issue list --repo OWNER/REPO --state all --limit N --json ...
gh pr list --repo OWNER/REPO --state all --limit N --json ...
gh release list --repo OWNER/REPO --limit N --json ...
```

The CLI owns its existing authentication context. Pipe does not call `gh auth token`, inspect environment variables, construct headers, or return stderr. Missing CLI/network state becomes `unavailable`; authentication errors become `unauthorized`; provider rate limits become `rate_limited`.

## Fixture-First Example

```python
from pipe_venture_builder.adapters import FixtureInventorySource, LinearInventoryAdapter

source = FixtureInventorySource(
    "tests/fixtures/connectors/linear-pages.json",
    source_system="linear",
    container_type="project",
)
snapshot = LinearInventoryAdapter(source).capture(
    "linear-project-001",
    captured_at="2026-07-21T12:00:00Z",
)
```

Fixture and live sources feed the same normalizer. A runtime should validate the returned dictionary against `schemas/ExternalSnapshot.schema.json` before persisting or passing it to reconciliation.

## Stop Conditions

Do not start or continue a live read when:

- credential use has not received the required explicit approval
- the target project or repository is not the ProductManifest binding
- customer, production, private, or sensitive data would enter the response
- the runtime would need to add a mutation-capable callback to the read interface
- the source returns raw headers or secret-shaped content
- the configured bounds are insufficient for a decision and a narrower follow-up has not been defined

The correct response is an explicit snapshot status or a documented blocker, never an empty inventory substitute.
