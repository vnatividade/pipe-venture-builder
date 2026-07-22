# Portable Bootstrap And Runtime Boundaries

## Purpose

This specification defines how Pipe Venture Builder should become usable on another computer without depending on one founder's directory layout, chat history, or agent-specific memory.

It defines the portability decision from `architecture/adr/adr-001-dual-entry-product-intake.md`. PIP-709 implements the initial ProductManifest, repository-local bootstrap, and read-only doctor subset described below.

Origin ticket: PIP-700.

It does not authenticate connectors, copy secrets, install executors or adapters, configure production, or mutate Linear/GitHub.

## Portability Outcome

A successful future bootstrap should let an operator:

1. clone or install a versioned Pipe distribution
2. run one diagnostic command
3. bind a new or existing product repository to Pipe
4. use `idea` or `adopt`
5. execute the same governed workflow through an available runtime
6. inspect missing capabilities and approvals without guessing

The operator may still need to authenticate Linear, GitHub, or other connectors interactively. Portability means reproducible configuration and diagnostics, not copying credentials.

## Three-Layer Distribution

### 1. Versioned Pipe toolkit

Contains:

- governance policies and approval contracts
- schemas
- product, validation, architecture, execution, and knowledge workflows
- agent/skill contracts
- Capability Registry
- runtime adapters and bootstrap manifests when implemented
- version and compatibility metadata

The toolkit is the shared, upgradeable distribution. Product-specific facts do not belong here.

### 2. Product repository

Contains:

- product-specific canonical artifacts
- `.pipe/mode.json`, controlled by the human-only operating-mode rule
- future `.pipe/project.json` with non-sensitive Pipe binding metadata
- source code, tests, architecture decisions, and delivery references
- safe pointers to Linear/GitHub containers

The product repository must remain understandable without the toolkit's installation directory being a fixed path.

### 3. Machine-local runtime state

Contains:

- installed executor binaries and versions
- connector authentication managed by each connector/runtime
- caches and pinned external dependency clones
- run/event/checkpoint database
- logs and temporary artifacts
- symlinks or registration records created by adapters

Machine-local state is recoverable. It must not be the only place holding product decisions, approvals, delivery evidence, or reusable learning.

## Product Manifest

PIP-709 creates `.pipe/project.json` in each product repository using the canonical `schemas/ProductManifest.schema.json` contract. The tracked example is `setup/ProductManifest.example.json`:

```json
{
  "schemaVersion": "0.1.0",
  "productId": "example-product",
  "pipeVersion": "0.1.0",
  "entryMode": "idea",
  "repository": {
    "root": "."
  },
  "linear": {
    "projectId": null
  },
  "github": {
    "repository": null
  },
  "capabilities": {
    "enabled": [
      "capability.internal.atelier"
    ]
  },
  "runtime": {
    "preferred": "hermes",
    "fallbacks": [
      "codex",
      "claude-code"
    ]
  }
}
```

Rules:

- Store stable identifiers and desired capability/runtime selection only.
- Never store tokens, credential paths, customer data, production data, or private source content.
- Never use the manifest to override `AGENTS.md`, approval gates, or `.pipe/mode.json`.
- Missing or invalid manifest means the product is unbound, not automatically greenfield.
- `pipe adopt` may propose a manifest, but creating or changing it requires the implementation ticket's write scope.

PIP-709 is the dedicated approved ticket for this contract. Bootstrap validates before creation, never overwrites an existing manifest, and doctor checks compatibility against the installed Pipe version.

## Command Contracts

Bootstrap and doctor are executable in the Python CLI. The remaining control-plane commands stay governed follow-up work.

### `pipe bootstrap`

Purpose: plan or create the repository-local ProductManifest and diagnose the selected local runtime without installing executors, adapters, dependencies, or credentials.

Implemented steps:

1. Resolve the toolkit from an explicit argument, machine-local environment hint, source checkout, or current ancestry, never a hard-coded user directory.
2. Validate the proposed ProductManifest against the canonical schema.
3. Show a deterministic non-mutating plan by default.
4. With explicit `--apply`, create only `.pipe/` when needed and `.pipe/project.json` with non-overwriting semantics.
5. Preserve `.pipe/mode.json` as human-only and report when it is absent or invalid.
6. Finish apply with `pipe doctor`.

