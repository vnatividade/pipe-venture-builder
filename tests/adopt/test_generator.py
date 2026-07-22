from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, skipUnless

from pipe_venture_builder.adopt import generate_product_baseline
from pipe_venture_builder.inventory.safety import MAX_METADATA_BYTES
from pipe_venture_builder.validation import validate_product_baseline

from tests.helpers import load_schema


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "brownfield"
GOLDEN_BASELINE = FIXTURE_ROOT / "expected-product-baseline.json"


class ProductBaselineGeneratorTests(TestCase):
    def test_representative_repository_matches_schema_and_golden_output(self) -> None:
        baseline = generate_product_baseline(FIXTURE_ROOT)

        self.assertEqual(validate_product_baseline(baseline, load_schema()), [])
        expected = json.loads(GOLDEN_BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(baseline, expected)

    def test_unchanged_runs_are_identical_with_stable_ids(self) -> None:
        first = generate_product_baseline(FIXTURE_ROOT)
        second = generate_product_baseline(FIXTURE_ROOT)

        self.assertEqual(first, second)
        self.assertEqual(first["baselineId"], "PB-brownfield-widget-adopt")
        self.assertEqual(
            [item["artifactId"] for item in first["artifacts"]],
            [item["artifactId"] for item in second["artifacts"]],
        )

    def test_sensitive_paths_and_values_never_appear_in_output(self) -> None:
        sentinel = "FAKE_SECRET_VALUE_MUST_NOT_LEAK_123456789"
        with TemporaryDirectory(prefix="pipe adoption safety ") as temporary:
            repository = Path(temporary) / "safe-product"
            shutil.copytree(FIXTURE_ROOT, repository)
            (repository / ".env").write_text(f"TOKEN={sentinel}\n", encoding="utf-8")
            sensitive_name = repository / "customer-secret-token.txt"
            sensitive_name.write_text(sentinel, encoding="utf-8")
            (repository / "package.json").write_text(
                json.dumps({"name": "unsafe-package", "apiKey": sentinel}),
                encoding="utf-8",
            )

            baseline = generate_product_baseline(repository)
            rendered = json.dumps(baseline, sort_keys=True)

        self.assertEqual(validate_product_baseline(baseline, load_schema()), [])
        self.assertNotIn(sentinel, rendered)
        self.assertNotIn(".env", rendered)
        self.assertNotIn(sensitive_name.name, rendered)
        self.assertNotIn("package.json", rendered)
        self.assertTrue(
            any(
                gap["gapId"] == "GAP-safety-omissions"
                for gap in baseline["governanceGaps"]
            )
        )

    def test_implementation_maturity_never_becomes_demand_evidence(self) -> None:
        baseline = generate_product_baseline(FIXTURE_ROOT)

        self.assertEqual(baseline["lifecycle"]["currentStage"], "ticket_execution")
        self.assertFalse(baseline["evidence"]["customerEvidencePresent"])
        self.assertEqual(baseline["evidence"]["demandValidationStatus"], "unproven")
        self.assertEqual(baseline["evidence"]["statementIds"], [])

    def test_conflicting_product_names_are_not_silently_resolved(self) -> None:
        with TemporaryDirectory(prefix="pipe identity conflict ") as temporary:
            repository = Path(temporary) / "existing-product"
            shutil.copytree(FIXTURE_ROOT, repository)
            (repository / "package.json").write_text(
                json.dumps({"name": "different-product"}), encoding="utf-8"
            )

            baseline = generate_product_baseline(repository)

        self.assertEqual(validate_product_baseline(baseline, load_schema()), [])
        conflict = next(
            statement
            for statement in baseline["statements"]
            if statement["statementId"] == "ST-product-identity-conflict"
        )
        self.assertEqual(conflict["classification"], "conflict")
        self.assertEqual(baseline["systems"]["repository"]["status"], "conflicting")
        self.assertTrue(
            any(
                gap["gapId"] == "GAP-product-identity"
                for gap in baseline["governanceGaps"]
            )
        )

    def test_bounded_size_limit_is_not_reported_as_sensitive_material(self) -> None:
        with TemporaryDirectory(prefix="pipe bounded inventory ") as temporary:
            repository = Path(temporary) / "large-product"
            shutil.copytree(FIXTURE_ROOT, repository)
            (repository / "README.md").write_text(
                "# Oversized metadata\n" + ("a" * MAX_METADATA_BYTES),
                encoding="utf-8",
            )

            baseline = generate_product_baseline(repository)

        gap_ids = {gap["gapId"] for gap in baseline["governanceGaps"]}
        self.assertIn("GAP-inventory-truncated", gap_ids)
        self.assertNotIn("GAP-safety-omissions", gap_ids)
        bounded_gap = next(
            gap
            for gap in baseline["governanceGaps"]
            if gap["gapId"] == "GAP-inventory-truncated"
        )
        self.assertEqual(
            (bounded_gap["severity"], bounded_gap["status"]), ("P2", "open")
        )

    def test_all_generated_references_resolve(self) -> None:
        baseline = generate_product_baseline(FIXTURE_ROOT)
        source_ids = {source["sourceId"] for source in baseline["sources"]}
        statement_ids = {
            statement["statementId"] for statement in baseline["statements"]
        }
        artifact_ids = {artifact["artifactId"] for artifact in baseline["artifacts"]}
        gap_ids = {gap["gapId"] for gap in baseline["governanceGaps"]}

        for statement in baseline["statements"]:
            self.assertLessEqual(set(statement["sourceIds"]), source_ids)
        for artifact in baseline["artifacts"]:
            self.assertLessEqual(set(artifact["provenanceStatementIds"]), statement_ids)
        for relationship in baseline["relationships"]:
            self.assertIn(relationship["fromArtifactId"], artifact_ids)
            self.assertIn(relationship["toArtifactId"], artifact_ids)
            self.assertLessEqual(set(relationship["sourceStatementIds"]), statement_ids)
        for gap in baseline["governanceGaps"]:
            self.assertLessEqual(set(gap["affectedArtifactIds"]), artifact_ids)
            self.assertLessEqual(set(gap["evidenceStatementIds"]), statement_ids)
        for action in baseline["nextActions"]:
            self.assertLessEqual(set(action["blockedByGapIds"]), gap_ids)
        self.assertLessEqual(
            set(baseline["lifecycle"]["stageRationaleStatementIds"]), statement_ids
        )
        self.assertLessEqual(set(baseline["evidence"]["statementIds"]), statement_ids)

    @skipUnless(shutil.which("git"), "Git is required for repository history inventory")
    def test_git_inventory_is_stable_for_paths_with_spaces(self) -> None:
        with TemporaryDirectory(prefix="pipe product with spaces ") as temporary:
            repository = Path(temporary) / "existing product"
            shutil.copytree(FIXTURE_ROOT, repository)
            environment = {
                **os.environ,
                "GIT_AUTHOR_DATE": "2026-01-02T03:04:05Z",
                "GIT_COMMITTER_DATE": "2026-01-02T03:04:05Z",
            }
            subprocess.run(
                ["git", "init", "-q", str(repository)], check=True, env=environment
            )
            subprocess.run(
                ["git", "-C", str(repository), "add", "."], check=True, env=environment
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "-c",
                    "user.name=Pipe Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "-qm",
                    "fixture baseline",
                ],
                check=True,
                env=environment,
            )

            first = generate_product_baseline(repository)
            second = generate_product_baseline(repository)

        self.assertEqual(first, second)
        self.assertEqual(first["generatedAt"], "2026-01-02T03:04:05Z")
        self.assertTrue(
            any(source["sourceType"] == "git_history" for source in first["sources"])
        )
        self.assertEqual(first["evidence"]["demandValidationStatus"], "unproven")

    @skipUnless(shutil.which("git"), "Git is required for repository history inventory")
    def test_empty_git_repository_is_reported_without_failure(self) -> None:
        with TemporaryDirectory(prefix="pipe empty git ") as temporary:
            repository = Path(temporary) / "empty-history-product"
            shutil.copytree(FIXTURE_ROOT, repository)
            subprocess.run(["git", "init", "-q", str(repository)], check=True)

            baseline = generate_product_baseline(repository)

        self.assertEqual(validate_product_baseline(baseline, load_schema()), [])
        self.assertEqual(baseline["generatedAt"], "1970-01-01T00:00:00Z")
        self.assertTrue(
            any(source["sourceType"] == "git_history" for source in baseline["sources"])
        )
        self.assertTrue(
            any(gap["gapId"] == "GAP-git-history" for gap in baseline["governanceGaps"])
        )
