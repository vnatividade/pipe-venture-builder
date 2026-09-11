from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path
from unittest import TestCase, skipUnless

from pipe_venture_builder.adapters.deepseek_harness import (
    DeepSeekHarnessContractError,
    DeepSeekHarnessRunContext,
)
from tests.deepseek_harness.helpers import (
    DEFAULT_REFS,
    FINGERPRINT,
    SECRET_SENTINEL,
    TEXT_SENTINEL,
    TICKET_ID,
    assert_blocked,
    assert_metadata_only,
    build_context,
    context_fields,
    fixture_base,
    forbid_host_access,
    make_fixture_root,
    rendered_error,
)
from tests.helpers import REPOSITORY_ROOT


class DeepSeekHarnessRunContextTests(TestCase):
    """C1 context contract: ADR-004 D2 (workflows) and D7 (workspace)."""

    def test_review_and_check_build_relative_metadata_only_document(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            for workflow in ("review", "check"):
                with self.subTest(workflow=workflow):
                    context = build_context(root, workflow=workflow)
                    document = context.document()

                    self.assertEqual(document["workflow"], workflow)
                    self.assertEqual(document["linearTicketId"], TICKET_ID)
                    self.assertEqual(document["workspaceRefs"], list(DEFAULT_REFS))
                    self.assertEqual(
                        document["workspaceFingerprint"], context.workspace_fingerprint
                    )
                    self.assertRegex(context.workspace_fingerprint, FINGERPRINT)
                    self.assertRegex(context.context_fingerprint, FINGERPRINT)
                    constraints = document["constraints"]
                    self.assertIs(constraints["runtimeApprovalIsAuthority"], False)
                    self.assertIs(constraints["externalMutationAllowed"], False)
                    self.assertNotIn("fixtureRoot", document)
                    self.assertNotIn(str(base), json.dumps(document))
                    assert_metadata_only(self, document)

    def test_workflows_outside_review_and_check_are_rejected(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            for workflow in (
                "idea",
                "adopt",
                "reconcile",
                "deploy",
                "execute",
                "Review",
                "review ",
                "",
                None,
                1,
                TEXT_SENTINEL,
            ):
                with self.subTest(workflow=workflow):
                    assert_blocked(
                        self,
                        "workflow_unsupported",
                        build_context,
                        root,
                        workflow=workflow,
                        forbidden=(str(base),),
                    )

    def test_linear_ticket_id_is_required(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            self.assertEqual(
                build_context(root, linear_ticket_id="PIP-1").linear_ticket_id, "PIP-1"
            )
            for ticket in (
                "idea-note",
                "pip-899",
                "PIP-",
                "PIP-abc",
                "PIP-899 ",
                "PIP-899\n",
                "PIP-899/../x",
                "LIN-899",
                "",
                None,
                899,
                SECRET_SENTINEL,
            ):
                with self.subTest(ticket=ticket):
                    assert_blocked(
                        self,
                        "linear_ticket_invalid",
                        build_context,
                        root,
                        linear_ticket_id=ticket,
                        forbidden=(str(base),),
                    )

    def test_workspace_refs_are_sorted_and_deduplicated(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            context = build_context(
                root, workspace_refs=["review/notes.md", "README.md", "README.md"]
            )
            self.assertEqual(context.workspace_refs, DEFAULT_REFS)
            self.assertEqual(context.document()["workspaceRefs"], list(DEFAULT_REFS))

    def test_workspace_refs_container_is_validated(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            for refs in ("README.md", b"README.md", [], (), None, {"README.md": 1}):
                with self.subTest(refs=refs):
                    assert_blocked(
                        self,
                        "workspace_refs_invalid",
                        build_context,
                        root,
                        workspace_refs=refs,
                        forbidden=(str(base),),
                    )

    def test_absolute_refs_are_rejected_without_echoing_paths(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            for ref in (
                "/etc/hosts",
                str(root / "README.md"),
                "//README.md",
            ):
                with self.subTest(ref=ref):
                    assert_blocked(
                        self,
                        "workspace_ref_invalid",
                        build_context,
                        root,
                        workspace_refs=[ref],
                        forbidden=(str(base), "/etc/hosts"),
                    )

    def test_traversal_and_non_canonical_refs_are_rejected(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            (base / "outside.md").write_text("outside\n", encoding="utf-8")
            for ref in (
                "../outside.md",
                "review/../README.md",
                "review/../../outside.md",
                f"../{TEXT_SENTINEL}/notes.md",
                "./README.md",
                "review/./notes.md",
                "review//notes.md",
                "review/",
                ".",
                "..",
                "",
                "review\\notes.md",
                "..\\outside.md",
                "README.md\x00",
                None,
                1,
                b"README.md",
                Path("README.md"),
            ):
                with self.subTest(ref=ref):
                    assert_blocked(
                        self,
                        "workspace_ref_invalid",
                        build_context,
                        root,
                        workspace_refs=[ref],
                        forbidden=(str(base),),
                    )

    def test_secret_shaped_ref_is_rejected_without_echo(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            (root / "review" / f"{SECRET_SENTINEL}.md").write_text(
                "synthetic\n", encoding="utf-8"
            )
            assert_blocked(
                self,
                "workspace_ref_invalid",
                build_context,
                root,
                workspace_refs=[f"review/{SECRET_SENTINEL}.md"],
                forbidden=(str(base),),
            )

    def test_git_and_env_refs_are_forbidden_lexically(self) -> None:
        # Lexical checks precede filesystem access: these paths do not exist,
        # and the refusal must name the forbidden path class, not absence.
        with fixture_base() as base:
            root = make_fixture_root(base)
            for ref in (
                ".git/config",
                "review/.git/HEAD",
                ".Git/config",
                ".env",
                ".ENV",
                "review/.env",
                ".env.local",
                "review/.env.production",
            ):
                with self.subTest(ref=ref):
                    assert_blocked(
                        self,
                        "path_forbidden",
                        build_context,
                        root,
                        workspace_refs=[ref],
                        forbidden=(str(base),),
                    )

    def test_unreferenced_git_env_and_special_entries_in_root_are_forbidden(self) -> None:
        cases = {
            "env-at-root": lambda root: (root / ".env").write_text(
                "SYNTHETIC=1\n", encoding="utf-8"
            ),
            "env-variant-nested": lambda root: (root / "review" / ".env.local").write_text(
                "SYNTHETIC=1\n", encoding="utf-8"
            ),
            "nested-git": lambda root: (root / "vendor" / ".git").mkdir(parents=True),
        }
        for name, prepare in cases.items():
            with self.subTest(case=name), fixture_base() as base:
                root = make_fixture_root(base)
                prepare(root)
                assert_blocked(
                    self,
                    "path_forbidden",
                    build_context,
                    root,
                    forbidden=(str(base),),
                )

    @skipUnless(hasattr(os, "mkfifo"), "requires os.mkfifo")
    def test_special_file_inside_root_is_forbidden(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            os.mkfifo(root / "review" / "pipe")
            assert_blocked(
                self, "path_forbidden", build_context, root, forbidden=(str(base),)
            )

    def test_git_worktree_is_never_a_fixture_root(self) -> None:
        with fixture_base() as base:
            for name, marker in (("dir-marker", "dir"), ("file-marker", "file")):
                with self.subTest(case=name):
                    root = make_fixture_root(base, name)
                    if marker == "dir":
                        (root / ".git").mkdir()
                    else:
                        (root / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
                    assert_blocked(
                        self,
                        "fixture_root_forbidden",
                        build_context,
                        root,
                        forbidden=(str(base),),
                    )

            repository = base / "repository"
            (repository / ".git").mkdir(parents=True)
            nested_root = make_fixture_root(repository, "fixture")
            with self.subTest(case="inside-worktree"):
                assert_blocked(
                    self,
                    "fixture_root_forbidden",
                    build_context,
                    nested_root,
                    forbidden=(str(base),),
                )

    def test_real_pipe_repository_is_never_a_fixture_root(self) -> None:
        # Only lstat-level inspection of the real worktree is expected; the
        # exact code depends on which D7 violation is met first.
        codes = {"fixture_root_forbidden", "path_forbidden", "symlink_forbidden"}
        for root, ref in (
            (REPOSITORY_ROOT, "README.md"),
            (REPOSITORY_ROOT / "docs", "hermes/README.md"),
        ):
            with self.subTest(root=root.name):
                with self.assertRaises(DeepSeekHarnessContractError) as caught:
                    build_context(root, workspace_refs=[ref])
                self.assertIn(caught.exception.code, codes)
                self.assertNotIn(
                    str(REPOSITORY_ROOT), rendered_error(caught.exception)
                )

    def test_symlinked_ref_file_is_rejected_even_with_internal_target(self) -> None:
        cases = {
            "internal-target": lambda base, root: root / "README.md",
            "external-target": lambda base, root: base / "outside.md",
            # A dangling link proves the refusal comes from lstat, not from
            # following the link and failing on its target.
            "dangling-target": lambda base, root: root / "missing.md",
        }
        for name, target in cases.items():
            with self.subTest(case=name), fixture_base() as base:
                root = make_fixture_root(base)
                (base / "outside.md").write_text("outside\n", encoding="utf-8")
                (root / "alias.md").symlink_to(target(base, root))
                assert_blocked(
                    self,
                    "symlink_forbidden",
                    build_context,
                    root,
                    workspace_refs=["alias.md"],
                    forbidden=(str(base),),
                )

    def test_symlinked_ref_component_is_rejected_even_with_internal_target(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            (root / "linked").symlink_to(root / "review", target_is_directory=True)
            assert_blocked(
                self,
                "symlink_forbidden",
                build_context,
                root,
                workspace_refs=["linked/notes.md"],
                forbidden=(str(base),),
            )

    def test_unreferenced_symlink_anywhere_in_root_is_rejected(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            (root / "review" / "shortcut.md").symlink_to(root / "README.md")
            assert_blocked(
                self,
                "symlink_forbidden",
                build_context,
                root,
                workspace_refs=["README.md"],
                forbidden=(str(base),),
            )

    def test_symlinked_fixture_root_or_ancestor_is_rejected(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            root_link = base / "root-link"
            root_link.symlink_to(root, target_is_directory=True)
            with self.subTest(case="root"):
                assert_blocked(
                    self,
                    "symlink_forbidden",
                    build_context,
                    root_link,
                    forbidden=(str(base),),
                )

            make_fixture_root(base / "real-parent")
            parent_link = base / "parent-link"
            parent_link.symlink_to(base / "real-parent", target_is_directory=True)
            with self.subTest(case="ancestor"):
                assert_blocked(
                    self,
                    "symlink_forbidden",
                    build_context,
                    parent_link / "fixture",
                    forbidden=(str(base),),
                )

    def test_fixture_root_must_be_an_existing_directory(self) -> None:
        with fixture_base() as base:
            (base / "file.md").write_text("file\n", encoding="utf-8")
            for root in (base / "missing", base / "file.md"):
                with self.subTest(root=root.name):
                    assert_blocked(
                        self,
                        "fixture_root_invalid",
                        build_context,
                        root,
                        forbidden=(str(base),),
                    )

    def test_non_file_refs_are_rejected(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            for ref in ("review", "missing.md", "review/missing.md"):
                with self.subTest(ref=ref):
                    assert_blocked(
                        self,
                        "workspace_ref_not_file",
                        build_context,
                        root,
                        workspace_refs=[ref],
                        forbidden=(str(base),),
                    )

    def test_workspace_fingerprint_covers_allowlisted_content_only(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            original = build_context(root).workspace_fingerprint

            (root / "unlisted.md").write_text("not allowlisted\n", encoding="utf-8")
            self.assertEqual(build_context(root).workspace_fingerprint, original)

            self.assertNotEqual(
                build_context(root, workspace_refs=["README.md"]).workspace_fingerprint,
                original,
            )

            (root / "README.md").write_text("# Changed fixture\n", encoding="utf-8")
            self.assertNotEqual(build_context(root).workspace_fingerprint, original)

    def test_fingerprints_do_not_depend_on_absolute_root(self) -> None:
        with fixture_base() as base:
            first = build_context(make_fixture_root(base, "first"))
            second = build_context(make_fixture_root(base / "elsewhere", "second"))
            self.assertEqual(first.workspace_fingerprint, second.workspace_fingerprint)
            self.assertEqual(first.context_fingerprint, second.context_fingerprint)
            self.assertEqual(first.document(), second.document())

    def test_context_fingerprint_binds_ticket_workflow_and_workspace(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            original = build_context(root)
            self.assertEqual(
                build_context(root).context_fingerprint, original.context_fingerprint
            )
            variants = {
                "workflow": build_context(root, workflow="check"),
                "ticket": build_context(root, linear_ticket_id="PIP-900"),
                "refs": build_context(root, workspace_refs=["README.md"]),
            }
            for name, variant in variants.items():
                with self.subTest(element=name):
                    self.assertNotEqual(
                        variant.context_fingerprint, original.context_fingerprint
                    )

    def test_context_is_immutable_and_document_is_a_copy(self) -> None:
        with fixture_base() as base:
            context = build_context(make_fixture_root(base))
            with self.assertRaises(AttributeError):
                context.workflow = "adopt"  # type: ignore[misc]
            document = context.document()
            document["workflow"] = "adopt"
            document["workspaceRefs"].append("../escape.md")
            self.assertEqual(context.document()["workflow"], "review")
            self.assertEqual(context.document()["workspaceRefs"], list(DEFAULT_REFS))

    def test_forbidden_fixture_root_name_is_refused_before_filesystem_access(self) -> None:
        for name in (".env", ".ENV.local", ".ssh"):
            with self.subTest(name=name), fixture_base() as base:
                root = make_fixture_root(base, name)
                with forbid_host_access() as log:
                    assert_blocked(
                        self,
                        "path_forbidden",
                        build_context,
                        root,
                        forbidden=(str(base),),
                    )
                self.assertEqual(log, [])

    def test_forbidden_ancestor_name_refuses_innocent_nested_root(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base / ".env", "fixture")
            with forbid_host_access() as log:
                assert_blocked(
                    self,
                    "path_forbidden",
                    build_context,
                    root,
                    forbidden=(str(base),),
                )
            self.assertEqual(log, [])

    def test_context_without_valid_scan_seal_is_refused(self) -> None:
        with fixture_base() as base:
            context = build_context(make_fixture_root(base))
        unsealed = {
            "linear_ticket_id": TICKET_ID,
            "workflow": "review",
            "workspace_refs": DEFAULT_REFS,
            "workspace_fingerprint": context.workspace_fingerprint,
        }
        for seal in (None, object()):
            with self.subTest(seal=type(seal).__name__):
                assert_blocked(
                    self,
                    "context_invalid",
                    DeepSeekHarnessRunContext,
                    _seal=seal,
                    **unsealed,
                )
        for changes in (
            {"workspace_refs": ("README.md",)},
            {"workspace_fingerprint": "sha256:" + "5" * 64},
        ):
            with self.subTest(changes=list(changes)):
                assert_blocked(self, "context_invalid", replace, context, **changes)

    def test_build_does_not_read_host_environment_or_spawn(self) -> None:
        with fixture_base() as base:
            root = make_fixture_root(base)
            with forbid_host_access(filesystem=False) as log:
                context = build_context(root)
            self.assertEqual(log, [])
            self.assertIsInstance(context, DeepSeekHarnessRunContext)

            # "~" is never expanded against the host home directory.
            with forbid_host_access(filesystem=False) as log:
                with self.assertRaises(DeepSeekHarnessContractError):
                    DeepSeekHarnessRunContext.build(**context_fields(Path("~")))
            self.assertEqual(log, [])
