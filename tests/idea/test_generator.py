from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.idea import generate_idea_baseline, load_idea_source
from pipe_venture_builder.validation import validate_product_baseline

from tests.helpers import load_schema


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "greenfield"
MARKDOWN_IDEA = FIXTURE_ROOT / "single-idea.md"
GOLDEN_BASELINE = FIXTURE_ROOT / "expected-idea-baseline.json"


class IdeaBaselineGeneratorTests(TestCase):
    def test_representative_markdown_matches_schema_and_golden_output(self) -> None:
        baseline = generate_idea_baseline(MARKDOWN_IDEA)

        self.assertEqual(validate_product_baseline(baseline, load_schema()), [])
        self.assertEqual(baseline["entryMode"], "idea")
        expected = json.loads(GOLDEN_BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(baseline, expected)

    def test_founder_statements_remain_assumptions_not_evidence(self) -> None:
        baseline = generate_idea_baseline(MARKDOWN_IDEA)
        material = [
            statement
            for statement in baseline["statements"]
            if statement["statementId"]
            not in {"ST-brainstorm-source", "ST-demand-evidence-missing"}
            and statement["classification"] != "missing"
        ]

        self.assertTrue(material)
        self.assertTrue(
            all(item["classification"] == "assumption" for item in material)
        )
        self.assertFalse(baseline["evidence"]["customerEvidencePresent"])
        self.assertEqual(
            baseline["evidence"]["demandValidationStatus"], "hypothesis_only"
        )
        self.assertEqual(baseline["evidence"]["statementIds"], [])

    def test_json_aliases_produce_one_traceable_idea(self) -> None:
        source = load_idea_source(FIXTURE_ROOT / "single-idea.json")
        baseline = generate_idea_baseline(FIXTURE_ROOT / "single-idea.json")

        self.assertEqual(source.name, "Rota Clara")
        self.assertEqual(source.target_user, "Fundadores solo")
        self.assertEqual(validate_product_baseline(baseline, load_schema()), [])
        self.assertEqual(baseline["product"]["productId"], "rota-clara")

    def test_ambiguous_input_stays_at_idea_intake_with_actionable_gaps(self) -> None:
        baseline = generate_idea_baseline(FIXTURE_ROOT / "ambiguous.md")

        self.assertEqual(validate_product_baseline(baseline, load_schema()), [])
        self.assertEqual(baseline["lifecycle"]["nextAllowedStage"], "idea_intake")
        gap = next(
            item
            for item in baseline["governanceGaps"]
            if item["gapId"] == "GAP-idea-framing"
        )
        self.assertEqual((gap["severity"], gap["status"]), ("P1", "blocked"))
        self.assertEqual(baseline["nextActions"][0]["actionId"], "NEXT-clarify-idea")

    def test_multiple_products_block_without_echoing_product_content(self) -> None:
        for filename in ("multiple-products.md", "multiple-products.json"):
            with (
                self.subTest(filename=filename),
                self.assertRaises(PipeError) as captured,
            ):
                generate_idea_baseline(FIXTURE_ROOT / filename)

            self.assertEqual(captured.exception.code, "IDEA_MULTIPLE_PRODUCTS")
            self.assertIn(
                "Split it into one source per product", captured.exception.message
            )
            self.assertNotIn("Alpha", captured.exception.message)
            self.assertNotIn("Beta", captured.exception.message)

    def test_raw_source_is_separately_traceable_and_runs_are_identical(self) -> None:
        first = generate_idea_baseline(MARKDOWN_IDEA)
        second = generate_idea_baseline(MARKDOWN_IDEA)

        self.assertEqual(first, second)
        self.assertEqual(first["sources"][0]["location"], "single-idea.md")
        self.assertEqual(first["artifacts"][1]["sourceRef"], "single-idea.md")
        self.assertRegex(
            first["sources"][0]["sourceId"], r"^SRC-brainstorm-[a-f0-9]{10}$"
        )

    def test_secret_and_personal_data_sources_are_blocked_without_leakage(self) -> None:
        sentinel = "FAKE_SECRET_VALUE_MUST_NOT_LEAK_123456789"
        with TemporaryDirectory(prefix="pipe idea safety ") as temporary:
            secret_source = Path(temporary) / "idea.md"
            secret_source.write_text(
                f"# Safe Name\n\n## Problem\nTOKEN={sentinel}\n", encoding="utf-8"
            )
            with self.assertRaises(PipeError) as secret_error:
                generate_idea_baseline(secret_source)

            personal_source = Path(temporary) / "personal.md"
            personal_source.write_text(
                "# Safe Name\n\n## Target User\nContact person@example.com\n",
                encoding="utf-8",
            )
            with self.assertRaises(PipeError) as personal_error:
                generate_idea_baseline(personal_source)

            sensitive_filename = Path(temporary) / "person@example.com.md"
            sensitive_filename.write_text("# Safe Name\n", encoding="utf-8")
            with self.assertRaises(PipeError) as filename_error:
                generate_idea_baseline(sensitive_filename)

        self.assertEqual(secret_error.exception.code, "IDEA_SOURCE_BLOCKED")
        self.assertNotIn(sentinel, secret_error.exception.message)
        self.assertEqual(personal_error.exception.code, "IDEA_SOURCE_BLOCKED")
        self.assertNotIn("person@example.com", personal_error.exception.message)
        self.assertEqual(filename_error.exception.code, "IDEA_SOURCE_BLOCKED")
        self.assertNotIn("person@example.com", filename_error.exception.message)

    def test_all_generated_references_resolve(self) -> None:
        baseline = generate_idea_baseline(MARKDOWN_IDEA)
        source_ids = {item["sourceId"] for item in baseline["sources"]}
        statement_ids = {item["statementId"] for item in baseline["statements"]}
        artifact_ids = {item["artifactId"] for item in baseline["artifacts"]}
        gap_ids = {item["gapId"] for item in baseline["governanceGaps"]}

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
