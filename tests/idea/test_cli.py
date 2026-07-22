from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.cli import main
from pipe_venture_builder.exit_codes import INPUT_UNAVAILABLE, SUCCESS


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "greenfield"
TOOLKIT_ROOT = Path(__file__).resolve().parents[2]


class IdeaCliTests(TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        code = main(args, stdout=stdout, stderr=stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_json_mode_returns_greenfield_baseline(self) -> None:
        code, stdout, stderr = self.run_cli(
            "idea",
            str(FIXTURE_ROOT / "single-idea.md"),
            "--root",
            str(TOOLKIT_ROOT),
            "--json",
        )

        payload = json.loads(stdout)
        self.assertEqual((code, stderr), (SUCCESS, ""))
        self.assertEqual(payload["command"], "idea")
        self.assertEqual(payload["baseline"]["entryMode"], "idea")

    def test_explicit_output_never_overwrites(self) -> None:
        with TemporaryDirectory(prefix="pipe idea output ") as temporary:
            output = Path(temporary) / "idea-baseline.json"
            first = self.run_cli(
                "idea",
                str(FIXTURE_ROOT / "single-idea.md"),
                "--root",
                str(TOOLKIT_ROOT),
                "--output",
                str(output),
            )
            original = output.read_text(encoding="utf-8")
            second = self.run_cli(
                "idea",
                str(FIXTURE_ROOT / "single-idea.md"),
                "--root",
                str(TOOLKIT_ROOT),
                "--output",
                str(output),
            )

        self.assertEqual((first[0], first[2]), (SUCCESS, ""))
        self.assertEqual(second[0], INPUT_UNAVAILABLE)
        self.assertIn("IDEA_OUTPUT_EXISTS", second[2])
        self.assertIn('"entryMode": "idea"', original)

    def test_multiple_product_error_is_stable_json(self) -> None:
        code, stdout, stderr = self.run_cli(
            "idea",
            str(FIXTURE_ROOT / "multiple-products.json"),
            "--root",
            str(TOOLKIT_ROOT),
            "--json",
        )

        payload = json.loads(stderr)
        self.assertEqual(stdout, "")
        self.assertNotEqual(code, SUCCESS)
        self.assertEqual(payload["code"], "IDEA_MULTIPLE_PRODUCTS")
