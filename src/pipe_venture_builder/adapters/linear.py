"""Read-only Linear inventory source and ExternalSnapshot normalizer."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .contracts import (
    AdapterReadError,
    DEFAULT_MAX_PAGES,
    DEFAULT_RECORD_LIMIT,
    SourceContractFailure,
    SourcePayload,
    SourceRateLimited,
    SourceUnauthorized,
    SourceUnavailable,
    UnsafeSourcePayload,
)
from .safety import payload_is_safe, safe_identifier, safe_text
from .snapshot import capture_snapshot, make_record

ConnectorInvoker = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


class LinearConnectorSource:
    """Use a host-provided authenticated Linear connector through fixed read calls.

    The host owns authentication. This class never accepts a token, header, or
    arbitrary tool name and never exposes a mutation method.
    """

    source_system = "linear"
    container_type = "project"
    # Verbos internos do adapter, não nomes de tool de nenhum servidor. Os nomes
    # anteriores (`linear_get_project`/`linear_list_issues`) não existem em lugar
    # nenhum: o MCP oficial expõe `get_project`/`list_issues` e escreve com
    # `save_issue`. Um invoker sobre MCP traduz estes verbos para os nomes de lá;
    # `linear_graphql.LinearGraphQLInvoker` traduz para queries versionadas.
    _PROJECT_TOOL = "project.read"
    _ISSUES_TOOL = "issues.list"

    def __init__(self, invoke: ConnectorInvoker) -> None:
        self._invoke = invoke

    def read(
        self,
        container_id: str,
        *,
        limit: int,
        max_pages: int,
    ) -> SourcePayload:
        project_result = self._safe_invoke(
            self._PROJECT_TOOL,
            {"query": container_id},
        )
        project = project_result.get("project", project_result)
        if not isinstance(project, Mapping):
            raise SourceContractFailure()

        issues: list[Mapping[str, Any]] = []
        cursor: str | None = None
        pages_read = 0
        truncated = False
        while pages_read < max_pages and len(issues) < limit:
            arguments: dict[str, Any] = {
                "project": container_id,
                "limit": min(250, limit - len(issues)),
            }
            if cursor is not None:
                arguments["cursor"] = cursor
            page = self._safe_invoke(self._ISSUES_TOOL, arguments)
            raw_items = _page_items(page)
            pages_read += 1
            for item in raw_items:
                if len(issues) >= limit:
                    truncated = True
                    break
                if not isinstance(item, Mapping):
                    raise SourceContractFailure()
                issues.append(item)
            cursor, has_more = _page_cursor(page)
            if not has_more:
                break
            if cursor is None:
                raise SourceContractFailure()
        if cursor is not None and pages_read >= max_pages:
            truncated = True
        if len(issues) >= limit and cursor is not None:
            truncated = True
        return SourcePayload(
            container=project,
            items=tuple(issues),
            pages_read=pages_read,
            truncated=truncated,
        )

    def _safe_invoke(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        try:
            result = self._invoke(tool_name, arguments)
        except AdapterReadError:
            raise
        except (FileNotFoundError, ConnectionError, TimeoutError) as exc:
            raise SourceUnavailable() from exc
        except PermissionError as exc:
            raise SourceUnauthorized() from exc
        except Exception as exc:
            raise SourceContractFailure() from exc
        if not isinstance(result, Mapping):
            raise SourceContractFailure()
        if not payload_is_safe(result):
            raise UnsafeSourcePayload()
        error_code = _error_code(result)
        if error_code in {"unauthorized", "authentication_required", "forbidden"}:
            raise SourceUnauthorized()
        if error_code in {"rate_limited", "rate_limit", "too_many_requests"}:
            raise SourceRateLimited()
        if error_code in {"unavailable", "connection_failed", "not_found"}:
            raise SourceUnavailable()
        if error_code is not None:
            raise SourceContractFailure()
        return result


class LinearInventoryAdapter:
    """Normalize a bounded Linear project inventory; no mutation surface exists."""

    def __init__(self, source: Any) -> None:
        if source.source_system != "linear" or source.container_type != "project":
            raise ValueError("Linear adapter requires a Linear project source")
        self._source = source

    def capture(
        self,
        project_id: str,
        *,
        captured_at: str | None = None,
        limit: int = DEFAULT_RECORD_LIMIT,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> dict[str, Any]:
        return capture_snapshot(
            self._source,
            project_id,
            _normalize_linear,
            captured_at=captured_at,
            limit=limit,
            max_pages=max_pages,
        )


def _normalize_linear(
    project: Mapping[str, Any],
    issues: tuple[Mapping[str, Any], ...],
    observed_at: str,
) -> list[dict[str, Any]]:
    project_id = safe_identifier(project["id"])
    project_key = project.get("slugId") or project.get("key") or project_id
    records = [
        make_record(
            source_system="linear",
            source_id=project_id,
            source_key=project_key,
            entity_type="project",
            observed_at=observed_at,
            title=project.get("name"),
            state=_state(project.get("state")),
            url=project.get("url"),
            source_created_at=project.get("createdAt"),
            source_updated_at=project.get("updatedAt"),
        )
    ]
    for issue in issues:
        issue_id = safe_identifier(issue["id"])
        relationships: list[dict[str, str]] = [
            {"type": "belongs_to", "targetSourceId": project_id}
        ]
        parent = issue.get("parent")
        if isinstance(parent, Mapping) and parent.get("id"):
            relationships.append(
                {"type": "child_of", "targetSourceId": str(parent["id"])}
            )
        relations = issue.get("relations")
        if isinstance(relations, Mapping):
            for field, relationship_type in (
                ("blocks", "blocks"),
                ("blockedBy", "blocked_by"),
            ):
                for target in _mapping_list(relations.get(field)):
                    if target.get("id"):
                        relationships.append(
                            {
                                "type": relationship_type,
                                "targetSourceId": str(target["id"]),
                            }
                        )
        priority = issue.get("priority")
        if isinstance(priority, Mapping):
            priority = priority.get("value")
        priority = priority if isinstance(priority, int) else None
        records.append(
            make_record(
                source_system="linear",
                source_id=issue_id,
                source_key=issue.get("identifier") or issue_id,
                entity_type="issue",
                observed_at=observed_at,
                title=issue.get("title"),
                state=_state(issue.get("state")),
                url=issue.get("url"),
                source_created_at=issue.get("createdAt"),
                source_updated_at=issue.get("updatedAt"),
                source_closed_at=issue.get("completedAt") or issue.get("canceledAt"),
                relationships=relationships,
                attributes={
                    "number": _linear_number(issue.get("identifier")),
                    "priority": priority,
                    "labels": _labels(issue.get("labels")),
                },
            )
        )
    return records


def _page_items(page: Mapping[str, Any]) -> list[Any]:
    for key in ("issues", "items", "nodes"):
        value = page.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, Mapping) and isinstance(value.get("nodes"), list):
            return value["nodes"]
    data = page.get("data")
    if isinstance(data, list):
        return data
    return []


def _page_cursor(page: Mapping[str, Any]) -> tuple[str | None, bool]:
    page_info = page.get("pageInfo")
    if isinstance(page_info, Mapping):
        cursor = page_info.get("endCursor") or page_info.get("nextCursor")
        has_more = bool(page_info.get("hasNextPage") or page_info.get("hasMore"))
    else:
        cursor = page.get("nextCursor")
        has_more = bool(page.get("hasMore") or cursor)
    if cursor is not None:
        cursor = safe_identifier(cursor)
    return cursor, has_more


def _error_code(result: Mapping[str, Any]) -> str | None:
    error = result.get("error")
    if isinstance(error, Mapping):
        code = error.get("code") or error.get("type") or error.get("status")
    elif isinstance(error, str):
        code = error
    else:
        code = result.get("errorCode")
    if code is None and result.get("ok") is False:
        return "unknown"
    normalized = safe_text(code, limit=100) if code is not None else None
    return (
        normalized.lower() if normalized else ("unknown" if error is not None else None)
    )


def _state(value: Any) -> str | None:
    if isinstance(value, Mapping):
        value = value.get("name") or value.get("type")
    return safe_text(value, limit=100)


def _labels(value: Any) -> list[str]:
    if isinstance(value, Mapping):
        value = value.get("nodes") or value.get("items") or []
    if not isinstance(value, list):
        return []
    labels = []
    for item in value:
        label = item.get("name") if isinstance(item, Mapping) else item
        if normalized := safe_text(label, limit=100):
            labels.append(normalized)
    return labels


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        value = value.get("nodes") or value.get("items") or []
    return (
        [item for item in value if isinstance(item, Mapping)]
        if isinstance(value, list)
        else []
    )


def _linear_number(identifier: Any) -> int | None:
    if not isinstance(identifier, str) or "-" not in identifier:
        return None
    suffix = identifier.rsplit("-", 1)[-1]
    return int(suffix) if suffix.isdigit() and int(suffix) > 0 else None