Executor/adapter installation, dependency caches, connector authentication, and reversible adapter registration remain PIP-713/PIP-714 work.

Stop when:

- an existing non-symlink path would be overwritten
- dependency integrity cannot be verified
- installation requires secrets or elevated privileges not explicitly approved
- a runtime adapter is incompatible with the selected Pipe version
- the installer would modify a product repository outside the declared target

### `pipe doctor`

Purpose: produce a read-only, redacted readiness report.

Checks:

- Pipe toolkit version and clean release identity
- product manifest presence and compatibility
- `.pipe/mode.json` validity without changing it
- repository root and Git availability
- Linear/GitHub connector availability and authentication status
- Codex, Claude Code, and Hermes adapter availability
- Capability Registry entry and referenced path existence
- schema parse/validation tooling
- pinned dependency presence and commit match
- user-specific hard-coded path scan
- write permissions only for intended local/cache/output directories
- stale baseline or reconciliation plan indicators

Output statuses:

```txt
ready
ready_with_warnings
blocked
not_configured
not_applicable
```

Individual checks additionally distinguish `configured`, `unavailable`, `unauthorized`, `incompatible`, `blocked`, and `not_applicable`. The overall report keeps the readiness statuses above.

The report must redact tokens, usernames when unnecessary, private repository URLs when sensitive, and local paths that reveal private context in shared logs.

### `pipe idea --source <artifact>`

Purpose: run the `idea` entry contract and produce or update ProductBaseline.

The source may be a safe repository artifact, guided-session handoff, or approved external pointer. The command must not assume the source is evidence of demand.

### `pipe adopt --repo <path>`

Purpose: run read-only brownfield inventory and produce ProductBaseline, governance gaps, and reconciliation proposals.

External systems remain read-only during the adoption command. Applying proposals is a separate, approved operation.

### `pipe status`

Purpose: show product stage, baseline freshness, open governance gaps, connector health, pending approvals, and in-flight execution state by reading canonical sources.

It must show divergence rather than choose a winner silently.

### `pipe run <command-or-ticket>`

Purpose: dispatch a governed operation through the selected runtime after readiness, ownership, approval, and context-pack checks pass.

The selected runtime is an executor. Pipe policy and the assigned ticket remain authoritative.

## Adapter Contract

Every executor adapter must expose equivalent operations:

| Operation | Required behavior |
|---|---|
| `detect` | Report installed/available version without mutation. |
| `install` | Create only documented local links/configuration; idempotent and conflict-safe. |
| `doctor` | Validate paths, versions, dependencies, and connector state with redaction. |
| `prepare_context` | Build a bounded source-linked Context Pack. |
| `execute` | Run only an approved ticket or planning request. |
| `checkpoint` | Persist recoverable operational state. |
| `handoff` | Write or propose canonical Linear/GitHub/repository handoff. |
| `uninstall` | Remove only items created by that adapter and list what remains. |

Adapter output must follow `architecture/capability-adapter-contract.md` and never treat a capability entry as permission.

## Hermes Boundary

Hermes is the preferred runtime candidate for a persistent Pipe control surface because it can host agent execution, approvals, checkpoints, and UI/API integration. In this architecture it is still an adapter target, not a policy owner.

Hermes may own:

- run lifecycle and executor sessions
- task-local context delivery
- checkpoints and resumability
- tool-call approval prompts
- runtime events and operational logs
- an optional dashboard view of Pipe state

Hermes must read or reference:

- target repository `AGENTS.md`
- `.pipe/mode.json`
- assigned Linear ticket or approved planning request
- ProductBaseline and relevant Context Pack
- Capability Registry entry and adapter contract
- current approvals and stop conditions

Hermes must not become canonical for:

- product strategy or PRD
- customer/market evidence
- architecture decisions
- Linear priority or final ticket status
- GitHub review/merge evidence
- durable knowledge that has not been promoted to the repository
- secrets copied from another computer

If Hermes is unavailable, the same ticket and Context Pack should be executable through Codex or Claude Code without changing governance semantics.

## Agent Atelier Portability Assessment

Atelier is present and registered:

