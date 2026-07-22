from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.cli import main
from pipe_venture_builder.exit_codes import INPUT_UNAVAILABLE, SUCCESS


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "brownfield"
TOOLKIT_ROOT = Path(__file__).resolve().parents[2]


class AdoptCliTests(TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        code = main(args, stdout=stdout, stderr=stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_json_mode_returns_the_generated_baseline(self) -> None:
        code, stdout, stderr = self.run_cli(
            "adopt",
            str(FIXTURE_ROOT),
            "--root",
            str(TOOLKIT_ROOT),
            "--json",
        )

        payload = json.loads(stdout)
        self.assertEqual((code, stderr), (SUCCESS, ""))
        self.assertEqual(payload["command"], "adopt")
        self.assertEqual(payload["baseline"]["entryMode"], "adopt")

    def test_output_is_explicit_and_never_overwrites(self) -> None:
        with TemporaryDirectory(prefix="pipe adopt output ") as temporary:
            output = Path(temporary) / "baseline.json"
            first = self.run_cli(
                "adopt",
                str(FIXTURE_ROOT),
                "--root",
                str(TOOLKIT_ROOT),
                "--output",
                str(output),
            )
            original = output.read_text(encoding="utf-8")
            second = self.run_cli(
                "adopt",
                str(FIXTURE_ROOT),
                "--root",
                str(TOOLKIT_ROOT),
                "--output",
                str(output),
            )

        self.assertEqual((first[0], first[2]), (SUCCESS, ""))
        self.assertEqual(second[0], INPUT_UNAVAILABLE)
        self.assertIn("ADOPT_OUTPUT_EXISTS", second[2])
        self.assertIn('"entryMode": "adopt"', original)
