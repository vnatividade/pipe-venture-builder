"""Mission Loop B, slice 3: worktree, commit, idempotent PR, checks polling."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.delivery import (
    branch_name,
    checks_status,
    commit_if_needed,
    ensure_worktree,
    existing_pr,
    open_pr,
    pr_body,
    pr_title,
    slugify,
    worktree_path,
)
from tests.mission.helpers import CREATED_AT
from tests.mission.loop_helpers import FakeBinaries, git, loop_mission, make_repo


class BranchAndWorktreeTests(TestCase):
    def test_branch_name_is_claude_prefixed_with_a_short_slug(self) -> None:
        self.assertEqual(slugify("Docs param de contradizer o código!"), "docs-param-de-contradizer-o-codigo")
        self.assertEqual(slugify("   "), "mission")
        self.assertLessEqual(len(slugify("palavra " * 30)), 40)
        with TemporaryDirectory() as directory:
            mission = build_mission(loop_mission(make_repo(Path(directory))), created_at=CREATED_AT)
        self.assertEqual(branch_name(mission), f"claude/{mission['missionId']}-docs-param-de-contradizer-o-codigo")

    def test_ensure_worktree_is_idempotent_and_survives_a_removed_directory(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            home = root / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            expected = home / mission["missionId"] / "worktree"
            self.assertEqual(worktree_path(mission["missionId"], home), expected)

            first = ensure_worktree(mission, home=home)
            self.assertEqual(first, expected)
            self.assertTrue((first / "README.md").is_file())
            self.assertEqual(git(first, "branch", "--show-current").strip(), branch_name(mission))
            self.assertEqual(git(first, "rev-parse", "HEAD"), git(repo, "rev-parse", "main"))

            second = ensure_worktree(mission, home=home)
            self.assertEqual(second, first)
            listed = [line for line in git(repo, "worktree", "list", "--porcelain").splitlines() if line.startswith("worktree ")]
            self.assertEqual(len(listed), 2, "main checkout + one mission worktree")

            (first / "README.md").write_text("work in progress\n", encoding="utf-8")
            git(first, "commit", "-q", "-am", "wip")
            shutil.rmtree(first)
            third = ensure_worktree(mission, home=home)
            self.assertEqual(third, first)
            self.assertEqual((third / "README.md").read_text(encoding="utf-8"), "work in progress\n",
                             "the existing branch is reused, not recreated from baseRef")

    def test_commit_if_needed_commits_only_when_dirty(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            worktree = ensure_worktree(mission, home=root / "home")
            self.assertFalse(commit_if_needed(worktree, f"{mission['missionId']}: nothing"))
            (worktree / "docs" / "guide.md").write_text("pipe idea\n", encoding="utf-8")
            (worktree / "docs" / "new.md").write_text("new\n", encoding="utf-8")
            self.assertTrue(commit_if_needed(worktree, f"{mission['missionId']}: supervisor commit"))
            self.assertEqual(git(worktree, "status", "--porcelain"), "")
            self.assertIn(f"{mission['missionId']}: supervisor commit", git(worktree, "log", "-1", "--format=%s"))
            self.assertFalse(commit_if_needed(worktree, "again"))


class PullRequestTests(TestCase):
    def test_open_pr_pushes_once_and_is_idempotent_per_branch(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            worktree = ensure_worktree(mission, home=root / "home")
            (worktree / "README.md").write_text("pipe idea\n", encoding="utf-8")
            commit_if_needed(worktree, f"{mission['missionId']}: change")
            branch = branch_name(mission)

            self.assertIsNone(existing_pr(fakes.gh_bin, branch, cwd=worktree))
            body = pr_body(mission, criteria=[{"id": "C1", "kind": "check", "satisfied": True}], cost_usd=1.5, cycles=1)
            first = open_pr(worktree, fakes.gh_bin, pr_title(mission), body, branch=branch, base="main")
            self.assertTrue(first.created)
            self.assertEqual(first.url, "https://github.example/owner/repo/pull/1")
            self.assertEqual(first.number, 1)
            self.assertEqual(
                git(repo, "ls-remote", "--heads", "origin", branch).split()[0],
                git(worktree, "rev-parse", "HEAD").strip(),
                "the branch was pushed before the PR was created",
            )

            second = open_pr(worktree, fakes.gh_bin, pr_title(mission), body, branch=branch, base="main")
            self.assertFalse(second.created)
            self.assertEqual(second.url, first.url)
            creates = [call for call in fakes.gh_calls() if call[:2] == ["pr", "create"]]
            self.assertEqual(len(creates), 1)
            self.assertEqual(dict(zip(creates[0][2::2], creates[0][3::2]))["--base"], "main")
            saved_body = (fakes.gh_state / "pr-1-body.md").read_text(encoding="utf-8")
            self.assertEqual(saved_body, body)

    def test_pr_body_follows_the_repository_template_and_cites_mission_and_ticket(self) -> None:
        with TemporaryDirectory() as directory:
            mission = build_mission(loop_mission(make_repo(Path(directory))), created_at=CREATED_AT)
        body = pr_body(
            mission,
            criteria=[{"id": "C1", "kind": "check", "satisfied": True}, {"id": "C3", "kind": "rubric", "satisfied": False}],
            cost_usd=2.345, cycles=2,
        )
        for heading in ("## Linear Ticket", "## Context", "## Included Scope", "## Excluded Scope",
                        "## Development Execution Loop", "## Validation Performed", "## Review Status",
                        "## Risks And Residual Concerns", "## Follow-Ups", "## Context And Token Efficiency",
                        "## Handoff Notes"):
            self.assertIn(heading, body)
        self.assertIn(mission["missionId"], body)
        self.assertIn("PIP-902", body)
        self.assertIn("- C1 (check): satisfied", body)
        self.assertIn("- C3 (rubric): pending", body)
        self.assertIn("US$ 2.35", body)
        self.assertIn(mission["title"], pr_title(mission))
        self.assertIn(mission["missionId"], pr_title(mission))
        self.assertNotIn(mission["intent"], body, "the founder's intent text stays out of the PR body")

    def test_checks_status_maps_buckets(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            root = Path(directory)
            fakes.gh_checks([["pending", "pass"], ["pass", "skipping"], ["fail", "pass"], [], ["cancel"]])
            self.assertEqual(checks_status(fakes.gh_bin, "claude/x", cwd=root), "pending")
            self.assertEqual(checks_status(fakes.gh_bin, "claude/x", cwd=root), "passed")
            self.assertEqual(checks_status(fakes.gh_bin, "claude/x", cwd=root), "failed")
            self.assertEqual(checks_status(fakes.gh_bin, "claude/x", cwd=root), "none")
            self.assertEqual(checks_status(fakes.gh_bin, "claude/x", cwd=root), "failed")
            calls = [call for call in fakes.gh_calls() if call[:2] == ["pr", "checks"]]
            self.assertEqual(len(calls), 5)
            self.assertIn("--json", calls[0])
            self.assertEqual(json.loads(json.dumps(calls[0]))[2], "claude/x")