| Surface | Current state | Portability implication |
|---|---|---|
| `.agents/skills/atelier/SKILL.md` | Shared tracked skill and intent router. | Suitable as the runtime-independent source. |
| `.codex/agents/atelier-specialization.md` | Codex role contract. | Already repository-relative. |
| `capabilities/entries/capability.internal.atelier.json` | Lifecycle `pilot`, review `approved`, consumers include Codex/Claude/human. | Can be discovered by `pipe doctor`. |
| `.agents/skills/atelier/install.sh` | Resolves its module directory dynamically and installs Claude links plus pinned dependencies. | Useful idempotent base, but currently Claude-specific and POSIX-shell-specific. |
| `.agents/skills/atelier/adapters/claude-code-agent.md` | Contains a fixed `~/Developer/pipe-venture-builder/...` path, with a portable symlink mentioned second. | Fixed path must be removed or replaced by the installed symlink/module lookup. |
| `dependencies.lock.json` | Pins external repositories to commits. | Enables reproducibility when integrity and compatibility are checked. |

Atelier portability is complete only when:

- no adapter depends on the founder's clone path
- Claude, Codex, and Hermes each have a declared adapter or a documented native fallback
- dependency cache root is configurable and machine-local
- installation is conflict-safe and reversible
- `doctor` verifies every referenced chapter, stack adapter, dependency, schema, and learning destination
- operating mode is read from the target product repository, not from the toolkit repository
- Windows or non-POSIX behavior is explicitly supported or clearly reported as not supported
- a fixture install succeeds from a clone path containing spaces and from a non-`~/Developer` directory

PIP-700 documents these gaps. It does not modify Atelier contract files or its installer.

## Version And Upgrade Rules

A portable release should declare:

- Pipe version
- minimum supported manifest version
- supported schema versions
- executor adapter compatibility
- capability entry versions or review dates
- pinned external dependency refs
- migration notes for breaking changes

Upgrade procedure must:

1. run `doctor` before change
2. show affected product manifests and adapters
3. preserve product-local canonical artifacts
4. back up recoverable local runtime state when format changes
5. apply versioned migrations only through an approved ticket when repository files change
6. run `doctor` after change
7. make rollback instructions explicit

## Security And Privacy Boundary

Bootstrap and doctor must never:

- print or copy tokens, credentials, private keys, or secret environment values
- upload repository content without explicit approval
- inspect customer or production data
- activate billing, paid services, outreach, or production jobs
- bind a dashboard beyond the local machine without a separate security decision
- expose unauthenticated plugin routes or mutation endpoints

Connector setup should use the connector's own interactive authentication flow. Pipe records capability/authentication state, not credential material.

## Portable Readiness Gate

Status is `ready` only when:

- toolkit version resolves independently of clone path
- target repository and mode are valid
- project manifest is compatible when one is required
- at least one executor adapter is available
- required schemas and capability entries parse
- selected capability dependencies are present or a fallback is declared
- connector gaps are visible
- no secret or sensitive access is required for the requested command
- ProductBaseline can be created or read
- the next operation has an assigned ticket or approved planning request

Use `ready_with_warnings` for optional runtime or capability gaps with a valid fallback. Use `blocked` for policy, schema, identity, access, or sensitive-data failures.

## Implementation Sequence

Recommended ticket order:

1. Define `ProductManifest.schema.json` and compatibility policy. **Implemented by PIP-709.**
2. Implement read-only `pipe doctor` with redacted output. **Implemented by PIP-709.**
3. Implement local, idempotent, plan-first ProductManifest bootstrap. **Implemented by PIP-709.**
4. Add Codex/Claude adapter discovery and fixture installs.
5. Remove Atelier's fixed path and add installer tests.
6. Define the Hermes adapter and threat model.
7. Add Hermes runtime registration and checkpoint integration.
8. Add cross-platform support based on actual target-machine demand.

Each item requires a separate approved Linear ticket. No implementation ticket is created by this specification.

## Done Criteria For This Specification

- shared toolkit, product repository, and machine-local state are separated
- manifest contains identifiers but no secrets
- bootstrap and doctor have explicit responsibilities and stop conditions
- Hermes is an executor/runtime rather than a canonical source of truth
- Codex and Claude remain viable fallbacks
- Agent Atelier presence and current portability gaps are explicit
- upgrade, security, and readiness boundaries are reviewable
- implementation work is sequenced without being authorized implicitly
