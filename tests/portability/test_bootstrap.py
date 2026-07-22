from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.bootstrap import (
    BootstrapOptions,
    apply_bootstrap,
    plan_bootstrap,
)
from pipe_venture_builder.errors import PipeError

from tests.portability.helpers import TOOLKIT_ROOT


OPTIONS = BootstrapOptions(
    product_id="portable-product",
    entry_mode="adopt",
    runtime="hermes",
    fallback_runtimes=("codex", "claude-code"),
    capabilities=("capability.internal.atelier",),
)


class BootstrapTests(TestCase):
    def test_plan_is_default_shape_and_does_not_mutate(self) -> None:
        with TemporaryDirectory(prefix="pipe bootstrap plan ") as temporary:
            root = Path(temporary)
            before = tuple(root.iterdir())

            result = plan_bootstrap(
                root,
                TOOLKIT_ROOT,
                pipe_version="0.1.0",
                options=OPTIONS,
            )

            self.assertEqual(tuple(root.iterdir()), before)
            self.assertEqual(result.action, "create")
            self.assertEqual(
                result.operations,
                (
                    {"operation": "create_directory", "target": ".pipe"},
                    {"operation": "create_file", "target": ".pipe/project.json"},
                ),
            )
            self.assertTrue(result.warnings)

    def test_apply_is_idempotent_and_never_rewrites(self) -> None:
        with TemporaryDirectory(prefix="pipe bootstrap idempotent ") as temporary:
            root = Path(temporary)
            first = apply_bootstrap(
                root,
                TOOLKIT_ROOT,
                pipe_version="0.1.0",
                options=OPTIONS,
            )
            manifest_path = root / ".pipe/project.json"
            original = manifest_path.read_bytes()
            second = apply_bootstrap(
                root,
                TOOLKIT_ROOT,
                pipe_version="0.1.0",
                options=BootstrapOptions(),
            )

        self.assertEqual(first.action, "created")
        self.assertEqual(second.action, "unchanged")
        self.assertEqual(second.operations, ())
        self.assertEqual(
            original,
            json.dumps(first.manifest, indent=2, sort_keys=True).encode() + b"\n",
        )

    def test_conflicting_manifest_is_preserved(self) -> None:
        with TemporaryDirectory(prefix="pipe bootstrap conflict ") as temporary:
            root = Path(temporary)
            apply_bootstrap(
                root,
                TOOLKIT_ROOT,
                pipe_version="0.1.0",
                options=OPTIONS,
            )
            manifest_path = root / ".pipe/project.json"
            original = manifest_path.read_bytes()

            with self.assertRaises(PipeError) as captured:
                apply_bootstrap(
                    root,
                    TOOLKIT_ROOT,
                    pipe_version="0.1.0",
                    options=BootstrapOptions(product_id="different-product"),
                )

            preserved = manifest_path.read_bytes()

        self.assertEqual(captured.exception.code, "BOOTSTRAP_CONFLICT")
        self.assertEqual(preserved, original)

    def test_missing_initial_configuration_writes_nothing(self) -> None:
        with TemporaryDirectory(prefix="pipe bootstrap missing ") as temporary:
            root = Path(temporary)

            with self.assertRaises(PipeError) as captured:
                apply_bootstrap(
                    root,
                    TOOLKIT_ROOT,
                    pipe_version="0.1.0",
                    options=BootstrapOptions(),
                )

            self.assertEqual(tuple(root.iterdir()), ())

        self.assertEqual(captured.exception.code, "BOOTSTRAP_CONFIGURATION_REQUIRED")

    def test_symlinked_pipe_directory_is_blocked(self) -> None:
        with TemporaryDirectory(prefix="pipe bootstrap symlink ") as temporary:
            root = Path(temporary)
            target = root / "target"
            target.mkdir()
            try:
                (root / ".pipe").symlink_to(target, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Symlinks unavailable in this test environment: {exc}")

            with self.assertRaises(PipeError) as captured:
                plan_bootstrap(
                    root,
                    TOOLKIT_ROOT,
                    pipe_version="0.1.0",
                    options=OPTIONS,
                )

        self.assertEqual(captured.exception.code, "BOOTSTRAP_TARGET_BLOCKED")
