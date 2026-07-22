from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from tests.helpers import REPOSITORY_ROOT


INTEGRATION_ROOT = REPOSITORY_ROOT / "integrations" / "hermes"


class HermesIntegrationPackageTests(TestCase):
    def test_manifest_declares_supervised_non_mutating_boundary(self) -> None:
        manifest = json.loads(
            (INTEGRATION_ROOT / "manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual(manifest["minimumRuntimeVersion"], "0.17.0")
        self.assertEqual(
            manifest["sessionIdentityEnvironment"], "HERMES_SESSION_ID"
        )
        self.assertTrue(manifest["constraints"]["pipeApprovalRequired"])
        for key in (
            "hermesApprovalIsAuthority",
            "externalMutationAllowed",
            "credentialsAllowed",
            "customerDataAllowed",
            "productionDataAllowed",
            "automaticInstallationAllowed",
        ):
            self.assertFalse(manifest["constraints"][key])

    def test_skill_has_valid_peer_matched_frontmatter(self) -> None:
        content = (INTEGRATION_ROOT / "skill" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertTrue(content.startswith("---\n"))
        frontmatter, body = content[4:].split("\n---\n", 1)
        fields = {
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if line and not line.startswith(" ") and ":" in line
        }
        self.assertTrue(
            {"name", "description", "version", "author", "license", "metadata"}
            <= fields
        )
        description = next(
            line.split(":", 1)[1].strip()
            for line in frontmatter.splitlines()
            if line.startswith("description:")
        )
        self.assertTrue(description.startswith("Use when "))
        self.assertLessEqual(len(description), 1024)
        self.assertIn("# Pipe Product Delivery Runtime", body)
        self.assertLessEqual(len(content), 100_000)

    def test_installer_is_plan_first_and_never_overwrites(self) -> None:
        installer = INTEGRATION_ROOT / "install.sh"
        with TemporaryDirectory() as directory:
            home = Path(directory) / "hermes-home"
            plan = subprocess.run(
                ["sh", str(installer), "--hermes-home", str(home), "--plan"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(plan.returncode, 0)
            self.assertFalse(home.exists())
            self.assertIn("no files were written", plan.stdout)

            applied = subprocess.run(
                ["sh", str(installer), "--hermes-home", str(home), "--apply"],
                check=False,
                capture_output=True,
                text=True,
            )
            destination = (
                home
                / "skills"
                / "autonomous-ai-agents"
                / "pipe-product-delivery"
                / "SKILL.md"
            )
            self.assertEqual(applied.returncode, 0)
            self.assertTrue(destination.is_file())
            self.assertEqual(os.stat(destination).st_mode & 0o777, 0o644)

            repeated = subprocess.run(
                ["sh", str(installer), "--hermes-home", str(home), "--apply"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(repeated.returncode, 8)
            self.assertIn("no files were overwritten", repeated.stderr)

    def test_package_has_no_founder_specific_path_or_secret_placeholder(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in INTEGRATION_ROOT.rglob("*")
            if path.is_file()
        )
        self.assertNotIn("/Users/agents", text)
        self.assertNotIn("api_key", text.lower())
        self.assertNotIn("access_token", text.lower())

    def test_fixture_smoke_starts_blocks_and_resumes_without_mutation(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(INTEGRATION_ROOT / "smoke.py"),
                "--skip-runtime-probe",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
            env={**os.environ, "PYTHONPATH": str(REPOSITORY_ROOT / "src")},
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["ok"])
        self.assertEqual(result["blockedState"], "runtime_blocked")
        self.assertEqual(result["attempt"], 2)
        self.assertTrue(result["auditChainValid"])
        self.assertFalse(result["externalMutationPerformed"])
