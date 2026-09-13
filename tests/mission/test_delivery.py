"""Mission Loop B, slice 3: worktree, commit, idempotent PR, checks polling."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from pipe_venture_builder.mission import delivery
from pipe_venture_builder.mission.contract import build_mission
from pipe_venture_builder.mission.delivery import (
    GIT_CONTEXT_ENV,
    WorktreeNotReady,
    branch_name,
    checks_status,
    child_env,
    commit_if_needed,
    current_branch,
    ensure_worktree,
    existing_pr,
    gh_env,
    git_config_snapshot,
    native_worktree_name,
    open_pr,
    pr_body,
    pr_title,
    push_branch,
    remove_worktree,
    slugify,
    worktree_path,
    worktree_ready,
)
from tests.mission.helpers import CREATED_AT
from tests.mission.loop_helpers import (
    FakeBinaries,
    fabricate_native_worktree,
    git,
    loop_mission,
    make_repo,
    remote_workspace,
)


class BranchAndWorktreeTests(TestCase):
    def test_branch_name_is_claude_prefixed_with_a_short_slug(self) -> None:
        self.assertEqual(slugify("Docs param de contradizer o código!"), "docs-param-de-contradizer-o-codigo")
        self.assertEqual(slugify("   "), "mission")
        self.assertLessEqual(len(slugify("palavra " * 30)), 40)
        with TemporaryDirectory() as directory:
            mission = build_mission(loop_mission(make_repo(Path(directory))), created_at=CREATED_AT)
        self.assertEqual(branch_name(mission), f"claude/{mission['missionId']}-docs-param-de-contradizer-o-codigo")

    def test_ensure_worktree_adopts_the_native_worktree_and_is_then_idempotent(self) -> None:
        # PIP-915: no more ``git worktree add`` here — a worker run's own
        # ``--worktree`` creates it natively; ``ensure_worktree`` only adopts
        # (relocates + renames) what that run left behind, once.
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            home = root / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            expected = home / mission["missionId"] / "worktree"
            self.assertEqual(worktree_path(mission["missionId"], home), expected)
            self.assertIsNone(worktree_ready(mission, home=home))

            native = fabricate_native_worktree(repo, mission)
            first = ensure_worktree(mission, home=home)
            self.assertEqual(first, expected)
            self.assertFalse(native.exists(), "the native worktree was moved, not copied")
            self.assertTrue((first / "README.md").is_file())
            self.assertEqual(git(first, "branch", "--show-current").strip(), branch_name(mission))
            self.assertEqual(git(first, "rev-parse", "HEAD"), git(repo, "rev-parse", "main"))
            self.assertEqual(worktree_ready(mission, home=home), first)

            second = ensure_worktree(mission, home=home)
            self.assertEqual(second, first)
            listed = [line for line in git(repo, "worktree", "list", "--porcelain").splitlines() if line.startswith("worktree ")]
            self.assertEqual(len(listed), 2, "main checkout + one mission worktree")

    def test_ensure_worktree_raises_when_the_canonical_directory_is_gone_and_nothing_native_is_left(self) -> None:
        # PIP-915: recreating a destroyed worktree by hand is exactly the
        # manual ``git worktree add`` capability this ticket removes — the
        # only way back is a fresh worker dispatch with ``--worktree``.
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            home = root / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=home)
            (worktree / "README.md").write_text("work in progress\n", encoding="utf-8")
            git(worktree, "commit", "-q", "-am", "wip")
            shutil.rmtree(worktree)
            with self.assertRaises(WorktreeNotReady):
                ensure_worktree(mission, home=home)

    def test_a_directory_inside_another_repository_is_not_the_mission_worktree(self) -> None:
        # B3 (review S6): ``rev-parse --is-inside-work-tree`` is true for any
        # directory inside any repository.
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            outer = root / "outer"
            outer.mkdir()
            git(outer, "init", "-q", "-b", "main")
            home = outer / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            empty = worktree_path(mission["missionId"], home)
            empty.mkdir(parents=True)
            fabricate_native_worktree(repo, mission)
            created = ensure_worktree(mission, home=home)
            self.assertEqual(created, empty)
            self.assertEqual(Path(git(created, "rev-parse", "--show-toplevel").strip()).resolve(),
                             created.resolve(), "a real worktree was created, not the outer repo reused")
            self.assertEqual(git(created, "branch", "--show-current").strip(), branch_name(mission))

            other = build_mission(loop_mission(repo, title="Outra missao qualquer"), created_at=CREATED_AT)
            filled = worktree_path(other["missionId"], home)
            filled.mkdir(parents=True)
            (filled / "notes.txt").write_text("not a worktree\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                ensure_worktree(other, home=home)

    def test_a_worktree_on_another_branch_or_of_another_repo_is_refused(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            home = root / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=home)
            git(worktree, "checkout", "-q", "-b", "elsewhere")
            with self.assertRaises(RuntimeError, msg="wrong branch"):
                ensure_worktree(mission, home=home)
            git(worktree, "checkout", "-q", branch_name(mission))
            self.assertEqual(ensure_worktree(mission, home=home), worktree)

            stranger_root = root / "stranger"
            stranger_root.mkdir()
            stranger = make_repo(stranger_root)
            foreign = worktree_path(mission["missionId"], root / "home2")
            foreign.parent.mkdir(parents=True)
            git(stranger, "worktree", "add", "-q", str(foreign), "-b", branch_name(mission))
            with self.assertRaises(RuntimeError, msg="a worktree of another repository"):
                ensure_worktree(mission, home=root / "home2")

    def test_commit_if_needed_commits_only_when_dirty(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=root / "home")
            self.assertFalse(commit_if_needed(worktree, f"{mission['missionId']}: nothing"))
            (worktree / "docs" / "guide.md").write_text("pipe idea\n", encoding="utf-8")
            (worktree / "docs" / "new.md").write_text("new\n", encoding="utf-8")
            self.assertTrue(commit_if_needed(worktree, f"{mission['missionId']}: supervisor commit"))
            self.assertEqual(git(worktree, "status", "--porcelain"), "")
            self.assertIn(f"{mission['missionId']}: supervisor commit", git(worktree, "log", "-1", "--format=%s"))
            self.assertFalse(commit_if_needed(worktree, "again"))


class WorktreeCleanupTests(TestCase):
    """PIP-915, C4: retiring a mission's worktree — including the lock the
    native ``claude --worktree`` worktree carries — leaves no orphan worktree
    directory and no dangling local branch behind."""

    def test_remove_worktree_unlocks_removes_and_deletes_the_branch(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            home = root / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission, locked=True)
            worktree = ensure_worktree(mission, home=home)
            branch = branch_name(mission)
            self.assertTrue(worktree.is_dir())
            self.assertIn(f"refs/heads/{branch}", git(repo, "branch", "--list", "--format=%(refname)"))
            # ``ensure_worktree`` already unlocked it while adopting (see
            # ``_adopt_native_worktree``) — lock it again here so this test
            # exercises ``remove_worktree``'s own unlock-then-remove path
            # directly, on the canonical worktree it actually receives.
            git(repo, "worktree", "lock", str(worktree))

            remove_worktree(mission, home=home)

            self.assertFalse(worktree.exists(), "no orphan worktree directory")
            listed = [line for line in git(repo, "worktree", "list", "--porcelain").splitlines()
                      if line.startswith("worktree ")]
            self.assertEqual(len(listed), 1, "only the main checkout is left")
            self.assertNotIn(f"refs/heads/{branch}", git(repo, "branch", "--list", "--format=%(refname)"),
                             "no branch left dangling with no working tree pointing at it")

    def test_remove_worktree_still_works_when_it_was_never_locked(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            home = root / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission, locked=False)
            worktree = ensure_worktree(mission, home=home)
            self.assertTrue(worktree.is_dir())

            remove_worktree(mission, home=home)

            self.assertFalse(worktree.exists())

    def test_remove_worktree_is_idempotent_when_nothing_was_ever_adopted(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            home = root / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            remove_worktree(mission, home=home)  # never raises
            remove_worktree(mission, home=home)  # calling it twice is still safe

    def test_plain_worktree_remove_alone_fails_on_a_locked_worktree(self) -> None:
        """Controle: prova que o lock é o obstáculo real — sem o unlock que
        ``remove_worktree`` faz, um ``git worktree remove --force`` comum
        falha ('cannot remove a locked working tree'). Sem isto, o teste
        acima passaria mesmo que ``remove_worktree`` nunca tratasse o lock."""

        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            home = root / "home"
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission, locked=True)
            worktree = ensure_worktree(mission, home=home)
            git(repo, "worktree", "lock", str(worktree))  # adoption already unlocked it once
            completed = subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=repo, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(completed.returncode, 0, "the control hook is not itself locked")
            self.assertIn("lock", (completed.stderr or "").lower())
            self.assertTrue(worktree.is_dir(), "the plain remove must not have actually removed it")


class GitConfigSnapshotTests(TestCase):
    def test_snapshot_changes_when_the_worktree_writes_repository_config(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=root / "home")
            before = git_config_snapshot(repo, worktree)
            self.assertEqual(git_config_snapshot(repo, worktree), before, "stable without changes")
            (worktree / "README.md").write_text("edit\n", encoding="utf-8")
            self.assertEqual(git_config_snapshot(repo, worktree), before, "file edits are not config")
            git(worktree, "config", "core.hooksPath", "ignored/hooks")
            self.assertNotEqual(git_config_snapshot(repo, worktree), before)
            self.assertNotIn("ignored/hooks", repr(git_config_snapshot(repo, worktree)),
                             "only hashes are kept")

    def test_adopting_a_remote_base_ref_native_worktree_writes_no_shared_tracking_config(self) -> None:
        # PIP-907 (c), re-scoped for PIP-915: creating the worktree off a
        # remote ``baseRef`` (``origin/main``) is a worker run's job now
        # (``fabricate_native_worktree`` stands in, ``--no-track`` as the
        # native tool presumably also does); what ``ensure_worktree`` itself
        # does — ``git worktree move`` + ``git branch -m`` — must not write
        # ``branch.<branch>.remote``/``.merge`` into the repository's *shared*
        # config on its own, the same file every worktree reads.
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            mission = build_mission(
                loop_mission(repo, workspace=remote_workspace(repo)), created_at=CREATED_AT
            )
            fabricate_native_worktree(repo, mission)
            before = git(repo, "config", "--local", "--list")
            ensure_worktree(mission, home=root / "home")
            self.assertEqual(git(repo, "config", "--local", "--list"), before)
            branch = branch_name(mission)
            tracking = subprocess.run(
                ["git", "config", "--get", f"branch.{branch}.remote"],
                cwd=repo, capture_output=True, text=True, check=False,
            )
            self.assertEqual(tracking.stdout.strip(), "")

    def test_a_second_missions_worktree_creation_does_not_change_the_snapshot(self) -> None:
        # PIP-907 (d, concurrent scenario): the exact mechanism behind the
        # 11/09 false positive — creating another mission's worktree off a
        # remote ``baseRef`` must not touch the config ``git_config_snapshot``
        # hashes, or a concurrent mission trips ``git_config_tampered`` for a
        # run that tampered nothing.
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            mission = build_mission(
                loop_mission(repo, workspace=remote_workspace(repo)), created_at=CREATED_AT
            )
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=root / "home")
            before = git_config_snapshot(repo, worktree)

            other = build_mission(
                loop_mission(repo, workspace=remote_workspace(repo), title="Outra missao concorrente"),
                created_at=CREATED_AT,
            )
            fabricate_native_worktree(repo, other)
            ensure_worktree(other, home=root / "home-b")
            self.assertEqual(git_config_snapshot(repo, worktree), before)


class PullRequestTests(TestCase):
    def test_open_pr_pushes_once_and_is_idempotent_per_branch(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
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

    def test_push_branch_publishes_head_not_the_local_branch_ref(self) -> None:
        # B4: ``git push origin <branch>`` publishes the local ref even when
        # HEAD (what was verified) is elsewhere.
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=root / "home")
            branch = branch_name(mission)
            (worktree / "README.md").write_text("first\n", encoding="utf-8")
            commit_if_needed(worktree, "first")
            git(worktree, "checkout", "-q", "--detach")
            (worktree / "README.md").write_text("second\n", encoding="utf-8")
            commit_if_needed(worktree, "second")
            push_branch(worktree, branch)
            self.assertEqual(
                git(repo, "ls-remote", "--heads", "origin", branch).split()[0],
                git(worktree, "rev-parse", "HEAD").strip(),
            )
            self.assertIsNone(current_branch(worktree))
            git(worktree, "checkout", "-q", branch)
            self.assertEqual(current_branch(worktree), branch)

    def test_push_does_not_leak_python_path_into_repository_hooks(self) -> None:
        # Demo real de 11/09: o supervisor roda do código-fonte com
        # PYTHONPATH=src; o pre-push do repositório herdou isso, tentou
        # `python3 -m pytest` e o push falhou com exit 1. Filhos git/gh não
        # podem herdar o ambiente do interpretador do supervisor.
        import os
        from unittest import mock

        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            hooks = root / "hooks"
            hooks.mkdir()
            hook = hooks / "pre-push"
            hook.write_text(
                '#!/bin/sh\nif [ -n "${PYTHONPATH:-}" ]; then echo leak >&2; exit 1; fi\nexit 0\n',
                encoding="utf-8",
            )
            hook.chmod(0o755)
            git(repo, "config", "core.hooksPath", str(hooks))
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=root / "home")
            branch = branch_name(mission)
            (worktree / "README.md").write_text("changed\n", encoding="utf-8")
            commit_if_needed(worktree, "change")
            with mock.patch.dict(os.environ, {"PYTHONPATH": "src", "PYTHONHOME": "/nowhere"}):
                push_branch(worktree, branch)
            self.assertIn(branch, git(repo, "ls-remote", "--heads", "origin", branch))

    def test_commit_and_push_never_run_hooks_from_the_worktree_or_the_repository(self) -> None:
        # PIP-907 (a): ``core.hooksPath`` is resolved relative to whatever
        # tree git is invoked from. A hook planted at that relative path
        # inside the mission WORKTREE (code the worker may have written) —
        # or simply sitting at the default ``.git/hooks`` — must never run
        # with the supervisor's credentials during the entrega's own commit
        # and push. This is how PIP-904 v1 moved a branch and set
        # ``core.bare=true`` on the real repository on 11/09.
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            git(repo, "config", "core.hooksPath", "scripts/git-hooks")
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=root / "home")
            branch = branch_name(mission)

            marker = root / "hook-ran"
            hooks = worktree / "scripts" / "git-hooks"
            hooks.mkdir(parents=True)
            for name in ("pre-commit", "commit-msg", "post-commit", "pre-push"):
                hook = hooks / name
                hook.write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 1\n', encoding="utf-8")
                hook.chmod(0o755)
            default_hook = repo / ".git" / "hooks" / "pre-push"
            default_hook.write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 1\n', encoding="utf-8")
            default_hook.chmod(0o755)

            (worktree / "README.md").write_text("changed\n", encoding="utf-8")
            self.assertTrue(commit_if_needed(worktree, "change"), "a hook exiting 1 must not fail the commit")
            push_branch(worktree, branch)
            self.assertFalse(marker.exists(), "no hook ran during the supervisor's commit or push")
            self.assertEqual(
                git(repo, "ls-remote", "--heads", "origin", branch).split()[0],
                git(worktree, "rev-parse", "HEAD").strip(),
            )

    def test_default_git_hooks_never_run_during_commit_and_push(self) -> None:
        # Sem ``core.hooksPath``: os hooks padrão em ``.git/hooks`` (revisão
        # do PIP-907, P3 — o teste acima tem hooksPath e nunca os consulta).
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=root / "home")
            marker = root / "hook-ran"
            for name in ("pre-commit", "commit-msg", "post-commit", "reference-transaction", "pre-push"):
                hook = repo / ".git" / "hooks" / name
                hook.write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 1\n', encoding="utf-8")
                hook.chmod(0o755)
            (worktree / "README.md").write_text("changed\n", encoding="utf-8")
            self.assertTrue(commit_if_needed(worktree, "change"))
            push_branch(worktree, branch_name(mission))
            self.assertFalse(marker.exists(), "a hook in .git/hooks ran during the supervisor's commit or push")

    def test_adopting_the_native_worktree_runs_no_hook(self) -> None:
        # Revisão do PIP-907, P1, re-scoped for PIP-915: creating the
        # worktree is a worker run's job now (``fabricate_native_worktree``
        # stands in, hook-safe on purpose — see its own comment); what
        # ``ensure_worktree`` itself does to adopt it — ``git worktree move``
        # and ``git branch -m`` — must still never run a repository hook
        # (``post-checkout``, ``reference-transaction``).
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            marker = root / "hook-ran"
            for name in ("post-checkout", "reference-transaction"):
                hook = repo / ".git" / "hooks" / name
                hook.write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 0\n', encoding="utf-8")
                hook.chmod(0o755)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            ensure_worktree(mission, home=root / "home")
            self.assertFalse(marker.exists(), "adopting the mission worktree ran a hook")

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
            self.assertEqual(json.loads(json.dumps(calls[0]))[2], "claude/x")
            self.assertIn("--json", calls[0])


class ChildEnvGitContextTests(TestCase):
    """PIP-907 (b): a linked worktree's hook can export an absolute
    ``GIT_DIR`` (and friends) into the environment; no git/gh child of the
    supervisor may inherit them — they redirected git at the wrong
    repository on 11/09."""

    POISON = {
        "GIT_DIR": "/nonexistent/should-not-be-used/.git",
        "GIT_WORK_TREE": "/nonexistent/should-not-be-used",
        "GIT_INDEX_FILE": "/nonexistent/should-not-be-used/.git/index",
        "GIT_OBJECT_DIRECTORY": "/nonexistent/should-not-be-used/.git/objects",
        "GIT_COMMON_DIR": "/nonexistent/should-not-be-used/.git",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/nonexistent/also-not-used",
        "GIT_PREFIX": "nonexistent/",
        "GIT_QUARANTINE_PATH": "/nonexistent/quarantine",
        "GIT_NAMESPACE": "nonexistent",
    }

    def test_child_env_strips_every_declared_git_context_variable(self) -> None:
        self.assertEqual(set(self.POISON), set(GIT_CONTEXT_ENV), "the poisoned set matches the declared one")
        with mock.patch.dict(os.environ, self.POISON):
            env = child_env()
        for key in GIT_CONTEXT_ENV:
            self.assertNotIn(key, env)

    def test_git_children_ignore_a_poisoned_git_dir_in_the_supervisor_environment(self) -> None:
        # A poisoned ``GIT_DIR`` pointing nowhere would make any git child
        # that inherited it fail outright ("not a git repository") — the
        # absence of that failure is the proof the variable was stripped.
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo = make_repo(root, with_origin=True)
            mission = build_mission(loop_mission(repo), created_at=CREATED_AT)
            fabricate_native_worktree(repo, mission)
            worktree = ensure_worktree(mission, home=root / "home")
            branch = branch_name(mission)
            (worktree / "README.md").write_text("changed\n", encoding="utf-8")
            with mock.patch.dict(os.environ, self.POISON):
                self.assertTrue(commit_if_needed(worktree, "change"))
                push_branch(worktree, branch)
            self.assertEqual(
                git(repo, "ls-remote", "--heads", "origin", branch).split()[0],
                git(worktree, "rev-parse", "HEAD").strip(),
            )


class ChildEnvIsolationTests(TestCase):
    """PIP-905: no child of the supervisor (git, gh, checks, worker, reviewer,
    responder) may inherit a variable that changes what git does or which
    Python interpreter runs. The filter is a ``GIT_`` **prefix** plus two short
    explicit lists, so a git version with a new variable is covered without
    anyone updating a list (revisão adversarial do PIP-905, achado A1)."""

    def test_every_git_prefixed_variable_is_stripped(self) -> None:
        # Prefixo, não lista: a revisão adversarial do PIP-905 mediu
        # GIT_CONFIG_GLOBAL, GIT_EXTERNAL_DIFF e GIT_SSH_COMMAND executando
        # programa e falsificando o diff mandado ao revisor.
        names = [
            "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX", "GIT_QUARANTINE_PATH", "GIT_NAMESPACE",
            "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0",
            "GIT_CONFIG_VALUE_0", "GIT_CONFIG_KEY_12", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM",
            "GIT_CONFIG_NOSYSTEM", "GIT_EXTERNAL_DIFF", "GIT_SSH_COMMAND", "GIT_SSH",
            "GIT_PROTOCOL_FROM_USER", "GIT_PAGER", "GIT_EDITOR", "GIT_SEQUENCE_EDITOR",
            "GIT_GRAFT_FILE", "GIT_SHALLOW_FILE", "GIT_REPLACE_REF_BASE", "GIT_IMPLICIT_WORK_TREE",
            "GIT_ASKPASS", "GIT_TRACE", "GIT_ALLOW_PROTOCOL", "GIT_CEILING_DIRECTORIES",
            "GIT_FUTURE_VARIABLE_NOBODY_HAS_SEEN_YET",
        ]
        with mock.patch.dict(os.environ, {name: "/poison" for name in names}):
            env = child_env()
        self.assertEqual([name for name in names if name in env and env[name] == "/poison"], [])

    def test_every_name_git_itself_calls_local_context_is_stripped(self) -> None:
        out = subprocess.run(
            ["git", "rev-parse", "--local-env-vars"], capture_output=True, text=True, check=True,
        )
        names = [line.strip() for line in out.stdout.splitlines() if line.strip()]
        self.assertIn("GIT_DIR", names, "sanity: git still lists GIT_DIR as local context")
        with mock.patch.dict(os.environ, {name: "/poison" for name in names}):
            env = child_env()
        self.assertEqual([name for name in names if name in env], [])

    def test_program_and_editor_variables_are_stripped(self) -> None:
        for name in ("EDITOR", "VISUAL", "PAGER", "SSH_ASKPASS"):
            with self.subTest(name=name), mock.patch.dict(os.environ, {name: "/poison"}):
                env = child_env()
            self.assertNotIn(name, env, name)

    def test_terminal_prompt_is_forced_off(self) -> None:
        with mock.patch.dict(os.environ, {"GIT_TERMINAL_PROMPT": "1"}):
            env = child_env()
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")

    def test_each_new_interpreter_variable_is_stripped(self) -> None:
        for name in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONUSERBASE", "PYTHONNOUSERSITE",
                     "PYTHONPLATLIBDIR", "PYTHONSAFEPATH", "VIRTUAL_ENV", "__PYVENV_LAUNCHER__"):
            with self.subTest(name=name), mock.patch.dict(os.environ, {name: "/poison"}):
                env = child_env()
            self.assertNotIn(name, env, name)

    def test_what_a_child_still_needs_survives_the_filter(self) -> None:
        with mock.patch.dict(os.environ, {"GH_TOKEN": "t", "SSH_AUTH_SOCK": "/tmp/agent.sock"}):
            env = child_env()
        for name in ("PATH", "HOME", "GH_TOKEN", "SSH_AUTH_SOCK"):
            self.assertIn(name, env, name)


class GhEnvTests(TestCase):
    """PIP-905: ``gh`` shells out to ``git`` internally, so it needs its own
    ``core.hooksPath=/dev/null`` on top of everything ``child_env()`` already
    strips."""

    def test_gh_env_forces_no_hooks_path(self) -> None:
        env = gh_env()
        self.assertEqual(env.get("GIT_CONFIG_COUNT"), "1")
        self.assertEqual(env.get("GIT_CONFIG_KEY_0"), "core.hooksPath")
        self.assertEqual(env.get("GIT_CONFIG_VALUE_0"), "/dev/null")

    def test_gh_env_overrides_an_inherited_git_config_and_drops_the_rest_of_it(self) -> None:
        with mock.patch.dict(os.environ, {
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": "/evil-hooks",
            "GIT_CONFIG_KEY_1": "core.bare",
            "GIT_CONFIG_VALUE_1": "true",
            "GIT_CONFIG_PARAMETERS": "'core.bare'='true'",
        }):
            env = gh_env()
        self.assertEqual(env.get("GIT_CONFIG_COUNT"), "1")
        self.assertEqual(env.get("GIT_CONFIG_KEY_0"), "core.hooksPath")
        self.assertEqual(env.get("GIT_CONFIG_VALUE_0"), "/dev/null")
        self.assertNotIn("GIT_CONFIG_KEY_1", env)
        self.assertNotIn("GIT_CONFIG_VALUE_1", env)
        self.assertNotIn("GIT_CONFIG_PARAMETERS", env)

    def test_gh_env_still_strips_interpreter_variables(self) -> None:
        with mock.patch.dict(os.environ, {"VIRTUAL_ENV": "/venv", "PYTHONPATH": "src"}):
            env = gh_env()
        self.assertNotIn("VIRTUAL_ENV", env)
        self.assertNotIn("PYTHONPATH", env)


class FakeGhInterpreterEnvSyncTests(TestCase):
    """PIP-909: ``fake_gh.py`` used to duplicate ``_INTERPRETER_ENV`` as a
    literal tuple, with nothing to catch the two drifting apart. It now
    imports the real one — this test pins that import, so a future edit to
    either tuple without the other fails here instead of leaving the fake's
    assertion silently vacuous."""

    def test_fake_gh_derives_the_real_interpreter_env_without_importing(self) -> None:
        # O fake roda como script, com o ambiente já limpo pelo ``gh_env()``:
        # importar o pacote ali quebrou o fake num ``env -i`` (PIP-909, revisão
        # adversarial, achado 1). Ele lê a tupla de ``delivery.py`` com ``ast``,
        # e este teste é o que garante que as duas não divergem.
        from tests.mission.fakes import fake_gh

        self.assertEqual(tuple(fake_gh._INTERPRETER_ENV), tuple(delivery._INTERPRETER_ENV))
        self.assertGreater(len(fake_gh._INTERPRETER_ENV), 0, "a derivação por ast achou a lista")
        source = Path(fake_gh.__file__).read_text(encoding="utf-8")
        self.assertNotIn("from pipe_venture_builder", source, "o fake continua stdlib puro")


class GhCallsReceiveGhEnvTests(TestCase):
    """PIP-905: every ``gh`` the supervisor runs uses ``gh_env()``, not the
    plain ``child_env()`` — the fake ``gh`` records what it actually got."""

    def test_every_gh_invocation_gets_hooks_off_and_no_interpreter_leak(self) -> None:
        with TemporaryDirectory() as directory, FakeBinaries(Path(directory)) as fakes:
            root = Path(directory)
            fakes.gh_checks([["pass"]])
            with mock.patch.dict(os.environ, {
                "VIRTUAL_ENV": "/poison",
                "GIT_CONFIG_COUNT": "9",
                "GIT_CONFIG_KEY_0": "core.hooksPath",
                "GIT_CONFIG_VALUE_0": "/evil-hooks",
            }):
                existing_pr(fakes.gh_bin, "claude/x", cwd=root)
                checks_status(fakes.gh_bin, "claude/x", cwd=root)
            envs = fakes.gh_envs()
            self.assertGreaterEqual(len(envs), 2)
            for env in envs:
                self.assertEqual(env.get("GIT_CONFIG_COUNT"), "1")
                self.assertEqual(env.get("GIT_CONFIG_KEY_0"), "core.hooksPath")
                self.assertEqual(env.get("GIT_CONFIG_VALUE_0"), "/dev/null")
                self.assertNotIn("VIRTUAL_ENV", env)
