# Review-Only Reconciliation Planning

PIP-711 adds the deterministic planning layer between read-only external inventory and any future approved apply operation. It compares one canonical `ProductBaseline` with bounded `ExternalSnapshot` values and emits a machine-valid `ReconciliationPlan` plus a concise human rendering.

The planner is a pure function. It does not receive a Linear or GitHub adapter, expose a mutation method, persist credentials, or apply an action.

## Public API

```python
from pipe_venture_builder.reconcile import (
    plan_reconciliation,
    render_reconciliation_plan,
)

plan = plan_reconciliation(
    product_baseline,
    observed_snapshots,
    verification_snapshots=optional_second_reads,
)
review_text = render_reconciliation_plan(plan)
```

`verification_snapshots` are optional fresh reads collected outside the planner. When a relevant target differs from the observed snapshot, the action becomes a blocked `investigate` proposal. The planner never performs that second read itself.

## Matching Hierarchy

The first matching level that returns candidates wins:

1. `explicit_reference`: an action `targetRef` or artifact `externalRef` exactly equals a record `sourceId`, `sourceKey`, or canonical URL.
2. `stable_external_id`: an artifact `sourceRef` exactly equals a record `sourceId` or `sourceKey`.
3. `git_relationship`: for GitHub only, an artifact `sourceRef` exactly equals a branch, head SHA, merge SHA, or tag.
4. `semantic_candidate`: normalized titles are equal. This is always low confidence and always produces `investigate`; it is never auto-confirmed.
5. `manual`: no machine match exists.

The planner uses the baseline's existing `reconciliationPlan` as the authoritative set of intents when it is non-empty. With no declared intents, it conservatively derives:

- a `link` intent for an artifact with a recognizable Linear or GitHub `externalRef`;
- a Linear `create` intent for a non-superseded product requirement, feature, epic, or ticket.

It does not infer GitHub code changes from the existence of source files, and it does not convert governance gaps into tickets automatically.

## Disposition Rules

| Condition | Planned result |
|---|---|
| Declared `create` target already exists | `ignore / already_satisfied` |
| Declared relationship already exists | `ignore / already_satisfied` |
| One exact target for `update` or unlinked `link` | Original action remains `proposed` |
| One title-only candidate | `investigate / proposed / low` |
| Multiple exact targets | `investigate / blocked` with `duplicate_target` |
| Multiple title-only targets | `investigate / blocked` with `ambiguous_match` |
| Snapshot more than 24 hours older than baseline | `investigate / blocked` with `stale_snapshot` |
| Partial or unavailable inventory for a mutation | `investigate / blocked` with `unavailable_source` |
| Relevant verification state differs | `investigate / blocked` with `changed_target` |
| Source artifact has unresolved P0/P1 conflict evidence | `investigate / blocked` with `source_conflict` |

Low-confidence intents always become `investigate`. Deletion, archival, closure, history rewriting, merge, deployment, and semantic auto-confirmation are absent from the action enum.

## Determinism And Idempotency

Plan, action, and blocker IDs are SHA-256-derived from canonical input identity. `generatedAt` is the latest timestamp already present in the baseline or snapshots; it never uses wall-clock time. Repeating the same inputs therefore returns byte-equivalent JSON.

Action idempotency keys use:

```text
<target-system>:<target-container>:<entity-descriptor>:<source-artifact-id>:v1
```

The entity descriptor contains the artifact type, intended action type, and a short hash of the complete intent. This preserves the five-part key shape while preventing distinct intents for the same primary artifact from colliding. Arrays are sorted before output. Source titles are used for in-memory candidate comparison but are not copied into actions or human output. The plan stores only canonical IDs, fixed reasons, fixed expected effects, and hashes of source state.

## Concurrency Guard

An apply layer must re-read the target and provide that result as a verification snapshot before acting. The planner compares the relevant record without its observation timestamp:

- for a matched update/link, a missing or changed source record blocks;
- for a create, a newly appeared match blocks to prevent a duplicate.

The returned `targetFingerprint` is evidence of what was observed, not permission to mutate it. PIP-711 does not implement the apply phase.

## Validation

The focused suite includes schema and human-rendering checks, repeated-input idempotency, already-satisfied behavior, a poison input with write-like methods, and golden cases for explicit, ambiguous, duplicate, stale, and conflicting states. All fixtures are local and sanitized; live credentials are unnecessary.
