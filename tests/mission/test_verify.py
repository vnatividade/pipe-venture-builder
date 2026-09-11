"""Mission Loop B, slice 2: deterministic verification (write set, checks, artifacts)."""

from __future__ import annotations

import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.delivery import GIT_CONTEXT_ENV
from pipe_venture_builder.mission.verify import (
    CheckResult,
    changed_files,
    check_artifact,
    diff_fingerprint,
    diff_text,
    outside_write_set,
    run_check,
    verify_criteria,
    within_write_set,
)
from tests.mission.helpers import CREATED_AT
from tests.mission.loop_helpers import GOOD_FILES, git, loop_mission, make_repo


class ChangedFilesTests(TestCase):
    def test_changed_files_sees_committed_staged_unstaged_and_untracked(self) -> None:
        with TemporaryDirectory() as directory:
            repo = make_repo(Path(directory))
            self.assertEqual(changed_files(repo, "main"), [])
            git(repo, "checkout", "-q", "-b", "work")
            (repo / "README.md").write_text("committed change\n", encoding="utf-8")
            git(repo, "commit", "-q", "-am", "readme")
            (repo / "docs" / "guide.md").write_text("staged\n", encoding="utf-8")
            git(repo, "add", "docs/guide.md")
            (repo / "docs" / "new file.md").write_text("untracked with space\n", encoding="utf-8")
            (repo / "extra").mkdir()
            (repo / "extra" / "x.txt").write_text("nested untracked\n", encoding="utf-8")
            self.assertEqual(
                changed_files(repo, "main"),
                ["README.md", "docs/guide.md", "docs/new file.md", "extra/x.txt"],
            )
            git(repo, "mv", "docs/guide.md", "docs/renamed.md")
            files = changed_files(repo, "main")
            self.assertIn("docs/renamed.md", files)
            self.assertIn("docs/guide.md", files)

    def test_changed_files_ignores_a_poisoned_git_dir_from_the_environment(self) -> None:
        # PIP-907 (b): a poisoned GIT_DIR pointing nowhere would make the
        # internal git plumbing here fail outright if inherited.
        with TemporaryDirectory() as directory:
            repo = make_repo(Path(directory))
            (repo / "README.md").write_text("changed\n", encoding="utf-8")
            poison = {name: "/nonexistent/should-not-be-used" for name in GIT_CONTEXT_ENV}
            with mock.patch.dict(os.environ, poison):
                self.assertEqual(changed_files(repo, "main"), ["README.md"])

    def test_a_rename_reports_the_source_path_committed_or_not(self) -> None:
        # A1: ``git diff --name-only`` detects renames and prints only the new
        # path, so ``git mv AGENTS.md docs/x.md && git commit`` deleted a
        # restricted file without the write set noticing.
        for commit in (True, False):
            with self.subTest(committed=commit), TemporaryDirectory() as directory:
                repo = make_repo(Path(directory))
                (repo / "AGENTS.md").write_text("rules\n" * 20, encoding="utf-8")
                git(repo, "add", "AGENTS.md")
                git(repo, "commit", "-q", "-m", "agents")
                git(repo, "checkout", "-q", "-b", "work")
                git(repo, "mv", "AGENTS.md", "docs/x.md")
                if commit:
                    git(repo, "commit", "-q", "-m", "move")
                files = changed_files(repo, "main")
                self.assertIn("AGENTS.md", files)
                self.assertIn("docs/x.md", files)
                self.assertEqual(outside_write_set(files, ["README.md", "docs/"]), ["AGENTS.md"])

    def test_write_set_matches_files_and_directory_prefixes(self) -> None:
        write_set = ["README.md", "docs/", "tests/mission"]
        self.assertTrue(within_write_set(["README.md", "docs/a.md", "tests/mission/x.py"], write_set))
        self.assertEqual(
            outside_write_set(["README.md", "READMEX.md", "docs2/a.md", "tests/other.py", "tests/missionary.py"], write_set),
            ["READMEX.md", "docs2/a.md", "tests/missionary.py", "tests/other.py"],
        )
        self.assertFalse(within_write_set(["src/a.py"], write_set))
        self.assertTrue(within_write_set([], write_set))


