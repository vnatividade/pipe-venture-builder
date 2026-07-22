from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.cli import main
from pipe_venture_builder.exit_codes import READINESS_BLOCKED, SUCCESS

from tests.portability.helpers import TOOLKIT_ROOT, initialize_product_repository


class PortabilityCliTests(TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        code = main(args, stdout=stdout, stderr=stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_plan_apply_doctor_and_idempotent_rerun(self) -> None:
        with TemporaryDirectory(prefix="pipe cli portable ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            common = (
                str(root),
                "--toolkit-root",
                str(TOOLKIT_ROOT),
                "--product-id",
                "portable-product",
                "--entry-mode",
                "adopt",
                "--json",
            )
            plan = self.run_cli("bootstrap", *common)
            self.assertFalse((root / ".pipe/project.json").exists())
            apply = self.run_cli("bootstrap", *common, "--apply")
            first_bytes = (root / ".pipe/project.json").read_bytes()
            rerun = self.run_cli(
                "bootstrap",
                str(root),
                "--toolkit-root",
                str(TOOLKIT_ROOT),
                "--apply",
                "--json",
            )
            second_bytes = (root / ".pipe/project.json").read_bytes()
            doctor = self.run_cli(
                "doctor",
                str(root),
                "--toolkit-root",
                str(TOOLKIT_ROOT),
                "--json",
            )

        self.assertEqual((plan[0], plan[2]), (SUCCESS, ""))
        self.assertEqual(json.loads(plan[1])["mode"], "plan")
        self.assertEqual((apply[0], apply[2]), (SUCCESS, ""))
        self.assertEqual(json.loads(apply[1])["result"]["action"], "created")
        self.assertEqual((rerun[0], rerun[2]), (SUCCESS, ""))
        self.assertEqual(json.loads(rerun[1])["result"]["action"], "unchanged")
        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual((doctor[0], doctor[2]), (SUCCESS, ""))
        self.assertIn(json.loads(doctor[1])["status"], {"ready", "ready_with_warnings"})

    def test_dry_run_alias_never_creates_manifest(self) -> None:
        with TemporaryDirectory(prefix="pipe cli dry run ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            code, stdout, stderr = self.run_cli(
                "bootstrap",
                str(root),
                "--toolkit-root",
                str(TOOLKIT_ROOT),
                "--product-id",
                "portable-product",
                "--entry-mode",
                "idea",
                "--dry-run",
                "--json",
            )

            created = (root / ".pipe/project.json").exists()

        self.assertEqual((code, stderr), (SUCCESS, ""))
        self.assertEqual(json.loads(stdout)["mode"], "plan")
        self.assertFalse(created)

    def test_doctor_missing_manifest_returns_stable_health_exit(self) -> None:
        with TemporaryDirectory(prefix="pipe cli doctor missing ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            code, stdout, stderr = self.run_cli(
                "doctor",
                str(root),
                "--toolkit-root",
                str(TOOLKIT_ROOT),
                "--json",
            )

        payload = json.loads(stdout)
        self.assertEqual((code, stderr), (READINESS_BLOCKED, ""))
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["status"], "not_configured")

    def test_idea_can_resolve_toolkit_from_source_install(self) -> None:
        fixture = TOOLKIT_ROOT / "tests/fixtures/greenfield/single-idea.md"
        code, stdout, stderr = self.run_cli("idea", str(fixture), "--json")

        self.assertEqual((code, stderr), (SUCCESS, ""))
        self.assertEqual(json.loads(stdout)["baseline"]["entryMode"], "idea")
