from __future__ import annotations

import json
from typing import Any, Mapping
from unittest import TestCase

from pipe_venture_builder.adapters import (
    FixtureInventorySource,
    LinearConnectorSource,
    LinearInventoryAdapter,
    SourcePayload,
    SourceUnauthorized,
)

from tests.adapters.helpers import CAPTURED_AT, FIXTURE_ROOT, assert_valid_snapshot


class _StaticLinearSource:
    source_system = "linear"
    container_type = "project"

    def __init__(
        self, payload: SourcePayload | None = None, error: Exception | None = None
    ):
        self._payload = payload
        self._error = error

    def read(self, _container_id: str, *, limit: int, max_pages: int) -> SourcePayload:
        del limit, max_pages
        if self._error:
            raise self._error
        assert self._payload is not None
        return self._payload


class LinearInventoryTests(TestCase):
    def test_fixture_pages_normalize_to_schema_valid_stable_records(self) -> None:
        source = FixtureInventorySource(
            FIXTURE_ROOT / "linear-pages.json",
            source_system="linear",
            container_type="project",
        )
        adapter = LinearInventoryAdapter(source)

        first = adapter.capture("linear-project-001", captured_at=CAPTURED_AT)
        second = adapter.capture("linear-project-001", captured_at=CAPTURED_AT)

        self.assertEqual(first, second)
        self.assertEqual(first["status"], "complete")
        self.assertEqual(first["pagination"]["returnedCount"], 2)
        self.assertEqual(first["pagination"]["pagesRead"], 2)
        self.assertEqual(
            [record["sourceKey"] for record in first["records"]],
            ["EX-1", "EX-2", "example-project"],
        )
        self.assertTrue(
            all(record["observedAt"] == CAPTURED_AT for record in first["records"])
        )
        assert_valid_snapshot(self, first)

    def test_successful_empty_read_is_distinct_from_unauthorized(self) -> None:
        container = {
            "id": "project-empty",
            "slugId": "empty-project",
            "name": "Empty Project",
            "url": "https://linear.app/example/project/empty",
            "state": "backlog",
            "createdAt": CAPTURED_AT,
            "updatedAt": CAPTURED_AT,
        }
        empty = LinearInventoryAdapter(
            _StaticLinearSource(SourcePayload(container=container, items=()))
        ).capture("project-empty", captured_at=CAPTURED_AT)
        unauthorized = LinearInventoryAdapter(
            _StaticLinearSource(error=SourceUnauthorized())
        ).capture("project-empty", captured_at=CAPTURED_AT)

        self.assertEqual(empty["status"], "empty")
        self.assertEqual(unauthorized["status"], "unauthorized")
        self.assertEqual(empty["pagination"]["pagesRead"], 1)
        self.assertEqual(unauthorized["pagination"]["pagesRead"], 0)
        assert_valid_snapshot(self, empty)
        assert_valid_snapshot(self, unauthorized)

    def test_fixture_pagination_limit_is_explicitly_partial(self) -> None:
        adapter = LinearInventoryAdapter(
            FixtureInventorySource(
                FIXTURE_ROOT / "linear-pages.json",
                source_system="linear",
                container_type="project",
            )
        )

        snapshot = adapter.capture(
            "linear-project-001",
            captured_at=CAPTURED_AT,
            max_pages=1,
        )

        self.assertEqual(snapshot["status"], "partial")
        self.assertTrue(snapshot["pagination"]["truncated"])
        self.assertEqual(snapshot["diagnostics"][0]["code"], "inventory_truncated")
        assert_valid_snapshot(self, snapshot)

    def test_linear_connector_invoker_can_only_receive_fixed_read_tools(self) -> None:
        calls: list[tuple[str, Mapping[str, Any]]] = []

        def invoke(tool_name: str, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
            calls.append((tool_name, arguments))
            if tool_name == "linear_get_project":
                return {
                    "id": "project-0001",
                    "slugId": "example-project",
                    "name": "Example Product",
                    "url": "https://linear.app/example/project/example",
                    "state": "started",
                    "createdAt": CAPTURED_AT,
                    "updatedAt": CAPTURED_AT,
                }
            return {"issues": [], "hasMore": False}

        source = LinearConnectorSource(invoke)
        snapshot = LinearInventoryAdapter(source).capture(
            "linear-project-001", captured_at=CAPTURED_AT
        )

        self.assertEqual(
            [name for name, _arguments in calls],
            ["linear_get_project", "linear_list_issues"],
        )
        self.assertTrue(all("token" not in arguments for _name, arguments in calls))
        self.assertFalse(
            {"create", "update", "delete", "save", "mutate"}.intersection(dir(source))
        )
        self.assertEqual(snapshot["status"], "empty")
        assert_valid_snapshot(self, snapshot)

    def test_unsafe_payload_and_error_details_never_leak(self) -> None:
        sentinel = "ghp_" + ("S" * 24)
        container = {
            "id": "project-unsafe",
            "slugId": "unsafe-project",
            "name": "Unsafe Project",
            "url": "https://linear.app/example/project/unsafe",
            "state": "started",
            "createdAt": CAPTURED_AT,
            "updatedAt": CAPTURED_AT,
        }
        source = _StaticLinearSource(
            SourcePayload(
                container=container,
                items=({"id": "issue-unsafe", "authorization": sentinel},),
            )
        )

        snapshot = LinearInventoryAdapter(source).capture(
            "project-unsafe", captured_at=CAPTURED_AT
        )
        rendered = json.dumps(snapshot)

        self.assertEqual(snapshot["status"], "blocked")
        self.assertEqual(snapshot["diagnostics"][0]["code"], "unsafe_source_payload")
        self.assertNotIn(sentinel, rendered)
        self.assertNotIn("authorization", rendered.lower())
        assert_valid_snapshot(self, snapshot)

    def test_query_bearing_source_url_is_blocked(self) -> None:
        source = _StaticLinearSource(
            SourcePayload(
                container={
                    "id": "project-query",
                    "slugId": "query-project",
                    "name": "Query Project",
                    "url": "https://linear.app/example/project/query?session=opaque",
                    "state": "started",
                    "createdAt": CAPTURED_AT,
                    "updatedAt": CAPTURED_AT,
                },
                items=(),
            )
        )

        snapshot = LinearInventoryAdapter(source).capture(
            "project-query", captured_at=CAPTURED_AT
        )

        self.assertEqual(snapshot["status"], "blocked")
        self.assertIsNone(snapshot["sourceContainer"]["url"])
        self.assertNotIn("session", json.dumps(snapshot))
        assert_valid_snapshot(self, snapshot)
