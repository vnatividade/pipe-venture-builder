"""Read-only GitHub CLI source and ExternalSnapshot normalizer."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .contracts import (
    DEFAULT_MAX_PAGES,
    DEFAULT_RECORD_LIMIT,
    SourceContractFailure,
    SourcePayload,
    SourceRateLimited,
    SourceUnauthorized,
    SourceUnavailable,
    UnsafeSourcePayload,
)
from .safety import (
    MAX_SOURCE_PAYLOAD_BYTES,
    payload_is_safe,
    safe_identifier,
    safe_text,
)
from .snapshot import capture_snapshot, make_record


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str = ""


CommandRunner = Callable[[Sequence[str], float], CommandResult]


class GitHubGhCliSource:
    """Read GitHub inventory with fixed non-mutating `gh` commands."""

    source_system = "github"
    container_type = "repository"

    def __init__(
        self,
        runner: CommandRunner | None = None,
        *,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._runner = runner or _subprocess_runner
        self._timeout_seconds = timeout_seconds

    def read(
        self,
        container_id: str,
        *,
        limit: int,
        max_pages: int,
    ) -> SourcePayload:
        del max_pages  # gh performs bounded list reads; no cursor is persisted.
        repository = self._run_json(
            (
                "gh",
                "repo",
                "view",
                container_id,
                "--json",
                "id,nameWithOwner,url,createdAt,updatedAt,defaultBranchRef",
            )
        )
        issue_items = self._run_json(
            (
                "gh",
                "issue",
                "list",
                "--repo",
                container_id,
                "--state",
                "all",
                "--limit",
                str(limit),
                "--json",
                "id,number,title,url,state,createdAt,updatedAt,closedAt,labels",
            )
        )
        pull_items = self._run_json(
            (
                "gh",
                "pr",
                "list",
                "--repo",
                container_id,
                "--state",
                "all",
                "--limit",
                str(limit),
                "--json",
                "id,number,title,url,state,isDraft,headRefName,baseRefName,headRefOid,createdAt,updatedAt,closedAt,mergedAt,mergeCommit,reviewDecision,statusCheckRollup,labels",
            )
        )
        release_items = self._run_json(
            (
                "gh",
                "release",
                "list",
                "--repo",
                container_id,
                "--limit",
                str(limit),
                "--json",
                "tagName,name,isDraft,isPrerelease,publishedAt,createdAt",
            )
        )
        if not isinstance(repository, Mapping):
            raise SourceContractFailure()
        collections = (issue_items, pull_items, release_items)
        if any(not isinstance(collection, list) for collection in collections):
            raise SourceContractFailure()

        typed_collections = tuple(
            (entity_type, collection)
            for entity_type, collection in zip(
                ("issue", "pull_request", "release"), collections, strict=True
            )
        )
        combined: list[Mapping[str, Any]] = []
        max_collection_size = max(
            (len(collection) for collection in collections), default=0
        )
        for index in range(max_collection_size):
            for entity_type, collection in typed_collections:
                if index >= len(collection):
                    continue
                item = collection[index]
                if not isinstance(item, Mapping):
                    raise SourceContractFailure()
                enriched = dict(item)
                enriched["_pipeEntityType"] = entity_type
                combined.append(enriched)
                if len(combined) >= limit:
                    break
            if len(combined) >= limit:
                break
        truncated = any(len(collection) >= limit for collection in collections)
        if sum(len(collection) for collection in collections) > len(combined):
            truncated = True
        return SourcePayload(
            container=repository,
            items=tuple(combined),
            pages_read=1,
            truncated=truncated,
        )

    def _run_json(self, command: Sequence[str]) -> Any:
        try:
            result = self._runner(command, self._timeout_seconds)
        except (FileNotFoundError, TimeoutError, subprocess.TimeoutExpired) as exc:
            raise SourceUnavailable() from exc
        except PermissionError as exc:
            raise SourceUnauthorized() from exc
        except Exception as exc:
            raise SourceContractFailure() from exc
        if not isinstance(result, CommandResult):
            raise SourceContractFailure()
        if result.returncode != 0:
            diagnostic = result.stderr.lower()
            if any(term in diagnostic for term in ("rate limit", "429")):
                raise SourceRateLimited()
            if any(
                term in diagnostic
                for term in ("not logged", "authentication", "unauthorized", "401")
            ):
                raise SourceUnauthorized()
            raise SourceUnavailable()
        if len(result.stdout.encode("utf-8")) > MAX_SOURCE_PAYLOAD_BYTES:
            raise UnsafeSourcePayload()
        try:
            payload = json.loads(result.stdout)
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise SourceContractFailure() from exc
        if not payload_is_safe(payload):
            raise UnsafeSourcePayload()
        return payload


class GitHubInventoryAdapter:
    """Normalize a bounded GitHub repository inventory without mutation APIs."""

    def __init__(self, source: Any) -> None:
        if source.source_system != "github" or source.container_type != "repository":
            raise ValueError("GitHub adapter requires a GitHub repository source")
        self._source = source

    def capture(
        self,
        repository: str,
        *,
        captured_at: str | None = None,
        limit: int = DEFAULT_RECORD_LIMIT,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> dict[str, Any]:
        return capture_snapshot(
            self._source,
            repository,
            _normalize_github,
            captured_at=captured_at,
            limit=limit,
            max_pages=max_pages,
        )


def _normalize_github(
    repository: Mapping[str, Any],
    items: tuple[Mapping[str, Any], ...],
    observed_at: str,
) -> list[dict[str, Any]]:
    repository_key = safe_identifier(repository["nameWithOwner"])
    repository_id = safe_identifier(repository.get("id") or repository_key)
    default_branch = repository.get("defaultBranchRef")
    if isinstance(default_branch, Mapping):
        default_branch = default_branch.get("name")
    records = [
        make_record(
            source_system="github",
            source_id=repository_id,
            source_key=repository_key,
            entity_type="repository",
            observed_at=observed_at,
            title=repository_key,
            state="active",
            url=repository.get("url"),
            source_created_at=repository.get("createdAt"),
            source_updated_at=repository.get("updatedAt"),
            attributes={"defaultBranch": default_branch},
        )
    ]
    for item in items:
        entity_type = item.get("_pipeEntityType")
        if entity_type == "issue":
            records.append(_github_issue(item, repository_id, observed_at))
        elif entity_type == "pull_request":
            records.append(_github_pull_request(item, repository_id, observed_at))
        elif entity_type == "release":
            records.append(_github_release(item, repository_id, observed_at))
        else:
            raise SourceContractFailure()
    return records


def _github_issue(
    item: Mapping[str, Any], repository_id: str, observed_at: str
) -> dict[str, Any]:
    source_id = item["id"]
    number = item.get("number")
    return make_record(
        source_system="github",
        source_id=source_id,
        source_key=str(number or source_id),
        entity_type="issue",
        observed_at=observed_at,
        title=item.get("title"),
        state=item.get("state"),
        url=item.get("url"),
        source_created_at=item.get("createdAt"),
        source_updated_at=item.get("updatedAt"),
        source_closed_at=item.get("closedAt"),
        relationships=[{"type": "belongs_to", "targetSourceId": repository_id}],
        attributes={
            "number": number if isinstance(number, int) else None,
            "labels": _labels(item.get("labels")),
        },
    )


def _github_pull_request(
    item: Mapping[str, Any], repository_id: str, observed_at: str
) -> dict[str, Any]:
    source_id = item["id"]
    number = item.get("number")
    merge_commit = item.get("mergeCommit")
    merge_sha = merge_commit.get("oid") if isinstance(merge_commit, Mapping) else None
    merged_at = item.get("mergedAt")
    return make_record(
        source_system="github",
        source_id=source_id,
        source_key=str(number or source_id),
        entity_type="pull_request",
        observed_at=observed_at,
        title=item.get("title"),
        state=item.get("state"),
        url=item.get("url"),
        source_created_at=item.get("createdAt"),
        source_updated_at=item.get("updatedAt"),
        source_closed_at=merged_at or item.get("closedAt"),
        relationships=[{"type": "belongs_to", "targetSourceId": repository_id}],
        attributes={
            "number": number if isinstance(number, int) else None,
            "labels": _labels(item.get("labels")),
            "draft": item.get("isDraft")
            if isinstance(item.get("isDraft"), bool)
            else None,
            "merged": merged_at is not None,
            "reviewDecision": item.get("reviewDecision"),
            "baseBranch": item.get("baseRefName"),
            "headBranch": item.get("headRefName"),
            "headSha": item.get("headRefOid"),
            "mergeCommitSha": merge_sha,
            "checkSummary": _check_summary(item.get("statusCheckRollup")),
        },
    )


def _github_release(
    item: Mapping[str, Any], repository_id: str, observed_at: str
) -> dict[str, Any]:
    tag = safe_identifier(item["tagName"])
    draft = item.get("isDraft") if isinstance(item.get("isDraft"), bool) else False
    prerelease = (
        item.get("isPrerelease")
        if isinstance(item.get("isPrerelease"), bool)
        else False
    )
    return make_record(
        source_system="github",
        source_id=f"release:{tag}",
        source_key=tag,
        entity_type="release",
        observed_at=observed_at,
        title=item.get("name") or tag,
        state="draft" if draft else "published",
        url=item.get("url"),
        source_created_at=item.get("createdAt"),
        source_updated_at=item.get("publishedAt"),
        relationships=[{"type": "belongs_to", "targetSourceId": repository_id}],
        attributes={
            "draft": draft,
            "tag": tag,
            "prerelease": prerelease,
        },
    )


def _labels(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    labels = []
    for item in value:
        label = item.get("name") if isinstance(item, Mapping) else item
        if normalized := safe_text(label, limit=100):
            labels.append(normalized)
    return labels


def _check_summary(value: Any) -> dict[str, int] | None:
    if not isinstance(value, list):
        return None
    summary = {
        "total": len(value),
        "successful": 0,
        "failed": 0,
        "pending": 0,
        "skipped": 0,
    }
    for check in value:
        if not isinstance(check, Mapping):
            summary["pending"] += 1
            continue
        status = safe_text(
            check.get("conclusion") or check.get("state") or check.get("status"),
            limit=100,
        )
        normalized = status.lower() if status else "pending"
        if normalized in {"success", "successful", "neutral"}:
            summary["successful"] += 1
        elif normalized in {
            "failure",
            "failed",
            "cancelled",
            "timed_out",
            "action_required",
            "startup_failure",
            "stale",
        }:
            summary["failed"] += 1
        elif normalized == "skipped":
            summary["skipped"] += 1
        else:
            summary["pending"] += 1
    return summary


def _subprocess_runner(command: Sequence[str], timeout: float) -> CommandResult:
    completed = subprocess.run(
        tuple(command),
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return CommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
