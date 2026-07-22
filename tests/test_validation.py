from copy import deepcopy
from unittest import TestCase

from pipe_venture_builder.errors import PipeError
from pipe_venture_builder.validation import (
    MAX_VALIDATION_ERRORS,
    ValidationFinding,
    invalid_baseline_error,
    validate_product_baseline,
)

from .helpers import load_schema, valid_baseline


class ProductBaselineValidationTests(TestCase):
    def setUp(self) -> None:
        self.schema = load_schema()

    def test_embedded_example_is_valid(self) -> None:
        self.assertEqual(validate_product_baseline(valid_baseline(), self.schema), [])

    def test_missing_required_property_is_actionable(self) -> None:
        baseline = deepcopy(valid_baseline())
        del baseline["product"]

        findings = validate_product_baseline(baseline, self.schema)

        self.assertTrue(findings)
        self.assertEqual(findings[0].rule, "required")
        self.assertEqual(findings[0].message, "Missing required property: product.")

    def test_fact_without_source_is_rejected(self) -> None:
        baseline = deepcopy(valid_baseline())
        baseline["statements"][0]["sourceIds"] = []

        findings = validate_product_baseline(baseline, self.schema)

        self.assertTrue(any(finding.rule == "minItems" for finding in findings))

    def test_invalid_datetime_is_rejected_by_format_checker(self) -> None:
        baseline = deepcopy(valid_baseline())
        baseline["generatedAt"] = "not-a-date"

        findings = validate_product_baseline(baseline, self.schema)

        self.assertTrue(any(finding.rule == "format" for finding in findings))

    def test_instance_values_are_never_rendered_in_findings(self) -> None:
        fake_secret = "FAKE_SECRET_VALUE_MUST_NOT_LEAK"
        baseline = deepcopy(valid_baseline())
        baseline["baselineId"] = fake_secret

        findings = validate_product_baseline(baseline, self.schema)
        rendered = " ".join(finding.message for finding in findings)

        self.assertTrue(findings)
        self.assertNotIn(fake_secret, rendered)

    def test_invalid_canonical_schema_maps_to_internal_contract_error(self) -> None:
        with self.assertRaises(PipeError) as captured:
            validate_product_baseline({}, {"type": "not-a-json-schema-type"})

        self.assertEqual(captured.exception.code, "BASELINE_SCHEMA_INVALID")
        self.assertEqual(captured.exception.exit_code, 7)

    def test_error_limit_reports_total_and_truncation(self) -> None:
        findings = [
            ValidationFinding(
                path=f"/field-{index}",
                schema_path="/required",
                rule="required",
                message="Missing required property.",
            )
            for index in range(MAX_VALIDATION_ERRORS + 3)
        ]

        error = invalid_baseline_error(findings)

        self.assertEqual(len(error.details), MAX_VALIDATION_ERRORS)
        self.assertIn(f"{MAX_VALIDATION_ERRORS + 3} error(s)", error.message)
        self.assertIn(f"first {MAX_VALIDATION_ERRORS}", error.message)
