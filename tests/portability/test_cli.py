from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pipe_venture_builder.cli import main
from pipe_venture_builder.exit_codes import READINESS_BLOCKED, SUCCESS

from tests.portability.helpers import TOOLKIT_ROOT, initialize_product_repository

# Espelha DoctorReport.is_ready. Um host sem o binário do runtime reporta `blocked`,
# e isso é resposta correta do produto — não é falha de teste.
READY_STATES = {"ready", "ready_with_warnings"}


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

        # `bootstrap --apply` roda o doctor e devolve READINESS_BLOCKED quando o
        # HOST não está pronto — por exemplo, sem o binário do runtime instalado.
        # Fixar SUCCESS aqui embutia a suposição de que a máquina tem hermes/codex/
        # claude: o teste ficava verde na máquina do fundador e vermelho em qualquer
        # runner (PIP-837). O que importa verificar é que o exit code é COERENTE com
        # o relatório do doctor devolvido na mesma resposta, não que o host esteja
        # equipado. Reproduza a diferença com:
        #   PATH=/usr/bin:/bin python -m pytest tests/portability/test_cli.py
        apply_payload = json.loads(apply[1])
        self.assertEqual(apply[2], "")
        self.assertEqual(apply_payload["result"]["action"], "created")
        self.assertEqual(
            apply[0],
            SUCCESS if apply_payload["doctor"]["status"] in READY_STATES else READINESS_BLOCKED,
            f"exit code incoerente com doctor.status={apply_payload['doctor']['status']}",
        )

        rerun_payload = json.loads(rerun[1])
        self.assertEqual(rerun[2], "")
        self.assertEqual(rerun_payload["result"]["action"], "unchanged")
        self.assertEqual(rerun[0], apply[0], "reaplicar sem mudança não pode mudar o exit code")
        self.assertEqual(first_bytes, second_bytes)

        # `doctor` isolado segue o MESMO contrato de exit code: 0 quando pronto,
        # READINESS_BLOCKED quando não. Verificamos a coerência, não a prontidão do host.
        doctor_status = json.loads(doctor[1])["status"]
        self.assertEqual(doctor[2], "")
        self.assertEqual(
            doctor[0],
            SUCCESS if doctor_status in READY_STATES else READINESS_BLOCKED,
            f"exit code incoerente com doctor.status={doctor_status}",
        )
        # E os dois caminhos precisam concordar sobre o mesmo host.
        self.assertEqual(doctor[0], apply[0])

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
