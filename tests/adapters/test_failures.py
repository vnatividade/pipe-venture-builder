from __future__ import annotations

from unittest import TestCase

from pipe_venture_builder.adapters import (
    LinearInventoryAdapter,
    SourceContractFailure,
    SourceRateLimited,
    SourceUnavailable,
)

from tests.adapters.helpers import CAPTURED_AT, assert_valid_snapshot


class _FailureSource:
    source_system = "linear"
    container_type = "project"

    def __init__(self, error: Exception) -> None:
        self._error = error

    def read(self, _container_id: str, *, limit: int, max_pages: int):
        del limit, max_pages
        raise self._error


class FailureStateTests(TestCase):
    def test_every_non_authorization_failure_has_an_explicit_status(self) -> None:
        cases = (
            (SourceUnavailable(), "unavailable", "source_unavailable"),
            (SourceRateLimited(), "rate_limited", "source_rate_limited"),
            (SourceContractFailure(), "failed", "source_contract_failed"),
        )
        for error, status, code in cases:
            with self.subTest(status=status):
                snapshot = LinearInventoryAdapter(_FailureSource(error)).capture(
                    "project-example",
                    captured_at=CAPTURED_AT,
                )
                self.assertEqual(snapshot["status"], status)
                self.assertEqual(snapshot["diagnostics"][0]["code"], code)
                self.assertEqual(snapshot["records"], [])
                assert_valid_snapshot(self, snapshot)

    def test_failure_snapshot_identity_includes_capture_time(self) -> None:
        adapter = LinearInventoryAdapter(_FailureSource(SourceUnavailable()))

        first = adapter.capture("project-example", captured_at=CAPTURED_AT)
        second = adapter.capture("project-example", captured_at="2026-07-21T12:00:01Z")

        self.assertNotEqual(first["snapshotId"], second["snapshotId"])