class ChecksAndArtifactsTests(TestCase):
    def test_run_check_keeps_only_return_code_and_output_size(self) -> None:
        with TemporaryDirectory() as directory:
            cwd = Path(directory)
            passed = run_check("echo secret-output-that-must-not-be-kept && exit 0", cwd)
            self.assertIsInstance(passed, CheckResult)
            self.assertTrue(passed.passed)
            self.assertEqual(passed.returncode, 0)
            self.assertGreater(passed.output_bytes, 0)
            self.assertFalse(passed.timed_out)
            self.assertFalse(hasattr(passed, "stdout"))
            self.assertNotIn("secret-output", repr(passed))
            failed = run_check("exit 3", cwd)
            self.assertEqual((failed.passed, failed.returncode), (False, 3))
            started = time.monotonic()
            slow = run_check("sleep 5", cwd, timeout=0.3)
            self.assertLess(time.monotonic() - started, 4)
            self.assertEqual((slow.passed, slow.timed_out), (False, True))
            self.assertIsNone(slow.returncode)
            uses_cwd = run_check("test -f marker", cwd)
            self.assertFalse(uses_cwd.passed)
            (cwd / "marker").write_text("x", encoding="utf-8")
            self.assertTrue(run_check("test -f marker", cwd).passed)

    def test_check_artifact_requires_existence_and_pattern(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "guide.md"
            missing = check_artifact(path, None)
            self.assertEqual((missing.exists, missing.satisfied, missing.fingerprint), (False, False, None))
            path.write_text("run pipe idea now\n", encoding="utf-8")
            plain = check_artifact(path, None)
            self.assertTrue(plain.satisfied)
            self.assertRegex(plain.fingerprint, r"^sha256:[a-f0-9]{64}$")
            self.assertTrue(check_artifact(path, "pipe (idea|adopt)").satisfied)
            unmatched = check_artifact(path, "pipe bootstrap")
            self.assertEqual((unmatched.exists, unmatched.satisfied), (True, False))
            self.assertFalse(check_artifact(Path(directory), None).satisfied, "a directory is not an artifact")

    def test_verify_criteria_covers_check_and_artifact_kinds_only(self) -> None:
        with TemporaryDirectory() as directory:
            repo = make_repo(Path(directory))
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            before = verify_criteria(mission, repo)
            self.assertEqual([(item.id, item.kind, item.satisfied) for item in before],
                             [("C1", "check", False), ("C2", "artifact", False)])
            self.assertEqual(before[0].evidence_ref, "check:C1:rc1")
            self.assertIsNone(before[0].evidence_fingerprint)
            for relative, content in GOOD_FILES.items():
                (repo / relative).write_text(content, encoding="utf-8")
            after = verify_criteria(mission, repo)
            self.assertTrue(all(item.satisfied for item in after))
            self.assertEqual(after[0].evidence_ref, "check:C1:rc0")
            self.assertEqual(after[1].evidence_ref, "artifact:C2")
            self.assertRegex(after[1].evidence_fingerprint, r"^sha256:")

    def test_run_check_ignores_git_context_variables_from_the_environment(self) -> None:
        # PIP-907 (b): a criterion ``check`` command is arbitrary shell that
        # often invokes ``git`` itself; it must not see a ``GIT_DIR`` (or any
        # of ``GIT_CONTEXT_ENV``) a hook chain exported into the supervisor's
        # own environment.
        poison = {name: "/nonexistent/should-not-be-used" for name in GIT_CONTEXT_ENV}
        probe = " || ".join(f'[ -n "${{{name}:-}}" ]' for name in GIT_CONTEXT_ENV)
        with TemporaryDirectory() as directory, mock.patch.dict(os.environ, poison):
            result = run_check(f"! ({probe})", Path(directory))
        self.assertTrue(result.passed, "none of GIT_CONTEXT_ENV reached the check command")

    def test_check_honours_criterion_cwd(self) -> None:
        with TemporaryDirectory() as directory:
            repo = make_repo(Path(directory))
            document = loop_mission(repo)
            document["successCriteria"] = [
                {"id": "D1", "text": "guide is here", "kind": "check", "command": "test -f guide.md", "cwd": "docs"},
            ]
            mission = build_mission(document, created_at=CREATED_AT)
            self.assertTrue(verify_criteria(mission, repo)[0].satisfied)


class DiffTests(TestCase):
    def test_diff_text_and_fingerprint_track_every_kind_of_change(self) -> None:
        with TemporaryDirectory() as directory:
            repo = make_repo(Path(directory))
            git(repo, "checkout", "-q", "-b", "work")
            empty = diff_fingerprint(repo, "main")
            self.assertEqual(diff_text(repo, "main"), "")
            (repo / "README.md").write_text("committed\n", encoding="utf-8")
            git(repo, "commit", "-q", "-am", "readme")
            committed = diff_fingerprint(repo, "main")
            self.assertNotEqual(empty, committed)
            self.assertIn("committed", diff_text(repo, "main"))
            (repo / "docs" / "untracked.md").write_text("brand new\n", encoding="utf-8")
            with_untracked = diff_fingerprint(repo, "main")
            self.assertNotEqual(committed, with_untracked)
            self.assertIn("brand new", diff_text(repo, "main"))
            self.assertEqual(diff_fingerprint(repo, "main"), with_untracked, "fingerprint is stable")

    def test_fingerprint_does_not_change_when_the_same_content_is_committed(self) -> None:
        # The circuit breaker compares cycles; the supervisor's delivery commit
        # must not look like progress.
        with TemporaryDirectory() as directory:
            repo = make_repo(Path(directory))
            git(repo, "checkout", "-q", "-b", "work")
            (repo / "README.md").write_text("changed\n", encoding="utf-8")
            (repo / "docs" / "guide.md").write_text("also changed\n", encoding="utf-8")
            git(repo, "add", "docs/guide.md")
            git(repo, "commit", "-q", "-m", "partial")
            (repo / "docs" / "guide.md").write_text("also changed, twice\n", encoding="utf-8")
            uncommitted = diff_fingerprint(repo, "main")
            git(repo, "commit", "-q", "-am", "rest")
            self.assertEqual(diff_fingerprint(repo, "main"), uncommitted)
            self.assertIn("also changed, twice", diff_text(repo, "main"))
