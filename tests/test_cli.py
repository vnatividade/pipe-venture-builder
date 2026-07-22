from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from pipe_venture_builder.cli import build_parser, main
from pipe_venture_builder.exit_codes import (
    BASELINE_INVALID,
    INPUT_INVALID_JSON,
    INTERNAL_CONTRACT_ERROR,
    PROJECT_ROOT_NOT_FOUND,
    SUCCESS,
    USAGE_ERROR,
)

from .helpers import make_pipe_root, valid_baseline, write_json


class CliTests(TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        code = main(args, stdout=stdout, stderr=stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_version_supports_human_and_json_output(self) -> None:
        code, stdout, stderr = self.run_cli("version")
        self.assertEqual((code, stderr), (SUCCESS, ""))
        self.assertRegex(stdout, r"^pipe \d+\.\d+\.\d+\n$")

        code, stdout, stderr = self.run_cli("version", "--json")
        payload = json.loads(stdout)
        self.assertEqual((code, stderr, payload["ok"]), (SUCCESS, "", True))
        self.assertEqual(payload["command"], "version")

    def test_root_command_discovers_project(self) -> None:
        with TemporaryDirectory(prefix="pipe cli ") as temporary:
            root = make_pipe_root(Path(temporary) / "product with spaces")
            nested = root / "docs"
            nested.mkdir()
            code, stdout, stderr = self.run_cli("root", str(nested), "--json")

        payload = json.loads(stdout)
        self.assertEqual((code, stderr), (SUCCESS, ""))
        self.assertEqual(payload["root"], str(root.resolve()))

    def test_validates_embedded_product_baseline_example(self) -> None:
        with TemporaryDirectory(prefix="pipe validate ") as temporary:
            root = make_pipe_root(Path(temporary) / "product")
            baseline = write_json(root / "baseline.json", valid_baseline())
            code, stdout, stderr = self.run_cli(
                "baseline",
                "validate",
                str(baseline),
                "--root",
                str(root),
                "--json",
            )

        payload = json.loads(stdout)
        self.assertEqual((code, stderr), (SUCCESS, ""))
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "baseline.validate")

    def test_invalid_baseline_has_stable_exit_code_and_redacted_output(self) -> None:
        fake_secret = "FAKE_SECRET_VALUE_MUST_NOT_LEAK"
        with TemporaryDirectory(prefix="pipe validate ") as temporary:
            root = make_pipe_root(Path(temporary) / "product")
            invalid = deepcopy(valid_baseline())
            invalid["baselineId"] = fake_secret
            baseline = write_json(root / "baseline.json", invalid)
            code, stdout, stderr = self.run_cli(
                "baseline",
                "validate",
                str(baseline),
                "--root",
                str(root),
                "--json",
            )

        payload = json.loads(stderr)
        self.assertEqual((code, stdout), (BASELINE_INVALID, ""))
        self.assertEqual(payload["code"], "BASELINE_INVALID")
        self.assertNotIn(fake_secret, stderr)

    def test_invalid_json_reports_position_without_source_content(self) -> None:
        fake_secret = "FAKE_SECRET_VALUE_MUST_NOT_LEAK"
        with TemporaryDirectory(prefix="pipe validate ") as temporary:
            root = make_pipe_root(Path(temporary) / "product")
            baseline = root / "baseline.json"
            baseline.write_text('{"secret": "' + fake_secret, encoding="utf-8")
            code, stdout, stderr = self.run_cli(
                "baseline",
                "validate",
                str(baseline),
                "--root",
                str(root),
                "--json",
            )

        payload = json.loads(stderr)
        self.assertEqual((code, stdout), (INPUT_INVALID_JSON, ""))
        self.assertEqual(payload["code"], "BASELINE_INVALID_JSON")
        self.assertNotIn(fake_secret, stderr)

    def test_non_utf8_json_uses_sanitized_json_error(self) -> None:
        with TemporaryDirectory(prefix="pipe validate ") as temporary:
            root = make_pipe_root(Path(temporary) / "product")
            baseline = root / "baseline.json"
            baseline.write_bytes(b"\xff\xfe{\x00}\x00")
            code, stdout, stderr = self.run_cli(
                "baseline",
                "validate",
                str(baseline),
                "--root",
                str(root),
                "--json",
            )

        payload = json.loads(stderr)
        self.assertEqual((code, stdout), (INPUT_INVALID_JSON, ""))
        self.assertEqual(payload["code"], "BASELINE_INVALID_JSON")
        self.assertNotIn("Traceback", stderr)
        self.assertNotIn("UnicodeDecodeError", stderr)

    def test_missing_root_is_a_deterministic_error(self) -> None:
        with TemporaryDirectory() as temporary:
            baseline = write_json(Path(temporary) / "baseline.json", {})
            code, stdout, stderr = self.run_cli(
                "baseline",
                "validate",
                str(baseline),
                "--root",
                temporary,
                "--json",
            )

        payload = json.loads(stderr)
        self.assertEqual((code, stdout), (PROJECT_ROOT_NOT_FOUND, ""))
        self.assertEqual(payload["code"], "PROJECT_ROOT_NOT_FOUND")

    def test_missing_explicit_schema_is_a_deterministic_error(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_pipe_root(Path(temporary) / "product")
            baseline = write_json(root / "baseline.json", valid_baseline())
            code, stdout, stderr = self.run_cli(
                "baseline",
                "validate",
                str(baseline),
                "--root",
                str(root),
                "--schema",
                "schemas/missing.schema.json",
                "--json",
            )

        payload = json.loads(stderr)
        self.assertEqual((code, stdout), (PROJECT_ROOT_NOT_FOUND, ""))
        self.assertEqual(payload["code"], "BASELINE_SCHEMA_UNAVAILABLE")

    def test_unexpected_failure_is_sanitized_as_internal_error(self) -> None:
        with patch("pipe_venture_builder.cli._handle_version", side_effect=RuntimeError("private")):
            code, stdout, stderr = self.run_cli("version", "--json")

        payload = json.loads(stderr)
        self.assertEqual((code, stdout), (INTERNAL_CONTRACT_ERROR, ""))
        self.assertEqual(payload["code"], "INTERNAL_ERROR")
        self.assertNotIn("private", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_top_level_version_and_usage_exit_codes(self) -> None:
        parser = build_parser()
        version_output = StringIO()
        with redirect_stdout(version_output), self.assertRaises(SystemExit) as version_exit:
            parser.parse_args(["--version"])
        self.assertEqual(version_exit.exception.code, SUCCESS)
        self.assertRegex(version_output.getvalue(), r"^pipe \d+\.\d+\.\d+\n$")

        usage_output = StringIO()
        with redirect_stderr(usage_output), self.assertRaises(SystemExit) as usage_exit:
            parser.parse_args([])
        self.assertEqual(usage_exit.exception.code, USAGE_ERROR)
        self.assertIn("required", usage_output.getvalue())
