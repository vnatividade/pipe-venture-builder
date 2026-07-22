from __future__ import annotations

import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from jsonschema import Draft202012Validator

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.manifest import (
    build_product_manifest,
    load_product_manifest,
    validate_product_manifest,
)
from pipe_venture_builder.validation import load_json_document

from tests.portability.helpers import TOOLKIT_ROOT, bootstrap_product


class ProductManifestTests(TestCase):
    def setUp(self) -> None:
        self.schema = load_json_document(
            TOOLKIT_ROOT / "schemas/ProductManifest.schema.json",
            kind="schema",
        )
        self.example = json.loads(
            (TOOLKIT_ROOT / "setup/ProductManifest.example.json").read_text(
                encoding="utf-8"
            )
        )

    def test_schema_and_tracked_example_are_valid(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual(validate_product_manifest(self.example, self.schema), [])

    def test_manifest_rejects_absolute_paths_and_secret_fields(self) -> None:
        for machine_path in (
            "/Users/founder/product",
            "C:\\Users\\founder\\product",
            "~/Developer/product",
        ):
            with self.subTest(machine_path=machine_path):
                candidate = copy.deepcopy(self.example)
                candidate["repository"]["root"] = machine_path
                findings = validate_product_manifest(candidate, self.schema)
                self.assertTrue(findings)

        secret_candidate = copy.deepcopy(self.example)
        secret_candidate["github"]["token"] = "FAKE_SECRET_MUST_NOT_APPEAR"
        findings = validate_product_manifest(secret_candidate, self.schema)
        rendered = json.dumps([item.as_dict() for item in findings])
        self.assertTrue(findings)
        self.assertNotIn("FAKE_SECRET_MUST_NOT_APPEAR", rendered)

        token = "ghp_" + ("A" * 24)
        token_candidate = copy.deepcopy(self.example)
        token_candidate["linear"]["projectId"] = token
        findings = validate_product_manifest(token_candidate, self.schema)
        rendered = json.dumps([item.as_dict() for item in findings])
        self.assertIn("sensitiveValue", {item.rule for item in findings})
        self.assertNotIn(token, rendered)

        linear_token = "lin_api_" + ("B" * 24)
        token_candidate["linear"]["projectId"] = linear_token
        findings = validate_product_manifest(token_candidate, self.schema)
        rendered = json.dumps([item.as_dict() for item in findings])
        self.assertIn("sensitiveValue", {item.rule for item in findings})
        self.assertNotIn(linear_token, rendered)

    def test_preferred_runtime_cannot_be_duplicated_as_fallback(self) -> None:
        candidate = copy.deepcopy(self.example)
        candidate["runtime"]["fallbacks"].append(candidate["runtime"]["preferred"])

        findings = validate_product_manifest(candidate, self.schema)

        self.assertIn("distinctRuntimeSelection", {item.rule for item in findings})

    def test_builder_is_deterministic_and_sorts_capabilities(self) -> None:
        manifest = build_product_manifest(
            product_id="portable-product",
            pipe_version="0.1.0",
            entry_mode="adopt",
            runtime="codex",
            fallback_runtimes=("claude-code",),
            capabilities=(
                "capability.internal.atelier",
                "capability.external.codex",
                "capability.internal.atelier",
            ),
        )

        self.assertEqual(
            manifest["capabilities"]["enabled"],
            ["capability.external.codex", "capability.internal.atelier"],
        )
        self.assertEqual(manifest["repository"]["root"], ".")

    def test_loader_blocks_manifest_symlinks_without_reading_target(self) -> None:
        with TemporaryDirectory(prefix="pipe manifest symlink ") as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_text(json.dumps(self.example), encoding="utf-8")
            (root / ".pipe").mkdir()
            link = root / ".pipe/project.json"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"Symlinks unavailable in this test environment: {exc}")

            with self.assertRaises(PipeError) as captured:
                load_product_manifest(root, TOOLKIT_ROOT)

        self.assertEqual(captured.exception.code, "MANIFEST_BLOCKED")

    def test_loaded_manifest_matches_created_manifest(self) -> None:
        with TemporaryDirectory(prefix="pipe manifest load ") as temporary:
            root = Path(temporary)
            expected = bootstrap_product(root)
            loaded = load_product_manifest(root, TOOLKIT_ROOT)

        self.assertEqual(loaded.data, expected)
