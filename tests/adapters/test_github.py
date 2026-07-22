from __future__ import annotations

import json
from collections.abc import Sequence
from unittest import TestCase

from pipe_venture_builder.adapters import (
    CommandResult,
    FixtureInventorySource,
    GitHubGhCliSource,
    GitHubInventoryAdapter,
)

from tests.adapters.helpers import CAPTURED_AT, FIXTURE_ROOT, assert_valid_snapshot


class GitHubInventoryTests(TestCase):
    def test_fixture_pages_normalize_reviews_checks_and_releases(self) -> None:
        adapter = GitHubInventoryAdapter(
            FixtureInventorySource(
                FIXTURE_ROOT / "github-pages.json",
                source_system="github",
                container_type="repository",
            )
        )

        snapshot = adapter.capture("example/product", captured_at=CAPTURED_AT)

        self.assertEqual(snapshot["status"], "complete")
        self.assertEqual(snapshot["pagination"]["returnedCount"], 3)
        pull_request = next(
            record
            for record in snapshot["records"]
            if record["entityType"] == "pull_request"
        )
        self.assertEqual(pull_request["attributes"]["reviewDecision"], "APPROVED")
        self.assertEqual(
            pull_request["attributes"]["checkSummary"],
            {
                "total": 2,
                "successful": 1,
                "failed": 0,
                "pending": 1,
                "skipped": 0,
            },
        )
        self.assertEqual(
            {record["entityType"] for record in snapshot["records"]},
            {"repository", "issue", "pull_request", "release"},
        )
        assert_valid_snapshot(self, snapshot)

    def test_gh_cli_source_uses_only_fixed_read_commands(self) -> None:
        commands: list[tuple[str, ...]] = []

        def runner(command: Sequence[str], _timeout: float) -> CommandResult:
            command = tuple(command)
            commands.append(command)
            if command[1:3] == ("repo", "view"):
                payload: object = {
                    "id": "R_example_001",
                    "nameWithOwner": "example/product",
                    "url": "https://github.com/example/product",
                    "createdAt": CAPTURED_AT,
                    "updatedAt": CAPTURED_AT,
                    "defaultBranchRef": {"name": "main"},
                }
            else:
                payload = []
            return CommandResult(0, json.dumps(payload))

        source = GitHubGhCliSource(runner)
        snapshot = GitHubInventoryAdapter(source).capture(
            "example/product", captured_at=CAPTURED_AT
        )

        self.assertEqual(len(commands), 4)
        self.assertTrue(all(command[0] == "gh" for command in commands))
        command_tokens = {token for command in commands for token in command}
        for forbidden in ("create", "edit", "merge", "comment", "close", "delete"):
            self.assertNotIn(forbidden, command_tokens)
        self.assertFalse(
            {"create", "update", "delete", "save", "mutate"}.intersection(dir(source))
        )
        self.assertEqual(snapshot["status"], "empty")
        assert_valid_snapshot(self, snapshot)

    def test_gh_cli_unauthorized_and_rate_limited_are_distinct_and_redacted(
        self,
    ) -> None:
        sentinel = "ghp_" + ("R" * 24)

        def unauthorized(_command: Sequence[str], _timeout: float) -> CommandResult:
            return CommandResult(1, "", f"not logged in; Authorization: {sentinel}")

        def rate_limited(_command: Sequence[str], _timeout: float) -> CommandResult:
            return CommandResult(1, "", f"HTTP 429 rate limit; request {sentinel}")

        unauthorized_snapshot = GitHubInventoryAdapter(
            GitHubGhCliSource(unauthorized)
        ).capture("example/product", captured_at=CAPTURED_AT)
        rate_snapshot = GitHubInventoryAdapter(GitHubGhCliSource(rate_limited)).capture(
            "example/product", captured_at=CAPTURED_AT
        )

        self.assertEqual(unauthorized_snapshot["status"], "unauthorized")
        self.assertEqual(rate_snapshot["status"], "rate_limited")
        self.assertNotIn(sentinel, json.dumps(unauthorized_snapshot))
        self.assertNotIn(sentinel, json.dumps(rate_snapshot))
        assert_valid_snapshot(self, unauthorized_snapshot)
        assert_valid_snapshot(self, rate_snapshot)

    def test_secret_shaped_success_payload_is_blocked_without_leakage(self) -> None:
        sentinel = "ghp_" + ("T" * 24)

        def runner(_command: Sequence[str], _timeout: float) -> CommandResult:
            return CommandResult(
                0, json.dumps({"headers": {"authorization": sentinel}})
            )

        snapshot = GitHubInventoryAdapter(GitHubGhCliSource(runner)).capture(
            "example/product", captured_at=CAPTURED_AT
        )

        self.assertEqual(snapshot["status"], "blocked")
        self.assertNotIn(sentinel, json.dumps(snapshot))
        assert_valid_snapshot(self, snapshot)

    def test_non_hex_commit_identifier_fails_closed(self) -> None:
        responses = {
            ("repo", "view"): {
                "id": "R_example_001",
                "nameWithOwner": "example/product",
                "url": "https://github.com/example/product",
                "createdAt": CAPTURED_AT,
                "updatedAt": CAPTURED_AT,
                "defaultBranchRef": {"name": "main"},
            },
            ("issue", "list"): [],
            ("pr", "list"): [
                {
                    "id": "PR_example_invalid",
                    "number": 99,
                    "title": "Invalid commit fixture",
                    "url": "https://github.com/example/product/pull/99",
                    "state": "OPEN",
                    "headRefOid": "not-a-git-sha",
                    "createdAt": CAPTURED_AT,
                    "updatedAt": CAPTURED_AT,
                }
            ],
            ("release", "list"): [],
        }

        def runner(command: Sequence[str], _timeout: float) -> CommandResult:
            return CommandResult(0, json.dumps(responses[tuple(command[1:3])]))

        snapshot = GitHubInventoryAdapter(GitHubGhCliSource(runner)).capture(
            "example/product", captured_at=CAPTURED_AT
        )

        self.assertEqual(snapshot["status"], "failed")
        assert_valid_snapshot(self, snapshot)

    def test_total_limit_round_robins_across_github_entity_types(self) -> None:
        repository = {
            "id": "R_example_001",
            "nameWithOwner": "example/product",
            "url": "https://github.com/example/product",
            "createdAt": CAPTURED_AT,
            "updatedAt": CAPTURED_AT,
            "defaultBranchRef": {"name": "main"},
        }
        issues = [
            {
                "id": f"I_example_{number}",
                "number": number,
                "title": f"Issue {number}",
                "url": f"https://github.com/example/product/issues/{number}",
                "state": "OPEN",
                "createdAt": CAPTURED_AT,
                "updatedAt": CAPTURED_AT,
            }
            for number in (1, 2, 3)
        ]
        pulls = [
            {
                "id": "PR_example_001",
                "number": 10,
                "title": "Pull request",
                "url": "https://github.com/example/product/pull/10",
                "state": "OPEN",
                "createdAt": CAPTURED_AT,
                "updatedAt": CAPTURED_AT,
            }
        ]
        responses = {
            ("repo", "view"): repository,
            ("issue", "list"): issues,
            ("pr", "list"): pulls,
            ("release", "list"): [],
        }

        def runner(command: Sequence[str], _timeout: float) -> CommandResult:
            return CommandResult(0, json.dumps(responses[tuple(command[1:3])]))

        snapshot = GitHubInventoryAdapter(GitHubGhCliSource(runner)).capture(
            "example/product", captured_at=CAPTURED_AT, limit=2
        )

        self.assertEqual(snapshot["status"], "partial")
        self.assertEqual(
            {record["entityType"] for record in snapshot["records"]},
            {"repository", "issue", "pull_request"},
        )
        assert_valid_snapshot(self, snapshot)
