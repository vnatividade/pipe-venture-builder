from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.doctor import run_doctor
from pipe_venture_builder.doctor.checks import _capability_governance_status

from tests.portability.helpers import (
    TOOLKIT_ROOT,
    bootstrap_product,
    initialize_product_repository,
)


class DoctorTests(TestCase):
    def test_capability_review_status_uses_the_canonical_enum(self) -> None:
        cases = {
            ("pilot", "approved"): "configured",
            ("pilot", "restricted"): "unauthorized",
            ("pilot", "not-reviewed"): "unauthorized",
            ("pilot", "needs-update"): "incompatible",
            ("pilot", "blocked"): "blocked",
            ("proposed", "approved"): "unavailable",
            ("deprecated", "approved"): "incompatible",
            ("blocked", "approved"): "blocked",
            ("restricted", "approved"): "unauthorized",
        }
        for (lifecycle, review_status), expected in cases.items():
            with self.subTest(lifecycle=lifecycle, review_status=review_status):
                self.assertEqual(
                    _capability_governance_status(lifecycle, review_status),
                    expected,
                )

    def test_configured_product_uses_fallback_and_reports_warning(self) -> None:
        with TemporaryDirectory(prefix="pipe doctor ready ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            bootstrap_product(root)

            report = run_doctor(
                root,
                TOOLKIT_ROOT,
                which=lambda _command: "/portable/bin/tool",
                git_inspector=lambda _root: str(root),
                platform_name="darwin",
                machine_name="arm64",
            )

        checks = {item.check_id: item for item in report.checks}
        self.assertEqual(report.status, "ready_with_warnings")
        self.assertEqual(checks["product_manifest"].status, "configured")
        self.assertEqual(checks["runtime_selection"].status, "configured")
        self.assertEqual(
            checks["runtime_adapter_capability_external_hermes"].status,
            "unavailable",
        )
        self.assertEqual(
            checks["runtime_adapter_capability_external_codex"].status,
            "unauthorized",
        )

    def test_check_states_distinguish_unauthorized_and_incompatible(self) -> None:
        with TemporaryDirectory(prefix="pipe doctor states ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            manifest = bootstrap_product(
                root,
                linear_project_id="linear-project",
                github_repository="owner/repository",
            )
            manifest["pipeVersion"] = "9.9.9"
            (root / ".pipe/project.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            report = run_doctor(
                root,
                TOOLKIT_ROOT,
                which=lambda _command: "/portable/bin/tool",
                git_inspector=lambda _root: str(root),
            )

        checks = {item.check_id: item for item in report.checks}
        self.assertEqual(report.status, "blocked")
        self.assertEqual(checks["manifest_pipe_version"].status, "incompatible")
        self.assertEqual(checks["connector_linear"].status, "unauthorized")
        self.assertEqual(checks["connector_github"].status, "unauthorized")

    def test_manifest_symlink_is_blocked_without_content_leakage(self) -> None:
        sentinel = "FAKE_PRIVATE_PATH_MUST_NOT_LEAK"
        with TemporaryDirectory(prefix="pipe doctor blocked ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            target = root / "unsafe.json"
            target.write_text(sentinel, encoding="utf-8")
            link = root / ".pipe/project.json"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"Symlinks unavailable in this test environment: {exc}")

            report = run_doctor(
                root,
                TOOLKIT_ROOT,
                which=lambda _command: "/portable/bin/tool",
                git_inspector=lambda _root: str(root),
            )

        rendered = json.dumps(report.as_dict())
        checks = {item.check_id: item for item in report.checks}
        self.assertEqual(checks["product_manifest"].status, "blocked")
        self.assertNotIn(sentinel, rendered)

    def test_missing_manifest_is_not_configured_and_read_only(self) -> None:
        with TemporaryDirectory(prefix="pipe doctor missing ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            before = sorted(path.relative_to(root) for path in root.rglob("*"))

            report = run_doctor(
                root,
                TOOLKIT_ROOT,
                which=lambda _command: "/portable/bin/tool",
                git_inspector=lambda _root: str(root),
            )

            after = sorted(path.relative_to(root) for path in root.rglob("*"))

        self.assertEqual(report.status, "not_configured")
        self.assertEqual(before, after)

    def test_incompatibility_is_not_masked_by_missing_configuration(self) -> None:
        with TemporaryDirectory(prefix="pipe doctor precedence ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root, mode=False)

            report = run_doctor(
                root,
                TOOLKIT_ROOT,
                which=lambda _command: "/portable/bin/tool",
                git_inspector=lambda _root: str(root),
                platform_name="unsupported-platform",
                machine_name="unknown",
            )

        self.assertEqual(report.status, "blocked")

    def test_no_executor_or_write_access_blocks_readiness(self) -> None:
        with TemporaryDirectory(prefix="pipe doctor blocked runtime ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            bootstrap_product(root)

            report = run_doctor(
                root,
                TOOLKIT_ROOT,
                which=lambda command: "/usr/bin/git" if command == "git" else None,
                access=lambda _path, _mode: False,
                git_inspector=lambda _root: str(root),
            )

        checks = {item.check_id: item for item in report.checks}
        self.assertEqual(report.status, "blocked")
        self.assertEqual(checks["runtime_selection"].status, "blocked")
        self.assertEqual(checks["repository_write_access"].status, "unauthorized")

    def test_supported_platform_fixture_matrix(self) -> None:
        matrix = json.loads(
            (Path(__file__).parent / "fixtures/platform-matrix.json").read_text(
                encoding="utf-8"
            )
        )
        with TemporaryDirectory(prefix="pipe doctor platforms ") as temporary:
            root = Path(temporary)
            initialize_product_repository(root)
            bootstrap_product(root)
            for case in matrix:
                with self.subTest(case=case):
                    report = run_doctor(
                        root,
                        TOOLKIT_ROOT,
                        which=lambda _command: "/portable/bin/tool",
                        git_inspector=lambda _root: str(root),
                        platform_name=case["platform"],
                        machine_name=case["architecture"],
                    )
                    platform_check = next(
                        item for item in report.checks if item.check_id == "platform"
                    )
                    self.assertEqual(platform_check.status, "configured")
